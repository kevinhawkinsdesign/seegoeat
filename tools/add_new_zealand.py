#!/usr/bin/env python3
"""Add Auckland, Wellington, and Queenstown to the data."""
import json, urllib.parse, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data.js'

CITIES = {
    "Auckland": {
        "country": "New Zealand", "emoji": "🇳🇿",
        "tagline": "⛵ New Zealand's biggest city, draped over two harbours and 48 volcanoes — Pacific food, world-class wineries on Waiheke Island, and a coastline that's never more than a ferry ride away.",
        "coords": [-36.8485, 174.7633],
        "places": [
            ("Amano", "Food", "A buzzy Britomart all-day eatery with a wood-fired oven at its heart and an in-house bakery. Hand-rolled pasta, charred wood-fired vegetables, the best focaccia in town. The kind of restaurant Auckland built its reputation on.", 4.5, True),
            ("Ahi", "Food", "Native Pacific ingredients cooked over open flame in the heart of the city. Chef Ben Bayly's menu reads like a love letter to Aotearoa — Te Mata mushrooms, Akaroa salmon, hāngī-cooked lamb. Genuinely original New Zealand cooking.", 4.6, True),
            ("Cazador", "Food", "Wild game, charcuterie, foraged greens. The Mt Eden bistro that introduced a generation of Aucklanders to the idea that 'paddock to plate' could be precise rather than rustic. The terrine board is unmissable.", 4.6, True),
            ("Apéro", "Food", "Tiny Karangahape Road bistro with bare bulbs, marble tables, and a wine list that takes you around the natural-wine world. Order the chicken liver parfait and a glass of something orange.", 4.5, True),
            ("Bestie", "Food", "Café-bakery in St Kevin's Arcade with sun-trap tables, killer doughnuts, and proper coffee. A Saturday-morning Auckland ritual.", 4.5),
            ("Daily Bread", "Food", "Multi-bakery group quietly making the best sourdough and croissants in the city. The Point Chev original is the move — buy a loaf for later, eat a pain au chocolat now.", 4.6),
            ("Mr Morris", "Food", "Britomart fine-dining in a beautifully restored heritage room. Chef Sid Sahrawat's modern Indian-inflected menu — kingfish ceviche, lamb with tamarind, Manuka-smoked everything — is one of the city's most polished tables.", 4.5, True),
            ("Lilian", "Nightlife", "Wine bar in the basement of an old Newmarket building, with low ceilings, an extensive natural list, and snacks that are far better than they need to be.", 4.6, True),
            ("Annabel's", "Nightlife", "A small, candle-lit Karangahape Road wine bar that nails the after-dinner glass — chosen with care, poured generously, sound-tracked perfectly. The kind of room you don't want to leave.", 4.5, True),
            ("Caretaker", "Nightlife", "Speakeasy-style cocktail bar tucked behind an unmarked door in Britomart. The bartenders ask what you're in the mood for, then make it. Trust them.", 4.5, True),
            ("Hotel Britomart", "Places to Stay", "The first 5 Green Star hotel in New Zealand, set inside three restored brick warehouses on the waterfront. Beautifully minimal rooms, kingfisher-blue tiles, and a ground-floor restaurant (kingi) doing the country's best sustainable seafood.", 4.7, True),
            ("QT Auckland", "Places to Stay", "Art-led design hotel on Viaduct Harbour with a maximalist sense of fun — pink velvet, brass detailing, harbour-view rooms. Esther, the in-house Levantine restaurant, is destination-worthy on its own.", 4.5, True),
            ("Park Hyatt Auckland", "Places to Stay", "Spectacular waterfront luxury at the edge of the Viaduct. Floor-to-ceiling harbour windows, an indoor lap pool, and quiet, oversized rooms. The most international-feeling hotel in town.", 4.6, True),
            ("Waiheke Island", "Places to See", "Forty minutes by ferry: vineyards on every hill, olive groves, oyster bars at the bottom of cliffs, and beaches where you'll spend longer than you planned. Mudbrick, Cable Bay, and Te Motu are the wineries; Oyster Inn is lunch.", 4.8, True),
            ("Auckland Art Gallery Toi o Tāmaki", "Places to See", "Aotearoa's largest art museum, with the country's most important holdings of Māori and Pacific contemporary art alongside European old masters. The kauri-clad atrium is a building worth visiting on its own.", 4.6, True),
            ("Mount Eden / Maungawhau", "Places to See", "A 196m volcanic cone in the middle of the city, with a 360° view from the rim across both harbours and out to Rangitoto. Twenty minutes' walk from the top of K' Road. Go at golden hour.", 4.7, True),
            ("Karangahape Road", "Places to See", "Auckland's inner-city ridge of vintage shops, queer bars, independent galleries, and the city's best ethnic eating. Walk it from top to bottom; eat your way through.", 4.5),
            ("Piha Beach", "Places to See", "Black-sand surf beach on the Tasman coast, 40 minutes west of the city through Waitākere rainforest. Lion Rock at the centre of it, dangerous waves, dramatic in any weather. The classic Auckland day trip.", 4.7, True),
            ("Goldie Estate (Waiheke)", "Places to See", "The original Waiheke winery — small, family-run, with a tasting room overlooking the vines. Their Bordeaux blends are the island's most awarded reds.", 4.6),
        ],
    },
    "Wellington": {
        "country": "New Zealand", "emoji": "🇳🇿",
        "tagline": "☕ The world's coolest little capital — wedged between hills and harbour, fuelled by independent coffee, a stacked craft beer scene, and a film-and-creative culture that punches absurdly above its weight.",
        "coords": [-41.2865, 174.7762],
        "places": [
            ("Hiakai", "Food", "Monique Fiso's Wellington restaurant doing modern Māori cuisine at the highest level — kawakawa, karengo, hāngī-cooked everything, paired with native ingredients you've never heard of. Genuinely important cooking. Book months ahead.", 4.7, True),
            ("Logan Brown", "Food", "Wellington fine-dining in a converted 1920s bank, with a tasting menu rooted in New Zealand land and sea — pāua ravioli, Cervena venison, Bluff oysters. Old-school in the best way.", 4.7, True),
            ("Ortega Fish Shack", "Food", "Wood-fired Mediterranean seafood in a colourful Courtenay Place room. The whole-fish baked in salt is the move. A Wellington classic for two decades.", 4.6, True),
            ("Loretta", "Food", "Cuba Street all-day bistro with a wood oven, perfect cocktails, and a brunch that's a near-religious experience. The eggs Florentine and a glass of orange wine. Sunday at its best.", 4.5),
            ("Fidel's", "Food", "Cuba Street institution since 1996 — Cuban-themed, slightly chaotic, open late, and home to the best fries-with-aioli in town. Order a Heaven on Earth and stay all afternoon.", 4.4),
            ("Sweet Mother's Kitchen", "Food", "New Orleans–inspired diner on Courtenay Place: gumbo, po'boys, cornbread, a brunch line out the door. Comforting in any weather (and Wellington has every weather).", 4.4),
            ("Whitebait", "Food", "Refined Wellington restaurant focused exclusively on what comes out of New Zealand waters. The set menu changes daily with the catch; the waterfront views are a bonus.", 4.5, True),
            ("Goldings Free Dive", "Nightlife", "Cuba Street craft beer bar with a rotating tap list of the country's best small-batch brewers, a cult pizza menu from Pizza Pomodoro next door, and a courtyard full of regulars.", 4.6, True),
            ("Hashigo Zake", "Nightlife", "The original Wellington craft beer cellar bar — narrow, no-nonsense, taps rotating constantly. The bar that helped start New Zealand's craft beer wave.", 4.6),
            ("CGR Merchant & Co.", "Nightlife", "Underground cocktail bar inside an old Chinese grocery on Courtenay Place. The list is precise, the room is dim and warm, and the back booth is the move.", 4.5, True),
            ("Havana Bar", "Nightlife", "Cuba Street bar set across two converted wooden cottages, with rum cocktails, late-night dancing, and the most laid-back atmosphere in town. Wellington nightlife in a nutshell.", 4.5),
            ("QT Wellington", "Places to Stay", "Waterfront art hotel with views straight across the harbour to the Rimutaka ranges, eccentric design throughout, and Hippopotamus — a French restaurant that's been a Wellington fixture for years.", 4.5, True),
            ("Sofitel Wellington", "Places to Stay", "Quiet luxury just up the hill from the waterfront, with the city's most reliable rooms, an excellent breakfast, and a location that puts you a five-minute walk from everything.", 4.6),
            ("Ohtel Wellington", "Places to Stay", "Boutique 1960s-styled hotel on Oriental Parade with harbour-view rooms, mid-century furniture chosen with care, and a beach across the road for morning walks.", 4.6, True),
            ("Te Papa Tongarewa", "Places to See", "New Zealand's national museum, free to enter, six floors deep on the waterfront. The colossal squid, the giant Tāne Mahuta carving, the moving Gallipoli exhibition. Give it half a day.", 4.7, True),
            ("Wellington Cable Car & Botanic Garden", "Places to See", "Take the 1902 red cable car up to Kelburn for the postcard view across the city, then walk down through 25 hectares of botanic garden back to Lambton Quay. The classic Wellington morning.", 4.6, True),
            ("Mount Victoria Lookout", "Places to See", "The 196m hill above the city with the best 360° view in Wellington — harbour, peninsula, mountains, on a clear day the South Island. A great sunset spot if you can find parking.", 4.8, True),
            ("Zealandia", "Places to See", "Predator-fenced urban ecosanctuary in the hills above the city, where you can see (and more often hear) tūī, kākā, takahē, and the country's only flighted nocturnal parrot. The two-hour walking loop is the move.", 4.7, True),
            ("Cuba Street", "Places to See", "The city's creative spine — vintage shops, record stores, café terraces spilling onto the pedestrianised stretch, the Bucket Fountain that no one can quite explain. Wander it slowly.", 4.7, True),
            ("Weta Workshop Tour (Mirimar)", "Places to See", "Behind-the-scenes tour of the workshop that built Lord of the Rings, Avatar, and District 9, in suburban Miramar. Practical magic — armouries, prosthetics, miniature sets. Geeky in the best way.", 4.7, True),
        ],
    },
    "Queenstown": {
        "country": "New Zealand", "emoji": "🇳🇿",
        "tagline": "🏔️ Alpine resort town wedged against Lake Wakatipu with the jagged Remarkables across the water — adventure capital of the world, with a food and wine scene (Central Otago Pinot) that's quietly become world-class.",
        "coords": [-45.0312, 168.6626],
        "places": [
            ("Rātā", "Food", "Josh Emett's contemporary New Zealand restaurant in a forest courtyard a block off the lake. Hand-dived scallops, lamb from down the road, an excellent Central Otago wine list. Polished without being precious.", 4.6, True),
            ("Botswana Butchery", "Food", "Lakefront fine-dining in a heritage homestead with roaring fires and one of the deepest wine cellars in the country. Aged steaks, fresh fish, an old-school sense of occasion.", 4.6, True),
            ("Amisfield Bistro & Cellar Door", "Food", "Out of town toward Arrowtown, the country's most beautiful winery restaurant — stone walls, oak fires, a 'trust the kitchen' four-course menu paired with Amisfield's exceptional Pinots. The lunch of the trip.", 4.7, True),
            ("Sherwood", "Food", "A sustainability-driven hotel restaurant with views over the lake to the mountains. Garden-grown produce, wood-fired everything, surprising vegetable cooking. Skip the resorts; eat here.", 4.5, True),
            ("Fergburger", "Food", "The Queenstown burger, open until 5am, with a queue down the block at any hour. It's a burger — but it's a really good burger. Eat it on the pier after a long day.", 4.5),
            ("Bespoke Kitchen", "Food", "The town's best brunch — soft scrambled eggs on sourdough, granola bowls that look like art, killer coffee — in a small Gorge Road room with a courtyard out back.", 4.6),
            ("Public Kitchen & Bar", "Food", "Steamer Wharf spot for shared plates, pub-style. Fresh oysters, wood-fired pizza, NZ wine by the glass. Walk-in friendly when everywhere else is booked.", 4.4),
            ("Eichardt's Bar", "Nightlife", "The bar inside Eichardt's hotel on the lakefront — fireplaces, sheepskin couches, perfect Negronis. The most atmospheric pre-dinner drink in town.", 4.6, True),
            ("Little Blackwood", "Nightlife", "Tiny cocktail bar tucked under Steamer Wharf with a creative seasonal list, candlelight, and an attitude that makes everyone feel like a regular.", 4.6, True),
            ("Atlas Beer Café", "Nightlife", "Lakefront craft beer specialist with a huge South Island brewery list, decent pub food, and one of the best pre-dinner sunset views in town.", 4.5),
            ("Eichardt's Private Hotel", "Places to Stay", "A heritage 1860s lakefront hotel with just ten suites, a roaring fire in the bar, and arguably the best location in Queenstown. Old-world luxury done right.", 4.8, True),
            ("Matakauri Lodge", "Places to Stay", "Relais & Châteaux lodge ten minutes from town, perched above the lake with mountain views from every room. Set-menu dinners, a deep cellar of Otago wine, an outdoor hot tub at dusk.", 4.9, True),
            ("Sofitel Queenstown", "Places to Stay", "Central luxury hotel right off Steamer Wharf — walk to dinner, walk to the gondola, walk home. Reliable, comfortable, beautifully run.", 4.6),
            ("QT Queenstown", "Places to Stay", "Playful design hotel right on the lake with mountain-facing rooms, a buzzing bar, and Reds — the in-house steakhouse — that's surprisingly good.", 4.5),
            ("Skyline Gondola & Bob's Peak", "Places to See", "Cable car up Bob's Peak for the iconic Queenstown view — town, lake, Remarkables, all in one frame. Stay for sunset, take the luge down, drink at the top.", 4.7, True),
            ("Glenorchy & Paradise Drive", "Places to See", "Drive 45 minutes around the head of the lake to the tiny settlement of Glenorchy, then onto the gravel road toward 'Paradise' — Lord of the Rings country, vast empty valleys, mountain reflections. Take a picnic.", 4.9, True),
            ("Milford Sound Day Trip", "Places to See", "A long day but the great New Zealand experience — drive (or fly) into Fiordland for a cruise through the most dramatic fjord on earth. Waterfalls, seals, sheer cliffs straight out of the water.", 4.8, True),
            ("Arrowtown", "Places to See", "Twenty minutes from Queenstown, a perfectly preserved 1860s gold-mining village with autumn-yellow trees, stone cottages, and the country's best pub lunch at Fork & Tap. A worthy half-day.", 4.7, True),
            ("Onsen Hot Pools", "Places to See", "Private cedar hot pools cantilevered over the Shotover River canyon. Book a session at sunset with a bottle of Pinot. Genuinely one of the most beautiful things you can do in New Zealand.", 4.9, True),
            ("Shotover Jet", "Places to See", "Half-hour jet-boat ride through the narrow Shotover River canyon at terrifying speed, with 360° spins inches from rock walls. Worth every dollar of the ticket.", 4.7, True),
            ("AJ Hackett Kawarau Bridge Bungy", "Places to See", "The world's first commercial bungy jump (opened 1988), 43m off a heritage bridge into the Kawarau River. Even if you don't jump, watching from the viewing platform is its own experience.", 4.7, True),
        ],
    },
}

NEW_CCODES = {"New Zealand": "nz"}

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

def maps_url(name, city):
    q = urllib.parse.quote_plus(f"{name} {city}")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

# 1. PLACES
ps, pe = extract_object(js, "const PLACES=")
places = json.loads(js[ps:pe])
total = 0
for city, info in CITIES.items():
    entries = []
    for name, cat, desc, *rest in info["places"]:
        rating = rest[0] if rest else None
        e = {"n": name, "c": cat, "d": desc, "u": maps_url(name, city)}
        if rating is not None: e["r"] = rating
        entries.append(e)
    places.setdefault(city, []).extend(entries)
    places[city].sort(key=lambda p: p["n"].lower())
    total += len(entries)
    print(f"PLACES: {city} → {len(entries)} entries")
js = js[:ps] + json.dumps(places, ensure_ascii=False, separators=(',', ':')) + js[pe:]

# 2. META
ms, me = extract_object(js, "const META=")
meta = json.loads(js[ms:me])
for city, info in CITIES.items():
    if city not in meta:
        meta[city] = {"country": info["country"], "emoji": info["emoji"], "tagline": info["tagline"]}
js = js[:ms] + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + js[me:]
print(f"META: added {len(CITIES)} cities")

# 3. COORDS
for city, info in CITIES.items():
    if f"'{city}':" not in js.split('const COORDS=')[1].split('};')[0]:
        lat, lng = info["coords"]
        js = js.replace("const COORDS={", f"const COORDS={{'{city}':[{lat},{lng}],", 1)
print("COORDS: added")

# 4. REGIONS
for city, info in CITIES.items():
    pat = re.compile(r"('Oceania':\s*\[)([^\]]+)(\])")
    m = pat.search(js)
    assert m
    inner = m.group(2)
    if f"'{city}'" in inner:
        continue
    items = [s.strip().strip("'") for s in inner.split(",") if s.strip()]
    items.append(city)
    items.sort(key=str.lower)
    new_inner = ", ".join(f"'{c}'" for c in items)
    js = pat.sub(lambda _m: _m.group(1) + new_inner + _m.group(3), js, count=1)
print("REGIONS: added to Oceania")

# 5. CCODES
cs, ce = extract_object(js, "const CCODES=")
ccodes = json.loads(js[cs:ce])
for country, code in NEW_CCODES.items():
    if country not in ccodes:
        ccodes[country] = code
js = js[:cs] + json.dumps(ccodes, ensure_ascii=False, separators=(', ', ': ')) + js[ce:]
print("CCODES: added New Zealand")

DATA.write_text(js, encoding='utf-8')
print(f"\nDone. {total} places added across {len(CITIES)} cities.")
