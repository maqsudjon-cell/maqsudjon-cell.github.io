# -*- coding: utf-8 -*-
"""Builds /uz/ — the Uzbek entry page.

Why: every page on the site ships English HTML and translates in the browser,
so Google only ever indexes the English copy. Uzbek queries ("bepul IELTS
testlari", "IELTS test ishlash onlayn") have almost no competition, but nothing
on the domain could rank for them. This page is real Uzbek HTML at its own URL,
declared as the hreflang="uz" counterpart of the homepage.

Facts on the page are sourced, not invented: prices were read from the IDP
Tashkent booking page on 2026-08-23 and each claim links to the news post that
carries the source.

Run:  python3 tools/site/build_uz.py
"""
import json, os, sys
from html import escape

sys.path.insert(0, os.path.dirname(__file__))
import shell
from build_tests_index import load

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
URL = 'https://flarestamina.com/uz/'

STYLE = '''
.cards{display:grid;gap:.8rem;margin-top:1.4rem}
@media(min-width:720px){.cards{grid-template-columns:1fr 1fr}}
.card{display:block;padding:1.15rem 1.25rem;border-radius:8px;background:var(--surface);box-shadow:var(--card);transition:box-shadow .2s}
.card:hover{box-shadow:var(--card-hover)}
.card h3{font-size:1rem;letter-spacing:-.01em;display:flex;align-items:baseline;gap:.5rem}
.card h3 span{font-family:var(--mono);font-size:.72rem;color:var(--subtle);font-weight:400}
.card p{margin-top:.4rem;font-size:.87rem;color:var(--muted);line-height:1.65}
.facts{list-style:none;display:grid;gap:.1rem;margin-top:1.2rem;border-top:1px solid var(--line)}
.facts li{display:grid;grid-template-columns:10rem 1fr;gap:1rem;padding:.7rem 0;border-bottom:1px solid var(--line);font-size:.9rem}
.facts b{font-family:var(--mono);font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:var(--subtle);font-weight:400;padding-top:.15rem}
@media(max-width:560px){.facts li{grid-template-columns:1fr;gap:.15rem}}
.sec{margin-top:3.5rem}
.sec h2{font-size:1.35rem;letter-spacing:-.02em}
.sec>p{margin-top:.7rem;color:var(--muted);font-size:.94rem;line-height:1.75;max-width:44rem}
.qa{margin-top:1.2rem;border-top:1px solid var(--line)}
.qa details{border-bottom:1px solid var(--line)}
.qa summary{cursor:pointer;padding:.85rem 0;font-weight:500;font-size:.95rem;list-style:none}
.qa summary::-webkit-details-marker{display:none}
.qa summary::after{content:"+";float:right;color:var(--subtle);font-family:var(--mono)}
.qa details[open] summary::after{content:"–"}
.qa p{padding:0 0 .95rem;color:var(--muted);font-size:.9rem;line-height:1.75;max-width:44rem}
.cta-row{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1.6rem}
.linkrow{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:1.2rem}
'''

FAQ = [
    ("Flarestamina'dagi testlar bepulmi?",
     "Ha. Listening va Reading testlari, Writing Lab, Speaking Lab va barcha kalkulyatorlar bepul va ro‘yxatdan o‘tishni talab qilmaydi. Akkaunt faqat natijalaringizni saqlab borish uchun kerak. Faqat to‘liq mock imtihon pullik."),
    ("IELTS testini onlayn qanday ishlayman?",
     "Listening yoki Reading bo‘limini tanlang, testni oching va vaqtni to‘xtatmasdan boshdan oxirigacha ishlang. Yuborganingizdan keyin 40 talik xom ball, u qaysi band ekani va har bir savol bo‘yicha to‘liq javob tahlili chiqadi."),
    ("IELTS necha ball tizimida baholanadi?",
     "Har bir bo‘lim 0 dan 9 gacha band bilan baholanadi, umumiy ball esa to‘rt bo‘lim o‘rtachasi sifatida chiqadi va eng yaqin 0,5 ga yaxlitlanadi. Listening va Reading’da 40 talik xom ball rasmiy jadval bo‘yicha bandga aylantiriladi."),
    ("O‘zbekistonda IELTS qancha turadi?",
     "2026-yil avgust holatiga ko‘ra kompyuterda topshirish 2 665 000 so‘m, qog‘ozda 2 639 000 so‘m. Narxlar o‘zgarib turadi — rasmiy manba havolasi bilan batafsil ma’lumot “IELTS narxi 2026” maqolasida."),
    ("IELTS sertifikati qancha muddat amal qiladi?",
     "Odatda ikki yil. Ba’zi tashkilotlar bundan qisqaroq muddat talab qilishi mumkin, shuning uchun ariza berayotgan joyingizning shartini alohida tekshiring."),
    ("IELTS 6.0 CEFR bo‘yicha qaysi daraja?",
     "IELTS 6.0 — B2. Ball konverteri sahifasida IELTS, CEFR, Multilevel, TOEFL iBT va Duolingo o‘rtasidagi moslikni ko‘rishingiz mumkin."),
]


def main():
    tests = [t for t in load() if (t.get('url') or '').startswith('https://flarestamina.com')]
    n_lis = sum(1 for t in tests if t.get('category') == 'Listening')
    n_read = sum(1 for t in tests if t.get('category') == 'Reading')
    # 'mashq testi' has to mean a practice test: the catalogue also carries
    # converters and calculators, and counting those inflates the headline.
    n_all = sum(1 for t in tests if t.get('category') != 'Tools')
    n_cat = len(tests)

    title = f'Bepul IELTS testlari onlayn — {n_all} ta mashq testi | Flarestamina'
    desc = (f'{n_lis} ta Listening va {n_read} ta Reading mashq testi, Writing va Speaking Lab — '
            'bepul, ro‘yxatdan o‘tmasdan. Haqiqiy imtihon formati, darhol band ball va javob tahlili.')

    cards = [
        ('/uz/listening/', 'IELTS Listening testlari', str(n_lis),
         'To‘rt bo‘lim, 40 ta savol, audio bir marta yangraydi — xuddi imtihondagidek. Tugatishingiz bilan band ball chiqadi.'),
        ('/uz/reading/', 'IELTS Reading testlari', str(n_read),
         'Academic Reading: uchta matn, 40 ta savol, 60 daqiqa. Oxirida qo‘shimcha vaqt yo‘q, xuddi haqiqiy imtihondagidek.'),
        ('/uz/writing/', 'IELTS Writing Lab', 'Task 1 + 2',
         'Task 1 va Task 2 uchun yozib, tuzilma va til bo‘yicha band bahosini olasiz. Rejalar va namunaviy tuzilmalar bilan.'),
        ('/uz/speaking/', 'IELTS Speaking Lab', '166 mavzu',
         'Part 1–3 savollari, ovozingizni yozib olish va band bo‘yicha izoh. Speaking mavzular rotatsiyasi alohida sahifada.'),
        ('/full-mock/', 'To‘liq mock imtihon', '3 bo‘lim',
         'Listening, Reading va Writing bir o‘tirishda — imtihon kuni qanday bo‘lsa shunday. Yagona pullik xizmat.'),
        ('/tests/', 'Barcha testlar ro‘yxati', str(n_cat),
         'Saytdagi har bir test va vosita bitta sahifada, bo‘limlarga ajratilgan holda.'),
    ]

    skills = [('/uz/listening/', 'Listening — format va savol turlari'),
              ('/uz/reading/', 'Reading — savol turlari va vaqt'),
              ('/uz/writing/', 'Writing — Task 1 va Task 2'),
              ('/uz/speaking/', 'Speaking — Part 1, 2, 3')]

    tools = [('/convert/', 'Ball konverteri'), ('/band-calculator/', 'Band kalkulyatori'),
             ('/plan/', 'O‘quv rejasi'), ('/deadlines/', 'Grant muddatlari'),
             ('/speaking-topics/', 'Speaking mavzular'), ('/news/', 'Yangiliklar')]

    facts = [
        ('Bo‘limlar', 'To‘rtta: Listening, Reading, Writing, Speaking. Listening va Reading’da 40 tadan savol bor.'),
        ('Baholash', 'Har bo‘lim 0–9 band. Umumiy ball — to‘rttasining o‘rtachasi, eng yaqin 0,5 ga yaxlitlanadi.'),
        ('Format', 'Kompyuterda yoki qog‘ozda. Savollar bir xil, farq faqat topshirish usulida va natija muddatida.'),
        ('Amal qilish muddati', 'Odatda ikki yil.'),
        ('CEFR bilan bog‘liqligi', 'IELTS 6.0 ≈ B2. To‘liq jadval ball konverteri sahifasida.'),
    ]

    news = [('/news/ielts-narxi-2026/', 'IELTS narxi 2026'),
            ('/news/ielts-qayerda-topshiriladi/', 'IELTS qayerda topshiriladi'),
            ('/news/ielts-sertifikat-2-yil/', 'Sertifikat necha yil amal qiladi'),
            ('/news/one-skill-retake-ozbekiston/', 'One Skill Retake'),
            ('/news/ielts-5-5-dan-6-5-ga/', '5.5 dan 6.5 ga qanday ko‘tarilish mumkin')]

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": URL + "#page", "url": URL, "name": title,
         "description": desc, "inLanguage": "uz",
         "isPartOf": {"@id": "https://flarestamina.com/#website"},
         "publisher": {"@id": "https://flarestamina.com/#org"}},
        {"@type": "FAQPage", "inLanguage": "uz", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Flarestamina", "item": "https://flarestamina.com/"},
            {"@type": "ListItem", "position": 2, "name": "O‘zbekcha", "item": URL}]}]}

    alt = ('<link rel="alternate" hreflang="uz" href="https://flarestamina.com/uz/">\n'
           '<link rel="alternate" hreflang="en" href="https://flarestamina.com/">\n'
           '<link rel="alternate" hreflang="x-default" href="https://flarestamina.com/">\n')

    body = f'''
<section class="page-head">
  <div class="wrap">
    <p class="kicker">O‘zbekcha</p>
    <h1>Bepul IELTS testlari onlayn</h1>
    <p class="lede">{n_lis} ta Listening va {n_read} ta Reading mashq testi, Writing va Speaking Lab — hammasi bepul va ro‘yxatdan o‘tmasdan. Testlar haqiqiy imtihon formatida va vaqti bilan ishlaydi: tugatganingizda 40 talik xom ball, u qaysi band ekani va har bir savol bo‘yicha to‘liq tahlil chiqadi.</p>
    <div class="cta-row">
      <a class="btn solid" href="/ielts-hub/">Testni boshlash</a>
      <a class="btn ghost" href="/tests/">Barcha testlar</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <section class="sec">
      <h2>Nima bor</h2>
      <div class="cards">
{chr(10).join(f'        <a class="card" href="{h}"><h3>{escape(t)} <span>{escape(c)}</span></h3><p>{escape(d)}</p></a>' for h, t, c, d in cards)}
      </div>
    </section>

    <section class="sec">
      <h2>Bo‘limlar bo‘yicha qo‘llanma</h2>
      <p>Har bir bo‘limning formati, savol turlari, xom balldan bandga o‘tish jadvali va ko‘p uchraydigan xatolar — o‘zbek tilida.</p>
      <div class="linkrow">
{chr(10).join(f'        <a class="chip" href="{h}">{escape(t)}</a>' for h, t in skills)}
      </div>
    </section>

    <section class="sec">
      <h2>IELTS haqida qisqacha</h2>
      <ul class="facts">
{chr(10).join(f'        <li><b>{escape(k)}</b><span>{escape(v)}</span></li>' for k, v in facts)}
      </ul>
    </section>

    <section class="sec">
      <h2>O‘zbekistonda topshirish</h2>
      <p>2026-yil avgust holatiga ko‘ra kompyuterda topshirish <strong>2 665 000 so‘m</strong>, qog‘ozda <strong>2 639 000 so‘m</strong> turadi; narxlar IDP Toshkent bron sahifasidan olingan. Kompyuterda natija 1–5 kunda chiqadi va One Skill Retake imkoniyati bor, qog‘ozda esa yo‘q. Har bir raqam manba havolasi bilan quyidagi maqolalarda yozilgan — narxlar o‘zgarib turadi, shuning uchun ro‘yxatdan o‘tishdan oldin rasmiy sahifani tekshiring.</p>
      <div class="linkrow">
{chr(10).join(f'        <a class="chip" href="{h}">{escape(t)}</a>' for h, t in news)}
      </div>
    </section>

    <section class="sec">
      <h2>Vositalar</h2>
      <p>Ball hisoblash, o‘quv rejasi va grant muddatlari — hammasi bepul.</p>
      <div class="linkrow">
{chr(10).join(f'        <a class="chip" href="{h}">{escape(t)}</a>' for h, t in tools)}
      </div>
    </section>

    <section class="sec">
      <h2>Qayerdan boshlash kerak</h2>
      <p>Birinchi qadam — hozirgi darajangizni bilish. Bitta Listening va bitta Reading testini vaqtni to‘xtatmasdan ishlang: shu ikki ball sizning boshlang‘ich nuqtangiz. Keyin xatolarni tahlil qiling — javobni emas, javob matnning qayerida turganini toping. Haftasiga ikkita test, yaxshilab ko‘rib chiqilgani, shoshib ishlangan yettitadan ko‘proq foyda beradi. Nishon ballgacha qancha vaqt kerakligini <a href="/plan/">o‘quv rejasi</a> sahifasi hisoblab beradi.</p>
    </section>

    <section class="sec">
      <h2>Ko‘p so‘raladigan savollar</h2>
      <div class="qa">
{chr(10).join(f'        <details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q, a in FAQ)}
      </div>
    </section>
  </div>
</section>
'''

    # The page is written in Uzbek, so the EN button should send the reader to
    # the English homepage instead of trying to translate this DOM back.
    en_switch = '''<script>
(function(){
  var b=document.querySelector('[data-lang="en"]');
  if(b) b.addEventListener('click',function(e){e.stopPropagation();location.href='/';},true);
})();
</script>
'''

    html = (shell.head(title, desc, URL, 'https://flarestamina.com/og-image.png?v=2',
                       extra_head=alt + '<script type="application/ld+json">\n'
                       + json.dumps(ld, ensure_ascii=False) + '\n</script>\n<style>\n'
                       + STYLE.strip() + '\n</style>\n', lang='uz')
            + shell.header() + body
            + shell.footer(json.dumps(dict(shell.CHROME_UZ), ensure_ascii=False, indent=1),
                           extra_scripts=en_switch))

    os.makedirs(os.path.join(ROOT, 'uz'), exist_ok=True)
    open(os.path.join(ROOT, 'uz', 'index.html'), 'w', encoding='utf-8').write(html)
    print(f'/uz/ built — {len(html)} bytes, {n_all} tests referenced')


if __name__ == '__main__':
    main()
