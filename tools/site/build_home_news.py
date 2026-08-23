#!/usr/bin/env python3
"""Inject the three newest /news/ posts into the home page.

Nothing on the home page told a visitor the articles existed — /news/ was one
small word in the nav. This writes a real card row between the markers below,
straight from news/posts.json, so it never goes stale by hand.

    python3 tools/site/build_home_news.py
"""
import json, os, re, html

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
START, END = '<!-- HOME-NEWS:START -->', '<!-- HOME-NEWS:END -->'
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
CAT = {'exam-update': 'exam update', 'deadline': 'deadline', 'fees': 'fees',
       'site-update': 'site update', 'guide': 'guide'}

def pretty(d):
    y, m, dd = (int(x) for x in d.split('-'))
    return '%d %s %d' % (dd, MONTHS[m-1], y)

def cards(posts):
    out = []
    for p in posts:
        cover = '/news/%s/cover.png' % p['slug']
        if not os.path.isfile(os.path.join(ROOT, cover.lstrip('/'))):
            continue
        out.append(
            '      <a class="pcard reveal" href="/news/%s/">\n'
            '        <img src="%s" alt="%s" width="1200" height="630" loading="lazy" decoding="async">\n'
            '        <div class="pcard-b">\n'
            '          <span class="pcard-m">%s · %s</span>\n'
            '          <b>%s</b>\n'
            '          <p>%s</p>\n'
            '        </div>\n      </a>' % (
                p['slug'], cover, html.escape(p['title'], quote=True),
                CAT.get(p.get('category',''), p.get('category','')), pretty(p['date']),
                html.escape(p['title']), html.escape(p['summary'])))
        if len(out) == 3:
            break
    return '\n'.join(out)

def main():
    posts = json.load(open(os.path.join(ROOT, 'news', 'posts.json'), encoding='utf-8'))['posts']
    ip = os.path.join(ROOT, 'index.html')
    s = open(ip, encoding='utf-8').read()
    if START not in s:
        raise SystemExit('markerlar yo‘q — index.html ga qo‘shing')
    block = '%s\n%s\n    %s' % (START, cards(posts), END)
    s = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda m: block, s, flags=re.S)
    open(ip, 'w', encoding='utf-8').write(s)
    print('bosh sahifaga %d ta maqola yozildi' % min(3, len(posts)))

if __name__ == '__main__':
    main()
