# HANDOFF — FLARESTAMINA (formerly pangea8)

_Last updated: 2026-07-15 — /founder + /news (News & Deadlines) shipped by Claude Code._

## /founder + /news (shipped 2026-07-15)

- **`/founder/`** — t3.gg-style minimal profile of Maqsudjon Polatov (JetBrains Mono, black, flare orange). Person + ProfilePage JSON-LD; the Person `@id` `https://flarestamina.com/founder/#person` is referenced as `author` by every news article (E-E-A-T link).
- **`/news/`** — "IELTS News & Deadlines": static index + one static dir per post (`/news/<slug>/index.html`). Shared CSS `/news/news.css`. Every post has: NewsArticle JSON-LD (+ FAQPage where useful), key-facts box, 🇺🇿 Qisqacha Uzbek summary (bilingual SEO), small "Source / Manba" attribution link (`rel="noopener nofollow"`), CTA into the hub, GoatCounter.
- **Adding a post:** copy `/news/_template.html` → follow the checklist comment at the top (template → posts.json → index card → feed.xml → push).
- **`/news/posts.json`** — machine-readable post index; **the sitemap workflow reads it** (`.github/workflows/sitemap.yml` now merges tests.json URLs + news posts + /founder/).
- **`/news/feed.xml`** — RSS 2.0, linked from index `<link rel="alternate">`.
- **IMPORTANT (auth gate):** founder/news deliberately do NOT load `fs-auth.js` — they must stay public or Google can't index them (see CRITICAL SEO fix below).
- Homepage links added: top nav "News", footer "News & Deadlines", footer founder credit → `/founder/`.
- Search Console: indexing requested 2026-07-15 for `/news/`, `/founder/`, `/writearticle/` (done via Chrome). News articles get discovered via sitemap.

## Community layer (shipped 2026-07-15, wave 2)

- **Backend:** Firestore REST on project **`pangeya-essay`** (public web key `AIzaSyBnmbg7...` — same open-rules model as the essay lab; ieltshub-e2aa8 rules DENY anon writes, that's why pangeya-essay). Collections: `articles`, `advice`, `advice_comments`. ⚠️ Rules are wide open (create/read/delete) — fine for launch, tighten later + add a moderation flag.
- **`/writearticle/`** — teacher-friendly Uzbek form (draft autosave in localStorage, honeypot, min 200 chars) → creates `articles` doc → appears in /news → Articles tab. Share this link directly with teachers.
- **`/news/` tabs** (`news/community.js`): `news | articles | ideas & advice` (hash-routed: /news/#articles, /news/#ideas). Articles = Firestore + `news/articles-seed.json` (2 editorial seeds, repo-versioned) with overlay reader. Ideas = FS Account composer (fs-auth.js loaded WITHOUT require() — page stays public/indexable), likes (field-transform increment + localStorage one-like guard), comments, Telegram share. Welcome post seeded in `advice`.
- **Hub card** added to `ielts-hub/tests.json` ("News, Deadlines & Community", category Tools) via GitHub API.
- GoatCounter events: article-published, article-read, advice-post, advice-like, advice-comment.

## Admin panel + bilingual + theme (shipped 2026-07-15, wave 3)

- **`/admin/`** — passcode-gated control panel (noindex + robots Disallow). Passcode SHA-256 stored as `PASS_HASH` in the page (plaintext = `Flare$Maqsud-2026!admin`; change by replacing the hash with `printf '%s' 'NEW' | shasum -a 256`). sessionStorage unlock. Tabs: Overview (site page links + mgmt tools: Search Console, GoatCounter, both Firebase consoles, GitHub repos, sitemap/robots/RSS), Articles (list/hide/show/edit-incl-UZ/delete Firestore `articles`), Ideas & Advice (list/hide/show/delete `advice` + delete `advice_comments`), Promote (ready TG/Twitter copy), Settings (security notes). Uses Firestore REST PATCH (updateMask) + DELETE on project pangeya-essay.
- **Hidden flag:** admin sets `hidden:true`; community.js filters hidden articles/advice from public /news. `fv()` now decodes booleanValue.
- **Bilingual articles:** Firestore articles may carry `title_uz`/`body_uz`/`lang`. community.js reader shows an EN/Oʻzbekcha toggle when both exist; card shows EN + "EN·UZ" badge. The 2 editorial articles now live in Firestore (owner:true), bilingual — the old "my students" framing was corrected. articles-seed.json is now empty (fallback only).
- **`/writearticle`:** full UZ/EN interface toggle (localStorage `fs_lang`) for foreign teachers + an article-language selector (writes `lang`).
- **Theme:** all `/news/*` pages + `/writearticle` + `/admin` now use the hub palette (warm-black `#0A0605` dark / `#F6F8F7` light) and a ◐ toggle that shares the hub's `p8-theme` localStorage key, so theme carries across the whole site.
- ⚠️ Firestore rules still open (create/read/update/delete) — hardening (restrict update/delete to owner) is the recommended next step; noted in /admin Settings tab.

## Brand

| Token | Value |
|---|---|
| Accent (flare orange) | `#FF5A1F` (press `#E8501A`, light-theme text-safe `#D9480F`, warm ramp `#FF7A3D` / `#FFA45C`) |
| Background | `#000000`, JetBrains Mono everywhere |
| Sub-tool red (Essay / Speaking) | `#D71921` — unchanged by design |
| Wordmark | two-tone: `FLARE` in orange, `STAMINA` in white; in prose: “Flarestamina” |
| Logo | 4-ray asymmetric flare mark (top ray longer), stroke-based, legible at 16 px |

Assets in this repo (MAIN): `/assets/logo.svg`, `/assets/mark.svg`, `favicon.svg`, `favicon.ico` (16/32/48), `favicon-96.png`, `apple-touch-icon.png` (180), `icon-192.png`, `icon-512.png`, `og-image.png`, `site.webmanifest`. The same icon set was pushed to `ielts-hub`, `ielts-hub-landing`, `ielts-hub-staging` (as `web-app-manifest-*.png`) and `pangea8-landing`.

## Domains

- **flarestamina.com** → MAIN (`maqsudjon-cell.github.io`, CNAME file). All project repos are reachable at `flarestamina.com/<repo>/`.
- **pangea8.com** → new repo `pangea8-redirect`: `index.html` + `404.html` do `location.replace('https://flarestamina.com' + path + search + hash)` with a `<meta refresh>` fallback — every old deep link survives.
- The `flarestamina` repo (the original 40-Day Challenge app, “Ignite Your Endurance”) lost its CNAME; the app itself is intact at `flarestamina.com/flarestamina/`.

## FS Account (one sign-up for the whole ecosystem)

**Backend = Firebase Auth, project `ieltshub-e2aa8` (owner's decision 2026-07-10: no Supabase).** The phone number is stored as an email alias `<digits>@fs.flarestamina.com`; the full name lives in the Firebase `displayName`. No server code, no env vars, no database setup — the account page talks to `identitytoolkit.googleapis.com` directly with the public web API key (same key as `signin.html`).

- **Client:** `/assets/fs-auth.js` — `FSAuth.getUser() / getToken() / require() / logout() / save()`. Session: localStorage `fs_session = {token, user, refreshToken}` shared across all `flarestamina.com` paths. Sessions are long-lived: the user object identifies the student; the Firebase idToken (~1 h) only matters for future server-verified calls (refresh via `securetoken.googleapis.com` with the stored refreshToken).
  - `ENFORCE` flag at the top: **true since 2026-07-11** — FS Account is mandatory everywhere (one-time redirect to `/account/`). Set to false only for emergencies (tools then fall back to the old name behavior).
- **Pages:** `/account/` (login + register, Nothing.tech style, `?return=` bounce-back, origin-whitelisted). Register = `accounts:signUp` + `accounts:update` (displayName); login = `accounts:signInWithPassword`; errors mapped (EMAIL_EXISTS, INVALID_LOGIN_CREDENTIALS, TOO_MANY_ATTEMPTS…). Verified end-to-end 2026-07-10 (register + login + duplicate + wrong-password paths).
- Phone rules (international): strip `[space - . ( )]`; `+…` must match `^\+[1-9]\d{6,14}$`; `998…` (12 digits) → `+`; 9-digit Uzbek local → `+998`; else clear error. Same normalization on login. Canonical E.164 kept in the session and inside the alias email.
- Brute force: Firebase's native TOO_MANY_ATTEMPTS throttling.
- **Deprecated, not deployed-to:** `pangeya-ai-/api/auth/*` (the earlier Supabase/JWT implementation) — code left in the repo for reference; safe to delete. No Vercel env vars are needed for auth.
- **Integration:** `ielts-hub/js/tracker.js` (served to every test page via `test-page-auto.js`) now requires FS Account — the old “enter your name” modal is deleted; results carry `{name, phone, first_name, last_name}` to Apps Script + Firestore. Essay platform (`pangeya-essay-platform-/index-14.html`): name input hidden/auto-filled, FS gate in `<head>`, passcode gate “LIFE KEEPS GOING” untouched. Speaking lab: prompts removed, FS phone is the user id (legacy `pangea8_spk_*` localStorage keys read as fallback). Full-mock: FS gate added in `mock.js`; Google popup kept because the coin wallet is keyed by Firebase UID — records now also carry `fsPhone`.
- **Forgot password v1:** links to https://t.me/mrbmp13. SMS OTP reset = future task.

## Pending manual steps

1. **Firebase console** (the one real remaining step): add `flarestamina.com` to **Authentication → Settings → Authorized domains** in projects **`ieltshub-e2aa8`** (fixes the legacy `signin.html` error + full-mock Google popup), **`pangeya-essay`**, and **`flarestamina`** (40-day app Google sign-in). FS Account itself does NOT need this — it already works.
2. **GitHub Pages**: enforce HTTPS on MAIN and `pangea8-redirect` once certs are issued; Cloudflare SSL mode Full.
3. ~~Telegram channel rename~~ — DONE 2026-07-11: channel is **t.me/flarestamina**; all footer CTAs, the landing link, the hub footer and both PDF footers now point at it.
4. **Apps Script (ielts-hub/apps-script/Code.gs)**: results now include `phone`, `first_name`, `last_name` — extend the sheet mapping if you want those columns.
5. Publish `announcements/telegram-post.md` (draft, Uzbek) to the channel when ready.

## 40-Day Challenge (incident 2026-07-10, resolved)

The old app URLs (`flarestamina.com/challenge/`, `/teacher/`) 404'd after the domain cutover. Fixed the same day: the app serves fully at **`flarestamina.com/flarestamina/challenge/`** (+`/teacher/`), redirect stubs on MAIN keep every old bookmark working, internal absolute paths in the app were made relative, and the challenge is listed on the hub as a Tools card. Student data was never at risk — it lives in Firestore (project `flarestamina`).

## Known intentional `pangea8` leftovers

- Repo-name **path segments** (repos not renamed to keep Pages URLs alive): `/pangea8-landing/`, `/pangea8-donate/`, `/pangea8-speaking/`, `/pangea8-nothing/`, `/support-pangea8/`, `pangea8-redirect`.
- ~~`t.me/pangea8` channel links~~ — resolved: channel renamed to `t.me/flarestamina`, all links updated 2026-07-11.
- `mp` build-log/changelog history (historic posts + RSS + `updates.json` fallback) — changelog exception.
- CORS transition entries (`pangea8.com`) in `api/auth/_utils.js` and the account-page return whitelist — remove after transition.
- Legacy localStorage keys `pangea8_spk_*` (Speaking) read as migration fallback.

## Future tasks

- SMS OTP password reset (replaces Telegram-admin flow).
- Full-mock wallet migration: map Firebase UID ↔ FS phone so Google popup can eventually go.
- Repo rename candidates (do only with redirects in place): `pangea8-speaking` → `flarestamina-speaking`, `pangea8-donate` → `flarestamina-donate`, `pangeya-essay-platform-` → `flarestamina-essay`, `pangeya-ai-` → `flarestamina-ai`; also retire `pangea8-landing` / `pangea8-nothing` / `support-pangea8` (archived/dupes).
- Rebrand legacy Google `signin.html` (still functional, rebranded strings) or fold it into `/account/`.
- Old sessions on pangea8.com localStorage don’t transfer (different origin) — students sign in once on the new domain.


## Features shipped 2026-07-11 (post-rebrand wave 2)

- **Cross-device results**: `ielts-hub/results.html` rebuilt in the terminal style — merges device history (`p8_results`) with Firestore `results` queried by the FS phone (REST runQuery, reads are currently public in rules; tightening = future task: add `allow read: if request.auth.token.email == resource.data.owner` after writing an owner alias field). Tiles: total / week / streak / best, 30-day CSS chart, merged history.
- **Share loop**: tracker.js shows a "Share your result" Telegram share toast after every saved result.
- **Analytics**: GoatCounter (`flarestamina.goatcounter.com`) injected on MAIN, hub, results, account, teachers, every test page (via test-page-auto.js) and full-mock (mock.js). OWNER TODO: register the code `flarestamina` at goatcounter.com (free) — until then hits are dropped silently.
- **Teachers funnel**: `flarestamina.com/teachers/` pitch page + hub footer link.
- **Hub**: START HERE strip for students with no history (points at Cambridge 21); fluid 1–4 column grid; category-aware search; canonical + JSON-LD.
- **Account**: signed-in visit without `?return=` now shows a profile card (name, phone, My results, Log out).
- OWNER TODO (optional): `info@flarestamina.com` via Cloudflare Email Routing; Google Search Console property + sitemap submit + request indexing (site-side SEO already done).

## Security & data hardening 2026-07-11

- `results.html` now reads Firestore with a Bearer idToken (`FSAuth.getFreshToken()` refreshes via securetoken API). Ready for owner-only rules.
- **OWNER TODO — Firestore rules (project ieltshub-e2aa8):** replace ONLY the read permission of `results` and `students` (keep `create`/`write` lines untouched — anon writes power the tracker):
  `allow read: if request.auth != null && resource.data.phone == "+" + request.auth.token.email.split("@")[0];`
  Audit findings: `results` + `students` currently world-readable; `wallets` / `coinRequests` / `history` closed ✓; `essays` (pangeya-essay) public by product design.
- Apps Script `Code.gs` (repo copy) now writes a Phone column (auto-migrates 4-column sheets). OWNER TODO: paste into script.google.com and Deploy → Manage deployments → Edit → New version.
- Analytics events: `event/result-saved` (tracker), `event/fs-signup` (account) — visible in GoatCounter.
- pangea8.com HTTPS enforced ✓; PWA manifests brand-black ✓; `/privacy/` page + footer links ✓; vanity URLs `/writing/ /speaking/ /mock/` ✓.

## CRITICAL SEO fix 2026-07-14 — crawler bypass in the auth gate

**Symptom:** Search Console refused to index `/ielts-hub/` ("blocked by noindex tag"), even though the hub HTML has no noindex.
**Cause:** `ENFORCE=true` + `FSAuth.require()` redirects any session-less visitor (including Googlebot's renderer) to `/account/`, which IS `noindex`. So every tool page effectively inherited noindex → the whole site was becoming unindexable.
**Fix:** `fs-auth.js` `require()` now calls `isBot()` (UA regex: google/bing/yandex/… + social preview bots) and skips the redirect for crawlers — they render the real public catalog; humans still hit the login gate. Not cloaking (catalog is public content). 
**Search Console done 2026-07-14:** property `https://flarestamina.com/` verified (HTML file `google126cc832a594e771.html` at root — do not delete), sitemap.xml submitted (107 URLs; external pierics.com URL removed + workflow now filters non-flarestamina URLs), re-indexing requested for `/` and `/ielts-hub/`.
**If you ever add a new gated tool:** make sure its page has no hard `noindex` and relies on this JS gate, or bots won't index it.

## SEO + security wave (2026-07-15, wave 4)

- **Every article now has a real page.** `.github/scripts/build_community.py` (run by `.github/workflows/community.yml`, every 3h + manual dispatch) reads Firestore `articles` and writes `news/a/<slug>/index.html` (full SEO, Article JSON-LD, EN/UZ toggle baked in), `news/t/<author>/index.html` (author profile), `news/og/<slug>.png` (unique link preview, Pillow + `assets/fonts/JetBrainsMono-*.ttf`) and `news/articles-index.json`. `community.js` reads that index and links cards straight to the generated page; the modal is only the fallback for articles published since the last run. `sitemap.yml` adds every article + author URL.
  - **Verified:** Googlebot fetched `/news/a/<slug>/` and got the full body (before: 0 matches on `/news/`).
  - **Gotcha:** the card is an `<a>`, so the author link inside it renders as a `<span>` — nested anchors make the browser split the DOM and duplicate cards.
- **`firestore.rules` (repo root) — WRITTEN BUT NOT PUBLISHED.** Anyone with the public key can still update/delete any doc (proven: anonymous PATCH 200, DELETE 200). Paste it at https://console.firebase.google.com/project/pangeya-essay/firestore/rules. The console could not be automated (long-poll SPA never reaches document_idle; only javascript_tool responds and the UI never rendered).
  - Rules model: anyone may **create** (no sign-up to publish, by design) with shape validation; **update/delete only for the owner** via Google idToken email check; public may only bump `likes`; `essays` untouched; everything else closed.
  - `/admin` already signs in with Google (Firebase compat SDK, project pangeya-essay) and sends `Authorization: Bearer <idToken>` on PATCH/DELETE. **Needs in the console:** Authentication → enable **Google** provider, and add **flarestamina.com** to Authorized domains.
- **Telegram alert on new articles**: wired in `community.yml`, skipped until repo secrets `TELEGRAM_BOT_TOKEN` (@BotFather) and `TELEGRAM_CHAT_ID` are set.
