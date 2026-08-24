#!/usr/bin/env python3
"""Cross-link the articles.

Every article was reachable only from the /news/ index — 23 of 35 had exactly
one internal link pointing at them, and none pointed at each other. The topics
run in obvious chains (price -> where to sit it -> One Skill Retake), so the
links were there to be made.

Picks three neighbours per article: same category first, then the nearest by
date, always matching the article's language. Re-run after publishing.
"""
import glob, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NEWS = os.path.join(ROOT, 'news')
UZ_HINT = re.compile(r'[‘’ʻ]|\b(bepul|narxi|qayerda|kerak|yil|uchun|ko|qanday|nechta)\b', re.I)

LABEL = {'uz': 'Shu mavzuda yana', 'en': 'More on this'}


def lang_of(post, page_lang=None):
    if page_lang:
        return page_lang
    return 'uz' if UZ_HINT.search(post['title'] + ' ' + post.get('summary', '')) else 'en'


def block(current, posts, lang):
    same = [p for p in posts if p['slug'] != current['slug']
            and lang_of(p) == lang and p.get('category') == current.get('category')]
    rest = [p for p in posts if p['slug'] != current['slug']
            and lang_of(p) == lang and p not in same]
    same.sort(key=lambda p: p.get('date', ''), reverse=True)
    rest.sort(key=lambda p: p.get('date', ''), reverse=True)
    picks = (same + rest)[:3]
    if len(picks) < 2:
        return ''
    out = ['    <nav class="related" aria-label="%s">' % html.escape(LABEL[lang]),
           '      <h2>%s</h2>' % html.escape(LABEL[lang]), '      <ul>']
    for p in picks:
        out.append('        <li><a href="/news/%s/">%s</a></li>'
                   % (p['slug'], html.escape(p['title'])))
    out += ['      </ul>', '    </nav>']
    return '\n'.join(out)


def main():
    posts = json.load(open(os.path.join(NEWS, 'posts.json'), encoding='utf-8'))['posts']
    by_slug = {p['slug']: p for p in posts}
    n = 0
    for f in sorted(glob.glob(os.path.join(NEWS, '*', 'index.html'))):
        slug = os.path.basename(os.path.dirname(f))
        if slug not in by_slug:
            continue
        s = open(f, encoding='utf-8').read()
        m = re.search(r'<html[^>]+lang="([a-z]{2})"', s)
        b = block(by_slug[slug], posts, m.group(1) if m else 'en')
        if not b:
            continue
        s = re.sub(r'\n\s*<nav class="related".*?</nav>', '', s, flags=re.S)
        anchor = re.search(r'[ \t]*<div class="post-nav">', s)
        if not anchor:
            continue
        s = s[:anchor.start()] + b + '\n\n' + s[anchor.start():]
        open(f, 'w', encoding='utf-8').write(s)
        n += 1
    print('cross-linked %d articles' % n)


if __name__ == '__main__':
    main()
