"""Full study notes for each UPSC Law Optional unit.

One module per subject (CAL, IL, CRIMES, TORTS, CONTRACTS, CLD). Each defines NOTES = {unit_no: markdown_text}.
Markdown subset: '## ' heading, '### ' sub-heading, '- ' bullet, '1. ' numbered, '| a | b |' table rows,
'> ' revision box, **bold**, *italic*. Write every line in our own words; verify every case and section.
"""
import html, importlib, re

CODES = ["CAL", "IL", "CRIMES", "TORTS", "CONTRACTS", "CLD"]


def load_all():
    out = {}
    for c in CODES:
        try:
            m = importlib.import_module(f"study.{c.lower()}")
        except ModuleNotFoundError:
            continue
        for n, t in m.NOTES.items():
            out[(c, n)] = t
    return out


def _inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"(\d+(?:\([0-9A-Za-z]+\))?[–-]\d+(?:\([0-9A-Za-z]+\))?)", r'<span class="nw">\1</span>', s)
    return s


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:48]


def render(md):
    """Return (html, toc[list of (id, title)])."""
    lines = md.strip("\n").split("\n")
    out, toc, i = [], [], 0
    para = []

    def flush():
        if para:
            out.append("<p>" + _inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            flush(); i += 1; continue
        if ln.startswith("## "):
            flush(); t = ln[3:].strip(); hid = "n-" + slug(t); toc.append((hid, t))
            out.append(f'<h3 id="{hid}">{_inline(t)}</h3>'); i += 1; continue
        if ln.startswith("### "):
            flush(); out.append(f"<h4>{_inline(ln[4:].strip())}</h4>"); i += 1; continue
        if ln.startswith("> "):
            flush(); box = []
            while i < len(lines) and lines[i].startswith("> "):
                box.append(lines[i][2:]); i += 1
            out.append('<div class="u-rev">' + render("\n".join(box))[0] + "</div>"); continue
        if ln.startswith("|"):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            h = "".join(f"<th>{_inline(c)}</th>" for c in rows[0])
            b = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class="u-table-wrap"><table class="u-t u-nt"><tr>{h}</tr>{b}</table></div>'); continue
        m = re.match(r"^(\s*)(- |\d+\. )", ln)
        if m:
            flush(); tag = "ol" if m.group(2)[0].isdigit() else "ul"; items = []
            while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i]):
                item = re.sub(r"^(- |\d+\. )", "", lines[i]); i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                    item += " " + lines[i].strip(); i += 1
                items.append(f"<li>{_inline(item)}</li>")
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>"); continue
        para.append(ln.strip()); i += 1
    flush()
    return "".join(out), toc


def words(md):
    return len(re.sub(r"[#>|*\-]", " ", md).split())
