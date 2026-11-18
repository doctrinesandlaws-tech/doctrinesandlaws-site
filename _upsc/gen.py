"""Builds the UPSC Law Optional desk: /upsc-law/ hub and one page per syllabus subject.

Called from build.py: gen.build(page, write, SITE, NAME, ORG, TODAY) -> list of URL paths.
Also returns the HTML for the homepage Student-desk panel.
"""
import html, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import notes_p1, notes_p2, craft_p1, craft_p2  # noqa: E402
from approach2026 import A as APPROACH  # noqa: E402
from y2026 import Y2026  # noqa: E402

e = html.escape

SUBJECTS = [
    # slug, title, paper, code, notes, pyq subject name, short label
    ("constitutional-administrative-law", "Constitutional and Administrative Law", "I", "CAL", notes_p1.CAL, "Constitutional and Administrative Law", "Constitutional & Administrative"),
    ("international-law", "International Law", "I", "IL", notes_p1.IL, "International Law", "International Law"),
    ("law-of-crimes", "Law of Crimes", "II", "CRIMES", notes_p2.CRIMES, "Law of Crimes", "Crimes"),
    ("law-of-torts", "Law of Torts", "II", "TORTS", notes_p2.TORTS, "Law of Torts", "Torts & Consumer Protection"),
    ("contracts-mercantile-law", "Law of Contracts and Mercantile Law", "II", "CONTRACTS", notes_p2.CONTRACTS, "Law of Contracts and Mercantile Law", "Contracts & Mercantile"),
    ("contemporary-legal-developments", "Contemporary Legal Developments", "II", "CLD", notes_p2.CLD, "Contemporary Legal Developments", "Contemporary Developments"),
]
CRAFT = {"CAL": craft_p1.CAL, "IL": craft_p1.IL, "CRIMES": craft_p2.CRIMES, "TORTS": craft_p2.TORTS, "CONTRACTS": craft_p2.CONTRACTS, "CLD": craft_p2.CLD}
EXTRA_TITLES = {("TORTS", 10): "Conspiracy."}

CSS = """<style>
.u-hero{margin:30px 0 8px}.u-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:18px 0}
.u-grid a{display:block;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px;text-decoration:none}
.u-grid a b{display:block;font:600 19px Fraunces,Georgia,serif;color:var(--teal)}.u-grid a span{font-size:13.5px;color:var(--muted)}
.u-paper{font:700 11px Inter;letter-spacing:.12em;text-transform:uppercase;color:var(--copper);margin:26px 0 0}
.u-toc{display:flex;flex-wrap:wrap;gap:6px;margin:16px 0}.u-toc a{font-size:13px;background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:5px 10px;text-decoration:none}
.u-unit{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:22px 24px;margin:22px 0;scroll-margin-top:16px}
.u-unit h2{font-size:24px;margin:4px 0 6px}.u-stat{font-size:13px;color:var(--muted)}.u-stat b{color:var(--copper)}
.u-unit h3{font:700 12px Inter;letter-spacing:.1em;text-transform:uppercase;color:var(--copper);margin:18px 0 6px}
.u-law{display:flex;flex-wrap:wrap;gap:6px;padding:0;margin:0;list-style:none}.u-law li{font-size:13.5px;background:var(--cream);border-radius:8px;padding:4px 9px}
.u-cases{padding-left:18px;margin:0}.u-cases li{margin:5px 0;font-size:15.5px}.u-cases i{color:var(--teal);font-style:italic;font-weight:600}
details.u-q{margin-top:14px;border-top:1px solid var(--line);padding-top:10px}details.u-q summary{cursor:pointer;font-weight:600;color:var(--teal)}
.u-q ol{padding-left:0;list-style:none;margin:8px 0}.u-q li{font-size:15px;margin:9px 0;padding-left:64px;position:relative}
.u-q li .y{position:absolute;left:0;top:1px;font:700 12px Inter;color:var(--copper);width:58px}.u-q li .y.n{color:#fff;background:var(--copper);border-radius:6px;padding:1px 5px;width:auto}
.u-q h4{font:600 13px Inter;color:var(--muted);margin:12px 0 2px}
.u-find{width:100%;padding:12px 14px;border:1px solid var(--line);border-radius:12px;font:inherit;background:var(--paper)}
table.u-t{width:100%;border-collapse:collapse;font-size:14.5px;background:var(--paper);border-radius:14px;overflow:hidden}
.u-t th,.u-t td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}.u-t th{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.u-note{font-size:14px;color:var(--muted)}
.u-decode{background:#F3E3D5;border-radius:12px;padding:12px 14px;margin:12px 0;font-size:15.5px}.u-decode b{color:var(--copper)}
.u-open{font-family:Fraunces,Georgia,serif;font-size:18px;color:var(--teal);border-left:3px solid var(--copper);padding-left:12px;margin:4px 0}
.u-frame{padding-left:20px;margin:0}.u-frame li{margin:4px 0}.u-edge{padding-left:18px;margin:0}.u-edge li{margin:4px 0;font-size:15.5px}
.u-flow{font:600 14px Inter;background:var(--cream);border:1px dashed var(--copper);border-radius:10px;padding:10px 12px}
.u-ap{margin-top:6px;font-size:14.5px;background:var(--cream);border-radius:10px;padding:8px 10px}.u-ap b{color:var(--teal)}
.u-method li{margin:6px 0}
</style>"""

FIND_JS = """<script>(function(){var f=document.getElementById('ufind');if(!f)return;f.addEventListener('input',function(){var q=f.value.toLowerCase().trim();
document.querySelectorAll('.u-unit').forEach(function(s){s.hidden=q&&s.textContent.toLowerCase().indexOf(q)<0;});});})();</script>"""


def load():
    pyq = json.load(open(os.path.join(HERE, "pyq.json"), encoding="utf-8"))
    by = {s["subject"]: s for s in pyq}
    out = []
    for slug, title, paper, code, notes, pname, short in SUBJECTS:
        topics = {t["n"]: t for t in by[pname]["topics"]}
        nums = sorted(set(notes) | {n for n in topics if n != 99})
        units = []
        for n in nums:
            t = topics.get(n, {"title": EXTRA_TITLES.get((code, n), ""), "qs": []})
            qs = [dict(q, new=False) for q in t["qs"]]
            for c, un, sub, qid, marks, text in Y2026:
                if c == code and un == n:
                    qs.append({"y": 2026, "q": f"{qid}, {marks} marks", "t": text, "sub": sub, "new": True, "ap": APPROACH.get(qid, "")})
            units.append({"n": n, "title": t["title"].rstrip("."), "qs": qs, "note": notes.get(n), "craft": CRAFT[code].get(n)})
        misc = topics.get(99, {"qs": []})["qs"]
        out.append(dict(slug=slug, title=title, paper=paper, code=code, short=short, units=units, misc=misc))
    return out


def qlist(qs):
    groups = {}
    for q in sorted(qs, key=lambda q: -q["y"]):
        groups.setdefault(q.get("sub") or "", []).append(q)
    h = []
    for sub, items in groups.items():
        if sub:
            h.append(f"<h4>{e(sub)}</h4>")
        h.append("<ol>")
        for q in items:
            cls = "y n" if q.get("new") else "y"
            ref = f' <span class="u-note">[{e(q["q"])}]</span>' if q.get("q") else ""
            ap = f'<div class="u-ap"><b>How to approach:</b> {e(q["ap"])}</div>' if q.get("ap") else ""
            h.append(f'<li><span class="{cls}">{q["y"]}</span>{e(q["t"])}{ref}{ap}</li>')
        h.append("</ol>")
    return "".join(h)


def unit_html(u):
    years = sorted({q["y"] for q in u["qs"]})
    stat = (f'Asked <b>{len(u["qs"])}</b> time{"s" if len(u["qs"]) != 1 else ""} · '
            f'{years[0]}–{years[-1]}' if years else "No question asked since 2013")
    if years and years[0] == years[-1]:
        stat = f'Asked <b>{len(u["qs"])}</b> time{"s" if len(u["qs"]) != 1 else ""} · {years[0]}'
    n = u["note"] or {}
    c = u.get("craft") or {}
    parts = [f'<section class="u-unit" id="u{u["n"]}"><span class="u-stat">Syllabus unit {u["n"]} · {stat}</span>',
             f'<h2>{e(u["title"])}</h2>']
    if c.get("decode"):
        parts.append(f'<div class="u-decode"><b>Decode the demand.</b> {e(c["decode"])}</div>')
    if c.get("intro"):
        parts.append(f'<h3>Open with</h3><p class="u-open">{e(c["intro"])}</p>')
    if c.get("frame"):
        parts.append("<h3>Answer frame</h3><ol class=\"u-frame\">" + "".join(f"<li>{e(x)}</li>" for x in c["frame"]) + "</ol>")
    if n.get("core"):
        parts.append(f'<h3>Concept in brief</h3><p>{e(n["core"])}</p>')
    if n.get("law"):
        parts.append("<h3>Key provisions</h3><ul class=\"u-law\">" + "".join(f"<li>{e(x)}</li>" for x in n["law"]) + "</ul>")
    if n.get("cases"):
        parts.append("<h3>Leading cases (cite the ratio, not the facts)</h3><ul class=\"u-cases\">" + "".join(f"<li><i>{e(cs)}</i>: {e(hd)}</li>" for cs, hd in n["cases"]) + "</ul>")
    if c.get("edge"):
        parts.append("<h3>Interdisciplinary edge</h3><ul class=\"u-edge\">" + "".join(f"<li>{e(x)}</li>" for x in c["edge"]) + "</ul>")
    if c.get("flow"):
        parts.append(f'<h3>Draw this</h3><p class="u-flow">{e(c["flow"])}</p>')
    if c.get("lens"):
        parts.append(f'<h3>Critical lens</h3><p>{e(c["lens"])}</p>')
    if c.get("close"):
        parts.append(f'<h3>Close with</h3><p class="u-open">{e(c["close"])}</p>')
    if u["qs"]:
        parts.append(f'<details class="u-q"{" open" if any(q.get("new") for q in u["qs"]) else ""}><summary>Previous-year questions ({len(u["qs"])})</summary>{qlist(u["qs"])}</details>')
    parts.append("</section>")
    return "".join(parts)


def build(page, write, SITE, NAME, ORG, TODAY):
    subs = load()
    paths = []
    all_units = []
    for s in subs:
        n_q = sum(len(u["qs"]) for u in s["units"]) + len(s["misc"])
        s["n_q"] = n_q
        toc = '<nav class="u-toc">' + "".join(f'<a href="#u{u["n"]}">{u["n"]}. {e(u["title"][:38])}{"…" if len(u["title"]) > 38 else ""}</a>' for u in s["units"]) + "</nav>"
        units = "".join(unit_html(u) for u in s["units"])
        misc = ""
        if s["misc"]:
            misc = f'<section class="u-unit" id="misc"><h2>Questions spanning several units</h2><details class="u-q" open><summary>Previous-year questions ({len(s["misc"])})</summary>{qlist([dict(q, new=False) for q in s["misc"]])}</details></section>'
        body = (CSS + f'<div class="u-hero"><span class="pill">UPSC CSE Law Optional · Paper {s["paper"]}</span>'
                f'<h1>{e(s["title"])}</h1><p class="dek">Each unit, in syllabus order, shows how to decode the question, frame the answer, which provisions and cases to cite, an interdisciplinary edge and a closing line, followed by every previous-year question from 2013 to 2026 ({n_q} questions).</p>'
                f'<p class="meta"><a href="/upsc-law/">UPSC Law Optional desk</a> · New 2026 questions are marked in copper.</p></div>'
                f'<input id="ufind" class="u-find" placeholder="Filter units: try a case, article or section, e.g. Art. 356, Bolam, s. 74" aria-label="Filter units">'
                f'{toc}{units}{misc}'
                f'<p class="u-note">Notes are original summaries prepared from the Constitution, statutes, treaties and judgments; check the full text of a judgment before citing it. IPC sections are given with their BNS, 2023 equivalents. General information for exam preparation, not legal advice.</p>'
                + FIND_JS)
        path = f"/upsc-law/{s['slug']}/"
        title = f"UPSC Law Optional: {s['title']} notes, cases and PYQs 2013–2026 | {NAME}"
        desc = f"{s['title']} for UPSC CSE Law Optional Paper {s['paper']}: syllabus-wise notes, key provisions, leading cases and {n_q} previous-year questions (2013–2026)."
        ld = {"@context": "https://schema.org", "@type": "LearningResource", "name": f"UPSC Law Optional: {s['title']}",
              "description": desc, "url": f"{SITE}{path}", "inLanguage": "en-IN", "educationalLevel": "Civil Services (Main) Examination",
              "learningResourceType": "Study notes and previous-year questions", "isAccessibleForFree": True,
              "dateModified": TODAY, "publisher": ORG, "author": ORG}
        write(f"upsc-law/{s['slug']}/index.html", page(title, desc, path, body, ld))
        paths.append(path)
        for u in s["units"]:
            all_units.append((len(u["qs"]), s, u))

    # Hub
    total = sum(s["n_q"] for s in subs)
    cards = []
    for paper in ("I", "II"):
        cards.append(f'<p class="u-paper">Paper {paper}</p><div class="u-grid">')
        for s in [x for x in subs if x["paper"] == paper]:
            cards.append(f'<a href="/upsc-law/{s["slug"]}/"><b>{e(s["title"])}</b><span>{len(s["units"])} units · {s["n_q"]} questions</span></a>')
        cards.append("</div>")
    top = sorted(all_units, key=lambda x: -x[0])[:12]
    toprows = "".join(f'<tr><td>{c}</td><td><a href="/upsc-law/{s["slug"]}/#u{u["n"]}">{e(u["title"])}</a></td><td>{e(s["short"])}</td></tr>' for c, s, u in top)
    subj_by_code = {s["code"]: s for s in subs}
    rows26 = "".join(
        f'<tr><td>{e(qid)}</td><td>{e(t[:150])}{"…" if len(t) > 150 else ""}</td><td><a href="/upsc-law/{subj_by_code[c]["slug"]}/#u{un}">{e(subj_by_code[c]["short"])}, unit {un}</a></td></tr>'
        for c, un, sub, qid, marks, t in Y2026)
    body = (CSS + f'<div class="u-hero"><span class="pill">Student desk</span><h1>UPSC Law Optional desk</h1>'
            f'<p class="dek">Both papers of the Civil Services (Main) Law optional, arranged unit by unit as in the official syllabus, with original notes, key provisions, leading cases and {total} previous-year questions from 2013 to 2026.</p></div>'
            + "".join(cards)
            + '<h2>The answer method behind every unit</h2><p>High-scoring Law optional answers share a pattern: they answer the exact question, build on sections and the ratio of cases, add a layer from outside the bare law, and end by looking forward. Each unit on this desk is written to that pattern.</p>'
            + '<ol class="u-method">'
            + '<li><b>Decode the demand.</b> Read the directive word first. <i>Discuss</i> wants both sides; <i>critically examine</i> or <i>evaluate</i> wants a verdict after testing the claim; <i>elucidate</i> or <i>explain</i> wants clarity with illustrations; <i>comment</i> wants a reasoned opinion. A quoted statement is a thesis to test, not to repeat. Count the parts of the question and answer every one.</li>'
            + '<li><b>Budget words by marks.</b> About 150 words for 10 marks, 200 for 15 and 250 for 20.</li>'
            + '<li><b>Open precisely.</b> One or two lines: a definition, the governing Article or section, or a sharp framing of the tension. No history lessons.</li>'
            + '<li><b>Build the body under headings.</b> Each heading makes one point and backs it with a provision and a case. Cite the ratio in a line; skip the facts unless the question is about them.</li>'
            + '<li><b>Solve problems with IRAC.</b> Issue, Rule (section plus case), Application to the facts, Conclusion. Commit to an answer.</li>'
            + '<li><b>Add the interdisciplinary edge.</b> Law Commission and committee reports, comparative law, jurisprudence, economics, data and current developments: one or two per answer, chosen for relevance.</li>'
            + '<li><b>Show a critical lens.</b> One honest limitation or counter-view shows judgement.</li>'
            + '<li><b>Draw when it helps.</b> A flowchart, timeline, table or zone diagram in a 15- or 20-mark answer saves words.</li>'
            + '<li><b>Close forward.</b> End with a way forward or a constitutional value, not a summary.</li></ol>'
            + '<p>Every unit page follows this order: decode the demand, an opening line, an answer frame, the concept, provisions and cases, the interdisciplinary edge, a diagram where useful, a critical lens and a closing line. Each 2026 question also carries a note on how to approach it.</p>'
            + f'<h2>Most-asked units, 2013–2026</h2><table class="u-t"><tr><th>Qs</th><th>Unit</th><th>Subject</th></tr>{toprows}</table>'
            + f'<h2>The 2026 papers, mapped to the syllabus</h2><p class="u-note">Every question from the 2026 Main examination (Law Paper I and Paper II), linked to the unit that covers it.</p><table class="u-t"><tr><th>Q</th><th>Question</th><th>Unit</th></tr>{rows26}</table>'
            + '<h2>Sources and method</h2><p>Questions are taken from the official UPSC question papers. Notes are written by Doctrines &amp; Laws from primary sources: the Constitution of India, Central Acts on India Code, treaties and the judgments themselves. For depth, pair them with standard texts such as M.P. Jain (Indian Constitutional Law), Malcolm Shaw (International Law), Ratanlal &amp; Dhirajlal (Law of Crimes and Law of Torts) and Pollock &amp; Mulla (Indian Contract Act). We do not reproduce coaching notes or toppers\' copies.</p>'
            + '<p class="u-note">General information for exam preparation, not legal advice. Spotted an error? Write to doctrinesandlaws@gmail.com.</p>')
    hub_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"UPSC Law Optional desk | {NAME}",
              "url": f"{SITE}/upsc-law/", "description": "Syllabus-wise UPSC CSE Law Optional notes, cases and previous-year questions.", "publisher": ORG}
    write("upsc-law/index.html", page(f"UPSC Law Optional: syllabus-wise notes, cases and PYQs (2013–2026) | {NAME}",
                                      f"Free UPSC CSE Law Optional desk: both papers unit by unit, with original notes, leading cases and {total} previous-year questions from 2013 to 2026.",
                                      "/upsc-law/", body, hub_ld, "website"))
    paths.insert(0, "/upsc-law/")

    panel = (f'<p class="srcnote" style="margin-top:0">Both papers of the UPSC Civil Services (Main) Law optional, unit by unit as in the syllabus: original notes, key provisions, leading cases and {total} previous-year questions (2013–2026).</p>'
             '<div class="res" style="margin-top:14px">'
             + "".join(f'<a href="/upsc-law/{s["slug"]}/"><b>{e(s["short"])}</b><span>Paper {s["paper"]} · {len(s["units"])} units · {s["n_q"]} questions</span></a>' for s in subs)
             + '</div><p style="margin-top:14px"><a href="/upsc-law/">Open the UPSC Law Optional desk &rarr;</a></p>')
    return paths, panel
