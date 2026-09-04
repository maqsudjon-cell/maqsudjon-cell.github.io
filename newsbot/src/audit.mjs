// audit.mjs — chiqarilgan sahifalarni SEO bo'yicha tekshiradi.
//
// Ish oqimida `continue-on-error` bilan turadi: xato topilsa logda ko'rinadi,
// lekin nashrni to'xtatmaydi. Maqsad — sahifa jimgina buzilib ketmasin.
//
// Tekshiradi: sarlavha va tavsif uzunligi, canonical, og:image, JSON-LD,
// bitta h1, ichki havolalar, sahifa vazni, lenta.json va sitemap mosligi.

import { readFile, readdir, stat } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const REPO = join(ROOT, "..");
const SITE = "https://flarestamina.com";

// Google sarlavhani ~60, tavsifni ~155 belgida kesadi.
const TITLE_MAX = 60;
const DESC_MAX = 160;
const DESC_MIN = 50;
const PAGE_MAX_KB = 120;

const problems = [];
const warn = (page, msg) => problems.push({ level: "ogohlantirish", page, msg });
const bad = (page, msg) => problems.push({ level: "XATO", page, msg });

const attr = (html, re) => html.match(re)?.[1]?.trim() ?? "";

function checkPage(page, html) {
  const title = attr(html, /<title>([\s\S]*?)<\/title>/i);
  const desc = attr(html, /<meta\s+name="description"\s+content="([^"]*)"/i);
  const canon = attr(html, /<link\s+rel="canonical"\s+href="([^"]*)"/i);
  const ogImg = attr(html, /<meta\s+property="og:image"\s+content="([^"]*)"/i);

  if (!title) bad(page, "sarlavha yo'q");
  else if (title.length > TITLE_MAX) warn(page, `sarlavha ${title.length} belgi (${TITLE_MAX} dan uzun, Google kesadi)`);

  if (!desc) bad(page, "tavsif yo'q");
  else if (desc.length > DESC_MAX) warn(page, `tavsif ${desc.length} belgi (${DESC_MAX} dan uzun)`);
  else if (desc.length < DESC_MIN) warn(page, `tavsif ${desc.length} belgi (juda qisqa)`);

  if (!canon) bad(page, "canonical yo'q");
  else if (canon !== `${SITE}${page}`) bad(page, `canonical mos emas: ${canon}`);

  if (!ogImg) warn(page, "og:image yo'q");

  const h1 = html.match(/<h1[^>]*>/gi) || [];
  if (h1.length === 0) bad(page, "h1 yo'q");
  else if (h1.length > 1) warn(page, `${h1.length} ta h1 (bitta bo'lishi kerak)`);

  for (const m of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/gi)) {
    try { JSON.parse(m[1]); } catch (e) { bad(page, `JSON-LD buzuq: ${e.message}`); }
  }

  // Ichki havola — tashqi manbaga chiqib ketadigan boshi berk sahifa bo'lmasin.
  const internal = new Set([...html.matchAll(/href="(\/[^"#][^"]*)"/g)].map((m) => m[1]));
  if (internal.size < 5) warn(page, `atigi ${internal.size} ta ichki havola`);

  const kb = Buffer.byteLength(html) / 1024;
  if (kb > PAGE_MAX_KB) warn(page, `sahifa ${kb.toFixed(0)} KB (${PAGE_MAX_KB} KB dan og'ir)`);
}

async function main() {
  let lenta = { posts: [] };
  try { lenta = JSON.parse(await readFile(join(REPO, "news/lenta.json"), "utf8")); } catch {}

  const pages = [["/news/lenta/", join(REPO, "news/lenta/index.html")]];
  for (const p of lenta.posts) {
    pages.push([`/news/x/${p.slug}/`, join(REPO, "news/x", p.slug, "index.html")]);
  }

  for (const [path, file] of pages) {
    let html;
    try { html = await readFile(file, "utf8"); }
    catch { bad(path, "sahifa fayli yo'q"); continue; }
    checkPage(path, html);
  }

  // Sahifasi bor, lekin ro'yxatda yo'q xabarlar — rebase to'qnashuvidan keyin
  // shunday bo'lib qolishi mumkin (ailenta'da o'lchangan).
  try {
    const known = new Set(lenta.posts.map((p) => p.slug));
    for (const d of await readdir(join(REPO, "news/x"), { withFileTypes: true })) {
      if (d.isDirectory() && !known.has(d.name)) {
        bad(`/news/x/${d.name}/`, "sahifa bor, lekin lenta.json da yo'q");
      }
    }
  } catch {}

  // Sitemap mosligi.
  try {
    const xml = await readFile(join(REPO, "sitemap.xml"), "utf8");
    for (const p of lenta.posts) {
      if (!xml.includes(`${SITE}/news/x/${p.slug}/`)) {
        warn(`/news/x/${p.slug}/`, "sitemap'da yo'q (keyingi sitemap yugurishida qo'shiladi)");
      }
    }
  } catch {}

  // Muqova rasmi bormi.
  for (const p of lenta.posts) {
    try { await stat(join(REPO, "news/x", p.slug, "cover.png")); }
    catch { warn(`/news/x/${p.slug}/`, "cover.png yo'q"); }
  }

  const errors = problems.filter((x) => x.level === "XATO");
  console.log(`Tekshirildi: ${pages.length} ta sahifa — ${errors.length} xato, ${problems.length - errors.length} ogohlantirish`);
  for (const x of problems) console.log(`  ${x.level === "XATO" ? "x" : "."} ${x.page}  ${x.msg}`);

  // continue-on-error tufayli nashr to'xtamaydi, lekin qadam qizil bo'ladi.
  if (errors.length) process.exitCode = 1;
}

if (process.argv[1]?.endsWith("audit.mjs")) main();
