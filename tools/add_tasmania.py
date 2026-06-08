#!/usr/bin/env python3
"""Add Tasmania as a curated city entry."""
import json, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data.js'

CITY = "Tasmania"
COUNTRY = "Australia"
EMOJI = "🇦🇺"
TAGLINE = "🏝️ Australia's wild southern island — sandstone Hobart on the Derwent, MONA's art-world provocations, kelp forests and quartz-sand beaches, single-malt distilleries, and some of the best produce in the country. Small in population, huge in flavour."
COORDS = [-42.0409, 146.8087]
REGION = "Oceania"

# (name, category, description, rating, is_favorite)
PLACES = [
    # Food
    ("Franklin", "Food", "Set inside a converted Ford showroom on Hobart's waterfront, Franklin built its reputation on wood-fired cooking that lets Tasmanian produce — kingfish, beef, brassicas — do the talking. The open kitchen, the curved bar, the focused wine list. The best dinner in town.", 4.7, True),
    ("Templo", "Food", "A 20-seat Italian-inspired set menu in North Hobart that punches far above its size. The pasta is hand-cut, the wine list is brilliantly opinionated, and the room feels like dining in a friend's incredibly stylish home. Book weeks ahead.", 4.7, True),
    ("Fico", "Food", "Chef Federica Andrisani's wood-fired neighbourhood restaurant in Hobart, doing Italian cooking with Tasmanian ingredients and zero pretence. The bread alone is worth the visit, and the burrata is the platonic ideal.", 4.6, True),
    ("Dier Makr", "Food", "An intimate restaurant pushing modern Australian cooking forward with foraged and small-producer ingredients. Kobi Ruzicka's plates are precise and inventive — fermented this, smoked that — without ever feeling cold.", 4.6, True),
    ("Stillwater", "Food", "A converted 1830s flour mill on the Tamar River in Launceston, doing some of the most refined cooking in the state. The tasting menu is the move; the views across the river at dusk are a bonus.", 4.5, True),
    ("Black Cow Bistro", "Food", "If you want to understand why Tasmanian beef is the country's best, eat at Black Cow in Launceston. Dry-aged, grass-fed, cooked over coals. The kind of steakhouse that takes meat seriously without being precious about it.", 4.6, True),
    ("The Agrarian Kitchen", "Food", "Rodney Dunn's farm-to-table restaurant in a converted asylum building in New Norfolk, half an hour from Hobart. The vegetables come from the garden out back, the meat from down the road. A pilgrimage worth making.", 4.6, True),
    ("Get Shucked", "Food", "Bruny Island oysters, shucked to order at a yellow shack by the water. Order a dozen, a glass of Tasmanian fizz, and watch the boats. The simplest, best meal of the trip.", 4.7, True),
    ("Bruny Island Cheese Co.", "Food", "Nick Haddow's cheesery and brewery on Bruny Island. Pick up a board, a sourdough loaf, and a bottle of their farmhouse ale, and eat under the trees. A masterclass in doing one thing extremely well.", 4.6, True),
    ("Pigeon Whole Bakers", "Food", "The sourdough is the best in Tasmania, the morning bun is the best anywhere. Get there early — they sell out by lunch and the line tells you everything.", 4.5, True),
    ("Jackman & McRoss", "Food", "Battery Point institution since the early '90s. The pies are famous for a reason, the pastries are excellent, and the courtyard tables are perfect on a sunny Hobart morning.", 4.4),
    ("Devil's Corner", "Food", "Cellar door and lookout on the east coast with the best view in Tasmania — Hazards range across the bay, fizzy on the tongue, oysters from the next paddock. The food trucks alongside are surprisingly good.", 4.5, True),

    # Nightlife
    ("Lark Distillery Cellar Door", "Nightlife", "The original Tasmanian single-malt distillery, opened in 1992 when it was still illegal to distil in small batches. Lark put Tasmanian whisky on the map. The Hobart waterfront cellar door is the place to taste through the range.", 4.5, True),
    ("Sullivans Cove Distillery", "Nightlife", "World-beating Tasmanian whisky — they've won 'best in the world' titles that genuinely changed how the global whisky market sees Australia. Book a tour at the distillery in Cambridge.", 4.6, True),
    ("Preachers", "Nightlife", "A pub built around a converted double-decker bus parked in the beer garden. Battery Point locals' choice for a casual pint with personality. Live music most weekends.", 4.4),
    ("Society Salamanca", "Nightlife", "Hobart's best cocktail bar, hidden upstairs off Salamanca Place. The list is creative without being fussy, the room is dark and warm, and the bartenders know what they're doing.", 4.5, True),
    ("Willing Bros Wine Merchants", "Nightlife", "A wine shop that's also a tiny natural wine bar in North Hobart. Sit at the counter, ask what's open, and trust the answer. The Tasmanian skin-contact selection is one of the best in the country.", 4.6),

    # Places to Stay
    ("Saffire Freycinet", "Places to Stay", "All-inclusive luxury lodge on the east coast overlooking the Hazards. Twenty private suites, a stunning restaurant, oyster farm experiences in the bay. One of the great hotels of Australia.", 4.9, True),
    ("Pumphouse Point", "Places to Stay", "A 1940s hydroelectric pumphouse converted into an 18-room hotel, sitting 250m out on Lake St Clair, connected to the shore by a single causeway. Genuinely unlike anywhere else. All-inclusive, contemplative, surreal.", 4.8, True),
    ("MACq 01 Hotel", "Places to Stay", "Hobart's storytelling hotel on the Hunter Street waterfront. Every room is themed around a Tasmanian character — a convict, a sailor, a bushranger — done with real care. Walk to MONA's ferry, walk to dinner.", 4.6, True),
    ("The Henry Jones Art Hotel", "Places to Stay", "Built into a former jam factory on the Hobart docks, with original brick walls hung with contemporary Tasmanian art. The art is the point; the location is unbeatable. Salamanca and the museums are at the door.", 4.6, True),
    ("Cradle Mountain Lodge", "Places to Stay", "The classic basecamp for Cradle Mountain — alpine cabins with fireplaces, a spa in the woods, and walking trails leaving from the door. The Highland restaurant is excellent. Wallabies on the lawn at dawn.", 4.5, True),

    # Places to See
    ("MONA — Museum of Old and New Art", "Places to See", "David Walsh's subterranean private museum cut into a Hobart cliff is the reason most travellers come to Tasmania. Confrontational, brilliant, occasionally absurd, never boring. Take the ferry from Hobart and give it a full day.", 4.6, True),
    ("Salamanca Market", "Places to See", "Saturday mornings in Hobart: 300 stalls of Tasmanian produce, makers, and oddities along the sandstone warehouses of Salamanca Place. The honey, the cheese, the woollens, the people-watching. Don't skip it.", 4.7, True),
    ("Wineglass Bay & Freycinet National Park", "Places to See", "The arc of white sand between the Hazards mountains is the postcard shot of Tasmania for good reason. The lookout walk is short and worth it; the descent to the beach is longer and even more worth it.", 4.8, True),
    ("Cradle Mountain–Lake St Clair National Park", "Places to See", "Dolerite peaks, button grass plains, ancient pencil pines reflected in glacial lakes. The Dove Lake Circuit (6km) is the iconic walk; the full Overland Track (six days) is one of Australia's great hikes.", 4.8, True),
    ("Bay of Fires", "Places to See", "Orange-lichen-covered granite boulders against turquoise water and quartz-white sand, stretching the entire north-east coast. Camp at one of the free sites near Binalong Bay and wake up to it.", 4.8, True),
    ("Bruny Island", "Places to See", "A day trip from Hobart by ferry: oysters, cheese, whisky, fairy penguins at dusk, and a sandy isthmus called The Neck where you can climb a wooden staircase for one of the great views in the state.", 4.7, True),
    ("Port Arthur Historic Site", "Places to See", "The most haunting and best-preserved convict ruins in Australia, on a wind-blown peninsula east of Hobart. The night ghost tour is genuinely affecting; the boat trip to the Isle of the Dead deepens the story.", 4.7, True),
    ("kunanyi / Mt Wellington", "Places to See", "The mountain that watches over Hobart. Drive or hike to the 1,271m summit for a panorama from the Tasman Peninsula to the Southwest wilderness. Bring layers — it has snow when the city has sun.", 4.7, True),
    ("Russell Falls (Mt Field National Park)", "Places to See", "A three-tier waterfall in temperate rainforest, twenty minutes from the carpark on a flat boardwalk. Easy enough for anyone, beautiful enough to feel earned.", 4.8, True),
    ("Maria Island", "Places to See", "Car-free island national park reachable by short ferry — convict ruins, painted cliffs of swirled sandstone, and wombats that will walk right past your boot. Day trip or camp overnight.", 4.8, True),
    ("Battery Point", "Places to See", "Hobart's oldest residential district, a tangle of narrow lanes and pastel weatherboard cottages on the hill above the harbour. Wander aimlessly, end up at a pub.", 4.6),
    ("Tahune Adventures", "Places to See", "Airwalk through the canopy of one of Tasmania's last great temperate rainforests, suspended 30 metres above the Picton and Huon rivers. The Eagle Hang Glider if you're feeling brave.", 4.4),
]

# ─── Edit data.js ─────────────────────────────────────────────────────────────
js = DATA.read_text(encoding='utf-8')

def extract_object(text, marker):
    i = text.find(marker)
    obj_start = text.find('{', i)
    depth = 0; in_dq = False; in_sq = False; esc = False
    for j in range(obj_start, len(text)):
        ch = text[j]
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
    raise ValueError

# 1. PLACES
ps, pe = extract_object(js, "const PLACES=")
places = json.loads(js[ps:pe])
def maps_url(name, city):
    q = urllib.parse.quote_plus(f"{name} {city}")
    return f"https://www.google.com/maps/search/?api=1&query={q}"
new_entries = []
for name, cat, desc, *rest in PLACES:
    rating = rest[0] if rest else None
    is_fav = rest[1] if len(rest) > 1 else False
    e = {"n": name, "c": cat, "d": desc, "u": maps_url(name, CITY)}
    if rating is not None: e["r"] = rating
    if is_fav: e["f"] = True
    new_entries.append(e)
places.setdefault(CITY, []).extend(new_entries)
places[CITY].sort(key=lambda p: p["n"].lower())
new_places_str = json.dumps(places, ensure_ascii=False, separators=(',', ':'))
js = js[:ps] + new_places_str + js[pe:]
print(f"PLACES: added {len(new_entries)} entries to {CITY}")

# 2. META
ms, me = extract_object(js, "const META=")
meta = json.loads(js[ms:me])
if CITY not in meta:
    meta[CITY] = {"country": COUNTRY, "emoji": EMOJI, "tagline": TAGLINE}
new_meta_str = json.dumps(meta, ensure_ascii=False, separators=(',', ':'))
js = js[:ms] + new_meta_str + js[me:]
print(f"META: added {CITY}")

# 3. COORDS — single-quoted JS object; insert at top
if f"'{CITY}':" not in js.split('const COORDS=')[1].split('};')[0]:
    lat, lng = COORDS
    entry = f"'{CITY}':[{lat},{lng}],"
    js = js.replace("const COORDS={", "const COORDS={" + entry, 1)
    print(f"COORDS: added {CITY}")

# 4. REGIONS
import re
pat = re.compile(r"('" + re.escape(REGION) + r"':\s*\[)([^\]]+)(\])")
m = pat.search(js)
assert m
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
