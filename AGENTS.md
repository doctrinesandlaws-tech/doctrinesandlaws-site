# Website agent rules (doctrinesandlaws-site)

- Edit content only in the arrays at the top of `index.html` (POSTS, DEVS, RIGHTS, CASES, MAP, MAXIMS, RES). Change layout or CSS only when asked.
- Never add: member profiles, testimonials, client lists, case results, fees, consultation buttons, contact forms, political consulting, ads or trackers.
- Before every push:
  1. Verify facts. Use real neutral citations; never invent one.
  2. Rule 36 check.
  3. Run a headless browser test at 1280 px and 390 px: zero console errors, the disclaimer gate works, search returns results, the reader modal opens.
  4. Look at screenshots of both sizes.
- Commit messages: `content: week of <date>` or `fix: <what>`. After pushing, fetch https://doctrinesandlaws.netlify.app and confirm the change is live. If the site breaks, run `git revert` and push.
- Report every run to the Social Media project at `website/reports/<YYYY-MM-DD>.md`.

## SEO build (run before every commit)
- Run `python3 build.py` after editing `index.html`. It regenerates:
  - `explainers/<slug>/` pages, one per POSTS item
  - `explainers/index.html`
  - `sitemap.xml`, `robots.txt`
  - `assets/og.png`
  - the `<!--SEO:START-->` block in `index.html`
- Never hand-edit the generated files; edit POSTS and rebuild.
- An explainer's slug is its POSTS `id` without `post-`. Never change a published slug, because its URL is indexed.

## Google Search Console
- `googledc4f398d4b61f658.html` verifies the site in Search Console (doctrinesandlaws@gmail.com). Never delete or edit it.

## UPSC Law Optional desk (`/upsc-law/`)
- Source lives in `_upsc/`: `notes_p1.py`, `notes_p2.py` (unit notes: core, provisions, leading cases), `pyq.json` (2013–2025 PYQs by syllabus unit), `y2026.py` (2026 papers). `build.py` calls `_upsc/gen.py`, which writes `/upsc-law/` and the six subject pages and fills the `<!--UPSC:START-->` panel in the Student desk.
- Keep it one part of the site: a Student-desk tab and a header link on inner pages only. Do not add it to the homepage hero or ticker.
- Each new UPSC Main paper: add its questions to `_upsc/` (map each to a syllabus unit), rebuild, and check the counts.
- Deepen one unit a week in the answer-method format (decode the demand, opening line, frame, concept, provisions, cases with ratio, interdisciplinary edge, diagram, critical lens, closing line). Learn from how toppers write (structure, decoding, interdisciplinary range), but write every line in our own words. Verify every case name, year and holding; cite IPC sections with BNS equivalents. For each new paper, add a "how to approach" note to every question in `approach<year>.py`.
