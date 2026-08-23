"""Builds /ielts-listening-test/ and /ielts-reading-test/.

Why these pages exist: /tests/ is one long mixed catalogue, so nothing on the
site targets the two phrases students actually type — "IELTS listening test"
and "IELTS reading test". These are the skill landing pages: what the section
is, how it is marked, and every paper of that skill as a plain <a href>.

Run after adding tests:  python3 tools/site/build_skill_pages.py
"""
import json, os, re, sys
from html import escape

sys.path.insert(0, os.path.dirname(__file__))
import shell
from build_tests_index import load, newest_first

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))

STYLE = '''
.tl{list-style:none;display:grid;gap:.4rem;margin-top:1.2rem}
@media(min-width:760px){.tl{grid-template-columns:1fr 1fr}}
.tl a{display:flex;flex-direction:column;gap:.15rem;padding:.75rem .95rem;border-radius:6px;background:var(--surface);box-shadow:var(--card);transition:box-shadow .2s}
.tl a:hover{box-shadow:var(--card-hover)}
.tl .t{font-weight:500;letter-spacing:-.01em;font-size:.92rem}
.tl .m{font-size:.75rem;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.facts{list-style:none;display:grid;gap:.1rem;margin-top:1.2rem;border-top:1px solid var(--line)}
.facts li{display:grid;grid-template-columns:9.5rem 1fr;gap:1rem;padding:.7rem 0;border-bottom:1px solid var(--line);font-size:.9rem}
.facts b{font-family:var(--mono);font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:var(--subtle);font-weight:400;padding-top:.15rem}
@media(max-width:560px){.facts li{grid-template-columns:1fr;gap:.15rem}}
.sec{margin-top:3.5rem}
.sec h2{font-size:1.35rem;letter-spacing:-.02em}
.sec p{margin-top:.7rem;color:var(--muted);font-size:.94rem;line-height:1.75;max-width:44rem}
.qa{margin-top:1.2rem;border-top:1px solid var(--line)}
.qa details{border-bottom:1px solid var(--line)}
.qa summary{cursor:pointer;padding:.85rem 0;font-weight:500;font-size:.95rem;list-style:none}
.qa summary::-webkit-details-marker{display:none}
.qa summary::after{content:"+";float:right;color:var(--subtle);font-family:var(--mono)}
.qa details[open] summary::after{content:"–"}
.qa p{padding:0 0 .95rem;color:var(--muted);font-size:.9rem;line-height:1.75;max-width:44rem}
.cta-row{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1.6rem}
'''

PAGES = {
    'Listening': dict(
        slug='ielts-listening-test',
        title='IELTS Listening Practice Test — {n} Free Papers with Answers',
        desc='{n} free IELTS Listening practice tests with answers and instant band scores. Four sections, 40 questions, real exam audio played once — no sign-up.',
        h1='IELTS Listening practice tests',
        kicker='Listening',
        lede='{n} full Listening papers, free and in real exam format: four sections, 40 questions, audio that plays once. You get a raw score out of 40 and the band it converts to the moment you finish.',
        facts=[('Sections', 'Four, in fixed order: a conversation in an everyday context, a monologue in an everyday context, a conversation of up to four people in a study context, and an academic monologue.'),
               ('Questions', '40 in total, ten per section.'),
               ('Audio', 'Played once only. That is the part most practice sites get wrong, and the part that decides your band.'),
               ('Timing', 'About 30 minutes of audio. On paper you then get 10 extra minutes to copy answers onto the answer sheet; on computer you get 2 minutes to check.'),
               ('Marking', 'One mark per correct answer. Your raw score out of 40 converts to a band — spelling and grammar count.')],
        how='Sit one paper end to end without pausing the audio. Mark it, then open the answer review and read the transcript for every question you missed — not just the answer, but the sentence that contained it. Two papers a week reviewed properly beats seven papers rushed.',
        faq=[('Are these IELTS Listening tests free?',
              'Yes. Every Listening paper on Flarestamina is free and needs no account. Signing in only stores your results so you can see progress over time.'),
             ('How many questions are in the IELTS Listening test?',
              '40 questions across four sections, ten per section. Each correct answer is worth one mark.'),
             ('How long is the IELTS Listening test?',
              'Roughly 30 minutes of audio. Paper-based candidates get 10 further minutes to transfer answers; computer-delivered candidates get 2 minutes to check them.'),
             ('Can I replay the audio?',
              'Not in the real exam — it plays once. These mocks follow the same rule, because practising with replays trains a skill the exam does not test.'),
             ('Do I get a band score?',
              'Yes. Each paper marks itself out of 40 and shows the band that raw score converts to, plus a full answer review.')],
    ),
    'Reading': dict(
        slug='ielts-reading-test',
        title='IELTS Reading Practice Test — {n} Free Papers with Answers',
        desc='{n} free IELTS Academic Reading practice tests with answers and instant band scores. Three passages, 40 questions, 60 minutes — no sign-up needed.',
        h1='IELTS Academic Reading practice tests',
        kicker='Reading',
        lede='{n} Academic Reading papers, free and timed like the real thing: three passages, 40 questions, 60 minutes with no extra time at the end. Instant marking and a full answer review.',
        facts=[('Passages', 'Three, getting harder as you go, taken from the kind of books, journals and newspapers the real exam uses.'),
               ('Questions', '40 in total, spread across the three passages.'),
               ('Timing', '60 minutes for everything. Unlike Listening there is no extra transfer time, so answers go straight onto the sheet.'),
               ('Question types', 'Matching headings, True/False/Not Given, matching information, sentence and summary completion, multiple choice, matching features, short answers.'),
               ('Marking', 'One mark per correct answer, converted to a band from your raw score out of 40.')],
        how='Give yourself the full 60 minutes and no more. The usual failure is not vocabulary, it is time: 20 minutes per passage, and if a question will not come, leave it and return. Afterwards, find where in the passage each answer actually lived — that is what builds speed.',
        faq=[('Are these IELTS Reading tests free?',
              'Yes, all of them, with no account required. Signing in only saves your results.'),
             ('How many passages are in IELTS Academic Reading?',
              'Three passages with 40 questions between them, and they get progressively harder.'),
             ('How long is the IELTS Reading test?',
              '60 minutes. There is no extra time to transfer answers, which is why pacing matters more here than in any other section.'),
             ('Is Academic Reading different from General Training?',
              'Yes. Academic uses three longer passages from academic-style sources; General Training uses shorter workplace and everyday texts. The papers here are Academic.'),
             ('Do these tests show the answers?',
              'Yes. After you submit you get your raw score, the band it converts to, and a question-by-question review with the correct answers.')],
    ),
}


def build(cat, cfg, tests):
    rows = newest_first([t for t in tests if t.get('category') == cat])
    n = len(rows)
    url = f'https://flarestamina.com/{cfg["slug"]}/'
    title = cfg['title'].format(n=n)
    desc = cfg['desc'].format(n=n)

    items, listitems = [], []
    for i, t in enumerate(rows, 1):
        meta = t.get('difficulty') or t.get('description') or ''
        items.append(f'      <li><a href="{escape(t["url"])}"><span class="t">{escape(t["title"])}</span>'
                     f'<span class="m">{escape(meta)}</span></a></li>')
        listitems.append({"@type": "ListItem", "position": i, "url": t['url'], "name": t['title']})

    facts = '\n'.join(f'      <li><b>{escape(k)}</b><span>{escape(v)}</span></li>' for k, v in cfg['facts'])
    faq = '\n'.join(
        f'      <details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>'
        for q, a in cfg['faq'])

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url + "#page", "url": url, "name": title,
         "description": desc, "inLanguage": "en",
         "isPartOf": {"@id": "https://flarestamina.com/#website"},
         "publisher": {"@id": "https://flarestamina.com/#org"}},
        {"@type": "ItemList", "name": f'Flarestamina IELTS {cat} practice tests',
         "numberOfItems": n, "itemListOrder": "https://schema.org/ItemListUnordered",
         "itemListElement": listitems},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in cfg['faq']]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Flarestamina", "item": "https://flarestamina.com/"},
            {"@type": "ListItem", "position": 2, "name": "All tests", "item": "https://flarestamina.com/tests/"},
            {"@type": "ListItem", "position": 3, "name": cfg['h1'], "item": url}]}]}

    body = f'''
<section class="page-head">
  <div class="wrap">
    <p class="kicker" data-i18n="kicker">{escape(cfg['kicker'])}</p>
    <h1 data-i18n="h1">{escape(cfg['h1'])}</h1>
    <p class="lede" data-i18n="lede">{escape(cfg['lede'].format(n=n))}</p>
    <div class="cta-row">
      <a class="btn solid" href="{escape(rows[0]['url']) if rows else '/ielts-hub/'}" data-i18n="ctaStart">Start the newest paper</a>
      <a class="btn ghost" href="/tests/" data-i18n="ctaAll">Every test</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <section class="sec">
      <h2 data-i18n="h2format">What the {escape(cat)} test looks like</h2>
      <ul class="facts">
{facts}
      </ul>
    </section>

    <section class="sec" id="tests">
      <h2 data-i18n="h2list">All {n} {escape(cat.lower())} papers</h2>
      <p data-i18n="listNote">Free, no account needed. Each one marks itself and shows a band the moment you submit.</p>
      <ul class="tl">
{chr(10).join(items)}
      </ul>
    </section>

    <section class="sec">
      <h2 data-i18n="h2how">How to use these</h2>
      <p data-i18n="how">{escape(cfg['how'])}</p>
    </section>

    <section class="sec">
      <h2 data-i18n="h2faq">Questions students ask</h2>
      <div class="qa">
{faq}
      </div>
    </section>
  </div>
</section>
'''

    uz = dict(shell.CHROME_UZ)
    uz.update(UZ[cat])
    html = (shell.head(title, desc, url, 'https://flarestamina.com/og-image.png?v=2',
                       extra_head='<script type="application/ld+json">\n'
                       + json.dumps(ld, ensure_ascii=False) + '\n</script>\n<style>\n'
                       + STYLE.strip() + '\n</style>\n')
            + shell.header() + body
            + shell.footer(json.dumps(uz, ensure_ascii=False, indent=1)))

    out = os.path.join(ROOT, cfg['slug'])
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(html)
    print(f'/{cfg["slug"]}/ built — {n} papers, {len(html)} bytes')
    return n


UZ = {
    'Listening': {
        "kicker": "Listening",
        "h1": "IELTS Listening mashq testlari",
        "lede": "To‘liq Listening testlari — bepul va haqiqiy imtihon formatida: to‘rt bo‘lim, 40 ta savol, audio bir marta yangraydi. Tugatganingizda 40 talik xom ball va u qaysi band ekanini darrov ko‘rasiz.",
        "ctaStart": "Eng yangi testni boshlash", "ctaAll": "Barcha testlar",
        "h2format": "Listening testi qanday tuzilgan",
        "h2list": "Barcha listening testlari",
        "listNote": "Bepul, ro‘yxatdan o‘tish shart emas. Har biri o‘zini tekshiradi va yuborishingiz bilan band ko‘rsatadi.",
        "h2how": "Bulardan qanday foydalanish kerak",
        "how": "Bitta testni audioni to‘xtatmasdan boshdan oxirigacha ishlang. Keyin tekshiring va xato qilgan har bir savol uchun transkriptni o‘qing — faqat javobni emas, javob turgan gapni. Haftasiga ikkita test, yaxshilab tahlil qilingani — shoshib ishlangan yettitadan afzal.",
        "h2faq": "Talabalar so‘raydigan savollar",
    },
    'Reading': {
        "kicker": "Reading",
        "h1": "IELTS Academic Reading mashq testlari",
        "lede": "Academic Reading testlari — bepul va haqiqiy vaqt bilan: uchta matn, 40 ta savol, 60 daqiqa, oxirida qo‘shimcha vaqt yo‘q. Darhol tekshiriladi va to‘liq javob tahlili beriladi.",
        "ctaStart": "Eng yangi testni boshlash", "ctaAll": "Barcha testlar",
        "h2format": "Reading testi qanday tuzilgan",
        "h2list": "Barcha reading testlari",
        "listNote": "Bepul, ro‘yxatdan o‘tish shart emas. Har biri o‘zini tekshiradi va yuborishingiz bilan band ko‘rsatadi.",
        "h2how": "Bulardan qanday foydalanish kerak",
        "how": "O‘zingizga to‘liq 60 daqiqa bering, ortiq emas. Ko‘pchilik so‘z boyligidan emas, vaqtdan yiqiladi: har matnga 20 daqiqa, savol chiqmasa tashlab ketib, keyin qayting. Keyin har bir javob matnning qayerida turganini toping — tezlikni shu o‘stiradi.",
        "h2faq": "Talabalar so‘raydigan savollar",
    },
}


def main():
    tests = [t for t in load() if (t.get('url') or '').startswith('https://flarestamina.com')]
    for cat, cfg in PAGES.items():
        build(cat, cfg, tests)


if __name__ == '__main__':
    main()
