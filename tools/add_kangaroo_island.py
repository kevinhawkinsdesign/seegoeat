#!/usr/bin/env python3
"""Add Kangaroo Island to data.js."""
import json, urllib.parse, re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'data.js'

CITY = "Kangaroo Island"
COUNTRY = "Australia"
EMOJI = "🇦🇺"
TAGLINE = "🐨 Australia's third-largest island, an hour's ferry from South Australia — wild beaches, Remarkable Rocks balanced on a granite dome, sea lions sleeping on the sand, koalas in the manna gums, and a small but seriously talented community of distillers, winemakers, and chefs."
COORDS = [-35.7752, 137.2143]
REGION = "Oceania"

# (name, category, description, rating)
PLACES = [
    # Food
    ("Sunset Food & Wine", "Food", "Cliff-top restaurant above American River with floor-to-ceiling views across the strait. Modern Australian cooking that leans heavily on the island's own producers — King George whiting, marron, abalone, KI honey. The standout meal on the island.", 4.7),
    ("The Enchanted Fig Tree", "Food", "Long-table lunch under the canopy of a 100-year-old Moreton Bay fig at Snug Cove. Seasonal four-course menu, all KI produce, runs from spring through autumn. A bucket-list outdoor dining experience.", 4.9),
    ("Cape Willoughby Lazy Lobster Co.", "Food", "Whole southern rock lobsters cooked simply at a shack on the wild eastern tip of the island, eaten at picnic tables looking out at the lighthouse. As good as seafood gets.", 4.7),
    ("Bella Restaurant", "Food", "Italian-inflected island restaurant in Kingscote with a wood-fired oven, hand-rolled pasta, and a deep KI wine list. Casual, warm, the locals' spot for a good night out.", 4.6),
    ("Stokes Bay Cafe", "Food", "Beach-shack café above one of the island's most beautiful hidden beaches — fish tacos, KI ploughman's, cold local beer. Lunch with sand on your feet.", 4.5),
    ("Penneshaw Hotel", "Food", "Honest Australian pub a stagger from the ferry terminal — fresh whiting, fat chips, schooners of Coopers. The first or last meal of the trip.", 4.3),

    # Nightlife / Drinks / Cellar Doors
    ("Kangaroo Island Spirits", "Nightlife", "Australia's first dedicated gin distillery, started in 2006 in Cygnet River. Wild-juniper-and-coastal-botanical gins poured at a cellar door surrounded by their own gardens. The Wild Gin is the bottle to take home.", 4.7),
    ("False Cape Wines", "Nightlife", "Family-owned cellar door perched above the sea on the eastern side of the island. Shiraz with serious structure and a tasting room with one of the best views in South Australia.", 4.6),
    ("Bay of Shoals Wines", "Nightlife", "Kingscote's lakeside winery with picnic tables on the lawn, an excellent Riesling, and oysters straight from the bay paired with whatever's open. Lunch material.", 4.5),
    ("Kangaroo Island Brewery", "Nightlife", "Small batch brewery in Cygnet River doing a tight range — pale ale, IPA, Saison — all on tap at a tin-shed cellar door with a fire pit out the back.", 4.6),
    ("The Islander Estate Vineyards", "Nightlife", "Bordeaux-blend specialist set up by a former Margaux winemaker — serious wines from a beautiful estate near Parndana. Tastings by appointment, worth the booking.", 4.5),

    # Places to Stay
    ("Southern Ocean Lodge", "Places to Stay", "The legendary clifftop lodge above Hanson Bay, rebuilt after the 2020 bushfires and reopened in 2023 — even better than before. All-inclusive luxury, panoramic Southern Ocean views, the most considered hospitality in Australia.", 4.9),
    ("Sea Dragon Lodge", "Places to Stay", "Sustainable eco-lodge on a 1,000-hectare property on the eastern side of the island, with private villas overlooking the ocean and dinners cooked on the property. Quieter and more intimate than the alternatives.", 4.7),
    ("Mercure Kangaroo Island Lodge", "Places to Stay", "The reliable mid-range option in American River — comfortable rooms, a pool, a restaurant with bay views. Walk to the boatshed where pelicans gather at sunset.", 4.2),
    ("Lifetime Private Retreats", "Places to Stay", "A collection of architecturally distinct private homes scattered across remote parts of the island — Snelling Beach, Wreckers Beach, Stokes Bay. Self-catered, panoramic, no neighbours.", 4.8),

    # Places to See
    ("Remarkable Rocks (Flinders Chase NP)", "Places to See", "A cluster of enormous lichen-orange granite boulders balanced on a domed headland 75 metres above the Southern Ocean. The most-photographed thing on the island for good reason. Go at dawn or last light.", 4.8),
    ("Admirals Arch (Flinders Chase NP)", "Places to See", "A natural rock archway hung with limestone stalactites at the south-west tip of the island, where 7,000 New Zealand fur seals haul out on the rocks below. The boardwalk down to it is a short, dramatic walk.", 4.8),
    ("Seal Bay Conservation Park", "Places to See", "One of the only places on earth where you can walk on a beach alongside a colony of wild Australian sea lions — a ranger-guided experience that gets you within a respectful few metres. Around 800 of an endangered species.", 4.8),
    ("Hanson Bay Wildlife Sanctuary", "Places to See", "A 600-hectare conservation reserve next to Southern Ocean Lodge with the best chance of seeing wild koalas in the manna gums along the Koala Walk. Self-guided, 1.5km loop, kangaroos and echidnas too.", 4.7),
    ("Stokes Bay", "Places to See", "A hidden white-sand beach reached only via a tunnel through the granite headland at one end. Calm rock-pool swimming, dramatic cliffs, almost always empty. The island's loveliest beach.", 4.8),
    ("Vivonne Bay", "Places to See", "A long arc of white sand on the south coast, voted Australia's best beach more than once. The Vivonne Bay Bistro at the jetty does excellent local seafood lunches.", 4.7),
    ("Little Sahara", "Places to See", "Pure white sand dunes rising 70 metres out of the bush, where you can rent a sandboard and ride down. Bizarre, brilliant, and just the right kind of fun.", 4.6),
    ("Raptor Domain", "Places to See", "Free-flight birds of prey display in the centre of the island — wedge-tailed eagles, barn owls, a barking owl that talks to you. Genuinely thrilling and run by serious conservationists.", 4.8),
    ("Cape du Couedic Lighthouse", "Places to See", "1909 lighthouse on the south-west tip near Admirals Arch and Remarkable Rocks. The three keepers' cottages can be rented; the cliffs around them are some of the most dramatic on the island.", 4.7),
    ("Clifford's Honey Farm", "Places to See", "Working farm producing pure Ligurian honey from the only protected strain of bees left in the world (Kangaroo Island has been a Ligurian-bee sanctuary since 1885). Honey ice cream, tastings, an excellent shop.", 4.6),
    ("Emu Bay Lavender Farm", "Places to See", "Rows of purple lavender against a coastal backdrop on the north coast, with a small café doing lavender scones and a shop selling oils, soaps, and gelato. Photo-perfect in summer.", 4.5),
    ("Kingscote Pier (Pelican Feeding)", "Places to See", "Daily 5pm pelican feeding at the Kingscote jetty by 'John the Pelican Man' — a quirky island tradition that's been running for decades. Show up early; bring a hat.", 4.5),
    ("American River Pelican Lagoon", "Places to See", "Quiet, sheltered estuary on the north coast known for kayaking among pelicans and resident dolphins, plus extraordinary sunsets from the boatshed. The trip's most peaceful hour.", 4.6),
    ("Murray Lagoon (Cape Gantheaume CP)", "Places to See", "The island's largest freshwater lagoon and one of the best birdwatching spots in South Australia — black swans, ibis, sea eagles, occasional brolgas. A short detour worth taking.", 4.5),
]

# ─── Edit data.js ─────────────────────────────────────────────────────────────
js = DATA.read_text(encoding='utf-8')

def extract_object(text, marker):
    i = text.find(marker); obj_start = text.find('{', i)
    depth=0; in_dq=False; in_sq=False; esc=False
    for j in range(obj_start, len(text)):
        ch=text[j]
        if in_dq:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch=='"': in_dq=False
        elif in_sq:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch=="'": in_sq=False
        else:
            if ch=='"': in_dq=True
            elif ch=="'": in_sq=True
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0: return obj_start, j+1

def maps_url(name, city):
    q = urllib.parse.quote_plus(f"{name} {city}")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

# PLACES
ps, pe = extract_object(js, "const PLACES=")
places = json.loads(js[ps:pe])
entries = []
for name, cat, desc, *rest in PLACES:
    rating = rest[0] if rest else None
    e = {"n": name, "c": cat, "d": desc, "u": maps_url(name, CITY)}
    if rating is not None: e["r"] = rating
    entries.append(e)
places.setdefault(CITY, []).extend(entries)
places[CITY].sort(key=lambda p: p["n"].lower())
js = js[:ps] + json.dumps(places, ensure_ascii=False, separators=(',', ':')) + js[pe:]
print(f"PLACES: {CITY} → {len(entries)} entries")

# META
ms, me = extract_object(js, "const META=")
meta = json.loads(js[ms:me])
if CITY not in meta:
    meta[CITY] = {"country": COUNTRY, "emoji": EMOJI, "tagline": TAGLINE}
js = js[:ms] + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + js[me:]
print(f"META: added {CITY}")

# COORDS
if f"'{CITY}':" not in js.split('const COORDS=')[1].split('};')[0]:
    lat, lng = COORDS
    js = js.replace("const COORDS={", f"const COORDS={{'{CITY}':[{lat},{lng}],", 1)
print("COORDS: added")

# REGIONS
pat = re.compile(r"('" + re.escape(REGION) + r"':\s*\[)([^\]]+)(\])")
m = pat.search(js)
inner = m.group(2)
if f"'{CITY}'" not in inner:
    items = [s.strip().strip("'") for s in inner.split(",") if s.strip()]
    items.append(CITY)
    items.sort(key=str.lower)
    new_inner = ", ".join(f"'{c}'" for c in items)
    js = pat.sub(lambda _m: _m.group(1) + new_inner + _m.group(3), js, count=1)
print(f"REGIONS: added {CITY} to {REGION}")

DATA.write_text(js, encoding='utf-8')
print(f"\nDone. {CITY} now has {len(places[CITY])} places.")
