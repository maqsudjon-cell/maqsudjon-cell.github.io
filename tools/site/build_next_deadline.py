#!/usr/bin/env python3
"""Copy the next few upcoming deadlines into the news page's info card.

/deadlines/ holds the list as a `var D=[...]` literal. Rather than duplicate
it, this reads that array, keeps the next five that have not
passed, and writes them into /news/index.html between the markers. The page
picks the first future one and counts the days itself, so the card keeps
working for months without a rebuild.

    python3 tools/site/build_next_deadline.py
"""
import datetime, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
START, END = '<!-- NEXT-DEADLINE:START -->', '<!-- NEXT-DEADLINE:END -->'

def parse():
    s = open(os.path.join(ROOT, 'deadlines', 'index.html'), encoding='utf-8').read()
    i = s.index('var D=[')
    body = s[i + len('var D='):]
    body = body[:body.index('\n];') + 2]
    out = []
    for m in re.finditer(r'\{[^{}]*\}', body):
        row = m.group(0)
        n = re.search(r'n\s*:\s*"([^"]*)"', row)
        d = re.search(r'date\s*:\s*"([^"]*)"', row)
        if n and d:
            out.append({'name': n.group(1), 'date': d.group(1)})
    return out

def short(name):
    """The card is one line — keep the recognisable part of the name."""
    name = re.split(r'\s+[—-]\s+', name)[0]
    name = re.sub(r'\s*\(.*?\)\s*', ' ', name).strip()
    return name[:28].strip()

def main():
    today = datetime.date.today().isoformat()
    rows = [r for r in parse() if r['date'] >= today]
    rows.sort(key=lambda r: r['date'])
    if not rows:
        print('kelayotgan muddat yo‘q'); return
    nxt = [{'name': short(r['name']), 'date': r['date']} for r in rows[:5]]
    p = os.path.join(ROOT, 'news', 'index.html')
    s = open(p, encoding='utf-8').read()
    block = '%s\n<script>window.FS_NEXT_DEADLINES = %s;</script>\n%s' % (
        START, json.dumps(nxt, ensure_ascii=False), END)
    if START in s:
        s = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda m: block, s, flags=re.S)
    else:
        s = s.replace('<script src="/assets/fs-auth.js"></script>', block + '\n<script src="/assets/fs-auth.js"></script>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('yozildi: %d ta muddat, birinchisi %s — %s' % (len(nxt), nxt[0]['name'], nxt[0]['date']))

if __name__ == '__main__':
    main()
