#!/usr/bin/env python3
"""
Foursquare Data Exporter - Manual Token Entry
Run this first to export your Foursquare data to JSON.
Then run foursquare_import.py to merge into index.html.
"""

import requests
import json
from datetime import datetime
from collections import defaultdict

CLIENT_ID = "J3VEPVZDVESSD0QLJVGAQYH15VMA3NYYS4TR22ZIISTW0NCY"
CLIENT_SECRET = "RPRDAXOQXN2EMXUZLPBFJFW4JYPPZ4OEGESGKJW4XZ2PCSEY"
BASE_URL = "https://api.foursquare.com/v2"


def print_instructions():
    print("=" * 70)
    print("FOURSQUARE OAUTH TOKEN - MANUAL SETUP")
    print("=" * 70)
    print()
    print("1. Open this URL in your browser:")
    print()
    auth_url = (
        f"https://foursquare.com/oauth2/authenticate"
        f"?client_id={CLIENT_ID}&response_type=token"
        f"&redirect_uri=https://seegoeat.com/"
    )
    print(f"   {auth_url}")
    print()
    print("2. Click 'Allow' to authorize the app")
    print("3. You'll be redirected to a URL that looks like:")
    print("   https://seegoeat.com/#access_token=XXXXXXXXXXXXX")
    print()
    print("4. Copy everything after 'access_token='")
    print()
    print("=" * 70)
    print()


def get_user_info(token):
    url = f"{BASE_URL}/users/self"
    params = {"oauth_token": token, "v": "20240101"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["response"]["user"]
    elif response.status_code == 401:
        print("✗ Invalid or expired token")
        return None
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
        return None


def get_user_checkins(token, limit=250, offset=0):
    url = f"{BASE_URL}/users/self/checkins"
    params = {"oauth_token": token, "v": "20240101", "limit": limit, "offset": offset}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    return response.json()


def get_user_likes(token, limit=200, offset=0):
    url = f"{BASE_URL}/users/self/venuelikes"
    params = {"oauth_token": token, "v": "20240101", "limit": limit, "offset": offset}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching likes: {response.status_code}")
        return None
    return response.json()


def categorize_venue(categories):
    if not categories:
        return "other"
    cat_name = categories[0].get("name", "").lower()
    food_kw = ["restaurant","café","coffee","food","bakery","deli","eatery","bistro",
               "diner","pizzeria","sushi","grill","kitchen","noodle","burger","sandwich",
               "taco","breakfast","cafe","steakhouse","seafood"]
    drink_kw = ["bar","pub","brewery","cocktail","wine","speakeasy","lounge",
                "nightclub","club","tavern"]
    stay_kw = ["hotel","hostel","resort","inn","motel","lodge","bed & breakfast","b&b","accommodation"]
    see_kw = ["museum","park","beach","monument","landmark","gallery","theater","theatre",
              "attraction","historic","scenic","viewpoint","garden","plaza","square",
              "castle","church","temple","mosque","cathedral","memorial"]
    if any(k in cat_name for k in food_kw):
        return "food"
    elif any(k in cat_name for k in drink_kw):
        return "drinks"
    elif any(k in cat_name for k in stay_kw):
        return "stay"
    elif any(k in cat_name for k in see_kw):
        return "see"
    return "other"


def maps_url(place):
    if place.get("lat") and place.get("lng"):
        return f"https://www.google.com/maps/search/?api=1&query={place['lat']},{place['lng']}"
    q = f"{place['name']} {place['city']} {place['country']}".replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={q}"


def transform_checkin(checkin):
    venue = checkin.get("venue", {})
    loc = venue.get("location", {})
    place = {
        "name": venue.get("name", "Unknown"),
        "category": categorize_venue(venue.get("categories", [])),
        "foursquare_category": (venue.get("categories") or [{}])[0].get("name", ""),
        "address": loc.get("address", ""),
        "city": loc.get("city", ""),
        "state": loc.get("state", ""),
        "country": loc.get("country", ""),
        "lat": loc.get("lat"),
        "lng": loc.get("lng"),
        "checkin_count": 1,
        "last_visited": datetime.fromtimestamp(checkin.get("createdAt", 0)).strftime("%Y-%m-%d"),
        "shout": checkin.get("shout", ""),
        "foursquare_id": venue.get("id", ""),
    }
    place["google_maps_url"] = maps_url(place)
    return place


def transform_like(venue):
    loc = venue.get("location", {})
    place = {
        "name": venue.get("name", "Unknown"),
        "category": categorize_venue(venue.get("categories", [])),
        "foursquare_category": (venue.get("categories") or [{}])[0].get("name", ""),
        "address": loc.get("address", ""),
        "city": loc.get("city", ""),
        "state": loc.get("state", ""),
        "country": loc.get("country", ""),
        "lat": loc.get("lat"),
        "lng": loc.get("lng"),
        "checkin_count": 0,
        "last_visited": None,
        "is_favorite": True,
        "shout": "",
        "foursquare_id": venue.get("id", ""),
    }
    place["google_maps_url"] = maps_url(place)
    return place


def fetch_all_checkins(token):
    all_checkins, offset = [], 0
    while True:
        print(f"  Fetching check-ins (offset: {offset})...")
        data = get_user_checkins(token, limit=250, offset=offset)
        if not data or "response" not in data:
            break
        items = data["response"]["checkins"]["items"]
        if not items:
            break
        all_checkins.extend(items)
        if len(all_checkins) >= data["response"]["checkins"]["count"]:
            break
        offset += 250
    return all_checkins


def fetch_all_likes(token):
    all_likes, offset = [], 0
    while True:
        print(f"  Fetching liked venues (offset: {offset})...")
        data = get_user_likes(token, limit=200, offset=offset)
        if not data or "response" not in data:
            break
        items = data["response"]["venues"]["items"]
        if not items:
            break
        all_likes.extend(items)
        if len(all_likes) >= data["response"]["venues"]["count"]:
            break
        offset += 200
    return all_likes


def aggregate_places(places, liked_ids):
    venue_map = {}
    for place in places:
        vid = place["foursquare_id"]
        if vid in liked_ids:
            place["is_favorite"] = True
        if vid in venue_map:
            venue_map[vid]["checkin_count"] += 1
            lv = place.get("last_visited")
            if lv and (not venue_map[vid].get("last_visited") or lv > venue_map[vid]["last_visited"]):
                venue_map[vid]["last_visited"] = lv
            if place["shout"]:
                venue_map[vid].setdefault("notes", [])
                if place["shout"] not in venue_map[vid]["notes"]:
                    venue_map[vid]["notes"].append(place["shout"])
            if place.get("is_favorite"):
                venue_map[vid]["is_favorite"] = True
        else:
            if place["shout"]:
                place["notes"] = [place["shout"]]
            venue_map[vid] = place
    return list(venue_map.values())


def export_data(token):
    print("\nVerifying token...")
    user = get_user_info(token)
    if not user:
        return False
    print(f"✓ {user.get('firstName', '')} {user.get('lastName', '')}")

    print("\nFetching check-ins...")
    checkins = fetch_all_checkins(token)
    print(f"✓ {len(checkins)} check-ins")

    print("\nFetching liked venues...")
    likes = fetch_all_likes(token)
    print(f"✓ {len(likes)} liked venues")

    places = [transform_checkin(c) for c in checkins]
    liked_ids = {v.get("id") for v in likes}
    checkin_ids = {p["foursquare_id"] for p in places}
    for venue in likes:
        if venue.get("id") not in checkin_ids:
            places.append(transform_like(venue))

    places = aggregate_places(places, liked_ids)
    favorites = [p for p in places if p.get("is_favorite")]

    cities = defaultdict(lambda: {"food": [], "drinks": [], "stay": [], "see": [], "other": []})
    for p in places:
        cities[p["city"] or "Unknown"][p["category"]].append(p)

    out_dir = "tools"
    with open(f"{out_dir}/foursquare_places_full.json", "w", encoding="utf-8") as f:
        json.dump({"total": len(places), "favorites": len(favorites),
                   "exported_at": datetime.now().isoformat(), "places": places}, f, indent=2, ensure_ascii=False)

    fav_cities = defaultdict(lambda: {"food": [], "drinks": [], "stay": [], "see": [], "other": []})
    for p in favorites:
        fav_cities[p["city"] or "Unknown"][p["category"]].append(p)

    with open(f"{out_dir}/foursquare_favorites.json", "w", encoding="utf-8") as f:
        json.dump({"total": len(favorites), "exported_at": datetime.now().isoformat(),
                   "places": favorites}, f, indent=2, ensure_ascii=False)

    with open(f"{out_dir}/foursquare_token.txt", "w") as f:
        f.write(token)

    print(f"\n✓ Exported {len(places)} unique places ({len(favorites)} favorites) across {len(cities)} cities")
    print("✓ Files: tools/foursquare_places_full.json, tools/foursquare_favorites.json")
    print("\nNext step: run  python3 tools/foursquare_import.py")
    return True


def main():
    try:
        with open("tools/foursquare_token.txt") as f:
            token = f.read().strip()
        if token and get_user_info(token):
            print("✓ Using saved token")
            if input("Use saved token? (y/n): ").lower() == "y":
                export_data(token)
                return
    except FileNotFoundError:
        pass

    print_instructions()
    token = input("Enter your Foursquare OAuth access token:\n> ").strip()
    if token:
        export_data(token)
    else:
        print("No token provided.")


if __name__ == "__main__":
    main()
