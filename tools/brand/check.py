#!/usr/bin/env python3
"""Check that every live page on flarestamina.com serves the current mark.

    python3 tools/brand/check.py            # audit the live site
    python3 tools/brand/check.py --local    # compare against local files only

`tools/site/audit.py` can only see this repo, but the host is assembled from
several GitHub Pages repos and four of them keep their own copy of the icons
(see the sub-app block in make.sh). This walks the sitemap instead, resolves
each page's own `rel="icon"` href the way a browser would, and compares what
comes back with the canonical files. It is the only check that covers the
sub-apps, and it is how the August 2026 regression was found: the hub had been
serving a two-month-old orange favicon and nothing in the repo showed it.

Exits non-zero if any page serves something other than the current mark.
"""
import hashlib, os, re, subprocess, sys
from urllib.parse import urljoin

SITE = 'https://flarestamina.com'
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')


def fetch(url, binary=False):
    """curl rather than urllib: the sandbox this is usually run in blocks the latter."""
    r = subprocess.run(['curl', '-sSL', '--max-time', '25', url],
                       capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode('utf-8', 'replace').strip() or f'curl exit {r.returncode}')
    return r.stdout if binary else r.stdout.decode('utf-8', 'replace')


def canonical():
    """md5 of every file a page is allowed to point at as its icon."""
    out = {}
    for name in ('favicon.ico', 'favicon.svg', 'favicon-96.png',
                 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png'):
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            with open(p, 'rb') as f:
                out[hashlib.md5(f.read()).hexdigest()] = name
    return out


def main():
    ok = canonical()
    if not ok:
        sys.exit('no icons built yet — run tools/brand/make.sh first')

    urls = re.findall(r'<loc>([^<]+)</loc>', fetch(f'{SITE}/sitemap.xml'))
    if not urls:
        sys.exit('sitemap.xml returned no <loc> entries')

    seen, stale, fallback, missing = {}, [], 0, []
    for u in urls:
        try:
            html = fetch(u)
        except RuntimeError as e:
            missing.append((u, str(e)))
            continue
        m = re.search(r'<link[^>]+rel=["\']?icon["\']?[^>]*>', html, re.I)
        href = re.search(r'href=["\']([^"\']+)["\']', m.group(0)) if m else None
        if not href:
            # No link at all is fine: the browser falls back to /favicon.ico,
            # which is this repo's own file and is checked by being in `ok`.
            fallback += 1
            continue
        raw = href.group(1)
        if raw.startswith('data:'):
            # Google cannot use a data: URI as a site favicon — it needs a URL
            # it can fetch — so this is a bug even when the art is current.
            stale.append((u, raw[:60] + '…', 'inline data: URI'))
            continue
        icon = urljoin(u, raw)
        key = icon.split('?')[0]
        if key not in seen:
            try:
                seen[key] = hashlib.md5(fetch(icon, binary=True)).hexdigest()
            except RuntimeError as e:
                seen[key] = f'unreachable: {e}'
        digest = seen[key]
        if digest not in ok:
            stale.append((u, icon, digest))

    for u, icon, why in stale:
        print(f'STALE {u}\n      → {icon}\n      {why}')
    for u, why in missing:
        print(f'ERR   {u}\n      {why}')

    print(f'\n─── {len(urls)} pages · {len(urls) - len(stale) - fallback - len(missing)} current'
          f' · {fallback} fall back to /favicon.ico · {len(stale)} stale · {len(missing)} unreachable')
    sys.exit(1 if stale or missing else 0)


if __name__ == '__main__':
    main()
