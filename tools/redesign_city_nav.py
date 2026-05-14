#!/usr/bin/env python3
"""
Full redesign:
1. Nav: Infatuation-inspired — clean, editorial, no box borders, underline active
2. City page: editorial list + featured strip (top 3 faves for cities >10 places)
3. Wikipedia image inject into featured + list items
"""
import re, json, subprocess

with open('../index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Nav CSS: fix remaining pieces ────────────────────────────────────────
# Replace 560px nav overrides
old_560_nav = '  .top-nav{padding:0 10px;}\n  .about-pg{padding:44px 20px 72px;}'
new_560_nav = '  .top-nav{padding:0 14px;height:56px;}\n  .nav-home{height:56px;padding:0 8px;font-size:12px;}\n  .nav-home::after{left:8px;right:8px;}\n  .logo img{height:22px;}\n  .map-btn{padding:0 14px;height:34px;font-size:11px;}\n  .city-select-wrap select{max-width:130px;border-radius:20px;min-width:0;padding:7px 12px;}\n  .about-pg{padding:44px 20px 72px;}'
assert old_560_nav in html, '560 nav block not found'
html = html.replace(old_560_nav, new_560_nav, 1)

# Remove duplicate .logo img in 560px (was added before, now handled above)
old_560_logo = '  .logo img{height:24px;}\n  .city-select-wrap select{max-width:110px;}'
if old_560_logo in html:
    html = html.replace(old_560_logo, '', 1)

# Remove duplicate old nav-home in 560px
old_560_nh = '  .nav-home{padding:0 10px;font-size:11px;}\n'
if old_560_nh in html:
    html = html.replace(old_560_nh, '', 1)

print('✓ 560px nav fixed')

# ── 2. Add new CSS: featured cards + editorial list ──────────────────────────
old_pcard_section = '.pcard{padding:22px 20px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);cursor:pointer;transition:background .15s;position:relative;}'
new_pcard_section = (
    # Keep pcard for fallback
    '.pcard{padding:22px 20px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);cursor:pointer;transition:background .15s;position:relative;}'

    # Editorial list container overrides pgrid
    '.pllist{padding:0;}'

    # Featured strip (top faves with images)
    '.pfeat{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--rule);border-bottom:1px solid var(--rule);}'
    '.pf-card{background:var(--paper);cursor:pointer;transition:background .15s;overflow:hidden;}'
    '.pf-card:hover{background:var(--warm);}'
    '.pf-img{width:100%;height:190px;overflow:hidden;background:var(--warm);position:relative;display:flex;align-items:center;justify-content:center;}'
    '.pf-img img{width:100%;height:100%;object-fit:cover;position:absolute;inset:0;transition:transform .4s;}'
    '.pf-card:hover .pf-img img{transform:scale(1.03);}'
    '.pf-ph{font-family:\'Playfair Display\',serif;font-size:56px;font-weight:700;color:rgba(255,255,255,.06);}'
    '.pf-body{padding:16px 20px 20px;}'
    '.pf-cat{font-size:9px;letter-spacing:0.18em;text-transform:uppercase;color:var(--blue);display:block;margin-bottom:7px;}'
    '.pf-name{font-family:\'Playfair Display\',serif;font-size:17px;font-weight:700;line-height:1.25;margin-bottom:6px;}'
    '.pf-desc{font-size:12px;color:var(--ink-light);line-height:1.6;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}'

    # Editorial list items
    '.pli{display:flex;align-items:flex-start;gap:18px;padding:20px 0;border-bottom:1px solid var(--rule);cursor:pointer;transition:background .15s;}'
    '.pli:first-child{border-top:1px solid var(--rule);}'
    '.pli:hover{background:var(--accent-bg);}'
    '.pli-img{width:90px;height:90px;flex-shrink:0;background:var(--warm);overflow:hidden;position:relative;display:flex;align-items:center;justify-content:center;}'
    '.pli-img img{width:100%;height:100%;object-fit:cover;position:absolute;inset:0;}'
    '.pli-ph{font-family:\'Playfair Display\',serif;font-size:28px;font-weight:700;color:rgba(255,255,255,.08);}'
    '.pli-body{flex:1;min-width:0;}'
    '.pli-meta{display:flex;align-items:center;gap:8px;margin-bottom:5px;}'
    '.pli-name{font-family:\'Playfair Display\',serif;font-size:17px;font-weight:700;line-height:1.25;margin-bottom:6px;}'
    '.pli-desc{font-size:13px;color:var(--ink-light);line-height:1.6;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:8px;}'
    '.fave-badge-inline{color:#e87040;font-size:12px;}'
)
assert old_pcard_section in html
html = html.replace(old_pcard_section, new_pcard_section, 1)
print('✓ Editorial CSS added')

# ── 3. Responsive: featured strip ────────────────────────────────────────────
old_960_pgrid = '  .pgrid{grid-template-columns:1fr 1fr;}'
new_960_pgrid = '  .pgrid{grid-template-columns:1fr 1fr;}\n  .pfeat{grid-template-columns:1fr 1fr;}\n  .pf-img{height:160px;}'
if old_960_pgrid in html:
    html = html.replace(old_960_pgrid, new_960_pgrid, 1)

old_560_pgrid = '  .pgrid{grid-template-columns:1fr;}'
new_560_pgrid = '  .pgrid{grid-template-columns:1fr;}\n  .pfeat{grid-template-columns:1fr;}\n  .pf-img{height:180px;}\n  .pli-img{width:72px;height:72px;}\n  .pli-name{font-size:15px;}'
if old_560_pgrid in html:
    html = html.replace(old_560_pgrid, new_560_pgrid, 1)
print('✓ Responsive CSS added')

# ── 4. Replace renderPlaces with editorial version ────────────────────────────
old_render = """function renderPlaces(k){
  const places=k==='All'?(PLACES[city]||[]):k==='My Favorites'?(PLACES[city]||[]).filter(p=>p.f):(PLACES[city]||[]).filter(p=>p.c===k);
  document.getElementById('catTitle').textContent=k;
  document.getElementById('catCount').textContent=places.length+' place'+(places.length!==1?'s':'');
  document.getElementById('plGrid').innerHTML=places.map(p=>{
    const pill=p.c+(p.r?` · ${p.r}★`:'');
    const faveBadge=(p.f&&k!=='My Favorites')?'<span class="fave-badge">♥</span>':'';
    return `<div class="pcard" onclick='openM(${JSON.stringify(p).replace(/'/g,"&#39;")},"${city.replace(/"/g,'&quot;')}")'>
      ${faveBadge}
      <span class="ppill">${pill}</span>
      <div class="pname">${p.n}</div>
      ${p.d?`<div class="pdesc">${p.d}</div>`:''}
      <a class="pml" href="${p.u}" target="_blank" rel="noopener" onclick="event.stopPropagation()">↗ Maps</a>
    </div>`;
  }).join('');
  fetchFaveThumbs(places,city);
}"""

new_render = """function renderPlaces(k){
  const all=PLACES[city]||[];
  const places=k==='All'?all:k==='My Favorites'?all.filter(p=>p.f):all.filter(p=>p.c===k);
  document.getElementById('catTitle').textContent=k;
  document.getElementById('catCount').textContent=places.length+' place'+(places.length!==1?'s':'');
  const grid=document.getElementById('plGrid');

  // Featured strip: top 3 faves by rating, only on All tab when city has >10 places
  const showFeat=k==='All'&&all.length>10;
  const featured=showFeat?[...places].filter(p=>p.f).sort((a,b)=>(b.r||0)-(a.r||0)).slice(0,3):[];
  const featSet=new Set(featured.map(p=>p.n));

  const featHTML=featured.length?`<div class="pfeat">${featured.map(p=>`
    <div class="pf-card" onclick='openM(${JSON.stringify(p).replace(/'/g,"&#39;")},"${city.replace(/"/g,'&quot;')}"})'> 
      <div class="pf-img" data-pname="${p.n.replace(/"/g,'&quot;')}"><div class="pf-ph">${p.n[0]}</div></div>
      <div class="pf-body">
        <span class="pf-cat">${p.c}${p.r?' · '+p.r+'★':''}</span>
        <div class="pf-name">${p.n}</div>
        <div class="pf-desc">${p.d||''}</div>
      </div>
    </div>`).join('')}</div>`:'';

  const listHTML=`<div class="pllist">${places.map(p=>{
    const pill=p.c+(p.r?` · ${p.r}★`:'');
    const fav=(p.f&&k!=='My Favorites')?'<span class="fave-badge-inline">♥</span>':'';
    return `<div class="pli" onclick='openM(${JSON.stringify(p).replace(/'/g,"&#39;")},"${city.replace(/"/g,'&quot;')}"})'> 
      <div class="pli-img" data-pname="${p.n.replace(/"/g,'&quot;')}"><div class="pli-ph">${p.c[0]}</div></div>
      <div class="pli-body">
        <div class="pli-meta"><span class="ppill">${pill}</span>${fav}</div>
        <div class="pli-name">${p.n}</div>
        ${p.d?`<div class="pli-desc">${p.d}</div>`:''}
        ${p.u?`<a class="pml" href="${p.u}" target="_blank" rel="noopener" onclick="event.stopPropagation()">↗ Maps</a>`:''}
      </div>
    </div>`;
  }).join('')}</div>`;

  grid.className='pllist-wrap';
  grid.innerHTML=featHTML+listHTML;
  fetchFaveThumbs(places,city);
}"""

assert old_render in html, 'renderPlaces not found'
html = html.replace(old_render, new_render, 1)
print('✓ renderPlaces rewritten')

# ── 5. Update injectCardImg to inject into featured + list items ──────────────
old_inject = 'function injectCardImg(name,url,cityKey){/* images shown in modal only */}'
new_inject = """function injectCardImg(name,url,cityKey){
  document.querySelectorAll('[data-pname]').forEach(el=>{
    if(el.dataset.pname===name&&!el.querySelector('img')){
      const img=document.createElement('img');
      img.src=url;img.alt='';img.loading='lazy';
      img.onerror=()=>{_pImgC[cityKey+'|'+name]='';_savePIC();img.remove();};
      el.appendChild(img);
    }
  });
}"""
assert old_inject in html, 'injectCardImg not found'
html = html.replace(old_inject, new_inject, 1)
print('✓ injectCardImg updated')

# ── 6. Add .pllist-wrap CSS (psec padding adjustment) ────────────────────────
old_psec = '.psec{padding:36px 48px 60px;}'
new_psec = '.psec{padding:0 48px 60px;}.pllist-wrap{}.pllist{}'
assert old_psec in html
html = html.replace(old_psec, new_psec, 1)

# ph (place header inside psec) needs top padding
old_ph = '.ph{display:flex;'
if old_ph in html:
    ph_idx = html.find(old_ph)
    ph_end = html.find('}', ph_idx) + 1
    old_ph_full = html[ph_idx:ph_end]
    html = html.replace(old_ph_full, old_ph_full.rstrip('}') + 'padding-top:28px;}', 1)
    print('✓ .ph padding fixed')
print('✓ psec padding fixed')

# ── Validate ──────────────────────────────────────────────────────────────────
m = re.search(r'const PLACES=(\{.*?\});', html, re.DOTALL)
json.loads(m.group(1))
s = html.find('<script>') + len('<script>')
e = html.find('</script>', s)
with open('/tmp/check.js', 'w') as f:
    f.write(html[s:e])
r = subprocess.run(['node', '--check', '/tmp/check.js'], capture_output=True, text=True)
print('JS:', 'OK' if r.returncode == 0 else 'ERROR:\n'+r.stderr[:300])

with open('../index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('\nAll done — saved.')
