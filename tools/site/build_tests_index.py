"""Builds /tests/ — a static, crawlable index of the whole catalogue.

Why this page exists: the hub renders its list from tests.json in JavaScript,
so no page on the site contained a real <a href> to any practice test. Google
knew the URLs from the sitemap alone, which is the weakest possible signal —
Search Console reported 105 of them as "Discovered, currently not indexed".
This page gives every test one plain internal link from an indexable page.

Run after adding tests:  python3 tools/site/build_tests_index.py
"""
import json, os, sys, urllib.request
from html import escape

sys.path.insert(0, os.path.dirname(__file__))
import shell

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = 'https://flarestamina.com/ielts-hub/tests.json'

ORDER = ['Listening', 'Reading', 'Writing', 'Speaking', 'Cambridge', 'Full Mock', 'Tools']
LABEL = {'Listening': 'Listening tests', 'Reading': 'Reading tests', 'Writing': 'Writing',
         'Speaking': 'Speaking', 'Cambridge': 'Cambridge', 'Full Mock': 'Full mock exams',
         'Tools': 'Tools and calculators'}
BLURB = {
    'Listening': 'Full papers with four sections and 40 questions, played once, exactly like the real test.',
    'Reading': 'Academic passages with 40 questions in 60 minutes, marked against the official band table.',
    'Writing': 'Task 1 and Task 2 practice with plans and model structures.',
    'Speaking': 'Parts 1 to 3, with the current topic rotation.',
    'Cambridge': 'The full Cambridge book — four tests, every skill.',
    'Full Mock': 'A complete exam in one sitting: Listening, Reading and Writing.',
    'Tools': 'Converters, calculators and trackers that support the practice.',
}


def load():
    local = os.path.join(os.path.dirname(ROOT), 'ielts-hub', 'tests.json')
    if os.path.exists(local):
        return json.load(open(local, encoding='utf-8'))['tests']
    req = urllib.request.Request(SRC, headers={'User-Agent': 'flarestamina-build'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())['tests']


def newest_first(rows):
    import re
    def key(t):
        m = re.search(r'(\d+)', t['title'])
        return -int(m.group(1)) if m else 0
    return sorted(rows, key=key)


def main():
    tests = [t for t in load() if (t.get('url') or '').startswith('https://flarestamina.com')]
    groups = {c: newest_first([t for t in tests if t.get('category') == c]) for c in ORDER}
    total = sum(len(v) for v in groups.values())

    sections, nav, listitems, pos = [], [], [], 1
    for c in ORDER:
        rows = groups.get(c) or []
        if not rows:
            continue
        nav.append(f'<a class="chip" href="#{c.lower().replace(" ", "-")}">{escape(LABEL[c])} <em>{len(rows)}</em></a>')
        items = []
        for t in rows:
            meta = t.get('difficulty') or t.get('description') or ''
            items.append(
                f'      <li><a href="{escape(t["url"])}"><span class="t">{escape(t["title"])}</span>'
                f'<span class="m">{escape(meta)}</span></a></li>')
            listitems.append({"@type": "ListItem", "position": pos, "url": t['url'], "name": t['title']})
            pos += 1
        sections.append(
            f'''  <section class="grp" id="{c.lower().replace(" ", "-")}">
    <h2>{escape(LABEL[c])} <span class="n">{len(rows)}</span></h2>
    <p class="blurb">{escape(BLURB[c])}</p>
    <ul class="tl">
{chr(10).join(items)}
    </ul>
  </section>''')

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": "https://flarestamina.com/tests/#page",
         "url": "https://flarestamina.com/tests/",
         "name": "Every IELTS practice test on Flarestamina",
         "description": f"All {total} free IELTS practice tests and tools, listed in one place.",
         "inLanguage": "en", "isPartOf": {"@id": "https://flarestamina.com/#website"},
         "publisher": {"@id": "https://flarestamina.com/#org"}},
        {"@type": "ItemList", "name": "Flarestamina IELTS practice tests",
         "numberOfItems": total, "itemListOrder": "https://schema.org/ItemListUnordered",
         "itemListElement": listitems},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Flarestamina", "item": "https://flarestamina.com/"},
            {"@type": "ListItem", "position": 2, "name": "All tests", "item": "https://flarestamina.com/tests/"}]}]}

    style = '''
.tl{list-style:none;display:grid;gap:.4rem;margin-top:1rem}
@media(min-width:760px){.tl{grid-template-columns:1fr 1fr}}
.tl a{display:flex;flex-direction:column;gap:.15rem;padding:.75rem .95rem;border-radius:6px;background:var(--surface);box-shadow:var(--card);transition:box-shadow .2s}
.tl a:hover{box-shadow:var(--card-hover)}
.tl .t{font-weight:500;letter-spacing:-.01em;font-size:.92rem}
.tl .m{font-size:.75rem;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.grp{margin-top:3.5rem}
.grp h2{font-size:1.35rem;display:flex;align-items:baseline;gap:.6rem}
.grp h2 .n{font-family:var(--mono);font-size:.8rem;color:var(--subtle);font-weight:400}
.grp .blurb{margin-top:.5rem;color:var(--muted);font-size:.9rem;max-width:44rem;line-height:1.7}
.jump{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:1.5rem}
.jump em{font-style:normal;font-family:var(--mono);font-size:.7rem;opacity:.65}
'''

    body = f'''
<section class="page-head">
  <div class="wrap">
    <p class="kicker">The whole catalogue</p>
    <h1>Every IELTS practice test on Flarestamina</h1>
    <p class="lede">All {total} papers and tools in one list — free, in real exam format, with instant band scores. The practice hub is the nicer way to browse them; this page exists so every test is one plain link away.</p>
    <div class="jump">{"".join(nav)}</div>
  </div>
</section>

<section>
  <div class="wrap">
{chr(10).join(sections)}
  </div>
</section>
'''

    html = (shell.head('Every IELTS practice test — Flarestamina',
                       f'All {total} free IELTS practice tests and tools on Flarestamina: Listening, Reading, Writing, Speaking, Cambridge and full mock exams.',
                       'https://flarestamina.com/tests/',
                       'https://flarestamina.com/og-image.png?v=2',
                       extra_head='<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False) + '\n</script>\n<style>\n' + style.strip() + '\n</style>\n')
            + shell.header() + body
            + shell.footer(json.dumps(dict(shell.CHROME_UZ), ensure_ascii=False, indent=1)))

    os.makedirs(os.path.join(ROOT, 'tests'), exist_ok=True)
    open(os.path.join(ROOT, 'tests', 'index.html'), 'w', encoding='utf-8').write(html)
    print(f'/tests/ built — {total} links across {len([c for c in ORDER if groups.get(c)])} groups, {len(html)} bytes')


if __name__ == '__main__':
    main()
