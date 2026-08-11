#!/usr/bin/env python3
"""Build the FIITJEE certificate-finder page from fiitjee/certificates.json.

Usage: python3 build_fiitjee_page.py   # writes fiitjee/index.html

Same page as the FIDE-tournament finder (build_page.py) — identical type,
palette and row treatment — plus a category chip row, because this event's
certificates are split across seven age groups and ranks restart at 1 in each.
The data is embedded inline, so fiitjee/index.html is fully self-contained.
"""
import json
import os

DATA = "fiitjee/certificates.json"
OUT = "fiitjee/index.html"


def main():
    with open(DATA, encoding="utf-8") as f:
        payload = json.load(f)

    categories = payload["categories"]
    # Flatten to one list; each row carries its category so "All" can label rows.
    rows = [
        {
            "rank": r["rank"],
            "name": r["name"],
            "cat": c["key"],
            "catLabel": c["label"],
            "view_url": r["view_url"],
        }
        for c in categories
        for r in c["records"]
    ]

    chips = "\n        ".join(
        '<button class="chip" type="button" data-cat="{key}">{label} '
        '<span class="chipn">{n}</span></button>'.format(
            key=c["key"], label=c["label"], n=len(c["records"])
        )
        for c in categories
    )

    html = (
        TEMPLATE.replace("__DATA__", json.dumps(rows, ensure_ascii=False))
        .replace("__CHIPS__", chips)
        .replace("__TOTAL__", str(len(rows)))
        .replace("__TITLE__", payload["event"])
        .replace("__SUB__", payload["subtitle"])
    )
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {OUT} with {len(rows)} certificates across "
          f"{len(categories)} categories embedded.")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Certificate Finder — __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Spline+Sans+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#1a1410;
    --paper:#f3ede1;
    --paper-2:#ece3d2;
    --maroon:#8b1e1e;
    --maroon-deep:#6d1414;
    --gold:#c8962a;
    --line:#d8ccb4;
    --shadow:rgba(40,24,12,.16);
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{
    margin:0;background:var(--paper);color:var(--ink);
    font-family:"Spline Sans Mono",ui-monospace,monospace;
    -webkit-font-smoothing:antialiased;
  }
  /* faint chessboard wash, the subject's own material, kept very quiet */
  body::before{
    content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.04;
    background-image:
      linear-gradient(45deg,var(--ink) 25%,transparent 25%,transparent 75%,var(--ink) 75%),
      linear-gradient(45deg,var(--ink) 25%,transparent 25%,transparent 75%,var(--ink) 75%);
    background-size:120px 120px;background-position:0 0,60px 60px;
  }
  .wrap{position:relative;z-index:1;max-width:980px;margin:0 auto;padding:0 20px}

  header{padding:64px 0 28px;border-bottom:2px solid var(--ink)}
  .eyebrow{
    font-size:12px;letter-spacing:.32em;text-transform:uppercase;
    color:var(--maroon);font-weight:600;margin:0 0 18px
  }
  h1{
    font-family:"Fraunces",Georgia,serif;font-weight:600;
    font-size:clamp(34px,6vw,60px);line-height:1.02;margin:0;letter-spacing:-.01em
  }
  .sub{margin:14px 0 0;font-size:14px;color:#6b5d49;letter-spacing:.02em}

  .tools{position:sticky;top:0;z-index:5;background:var(--paper);
    padding:22px 0 18px;border-bottom:1px solid var(--line);margin-bottom:6px}
  .searchrow{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
  .field{position:relative;flex:1 1 240px;min-width:200px}
  .field input{
    width:100%;padding:15px 16px 15px 44px;border:1.5px solid var(--ink);
    background:#fff;color:var(--ink);font-family:inherit;font-size:16px;border-radius:0;
  }
  .field input:focus{outline:3px solid var(--gold);outline-offset:1px}
  .field svg{position:absolute;left:15px;top:50%;transform:translateY(-50%);opacity:.55}
  .count{font-size:13px;color:#6b5d49;white-space:nowrap}
  .count b{color:var(--maroon)}

  /* category chips — same square, letterspaced idiom as the rest of the page */
  .cats{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 0}
  .chip{
    font-family:inherit;font-size:11px;letter-spacing:.14em;text-transform:uppercase;
    padding:8px 12px;border:1.5px solid var(--line);background:transparent;
    color:#6b5d49;cursor:pointer;border-radius:0;
    transition:background .12s,border-color .12s,color .12s
  }
  .chip:hover{border-color:var(--ink);color:var(--ink)}
  .chip:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
  .chip[aria-pressed="true"]{
    background:var(--maroon);border-color:var(--maroon);color:#fff
  }
  .chipn{font-variant-numeric:tabular-nums;opacity:.65;margin-left:4px}

  ul{list-style:none;margin:0;padding:22px 0 80px}
  .row{
    display:grid;grid-template-columns:64px 1fr auto;align-items:center;gap:18px;
    padding:14px 16px;border:1px solid transparent;border-bottom:1px solid var(--line);
    text-decoration:none;color:inherit;transition:background .12s,border-color .12s,transform .12s
  }
  .row:hover,.row:focus-visible{
    background:#fff;border-color:var(--ink);transform:translateX(3px);outline:none
  }
  .row:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
  .rank{
    font-family:"Fraunces",serif;font-size:26px;font-weight:600;color:var(--maroon);
    text-align:right;font-variant-numeric:tabular-nums
  }
  .rank .ord{font-size:13px;vertical-align:super;margin-left:1px;color:var(--gold)}
  .name{font-size:17px;font-weight:500;letter-spacing:.01em}
  .catbadge{
    display:inline-block;margin-left:10px;font-size:10px;letter-spacing:.16em;
    text-transform:uppercase;color:var(--gold);font-weight:600;white-space:nowrap
  }
  .open{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#6b5d49;
    display:flex;align-items:center;gap:7px}
  .row:hover .open{color:var(--maroon)}
  .open svg{transition:transform .12s}
  .row:hover .open svg{transform:translate(2px,-2px)}

  .empty{padding:60px 16px;text-align:center;color:#6b5d49}
  .empty b{color:var(--ink)}

  footer{border-top:2px solid var(--ink);padding:26px 0 60px;font-size:12px;color:#6b5d49;
    display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}

  @media (max-width:560px){
    .row{grid-template-columns:50px 1fr;gap:12px}
    .open{display:none}
    .rank{font-size:22px}
    .catbadge{display:block;margin:3px 0 0}
  }
  @media (prefers-reduced-motion:reduce){
    *{transition:none!important;scroll-behavior:auto}
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="eyebrow">Certificate of Merit · Find yours</p>
    <h1>__TITLE__</h1>
    <p class="sub">__SUB__</p>
  </header>

  <div class="tools">
    <div class="searchrow">
      <label class="field">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.2-3.2"/></svg>
        <input id="q" type="search" placeholder="Search by name or rank…" autocomplete="off" aria-label="Search certificates by name or rank">
      </label>
      <span class="count" id="count"></span>
    </div>
    <div class="cats" id="cats" role="group" aria-label="Filter by age category">
      <button class="chip" type="button" data-cat="">All</button>
      __CHIPS__
    </div>
  </div>

  <ul id="list" aria-live="polite"></ul>

  <footer>
    <span>__TOTAL__ certificates</span>
    <span>Opens each certificate in Google Drive</span>
  </footer>
</div>

<script>
const DATA = __DATA__;

function ordinal(n){
  const s=["th","st","nd","rd"], v=n%100;
  return n + (s[(v-20)%10]||s[v]||s[0]);
}
function ordSuffix(n){
  const s=["th","st","nd","rd"], v=n%100;
  return (s[(v-20)%10]||s[v]||s[0]);
}

const listEl=document.getElementById('list');
const countEl=document.getElementById('count');
const qEl=document.getElementById('q');
const catsEl=document.getElementById('cats');
const chips=[...catsEl.querySelectorAll('.chip')];

let cat='';   // '' = all categories

function render(items){
  listEl.innerHTML='';
  if(!items.length){
    listEl.innerHTML='<li class="empty">No match. Try a different <b>name</b> or <b>rank</b>.</li>';
    countEl.innerHTML='0 shown';
    return;
  }
  const frag=document.createDocumentFragment();
  for(const r of items){
    const a=document.createElement('a');
    a.className='row';
    a.href=r.view_url;
    a.target='_blank';
    a.rel='noopener';
    a.innerHTML=
      '<span class="rank">'+r.rank+'<span class="ord">'+ordSuffix(r.rank)+'</span></span>'+
      '<span class="name">'+r.name+
        (cat?'':'<span class="catbadge">'+r.catLabel+'</span>')+
      '</span>'+
      '<span class="open">Open <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17 17 7M9 7h8v8"/></svg></span>';
    frag.appendChild(a);
  }
  listEl.appendChild(frag);
  countEl.innerHTML='<b>'+items.length+'</b> shown';
}

function filter(){
  const t=qEl.value.trim().toLowerCase();
  const num=t.replace(/\D/g,'');
  const out=DATA.filter(r=>{
    if(cat && r.cat!==cat) return false;
    if(!t) return true;
    if(r.name.toLowerCase().includes(t)) return true;
    if(num && String(r.rank)===num) return true;
    return false;
  });
  render(out);
}

for(const c of chips){
  c.addEventListener('click',()=>{
    cat=c.dataset.cat;
    for(const o of chips) o.setAttribute('aria-pressed', String(o===c));
    filter();
  });
}
chips[0].setAttribute('aria-pressed','true');

qEl.addEventListener('input',filter);
filter();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
