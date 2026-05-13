#!/usr/bin/env python3
"""
Patch index.html with:
1. Wikipedia auto-fetch thumbnails for fave cards + modal
2. Fave ♥ badge on cards when not on My Favorites tab
"""

with open('../index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add position:relative to .pcard so heart badge can be absolute ────────
old_pcard_css = '.pcard{padding:22px 20px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);cursor:pointer;transition:background .15s;}'
new_pcard_css = '.pcard{padding:22px 20px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);cursor:pointer;transition:background .15s;position:relative;}'
assert old_pcard_css in html, 'pcard CSS not found'
html = html.replace(old_pcard_css, new_pcard_css, 1)

# ── 2. Add fave-badge CSS (after existing pcard CSS block) ───────────────────
old_after_pcard = '.pcard:nth-child(3n){border-right:none;}'
new_after_pcard = '.pcard:nth-child(3n){border-right:none;}.fave-badge{position:absolute;top:10px;right:12px;color:#e87040;font-size:13px;line-height:1;pointer-events:none;text-shadow:0 1px 3px rgba(0,0,0,.4);}'
assert old_after_pcard in html, 'pcard nth-child CSS not found'
html = html.replace(old_after_pcard, new_after_pcard, 1)

# ── 3. Update renderPlaces to add fave badge + call fetchFaveThumbs ──────────
old_pill_line = "    const pill=p.c+(p.r?` · ${p.r}★`:'');\n    const thumb=p.img?`<img class=\"pthumb\" src=\"${p.img}\" alt=\"\" loading=\"lazy\">`:''  \n    return `<div class=\"pcard${p.img?' has-img':''}\" onclick='openM(${JSON.stringify(p).replace(/'/g,\"&#39;\")},"
# find exact text
idx = html.find("    const pill=p.c+(p.r?` · ${p.r}★`:'');\n    const thumb=")
end = html.find("    return `<div class=\"pcard", idx)
old_block = html[idx:end]
new_block = (
    "    const pill=p.c+(p.r?` · ${p.r}★`:'');\n"
    "    const thumb=p.img?`<img class=\"pthumb\" src=\"${p.img}\" alt=\"\" loading=\"lazy\">`:'';\n"
    "    const faveBadge=(p.f&&k!=='My Favorites')?'<span class=\"fave-badge\">♥</span>':'';\n"
)
print('old_block found at:', idx)
print('old_block:', repr(old_block))
html = html[:idx] + new_block + html[end:]

# Also update the return line to include faveBadge
old_return = '    return `<div class="pcard${p.img?\' has-img\':\'\'}" onclick=\'openM(${JSON.stringify(p).replace(/\'/g,"&#39;")},"${city.replace(/"/g,\'&quot;\')}")\'>\n      ${thumb}\n      <span class="ppill">'
new_return = '    return `<div class="pcard${p.img?\' has-img\':\'\'}" onclick=\'openM(${JSON.stringify(p).replace(/\'/g,"&#39;")},"${city.replace(/"/g,\'&quot;\')}")\'>\n      ${thumb}${faveBadge}\n      <span class="ppill">'
assert old_return in html, f'return line not found\nExpected: {repr(old_return)}\nGot context: {repr(html[html.find("return `<div"):html.find("return `<div")+300])}'
html = html.replace(old_return, new_return, 1)

# Add fetchFaveThumbs call at end of renderPlaces
old_join = "  }).join('');\n}"
# There might be multiple — find the one in renderPlaces
rp_idx = html.find('function renderPlaces')
join_idx = html.find("  }).join('');\n}", rp_idx)
html = html[:join_idx] + "  }).join('');\n  fetchFaveThumbs(places,city);\n}" + html[join_idx + len("  }).join('');\n}"):]
print('fetchFaveThumbs call added')

# ── 4. Add Wikipedia auto-fetch functions before renderPlaces ─────────────────
wiki_js = '''
const _pImgC=JSON.parse(sessionStorage.getItem('_pImgC')||'{}');
function _savePIC(){try{sessionStorage.setItem('_pImgC',JSON.stringify(_pImgC));}catch(e){}}
function injectCardImg(name,url,cityKey){
  document.querySelectorAll('.pcard').forEach(el=>{
    const nm=el.querySelector('.pname');
    if(nm&&nm.textContent.trim()===name&&!el.querySelector('.pthumb')){
      const img=document.createElement('img');
      img.className='pthumb';img.src=url;img.alt='';img.loading='lazy';
      img.onerror=()=>{_pImgC[cityKey+'|'+name]='';_savePIC();el.classList.remove('has-img');img.remove();};
      el.classList.add('has-img');
      el.insertBefore(img,el.firstChild);
    }
  });
}
function fetchFaveThumbs(places,cityName){
  places.filter(p=>p.f&&!p.img).forEach((p,i)=>{
    const key=cityName+'|'+p.n;
    if(_pImgC[key]!==undefined){if(_pImgC[key])injectCardImg(p.n,_pImgC[key],cityName);return;}
    setTimeout(()=>{
      const tries=[p.n,p.n+', '+cityName];
      const attempt=(j)=>{
        if(j>=tries.length){_pImgC[key]='';_savePIC();return;}
        fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'+encodeURIComponent(tries[j]))
          .then(r=>r.json())
          .then(d=>{
            if(d.type==='disambiguation'||!d.thumbnail){attempt(j+1);return;}
            const url=(d.originalimage||d.thumbnail).source||'';
            if(!url){attempt(j+1);return;}
            _pImgC[key]=url;_savePIC();injectCardImg(p.n,url,cityName);
          })
          .catch(()=>attempt(j+1));
      };
      attempt(0);
    },i*220);
  });
}
'''

insert_before = 'function renderPlaces('
assert insert_before in html
html = html.replace(insert_before, wiki_js + insert_before, 1)
print('Wiki fetch functions added')

# ── 5. Update openM to show cached/fetched image for faves without p.img ─────
old_photo_block = "  const photo=document.getElementById('mPhoto');if(p.img){photo.src=p.img;photo.style.display='block';}else{photo.src='';photo.style.display='none';}"
new_photo_block = (
  "  const photo=document.getElementById('mPhoto');\n"
  "  const _mImgUrl=p.img||((p.f&&_pImgC[c+'|'+p.n])||'');\n"
  "  if(_mImgUrl){photo.src=_mImgUrl;photo.style.display='block';}\n"
  "  else if(p.f){\n"
  "    photo.src='';photo.style.display='none';\n"
  "    const _mk=c+'|'+p.n;\n"
  "    if(_pImgC[_mk]===undefined){\n"
  "      fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'+encodeURIComponent(p.n))\n"
  "        .then(r=>r.json()).then(d=>{\n"
  "          const url=d.type!=='disambiguation'&&d.thumbnail?(d.originalimage||d.thumbnail).source||'':'';\n"
  "          _pImgC[_mk]=url;_savePIC();\n"
  "          if(url&&document.getElementById('mover').classList.contains('on')&&document.getElementById('mName').textContent===p.n){photo.src=url;photo.style.display='block';}\n"
  "        }).catch(()=>{_pImgC[_mk]='';_savePIC();});\n"
  "    }\n"
  "  } else{photo.src='';photo.style.display='none';}"
)
assert old_photo_block in html, 'photo block not found'
html = html.replace(old_photo_block, new_photo_block, 1)
print('openM photo block updated')

# ── Validate ──────────────────────────────────────────────────────────────────
import re, json
m = re.search(r'const PLACES=(\{.*?\});', html, re.DOTALL)
json.loads(m.group(1))
print('PLACES JSON: valid')
assert 'fetchFaveThumbs' in html
assert 'fave-badge' in html
assert '_pImgC' in html
print('All assertions passed')

with open('../index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved.')
