// build.mjs — data/posts.json dan statik sahifalarni quradi.
//
// Chiqish:
//   news/x/<slug>/index.html   har bir avtomat xabar
//   news/lenta/index.html      lenta ro'yxati
//   news/lenta/feed.xml        RSS
//   news/lenta.json            sitemap ish oqimi shu fayldan o'qiydi
//   news/index.html            ichidagi LENTA belgilari orasiga so'nggi xabarlar

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { SITE, esc, head, footer, humanDate, isoDay, BOT_NOTE, CATEGORY_UZ } from "./shell.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const REPO = join(ROOT, "..");
const OUT = join(REPO, "news");

// Chiqishdagi VAQT MUHRLARI kontentdan kelib chiqishi shart, joriy vaqtdan
// emas. Ilgari lenta.json ichida `generated: new Date()` turardi va shu
// tufayli har yugurish — yangi xabar bo'lmasa ham — fayllarni o'zgartirib,
// commit qilar edi: git tarixi shishardi, GitHub Pages bekorga qayta
// qurilardi va bir vaqtda ishlagan ish oqimlari to'qnashardi.
const FALLBACK = "2026-09-04T00:00:00.000Z";   // lenta bo'sh bo'lgandagi sana

const KEEP = 120;          // lentada saqlanadigan xabarlar soni
const ON_NEWS_INDEX = 4;   // /news/ bosh sahifasiga chiqadigan soni

// Har bir kategoriya uchun saytning o'z sahifalari. Avtomat xabar tashqi
// havola bilan tugab qolmasin — o'quvchi shu yerdan foydali narsaga o'tsin.
const RELATED = {
  "exam-update": [
    ["/ielts-hub/", "100+ bepul IELTS mock test"],
    ["/convert/", "IELTS ↔ CEFR ↔ Multilevel konverteri"],
    ["/news/ielts-qayerda-topshiriladi/", "IELTS qayerda topshiriladi: 14 ta shahar"],
  ],
  "fees": [
    ["/news/ielts-narxi-2026/", "IELTS narxi 2026 — O‘zbekistonda"],
    ["/convert/", "Ball konverteri"],
    ["/ielts-hub/", "Bepul mock testlar"],
  ],
  "deadline": [
    ["/deadlines/", "Grant muddatlari — jonli sanoq"],
    ["/news/", "Barcha grant e’lonlari"],
    ["/plan/", "O‘quv rejasi generatori"],
  ],
  "guide": [
    ["/plan/", "Shaxsiy o‘quv rejasi"],
    ["/ielts-hub/", "Bepul mock testlar"],
    ["/writing/", "Writing Lab"],
  ],
};

const CTA = `<a class="cta-card" href="/ielts-hub/"><span><span class="t">Imtihonga tayyorlaning</span><span class="s">100+ bepul IELTS mock test, natija darhol chiqadi</span></span><span class="btn solid">Boshlash</span></a>`;

function postPage(p) {
  const path = `/news/x/${p.slug}/`;
  const desc = p.summary.length > 155 ? `${p.summary.slice(0, 152)}…` : p.summary;
  const date = isoDay(p.published);
  const cover = `/news/x/${p.slug}/cover.png`;

  const jsonld = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "NewsArticle",
        "@id": `${SITE}${path}#article`,
        headline: p.title,
        description: desc,
        datePublished: p.published,
        dateModified: p.created,
        inLanguage: "uz",
        mainEntityOfPage: `${SITE}${path}`,
        image: `${SITE}${cover}`,
        // Muallif — tashkilot. Bu xabarni odam yozmagan, shuning uchun uni
        // odamga bog'lash noto'g'ri bo'lardi.
        author: { "@type": "Organization", "@id": `${SITE}/#org`, name: "Flarestamina" },
        publisher: { "@id": `${SITE}/#org` },
        isBasedOn: p.source.url,
        citation: [p.source.url, ...p.also.map((a) => a.url)],
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Flarestamina", item: `${SITE}/` },
          { "@type": "ListItem", position: 2, name: "Yangiliklar", item: `${SITE}/news/` },
          { "@type": "ListItem", position: 3, name: "Lenta", item: `${SITE}/news/lenta/` },
          { "@type": "ListItem", position: 4, name: p.title, item: `${SITE}${path}` },
        ],
      },
    ],
  };

  const points = p.points.length
    ? `<div class="facts"><h2>Qisqacha</h2><ul>${p.points.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>`
    : "";

  // Google News havolasi asl maqolaga bormaydi (JS redirect), shuning uchun
  // bunday manba havola qilinmaydi — faqat nashr nomi ko'rsatiladi.
  const src = p.source.indirect
    ? `<p class="source">Manba: ${esc(p.source.name)} <span class="dot">·</span> Google News orqali topildi</p>`
    : `<p class="source">Manba: <a href="${esc(p.source.url)}" rel="noopener nofollow" target="_blank">${esc(p.source.name)}</a> — ${esc(p.source.title)}</p>`;

  const also = p.also.length
    ? `<p class="source">Boshqa nashrlar:</p><ul class="also-list">${p.also
        .map((a) => `<li><a href="${esc(a.url)}" rel="noopener nofollow" target="_blank">${esc(a.name)}</a></li>`)
        .join("")}</ul>`
    : "";

  const related = (RELATED[p.category] || RELATED.guide)
    .map(([href, label]) => `<li><a href="${href}">${esc(label)}</a></li>`).join("");

  return `${head({ title: p.title, description: desc, path, image: cover, published: p.published, modified: p.created, jsonld })}
<main id="content">
<div class="wrap narrow" style="padding-top:2.5rem">
<article class="post">
  <p class="crumbs"><a href="/news/lenta/">← lenta</a></p>
  <h1>${esc(p.title)}</h1>
  <div class="post-meta">
    <span class="chip ${p.category}">${CATEGORY_UZ[p.category] || p.category}</span>
    <time datetime="${date}">${humanDate(p.published)}</time>
    <span class="bot-badge">avtomat</span>
  </div>

  <div class="prose">
    ${points}
    <p>${esc(p.summary)}</p>
    ${src}
    ${also}
    ${BOT_NOTE}

    <h2>Shu mavzuda saytda</h2>
    <ul>${related}</ul>

    ${CTA}

    <div class="post-nav"><a class="chip" href="/news/lenta/">← Butun lenta</a> <a class="chip" href="/news/">Batafsil maqolalar</a></div>
  </div>
</article>
</div>
</main>
${footer()}`;
}

function card(p) {
  const date = isoDay(p.published);
  return `  <a class="post-card" href="/news/x/${p.slug}/" data-cat="${p.category}">
    <img class="thumb" src="/news/x/${p.slug}/cover.png" alt="${esc(p.title)}" width="1200" height="630" loading="lazy" decoding="async">
    <div class="meta"><span class="chip">${CATEGORY_UZ[p.category] || p.category}</span><time datetime="${date}">${humanDate(p.published)}</time><span class="dot">·</span><span class="bot-badge">avtomat</span></div>
    <h2>${esc(p.title)}</h2>
    <p class="sum">${esc(p.summary)}</p>
    <span class="src">${esc(p.source.name)}</span>
  </a>`;
}

function lentaPage(posts) {
  const desc = "IELTS, til imtihonlari, viza talablari va grant muddatlari — manbalardan avtomat yig'ilib, o'zbekchada qisqartirilgan xabarlar lentasi.";
  const jsonld = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "@id": `${SITE}/news/lenta/#page`,
    name: "IELTS yangiliklari lentasi",
    description: desc,
    inLanguage: "uz",
    isPartOf: { "@id": `${SITE}/#website` },
    mainEntity: {
      "@type": "ItemList",
      itemListElement: posts.slice(0, 30).map((p, i) => ({
        "@type": "ListItem", position: i + 1, url: `${SITE}/news/x/${p.slug}/`, name: p.title,
      })),
    },
  };

  const cats = [...new Set(posts.map((p) => p.category))];
  const chips = ['<button class="active" data-f="all">Hammasi</button>']
    .concat(cats.map((c) => `<button data-f="${c}">${CATEGORY_UZ[c] || c}</button>`)).join("\n  ");

  const body = posts.length
    ? posts.map(card).join("\n\n")
    : `<div class="lenta-empty"><p>Hozircha yangi xabar yo‘q.</p><p>Lenta har uch soatda yangilanadi va faqat haqiqiy o‘zgarishlarni chiqaradi — bo‘sh kun bo‘lishi normal holat.</p></div>`;

  return `${head({ title: "IELTS yangiliklari lentasi", description: desc, path: "/news/lenta/", jsonld })}
<main id="content">
<section class="hero wrap">
  <p class="kicker">Manbali · Sanali · Avtomat</p>
  <h1>Lenta</h1>
  <p class="sub">IELTS, til imtihonlari, viza talablari va grantlar. Har uch soatda yangilanadi.</p>
</section>

<div class="chipbar wrap" role="tablist" aria-label="Filtr">
  ${chips}
  <span class="chip-sep" aria-hidden="true"></span>
  <a class="btn ghost" href="/news/">Batafsil maqolalar</a>
</div>

<main class="list wrap" id="lenta-list">
${body}
</main>

<section class="wrap" style="margin:2rem auto 3rem">
  <div class="bot-note">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="8" width="16" height="12" rx="2"/><path d="M12 8V4M9 14h.01M15 14h.01"/></svg>
    <span>Lentadagi xabarlarni avtomat tizim ochiq manbalardan yig'ib, o'zbekchada qisqartiradi va har birida manbani ko'rsatadi. Qo'lda yozilgan batafsil maqolalar <a href="/news/">/news/</a> sahifasida. Rasmiy narx va muddatlarni doim manbadan tekshiring.</span>
  </div>
  <p style="margin-top:1rem"><a class="chip" href="/news/lenta/feed.xml">RSS</a> <a class="chip" href="https://t.me/flarestamina" target="_blank" rel="noopener">Telegram</a></p>
</section>
</main>
<script>
(function () {
  var bar = document.querySelector('.chipbar');
  var cards = [].slice.call(document.querySelectorAll('#lenta-list .post-card'));
  if (!bar) return;
  bar.addEventListener('click', function (e) {
    var b = e.target.closest('button[data-f]');
    if (!b) return;
    bar.querySelectorAll('button[data-f]').forEach(function (x) { x.classList.toggle('active', x === b); });
    var f = b.dataset.f;
    cards.forEach(function (c) { c.hidden = f !== 'all' && c.dataset.cat !== f; });
  });
})();
</script>
${footer()}`;
}

function feed(posts) {
  const items = posts.slice(0, 40).map((p) => `    <item>
      <title>${esc(p.title)}</title>
      <link>${SITE}/news/x/${p.slug}/</link>
      <guid isPermaLink="true">${SITE}/news/x/${p.slug}/</guid>
      <pubDate>${new Date(p.published).toUTCString()}</pubDate>
      <category>${esc(CATEGORY_UZ[p.category] || p.category)}</category>
      <description>${esc(p.summary)}</description>
    </item>`).join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Flarestamina — IELTS yangiliklari lentasi</title>
    <link>${SITE}/news/lenta/</link>
    <atom:link href="${SITE}/news/lenta/feed.xml" rel="self" type="application/rss+xml"/>
    <description>IELTS, til imtihonlari, viza va grant xabarlari o'zbek tilida.</description>
    <language>uz</language>
    <lastBuildDate>${new Date(posts[0]?.published || FALLBACK).toUTCString()}</lastBuildDate>
${items}
  </channel>
</rss>
`;
}

// /news/ bosh sahifasidagi belgilar orasini almashtiradi. Belgilar yo'q bo'lsa
// hech narsa qilmaydi — qo'lda yozilgan sahifani buzib qo'ymaslik uchun.
async function injectIntoNewsIndex(posts) {
  const path = join(OUT, "index.html");
  let html;
  try { html = await readFile(path, "utf8"); } catch { return false; }

  const START = "<!-- LENTA:START -->";
  const END = "<!-- LENTA:END -->";
  const a = html.indexOf(START);
  const b = html.indexOf(END);
  if (a === -1 || b === -1 || b < a) {
    console.log("  . /news/index.html da LENTA belgilari yo'q — o'tkazib yuborildi");
    return false;
  }

  const strip = posts.slice(0, ON_NEWS_INDEX).map((p) => `      <a class="lenta-row" href="/news/x/${p.slug}/">
        <time datetime="${isoDay(p.published)}">${humanDate(p.published)}</time>
        <span class="t">${esc(p.title)}</span>
      </a>`).join("\n");

  const block = posts.length ? `${START}
<section class="wrap lenta-strip">
  <div class="lenta-head">
    <h2>Lenta <span class="bot-badge">avtomat</span></h2>
    <a href="/news/lenta/">hammasi →</a>
  </div>
  <div class="lenta-rows">
${strip}
  </div>
</section>
${END}` : `${START}${END}`;

  const next = html.slice(0, a) + block + html.slice(b + END.length);
  if (next === html) return false;
  await writeFile(path, next);
  return true;
}

async function main() {
  let posts = [];
  try { posts = JSON.parse(await readFile(join(ROOT, "data/posts.json"), "utf8")); } catch {}

  posts.sort((a, b) => b.published.localeCompare(a.published));
  posts = posts.slice(0, KEEP);

  for (const p of posts) {
    const dir = join(OUT, "x", p.slug);
    await mkdir(dir, { recursive: true });
    await writeFile(join(dir, "index.html"), postPage(p));
  }

  await mkdir(join(OUT, "lenta"), { recursive: true });
  await writeFile(join(OUT, "lenta/index.html"), lentaPage(posts));
  await writeFile(join(OUT, "lenta/feed.xml"), feed(posts));

  // sitemap.yml shu fayldan o'qiydi.
  await writeFile(join(OUT, "lenta.json"), JSON.stringify({
    note: "Avtomat lenta indeksi. newsbot/src/build.mjs yozadi — qo'lda tahrirlamang.",
    updated: (posts[0]?.published || FALLBACK).slice(0, 10),
    posts: posts.map((p) => ({
      slug: p.slug, title: p.title, date: isoDay(p.published), category: p.category,
    })),
  }, null, 2));

  const injected = await injectIntoNewsIndex(posts);
  console.log(`Qurildi: ${posts.length} ta sahifa, lenta, RSS${injected ? ", /news/ bosh sahifasi yangilandi" : ""}`);
}

if (process.argv[1]?.endsWith("build.mjs")) main();
