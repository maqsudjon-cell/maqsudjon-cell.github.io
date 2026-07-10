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

- **Client:** `/assets/fs-auth.js` — `FSAuth.getUser() / getToken() / require() / logout() / save()`. Session: localStorage `fs_session = {token, user}` shared across all `flarestamina.com` paths. Client checks JWT expiry; server verifies on API calls.
- **Pages:** `/account/` (login + register, Nothing.tech style, `?return=` bounce-back, origin-whitelisted).
- **Backend:** repo `pangeya-ai-` (Vercel, `https://pangeya-ai.vercel.app`):
  - `POST /api/auth/register` — `{first_name, last_name, phone, password}` → bcrypt(10) → Supabase `fs_users` → JWT + user.
  - `POST /api/auth/login` — `{phone, password}`, 5 fails / 10 min / phone (per-instance memory), JWT + user.
  - JWT HS256, secret `FS_JWT_SECRET`, expiry 30 d. `password_hash` never returned.
  - Phone rules (international): strip `[space - . ( )]`; `+…` must match `^\+[1-9]\d{6,14}$`; `998…` (12 digits) → `+`; 9-digit Uzbek local → `+998`; else clear error. Same normalization on login. Canonical E.164 stored.
  - CORS allowlist: `flarestamina.com`, `www`, plus `pangea8.com` during transition (remove later).
  - Supabase access via PostgREST with `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` env vars.
- **SQL (run in Supabase console):** see `fs_users` table in the final report / `announcements/` sibling; canonical copy:

```sql
create table fs_users (
  id uuid primary key default gen_random_uuid(),
  first_name text not null,
  last_name text not null,
  phone text unique not null,
  password_hash text not null,
  created_at timestamptz default now()
);
alter table fs_users enable row level security;
```

- **Integration:** `ielts-hub/js/tracker.js` (served to every test page via `test-page-auto.js`) now requires FS Account — the old “enter your name” modal is deleted; results carry `{name, phone, first_name, last_name}` to Apps Script + Firestore. Essay platform (`pangeya-essay-platform-/index-14.html`): name input hidden/auto-filled, FS gate in `<head>`, passcode gate “LIFE KEEPS GOING” untouched. Speaking lab: prompts removed, FS phone is the user id (legacy `pangea8_spk_*` localStorage keys read as fallback). Full-mock: FS gate added in `mock.js`; Google popup kept because the coin wallet is keyed by Firebase UID — records now also carry `fsPhone`.
- **Forgot password v1:** links to https://t.me/mrbmp13. SMS OTP reset = future task.

## Pending manual steps

1. **Vercel** (pangeya-ai- project): add env vars `FS_JWT_SECRET` (long random string), `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (service_role). Redeploy. Optionally add flarestamina.com to any allowed-origin config of the older AI endpoints.
2. **Supabase**: run the `fs_users` SQL above; add `https://flarestamina.com` to Auth → URL configuration / allowed origins (Speaking Lab storage too).
3. **Cloudflare (flarestamina.com)**: apex A/AAAA → GitHub Pages (185.199.108–111.153 / already working), `www` CNAME → `maqsudjon-cell.github.io`; SSL mode Full. Keep pangea8.com DNS pointed at GitHub Pages for the redirect repo.
4. **GitHub Pages**: enforce HTTPS on MAIN and `pangea8-redirect` once certs are issued.
5. **Firebase console**: add `flarestamina.com` to Authorized domains for the projects behind ielts-hub tracker (`pangea8`/hub project), full-mock, essay (`pangeya-essay`), and the 40-day app; re-check Firestore rules if domain-scoped.
6. **Telegram**: the channel handle `t.me/pangea8` is still linked from footers — rename/create the channel and tell me; I’ll update the links (listed as documented leftovers).
7. **Apps Script (ielts-hub/apps-script/Code.gs)**: results now include `phone`, `first_name`, `last_name` — extend the sheet mapping if you want those columns.
8. Publish `announcements/telegram-post.md` (draft, Uzbek) to the channel when ready.

## Known intentional `pangea8` leftovers

- Repo-name **path segments** (repos not renamed to keep Pages URLs alive): `/pangea8-landing/`, `/pangea8-donate/`, `/pangea8-speaking/`, `/pangea8-nothing/`, `/support-pangea8/`, `pangea8-redirect`.
- `t.me/pangea8` channel links (manual rename — see above).
- `mp` build-log/changelog history (historic posts + RSS + `updates.json` fallback) — changelog exception.
- CORS transition entries (`pangea8.com`) in `api/auth/_utils.js` and the account-page return whitelist — remove after transition.
- Legacy localStorage keys `pangea8_spk_*` (Speaking) read as migration fallback.

## Future tasks

- SMS OTP password reset (replaces Telegram-admin flow).
- Full-mock wallet migration: map Firebase UID ↔ FS phone so Google popup can eventually go.
- Repo rename candidates (do only with redirects in place): `pangea8-speaking` → `flarestamina-speaking`, `pangea8-donate` → `flarestamina-donate`, `pangeya-essay-platform-` → `flarestamina-essay`, `pangeya-ai-` → `flarestamina-ai`; also retire `pangea8-landing` / `pangea8-nothing` / `support-pangea8` (archived/dupes).
- Rebrand legacy Google `signin.html` (still functional, rebranded strings) or fold it into `/account/`.
- Old sessions on pangea8.com localStorage don’t transfer (different origin) — students sign in once on the new domain.
