"""Builds the tool pages. Their logic and data tables are carried over from
the pages they replace; only the shell and the class names changed.

The one deliberate behaviour change is language: these pages each had their
own toggle writing `fs_lang`. They now follow the site-wide toggle in
paper.js, so a student picks a language once and it holds everywhere.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import shell

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
HERE = os.path.dirname(__file__)


def read(name):
    return open(os.path.join(HERE, name), encoding='utf-8').read().strip()


def write(rel, html):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(html)
    print('  ✓', rel, f'({len(html)} bytes)')


def page(rel, *, title, desc, canonical, og, uz, body, ld='', style='', logic='', current=''):
    u = dict(shell.CHROME_UZ); u.update(uz)
    extra = ''
    if ld:
        extra += '<script type="application/ld+json">\n' + ld + '\n</script>\n'
    if style:
        extra += '<style>\n' + style.strip() + '\n</style>\n'
    scripts = ('<script>\n' + logic.strip() + '\n</script>\n') if logic else ''
    html = (shell.head(title, desc, canonical, og, extra_head=extra)
            + shell.header(current) + body
            + shell.footer(json.dumps(u, ensure_ascii=False, indent=1), extra_scripts=scripts))
    write(rel, html)


# ─────────────────────────────────────────────────────── /convert/
page('convert/index.html',
     title='IELTS ↔ CEFR ↔ Multilevel ↔ TOEFL converter — Flarestamina',
     desc='Pick your IELTS band and see the CEFR level, Uzbekistan Multilevel equivalent, TOEFL iBT and Duolingo scores, plus what it earns at DTM.',
     canonical='https://flarestamina.com/convert/',
     og='https://flarestamina.com/convert/og.png?v=2',
     ld=read('convert-ld.json'),
     logic=read('convert-logic.js'),
     uz={'lnkCalcT': 'Band kalkulyator', 'lnkNewsT': 'IELTS yangiliklari',
         'ctaBtn': 'Mashqni boshlash'},
     style='''
.bands{display:flex;flex-wrap:wrap;gap:.45rem;margin-bottom:1.75rem}
.bands button{display:inline-flex;align-items:center;justify-content:center;min-width:3.4rem;height:2.4rem;padding:0 .8rem;border-radius:999px;border:1px solid var(--border);font-family:var(--mono);font-size:.85rem;color:var(--muted);transition:color .15s,border-color .15s,background .15s}
.bands button:hover{color:var(--fg);border-color:var(--border-strong)}
.bands button.on{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.results{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin-bottom:1.25rem}
@media(min-width:760px){.results{grid-template-columns:repeat(4,1fr)}}
.rcard{border-radius:6px;background:var(--surface);box-shadow:var(--card);padding:1.1rem 1.15rem}
.rcard .lab{font-family:var(--mono);font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;color:var(--subtle)}
.rcard .val{margin-top:.3rem;font-size:1.75rem;font-weight:500;letter-spacing:-.04em;font-variant-numeric:tabular-nums}
.rcard .sub{margin-top:.15rem;font-size:.75rem;color:var(--muted)}
.dtm-note{border-radius:6px;background:var(--surface);box-shadow:var(--card);padding:1rem 1.15rem;font-size:.9rem;line-height:1.65;color:var(--muted)}
.dtm-note b{color:var(--fg);font-weight:500}
.dtm-note a{border-bottom:1px solid var(--border-strong)}
.sec{margin-top:3.5rem}
.sec h2{font-size:1.4rem;margin-bottom:1rem}
table.cv tr.hl td{background:color-mix(in oklab,var(--fg) 4%,transparent)}
.cv-note{margin-top:.9rem;font-size:.78rem;line-height:1.7;color:var(--subtle)}
.faq details{border-bottom:1px solid var(--border)}
.faq details:first-child{border-top:1px solid var(--border)}
.faq summary{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:1.15rem 0;cursor:pointer;font-weight:500;font-size:.98rem;list-style:none}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font-family:var(--mono);color:var(--subtle);flex:none}
.faq details[open] summary::after{content:"−"}
.faq p{padding:0 0 1.15rem;max-width:44rem;color:var(--muted);font-size:.9rem;line-height:1.7}
.faq p a{border-bottom:1px solid var(--border-strong)}
.faq strong{color:var(--fg);font-weight:500}
.cta-card{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:1rem;margin-top:3rem;border-radius:6px;background:var(--surface);box-shadow:var(--card);padding:1.35rem 1.4rem}
.cta-card .t{font-weight:500;letter-spacing:-.02em}
.cta-card .s{margin-top:.25rem;font-size:.85rem;color:var(--muted)}
.more{margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:.5rem}
''',
     body='''
<section class="page-head">
  <div class="wrap">
    <p class="kicker" data-k="kicker">Free · No sign-up · 2026</p>
    <h1>IELTS ↔ CEFR ↔ Multilevel ↔ TOEFL</h1>
    <p class="lede" data-k="lead">Pick your IELTS band — instantly see the CEFR level, Uzbekistan Multilevel equivalent, TOEFL iBT and Duolingo scores, plus what it earns you at DTM.</p>
    <div class="rail"></div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="bands" id="bands" role="group" aria-label="IELTS band"></div>

    <div class="results">
      <div class="rcard"><div class="lab">CEFR</div><div class="val" id="r-cefr">B2</div><div class="sub" data-k="cefrSub">European level</div></div>
      <div class="rcard"><div class="lab">Multilevel</div><div class="val" id="r-ml">B2</div><div class="sub" data-k="mlSub">national certificate</div></div>
      <div class="rcard"><div class="lab">TOEFL iBT</div><div class="val" id="r-toefl">79–93</div><div class="sub" data-k="toeflSub">official ETS table</div></div>
      <div class="rcard"><div class="lab">Duolingo</div><div class="val" id="r-det">115–120</div><div class="sub" data-k="detSub">approximate</div></div>
    </div>

    <div class="dtm-note" id="dtm-note"></div>

    <section class="sec">
      <h2 data-k="tblH">Full comparison table</h2>
      <div class="tbl-scroll">
        <table class="cv">
          <thead><tr><th>IELTS</th><th>CEFR</th><th>Multilevel</th><th>TOEFL iBT</th><th>Duolingo ≈</th><th data-k="thDtm">DTM (foreign language)</th></tr></thead>
          <tbody>
            <tr><td>8.5 – 9.0</td><td>C2</td><td>C1*</td><td>115 – 120</td><td>155 – 160</td><td>max</td></tr>
            <tr><td>7.0 – 8.0</td><td>C1</td><td>C1</td><td>94 – 114</td><td>125 – 150</td><td>max</td></tr>
            <tr class="hl"><td>5.5 – 6.5</td><td>B2</td><td>B2</td><td>46 – 93</td><td>95 – 120</td><td><strong>max (93.0 / 63.0)</strong></td></tr>
            <tr><td>4.0 – 5.0</td><td>B1</td><td>B1</td><td>32 – 45</td><td>55 – 90</td><td>75% (2026)</td></tr>
          </tbody>
        </table>
      </div>
      <p class="cv-note" data-k="tblNote">* Multilevel issues C1 as its highest level. IELTS↔CEFR per ielts.org; IELTS↔TOEFL per the ETS linking study; Duolingo is approximate — verify in the official converter. DTM privileges apply to valid (unexpired) certificates.</p>
    </section>

    <section class="sec">
      <h2 data-k="faqH">Frequently asked questions</h2>
      <div class="faq">
        <details><summary data-k="q1">What level is IELTS 6.5?</summary><p data-k="a1">IELTS 5.5–6.5 officially corresponds to CEFR <strong>B2</strong>. From 7.0 it counts as C1. Many universities abroad ask for exactly 6.5 — the top of B2 — for a master’s.</p></details>
        <details><summary data-k="q2">Multilevel B2 equals which IELTS band?</summary><p data-k="a2">Multilevel is a CEFR-based national exam. A B2 certificate matches IELTS <strong>5.5–6.5</strong>, and C1 matches IELTS <strong>7.0–8.0</strong>. For the DTM privilege the two carry equal weight.</p></details>
        <details><summary data-k="q3">What do I need for the maximum DTM score?</summary><p data-k="a3">A valid <strong>B2+ certificate</strong> (IELTS 5.5+, Multilevel B2+) gives the maximum foreign-language score without sitting the exam: 93.0 as first subject, 63.0 as second. From 2026 B1 gives 75% of the maximum. Details: <a href="/news/ielts-dtm-maksimal-ball-2026/">the DTM rules article</a>.</p></details>
        <details><summary data-k="q4">TOEFL 90 — what IELTS band?</summary><p data-k="a4">By the official ETS table, TOEFL iBT 79–93 = IELTS <strong>6.5</strong>. TOEFL 94–101 = IELTS 7.0. Use this table to compare which test suits you when applying.</p></details>
        <details><summary data-k="q5">Does the Duolingo test replace IELTS?</summary><p data-k="a5">Partly: 5,500+ universities (mostly US) accept it and it costs about $65. But UK visa routes and most state scholarships (El-Yurt Umidi, Chevening) still ask for IELTS. Roughly DET 115–120 ≈ IELTS 6.5.</p></details>
      </div>
    </section>

    <a class="cta-card" href="/ielts-hub/">
      <span><span class="t" data-k="ctaT">Know your level? Now raise the band</span><span class="s" data-k="ctaS">100+ free IELTS mocks — real format, instant band scores</span></span>
      <span class="btn solid" data-i18n="ctaBtn">Start practicing</span>
    </a>

    <div class="more">
      <a class="chip" href="/band-calculator/" data-i18n="lnkCalcT">Band calculator</a>
      <a class="chip" href="/news/" data-i18n="lnkNewsT">IELTS news</a>
    </div>
  </div>
</section>
''')

print('done')


# ─────────────────────────────────────────────────────── /deadlines/
page('deadlines/index.html',
     title='Scholarship deadlines 2026–2027 — Flarestamina',
     desc='Every major scholarship for students in Uzbekistan on one page, with live day counters and a preparation guide for each.',
     canonical='https://flarestamina.com/deadlines/',
     og='https://flarestamina.com/deadlines/og.png?v=2',
     ld=read('deadlines-ld.json'),
     logic=read('deadlines-logic.js'),
     uz={'ctaBtn': 'Mashqni boshlash'},
     style='''
#list{display:grid;gap:.75rem}
@media(min-width:820px){#list{grid-template-columns:1fr 1fr}}
.dl{display:flex;align-items:flex-start;gap:1.1rem;border-radius:6px;background:var(--surface);box-shadow:var(--card);padding:1.2rem 1.25rem;transition:box-shadow .2s}
.dl:hover{box-shadow:var(--card-hover)}
.dl.urgent{box-shadow:0 0 0 1px color-mix(in oklab,var(--fg) 30%,transparent)}
.dl .inf{flex:1;min-width:0;order:1}
.dl .count{order:2;flex:none;text-align:right;min-width:3.5rem}
.dl .count .n{font-family:var(--mono);font-size:1.7rem;font-weight:500;letter-spacing:-.04em;line-height:1;font-variant-numeric:tabular-nums}
.dl .count .u{margin-top:.2rem;font-family:var(--mono);font-size:.58rem;letter-spacing:.14em;text-transform:uppercase;color:var(--subtle)}
.dl .inf h2{font-size:1.05rem;font-weight:500;letter-spacing:-.02em;line-height:1.3}
.dl .meta{margin-top:.7rem;display:flex;flex-wrap:wrap;align-items:center;gap:.4rem .85rem;font-size:.8rem}
.dl .meta .st{font-family:var(--mono);font-size:.66rem;letter-spacing:.06em;border:1px solid var(--border);border-radius:999px;padding:.2rem .55rem;color:var(--muted)}
.dl .meta .st.c{color:var(--ok);border-color:color-mix(in oklab,var(--ok) 40%,transparent)}
.dl .meta .st.e{color:var(--warn);border-color:color-mix(in oklab,var(--warn) 40%,transparent)}
.dl .meta .kind{color:var(--subtle);font-family:var(--mono);font-size:.7rem}
.dl .meta a{color:var(--muted);border-bottom:1px solid var(--border)}
.dl .meta a:hover{color:var(--fg);border-bottom-color:var(--fg)}
.note-box{margin-top:2rem;font-size:.8rem;line-height:1.8;color:var(--subtle);max-width:52rem}
.note-box a{border-bottom:1px solid var(--border-strong)}
''',
     body='''
<section class="page-head">
  <div class="wrap">
    <p class="kicker" data-k="kicker">Live countdown · Updates daily</p>
    <h1 data-k="h1">Scholarship deadlines 2026–2027</h1>
    <p class="lede" data-k="lead">Every major scholarship on one page — with live day counters. Each card links to our preparation guide. Bookmark it and check weekly.</p>
    <div class="rail"></div>
  </div>
</section>

<section>
  <div class="wrap">
    <div id="list"></div>
    <p class="note-box" data-k="note"></p>

    <a class="cta-card" href="/ielts-hub/">
      <span><span class="t" data-k="ctaT">Need a higher band before the deadline?</span><span class="s" data-k="ctaS">100+ free IELTS mocks — real format, instant results</span></span>
      <span class="btn solid" data-i18n="ctaBtn">Start practicing</span>
    </a>

    <div class="more">
      <a class="chip" href="/convert/" data-k="lnk1">Score converter →</a>
      <a class="chip" href="/news/" data-k="lnk2">News →</a>
    </div>
  </div>
</section>
''')


# ─────────────────────────────────────────────────────── /plan/
page('plan/index.html',
     title='IELTS study plan generator — Flarestamina',
     desc='Answer four questions and get a week-by-week IELTS study plan, plus an honest read on whether your timeline is realistic.',
     canonical='https://flarestamina.com/plan/',
     og='https://flarestamina.com/plan/og.png?v=2',
     ld=read('plan-ld.json'),
     logic=read('plan-logic.js'),
     uz={'ctaBtn': 'Mashqni boshlash'},
     style='''
.qs{max-width:44rem}
.gen{display:inline-flex;align-items:center;justify-content:center;height:2.9rem;padding:0 1.5rem;border-radius:999px;background:var(--fg);color:var(--bg);font-size:.95rem;font-weight:500;transition:box-shadow .18s}
.gen:hover{box-shadow:0 8px 22px -12px rgb(10 10 10 / .55)}
#result{margin-top:3rem;max-width:48rem}
.verdict{border-radius:6px;background:var(--surface);box-shadow:var(--card);padding:1.25rem 1.35rem;margin-bottom:1.5rem;color:var(--muted);line-height:1.7;font-size:.92rem;border-left:3px solid var(--border-strong)}
.verdict b{display:block;margin-bottom:.4rem;color:var(--fg);font-weight:500;font-size:1.05rem;letter-spacing:-.02em}
.verdict a{color:var(--fg);border-bottom:1px solid var(--border-strong)}
.verdict.ok{border-left-color:var(--ok)}
.verdict.tight{border-left-color:var(--warn)}
.verdict.hard{border-left-color:var(--bad)}
.phase{border-radius:6px;background:var(--surface);box-shadow:var(--card);padding:1.25rem 1.35rem;margin-bottom:.7rem}
.ph-meta{font-family:var(--mono);font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--subtle)}
.phase h3{margin:.5rem 0 .75rem;font-size:1.1rem}
.phase ul{padding-left:1.1rem;color:var(--muted);font-size:.9rem;line-height:1.7}
.phase li+li{margin-top:.4rem}
.pr-actions{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.5rem}
.pr-actions button,.pr-actions a{display:inline-flex;align-items:center;height:2.4rem;padding:0 1.05rem;border-radius:999px;border:1px solid var(--border-strong);font-size:.85rem;font-weight:500;transition:background .15s}
.pr-actions button:hover,.pr-actions a:hover{background:color-mix(in oklab,var(--fg) 5%,transparent)}
@media print{
  .hdr,.sheet,.ftr,.cta-card,.more,.qs,.pr-actions{display:none!important}
  #result{margin:0;max-width:none}
  .phase,.verdict{box-shadow:none;border:1px solid #ddd}
}
''',
     body='''
<section class="page-head">
  <div class="wrap">
    <p class="kicker" data-k="kicker">Free · 30 seconds · Printable</p>
    <h1 data-k="h1">IELTS study plan generator</h1>
    <p class="lede" data-k="lead">Answer four questions and get a week-by-week plan plus an honest verdict: is there enough time, or should you move the exam?</p>
    <div class="rail"></div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="qs">
      <div class="q"><label data-k="q1">1 · Your current band (from a mock)</label><div class="opts" id="qCur"></div></div>
      <div class="q"><label data-k="q2">2 · Target band</label><div class="opts" id="qTgt"></div></div>
      <div class="q"><label data-k="q3">3 · Weeks until the exam</label>
        <div class="opts" id="qWk">
          <button data-v="4">4</button><button data-v="8" class="on">8</button><button data-v="12">12</button><button data-v="16">16</button><button data-v="24">24+</button>
        </div></div>
      <div class="q"><label data-k="q4">4 · Your weakest section</label>
        <div class="opts" id="qWeak">
          <button data-v="listening">Listening</button><button data-v="reading">Reading</button>
          <button data-v="writing" class="on">Writing</button><button data-v="speaking">Speaking</button>
        </div></div>
      <button class="gen" id="go" data-k="gen">Build the plan →</button>
    </div>

    <div id="result" hidden></div>

    <a class="cta-card" href="/ielts-hub/">
      <span><span class="t" data-k="ctaT">A plan does not work without mock tests</span><span class="s" data-k="ctaS">100+ free IELTS mocks — real format, instant band scores</span></span>
      <span class="btn solid" data-i18n="ctaBtn">Start practicing</span>
    </a>

    <div class="more">
      <a class="chip" href="/deadlines/" data-k="l1">Scholarship deadlines →</a>
      <a class="chip" href="/convert/" data-k="l2">Score converter →</a>
      <a class="chip" href="/speaking-topics/" data-k="l3">Speaking topics →</a>
    </div>
  </div>
</section>
''')

