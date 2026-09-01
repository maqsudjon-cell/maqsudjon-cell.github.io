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
FONT_SANS = os.path.join(ROOT, 'assets/fonts/Inter-Variable.ttf')
FONT_MONO = os.path.join(ROOT, 'assets/fonts/IBMPlexMono-Regular.ttf')


def inter(size, weight='Medium'):
    """Inter at a named weight — the variable file carries every instance."""
    from PIL import ImageFont
    f = ImageFont.truetype(FONT_SANS, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f

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
    """Paper-design card: white ground, the spark, a mono kicker, the title in
    Inter and the gradient rail. Mirrors tools/brand/og.html, which draws the
    site's own cards — keep the two in step."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    FG, MUTED, SUBTLE = '#0a0a0a', '#5c5c5c', '#8a8a8a'
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)

    # four-point spark, same path proportions as favicon.svg, drawn at 56px
    cx, cy, s_ = 72 + 28, 64 + 28, 28
    waist = s_ * 0.153           # 2.45 out of the mark's 16-unit radius
    d.polygon([(cx, cy - s_), (cx + waist, cy - waist), (cx + s_, cy), (cx + waist, cy + waist),
               (cx, cy + s_), (cx - waist, cy + waist), (cx - s_, cy), (cx - waist, cy - waist)], fill=FG)

    fk = ImageFont.truetype(FONT_MONO, 16)
    d.text((72, 196), 'A R T I C L E', font=fk, fill=SUBTLE)

    # wrapped title, stepping the size down the way the HTML card does
    title = a['title']
    size = 64 if len(title) <= 34 else (52 if len(title) <= 52 else 44)
    ft = inter(size, 'Medium')
    words, lines, cur = title.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=ft) > W - 200 and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    lines = lines[:4]
    y = 232
    for ln in lines:
        d.text((72, y), ln, font=ft, fill=FG)
        y += int(size * 1.16)

    # gradient rail: teal -> sky -> indigo -> fuchsia
    stops = [(0.0, (45, 212, 191)), (0.32, (56, 189, 248)), (0.64, (129, 140, 248)), (1.0, (232, 121, 249))]
    rail_y, rail_w = min(y + 22, H - 150), 280
    for i in range(rail_w):
        t = i / (rail_w - 1)
        for j in range(len(stops) - 1):
            a0, c0 = stops[j]; a1, c1 = stops[j + 1]
            if a0 <= t <= a1:
                k = (t - a0) / (a1 - a0)
                col = tuple(int(c0[n] + (c1[n] - c0[n]) * k) for n in range(3))
                break
        d.rectangle([72 + i, rail_y, 72 + i, rail_y + 3], fill=col)

    fr = inter(20, 'Regular')
    by = a['author'] + (' · ' + a['center'] if a['center'] else '')
    d.text((72, H - 78), by[:64], font=fr, fill=MUTED)
    url = 'flarestamina.com/news'
    d.text((W - 72 - d.textlength(url, font=inter(20, 'Medium')), H - 78), url,
           font=inter(20, 'Medium'), fill=FG)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, 'PNG', optimize=True)


# ---------------------------------------------------------------- templates
HEAD_COMMON = '''<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#ffffff">
<script>
(function () {{
  document.documentElement.classList.add('js');
  try {{
    var t = localStorage.getItem('fs-paper-theme') || localStorage.getItem('theme') || localStorage.getItem('p8-theme');
    if (t === 'dark') {{ document.documentElement.classList.add('dark'); document.documentElement.dataset.theme = 'dark'; }}
    else {{ document.documentElement.dataset.theme = 'light'; }}
  }} catch (e) {{ document.documentElement.dataset.theme = 'light'; }}
}})();
</script>
<link rel="icon" href="/favicon.ico?v=2" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/favicon.svg?v=2">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png?v=2">
<link rel="alternate" type="application/rss+xml" title="Flarestamina IELTS News" href="/news/feed.xml">
<link rel="preload" href="/assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/plex-mono-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/paper.css?v=1">
<link rel="stylesheet" href="/news/news.css?v=3">'''

HEADER = '''<a class="skip" href="#content" data-i18n="skip">Skip to content</a>

<header class="hdr">
  <div class="hdr-in">
    <a class="brand" href="/" aria-label="Flarestamina"><svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16 1.4 L17.85 13.55 L30.6 16 L17.85 18.45 L16 30.6 L14.15 18.45 L1.4 16 L14.15 13.55 Z"/></svg>Flarestamina</a>
    <nav class="hdr-nav" aria-label="Primary">
      <a href="/ielts-hub/" data-i18n="navPractice">Practice</a>
      <a href="/#tools" data-i18n="navTools">Tools</a>
      <a href="/news/" aria-current="page" data-i18n="navNews">News</a>
    </nav>
    <span class="hdr-sp"></span>
    <div class="lang" role="group" aria-label="Language">
      <button type="button" data-lang="en" class="on">EN</button>
      <button type="button" data-lang="uz">UZ</button>
    </div>
    <button class="icon-btn" id="tgl" aria-label="Theme"><svg id="ico-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg><svg id="ico-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="display:none"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>
    <div class="hdr-desk">
      <a class="btn ghost" id="acct" href="/account/?return=https%3A%2F%2Fflarestamina.com%2Fielts-hub%2F" data-i18n="signin">Sign in</a>
      <a class="btn solid" href="/ielts-hub/" data-i18n="startFree">Start free</a>
    </div>
    <button class="icon-btn burger" id="burger" aria-label="Menu" aria-expanded="false" aria-controls="sheet">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
</header>

<div class="sheet" id="sheet">
  <a href="/ielts-hub/" data-i18n="navPractice">Practice</a>
      <a href="/#tools" data-i18n="navTools">Tools</a>
      <a href="/news/" aria-current="page" data-i18n="navNews">News</a>
  <div class="row">
    <a class="btn ghost" href="/account/?return=https%3A%2F%2Fflarestamina.com%2Fielts-hub%2F" data-i18n="signin">Sign in</a>
    <a class="btn solid" href="/ielts-hub/" data-i18n="startFree">Start free</a>
  </div>
</div>

<main id="content">'''

FOOTER = '''</main>

<footer class="ftr">
  <div class="wrap">
    <div class="f-grid">
      <div class="f-brand">
        <span class="brand"><svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16 1.4 L17.85 13.55 L30.6 16 L17.85 18.45 L16 30.6 L14.15 18.45 L1.4 16 L14.15 13.55 Z"/></svg>Flarestamina</span>
        <p data-i18n="footBlurb">Free IELTS Academic practice. Built in Tashkent.</p>
      </div>
      <div class="f-col">
        <p data-i18n="footPractice">Practice</p>
        <a href="/ielts-hub/" data-i18n="tHub">Practice Hub</a>
        <a href="/tests/" data-i18n="tAll">All tests</a>
        <a href="/ielts-hub/?cat=Listening">Listening</a>
        <a href="/ielts-hub/?cat=Reading">Reading</a>
        <a href="/writing/" data-i18n="tWrite">Writing Lab</a>
        <a href="/pangea8-speaking/" data-i18n="tSpeak">Speaking Lab</a>
      </div>
      <div class="f-col">
        <p data-i18n="footTools">Tools</p>
        <a href="/convert/" data-i18n="tConvert">Score Converter</a>
        <a href="/deadlines/" data-i18n="tDeadlines">Deadlines</a>
        <a href="/plan/" data-i18n="tPlan">Study Plan</a>
        <a href="/speaking-topics/" data-i18n="tTopics">Speaking Topics</a>
      </div>
      <div class="f-col">
        <p data-i18n="footCompany">Company</p>
        <a href="/founder/" data-i18n="fFounder">Founder</a>
        <a href="/teachers/" data-i18n="fTeachers">For teachers</a>
        <a href="/privacy/" data-i18n="fPrivacy">Privacy</a>
        <a href="https://t.me/flarestamina" target="_blank" rel="noopener">Telegram</a>
      </div>
    </div>
    <div class="f-base">
      <span>© <span id="yy"></span> Flarestamina. <span data-i18n="footFor">For students.</span></span>
      <span data-i18n="footCity">Tashkent, Uzbekistan</span>
      <span data-i18n="footDisc">Not affiliated with IELTS, IDP or British Council.</span>
    </div>
  </div>
</footer>

<script src="/assets/fs-auth.js"></script>
<script>window.FS_UZ = {{
 "skip": "Asosiy kontentga o‘tish",
 "navPractice": "Mashq",
 "navTools": "Vositalar",
 "navNews": "Yangiliklar",
 "signin": "Kirish",
 "startFree": "Bepul boshlash",
 "footBlurb": "Bepul IELTS Academic mashq. Toshkentda yaratilgan.",
 "footPractice": "Mashq",
 "footTools": "Vositalar",
 "footCompany": "Kompaniya",
 "tHub": "Practice Hub",\n "tAll": "Barcha testlar",
 "tWrite": "Writing Lab",
 "tSpeak": "Speaking Lab",
 "tConvert": "Ball konverteri",
 "tDeadlines": "Muddatlar",
 "tPlan": "O‘quv rejasi",
 "tTopics": "Speaking mavzular",
 "fFounder": "Asoschi",
 "fTeachers": "O‘qituvchilarga",
 "fPrivacy": "Maxfiylik",
 "footFor": "Talabalar uchun.",
 "footCity": "Toshkent, O‘zbekiston",
 "footDisc": "IELTS, IDP yoki British Council bilan bog‘liq emas."
}};</script>
<script src="/assets/paper.js?v=2"></script>
<script data-goatcounter="https://flarestamina.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
'''


def article_page(a, slug, author_slug):
    url = '%s/news/a/%s/' % (SITE, slug)
    og = '%s/news/og/%s.png?v=2' % (SITE, slug)
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
        uz_block = ('<div class="prose" id="body-uz" hidden lang="uz">'
                    '<p class="a-alt-h" role="heading" aria-level="1">%s</p>%s</div>' % (escape(a['title_uz']), paras(a['body_uz'])))

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
<title>{seo_title}</title>
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
<div class="wrap narrow" style="padding-top:2.5rem">
<article class="post">
  <p class="crumbs"><a href="/news/">← news</a> / <a href="/news/#articles">articles</a></p>
  {toggle}
  <div id="body-en">
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

  <div class="prose" id="prose-en">{body}</div>
  {uz_block}

  <p class="source">Written by a member of the Flarestamina community · <a href="/news/t/{author_slug}/">more from {author}</a></p>

  <a class="cta-card" href="/ielts-hub/">
    <span><span class="t">Practise what you just read — free</span><span class="s">100+ IELTS mock tests in real exam format, instant band scores</span></span>
    <span class="btn solid">Start practicing</span>
  </a>

  <div class="a-share">
    <a class="chip" href="https://t.me/share/url?url={url_enc}&text={share_enc}" target="_blank" rel="noopener">↗ Share on Telegram</a>
  </div>

  <div class="post-nav"><a class="chip" href="/news/#articles">← All articles</a><a class="chip" href="/writearticle/">Write your own →</a></div>
</article>
</div>
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
           seo_title=escape(a['title']),
           desc=escape(desc), url=url, og=og, date=a['date'], author=escape(a['author']),
           ld=json.dumps(ld, ensure_ascii=False), header=HEADER, footer=FOOTER, toggle=toggle,
           ava=ava, center=('<i>%s</i>' % escape(a['center'])) if a['center'] else '',
           authorlink=('<a class="a-link" href="%s" target="_blank" rel="noopener nofollow ugc">%s</a>'
                       % (escape(link), escape(link.replace('https://', '').rstrip('/')))) if link else '',
           body=paras(a['body']), uz_block=uz_block, author_slug=author_slug,
           url_enc=urllib.parse.quote(url, safe=''),
           share_enc=urllib.parse.quote('"%s" — %s (Flarestamina)' % (a['title'], a['author']), safe=''))


def load_featured():
    try:
        return set(json.load(open(os.path.join(ROOT, 'news/featured.json')))['authors'])
    except Exception:
        return set()


def author_page(author, center, link, items, featured=False):
    slug = slugify(author)
    url = '%s/news/t/%s/' % (SITE, slug)
    link = safe_url(link)
    desc = 'IELTS articles by %s%s on Flarestamina — free IELTS practice for students in Uzbekistan.' % (
        author, (' (' + center + ')') if center else '')
    star = ' <span class="feat-badge">★ Featured</span>' if featured else ''
    cards = ''
    for it in items:
        cards += ('<a class="post-card" href="/news/a/%s/">'
                  '<div class="meta"><span class="chip article">article</span><time>%s</time></div>'
                  '<h2>%s</h2><p class="sum">%s…</p></a>' % (
                      it['slug'], it['a']['date'], escape(it['a']['title']),
                      escape(re.sub(r'\s+', ' ', it['a']['body'])[:150])))
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ProfilePage", "@id": url + "#page",
         "url": url, "name": author,
         "inLanguage": "en",
         "isPartOf": {"@id": SITE + "/#website"},
         "mainEntity": {"@type": "Person", "@id": url + "#person", "name": author,
                        **({"url": link} if link else {}),
                        **({"worksFor": {"@type": "Organization", "name": center}} if center else {}),
                        "knowsAbout": ["IELTS", "English language teaching"]}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Flarestamina", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "News", "item": SITE + "/news/"},
            {"@type": "ListItem", "position": 3, "name": "Articles", "item": SITE + "/news/#articles"},
            {"@type": "ListItem", "position": 4, "name": author, "item": url}]}]}
    return '''<!DOCTYPE html>
<html lang="en">
<head>
{head}
<title>{author} — IELTS articles</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:site_name" content="Flarestamina">
<meta property="og:type" content="profile">
<meta property="og:title" content="{author} — IELTS articles">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/news/og.png?v=2">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{site}/news/og.png?v=2">
<script type="application/ld+json">{ld}</script>
</head>
<body>
{header}
<section class="hero wrap">
  <p class="crumbs"><a href="/news/">← news</a> / <a href="/news/#articles">articles</a></p>
  <div class="a-author big" style="border:none;padding-top:6px">
    <span class="a-ava" style="width:46px;height:46px;font-size:19px">{ava}</span>
    <div><h1 class="a-name">{author}</h1>{star}{center}</div>
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
           star=star,
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
    featured = load_featured()
    for aslug, items in by_author.items():
        a0 = items[0]['a']
        out = os.path.join(ROOT, 'news/t', aslug)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(author_page(a0['author'], a0['center'], a0['link'], items, aslug in featured))
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
