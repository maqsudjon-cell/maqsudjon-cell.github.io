"""Builds the small content pages: /founder/, /teachers/, /privacy/ and 404.

Body copy is carried over from the pages these replace, word for word.
Nothing here is new marketing — only the shell around it changed.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import shell

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')


def write(rel, html):
    path = os.path.normpath(os.path.join(ROOT, rel))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(html)
    print('  ✓', rel, f'({len(html)} bytes)')


def page(rel, *, title, desc, canonical, og, uz, body, extra_head='', robots='index, follow, max-image-preview:large', current=''):
    u = dict(shell.CHROME_UZ); u.update(uz)
    html = (shell.head(title, desc, canonical, og, robots=robots, extra_head=extra_head)
            + shell.header(current) + body
            + shell.footer(json.dumps(u, ensure_ascii=False, indent=1)))
    write(rel, html)


# ─────────────────────────────────────────────────────── founder
FOUNDER_LD = open(os.path.join(ROOT, 'tools/site/founder-ld.json'), encoding='utf-8').read().strip()

page('founder/index.html',
     title='Maqsudjon Polatov — Founder of Flarestamina',
     desc='Founder of Flarestamina, a free IELTS practice ecosystem engineered in Tashkent, Uzbekistan.',
     canonical='https://flarestamina.com/founder/',
     og='https://flarestamina.com/founder/og.png',
     extra_head='<script type="application/ld+json">\n' + FOUNDER_LD + '\n</script>\n',
     uz={
       'kicker': 'Asoschi',
       'h1': 'Maqsudjon Polatov',
       'role': 'Bepul IELTS vositalarini quradi · Toshkent',
       'bio': '<strong>Maqsudjon Polatov</strong> — <a href="/">Flarestamina</a> asoschisi. Bu Toshkentda yaratilgan bepul IELTS mashq ekosistemasi: haqiqiy imtihon formatidagi 100+ Listening, Reading, Writing va Speaking testi, darhol band bahosi va natijalarni kuzatish. Har bir talaba uchun bepul — doimo.',
       'projects': 'Loyihalar', 'elsewhere': 'Boshqa joylarda',
       'p1d': '100+ bepul IELTS mock test', 'p2d': 'Esse tekshiruvi, band izohi',
       'p3d': '1–3 qism mashqi', 'p4d': 'Haqiqiy imtihon simulyatsiyasi',
       'p5d': 'Kunlik mashq seriyasi', 'p6d': 'IELTS yangiliklari va muddatlar',
       'p7d': 'maqsudjon.com’dagi build log ↗',
       'sTeachers': 'O‘qituvchilarga',
     },
     body='''
<section class="page-head">
  <div class="wrap narrow">
    <p class="kicker" data-i18n="kicker">Founder</p>
    <h1 data-i18n="h1">Maqsudjon Polatov</h1>
    <p class="lede" data-i18n="role">Builds free IELTS things · Tashkent</p>
    <div class="rail"></div>
  </div>
</section>

<section>
  <div class="wrap narrow">
    <div class="prose" style="margin-bottom:3rem">
      <p data-i18n-html="bio"><strong>Maqsudjon Polatov</strong> — founder of <a href="/">Flarestamina</a>, a free IELTS practice ecosystem engineered in Tashkent, Uzbekistan. 100+ Listening, Reading, Writing and Speaking tests in real exam format, with instant band scores and progress tracking. Free for every student, forever.</p>
    </div>

    <p class="kicker" style="margin-bottom:.5rem" data-i18n="projects">Projects</p>
    <div class="rows">
      <a href="/ielts-hub/"><span><b>Flarestamina</b><small class="muted" data-i18n="p1d">100+ free IELTS mock tests</small></span>''' + shell.ARROW_UR + '''</a>
      <a href="/writearticle/"><span><b>Writing Lab</b><small class="muted" data-i18n="p2d">Essay checker, band feedback</small></span>''' + shell.ARROW_UR + '''</a>
      <a href="/pangea8-speaking/"><span><b>Speaking Lab</b><small class="muted" data-i18n="p3d">Part 1–3 practice</small></span>''' + shell.ARROW_UR + '''</a>
      <a href="/full-mock/"><span><b>Full Mock</b><small class="muted" data-i18n="p4d">Real exam simulation</small></span>''' + shell.ARROW_UR + '''</a>
      <a href="/challenge/"><span><b>40-day challenge</b><small class="muted" data-i18n="p5d">Daily study streak</small></span>''' + shell.ARROW_UR + '''</a>
      <a href="/news/"><span><b>News</b><small class="muted" data-i18n="p6d">IELTS updates &amp; deadlines</small></span>''' + shell.ARROW_UR + '''</a>
      <a href="https://maqsudjon.com/#updates" rel="noopener"><span><b>Blog</b><small class="muted" data-i18n="p7d">Build log on maqsudjon.com ↗</small></span>''' + shell.ARROW_UR + '''</a>
    </div>

    <p class="kicker" style="margin:2.5rem 0 .75rem" data-i18n="elsewhere">Elsewhere</p>
    <div style="display:flex;flex-wrap:wrap;gap:.5rem">
      <a class="chip" href="https://t.me/flarestamina" rel="noopener" target="_blank">Telegram</a>
      <a class="chip" href="https://github.com/maqsudjon-cell" rel="noopener" target="_blank">GitHub</a>
      <a class="chip" href="https://maqsudjon.com" rel="noopener" target="_blank">maqsudjon.com</a>
      <a class="chip" href="/teachers/" data-i18n="sTeachers">For teachers</a>
    </div>
  </div>
</section>
''')

print('done')


# ─────────────────────────────────────────────────────── teachers
page('teachers/index.html',
     title='For teachers — Flarestamina',
     desc='Bring your class. One account per student, every result tracked, 100+ free IELTS tests and affordable full mocks.',
     canonical='https://flarestamina.com/teachers/',
     og='https://flarestamina.com/teachers/og.png',
     current='/teachers/',
     uz={
       'kicker': 'O‘qituvchilarga', 'h1': 'Sinfingizni olib keling. Har bir natijani ko‘ring.',
       'lede': 'Flarestamina — O‘zbekistonda yaratilgan bepul IELTS mashq ekosistemasi: haqiqiy formatdagi 100+ test, darhol baholash bilan. O‘qituvchi uchun u shundoq ishlaydi:',
       't1': 'Har talabaga bitta akkaunt',
       'b1': 'Talaba bir marta telefon raqami bilan ro‘yxatdan o‘tadi — saytdagi har bir test uni taniydi. Ism yozib o‘tirish yo‘q, soxta ism yo‘q.',
       't2': 'Har bir natija saqlanadi',
       'b2': 'Tugatilgan har test talabaning ismi va raqami bilan saqlanadi — kim nimani, qachon ishlaganini doim bilasiz.',
       't3': '100+ bepul test va arzon mock',
       'b3': 'Listening, Reading, Cambridge 21, Writing va Speaking lablari — bepul. To‘liq kompyuterda o‘tkaziladigan mocklar 10 000 so‘m.',
       't4': 'Sinf hisobotlari',
       'b4': 'Bizga yozing — guruhingiz uchun natijalar ko‘rinishini sozlab beramiz: kunlik faollik, ballar, seriyalar.',
       'cta': 'Telegramda yozing', 'ctaSub': '@flarestamina kanali',
     },
     body='''
<section class="page-head">
  <div class="wrap narrow">
    <p class="kicker" data-i18n="kicker">For teachers</p>
    <h1 data-i18n="h1">Bring your class. See every result.</h1>
    <p class="lede" data-i18n="lede">Flarestamina is a free IELTS practice ecosystem built in Uzbekistan — 100+ real-format tests with instant scoring. For teachers it works out of the box:</p>
    <div class="rail"></div>
  </div>
</section>

<section>
  <div class="wrap narrow">
    <div class="grid c2">
      <div class="card reveal"><p class="kicker">01</p><h3 style="margin-top:.75rem;font-size:1.1rem" data-i18n="t1">One account per student</h3><p class="muted" style="margin-top:.5rem;font-size:.9rem;line-height:1.7" data-i18n="b1">Students register once with a phone number — every test on the site recognizes them. No name-typing, no fake names.</p></div>
      <div class="card reveal"><p class="kicker">02</p><h3 style="margin-top:.75rem;font-size:1.1rem" data-i18n="t2">Every result, tracked</h3><p class="muted" style="margin-top:.5rem;font-size:.9rem;line-height:1.7" data-i18n="b2">Each finished test is saved with the student’s name and phone — you always know who practised what, and when.</p></div>
      <div class="card reveal"><p class="kicker">03</p><h3 style="margin-top:.75rem;font-size:1.1rem" data-i18n="t3">100+ free tests, affordable mocks</h3><p class="muted" style="margin-top:.5rem;font-size:.9rem;line-height:1.7" data-i18n="b3">Listening, Reading, Cambridge 21, Writing and Speaking labs — free. Full computer-delivered mocks at 10,000 UZS.</p></div>
      <div class="card reveal"><p class="kicker">04</p><h3 style="margin-top:.75rem;font-size:1.1rem" data-i18n="t4">Class reports</h3><p class="muted" style="margin-top:.5rem;font-size:.9rem;line-height:1.7" data-i18n="b4">Message us and we’ll set up a results view for your group — daily activity, scores, streaks.</p></div>
    </div>

    <div class="card reveal" style="margin-top:2rem;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:1rem">
      <div>
        <b style="font-weight:500;display:block" data-i18n="cta">Message us on Telegram</b>
        <small class="muted" data-i18n="ctaSub">@flarestamina channel</small>
      </div>
      <a class="btn solid" href="https://t.me/flarestamina" target="_blank" rel="noopener">Telegram →</a>
    </div>
  </div>
</section>
''')


# ─────────────────────────────────────────────────────── privacy
page('privacy/index.html',
     title='Privacy — Flarestamina',
     desc='What Flarestamina stores, where it lives, and how to delete it. Short and honest.',
     canonical='https://flarestamina.com/privacy/',
     og='https://flarestamina.com/og-image.png',
     current='/privacy/',
     uz={
       'kicker': 'Maxfiylik', 'h1': 'Qisqa va halol.', 'updated': 'Oxirgi yangilanish: 11-iyul, 2026',
       'h2a': 'Nimani saqlaymiz',
       'l1': '<strong>FS Akkauntingiz:</strong> ism, familiya, telefon raqam (bu sizning login ID’ingiz).',
       'l2': '<strong>Mashq natijalaringiz:</strong> test nomi, ball va sana — progressingiz istalgan qurilmada siz bilan bo‘lsin.',
       'l3': '<strong>O‘zingiz yuborgan narsalar:</strong> Writing Lab’dagi esselar va Speaking Lab’dagi ovozli yozuvlar — o‘qituvchi izoh bera olishi uchun.',
       'h2b': 'Qayerda turadi',
       'l4': 'Akkauntlar va natijalar — <strong>Google Firebase</strong>; natijalarning nusxasi o‘qituvchi kuzatuvi uchun ishlatiladigan yopiq <strong>Google Sheet</strong>ga tushadi.',
       'l5': 'Speaking yozuvlari — <strong>Supabase Storage</strong>.',
       'l6': 'Full Mock uchun to‘lov qo‘lda karta o‘tkazmasi orqali — <strong>karta ma’lumotlarini biz ko‘rmaymiz va saqlamaymiz</strong>.',
       'h2c': 'Nimani hech qachon qilmaymiz',
       'l7': 'Ma’lumotlaringizni hech kimga sotmaymiz va bermaymiz.',
       'l8': 'Reklama yo‘q, treker yo‘q. Statistika vositamiz (<strong>GoatCounter</strong>) <strong>cookie ishlatmaydi</strong> va shaxsiy hech narsa saqlamaydi.',
       'l9': 'Parolingizni Google Firebase boshqaradi — biz uni o‘qiy olmaymiz.',
       'h2d': 'Ma’lumotlaringizni o‘chirish',
       'l10': 'Ro‘yxatdan o‘tgan raqamingizdan Telegramda <a href="https://t.me/mrbmp13" target="_blank" rel="noopener">@mrbmp13</a>ga yozing — akkauntingizni va har bir natijani 48 soat ichida o‘chiramiz.',
     },
     body='''
<section class="page-head">
  <div class="wrap narrow">
    <p class="kicker" data-i18n="kicker">Privacy</p>
    <h1 data-i18n="h1">Short and honest.</h1>
    <p class="lede mono" style="font-size:.8rem" data-i18n="updated">Last updated: 11 July 2026</p>
    <div class="rail"></div>
  </div>
</section>

<section>
  <div class="wrap narrow">
    <div class="prose">
      <h2 data-i18n="h2a">What we store</h2>
      <ul>
        <li data-i18n-html="l1"><strong>Your FS Account:</strong> first name, last name, phone number (this is your login ID).</li>
        <li data-i18n-html="l2"><strong>Your practice results:</strong> test name, score and date — so your progress follows you on any device.</li>
        <li data-i18n-html="l3"><strong>What you submit yourself:</strong> essays in the Writing Lab and voice recordings in the Speaking Lab, so a teacher can give feedback.</li>
      </ul>

      <h2 data-i18n="h2b">Where it lives</h2>
      <ul>
        <li data-i18n-html="l4">Accounts and results — <strong>Google Firebase</strong>; a copy of results goes to a private <strong>Google Sheet</strong> used for teacher tracking.</li>
        <li data-i18n-html="l5">Speaking recordings — <strong>Supabase Storage</strong>.</li>
        <li data-i18n-html="l6">Payments for the Full Mock are manual card transfers — <strong>we never see or store card details</strong>.</li>
      </ul>

      <h2 data-i18n="h2c">What we never do</h2>
      <ul>
        <li data-i18n-html="l7">No selling or sharing of your data with anyone.</li>
        <li data-i18n-html="l8">No advertising, no trackers. Our statistics tool (<strong>GoatCounter</strong>) uses <strong>no cookies</strong> and stores nothing personal.</li>
        <li data-i18n-html="l9">Your password is handled by Google Firebase — we can’t read it.</li>
      </ul>

      <h2 data-i18n="h2d">Delete your data</h2>
      <p data-i18n-html="l10">Message <a href="https://t.me/mrbmp13" target="_blank" rel="noopener">@mrbmp13</a> on Telegram from the phone number you registered with — we delete your account and every result within 48 hours.</p>
    </div>
  </div>
</section>
''')


# ─────────────────────────────────────────────────────── 404
page('404.html',
     title='Page not found — Flarestamina',
     desc='That page does not exist. Head back to the practice hub.',
     canonical='https://flarestamina.com/404.html',
     og='https://flarestamina.com/og-image.png',
     robots='noindex, follow',
     uz={'kicker': '404', 'h1': 'Bu sahifa yo‘q.',
         'lede': 'Havola eskirgan yoki manzilda xato bor. Mashq quyidan davom etadi.',
         'b1': 'Mashqqa o‘tish', 'b2': 'Bosh sahifa'},
     body='''
<section class="page-head">
  <div class="wrap narrow">
    <p class="kicker" data-i18n="kicker">404</p>
    <h1 data-i18n="h1">That page isn’t here.</h1>
    <p class="lede" data-i18n="lede">The link is out of date, or the address has a typo. The practice carries on below.</p>
    <div class="rail"></div>
    <div style="display:flex;flex-wrap:wrap;gap:.6rem;margin-top:2rem">
      <a class="btn solid lg" href="/ielts-hub/" data-i18n="b1">Go to the hub</a>
      <a class="btn ghost lg" href="/" data-i18n="b2">Home</a>
    </div>
  </div>
</section>
''')
