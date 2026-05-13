#!/usr/bin/env python3
"""Insert Marrakech into index.html - corrected version"""
import re

with open('../index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Verify we can find PLACES block
pm = re.search(r'const PLACES=\{', html)
places_start = pm.end()
medellin_in_places = html.find('"Medellin"', places_start)
print('PLACES start:', places_start)
print('Medellin in PLACES:', medellin_in_places)
print('Context:', repr(html[medellin_in_places-20:medellin_in_places+20]))

# The anchor string is unique enough
ANCHOR = '}],"Medellin": [{"n": "Carmen"'

assert ANCHOR in html, f"Anchor not found: {ANCHOR}"

marrakech_places = (
    '"Marrakech":['
    '{"n":"Bab Doukkala Neighbourhood","c":"Places to See","d":"Step beyond the souks and Djemaa el-Fna into this quiet residential quarter near the old city gate, where local life unfolds: a neighbourhood hammam, a bakery pulling bread from a wood-fired oven, kids playing in an unrestored alley. The real medina, unhurried.","r":4.3},'
    '{"n":"Café Clock","c":"Food","d":"A cultural hub as much as a café, set across two floors of a 1930s medina house. Camel burgers are the menu talking point, but come for the storytelling evenings, Gnawa music nights, and the freshest harira soup in the city.","r":4.3},'
    '{"n":"Café des Épices","c":"Food","d":"A rooftop café perched above the spice souk on Rahba Lakdima, serving mint tea, fresh juices and simple Moroccan plates with one of the medina\'s best bird\'s-eye views. Arrive early for the light.","r":4.4},'
    '{"n":"Dar Cherifa","c":"Places to See","d":"A 16th-century riad in the heart of the medina that doubles as an art gallery and literary café. The carved cedarwood ceilings are breathtaking and the afternoon crowd — artists, writers, the quietly curious — is as good as the architecture.","r":4.5,"f":true},'
    '{"n":"Grand Café de la Poste","c":"Food","d":"A colonial-era landmark in the Ville Nouvelle that has been feeding Marrakech\'s creative set since 1925. The brasserie menu is French through and through — steak frites, croque monsieur, an excellent wine list — and the zinc bar is one of the most atmospheric rooms in the city.","r":4.4},'
    '{"n":"Jardin Secret","c":"Places to See","d":"A beautifully restored 19th-century Islamic garden hidden behind high medina walls. Two enclosed gardens — one Islamic, one exotic — with a working khettara water channel. Far less crowded than Majorelle and more historically interesting.","r":4.5,"f":true},'
    '{"n":"Jnane Tamsna","c":"Places to Stay","d":"The most extraordinary hotel in Morocco, and the personal creation of Meryanne Loum-Martin — a Senegalese-American lawyer, designer and author who arrived in Marrakech in the early 1990s and transformed an abandoned olive grove in the Palmeraie into this lush paradise. Meryanne planted every tree herself, sourced every tile, and wove the identity of the place from her deep knowledge of Moroccan botanical tradition. The result is six villas in five acres of intensely cultivated gardens, the rooms full of antiques and local craft, the food grown on site. She is the kind of host who makes you feel the hotel was made for you specifically — because, in a real sense, it was made for everyone who loves beauty.","r":5.0,"f":true},'
    '{"n":"La Famille","c":"Food","d":"A sun-drenched organic garden restaurant just outside the medina walls, where the menu changes daily based on what was harvested that morning. No meat, no stress, just Moroccan vegetables done with rare care. The fig and argan oil salad is legendary.","r":4.5,"f":true},'
    '{"n":"Musée Yves Saint Laurent","c":"Places to See","d":"The terracotta cube next to Jardin Majorelle that houses rotating exhibitions of YSL\'s archive alongside permanent displays on his deep love for Morocco. The building itself, designed by Studio KO, is as precise and beautiful as the clothes inside.","r":4.6,"f":true},'
    '{"n":"Nomad","c":"Food","d":"A three-storey rooftop restaurant in the medina doing elevated modern Moroccan: charcoal-roasted aubergine, lamb mechoui tacos, outstanding natural wine list. The top terrace has a view straight across the rooftops toward the Koutoubia. Book ahead.","r":4.5}'
    ']'
)

# Replace: insert Marrakech before Medellin
new_anchor = '}],' + marrakech_places + ',"Medellin": [{"n": "Carmen"'
html = html.replace(ANCHOR, new_anchor, 1)

assert 'Jnane Tamsna' in html, "Jnane Tamsna not found after insert"
print("PLACES: OK")

# ── COORDS: already done in previous session (Marrakech coords were added) ──
# Check if already there
if "'Marrakech'" not in html:
    old_coords = "'Marmaris':[36.8556,28.2716],'Medellin'"
    new_coords = "'Marmaris':[36.8556,28.2716],'Marrakech':[31.6295,-7.9811],'Medellin'"
    html = html.replace(old_coords, new_coords, 1)
    print("COORDS: inserted")
else:
    print("COORDS: already present")

# ── REGIONS: already done ──
if "'Africa & Islands': ['Cape Town', 'Maldives', 'Marrakech'" in html:
    print("REGIONS: already present")
else:
    old_region = "'Africa & Islands': ['Cape Town', 'Maldives', 'Monrovia'"
    new_region = "'Africa & Islands': ['Cape Town', 'Maldives', 'Marrakech', 'Monrovia'"
    html = html.replace(old_region, new_region, 1)
    print("REGIONS: inserted")

# ── META: already done ──
if '"Marrakech":{"country":"Morocco"' in html:
    print("META: already present")
else:
    marrakech_meta = '"Marrakech":{"country":"Morocco","emoji":"\U0001f1f2\U0001f1e6","tagline":"\U0001f339 A city of sensory overload and deep serenity at once: labyrinthine medina souks fragrant with saffron and rose, gardens of extraordinary privacy, riads that open narrow doorways onto palatial courtyards. I lose myself every single time in the best possible way."},'
    old_meta = '"Cape Town":{"country":"South Africa"'
    new_meta = marrakech_meta + '"Cape Town":{"country":"South Africa"'
    html = html.replace(old_meta, new_meta, 1)
    print("META: inserted")

with open('../index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\nAll done. Verifying counts...")
print(f"  Marrakech in html: {html.count('Marrakech')}")
