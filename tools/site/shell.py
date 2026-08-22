"""Shared page shell for the paper design.

Every migrated page is assembled from here so the header, footer and head
metadata cannot drift between pages. Import it from a build script; do not
hand-edit the header or footer inside a page.
"""

SPARK = ('<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true">'
         '<path d="M16 1.4 L17.85 13.55 L30.6 16 L17.85 18.45 L16 30.6 '
         'L14.15 18.45 L1.4 16 L14.15 13.55 Z"/></svg>')

MOON = ('<svg id="ico-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.8"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')
SUN = ('<svg id="ico-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" '
       'stroke="currentColor" stroke-width="1.8" style="display:none"><circle cx="12" cy="12" r="4"/>'
       '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')

ARROW_UR = ('<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" aria-hidden="true"><path d="M7 7h10v10M7 17 17 7"/></svg>')

RETURN_HUB = 'https://%3A%2F%2F'  # placeholder guard, unused


def head(title, desc, canonical, og_image='https://flarestamina.com/og-image.png?v=2',
         robots='index, follow, max-image-preview:large', extra_head='', og_type='website'):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#ffffff">
<meta name="author" content="Maqsudjon Polatov">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/favicon.ico?v=2" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/favicon.svg?v=2">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96.png?v=2">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png?v=2">
<link rel="manifest" href="/site.webmanifest?v=2">
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<meta property="og:site_name" content="Flarestamina">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_image}">
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
<link rel="preload" href="/assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/plex-mono-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/paper.css?v=1">
{extra_head}</head>
'''


NAV = [('/ielts-hub/', 'navPractice', 'Practice'),
       ('/#tools', 'navTools', 'Tools'),
       ('/news/', 'navNews', 'News')]


def header(current=''):
    def links(cls=''):
        out = []
        for href, key, label in NAV:
            cur = ' aria-current="page"' if href == current else ''
            out.append(f'<a href="{href}"{cur} data-i18n="{key}">{label}</a>')
        return '\n      '.join(out)

    return f'''<body>
<a class="skip" href="#content" data-i18n="skip">Skip to content</a>

<header class="hdr">
  <div class="hdr-in">
    <a class="brand" href="/" aria-label="Flarestamina">{SPARK}Flarestamina</a>
    <nav class="hdr-nav" aria-label="Primary">
      {links()}
    </nav>
    <span class="hdr-sp"></span>
    <div class="lang" role="group" aria-label="Language">
      <button type="button" data-lang="en" class="on">EN</button>
      <button type="button" data-lang="uz">UZ</button>
    </div>
    <button class="icon-btn" id="tgl" aria-label="Theme">{MOON}{SUN}</button>
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
  {links()}
  <div class="row">
    <a class="btn ghost" href="/account/?return=https%3A%2F%2Fflarestamina.com%2Fielts-hub%2F" data-i18n="signin">Sign in</a>
    <a class="btn solid" href="/ielts-hub/" data-i18n="startFree">Start free</a>
  </div>
</div>

<main id="content">
'''


def footer(uz_json, extra_scripts=''):
    return f'''</main>

<footer class="ftr">
  <div class="wrap">
    <div class="f-grid">
      <div class="f-brand">
        <span class="brand">{SPARK}Flarestamina</span>
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
<script>window.FS_UZ = {uz_json};</script>
<script src="/assets/paper.js?v=1"></script>
{extra_scripts}<script data-goatcounter="https://flarestamina.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
'''


# Chrome strings every page shares. Page-specific keys get merged on top.
CHROME_UZ = {
    "skip": "Asosiy kontentga o‘tish",
    "navPractice": "Mashq", "navTools": "Vositalar", "navNews": "Yangiliklar",
    "signin": "Kirish", "startFree": "Bepul boshlash",
    "footBlurb": "Bepul IELTS Academic mashq. Toshkentda yaratilgan.",
    "footPractice": "Mashq", "footTools": "Vositalar", "footCompany": "Kompaniya",
    "tHub": "Practice Hub", "tAll": "Barcha testlar", "tWrite": "Writing Lab", "tSpeak": "Speaking Lab",
    "tConvert": "Ball konverteri", "tDeadlines": "Muddatlar", "tPlan": "O‘quv rejasi",
    "tTopics": "Speaking mavzular",
    "fFounder": "Asoschi", "fTeachers": "O‘qituvchilarga", "fPrivacy": "Maxfiylik",
    "footFor": "Talabalar uchun.", "footCity": "Toshkent, O‘zbekiston",
    "footDisc": "IELTS, IDP yoki British Council bilan bog‘liq emas.",
}
