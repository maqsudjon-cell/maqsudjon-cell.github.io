"""Re-shells the news pages into the paper design.

Article bodies, dates, sources and every JSON-LD block are left exactly as
they are — this only swaps the page chrome and the stylesheet. Run it again
after adding a post if the template ever changes.
"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import shell

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)

HEAD_DROP = [
    r'<meta name="color-scheme"[^>]*>\s*',
    r'<link rel="preconnect"[^>]*>\s*',
    r'<link[^>]*fonts\.googleapis\.com/css2[^>]*>\s*',
    r'<style>.*?</style>\s*',
    r'<script>\(function\(\)\{var t=.*?</script>\s*',
    r'<link rel="icon"[^>]*>\s*',
    r'<link rel="apple-touch-icon"[^>]*>\s*',
    r'<meta name="theme-color"[^>]*>\s*',
]

PAPER_HEAD = '''<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/favicon.ico?v=2" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/favicon.svg?v=2">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png?v=2">
<script>
(function () {
  document.documentElement.classList.add('js');
  try {
    var t = localStorage.getItem('fs-paper-theme') || localStorage.getItem('theme') || localStorage.getItem('p8-theme');
    if (t === 'dark') { document.documentElement.classList.add('dark'); document.documentElement.dataset.theme = 'dark'; }
    else { document.documentElement.dataset.theme = 'light'; }
  } catch (e) { document.documentElement.dataset.theme = 'light'; }
})();
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/paper.css?v=1">
'''

FOOT = shell.footer(json.dumps(dict(shell.CHROME_UZ), ensure_ascii=False, indent=1))


def convert(path):
    s = open(path, encoding='utf-8').read()
    if '/assets/paper.css' in s:
        return 'already'
    head = s.split('<head>', 1)[1].split('</head>', 1)[0]
    body = s.split('</head>', 1)[1]

    for pat in HEAD_DROP:
        head = re.sub(pat, '', head, flags=re.S)
    # news pages get the news card rather than the generic one
    head = head.replace('https://flarestamina.com/og-image.png?v=2', 'https://flarestamina.com/news/og.png?v=2')
    head = head.strip() + '\n' + PAPER_HEAD

    body = re.sub(r'<header class="site">.*?</header>', '', body, flags=re.S)
    body = re.sub(r'<footer class="site">.*?</footer>', '', body, flags=re.S)
    body = re.sub(r'<script>\s*function fsTheme.*?</script>', '', body, flags=re.S)
    inner = body.split('<body', 1)[1].split('>', 1)[1].split('</body>')[0].strip()

    inner = inner.replace('<article class="post wrap">', '<article class="post">')
    inner = inner.replace('<div class="body">', '<div class="prose">')
    # the article's own CTA and link row become paper components
    inner = re.sub(r'<a class="cta"[^>]*>\s*<div class="t">(.*?)</div>\s*<div class="s">(.*?)</div>\s*</a>',
                   lambda m: ('<a class="cta-card" href="/ielts-hub/"><span><span class="t">'
                              + re.sub(r'<span class="fl">.*?</span>', '', m.group(1)).strip()
                              + '</span><span class="s">' + m.group(2).strip()
                              + '</span></span><span class="btn solid">Start practicing</span></a>'),
                   inner, flags=re.S)
    inner = re.sub(r'<p class="more">(.*?)</p>',
                   lambda m: '<div class="post-nav">' + re.sub(r'\s*·\s*', '', re.sub(r'<a ', '<a class="chip" ', m.group(1))) + '</div>',
                   inner, flags=re.S)

    out = ('<!DOCTYPE html>\n<html lang="' + (re.search(r'<html lang="([^"]+)"', s).group(1) if re.search(r'<html lang="([^"]+)"', s) else 'en')
           + '">\n<head>\n' + head + '</head>\n'
           + shell.header('/news/').replace('<main id="content">\n', '<main id="content">\n<div class="wrap narrow" style="padding-top:2.5rem">\n')
           + inner + '\n</div>\n' + FOOT)
    open(path, 'w', encoding='utf-8').write(out)
    return 'ok'


if __name__ == '__main__':
    targets = sorted(set(glob.glob('news/*/index.html') + glob.glob('news/*/*/index.html')))
    n = {'ok': 0, 'already': 0}
    for t in targets:
        n[convert(t)] += 1
    print(f'articles: {n["ok"]} converted, {n["already"]} already done')
