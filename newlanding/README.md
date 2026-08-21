# newlanding

Flarestamina marketing page — light, sparse, x.ai-grade motion.

Live: [flarestamina.com/newlanding](https://flarestamina.com/newlanding/)  
Hub: [flarestamina.com/hubielts](https://flarestamina.com/hubielts/)

## What this is

The public first screen of Flarestamina.

- White paper, Inter + IBM Plex Mono
- Spark mark with a short colour wash on load (teal → indigo → fuchsia)
- Cycling headline (`exam day.` / `Listening.` / …) with a gradient rail
- Four skills, tools, FAQ, founder note
- EN / UZ
- Start → Practice Hub (`/hubielts/`)

No account is required to open the hub from this page.

## Stack

- Vite 8
- React 19
- Tailwind v4 (`@theme` tokens)
- No backend. Static export.

Source of the built files lives with the Flarestamina app builder; **this repo is the published site**.

## Brand

Same four-point spark as the hub. `favicon.svg` and `og.png` are code-drawn (SVG path + Chromium raster). Not AI-generated.

OG line: **Practice like it’s exam day.**

## Files

| File | Role |
| --- | --- |
| `index.html` | SPA shell |
| `assets/` | JS + CSS from the Vite build (`base: '/newlanding/'`) |
| `favicon.svg` | Spark |
| `og.png` | 1200×630 card |
| `og.svg` | Vector source |
| `apple-touch-icon.png` | 180×180 |
| `404.html` | Same as index (GitHub Pages fallback) |
| `site.webmanifest` | Name + icons |

## Local

The published tree is already built. Serve it with the same base path:

```bash
python3 -m http.server 8080
# open http://127.0.0.1:8080/newlanding/
```

Or from the app-builder workspace:

```bash
npx vite build --config vite.landing.config.ts
```

`vite.landing.config.ts` sets `base: '/newlanding/'` so asset URLs match GitHub Pages.

## Deploy

GitHub Pages, `main`, `/`. Workflow: `.github/workflows/pages.yml`.

Project URL:

`https://flarestamina.com/newlanding/`

Do not put a `CNAME` in this repo — the apex domain already belongs to the user site.

## License

Private / Flarestamina. Engineered in Tashkent.
