#!/usr/bin/env bash
# Pre-deploy check for seegoeat — run before every Stop
HTML=/home/user/seegoeat/index.html
FAILS=0
OUT=""

ok()   { OUT="$OUT\n✓ $1"; }
fail() { OUT="$OUT\n❌ $1"; FAILS=$((FAILS+1)); }

# 1. JS syntax check
JS_RESULT=$(node -e "
const fs = require('fs');
const html = fs.readFileSync('$HTML', 'utf8');
const blocks = [...html.matchAll(/<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const bad = [];
for (let i=0; i<blocks.length; i++) {
  try { new Function(blocks[i]); } catch(e) { bad.push('block '+i+': '+e.message); }
}
if (bad.length) { console.log(bad.join('; ')); process.exit(1); }
" 2>&1)
if [ $? -eq 0 ]; then ok "JS syntax valid"; else fail "JS syntax error: $JS_RESULT"; fi

# 2. Modal div
if grep -q '<div class="mover" id="mover"' "$HTML"; then
  ok "Modal <div> present"
else
  fail "Modal <div> missing — openM() will crash on every tap"
fi

# 3. Stats elements
for ID in stTotal stCities stReviewed; do
  if grep -q "id=\"$ID\"" "$HTML"; then ok "Stat #$ID present"
  else fail "Stat #$ID MISSING"; fi
done

# 4. Map
if grep -q 'id="homeMap"' "$HTML"; then ok "#homeMap present"; else fail "#homeMap MISSING"; fi
if grep -q 'unpkg.com/leaflet' "$HTML"; then ok "Leaflet CDN present"; else fail "Leaflet CDN MISSING"; fi
if grep -q "window.addEventListener('load'" "$HTML"; then ok "Map load handler present"; else fail "Map load handler MISSING"; fi
if grep -q "getElementById('stTotal').textContent" "$HTML"; then ok "Stats population code present"; else fail "Stats population code MISSING"; fi

# 5. Footer consistency across all footers in index.html
FOOTER_CHECK=$(python3 -c "
import re, sys
html = open('$HTML').read()
footers = re.findall(r'<footer>(.*?)</footer>', html, re.DOTALL)
if len(footers) < 2:
    print('only one footer')
    sys.exit(0)
auth = footers[0]
bad = [i+2 for i,f in enumerate(footers[1:]) if f.strip() != auth.strip()]
if bad:
    print('footers ' + str(bad) + ' differ from authority')
    sys.exit(1)
print(str(len(footers)) + ' footers match')
" 2>&1)
if [ $? -eq 0 ]; then ok "Footers: $FOOTER_CHECK"; else fail "Footer mismatch: $FOOTER_CHECK"; fi

# 6. No dead getElementById refs
DEAD_FOUND=""
for DEAD in stCitiesHero pg-about; do
  if grep -q "getElementById('$DEAD')" "$HTML"; then DEAD_FOUND="$DEAD_FOUND $DEAD"; fi
done
if [ -z "$DEAD_FOUND" ]; then ok "No dead getElementById refs"
else fail "Dead refs found:$DEAD_FOUND"; fi

# 7. PLACES JSON valid
PLACES_CHECK=$(python3 -c "
import re, json, sys
html = open('$HTML').read()
m = re.search(r'const PLACES\s*=\s*(\{)', html)
if not m: print('PLACES not found'); sys.exit(1)
start = m.start(1); depth = 0
for i, ch in enumerate(html[start:], start):
    if ch=='{': depth+=1
    elif ch=='}':
        depth-=1
        if depth==0: end=i+1; break
try:
    json.loads(html[start:end])
    print('valid')
except Exception as e:
    print(str(e)); sys.exit(1)
" 2>&1)
if [ $? -eq 0 ]; then ok "PLACES JSON $PLACES_CHECK"; else fail "PLACES JSON invalid: $PLACES_CHECK"; fi

# Report
printf "$OUT\n"
echo ""

if [ "$FAILS" -gt 0 ]; then
  printf '{"systemMessage": "🚫 Pre-deploy check FAILED (%d issue(s)) — fix before pushing", "continue": false}\n' "$FAILS"
  exit 2
else
  printf '{"systemMessage": "✅ Pre-deploy checks all passed"}\n'
fi
