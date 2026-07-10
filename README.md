# Flarestamina — Landing Page

Modern landing page for **[flarestamina.com](https://flarestamina.com)** — a free IELTS practice hub with 100+ tests.

**Live:** https://flarestamina.com/pangea8-landing/

## Features

- Dark hi-tech design — emerald/teal gradients, aurora glow, animated grid
- Spotlight hover cards, 3D tilt product mock, count-up stats, band-score gauge
- Test grid mock mirroring the real Practice Hub (3-column layout)
- **Google Sign-In** via Firebase Auth — signed-in users jump straight to the hub
- Single `index.html`, no build step, no frameworks — only Google Fonts + Firebase SDK
- Fully responsive, `prefers-reduced-motion` support

## Firebase setup (required for sign-in)

In [Firebase Console](https://console.firebase.google.com) → project `ieltshub-e2aa8`:

1. **Authentication → Sign-in method** → enable **Google**
2. **Authentication → Settings → Authorized domains** → add:
   - `flarestamina.com`
   - `flarestamina.com`

Without step 2, the Google popup will be blocked on those domains.

## Deploy

Hosted on **GitHub Pages** (branch `main`, root). Any static host works — it's one file.

---

Built with passion for students · [founder](https://maqsudjon.com)
