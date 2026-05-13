#!/usr/bin/env python3
"""
Foursquare → SeeGoEat Importer
Reads tools/foursquare_favorites.json (or foursquare_places_full.json)
and merges places into index.html.

Usage:
    python3 tools/foursquare_import.py                  # favorites only (recommended)
    python3 tools/foursquare_import.py --all            # all check-ins
    python3 tools/foursquare_import.py --min-checkins 3 # visited 3+ times
    python3 tools/foursquare_import.py --dry-run        # preview without writing
"""

import re
import json
import sys
import argparse
from urllib.parse import quote_plus
from collections import defaultdict

# ── Category mapping ──────────────────────────────────────────────────────────────────
CAT_MAP = {
    "food":   "Food",
    "drinks": "Nightlife",
    "stay":   "Places to Stay",
    "see":    "Places to See",
    "other":  "Places to See",
}

# ── City name normalisation ───────────────────────────────────────────────────────────────
# Maps Foursquare city names to the canonical names used in index.html
CITY_ALIASES = {
    "New York":           "New York City",
    "NYC":                "New York City",
    "DC":                 "Washington DC",
    "Washington":         "Washington DC",
    "SF":                 "San Francisco",
    "LA":                 "Los Angeles",
    "BCN":                "Barcelona",
    "L'Hospitalet de Llobregat": "Barcelona",
    "Badalona":           "Barcelona",
    "Sant Cugat del Vallès": "Barcelona",
    "Esplugues de Llobregat": "Barcelona",
    "Poble Sec":          "Barcelona",
    "Eixample":           "Barcelona",
    "El Born":            "Barcelona",
    "Gracia":             "Barcelona",
    "Gràcia":             "Barcelona",
    "Tulum Pueblo":       "Tulum",
    "Playa del Carmen":   "Playa del Carmen",
    "Cancún":             "Cancun",
    "México City":        "Mexico City",
    "Ciudad de México":   "Mexico City",
    "Kyōto":              "Kyoto",
    "Ōsaka":              "Osaka",
    "Kōbe":               "Kobe",
    "Den Haag":           "Amsterdam",
    "Haarlem":            "Amsterdam",
    "Reykjanes":          "Reykjavík",
    "Keflavik":           "Keflavík",
    "Cape Town City Bowl":"Cape Town",
    "Sea Point":          "Cape Town",
    "Camps Bay":          "Cape Town",
    "Marbella":           "Marbella/Málaga",
    "Málaga":             "Marbella/Málaga",
    "Malaga":             "Marbella/Málaga",
    "Buenos Aires":       "Buenos Aires",
    "Porto Alegre":       None,   # not covered — skip
}

# Cities we actively cover (pulled from PLACES keys at runtime)
KNOWN_CITIES = set()


def load_html(path="../index.html"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_html(html, path="../index.html"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def parse_places(html):
    """Extract the PLACES JS object as a dict of city → list of raw entry strings."""
    m = re.search(r"const PLACES=(\{)(.*?)(\});", html, re.DOTALL)
    if not m:
        raise ValueError("Could not find const PLACES= in index.html")
    return m


def get_known_cities(html):
    """Return set of city names already in PLACES."""
    m = parse_places(html)
    return set(re.findall(r'"([^"]+)":\s*\[', m.group(2)))


def resolve_city(fsq_city, fsq_country):
    """Map a Foursquare city name to a canonical seegoeat city, or None to skip."""
    if fsq_city in CITY_ALIASES:
        return CITY_ALIASES[fsq_city]
    if fsq_city in KNOWN_CITIES:
        return fsq_city
    return None   # city not covered → skip


def build_place_entry(place, is_fave):
    """Convert a Foursquare place dict to a seegoeat PLACES entry dict."""
    cat = CAT_MAP.get(place.get("category", "other"), "Places to See")
    name = place["name"]
    notes = place.get("notes") or []
    description = notes[0] if notes else ""

    entry = {
        "n": name,
        "c": cat,
        "d": description,
        "u": place.get("google_maps_url", ""),
        "r": round(min(place.get("checkin_count", 1), 5) * 0.8 + 3.2, 1),
    }
    if is_fave:
        entry["f"] = True
    return entry


def entry_to_json(entry):
    """Serialise a place entry to compact JSON matching the existing style."""
    parts = []
    for k, v in entry.items():
        if v is None or v == "":
            continue
        if isinstance(v, bool):
            parts.append(f'"{k}":{str(v).lower()}')
        elif isinstance(v, (int, float)):
            parts.append(f'"{k}":{v}')
        else:
            escaped = str(v).replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'"{k}":"{escaped}"')
    return "{" + ",".join(parts) + "}"


def get_existing_names(city_arr_str):
    """Return lowercase set of place names already in a city's array string."""
    return {n.lower() for n in re.findall(r'"n":\s*"([^"]+)"', city_arr_str)}


def insert_sorted(city_arr_str, new_entry_str, new_name):
    """Insert new_entry_str into city_arr_str in alphabetical order by name."""
    entries = re.findall(r"\{[^{}]*\}", city_arr_str)
    entries_with_names = []
    for e in entries:
        nm = re.search(r'"n":\s*"([^"]+)"', e)
        entries_with_names.append((nm.group(1).lower() if nm else "", e))

    entries_with_names.append((new_name.lower(), new_entry_str))
    entries_with_names.sort(key=lambda x: x[0])
    return "[" + ",".join(e for _, e in entries_with_names) + "]"


def merge_places(html, new_places_by_city, dry_run=False):
    """Merge new places into the PLACES block in index.html."""
    places_match = parse_places(html)
    places_str = places_match.group(2)

    added = defaultdict(list)
    skipped_dup = defaultdict(list)

    for city, entries in new_places_by_city.items():
        # Find city array in places_str
        city_m = re.search(
            r'"' + re.escape(city) + r'":\s*(\[.*?\])(?=,"\w|$)',
            places_str, re.DOTALL
        )

        if city_m:
            existing = get_existing_names(city_m.group(1))
            new_arr = city_m.group(1)
            for entry_dict in entries:
                if entry_dict["n"].lower() in existing:
                    skipped_dup[city].append(entry_dict["n"])
                    continue
                entry_str = entry_to_json(entry_dict)
                new_arr = insert_sorted(new_arr, entry_str, entry_dict["n"])
                existing.add(entry_dict["n"].lower())
                added[city].append(entry_dict["n"])

            if not dry_run:
                places_str = places_str.replace(city_m.group(1), new_arr, 1)
        else:
            # New city — build array and append to PLACES
            arr_entries = [entry_to_json(e) for e in entries]
            new_city_block = f'"{city}":[' + ",".join(arr_entries) + "]"
            places_str = places_str.rstrip() + "," + new_city_block
            for e in entries:
                added[city].append(e["n"])

    if not dry_run:
        new_html = html.replace(
            places_match.group(1) + places_match.group(2) + places_match.group(3),
            places_match.group(1) + places_str + places_match.group(3),
        )
        return new_html, added, skipped_dup

    return html, added, skipped_dup


def main():
    parser = argparse.ArgumentParser(description="Import Foursquare places into index.html")
    parser.add_argument("--all", action="store_true", help="Import all places, not just favorites")
    parser.add_argument("--min-checkins", type=int, default=0, help="Minimum check-in count to import")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--html", default="../index.html", help="Path to index.html")
    args = parser.parse_args()

    # Load data
    json_file = "tools/foursquare_places_full.json" if args.all else "tools/foursquare_favorites.json"
    try:
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"✗ {json_file} not found — run foursquare_export.py first")
        sys.exit(1)

    places = data["places"]
    print(f"Loaded {len(places)} places from {json_file}")

    html = load_html(args.html)
    global KNOWN_CITIES
    KNOWN_CITIES = get_known_cities(html)
    print(f"Known cities in index.html: {len(KNOWN_CITIES)}")

    # Filter and group
    skipped_city = []
    new_places_by_city = defaultdict(list)

    for place in places:
        if args.min_checkins and place.get("checkin_count", 0) < args.min_checkins:
            continue

        fsq_city = place.get("city", "")
        fsq_country = place.get("country", "")
        canonical = resolve_city(fsq_city, fsq_country)

        if canonical is None:
            skipped_city.append(f"{place['name']} ({fsq_city})")
            continue

        is_fave = place.get("is_favorite", False)
        entry = build_place_entry(place, is_fave)
        new_places_by_city[canonical].append(entry)

    print(f"Places to process: {sum(len(v) for v in new_places_by_city.values())} across {len(new_places_by_city)} cities")
    print(f"Skipped (city not covered): {len(skipped_city)}")

    if args.dry_run:
        print("\n── DRY RUN ───────────────────────────────────────────────────────────────────")

    # Merge
    new_html, added, dupes = merge_places(html, new_places_by_city, dry_run=args.dry_run)

    # Report
    total_added = sum(len(v) for v in added.values())
    total_dupes = sum(len(v) for v in dupes.values())
    print(f"\n✓ Added {total_added} new places ({total_dupes} duplicates skipped)")
    for city, names in sorted(added.items()):
        print(f"  {city}: +{len(names)} ({', '.join(names[:4])}{'...' if len(names)>4 else ''})")

    if not args.dry_run and total_added > 0:
        save_html(new_html, args.html)
        print(f"\n✓ index.html updated — commit and push when ready")
        print("  git add index.html && git commit -m 'Import Foursquare places'")


if __name__ == "__main__":
    main()
