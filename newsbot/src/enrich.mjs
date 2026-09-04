// enrich.mjs — tanlangan klasterlarni asl maqola matni bilan to'ldiradi.
//
// Ikki ish qiladi:
//   1. Google News havolasini asl maqola manziliga aylantiradi.
//   2. O'sha sahifani yuklab, matnini ajratadi.
//
// Nima uchun kerak: Google News RSS'i tavsif bermaydi — <description> ichida
// sarlavhaning o'zi turadi. Bunday xabardan model hech narsa yoza olmaydi
// (yoki yozsa, to'qib chiqargan bo'ladi). Asl matn bo'lsa xulosa manbaga
// bog'lanadi va sahifada haqiqiy havola turadi.
//
// FAQAT filter tanlagan klasterlar uchun ishlaydi (5 ta atrofida), shuning
// uchun so'rovlar kam va ketma-ket yuboriladi.

import { readFile, writeFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36";
const TIMEOUT = 20_000;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function get(url, opts = {}) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), TIMEOUT);
  try {
    const res = await fetch(url, {
      ...opts,
      headers: { "user-agent": UA, accept: "text/html,*/*", ...(opts.headers || {}) },
      signal: ctrl.signal,
      redirect: "follow",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  } finally {
    clearTimeout(t);
  }
}

// Google News havolasini asl manzilga aylantiradi.
//
// Havolaning o'zi yo'naltirmaydi (JS bilan ochiladi). Lekin sahifa ichida
// imzo (data-n-a-sg) va vaqt belgisi (data-n-a-ts) turadi — shu ikkisi bilan
// Google'ning o'z ichki endpointidan asl manzilni so'rash mumkin.
export async function resolveGoogleNews(url) {
  const m = url.match(/\/rss\/articles\/([^?/]+)/);
  if (!m) return null;
  const id = m[1];

  const html = await get(`https://news.google.com/rss/articles/${id}`);
  const sg = html.match(/data-n-a-sg="([^"]+)"/)?.[1];
  const ts = html.match(/data-n-a-ts="([^"]+)"/)?.[1];
  if (!sg || !ts) return null;

  const inner = JSON.stringify([
    "garturlreq",
    [["X", "X", ["X", "X"], null, null, 1, 1, "US:en", null, 1, null, null, null, null, null, 0, 1],
     "X", "X", 1, [1, 1, 1], 1, 1, null, 0, 0, null, 0],
    id, Number(ts), sg,
  ]);
  const body = new URLSearchParams({ "f.req": JSON.stringify([[["Fbv4je", inner, null, "generic"]]]) });

  const res = await get("https://news.google.com/_/DotsSplashUi/data/batchexecute", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded;charset=UTF-8" },
    body,
  });

  const found = res.match(/https?:\/\/(?!news\.google)[^\\"\s]+/);
  return found ? found[0] : null;
}

// Sahifadan maqola matnini ajratadi. Tashqi kutubxona yo'q: skript, uslub va
// navigatsiyani olib tashlab, <p> teglaridagi matnni yig'amiz.
export function extractText(html) {
  const cleaned = html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<(nav|header|footer|aside|form|noscript)[\s\S]*?<\/\1>/gi, " ");

  const paras = [...cleaned.matchAll(/<p[^>]*>([\s\S]*?)<\/p>/gi)]
    .map((x) => x[1].replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&quot;/g, '"')
      .replace(/&#39;|&apos;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
      .replace(/\s+/g, " ").trim())
    // Qisqa qatorlar deyarli har doim tugma, sana yoki cookie eslatmasi.
    .filter((s) => s.length > 60);

  return paras.join("\n").slice(0, 2500);
}

async function main() {
  const clusters = JSON.parse(await readFile(join(ROOT, "data/clusters.json"), "utf8"));
  if (!clusters.length) return console.log("Boyitadigan klaster yo'q.");

  let resolved = 0, fetched = 0, failed = 0;

  for (const c of clusters) {
    for (const it of c.items) {
      try {
        if (it.indirect) {
          const real = await resolveGoogleNews(it.url);
          if (real) {
            it.url = real;
            it.indirect = false;
            it.resolved = true;
            resolved++;
          }
        }
        // Matni allaqachon yetarli bo'lsa, sahifani yuklab o'tirmaymiz.
        if (!it.indirect && (it.summary || "").length < 400) {
          const text = extractText(await get(it.url));
          if (text.length > 200) { it.fulltext = text; fetched++; }
        }
      } catch (e) {
        failed++;
        console.error(`  . ${it.sourceName}: ${e.message}`);
      }
      await sleep(700);   // manbalarni bosmaslik uchun
    }
  }

  await writeFile(join(ROOT, "data/clusters.json"), JSON.stringify(clusters, null, 2));
  console.log(`Boyitildi: ${resolved} ta havola ochildi, ${fetched} ta maqola o'qildi, ${failed} ta xato`);
}

if (process.argv[1]?.endsWith("enrich.mjs")) main();
