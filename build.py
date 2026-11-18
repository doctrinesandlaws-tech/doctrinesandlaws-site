#!/usr/bin/env python3
"""SEO build for doctrinesandlaws.netlify.app.

Run after editing the content arrays in index.html:
    python3 build.py

It reads POSTS from index.html and writes:
  - explainers/<slug>/index.html : one crawlable page per explainer
  - explainers/index.html         : list of all explainers
  - sitemap.xml, robots.txt
  - assets/crest.jpg, assets/og.png (share image)
  - the <!--SEO:START-->…<!--SEO:END--> block in index.html <head>
Needs: python3, node (to read the JS arrays), Pillow (for og.png).
"""
import base64, datetime, html, json, os, re, subprocess, sys

SITE = "https://doctrinesandlaws.netlify.app"
NAME = "Doctrines & Laws"
FIRM = "Doctrines & Laws Chambers"
ROOT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.today().isoformat()
MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def write(p, s, mode="w"):
    full = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        f.write(s)


def extract_array(src, name):
    start = src.index(f"const {name}=[")
    end = src.index("\n];", start) + 3
    js = src[start:end]
    code = js.replace(f"const {name}=", "const X=", 1) + "\nprocess.stdout.write(JSON.stringify(X));"
    out = subprocess.run(["node", "-e", code], capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"Could not parse {name}: {out.stderr}")
    return json.loads(out.stdout)


def month_iso(when):
    m = re.match(r"([A-Z][a-z]{2})\w* (\d{4})", when or "")
    return f"{m.group(2)}-{MONTHS[m.group(1)]:02d}-01" if m else TODAY


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


sys.path.insert(0, os.path.join(ROOT, "_build"))
import chrome  # noqa: E402
write("assets/site.css", chrome.SITE_CSS)

src = read("index.html")
crest_b64 = base64.b64encode(open(os.path.join(ROOT, "assets/crest.jpg"), "rb").read()).decode()

# share image (1200x630)
try:
    from PIL import Image, ImageDraw, ImageFont
    import io
    img = Image.new("RGB", (1200, 630), (246, 241, 231))
    d = ImageDraw.Draw(img)
    crest = Image.open(io.BytesIO(base64.b64decode(crest_b64))).convert("RGB").resize((300, 300))
    img.paste(crest, (820, 165))
    def font(names, size):
        for n in names:
            try:
                return ImageFont.truetype(n, size)
            except OSError:
                pass
        return ImageFont.load_default()
    serif = ["DejaVuSerif-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
    sans = ["DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    d.text((80, 150), "Law,", font=font(serif, 110), fill=(31, 74, 82))
    d.text((80, 270), "explained.", font=font(serif, 110), fill=(168, 100, 58))
    d.text((84, 452), "Free legal education · Doctrines & Laws", font=font(sans, 34), fill=(94, 107, 106))
    d.rectangle((80, 428, 200, 434), fill=(168, 100, 58))
    buf = io.BytesIO(); img.save(buf, "PNG", optimize=True)
    write("assets/og.png", buf.getvalue(), "wb")
except Exception as e:  # Pillow missing: keep crest as share image
    print("og.png skipped:", e)

posts = extract_array(src, "POSTS")
if "const ARCHIVE=[" in src:
    posts += extract_array(src, "ARCHIVE")

FIRM_LD = {"@type": "Organization", "name": FIRM,
           "address": {"@type": "PostalAddress", "streetAddress": "Asia House, Kasturba Gandhi Marg",
                       "addressLocality": "New Delhi", "postalCode": "110001", "addressCountry": "IN"}}
ORG = {"@type": "Organization", "name": NAME, "alternateName": "Law, explained.", "url": SITE + "/",
       "logo": SITE + "/assets/crest.jpg",
       "description": "A free legal-education initiative: Indian law explained for citizens, law students and UPSC Law Optional aspirants.",
       "email": "doctrinesandlaws@gmail.com", "parentOrganization": FIRM_LD,
       "sameAs": ["https://www.linkedin.com/company/doctrines-and-laws",
                  "https://www.instagram.com/doctrinesnlaws",
                  "https://x.com/doctrinesnlaws"]}

STYLE = """:root{--cream:#F6F1E7;--paper:#FFFDF8;--ink:#17323A;--teal:#1F4A52;--copper:#A8643A;--muted:#5E6B6A;--line:#E4DAC7}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;background:var(--cream);color:var(--ink);font:17px/1.7 Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-wrap:break-word}
main.wrap{padding-bottom:40px}h2{font-size:clamp(24px,3.4vw,30px);margin:34px 0 10px}
a{color:var(--teal)}.wrap{max-width:760px;margin:0 auto;padding:0 22px}
h1,h2{font-family:Fraunces,Georgia,serif;color:var(--teal);line-height:1.15}h1{font-size:clamp(32px,5vw,46px);margin:14px 0 10px}
.pill{display:inline-block;font:700 11px Inter;letter-spacing:.12em;text-transform:uppercase;color:var(--copper);background:#F3E3D5;padding:5px 10px;border-radius:999px}
.dek{color:var(--muted);font-size:19px;margin:0 0 24px}article{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:28px 30px;margin:28px 0}
.take{background:var(--cream);border-left:4px solid var(--copper);padding:12px 16px;border-radius:0 12px 12px 0;font-family:Fraunces,Georgia,serif;font-size:20px;color:var(--teal)}
.meta{font-size:14px;color:var(--muted)}.list a{display:block;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0;text-decoration:none}
.list b{display:block;font:600 21px Fraunces,Georgia,serif;color:var(--teal)}.list span{color:var(--muted);font-size:15px}
@media(max-width:600px){body{font-size:16.5px}article{padding:20px 18px;border-radius:16px}.dek{font-size:17.5px}}
.related{margin:8px 0 30px}.related h2{font-size:22px}
.gate{position:fixed;inset:0;background:rgba(19,41,46,.78);display:flex;align-items:center;justify-content:center;padding:14px;z-index:9}.gate[hidden]{display:none}
.gate .box{background:var(--paper);max-width:600px;border-radius:18px;padding:26px;border-top:6px solid var(--teal);max-height:92vh;overflow:auto;font-size:14.5px}
.gate h2{margin:0 0 10px}.gate button{border:0;border-radius:999px;padding:11px 22px;font-weight:600;cursor:pointer;background:var(--teal);color:#fff;margin-right:8px}
.gate button.g{background:transparent;color:var(--teal);border:1px solid var(--teal)}"""

GATE = """<div class="gate" id="gate" role="dialog" aria-modal="true"><div class="box"><h2>Disclaimer</h2>
<p>The Bar Council of India does not permit advocates to advertise or solicit work in any form or manner. By clicking “I Agree”, you acknowledge that you are accessing this website of your own accord; that there has been no advertisement, solicitation, invitation or inducement by Doctrines &amp; Laws Chambers or any of its members; and that the content is general legal information for education and awareness only, which does not constitute legal advice or create a lawyer–client relationship.</p>
<button id="agree">I Agree</button><button class="g" onclick="document.getElementById('nx').style.display='block'">Exit</button>
<p id="nx" style="display:none;color:#A8643A">You may close this window. The website can be viewed only after accepting the disclaimer.</p></div></div>
<script>(function(){var g=document.getElementById('gate');try{if(sessionStorage.getItem('dl-ok')==='1')g.hidden=true}catch(e){}
document.getElementById('agree').onclick=function(){try{sessionStorage.setItem('dl-ok','1')}catch(e){}g.hidden=true};
document.addEventListener('click',function(ev){if(ev.target.id==='showDisc'){ev.preventDefault();g.hidden=false;}});})();</script>"""


def page(title, desc, path, body, jsonld, og_type="article", active=""):
    url = f"{SITE}{path}"
    e = html.escape
    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/assets/crest-96.jpg"><link rel="apple-touch-icon" href="/assets/crest-192.jpg"><meta name="theme-color" content="#F6F1E7">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{e(NAME)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@DoctrinesnLaws">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,600;0,700;1,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<style>{STYLE}</style>
</head>
<body>
{GATE}
{chrome.header(active)}
<main class="wrap">{body}</main>
{chrome.footer(LATEST)}
</body>
</html>
"""


LATEST = [(p["title"], f"/explainers/{p['id'].replace('post-', '', 1)}/") for p in posts[:5]]
urls = [(f"{SITE}/", TODAY), (f"{SITE}/explainers/", TODAY)]
e = html.escape


def crumb_html(items):
    out = ['<nav class="crumbs" aria-label="Breadcrumb">']
    for i, (n, p) in enumerate(items):
        if i:
            out.append('<span aria-hidden="true">/</span>')
        out.append(f'<a href="{p}">{e(n)}</a>' if p else f"<span>{e(n)}</span>")
    return "".join(out) + "</nav>"


def crumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE}{p}"} for i, (n, p) in enumerate(items)]}


items = []
slugs = [(p, p["id"].replace("post-", "", 1)) for p in posts]
for idx, (p, slug) in enumerate(slugs):
    path = f"/explainers/{slug}/"
    desc = p["dek"]
    pub = month_iso(p.get("when"))
    trail = [("Home", "/"), ("Explainers", "/explainers/"), (p["title"], path)]
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": p["title"],
           "description": desc, "datePublished": pub, "dateModified": TODAY,
           "inLanguage": "en-IN", "mainEntityOfPage": f"{SITE}{path}",
           "image": f"{SITE}/assets/og.png", "author": ORG, "publisher": ORG,
           "articleSection": p["cat"], "isAccessibleForFree": True}, crumb_ld(trail)]
    ig = f'<p class="meta"><a href="https://www.instagram.com/p/{p["ig"]}/">See the carousel on Instagram</a> · <a href="/explainers/">All explainers</a></p>' if p.get("ig") else ""
    same = [x for x in slugs if x[0] is not p and x[0]["cat"] == p["cat"]]
    rest = [x for x in slugs if x[0] is not p and x[0]["cat"] != p["cat"]]
    rel = (same + rest)[:3]
    related = ('<section class="related"><h2>Read next</h2><div class="list">'
               + "".join(f'<a href="/explainers/{s2}/"><b>{e(q["title"])}</b><span>{e(q["dek"])}</span></a>' for q, s2 in rel)
               + '</div></section>')
    body = f"""{crumb_html(trail)}<article><span class="pill">{e(p['cat'])}</span>
<h1>{e(p['title'])}</h1><p class="dek">{e(desc)}</p>
<div>{p['body']}</div>
<p class="meta">{e(p.get('when', ''))} · General information, not legal advice.</p>{ig}</article>{related}"""
    write(f"explainers/{slug}/index.html", page(f"{p['title']} | {NAME}", desc, path, body, ld, active="explainers"))
    urls.append((f"{SITE}{path}", TODAY))
    items.append(f'<a href="{path}"><b>{e(p["title"])}</b><span>{e(desc)}</span></a>')

trail = [("Home", "/"), ("Explainers", "/explainers/")]
list_ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"Explainers | {NAME}",
            "url": f"{SITE}/explainers/", "publisher": ORG, "inLanguage": "en-IN", "isAccessibleForFree": True}, crumb_ld(trail)]
write("explainers/index.html", page(f"Indian law explained in plain language: free explainers | {NAME}",
      "Free plain-language explainers on Indian law: Supreme Court and High Court judgments, BNS, BNSS and other statutes, and your rights, by Doctrines & Laws.",
      "/explainers/", f'{crumb_html(trail)}<h1>Explainers</h1><p class="dek">Each explainer takes a single judgment or statute and answers the question a non-lawyer would actually ask.</p><div class="list">{"".join(items)}</div>',
      list_ld, "website", active="explainers"))

# UPSC Law Optional desk (source: _upsc/)
sys.path.insert(0, os.path.join(ROOT, "_upsc"))
import gen as upsc_gen  # noqa: E402
upsc_paths, upsc_panel, feat = upsc_gen.build(page, write, SITE, NAME, ORG, TODAY)
urls += [(f"{SITE}{p}", TODAY) for p in upsc_paths]

write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

# ---- homepage ----
HOME_TITLE = "Doctrines & Laws: free Indian law explainers and UPSC Law Optional notes"
HOME_DESC = ("Free legal education by Doctrines & Laws: plain-language explainers on Indian law, this week's Supreme Court rulings, "
             f"know-your-rights guides and UPSC Law Optional notes with {feat['total']} PYQs.")
home_ld = [{"@context": "https://schema.org", **ORG},
           {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "alternateName": "Law, explained.",
            "url": SITE + "/", "inLanguage": "en-IN", "publisher": {"@type": "Organization", "name": NAME, "url": SITE + "/"}}]
seo = f"""<!--SEO:START-->
<title>{e(HOME_TITLE)}</title>
<meta name="description" content="{e(HOME_DESC)}">
<link rel="canonical" href="{SITE}/">
<link rel="icon" href="/assets/crest-96.jpg"><link rel="apple-touch-icon" href="/assets/crest-192.jpg"><meta name="theme-color" content="#F6F1E7">
<link rel="stylesheet" href="/assets/site.css">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(HOME_TITLE)}">
<meta property="og:description" content="{e(HOME_DESC)}">
<meta property="og:url" content="{SITE}/"><meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@DoctrinesnLaws">
<script type="application/ld+json">{json.dumps(home_ld, ensure_ascii=False)}</script>
<!--SEO:END-->"""
src = re.sub(r"<title>.*?</title>\n", "", src, count=1, flags=re.S)
src = re.sub(r'<meta name="description"[^>]*>\n', "", src, count=1)
src = re.sub(r"<!--SEO:START-->.*?<!--SEO:END-->", lambda m: seo, src, flags=re.S)

subj_cards = "".join(
    f'<a class="uf-s" href="/upsc-law/{slug}/"><small>Paper {paper}</small><b>{e(title)}</b><span>{nu} units · {nq} questions</span></a>'
    for slug, title, paper, nu, nq in feat["subs"])
top_links = "".join(f'<li><a href="{p}">{e(l)}</a><span>{c} Qs</span></li>' for l, p, c in feat["top"])
upsc_feature = f"""<!--UPSCFEAT:START--><section class="uf" id="upsc" aria-labelledby="uf-h">
  <div class="wrap">
    <div class="uf-head reveal">
      <div><div class="kicker">UPSC CSE &middot; Law Optional</div>
      <h2 id="uf-h">The whole Law optional, <em>unit by unit.</em></h2>
      <p class="sub">Free notes for both papers in the order of the official syllabus: how to decode each question, an answer frame, provisions, leading cases and every previous-year question since 2013.</p></div>
      <div class="uf-stats"><div><b>{feat['units']}</b><span>syllabus units</span></div><div><b>{feat['total']}</b><span>past questions</span></div><div><b>2013&ndash;26</b><span>papers mapped</span></div></div>
    </div>
    <div class="uf-grid reveal">{subj_cards}</div>
    <div class="uf-foot reveal">
      <div class="uf-top"><h3>Most-asked units</h3><ol>{top_links}</ol></div>
      <a class="btn uf-cta" href="/upsc-law/">Open the UPSC Law Optional desk &rarr;</a>
    </div>
  </div>
</section><!--UPSCFEAT:END-->"""
src = re.sub(r"<!--UPSCFEAT:START-->.*?<!--UPSCFEAT:END-->", lambda m: upsc_feature, src, flags=re.S)
src = re.sub(r"<!--HDR:START-->.*?<!--HDR:END-->", lambda m: "<!--HDR:START-->" + chrome.header("", home=True) + "<!--HDR:END-->", src, flags=re.S)
src = re.sub(r"<!--FTR:START-->.*?<!--FTR:END-->", lambda m: "<!--FTR:START-->" + chrome.footer(LATEST) + "<!--FTR:END-->", src, flags=re.S)
src = re.sub(r"/\*UPSCX:START\*/.*?/\*UPSCX:END\*/", lambda m: "/*UPSCX:START*/" + json.dumps(feat["search"], ensure_ascii=False) + "/*UPSCX:END*/", src, flags=re.S)
src = re.sub(r"<!--UPSC:START-->.*?<!--UPSC:END-->", lambda m: "<!--UPSC:START-->" + upsc_panel + "<!--UPSC:END-->", src, flags=re.S)
src = src.replace('<html lang="en">', '<html lang="en-IN">', 1)
write("index.html", src)
print(f"Built {len(posts)} explainer pages, {len(upsc_paths)} UPSC pages, sitemap with {len(urls)} URLs.")
