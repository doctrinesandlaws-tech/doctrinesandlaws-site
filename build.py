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


src = read("index.html")
crest_b64 = re.search(r"data:image/jpeg;base64,([A-Za-z0-9+/=]+)", src).group(1)
write("assets/crest.jpg", base64.b64decode(crest_b64), "wb")

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
    d.text((84, 452), "Free legal-literacy hub · Doctrines & Laws", font=font(sans, 34), fill=(94, 107, 106))
    d.rectangle((80, 428, 200, 434), fill=(168, 100, 58))
    buf = io.BytesIO(); img.save(buf, "PNG", optimize=True)
    write("assets/og.png", buf.getvalue(), "wb")
except Exception as e:  # Pillow missing: keep crest as share image
    print("og.png skipped:", e)

posts = extract_array(src, "POSTS")
if "const ARCHIVE=[" in src:
    posts += extract_array(src, "ARCHIVE")

ORG = {"@type": "Organization", "name": FIRM, "url": SITE + "/",
       "logo": SITE + "/assets/crest.jpg",
       "address": {"@type": "PostalAddress", "streetAddress": "Asia House, Kasturba Gandhi Marg",
                   "addressLocality": "New Delhi", "postalCode": "110001", "addressCountry": "IN"},
       "email": "doctrinesandlaws@gmail.com",
       "sameAs": ["https://www.linkedin.com/company/doctrines-and-laws",
                  "https://www.instagram.com/doctrinesnlaws",
                  "https://x.com/doctrinesnlaws"]}

STYLE = """:root{--cream:#F6F1E7;--paper:#FFFDF8;--ink:#17323A;--teal:#1F4A52;--copper:#A8643A;--muted:#5E6B6A;--line:#E4DAC7}
*{box-sizing:border-box}body{margin:0;background:var(--cream);color:var(--ink);font:17px/1.7 Inter,system-ui,sans-serif}
a{color:var(--teal)}.wrap{max-width:760px;margin:0 auto;padding:0 22px}
header{border-bottom:1px solid var(--line);background:rgba(246,241,231,.9)}header .wrap{display:flex;align-items:center;justify-content:space-between;height:64px;max-width:1040px}
.brand{display:flex;gap:10px;align-items:center;text-decoration:none;font:700 20px Fraunces,Georgia,serif;color:var(--teal)}.brand img{width:36px;height:36px;border-radius:50%}
.brand i{color:var(--copper);font-style:normal}nav a{margin-left:18px;font-size:14px;text-decoration:none;color:var(--ink)}
h1,h2{font-family:Fraunces,Georgia,serif;color:var(--teal);line-height:1.15}h1{font-size:clamp(32px,5vw,46px);margin:14px 0 10px}
.pill{display:inline-block;font:700 11px Inter;letter-spacing:.12em;text-transform:uppercase;color:var(--copper);background:#F3E3D5;padding:5px 10px;border-radius:999px}
.dek{color:var(--muted);font-size:19px;margin:0 0 24px}article{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:28px 30px;margin:28px 0}
.take{background:var(--cream);border-left:4px solid var(--copper);padding:12px 16px;border-radius:0 12px 12px 0;font-family:Fraunces,Georgia,serif;font-size:20px;color:var(--teal)}
.meta{font-size:14px;color:var(--muted)}.list a{display:block;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0;text-decoration:none}
.list b{display:block;font:600 21px Fraunces,Georgia,serif;color:var(--teal)}.list span{color:var(--muted);font-size:15px}
footer{border-top:1px solid var(--line);margin-top:40px;padding:24px 0 40px;font-size:13.5px;color:var(--muted)}
.gate{position:fixed;inset:0;background:rgba(19,41,46,.78);display:flex;align-items:center;justify-content:center;padding:14px;z-index:9}.gate[hidden]{display:none}
.gate .box{background:var(--paper);max-width:600px;border-radius:18px;padding:26px;border-top:6px solid var(--teal);max-height:92vh;overflow:auto;font-size:14.5px}
.gate h2{margin:0 0 10px}.gate button{border:0;border-radius:999px;padding:11px 22px;font-weight:600;cursor:pointer;background:var(--teal);color:#fff;margin-right:8px}
.gate button.g{background:transparent;color:var(--teal);border:1px solid var(--teal)}"""

GATE = """<div class="gate" id="gate" role="dialog" aria-modal="true"><div class="box"><h2>Disclaimer</h2>
<p>The Bar Council of India does not permit advocates to advertise or solicit work in any form or manner. By clicking “I Agree”, you acknowledge that you are accessing this website of your own accord; that there has been no advertisement, solicitation, invitation or inducement by Doctrines &amp; Laws Chambers or any of its members; and that the content is general legal information for education and awareness only, which does not constitute legal advice or create a lawyer–client relationship.</p>
<button id="agree">I Agree</button><button class="g" onclick="document.getElementById('nx').style.display='block'">Exit</button>
<p id="nx" style="display:none;color:#A8643A">You may close this window. The website can be viewed only after accepting the disclaimer.</p></div></div>
<script>(function(){var g=document.getElementById('gate');try{if(sessionStorage.getItem('dl-ok')==='1')g.hidden=true}catch(e){}
document.getElementById('agree').onclick=function(){try{sessionStorage.setItem('dl-ok','1')}catch(e){}g.hidden=true};})();</script>"""


def page(title, desc, path, body, jsonld, og_type="article"):
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
<link rel="icon" href="/assets/crest.jpg">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{e(NAME)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@DoctrinesnLaws">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<style>{STYLE}</style>
</head>
<body>
{GATE}
<header><div class="wrap"><a class="brand" href="/"><img src="/assets/crest.jpg" alt="">Doctrines <i>&amp;</i> Laws</a>
<nav><a href="/explainers/">Explainers</a><a href="/#court">This week in court</a><a href="/#rights">Know your rights</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">All content is general legal information, provided for education and awareness. It is not legal advice and does not create a lawyer–client relationship. &copy; {datetime.date.today().year} {e(FIRM)}, New Delhi.</div></footer>
</body>
</html>
"""


urls = [(f"{SITE}/", TODAY), (f"{SITE}/explainers/", TODAY)]
items = []
for p in posts:
    slug = p["id"].replace("post-", "", 1)
    path = f"/explainers/{slug}/"
    desc = p["dek"]
    pub = month_iso(p.get("when"))
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": p["title"],
          "description": desc, "datePublished": pub, "dateModified": TODAY,
          "inLanguage": "en-IN", "mainEntityOfPage": f"{SITE}{path}",
          "image": f"{SITE}/assets/og.png", "author": ORG, "publisher": ORG,
          "articleSection": p["cat"], "isAccessibleForFree": True}
    ig = f'<p class="meta"><a href="https://www.instagram.com/p/{p["ig"]}/">See the carousel on Instagram</a> · <a href="/explainers/">All explainers</a></p>' if p.get("ig") else ""
    body = f"""<article><span class="pill">{html.escape(p['cat'])}</span>
<h1>{html.escape(p['title'])}</h1><p class="dek">{html.escape(desc)}</p>
<div>{p['body']}</div>
<p class="meta">{html.escape(p.get('when', ''))} · General information, not legal advice.</p>{ig}</article>"""
    write(f"explainers/{slug}/index.html", page(f"{p['title']} | {NAME}", desc, path, body, ld))
    urls.append((f"{SITE}{path}", TODAY))
    items.append(f'<a href="{path}"><b>{html.escape(p["title"])}</b><span>{html.escape(desc)}</span></a>')

list_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"Explainers | {NAME}",
           "url": f"{SITE}/explainers/", "publisher": ORG}
write("explainers/index.html", page(f"Legal explainers: Indian law in plain language | {NAME}",
      "Plain-language explainers on Indian Supreme Court and High Court judgments and statutes, by Doctrines & Laws.",
      "/explainers/", f'<h1>Explainers</h1><p class="dek">Each explainer takes a single judgment or statute and answers the question a non-lawyer would actually ask.</p><div class="list">{"".join(items)}</div>',
      list_ld, "website"))

write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

# SEO block in index.html head
home_ld = [{"@context": "https://schema.org", **ORG},
           {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE + "/",
            "inLanguage": "en-IN", "publisher": {"@type": "Organization", "name": FIRM}}]
seo = f"""<!--SEO:START-->
<link rel="canonical" href="{SITE}/">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="Doctrines &amp; Laws | Law, explained.">
<meta property="og:description" content="A free legal-literacy hub: plain-language explainers on Indian judgments and statutes, this week's Supreme Court rulings, know-your-rights guides and a study desk for law students.">
<meta property="og:url" content="{SITE}/"><meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@DoctrinesnLaws">
<script type="application/ld+json">{json.dumps(home_ld, ensure_ascii=False)}</script>
<!--SEO:END-->"""
if "<!--SEO:START-->" in src:
    src = re.sub(r"<!--SEO:START-->.*?<!--SEO:END-->", lambda m: seo, src, flags=re.S)
else:
    src = src.replace('<link rel="icon"', seo + '\n<link rel="icon"', 1)
src = src.replace('<html lang="en">', '<html lang="en-IN">', 1)
write("index.html", src)
print(f"Built {len(posts)} explainer pages, sitemap with {len(urls)} URLs.")
