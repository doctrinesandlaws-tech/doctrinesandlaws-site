"""Shared site chrome (header, mobile menu, footer) for every page. Written to /assets/site.css and injected into HTML."""
import html

e = html.escape

SITE_CSS = r""":root{--cream:#F6F1E7;--paper:#FFFDF8;--ink:#17323A;--teal:#1F4A52;--teal-2:#2B6470;--deep:#13292E;--copper:#A8643A;--copper-2:#C98B5E;--gold:#F0C29C;--muted:#5E6B6A;--line:#E4DAC7;--sh:0 1px 2px rgba(23,50,58,.05),0 10px 30px rgba(23,50,58,.08)}
.sh{position:sticky;top:0;z-index:40;background:rgba(246,241,231,.9);-webkit-backdrop-filter:saturate(1.4) blur(12px);backdrop-filter:saturate(1.4) blur(12px);border-bottom:1px solid var(--line)}
.sh-in{max-width:1180px;margin:0 auto;padding:0 20px;height:68px;display:flex;align-items:center;gap:18px}
.sh .brand{display:flex;align-items:center;gap:10px;text-decoration:none;flex:none;min-width:0}
.sh .brand img{width:40px;height:40px;border-radius:50%;box-shadow:0 0 0 2px var(--paper);flex:none}
.sh .brand b{display:block;font:700 20px/1.1 Fraunces,Georgia,serif;color:var(--teal);white-space:nowrap}
.sh .brand b i{color:var(--copper);font-style:normal}
.sh .brand small{display:block;font:600 10.5px/1.3 Inter,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--copper);white-space:nowrap;margin-top:2px}
.sh-nav{display:flex;align-items:center;gap:2px;margin-left:auto}
.sh-nav a{white-space:nowrap;padding:8px 11px;border-radius:999px;text-decoration:none;color:var(--ink);font:500 14px Inter,system-ui,sans-serif}
.sh-nav a:hover{background:var(--paper);color:var(--copper)}
.sh-nav a[aria-current=page]{color:var(--copper)}
.sh-nav a.hot,.sh-hot{background:var(--teal);color:#fff!important;font-weight:600;padding:8px 14px}
.sh-nav a.hot:hover,.sh-hot:hover{background:var(--teal-2)}
.sh-hot{display:none;white-space:nowrap;border-radius:999px;text-decoration:none;font:600 13.5px Inter,system-ui,sans-serif;margin-left:auto}
.sh-act{display:flex;align-items:center;gap:8px;flex:none}
.sh-btn{display:inline-flex;align-items:center;gap:8px;height:40px;border:1px solid var(--line);background:var(--paper);border-radius:999px;padding:0 13px;color:var(--teal);cursor:pointer;font:500 14px Inter,system-ui,sans-serif;text-decoration:none;white-space:nowrap}
.sh-btn:hover{border-color:var(--copper-2)}
.sh-btn kbd{font:600 11px Inter;border:1px solid var(--line);border-radius:6px;padding:1px 6px;color:var(--muted)}
.sh-menu{display:none;width:40px;padding:0;justify-content:center}
.sh-menu span,.sh-menu span::before,.sh-menu span::after{display:block;width:17px;height:2px;background:var(--teal);border-radius:2px;position:relative;transition:.25s}
.sh-menu span::before,.sh-menu span::after{content:"";position:absolute;left:0}
.sh-menu span::before{top:-6px}.sh-menu span::after{top:6px}
.sh.open .sh-menu span{background:transparent}.sh.open .sh-menu span::before{top:0;transform:rotate(45deg)}.sh.open .sh-menu span::after{top:0;transform:rotate(-45deg)}
.sheet{display:none;border-top:1px solid var(--line);background:var(--paper);max-height:calc(100vh - 68px);overflow:auto;box-shadow:0 30px 60px rgba(23,50,58,.18)}
.sh.open .sheet{display:block;animation:shDrop .25s ease}
@keyframes shDrop{from{opacity:0;transform:translateY(-6px)}}
.sheet-in{max-width:1180px;margin:0 auto;padding:18px 20px 26px;display:grid;gap:18px}
.sheet a{text-decoration:none}
.sheet .feat{display:block;border-radius:18px;padding:18px;background:linear-gradient(135deg,var(--teal),#173A40);color:#E6EFED}
.sheet .feat small{font:700 11px Inter;letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}
.sheet .feat b{display:block;font:600 22px/1.2 Fraunces,Georgia,serif;color:#fff;margin:6px 0 4px}
.sheet .feat span{font-size:14px;color:#BFD3D0}
.sheet .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px}
.sheet .grid a{display:block;padding:12px 14px;border:1px solid var(--line);border-radius:14px;background:var(--cream)}
.sheet .grid a b{display:block;color:var(--teal);font:600 16px Fraunces,Georgia,serif}
.sheet .grid a span{font-size:13px;color:var(--muted)}
.sheet h6{margin:4px 0 0;font:700 11px Inter;letter-spacing:.16em;text-transform:uppercase;color:var(--copper)}
.sheet .subj{display:flex;flex-wrap:wrap;gap:8px}
.sheet .subj a{font-size:13.5px;padding:7px 12px;border-radius:999px;border:1px solid var(--line);color:var(--teal);background:var(--paper)}
@media (max-width:1180px){.sh-nav{display:none}.sh-menu{display:inline-flex}.sh-hot{display:inline-flex;align-items:center;height:40px;padding:0 15px}}
@media (max-width:760px){.sh-hot{display:none}.sh-act{margin-left:auto}}
@media (max-width:640px){.sh-btn .t,.sh-btn kbd{display:none}.sh-btn.s{width:40px;padding:0;justify-content:center}}
@media (max-width:420px){.sh-in{padding:0 14px;gap:10px}.sh .brand b{font-size:18px}.sh .brand img{width:36px;height:36px}.sh .brand small{font-size:9.5px;letter-spacing:.1em}}
.sf{background:var(--deep);color:#9DB4B0;padding:56px 0 40px;font:14px/1.6 Inter,system-ui,sans-serif}
.sf-in{max-width:1180px;margin:0 auto;padding:0 20px}
.sf-top{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:30px}
.sf .brand{display:flex;align-items:center;gap:10px;text-decoration:none}
.sf .brand img{width:40px;height:40px;border-radius:50%}
.sf .brand b{font:700 20px Fraunces,Georgia,serif;color:#fff}.sf .brand b i{color:var(--gold);font-style:normal}
.sf .mission{margin:14px 0 16px;color:#BFD3D0;max-width:340px}
.sf h6{margin:0 0 12px;font:700 11.5px Inter;letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}
.sf ul{list-style:none;margin:0;padding:0}.sf li{margin:0 0 8px}
.sf a{color:#DCE7E5;text-decoration:none}.sf a:hover{color:var(--gold)}
.sf .soc{display:flex;gap:8px;flex-wrap:wrap}.sf .soc a{border:1px solid #2E4B51;border-radius:999px;padding:6px 13px;font-size:13px}
.sf-bot{border-top:1px solid #24414A;margin-top:34px;padding-top:22px;font-size:13px;color:#87A19C}
.sf-bot p{margin:0 0 8px;max-width:900px}
@media (max-width:900px){.sf-top{grid-template-columns:1fr 1fr}.sf-top>div:first-child{grid-column:1/-1}}
@media (max-width:480px){.sf{padding:44px 0 32px}.sf-top{gap:24px}}
.crumbs{font-size:13px;color:var(--muted);margin:22px 0 0;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.crumbs a{color:var(--muted);text-decoration:none}.crumbs a:hover{color:var(--copper)}
.crumbs span[aria-hidden]{color:#C9B99E}
"""

SUBJECT_LINKS = [
    ("constitutional-administrative-law", "Constitutional & Administrative Law"),
    ("international-law", "International Law"),
    ("law-of-crimes", "Law of Crimes"),
    ("law-of-torts", "Law of Torts & Consumer Protection"),
    ("contracts-mercantile-law", "Contracts & Mercantile Law"),
    ("contemporary-legal-developments", "Contemporary Legal Developments"),
]

MENU_JS = """<script>(function(){var h=document.getElementById('sh'),b=document.getElementById('shMenu');if(!h||!b)return;
function set(o){h.classList.toggle('open',o);b.setAttribute('aria-expanded',o);}
b.addEventListener('click',function(){set(!h.classList.contains('open'))});
h.querySelector('.sheet').addEventListener('click',function(ev){if(ev.target.closest('a'))set(false)});
document.addEventListener('keydown',function(ev){if(ev.key==='Escape')set(false)});})();</script>"""


def header(active="", home=False):
    def cur(k):
        return ' aria-current="page"' if k == active else ""
    search = ('<button class="sh-btn s" id="openSearch" aria-label="Search the site">' if home
              else '<a class="sh-btn s" href="/#search" aria-label="Search the site">')
    search += ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
               '<span class="t">Search</span>' + ("<kbd>/</kbd></button>" if home else "</a>"))
    subj = "".join(f'<a href="/upsc-law/{s}/">{e(t)}</a>' for s, t in SUBJECT_LINKS)
    return f"""<header class="sh" id="sh">
<div class="sh-in">
<a class="brand" href="/" aria-label="Doctrines &amp; Laws home"><img src="/assets/crest-96.jpg" alt="" width="40" height="40"><span><b>Doctrines <i>&amp;</i> Laws</b><small>Free legal education</small></span></a>
<nav class="sh-nav" aria-label="Main">
<a href="/explainers/"{cur('explainers')}>Explainers</a><a href="/#court"{cur('court')}>This week in court</a><a href="/#rights"{cur('rights')}>Know your rights</a><a href="/#desk"{cur('desk')}>Student desk</a><a class="hot" href="/upsc-law/"{cur('upsc')}>UPSC Law Optional</a>
</nav>
<a class="sh-hot" href="/upsc-law/">UPSC Law Optional</a>
<div class="sh-act">{search}<button class="sh-btn sh-menu" id="shMenu" aria-label="Open menu" aria-expanded="false" aria-controls="sheet"><span></span></button></div>
</div>
<div class="sheet" id="sheet"><div class="sheet-in">
<a class="feat" href="/upsc-law/"><small>UPSC CSE &middot; Law Optional</small><b>Both papers, unit by unit</b><span>Notes, answer frames, leading cases and every question since 2013.</span></a>
<div class="subj">{subj}</div>
<h6>Explore</h6>
<div class="grid">
<a href="/explainers/"><b>Explainers</b><span>Indian law in plain language</span></a>
<a href="/#court"><b>This week in court</b><span>Supreme Court rulings in one line</span></a>
<a href="/#rights"><b>Know your rights</b><span>Arrest, FIR, legal aid, consumer</span></a>
<a href="/#desk"><b>Student desk</b><span>Cases, IPC&rarr;BNS finder, maxims</span></a>
<a href="/#resources"><b>Official resources</b><span>Courts, statutes, complaints</span></a>
<a href="/#about"><b>About</b><span>Who runs this, and why</span></a>
</div>
</div></div>
</header>
{MENU_JS}"""


def footer(latest=()):
    lat = "".join(f'<li><a href="{e(u)}">{e(t)}</a></li>' for t, u in latest[:5])
    subj = "".join(f'<li><a href="/upsc-law/{s}/">{e(t)}</a></li>' for s, t in SUBJECT_LINKS)
    return f"""<footer class="sf"><div class="sf-in">
<div class="sf-top">
<div><a class="brand" href="/"><img src="/assets/crest-96.jpg" alt="" width="40" height="40" loading="lazy"><b>Doctrines <i>&amp;</i> Laws</b></a>
<p class="mission">A free legal-education initiative of Doctrines &amp; Laws Chambers, New Delhi: Indian law explained for citizens, law students and civil-services aspirants.</p>
<div class="soc"><a href="https://www.instagram.com/doctrinesnlaws">Instagram</a><a href="https://x.com/doctrinesnlaws">X</a><a href="https://www.linkedin.com/company/doctrines-and-laws">LinkedIn</a></div></div>
<div><h6>UPSC Law Optional</h6><ul><li><a href="/upsc-law/">The desk</a></li>{subj}</ul></div>
<div><h6>Latest explainers</h6><ul>{lat}<li><a href="/explainers/">All explainers &rarr;</a></li></ul></div>
<div><h6>Learn</h6><ul><li><a href="/#court">This week in court</a></li><li><a href="/#rights">Know your rights</a></li><li><a href="/#desk">Student desk</a></li><li><a href="/#resources">Official resources</a></li><li><a href="/#about">About</a></li><li><a href="mailto:doctrinesandlaws@gmail.com">Suggest a topic</a></li></ul></div>
</div>
<div class="sf-bot"><p>All content is general legal information for education and awareness. It is not legal advice and does not create a lawyer&ndash;client relationship. Laws and judgments change, so verify with the official text. Nothing here is an advertisement or solicitation within the meaning of Rule 36 of the Bar Council of India Rules.</p>
<p>&copy; 2026 Doctrines &amp; Laws &middot; An initiative of Doctrines &amp; Laws Chambers, New Delhi &middot; <a href="#" id="showDisc">Disclaimer</a></p></div>
</div></footer>"""
