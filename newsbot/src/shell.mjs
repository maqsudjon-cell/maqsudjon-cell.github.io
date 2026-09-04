// shell.mjs — /news/ sahifalari bilan bir xil qobiq (sarlavha, menyu, futer).
//
// Manba: news/_template.html. Shablon o'zgarsa BU FAYL ham yangilanishi kerak,
// aks holda avtomat sahifalar qo'lda yozilganlaridan farq qilib qoladi.

export const SITE = "https://flarestamina.com";

export const esc = (s = "") =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");

const MONTHS_UZ = ["yan", "fev", "mar", "apr", "may", "iyn", "iyl", "avg", "sen", "okt", "noy", "dek"];

export function humanDate(iso) {
  const d = new Date(iso);
  return `${d.getUTCDate()} ${MONTHS_UZ[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

export const isoDay = (iso) => new Date(iso).toISOString().slice(0, 10);

const SPARK = '<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16 1.4 L17.85 13.55 L30.6 16 L17.85 18.45 L16 30.6 L14.15 18.45 L1.4 16 L14.15 13.55 Z"/></svg>';

export function head({ title, description, path, image, published, modified, jsonld }) {
  const url = `${SITE}${path}`;
  const img = image ? `${SITE}${image}` : `${SITE}/news/og.png?v=2`;
  return `<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${url}">
<link rel="alternate" type="application/rss+xml" title="Flarestamina lenta" href="/news/lenta/feed.xml">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:site_name" content="Flarestamina">
<meta property="og:type" content="${published ? "article" : "website"}">
<meta property="og:locale" content="uz_UZ">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${img}">
${published ? `<meta property="article:published_time" content="${published}">` : ""}
${modified ? `<meta property="article:modified_time" content="${modified}">` : ""}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:image" content="${img}">
${jsonld ? `<script type="application/ld+json">\n${JSON.stringify(jsonld, null, 2)}\n</script>` : ""}
<meta name="theme-color" content="#ffffff">
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
<link rel="preload" href="/assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/plex-mono-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/paper.css?v=1">
<link rel="stylesheet" href="/news/news.css?v=3">
<style>
/* Lenta — avtomat yig'ilgan xabarlar. Qo'lda yozilgan postlardan farq qilishi
   uchun kichik belgilar; qolgan hamma narsa news.css tokenlaridan keladi
   (rangni bu yerda qattiq yozmang — yorug' mavzuda matn ko'rinmay qoladi). */
.bot-note{display:flex;gap:.55rem;align-items:flex-start;margin:1.25rem 0 0;padding:.7rem .85rem;
  border:1px solid var(--border);border-radius:10px;font-size:.8rem;line-height:1.5;color:var(--muted)}
.bot-note svg{flex:0 0 auto;margin-top:.15rem;opacity:.7}
.bot-badge{font:500 .68rem/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;
  border:1px solid var(--border);border-radius:999px;padding:.3rem .5rem;color:var(--muted)}
.also-list{margin:.4rem 0 0;padding-left:1.1rem}
.also-list li{margin:.2rem 0}
.lenta-empty{border:1px dashed var(--border);border-radius:12px;padding:2rem;text-align:center;color:var(--muted)}
</style>
</head>
<body>
<a class="skip" href="#content">Asosiy kontentga o‘tish</a>

<header class="hdr">
  <div class="hdr-in">
    <a class="brand" href="/" aria-label="Flarestamina">${SPARK}Flarestamina</a>
    <nav class="hdr-nav" aria-label="Primary">
      <a href="/ielts-hub/">Mashq</a>
      <a href="/#tools">Vositalar</a>
      <a href="/news/" aria-current="page">Yangiliklar</a>
    </nav>
    <span class="hdr-sp"></span>
    <button class="icon-btn" id="tgl" aria-label="Theme"><svg id="ico-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg><svg id="ico-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="display:none"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>
    <div class="hdr-desk">
      <a class="btn solid" href="/ielts-hub/">Bepul boshlash</a>
    </div>
    <button class="icon-btn burger" id="burger" aria-label="Menu" aria-expanded="false" aria-controls="sheet">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
</header>

<div class="sheet" id="sheet">
  <a href="/ielts-hub/">Mashq</a>
  <a href="/#tools">Vositalar</a>
  <a href="/news/">Yangiliklar</a>
  <div class="row">
    <a class="btn solid" href="/ielts-hub/">Bepul boshlash</a>
  </div>
</div>
`;
}

export function footer() {
  return `
<footer class="ftr">
  <div class="wrap">
    <div class="f-grid">
      <div class="f-brand">
        <span class="brand">${SPARK}Flarestamina</span>
        <p>Bepul IELTS Academic mashq. Toshkentda yaratilgan.</p>
      </div>
      <div class="f-col">
        <p>Mashq</p>
        <a href="/ielts-hub/">Practice Hub</a>
        <a href="/tests/">Barcha testlar</a>
        <a href="/ielts-hub/?cat=Listening">Listening</a>
        <a href="/ielts-hub/?cat=Reading">Reading</a>
        <a href="/writing/">Writing Lab</a>
        <a href="/pangea8-speaking/">Speaking Lab</a>
      </div>
      <div class="f-col">
        <p>Vositalar</p>
        <a href="/convert/">Ball konverteri</a>
        <a href="/deadlines/">Muddatlar</a>
        <a href="/plan/">O‘quv rejasi</a>
        <a href="/speaking-topics/">Speaking mavzular</a>
      </div>
      <div class="f-col">
        <p>Kompaniya</p>
        <a href="/founder/">Asoschi</a>
        <a href="/teachers/">O‘qituvchilarga</a>
        <a href="/privacy/">Maxfiylik</a>
        <a href="https://t.me/flarestamina" target="_blank" rel="noopener">Telegram</a>
      </div>
    </div>
    <div class="f-base">
      <span>© <span id="yy"></span> Flarestamina. Talabalar uchun.</span>
      <span>Toshkent, O‘zbekiston</span>
      <span>IELTS, IDP yoki British Council bilan bog‘liq emas.</span>
    </div>
  </div>
</footer>

<script src="/assets/paper.js?v=2"></script>
<script data-goatcounter="https://flarestamina.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
`;
}

// Har bir avtomat sahifada ochiq turadigan izoh. Bu xabarlarni odam yozgan
// deb ko'rsatish — to'qib chiqarish bilan barobar, shuning uchun sahifada ham,
// JSON-LD da ham muallif sifatida tashkilot ko'rsatiladi, odam emas.
export const BOT_NOTE = `<div class="bot-note">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="8" width="16" height="12" rx="2"/><path d="M12 8V4M9 14h.01M15 14h.01"/></svg>
  <span>Bu qisqacha xabarni avtomat tizim quyidagi manbadan yig'ib, o'zbekchada qisqartirdi. Rasmiy tafsilot uchun manbaga o'ting — narx va muddatlar o'zgarishi mumkin.</span>
</div>`;

export const CATEGORY_UZ = {
  "exam-update": "imtihon",
  "fees": "narx",
  "deadline": "muddat",
  "guide": "foydali",
};
