# hubielts

White Flarestamina **Practice Hub** — pick a skill, sit the paper, see the band.

Live: [flarestamina.com/hubielts](https://flarestamina.com/hubielts/)  
Landing: [flarestamina.com/newlanding](https://flarestamina.com/newlanding/)

## What this is

A student-first IELTS practice library. The first screen is four skills, not 100+ cards.

- **Listening / Reading / Writing / Speaking** — open a skill, then start a paper
- **Full Mock** — paid exam sitting, marked with a moving teal→indigo→fuchsia rail
- **Cambridge 21** — the free full book
- **Tools** — converter, plan, deadlines, speaking lab
- **EN / UZ**
- Light by default (x.ai paper). Dark is a toggle.

Tests themselves still live on their own Flarestamina URLs. This repo is the **index**.

## Brand

The mark is a four-point spark — SVG geometry, not a generated image.

```
M16 1.4 L17.85 13.55 L30.6 16 L17.85 18.45
L16 30.6 L14.15 18.45 L1.4 16 L14.15 13.55 Z
```

`favicon.svg`, `apple-touch-icon.png`, `og.png` are drawn from that path (HTML + Chromium screenshot). Nothing here is AI-generated artwork.

## Files

| File | Role |
| --- | --- |
| `index.html` | Hub UI (single page, no build step) |
| `results.html` | Local result history |
| `tests.json` | Catalog: title, category, url, difficulty |
| `favicon.svg` | Spark mark |
| `og.png` | 1200×630 Open Graph card |
| `og.svg` | Vector source for the card |
| `apple-touch-icon.png` | 180×180 |
| `site.webmanifest` | PWA name + icons |

## Catalog

`tests.json`:

```json
{
  "tests": [
    {
      "title": "Mock Listening 76",
      "category": "Listening",
      "url": "https://flarestamina.com/…",
      "difficulty": "Band 6-7"
    }
  ]
}
```

Categories the UI understands: `Listening`, `Reading`, `Writing`, `Speaking`, `Cambridge`, `Full Mock`, `Tools`.

Add a test → append an object → push. No rebuild.

## Local

```bash
python3 -m http.server 8080
# open http://127.0.0.1:8080/
```

## Deploy

GitHub Pages, `main`, `/`. Workflow: `.github/workflows/pages.yml`.

With the Flarestamina user site, this project is also served at:

`https://flarestamina.com/hubielts/`

## Account

Sign in is optional. Hub does not block practice. Results still write through the existing tracker on each test page (`IELTSTracker.sendResult`) into Google Sheets.

## License

Private / Flarestamina. Engineered in Tashkent.
