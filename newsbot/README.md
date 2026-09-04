# News lenta — avtomat IELTS xabarlari

`/news/lenta/` sahifasini to'ldiradigan quvur. Manbalardan xabar yig'adi,
bir voqea haqidagilarini birlashtiradi, asl maqolani o'qiydi, o'zbekchada
qisqartiradi va statik sahifa qilib chiqaradi.

Ish oqimi: `.github/workflows/newsbot.yml` (har 3 va 6 soatda + qo'lda).

```
collect → filter → enrich → write → build → covers → sitemap → audit → push → indexnow
```

| Qadam | Fayl | Nima qiladi |
|---|---|---|
| collect | `src/collect.mjs` | 13 ta RSS + 8 ta Google News so'rovi → `data/raw.json` |
| filter | `src/filter.mjs` | mavzuga saralaydi, klasterlaydi, ball beradi → `data/clusters.json` |
| enrich | `src/enrich.mjs` | Google News havolasini ochadi, maqola matnini oladi |
| write | `src/write.mjs` | Gemini bilan o'zbekcha xabar yozadi → `data/posts.json` |
| build | `src/build.mjs` | `news/x/<slug>/`, `news/lenta/`, RSS, `news/lenta.json` |
| covers | `covers.py` | har xabarga muqova rasmi (Pillow, paper uslubi) |
| sitemap | `.github/scripts/build_sitemap.py` | `sitemap.xml` + `news-sitemap.xml` |
| audit | `src/audit.mjs` | SEO tekshiruvi (sarlavha, tavsif, canonical, JSON-LD, h1) |
| indexnow | `tools/site/indexnow.py` | Bing va Yandex'ga yangi manzillar |
| telegram | `src/telegram.mjs` | **hozircha o'chirilgan** — ish oqimida izohga olingan |

## Sozlash

`GEMINI_API_KEY` — repo sekreti. Busiz quvur **yiqilmaydi**: `write` qadami
"LLM xatosi" deb logga yozadi va bo'sh o'tadi, ya'ni hech narsa nashr
etilmaydi. Kalit qo'yilgan zahoti keyingi yugurishda o'zi ishlab ketadi.

Ixtiyoriy: `AI_PROVIDER=anthropic` + `ANTHROPIC_API_KEY`.
`TELEGRAM_BOT_TOKEN` va `TELEGRAM_CHAT_ID` allaqachon repoda bor.

## Chegara (eng muhim sozlama)

`MIN_SCORE` — nashr bo'sag'asi, standart **30**. Actions'da "Run workflow"
tugmasi orqali bir yugurishga o'zgartirsa bo'ladi.

IELTS yangiligi kam: Google News'ning "IELTS" so'rovi bir haftada atigi
**5 ta** natija beradi va ularning ko'pi "Study in Italy without IELTS"
turidagi SEO axlati. Shuning uchun chegara qattiq: **hech narsa chiqmagani
yomon xabar chiqqanidan afzal**.

2026-09-04 dagi o'lchov: 295 xom xabar → 27 tasi mavzuga oid → 22 klaster →
30+ ball olgani **bitta** (O'zbekistonda IELTS narxi oshgani, 66 ball).
Keyingi eng yuqorisi 25 ball edi. Ya'ni bo'sag'a haqiqiy xabarni axlatdan
aniq ajratyapti.

Chegarani pasaytirsangiz lenta to'ladi, lekin sifat tushadi.

## Duch kelingan tuzoqlar

- **`ielts.org` da RSS yo'q** (404). Cambridge English va British Council'da
  ham. Yangi feed qo'shishdan oldin `curl` bilan sinang.
- **Google News havolasi asl maqolaga bormaydi.** `enrich.mjs` uni ochadi:
  sahifadagi `data-n-a-sg` va `data-n-a-ts` bilan Google'ning ichki
  `batchexecute` endpointidan so'raladi. Busiz modelda sarlavhadan boshqa
  hech narsa bo'lmaydi va xulosa to'qib chiqarilgan bo'lardi.
- **Savol belgisi bo'yicha rad etmang.** Bu qoida bir marta yugurishdagi eng
  qimmatli xabarni ("IELTS test fee increased: how much does it cost now?")
  axlatga chiqargan. O'zbek nashrlari haqiqiy yangilikni ham savol shaklida
  yozadi.
- **O'zbek kirill matnini unutmang.** UzA va Gazeta.uz kirillda yozadi;
  lotincha lug'at ularning 155 xabaridan 151 tasiga 0 ball bergan edi.
- **CSS tokeni `--border`, `--hair` emas.** Noto'g'ri nom bilan chegara
  umuman chizilmaydi.
- **Manba obro'sini mavzudan ustun qo'ymang.** ICEF Monitor va The PIE News
  universitet va agentlarga yozadi ("commencements", "market outlook") —
  IELTS'ga aloqador, lekin o'quvchi uchun yangilik emas. `TRADE` naqshi
  shularga jarima beradi.
- Sahifada ham, JSON-LD da ham muallif **tashkilot**, odam emas. Bu
  xabarlarni odam yozmagan.

## Qo'lda ishga tushirish

```bash
node newsbot/src/collect.mjs
node newsbot/src/filter.mjs        # MIN_SCORE=25 node ... — bo'sag'ani o'zgartirish
node newsbot/src/enrich.mjs
GEMINI_API_KEY=... node newsbot/src/write.mjs
node newsbot/src/build.mjs
python3 newsbot/covers.py
```

## SEO — nima avtomat, nima yo'q

**Avtomat:**
- `sitemap.xml` har nashrdan keyin qayta quriladi (ilgari kuniga bir marta edi).
- `news-sitemap.xml` — Google News formati, faqat oxirgi 48 soatdagi xabarlar.
  Bo'sh bo'lishi normal. `robots.txt` da ikkala sitemap ham ko'rsatilgan.
- IndexNow — Bing, Yandex, Seznam, Naver bir necha daqiqada oladi.
  Kalit fayli `/25435284112beaba0983abf75c9f8164.txt` — **o'chirmang**.
- RSS: `/news/lenta/feed.xml`, `/news/` sahifasining `<head>` idan topiladi.
- JSON-LD: har xabarda `NewsArticle` + `BreadcrumbList`, lenta sahifasida
  `CollectionPage` + `ItemList`.
- `src/audit.mjs` har yugurishda sarlavha va tavsif uzunligini, canonical'ni,
  JSON-LD'ni, h1 sonini va ichki havolalarni tekshiradi.

**Avtomat EMAS (va bo'lmaydi):**
- Google Search Console'da "indekslashni so'rash" tugmasi. Uni dastur bilan
  bosish Google qoidasiga zid, Indexing API esa faqat ish e'lonlari va
  translyatsiyalar uchun. To'g'ri yo'l — sitemap (Google o'zi qayta o'qiydi)
  va IndexNow. Sitemap bir marta yuborilsa yetadi.
- Google Publisher Center: o'zbek tili ro'yxatda yo'q.

## GoatCounter

Kod `flarestamina`, har sahifada BITTA skript (dublikat pageview'ni
ikkilantiradi — bu xato ilgari bo'lgan). Hodisalar:

| Hodisa | Qachon |
|---|---|
| `lenta-manba` | o'quvchi asl manbaga o'tdi |
| `lenta-cta` | mashq sahifasiga o'tdi |
| `lenta-rss` | RSS ga o'tdi |
| `lenta-filtr-<kat>` | lentada filtr bosildi |

Sahifa ko'rish lentaning ishlayotganini ko'rsatmaydi — o'quvchi manbaga yoki
mashqqa o'tdimi, muhimi shu.

## Bog'liq joylar

- `news/index.html` — `<!-- LENTA:START -->` / `<!-- LENTA:END -->` orasini
  `build.mjs` yozadi. Qo'lda tahrirlamang.
- `news/news.css` — lenta uslublari fayl oxirida.
- `.github/workflows/sitemap.yml` — `news/lenta.json` dan manzillarni oladi.
