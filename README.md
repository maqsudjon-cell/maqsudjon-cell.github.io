# Flarestamina

This repository is the live [flarestamina.com](https://flarestamina.com/) site. GitHub Pages serves it from `main` (see `CNAME`).

**Live:** https://flarestamina.com/

Free IELTS practice — Listening, Reading, Writing and Speaking — plus news, score tools, and an account that works across the tools.

## Stack

- Static HTML, CSS, and JavaScript.
- Firebase Auth for FS Account (`/account/`, shared client `/assets/fs-auth.js`, project `ieltshub-e2aa8`). Firestore for the Writing Lab, community articles, and `/admin/` (project `pangeya-essay`).
- GitHub Pages.
- Actions:
  - `.github/workflows/sitemap.yml` — rebuilds `sitemap.xml` and `news-sitemap.xml` with `.github/scripts/build_sitemap.py`
  - `.github/workflows/community.yml` — writes Firestore articles out to `/news/a/` and author pages under `/news/t/`
  - `.github/workflows/newsbot.yml` — fills the `/news/lenta/` feed

## Where things live

- `/` — homepage (`index.html`)
- `/tests/`, `/ielts-listening-test/`, `/ielts-reading-test/`, `/ielts-reading-passage-*` — practice catalogues in this repo. `/ielts-hub/` is the practice hub on the same domain.
- `/writing/` — Writing Lab
- `/speaking/` — redirect to the Speaking Lab at `/pangea8-speaking/`
- `/uz/` — Uzbek guides for the four skills
- `/news/` — articles, `/news/lenta/`, and community pages
- `/convert/`, `/deadlines/`, `/plan/`, `/speaking-topics/` — score converter, scholarship deadlines, study plan, speaking topics
- `/founder/`, `/teachers/`, `/privacy/`, `/writearticle/`, `/account/`, `/admin/`
- `/pangea8-landing/` — redirect stub to `/`, so the old path keeps working
