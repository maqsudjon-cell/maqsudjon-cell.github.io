#!/usr/bin/env python3
"""Give every /news/ post its own cover image and point its tags at it.

Before this, all posts shared /news/og.png, so every share looked identical.
Reads posts.json, draws one cover per slug into /news/<slug>/cover.png, then
rewrites og:image / twitter:image / the JSON-LD image in that post's index.html.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from cover import draw_cover

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
NEWS = os.path.join(ROOT, 'news')
CAT = {'exam-update': 'imtihon', 'deadline': 'muddat', 'fees': 'narxlar',
       'site-update': 'yangilanish', 'guide': 'qo’llanma'}

def main(write=True):
    posts = json.load(open(os.path.join(NEWS, 'posts.json')))['posts']
    done = skipped = 0
    for p in posts:
        slug, d = p['slug'], os.path.join(NEWS, p['slug'])
        idx = os.path.join(d, 'index.html')
        if not os.path.isfile(idx):
            print('  %-42s index.html yo‘q' % slug); skipped += 1; continue
        out = os.path.join(d, 'cover.png')
        draw_cover(p['title'], CAT.get(p.get('category',''), p.get('category','news')),
                   p.get('date',''), slug, out)
        url = 'https://flarestamina.com/news/%s/cover.png' % slug
        s = open(idx, encoding='utf-8').read(); orig = s
        s = re.sub(r'(<meta property="og:image" content=")[^"]*(")', r'\g<1>'+url+r'\g<2>', s)
        s = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")', r'\g<1>'+url+r'\g<2>', s)
        s = re.sub(r'("image"\s*:\s*")https://flarestamina\.com/news/og\.png[^"]*(")', r'\g<1>'+url+r'\g<2>', s)
        if write and s != orig:
            open(idx, 'w', encoding='utf-8').write(s)
        print('  %-42s cover.png + teglar' % slug); done += 1
    print('\ntayyor: %d / o‘tkazildi: %d' % (done, skipped))

if __name__ == '__main__':
    main()
