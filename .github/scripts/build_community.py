#!/usr/bin/env python3
"""
Turns community content (Firestore) into static, indexable pages.

Generates:
  news/a/<slug>/index.html    one real page per article  -> Google can index it,
                              the author can share their own link
  news/t/<author>/index.html  one page per author (teacher profile)
  news/og/<slug>.png          per-article Open Graph image (unique link preview)
  news/articles-index.json    {firestore id: {slug, author_slug}} — community.js
                              reads it so a card links to the static page once it
                              exists, and falls back to the modal until then.

Source of truth: Firestore project `pangeya-essay`, collection `articles`.
Run: python3 .github/scripts/build_community.py   (from the repo root)
"""

import json, os, re, shutil, subprocess, unicodedata, urllib.parse
from html import escape

KEY = 'AIzaSyBnmbg7CyLki-M1E4rxPevJ741yTykliDA'
FS = 'https://firestore.googleapis.com/v1/projects/pangeya-essay/databases/(default)/documents'
SITE = 'https://flarestamina.com'
ROOT = os.getcwd()
FONT_B = os.path.join(ROOT, 'assets/fonts/JetBrainsMono-Bold.ttf')
FONT_R = os.path.join(ROOT, 'assets/fonts/JetBrainsMono-Regular.ttf')

# ---------------------------------------------------------------- helpers
UZ_MAP = {'‘': "'", '’': "'", 'ʻ': "'", 'ʼ': "'", '“': '"', '”': '"', '–': '-', '—': '-'}


def slugify(s, maxlen=60):
    for a, b in UZ_MAP.items():
        s = s.replace(a, b)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r"[^a-zA-Z0-9]+", '-', s).strip('-').lower()
    s = re.sub(r'-{2,}', '-', s)
    return (s[:maxlen].rstrip('-')) or 'article'


def fv(doc, f):
    v = (doc.get('fields') or {}).get(f)
    if not v:
        return ''
    for k in ('stringValue', 'booleanValue'):
        if k in v:
            return v[k]
    if 'integerValue' in v:
        return int(v['integerValue'])
    return ''


def fetch_articles():
    q = {"structuredQuery": {"from": [{"collectionId": "articles"}],
                             "orderBy": [{"field": {"fieldPath": "date"}, "direction": "DESCENDING"}],
                             "limit": 300}}
    raw = subprocess.run(['curl', '-sS', '-X', 'POST', FS + ':runQuery?key=' + KEY,
                          '-H', 'Content-Type: application/json', '-d', json.dumps(q)],
                         capture_output=True, text=True, timeout=60, check=True).stdout
    rows = json.loads(raw)
    if not isinstance(rows, list):
        raise SystemExit('Firestore error: %s' % raw[:300])
    out = []
    for r in rows:
        d = r.get('document')
        if not d:
            continue
        a = {
            'id': d['name'].split('/')[-1],
            'title': fv(d, 'title'), 'body': fv(d, 'body'),
            'title_uz': fv(d, 'title_uz'), 'body_uz': fv(d, 'body_uz'),
            'lang': fv(d, 'lang') or 'en', 'author': fv(d, 'author') or 'Flarestamina',
            'center': fv(d, 'center'), 'link': fv(d, 'link'),
            'date': (fv(d, 'date') or '')[:10], 'hidden': fv(d, 'hidden') is True,
        }
        if not a['title'] or not a['body'] or a['hidden'] or a['title'].startswith('__'):
            continue
        out.append(a)
    return out


def paras(text):
    return '\n'.join('<p>%s</p>' % escape(p).replace('\n', '<br>')
                     for p in re.split(r'\n{2,}', text.strip()) if p.strip())


def safe_url(u):
    u = (u or '').strip()
    if not u:
        return ''
    if not re.match(r'^https?://', u, re.I):
        u = 'https://' + u
    return u if re.match(r'^https?://[\w.-]+', u) else ''


# ---------------------------------------------------------------- OG images
def og_image(a, path):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    img = Image.new('RGB', (W, H), '#0A0605')
    d = ImageDraw.Draw(img)
    # warm flare glow, top-right
    for i in range(180, 0, -6):
        alpha = int(26 * (i / 180))
        d.ellipse([W - 420 - i, -260 - i, W + 120 + i, 240 + i], fill=(20 + alpha // 3, 8, 4))
    d.rectangle([0, 0, 14, H], fill='#FF5A1F')          # left flare bar
    fb = ImageFont.truetype(FONT_B, 54)
    fr = ImageFont.truetype(FONT_R, 24)
    fs = ImageFont.truetype(FONT_B, 22)

    d.text((70, 62), 'FLARE', font=fs, fill='#FF5A1F')
    d.text((70 + d.textlength('FLARE', font=fs), 62), 'STAMINA', font=fs, fill='#EAF2EE')
    d.text((70, 104), 'ARTICLE', font=ImageFont.truetype(FONT_R, 18), fill='#8FA89E')

    # wrapped title
    title = a['title']
    words, lines, cur = title.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=fb) > W - 150 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    lines = lines[:5]
    y = 190
    for ln in lines:
        d.text((70, y), ln, font=fb, fill='#EAF2EE')
        y += 68

    d.line([(70, H - 130), (W - 70, H - 130)], fill='#2a2320', width=1)
    by = a['author'] + (' · ' + a['center'] if a['center'] else '')
    d.text((70, H - 104), by[:64], font=fr, fill='#FF7A3D')
    d.text((70, H - 66), 'flarestamina.com/news', font=fr, fill='#8FA89E')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, 'PNG', optimize=True)


# ---------------------------------------------------------------- templates
HEAD_COMMON = '''<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="dark light">
<script>(function(){{var t="dark";try{{t=localStorage.getItem("p8-theme")||"dark";}}catch(e){{}}document.documentElement.setAttribute("data-theme",t);}})();function fsTheme(){{var d=document.documentElement,n=d.getAttribute("data-theme")==="light"?"dark":"light";d.setAttribute("data-theme",n);try{{localStorage.setItem("p8-theme",n);}}catch(e){{}}}}</script>
<meta name="theme-color" content="#0A0605">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="Flarestamina IELTS News" href="/news/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/news/news.css">'''

HEADER = '''<header class="site">
  <div class="wrap bar">
    <a class="brand" href="/">
      <svg viewBox="0 0 24 24" fill="none" stroke="#FF5A1F" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M12 9.5V1.5M14.5 12h7M12 14.5V19M9.5 12H4"/></svg>
      <span><span class="fl">FLARE</span>STAMINA</span>
    </a>
    <nav aria-label="Site">
      <a href="/ielts-hub/">practice</a>
      <a href="/news/" aria-current="page">news</a>
      <a href="/founder/">founder</a>
      <button class="theme-btn" onclick="fsTheme()" aria-label="Toggle theme" title="Light / dark">◐</button>
    </nav>
  </div>
</header>'''

FOOTER = '''<footer class="site">
  <div class="wrap row">
    <span>© 2026 <a href="/">Flarestamina</a> · built by <a href="/founder/">Maqsudjon Polatov</a></span>
    <span><a href="https://t.me/flarestamina" rel="noopener">telegram</a> · <a href="/news/feed.xml">rss</a></span>
  </div>
</footer>
<script data-goatcounter="https://flarestamina.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'''


def article_page(a, slug, author_slug):
    url = '%s/news/a/%s/' % (SITE, slug)
    og = '%s/news/og/%s.png' % (SITE, slug)
    both = bool(a['title_uz'] and a['body_uz'])
    desc = re.sub(r'\s+', ' ', a['body'])[:155].strip()
    link = safe_url(a['link'])
    ava = escape(a['author'][:1].upper())

    toggle = ''
    if both:
        toggle = ('<div class="a-lang" id="langbar">'
                  '<button data-l="en" class="on">English</button>'
                  '<button data-l="uz">Oʻzbekcha</button></div>')
    uz_block = ''
    if both:
        uz_block = ('<div class="body" id="body-uz" hidden lang="uz">'
                    '<h1 class="a-alt-h">%s</h1>%s</div>' % (escape(a['title_uz']), paras(a['body_uz'])))

    ld = {
        "@context": "https://schema.org",
        "@graph": [{
            "@type": "Article",
            "@id": url + "#article",
            "headline": a['title'][:110],
            "description": desc,
            "datePublished": a['date'],
            "dateModified": a['date'],
            "inLanguage": "uz" if a['lang'] == 'uz' else "en",
            "mainEntityOfPage": url,
            "image": og,
            "author": {"@type": "Person", "name": a['author'],
                       **({"url": link} if link else {}),
                       **({"worksFor": {"@type": "Organization", "name": a['center']}} if a['center'] else {})},
            "publisher": {"@id": SITE + "/#org"},
            "isPartOf": {"@id": SITE + "/news/#page"},
        }, {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Flarestamina", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "News", "item": SITE + "/news/"},
                {"@type": "ListItem", "position": 3, "name": "Articles", "item": SITE + "/news/#articles"},
                {"@type": "ListItem", "position": 4, "name": a['title'][:70], "item": url},
            ]}]}

    return '''<!DOCTYPE html>
<html lang="{lang}">
<head>
{head}
<title>{title} | Flarestamina</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="author" content="{author}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:site_name" content="Flarestamina">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="article:published_time" content="{date}">
<meta property="article:author" content="{author}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
{header}
<article class="post wrap">
  <p class="crumbs"><a href="/news/">← news</a> / <a href="/news/#articles">articles</a></p>
  {toggle}
  <div class="body" id="body-en">
    <h1 class="a-alt-h">{title}</h1>
  </div>
  <div class="post-meta">
    <span class="chip article">article</span>
    <time datetime="{date}">{date}</time>
  </div>
  <div class="a-author big" style="border:none;padding-top:14px">
    <span class="a-ava">{ava}</span>
    <div><b>{author}</b>{center}</div>
    {authorlink}
  </div>

  <div class="body" id="prose-en">{body}</div>
  {uz_block}

  <p class="source">Written by a member of the Flarestamina community · <a href="/news/t/{author_slug}/">more from {author}</a></p>

  <a class="cta" href="/ielts-hub/">
    <div class="t">Practise what you just read — free <span class="fl">→</span></div>
    <div class="s">100+ IELTS mock tests in real exam format, instant band scores</div>
  </a>

  <div class="a-share" style="margin-top:22px">
    <a href="https://t.me/share/url?url={url_enc}&text={share_enc}" target="_blank" rel="noopener">↗ share on telegram</a>
  </div>

  <p class="more"><a href="/news/#articles">← all articles</a> · <a href="/writearticle/">write your own →</a></p>
</article>
{footer}
<script>
(function(){{
  var bar=document.getElementById('langbar'); if(!bar) return;
  var en=[document.getElementById('body-en'),document.getElementById('prose-en')];
  var uz=document.getElementById('body-uz');
  bar.addEventListener('click',function(e){{
    var b=e.target.closest('button'); if(!b) return;
    var l=b.getAttribute('data-l');
    [].forEach.call(bar.querySelectorAll('button'),function(x){{x.classList.toggle('on',x===b)}});
    en.forEach(function(x){{if(x)x.hidden=(l!=='en')}});
    if(uz) uz.hidden=(l!=='uz');
  }});
}})();
</script>
</body>
</html>
'''.format(lang=('uz' if a['lang'] == 'uz' else 'en'), head=HEAD_COMMON, title=escape(a['title']),
           desc=escape(desc), url=url, og=og, date=a['date'], author=escape(a['author']),
           ld=json.dumps(ld, ensure_ascii=False), header=HEADER, footer=FOOTER, toggle=toggle,
           ava=ava, center=('<i>%s</i>' % escape(a['center'])) if a['center'] else '',
           authorlink=('<a class="a-link" href="%s" target="_blank" rel="noopener nofollow ugc">%s</a>'
                       % (escape(link), escape(link.replace('https://', '').rstrip('/')))) if link else '',
           body=paras(a['body']), uz_block=uz_block, author_slug=author_slug,
           url_enc=urllib.parse.quote(url, safe=''),
           share_enc=urllib.parse.quote('"%s" — %s (Flarestamina)' % (a['title'], a['author']), safe=''))


def author_page(author, center, link, items):
    slug = slugify(author)
    url = '%s/news/t/%s/' % (SITE, slug)
    link = safe_url(link)
    desc = 'IELTS articles by %s%s on Flarestamina — free IELTS practice for students in Uzbekistan.' % (
        author, (' (' + center + ')') if center else '')
    cards = ''
    for it in items:
        cards += ('<a class="post-card" href="/news/a/%s/">'
                  '<div class="meta"><span class="chip article">article</span><time>%s</time></div>'
                  '<h2>%s</h2><p class="sum">%s…</p></a>' % (
                      it['slug'], it['a']['date'], escape(it['a']['title']),
                      escape(re.sub(r'\s+', ' ', it['a']['body'])[:150])))
    ld = {"@context": "https://schema.org", "@type": "ProfilePage",
          "url": url, "name": author,
          "mainEntity": {"@type": "Person", "name": author,
                         **({"url": link} if link else {}),
                         **({"worksFor": {"@type": "Organization", "name": center}} if center else {}),
                         "knowsAbout": ["IELTS", "English language teaching"]}}
    return '''<!DOCTYPE html>
<html lang="en">
<head>
{head}
<title>{author} — IELTS articles | Flarestamina</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:site_name" content="Flarestamina">
<meta property="og:type" content="profile">
<meta property="og:title" content="{author} — IELTS articles">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld}</script>
</head>
<body>
{header}
<section class="hero wrap">
  <p class="crumbs"><a href="/news/">← news</a> / <a href="/news/#articles">articles</a></p>
  <div class="a-author big" style="border:none;padding-top:6px">
    <span class="a-ava" style="width:46px;height:46px;font-size:19px">{ava}</span>
    <div><b style="font-size:20px">{author}</b>{center}</div>
  </div>
  <p class="sub">{n} article{s} on Flarestamina.{linkline}</p>
</section>
<main class="list wrap">{cards}</main>
<div class="wrap">
  <a class="write-cta" href="/writearticle/">
    <div>
      <div class="t">Ustozmisiz? Siz ham maqola yozing 📝</div>
      <div class="s">Your name, socials and centre included · 3 minutes, no sign-up</div>
    </div>
    <span class="btn">Write an article</span>
  </a>
</div>
{footer}
</body>
</html>
'''.format(head=HEAD_COMMON, author=escape(author), desc=escape(desc), url=url, site=SITE,
           ld=json.dumps(ld, ensure_ascii=False), header=HEADER, footer=FOOTER,
           ava=escape(author[:1].upper()),
           center=('<i>%s</i>' % escape(center)) if center else '',
           n=len(items), s='' if len(items) == 1 else 's',
           linkline=(' <a href="%s" target="_blank" rel="noopener nofollow ugc">%s</a>'
                     % (escape(link), escape(link.replace('https://', '').rstrip('/')))) if link else '',
           cards=cards)


# ---------------------------------------------------------------- main
def main():
    # what already had a page last run? anything new gets announced.
    try:
        prev = set(json.load(open(os.path.join(ROOT, 'news/articles-index.json')))['articles'].keys())
    except Exception:
        prev = set()

    arts = fetch_articles()
    print('articles fetched:', len(arts))

    # stable, unique slugs
    seen, entries = {}, []
    for a in arts:
        s = slugify(a['title'])
        if s in seen:
            s = '%s-%s' % (s, a['id'][:5].lower())
        seen[s] = True
        entries.append({'a': a, 'slug': s, 'author_slug': slugify(a['author'])})

    for d in ('news/a', 'news/t', 'news/og'):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)

    index = {}
    for e in entries:
        a, slug = e['a'], e['slug']
        out = os.path.join(ROOT, 'news/a', slug)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(article_page(a, slug, e['author_slug']))
        og_image(a, os.path.join(ROOT, 'news/og', slug + '.png'))
        index[a['id']] = {'slug': slug, 'author_slug': e['author_slug'], 'date': a['date']}
        print('  page + og:', slug)

    # author pages
    by_author = {}
    for e in entries:
        by_author.setdefault(e['author_slug'], []).append(e)
    for aslug, items in by_author.items():
        a0 = items[0]['a']
        out = os.path.join(ROOT, 'news/t', aslug)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(author_page(a0['author'], a0['center'], a0['link'], items))
        print('  author:', aslug, '(%d)' % len(items))

    with open(os.path.join(ROOT, 'news/articles-index.json'), 'w', encoding='utf-8') as f:
        json.dump({'generated': True, 'articles': index, 'authors': sorted(by_author)}, f,
                  ensure_ascii=False, indent=1)
    print('articles-index.json written:', len(index), 'articles,', len(by_author), 'authors')

    # hand the freshly published articles to the workflow so it can notify Telegram
    fresh = [e for e in entries if prev and e['a']['id'] not in prev]
    out = os.environ.get('GITHUB_OUTPUT')
    if out:
        lines = []
        for e in fresh:
            a = e['a']
            lines.append('%s\u2014%s\u2014%s/news/a/%s/' % (a['title'], a['author'], SITE, e['slug']))
        with open(out, 'a', encoding='utf-8') as f:
            f.write('new_count=%d\n' % len(fresh))
            f.write('new_list<<EOF_LIST\n' + '\n'.join(lines) + '\nEOF_LIST\n')
    print('new since last run:', len(fresh))


if __name__ == '__main__':
    main()
