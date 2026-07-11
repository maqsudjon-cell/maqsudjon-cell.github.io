# HANDOFF — FLARESTAMINA (formerly pangea8)

_Last updated: 2026-07-10 — full rebrand + FS Account rollout executed by Claude Code._

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
