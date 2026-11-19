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
INDEXNOW_KEY = "bc132384cedc37a04eed05a67be7af63"  # IndexNow (Bing, Yandex, Seznam, Naver); the key file sits at the site root
HEADLINKS = ('<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/jpeg" sizes="96x96" href="/assets/crest-96.jpg">'
             '<link rel="apple-touch-icon" href="/assets/crest-192.jpg"><link rel="manifest" href="/site.webmanifest">'
             '<meta name="theme-color" content="#F6F1E7">'
             '<link rel="alternate" type="application/rss+xml" title="Doctrines &amp; Laws: explainers" href="/feed.xml">'
             '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
             '<meta property="og:image:alt" content="Doctrines &amp; Laws: Law, explained."><meta property="og:locale" content="en_IN">')
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
.topics{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 26px}.topics .chip{display:inline-block;border:1px solid var(--line);background:var(--paper);color:var(--teal);border-radius:999px;padding:7px 13px;font-size:14px;font-weight:600;text-decoration:none}
.topics .chip:hover{border-color:var(--copper);color:var(--copper)}.topics small{color:var(--muted);font-weight:500}
.widebox{width:min(1120px,94vw);position:relative;left:50%;transform:translateX(-50%)}
.widebox .list{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}.widebox .list a{margin:0}.widebox .dek{max-width:760px}
.topic-group{margin:10px 0 34px}.topic-group h2 a{text-decoration:none;color:var(--teal)}
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
{HEADLINKS}
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

# ---- topic hubs: one landing page per category, and a grouped explainers index ----
TOPIC_INTRO = {
    "Cyber law": "Online fraud, digital arrest scams, hacking and identity theft: what Indian law says and what to do when it happens to you.",
    "Technology": "How Indian law regulates platforms, apps and the internet: safe harbour, takedowns, blocking orders and your remedies as a user.",
    "AI & law": "Deepfakes, AI-generated content, copyright and AI training, and the rules India has made for artificial intelligence.",
    "Data privacy": "Your rights over personal data under the Digital Personal Data Protection Act, 2023 and the DPDP Rules, 2025.",
    "Entertainment & media": "Film certification, piracy, personality rights, celebrity deepfakes and the law that governs films, music and streaming.",
    "Sports & gaming": "Sports governance, athletes' rights, sports disputes, e-sports and the ban on real-money online games.",
    "Consumer": "Your rights as a buyer online and offline: dark patterns, hidden charges, refunds and how to complain.",
    "Constitutional": "Fundamental rights, the limits of State power and landmark constitutional judgments, explained in plain language.",
    "Criminal": "FIRs, arrest, bail and the new criminal laws (BNS, BNSS and BSA), explained for citizens.",
    "Civil": "Property disputes, accident compensation and everyday civil law questions.",
    "Evidence": "How courts treat electronic records, WhatsApp chats and other evidence under the Bharatiya Sakshya Adhiniyam, 2023.",
    "Administrative": "How government bodies must act: natural justice, reasoned orders and judicial review.",
}
TOPIC_ORDER = ["Cyber law", "Technology", "AI & law", "Data privacy", "Entertainment & media", "Sports & gaming",
               "Consumer", "Constitutional", "Criminal", "Civil", "Evidence", "Administrative"]


def topic_slug(c):
    return re.sub(r"[^a-z0-9]+", "-", c.lower().replace("&", "and")).strip("-")


by_cat = {}
for p, slug in slugs:
    by_cat.setdefault(p["cat"], []).append((p, slug))
cats = [c for c in TOPIC_ORDER if c in by_cat] + [c for c in by_cat if c not in TOPIC_ORDER]


def card(q, s2):
    return f'<a href="/explainers/{s2}/"><b>{e(q["title"])}</b><span>{e(q["dek"])}</span></a>'


chips = "".join(f'<a class="chip" href="/explainers/topic/{topic_slug(c)}/">{e(c)} <small>({len(by_cat[c])})</small></a>' for c in cats)
for c in cats:
    tpath = f"/explainers/topic/{topic_slug(c)}/"
    ttrail = trail + [(c, tpath)]
    intro = TOPIC_INTRO.get(c, f"Plain-language explainers on {c.lower()} in India.")
    tld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{c} in India: explainers | {NAME}",
            "url": f"{SITE}{tpath}", "description": intro, "publisher": ORG, "inLanguage": "en-IN", "isAccessibleForFree": True,
            "hasPart": [{"@type": "Article", "headline": q["title"], "url": f"{SITE}/explainers/{s2}/"} for q, s2 in by_cat[c]]},
           crumb_ld(ttrail)]
    others = "".join(f'<a class="chip" href="/explainers/topic/{topic_slug(x)}/">{e(x)}</a>' for x in cats if x != c)
    write(f"explainers/topic/{topic_slug(c)}/index.html", page(
        f"{c} in India Explained: Free Plain-Language Guides | {NAME}", intro, tpath,
        f'<div class="widebox">{crumb_html(ttrail)}<span class="pill">Topic</span><h1>{e(c)} in India, explained</h1><p class="dek">{e(intro)}</p>'
        f'<div class="list">{"".join(card(q, s2) for q, s2 in by_cat[c])}</div>'
        f'<section class="related"><h2>Other topics</h2><p class="topics">{others}</p></section></div>',
        tld, "website", active="explainers"))
    urls.append((f"{SITE}{tpath}", TODAY))

groups = "".join(
    f'<section class="topic-group" id="{topic_slug(c)}"><h2><a href="/explainers/topic/{topic_slug(c)}/">{e(c)}</a></h2>'
    f'<div class="list">{"".join(card(q, s2) for q, s2 in by_cat[c])}</div></section>' for c in cats)
list_ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"Explainers | {NAME}",
            "url": f"{SITE}/explainers/", "publisher": ORG, "inLanguage": "en-IN", "isAccessibleForFree": True}, crumb_ld(trail)]
write("explainers/index.html", page(f"Indian Law Explained in Plain Language: Free Explainers | {NAME}",
      "Free plain-language explainers on Indian law: cyber law, AI, technology, data privacy, entertainment, sports and gaming, consumer rights, constitutional and criminal law.",
      "/explainers/", f'<div class="widebox">{crumb_html(trail)}<h1>Explainers</h1><p class="dek">Each explainer takes a single judgment, statute or rule and answers the question a non-lawyer would actually ask. Browse by topic.</p>'
      f'<p class="topics">{chips}</p>{groups}</div>',
      list_ld, "website", active="explainers"))

# UPSC Law Optional desk (source: _upsc/)
sys.path.insert(0, os.path.join(ROOT, "_upsc"))
import gen as upsc_gen  # noqa: E402
upsc_paths, upsc_panel, feat = upsc_gen.build(page, write, SITE, NAME, ORG, TODAY)
urls += [(f"{SITE}{p}", TODAY) for p in upsc_paths]

write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

# ---- 404 page ----
write("404.html", page(f"Page not found | {NAME}", "This page does not exist. Try the explainers or the UPSC Law Optional desk.", "/404.html",
      '<h1>Page not found</h1><p class="dek">This page does not exist or has moved.</p>'
      '<div class="list"><a href="/"><b>Home</b><span>This week in court, know your rights and more</span></a>'
      '<a href="/explainers/"><b>Explainers</b><span>Indian law in plain language</span></a>'
      '<a href="/upsc-law/"><b>UPSC Law Optional</b><span>Study notes and past questions, unit by unit</span></a></div>',
      [{"@context": "https://schema.org", "@type": "WebPage", "name": "Page not found"}], "website").replace(
      '<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1))

# ---- discovery files: favicon, manifest, RSS feed, llms.txt, IndexNow key ----
try:
    from PIL import Image
    ico = Image.open(os.path.join(ROOT, "assets/crest.jpg")).convert("RGBA")
    ico.save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
except Exception as ex:
    print("favicon.ico skipped:", ex)
write("site.webmanifest", json.dumps({
    "name": "Doctrines & Laws: Indian law, explained", "short_name": "Doctrines & Laws",
    "description": "Free legal education: plain-language explainers on Indian law and UPSC Law Optional notes.",
    "start_url": "/", "scope": "/", "display": "browser", "lang": "en-IN",
    "background_color": "#F6F1E7", "theme_color": "#F6F1E7",
    "icons": [{"src": "/assets/crest-192.jpg", "sizes": "192x192", "type": "image/jpeg"},
              {"src": "/assets/crest.jpg", "sizes": "240x240", "type": "image/jpeg"}]}, indent=1) + "\n")
write(f"{INDEXNOW_KEY}.txt", INDEXNOW_KEY)


def rfc822(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%a, %d %b %Y 00:00:00 +0530")


feed_items = "".join(
    f"""<item><title>{e(p['title'])}</title><link>{SITE}/explainers/{slug}/</link><guid isPermaLink="true">{SITE}/explainers/{slug}/</guid>"""
    f"""<category>{e(p['cat'])}</category><pubDate>{rfc822(month_iso(p.get('when')))}</pubDate><description>{e(p['dek'])}</description></item>\n"""
    for p, slug in slugs)
write("feed.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>Doctrines &amp; Laws: Indian law, explained</title><link>{SITE}/</link>
<atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
<description>Free plain-language explainers on Indian law: Supreme Court and High Court rulings, statutes and your rights. General information, not legal advice.</description>
<language>en-IN</language><lastBuildDate>{rfc822(TODAY)}</lastBuildDate>
<image><url>{SITE}/assets/crest-192.jpg</url><title>Doctrines &amp; Laws: Indian law, explained</title><link>{SITE}/</link></image>
{feed_items}</channel></rss>
""")

llms = [f"# {NAME}", "",
        "> Law, explained. A free legal-education initiative of Doctrines & Laws Chambers, New Delhi: plain-language explainers on Indian law "
        "for citizens and law students, and free UPSC Civil Services Law Optional study notes. General information only, not legal advice.", "",
        "## Main sections", "",
        f"- [Home]({SITE}/): this week in court, know-your-rights guides, landmark cases, IPC to BNS section finder, official resources",
        f"- [Explainers]({SITE}/explainers/): one judgment or statute per page, answered in plain English",
        f"- [UPSC Law Optional]({SITE}/upsc-law/): study notes, answer frames and previous-year questions (2013 onwards) for every syllabus unit",
        "", "## Explainers", ""]
llms += [f"- [{p['title']}]({SITE}/explainers/{slug}/): {p['dek']}" for p, slug in slugs]
llms += ["", "## Explainer topics", ""] + [f"- [{c}]({SITE}/explainers/topic/{topic_slug(c)}/): {TOPIC_INTRO.get(c, '')}" for c in cats]
llms += ["", "## UPSC Law Optional subjects", ""]
llms += [f"- [{title}]({SITE}/upsc-law/{sl}/): Paper {paper}, {nu} units" for sl, title, paper, nu, nq in feat["subs"]]
llms += ["", "## Optional", "", f"- [Sitemap]({SITE}/sitemap.xml)", f"- [RSS feed]({SITE}/feed.xml)", ""]
write("llms.txt", "\n".join(llms))

# ---- homepage ----
HOME_TITLE = "Doctrines & Laws | Indian Law, Explained: Free Explainers and UPSC Law Optional Notes"
HOME_DESC = ("Free legal education by Doctrines & Laws. Plain-language explainers on cyber law, AI, data privacy, consumer and "
             f"constitutional rights, this week's Supreme Court rulings and UPSC Law Optional notes with {feat['total']} PYQs.")
home_ld = [{"@context": "https://schema.org", **ORG},
           {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "alternateName": "Law, explained.",
            "url": SITE + "/", "inLanguage": "en-IN", "publisher": {"@type": "Organization", "name": NAME, "url": SITE + "/"}}]
seo = f"""<!--SEO:START-->
<title>{e(HOME_TITLE)}</title>
<meta name="description" content="{e(HOME_DESC)}">
<link rel="canonical" href="{SITE}/">
{HEADLINKS}
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
      <p class="sub">Free study notes for both papers in the order of the official syllabus, with how to decode each question, an answer frame, leading cases and every previous-year question since 2013.</p></div>
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
