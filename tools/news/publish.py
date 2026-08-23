#!/usr/bin/env python3
"""Publish a news post from a JSON spec, wiring up every place it has to appear.

Adding a post by hand meant editing five files in the right order (the article,
posts.json, the index card, feed.xml, the cover) and it was easy to miss one.
This takes one spec file and does all five.

    python3 tools/news/publish.py drafts/my-post.json

Spec keys:
    slug, title, description, date (YYYY-MM-DD), category, lang ("uz"|"en"),
    read (e.g. "4 min"), body (HTML for inside .prose), sources [{name,url}],
    summary (card text), cta {title, sub, href, btn}
"""
import json, os, re, sys, html, datetime
sys.path.insert(0, os.path.dirname(__file__))
from cover import draw_cover

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
NEWS = os.path.join(ROOT, 'news')
SKELETON = os.path.join(NEWS, 'ielts-fee-uzbekistan-2026', 'index.html')
CHIP = {'exam-update': 'chip', 'deadline': 'chip deadline', 'fees': 'chip fees',
        'site-update': 'chip', 'guide': 'chip'}
CAT_LABEL = {'exam-update': 'exam update', 'deadline': 'deadline', 'fees': 'fees',
             'site-update': 'site update', 'guide': 'guide'}
CAT_UZ = {'exam-update': 'imtihon', 'deadline': 'muddat', 'fees': 'narxlar',
          'site-update': 'yangilanish', 'guide': 'qo’llanma'}
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def pretty(d):
    y, m, dd = (int(x) for x in d.split('-'))
    return '%d %s %d' % (dd, MONTHS[m-1], y)

def build_article(spec):
    s = open(SKELETON, encoding='utf-8').read()
    slug, title, desc = spec['slug'], spec['title'], spec['description']
    date, cat, lang = spec['date'], spec['category'], spec.get('lang', 'uz')
    url = 'https://flarestamina.com/news/%s/' % slug
    cover = url + 'cover.png'
    et, ed = html.escape(title, quote=True), html.escape(desc, quote=True)
    jt, jd = json.dumps(title)[1:-1], json.dumps(desc)[1:-1]

    s = re.sub(r'<html lang="[^"]*">', '<html lang="%s">' % lang, s, count=1)
    s = re.sub(r'<title>.*?</title>', lambda m: '<title>%s | Flarestamina</title>' % et, s, count=1, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1)+ed+m.group(2), s, count=1)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1)+url+m.group(2), s, count=1)
    for prop, val in (('og:title', et), ('og:description', ed), ('og:url', url), ('og:image', cover)):
        s = re.sub(r'(<meta property="%s" content=")[^"]*(")' % re.escape(prop),
                   lambda m, v=val: m.group(1)+v+m.group(2), s, count=1)
    for name, val in (('twitter:title', et), ('twitter:image', cover)):
        s = re.sub(r'(<meta name="%s" content=")[^"]*(")' % re.escape(name),
                   lambda m, v=val: m.group(1)+v+m.group(2), s, count=1)
    s = re.sub(r'(<meta property="article:published_time" content=")[^"]*(")',
               lambda m: m.group(1)+date+m.group(2), s, count=1)
    s = re.sub(r'(<meta property="article:section" content=")[^"]*(")',
               lambda m: m.group(1)+CAT_LABEL.get(cat, cat)+m.group(2), s, count=1)

    # JSON-LD
    s = re.sub(r'("headline"\s*:\s*")[^"]*(")', lambda m: m.group(1)+jt+m.group(2), s, count=1)
    s = re.sub(r'("description"\s*:\s*")[^"]*(")', lambda m: m.group(1)+jd+m.group(2), s, count=1)
    s = re.sub(r'("datePublished"\s*:\s*")[^"]*(")', lambda m: m.group(1)+date+m.group(2), s, count=1)
    s = re.sub(r'("dateModified"\s*:\s*")[^"]*(")', lambda m: m.group(1)+date+m.group(2), s, count=1)
    s = re.sub(r'("inLanguage"\s*:\s*")[^"]*(")', lambda m: m.group(1)+lang+m.group(2), s, count=1)
    s = re.sub(r'https://flarestamina\.com/news/ielts-fee-uzbekistan-2026/', url, s)
    src0 = spec['sources'][0]['url'] if spec.get('sources') else 'https://flarestamina.com/'
    s = re.sub(r'("isBasedOn"\s*:\s*")[^"]*(")', lambda m: m.group(1)+src0+m.group(2), s, count=1)
    s = re.sub(r'("citation"\s*:\s*")[^"]*(")', lambda m: m.group(1)+src0+m.group(2), s, count=1)
    s = re.sub(r'("image"\s*:\s*")[^"]*(")', lambda m: m.group(1)+cover+m.group(2), s, count=1)
    s = re.sub(r'(\{ "@type": "ListItem", "position": 3, "name": ")[^"]*(")',
               lambda m: m.group(1)+jt[:60]+m.group(2), s, count=1)

    # visible article
    s = re.sub(r'<h1>.*?</h1>', '<h1>%s</h1>' % html.escape(title), s, count=1, flags=re.S)
    s = re.sub(r'<span class="chip[^"]*">[^<]*</span>',
               '<span class="%s">%s</span>' % (CHIP.get(cat, 'chip'), CAT_LABEL.get(cat, cat)), s, count=1)
    s = re.sub(r'<time datetime="[^"]*">[^<]*</time>',
               '<time datetime="%s">%s</time>' % (date, pretty(date)), s, count=1)
    s = re.sub(r'<img class="post-cover"[^>]*>',
               '<img class="post-cover" src="/news/%s/cover.png" alt="%s" width="1200" height="630" decoding="async">' % (slug, et),
               s, count=1)

    srcs = ' · '.join('<a href="%s" rel="noopener nofollow">%s</a>' % (x['url'], html.escape(x['name']))
                      for x in spec.get('sources', []))
    cta = spec.get('cta', {})
    body = ('%s\n\n    <p class="source">Manba: %s</p>\n\n'
            '    <a class="cta-card" href="%s"><span><span class="t">%s</span>'
            '<span class="s">%s</span></span><span class="btn solid">%s</span></a>\n\n'
            '    <div class="post-nav"><a class="chip" href="/news/">← Barcha IELTS yangiliklari</a></div>\n  ') % (
        spec['body'].rstrip(), srcs,
        cta.get('href', '/ielts-hub/'), html.escape(cta.get('title', 'Bepul mock test bilan bandingizni o‘lchang')),
        html.escape(cta.get('sub', 'Real imtihon formatida, natija darrov')), html.escape(cta.get('btn', 'Mashqni boshlash')))
    i = s.index('<div class="prose">') + len('<div class="prose">')
    j = s.index('</div>\n</article>') if '</div>\n</article>' in s else s.index('</article>')
    j = s.rindex('</div>', i, j)
    s = s[:i] + '\n    ' + body + s[j:]
    return s

def publish(spec):
    slug = spec['slug']
    d = os.path.join(NEWS, slug)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(build_article(spec))
    draw_cover(spec['title'], CAT_UZ.get(spec['category'], spec['category']),
               spec['date'], slug, os.path.join(d, 'cover.png'))

    # posts.json
    pj = os.path.join(NEWS, 'posts.json')
    data = json.load(open(pj, encoding='utf-8'))
    data['posts'] = [p for p in data['posts'] if p['slug'] != slug]
    data['posts'].insert(0, {'slug': slug, 'title': spec['title'], 'date': spec['date'],
                             'category': spec['category'], 'summary': spec['summary'],
                             'source': spec['sources'][0]['name'] if spec.get('sources') else 'flarestamina.com'})
    json.dump(data, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    # index card
    ip = os.path.join(NEWS, 'index.html')
    s = open(ip, encoding='utf-8').read()
    s = re.sub(r'\s*<a class="post-card" href="/news/%s/".*?</a>\n' % re.escape(slug), '\n', s, flags=re.S)
    card = ('  <a class="post-card" href="/news/%s/" data-cat="%s">\n'
            '    <img class="thumb" src="/news/%s/cover.png" alt="%s" width="1200" height="630" loading="lazy" decoding="async">\n'
            '    <div class="meta"><span class="%s">%s</span><time datetime="%s">%s</time>'
            '<span class="dot">·</span><span>%s</span></div>\n'
            '    <h2>%s</h2>\n    <p class="sum">%s</p>\n    <span class="src">%s</span>\n  </a>\n\n') % (
        slug, spec['category'], slug, html.escape(spec['title'], quote=True),
        CHIP.get(spec['category'], 'chip'), CAT_LABEL.get(spec['category'], spec['category']),
        spec['date'], pretty(spec['date']), spec.get('read', '4 min'),
        html.escape(spec['title']), html.escape(spec['summary']),
        html.escape(spec['sources'][0]['name'] if spec.get('sources') else 'flarestamina.com'))
    anchor = '<main class="list wrap">\n'
    s = s.replace(anchor, anchor + card, 1)
    n = len(json.load(open(pj, encoding='utf-8'))['posts'])
    s = re.sub(r'(<span class="count" id="count">)\d+( posts</span>)', lambda m: m.group(1)+str(n)+m.group(2), s, count=1)
    open(ip, 'w', encoding='utf-8').write(s)

    # feed.xml
    fp = os.path.join(NEWS, 'feed.xml')
    f = open(fp, encoding='utf-8').read()
    url = 'https://flarestamina.com/news/%s/' % slug
    f = re.sub(r'\s*<item>(?:(?!</item>).)*?%s(?:(?!</item>).)*?</item>' % re.escape(url), '', f, flags=re.S)
    pub = datetime.datetime.strptime(spec['date'], '%Y-%m-%d').strftime('%a, %d %b %Y 09:00:00 +0500')
    item = ('\n  <item>\n    <title>%s</title>\n    <link>%s</link>\n    <guid isPermaLink="true">%s</guid>\n'
            '    <pubDate>%s</pubDate>\n    <description>%s</description>\n  </item>') % (
        html.escape(spec['title']), url, url, pub, html.escape(spec['summary']))
    m = re.search(r'<item>', f)
    f = (f[:m.start()].rstrip('\n ') + item + '\n  ' + f[m.start():]) if m else f.replace('</channel>', item + '\n</channel>')
    open(fp, 'w', encoding='utf-8').write(f)
    print('  chiqdi: /news/%s/' % slug)

if __name__ == '__main__':
    for path in sys.argv[1:]:
        publish(json.load(open(path, encoding='utf-8')))
