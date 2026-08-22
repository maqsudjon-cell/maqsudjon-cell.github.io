#!/usr/bin/env python3
"""Static audit of every page in the repo.

Checks structure, metadata, accessibility affordances and internal
consistency. Prints one line per finding, grouped by severity, so the
output can be diffed between runs.

    python3 tools/site/audit.py
"""
import glob, json, os, re, sys
from collections import Counter
from html.parser import HTMLParser

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
SITE = 'https://flarestamina.com'


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.mismatch, self.ids, self.headings = [], [], [], []
        self.imgs_no_alt, self.links_no_text, self.btns_no_label = 0, [], 0
        self.inputs_unlabelled, self.labels_for, self.input_ids = [], set(), []
        self._cur, self._buf = None, ''
        self.lang_attr = None
        self.dup_meta = Counter()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang_attr = a.get('lang')
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'img' and not a.get('alt') and a.get('alt') != '':
            self.imgs_no_alt += 1
        if tag == 'input':
            if a.get('type') not in ('hidden',):
                self.input_ids.append((a.get('id'), a.get('aria-label'), a.get('placeholder')))
        if tag == 'label' and a.get('for'):
            self.labels_for.add(a['for'])
        if tag == 'meta':
            k = a.get('name') or a.get('property')
            if k:
                self.dup_meta[k] += 1
        if tag in ('h1','h2','h3','h4','h5','h6'):
            self._cur, self._buf = tag, ''
        if tag == 'a':
            self._link = a
            self._linkbuf = ''
        if tag not in VOID:
            self.stack.append(tag)

    def handle_data(self, d):
        if self._cur:
            self._buf += d
        if hasattr(self, '_linkbuf'):
            self._linkbuf += d

    def handle_endtag(self, tag):
        if tag == self._cur:
            self.headings.append((tag, ' '.join(self._buf.split())[:70]))
            self._cur = None
        if tag == 'a' and hasattr(self, '_link'):
            txt = ' '.join(self._linkbuf.split())
            if not txt and not self._link.get('aria-label') and 'href' in self._link:
                self.links_no_text.append(self._link.get('href'))
            del self._link, self._linkbuf
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.mismatch.append(tag)
        else:
            self.stack.pop()


def meta(s, key):
    m = (re.search(r'<meta\s+name="%s"\s+content="([^"]*)"' % key, s)
         or re.search(r'<meta\s+property="%s"\s+content="([^"]*)"' % key, s))
    return m.group(1) if m else None


def audit(path):
    s = open(path, encoding='utf-8').read()
    out = []
    redirect = 'location.replace' in s and len(s) < 4000
    d = Doc(); d.feed(s)

    def add(sev, msg): out.append((sev, msg))

    if d.mismatch or d.stack:
        add('ERR', f'tag mismatch {d.mismatch[:3]} unclosed {d.stack[:3]}')
    dup = [i for i, n in Counter(d.ids).items() if n > 1]
    if dup:
        add('ERR', f'duplicate id: {dup}')
    for k, n in d.dup_meta.items():
        if n > 1 and k not in ('og:image:width', 'og:image:height'):
            add('WARN', f'duplicate meta "{k}" x{n}')

    if redirect:
        return out

    title = re.search(r'<title>(.*?)</title>', s, re.S)
    title = ' '.join(title.group(1).split()) if title else None
    if not title:
        add('ERR', 'no <title>')
    elif len(title) > 65:
        add('WARN', f'title {len(title)} chars (>65 truncates in search): {title[:60]}…')
    desc = meta(s, 'description')
    if not desc:
        add('ERR', 'no meta description')
    elif not (50 <= len(desc) <= 165):
        add('WARN', f'description {len(desc)} chars (aim 50–165)')

    if not re.search(r'<link rel="canonical"', s):
        add('WARN', 'no canonical')
    if 'noindex' not in (meta(s, 'robots') or ''):
        for k in ('og:title', 'og:image', 'og:url'):
            if not meta(s, k):
                add('WARN', f'no {k}')

    h1 = [h for h in d.headings if h[0] == 'h1']
    if len(h1) == 0:
        add('ERR', 'no h1')
    elif len(h1) > 1:
        add('WARN', f'{len(h1)} h1 elements')
    lvls = [int(t[1]) for t, _ in d.headings]
    for i in range(1, len(lvls)):
        if lvls[i] - lvls[i - 1] > 1:
            add('WARN', f'heading jumps h{lvls[i-1]}→h{lvls[i]}')
            break

    for l in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            json.loads(l)
        except Exception as e:
            add('ERR', f'invalid JSON-LD: {e}')

    if d.imgs_no_alt:
        add('WARN', f'{d.imgs_no_alt} img without alt')
    if d.links_no_text:
        add('WARN', f'{len(d.links_no_text)} link(s) with no text/aria-label: {d.links_no_text[:2]}')
    for iid, aria, ph in d.input_ids:
        if not aria and (not iid or iid not in d.labels_for):
            if not re.search(r'<label[^>]*>\s*<span[^>]*>[^<]+</span>\s*<input[^>]*id="%s"' % re.escape(iid or ''), s):
                add('INFO', f'input id={iid!r} may lack a programmatic label')
    if not d.lang_attr:
        add('WARN', 'no <html lang>')

    if 'paper.css' not in s and 'fs-paper-theme' not in s:
        add('ERR', 'not on the paper design')
    if re.search(r'href="[^"]*\.(?:css|js)"(?![^>]*\?)', s):
        pass
    return out


def main():
    files = sorted(set(glob.glob('*.html') + glob.glob('*/index.html')
                       + glob.glob('*/*/index.html') + glob.glob('*/*/*/index.html')))
    # Not Flarestamina pages: a Search Console token file, and two separate
    # products that happen to be hosted on the same domain with their own brands.
    SKIP = ('google', 'chzq/', 'wedding/')
    files = [f for f in files
             if 'node_modules' not in f and not any(f.startswith(x) or x in f for x in SKIP)]
    tot = Counter()
    for f in files:
        rows = audit(f)
        if rows:
            print(f'\n{f}')
            for sev, msg in rows:
                print(f'  {sev:5} {msg}')
                tot[sev] += 1
    print(f'\n─── {len(files)} pages · ' + ' · '.join(f'{k} {v}' for k, v in sorted(tot.items())) or 'clean')


if __name__ == '__main__':
    main()
