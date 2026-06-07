#!/usr/bin/env python3
"""Extract META, PLACES, COORDS, REGIONS, CCODES from index.html into data.js
and replace inline references with an external <script src='data.js'>.

Also patches about.html to load data.js and compute stats dynamically.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / 'index.html'
ABOUT = ROOT / 'about.html'
DATA  = ROOT / 'data.js'

html = INDEX.read_text(encoding='utf-8')

def extract_const_block(text, marker):
    """Find a `const NAME={...}` declaration and return (start_of_const, end_after_closing_brace)."""
    i = text.find(marker)
    assert i >= 0, f"{marker!r} not found"
    obj_start = text.find('{', i)
    depth = 0; in_dq = False; in_sq = False; esc = False
    for j in range(obj_start, len(text)):
        ch = text[j]
        if in_dq:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == '"': in_dq = False
        elif in_sq:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == "'": in_sq = False
        else:
            if ch == '"': in_dq = True
            elif ch == "'": in_sq = True
            elif ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return i, j + 1
    raise ValueError(f"unbalanced braces in {marker!r}")

# Extract each const block in source order
markers = ["const META=", "const PLACES=", "const CCODES=", "const COORDS=", "const REGIONS"]
# Sort by source position
positions = sorted([(html.find(m), m) for m in markers])

blocks = []
for _, m in positions:
    s, e = extract_const_block(html, m)
    blocks.append((s, e, html[s:e]))

# Write data.js (in source order)
data_js = "// Auto-extracted from index.html — edit here, both index.html and about.html consume it.\n"
for _, _, src in blocks:
    data_js += src + ";\n"
DATA.write_text(data_js, encoding='utf-8')
print(f"Wrote {DATA} ({len(data_js):,} bytes)")

# Remove blocks from index.html (back-to-front so offsets stay valid)
for s, e, _ in reversed(blocks):
    # Also consume any trailing semicolon
    trim_e = e
    while trim_e < len(html) and html[trim_e] in ';':
        trim_e += 1
    html = html[:s] + html[trim_e:]

# Insert <script src="data.js"></script> right before the <script> that holds the JS
i = html.find('<script>\n')
assert i >= 0, "<script> opener not found"
inject = '<script src="data.js"></script>\n'
html = html[:i] + inject + html[i:]
INDEX.write_text(html, encoding='utf-8')
print(f"index.html: extracted {len(blocks)} const blocks, added <script src='data.js'>")

# ─── about.html ───────────────────────────────────────────────────────────────
about = ABOUT.read_text(encoding='utf-8')

# Add data.js loader before </body> if not present
if 'data.js' not in about:
    # Replace the hardcoded "147 Cities covered" / "74+ Countries visited" with placeholders + IDs
    about = about.replace(
        '<div class="about-stat"><span class="about-stat-n">74+</span><span class="about-stat-l">Countries visited</span></div>',
        '<div class="about-stat"><span class="about-stat-n" id="aboutCountries">74+</span><span class="about-stat-l">Countries visited</span></div>'
    )
    about = about.replace(
        '<div class="about-stat"><span class="about-stat-n">147</span><span class="about-stat-l">Cities covered</span></div>',
        '<div class="about-stat"><span class="about-stat-n" id="aboutCities">—</span><span class="about-stat-l">Cities covered</span></div>'
    )
    # Inject loader + stats script before </body>
    snippet = (
        '<script src="data.js"></script>\n'
        '<script>\n'
        '(function(){\n'
        '  if(typeof PLACES==="undefined"||typeof META==="undefined") return;\n'
        '  var cities=Object.keys(PLACES).length;\n'
        '  var countries=new Set();\n'
        '  for(var c in PLACES){var ctry=(META[c]||{}).country;if(ctry)countries.add(ctry);}\n'
        '  var cEl=document.getElementById("aboutCities");\n'
        '  if(cEl) cEl.textContent=cities;\n'
        '  var nEl=document.getElementById("aboutCountries");\n'
        '  if(nEl) nEl.textContent=Math.max(74,countries.size)+"+";\n'
        '})();\n'
        '</script>\n'
    )
    about = about.replace('</body>', snippet + '</body>', 1)
    ABOUT.write_text(about, encoding='utf-8')
    print("about.html: linked data.js + dynamic stats wired up")
else:
    print("about.html: already linked")
