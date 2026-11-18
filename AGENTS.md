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
