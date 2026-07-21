# App Legal Center

Static website hosting the Terms of Service and per-app Privacy Policies for
my iOS apps, for use with App Store Connect.

- **`generate.py`** — the generator. All content lives here (developer info,
  app list, legal text). Edit it, then run `python3 generate.py`.
- **`docs/`** — the generated website. This is what GitHub Pages serves.
  Do not hand-edit files in here; they are overwritten on each run.

## Update the site

1. Edit `CONFIG` (your name / email / jurisdiction) or the `APPS` list in
   `generate.py`.
2. Run:
   ```
   python3 generate.py
   ```
3. Commit and push (see below). GitHub Pages redeploys automatically.

## Deploy to GitHub Pages (one-time setup)

1. Create a free account at https://github.com if you don't have one.
2. Create a new **public** repository named `legal` (empty — no README).
3. In this folder, push the code:
   ```
   git remote add origin https://github.com/YOUR_USERNAME/legal.git
   git branch -M main
   git push -u origin main
   ```
4. On GitHub: **Settings → Pages**. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main**, folder: **/docs** → **Save**.
5. Wait ~1 minute. Your site is live at:
   ```
   https://YOUR_USERNAME.github.io/legal/
   ```

## URLs to paste into App Store Connect

For each app, the **Privacy Policy URL** is:

```
https://YOUR_USERNAME.github.io/legal/privacy/<slug>.html
```

The shared **Terms of Use (EULA) URL** (optional; use if you don't rely on
Apple's standard EULA) is:

```
https://YOUR_USERNAME.github.io/legal/terms.html
```

App slugs: color-sort, reactor, blockburst, matcha-tycoon, econquest,
strategylab, derivatives-101, cashflow, dailyhealth, signquest, oleloquest,
pourfolio, chapteros.

## Before you submit — verify each app's data category

The Privacy Policy for each app must match what the app actually does and the
Privacy "nutrition label" you fill out in App Store Connect. Categories used:

- **offline** — collects/transmits no data (Derivatives 101, Cashflow,
  DailyHealth, SignQuest).
- **ads** — shows Google AdMob ads, which collect device/ad data (Color Sort,
  Reactor, BlockBurst, Matcha Shop Tycoon, EconQuest, StrategyLab).
- **iap** — in-app purchases, offline content, no ads (ʻŌleloQuest).
- **cloud** — accounts + data stored in Firebase (Pourfolio, ChapterOS).

If an app's data practices change (e.g. you add or remove ads, or add
accounts), change its `category` in `generate.py` and regenerate.
