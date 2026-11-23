// collect.mjs — barcha manbalardan xom xabarlarni yig'adi.
// Tashqi kutubxona yo'q: Node 20+ dagi fetch va oddiy XML parser yetarli.
//
// Chiqish: newsbot/data/raw.json

import { readFile, writeFile, mkdir, rename } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const UA = "Mozilla/5.0 (compatible; FlarestaminaNewsBot/1.0; +https://flarestamina.com/news/)";
const TIMEOUT = 20_000;

const hash = (s) => createHash("sha1").update(s).digest("hex").slice(0, 12);

const ENTITIES = {
  amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ",
  "#39": "'", "#8217": "’", "#8216": "‘", "#8220": "“",
  "#8221": "”", "#8211": "–", "#8212": "—", "#160": " ",
};

function decode(str = "") {
  return str
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
      if (e.toLowerCase().startsWith("#x")) return String.fromCodePoint(parseInt(e.slice(2), 16));
      return ENTITIES[e] ?? ENTITIES[e.toLowerCase()] ?? m;
    })
    .trim();
}

const stripTags = (s = "") => decode(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

function tag(block, name) {
  const m = block.match(new RegExp(`<${name}(?:\\s[^>]*)?>([\\s\\S]*?)</${name}>`, "i"));
  return m ? decode(m[1]) : "";
}

async function get(url) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), TIMEOUT);
  try {
    const res = await fetch(url, { headers: { "user-agent": UA, accept: "*/*" }, signal: ctrl.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  } finally {
    clearTimeout(t);
  }
}

export function normalizeUrl(raw) {
  try {
    const u = new URL(raw);
    for (const k of [...u.searchParams.keys()]) {
      if (/^(utm_|ref|source|fbclid|gclid|oc$|hl$)/i.test(k)) u.searchParams.delete(k);
    }
    u.hash = "";
    u.hostname = u.hostname.replace(/^www\./, "");
    let s = u.toString();
    if (s.endsWith("/")) s = s.slice(0, -1);
    return s;
  } catch {
    return raw;
  }
}

function hostOf(raw) {
  if (typeof raw !== "string" || !raw) return "";
  try {
    return new URL(raw).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

// Nashr nomi bo'sh qolsa (Google News sarlavhasida " - Nashr" yo'q va manbada
// `name` ham yo'q) keyingi filtr butun yig'ishni yiqitmasin.
// Tartib: sozlangan nom, feed hosti, maqola hosti, oxirida xavfsiz yorliq.
export function sourceLabel(src, itemUrl = "") {
  const configured = typeof src?.name === "string" ? src.name.trim() : "";
  if (configured) return configured;
  return hostOf(src?.url) || hostOf(itemUrl) || "Unknown";
}

function ensureSourceName(it) {
  const current = typeof it?.sourceName === "string" ? it.sourceName.trim() : "";
  it.sourceName = current || sourceLabel(null, it?.url);
  return it.sourceName;
}

function isoOrNow(published) {
  const t = Date.parse(published);
  if (!Number.isFinite(t)) return new Date().toISOString();
  return new Date(t).toISOString();
}

function parseBlock(b, src) {
  const title = stripTags(tag(b, "title"));
  if (!title) return null;

  // Atom: <link href="..."/>, RSS: <link>...</link>
  let link = tag(b, "link");
  if (!link || link.startsWith("<")) {
    const alt = b.match(/<link[^>]*rel=["']alternate["'][^>]*href=["']([^"']+)["']/i)
      || b.match(/<link[^>]*href=["']([^"']+)["']/i);
    link = alt ? decode(alt[1]) : "";
  }
  if (!link) link = stripTags(tag(b, "guid"));
  if (!/^https?:/i.test(link)) return null;

  const published = tag(b, "pubDate") || tag(b, "published") || tag(b, "updated") || tag(b, "dc:date");
  const summary = stripTags(
    tag(b, "description") || tag(b, "summary") || tag(b, "content") || tag(b, "content:encoded")
  ).slice(0, 900);

  const url = normalizeUrl(link);
  return {
    id: hash(url),
    title,
    url,
    source: src?.id ?? "",
    sourceName: sourceLabel(src, url),
    published: published ? isoOrNow(published) : new Date().toISOString(),
    summary,
    weight: src?.weight ?? 1,
    primary: !!src?.primary,
    official: !!src?.official,
    local: !!src?.local,
  };
}

export function parseFeed(xml, src) {
  const out = [];
  const blocks = String(xml || "").match(/<(item|entry)(?:\s[^>]*)?>[\s\S]*?<\/\1>/gi) || [];

  for (const b of blocks) {
    try {
      const item = parseBlock(b, src);
      if (item) out.push(item);
    } catch (e) {
      console.error(`  x ${src?.id || "item"}: ${e.message}`);
    }
  }
  return src?.cap ? out.slice(0, src.cap) : out;
}

// Google News sarlavhasi "Sarlavha - Nashr" ko'rinishida keladi. Nashr
// nomida ham chiziqcha bo'lishi mumkin, shuning uchun OXIRGI ajratgichdan
// bo'lamiz. Ajratgich yo'q bo'lsa sozlangan nom (yoki host) qoladi.
export function withGooglePublisher(it) {
  const title = typeof it?.title === "string" ? it.title : "";
  const cut = title.lastIndexOf(" - ");
  if (cut > 10 && title.length - cut < 45) {
    const publisher = title.slice(cut + 3).trim();
    if (publisher) {
      it.sourceName = publisher;
      it.title = title.slice(0, cut).trim();
    }
  }
  ensureSourceName(it);
  return it;
}

export function itemsFromFeed(xml, src, { google = false } = {}) {
  const parsed = parseFeed(xml, src);
  if (!google) return parsed;
  const out = [];
  for (const it of parsed) {
    try {
      out.push(withGooglePublisher(it));
    } catch (e) {
      console.error(`  x ${src?.id || "item"}: ${e.message}`);
    }
  }
  return out;
}

// Google News. Oyna har so'rov uchun alohida: IELTS xabari kam, "when:2d"
// bilan lenta bo'sh qoladi.
async function collectGoogleNews(q) {
  const hl = q.hl || "en-US";
  const gl = q.gl || "US";
  const ceid = `${gl}:${hl.split("-")[0]}`;
  const url = `https://news.google.com/rss/search?q=${encodeURIComponent(`${q.q} when:${q.when || "7d"}`)}&hl=${hl}&gl=${gl}&ceid=${ceid}`;
  const xml = await get(url);
  return itemsFromFeed(xml, q, { google: true });
}

// Bitta manba (tarmoq, XML, bitta yozuv) butun yig'ishni to'xtatmasin.
export async function loadSource(label, task) {
  try {
    const rows = await task();
    return Array.isArray(rows) ? rows : [];
  } catch (e) {
    console.error(`  x ${label}: ${e.message}`);
    return [];
  }
}

export function selectItems(all, cfg, now = Date.now()) {
  const cutoff = now - (cfg?.maxAgeHours ?? 336) * 3600_000;
  const blocked = (cfg?.blockDomains || [])
    .filter((d) => typeof d === "string")
    .map((d) => d.toLowerCase());

  let tooOld = 0, spamSource = 0, dropped = 0;
  const items = [];
  for (const it of all) {
    try {
      if (!it || typeof it !== "object") { dropped++; continue; }
      ensureSourceName(it);
      const t = Date.parse(it.published);
      if (!Number.isFinite(t) || t < cutoff) { tooOld++; continue; }
      const name = it.sourceName.toLowerCase();
      if (blocked.some((d) => d && name.includes(d))) { spamSource++; continue; }
      items.push(it);
    } catch (e) {
      dropped++;
      console.error(`  x item: ${e.message}`);
    }
  }
  return { items, tooOld, spamSource, dropped };
}

export function applyGoogleWeights(items, cfg) {
  const publishers = cfg?.publishers || {};
  for (const it of items) {
    try {
      if (typeof it?.source !== "string" || !it.source.startsWith("gn-")) continue;
      const key = typeof it.sourceName === "string" ? it.sourceName : "";
      it.weight = publishers[key] ?? 1;
      if (it.local) it.weight += 2;
      it.indirect = true;
    } catch (e) {
      console.error(`  x item: ${e.message}`);
    }
  }
  return items;
}

async function main() {
  const cfg = JSON.parse(await readFile(join(ROOT, "sources.json"), "utf8"));
  const jobs = [];

  for (const f of cfg.feeds) {
    jobs.push(loadSource(f.id, () => get(f.url).then((xml) => itemsFromFeed(xml, f))));
  }
  for (const q of cfg.googleNews || []) {
    jobs.push(loadSource(q.id, () => collectGoogleNews(q)));
  }

  const all = (await Promise.all(jobs)).flat();

  // Feedlar arxivni ham beradi — sana bo'yicha kesamiz.
  const { items, tooOld, spamSource, dropped } = selectItems(all, cfg);

  // So'rovning emas, nashrning obro'si. Google News havolasi asl maqolaga
  // bormaydi (JS redirect): bunday xabar tasdiq uchun yaraydi, lekin saytda
  // manba sifatida ko'rsatilmaydi.
  applyGoogleWeights(items, cfg);

  // Bitta URL bir necha manbadan kelishi mumkin — eng og'irini qoldiramiz.
  const byUrl = new Map();
  for (const it of items) {
    try {
      if (typeof it?.url !== "string" || !it.url) continue;
      const cur = byUrl.get(it.url);
      if (!cur || it.weight > cur.weight) byUrl.set(it.url, it);
    } catch (e) {
      console.error(`  x item: ${e.message}`);
    }
  }
  const publishedKey = (it) => (typeof it?.published === "string" ? it.published : "");
  const unique = [...byUrl.values()].sort((a, b) => publishedKey(b).localeCompare(publishedKey(a)));

  await mkdir(join(ROOT, "data"), { recursive: true });
  const tmp = join(ROOT, "data/raw.json.tmp");
  await writeFile(tmp, JSON.stringify(unique, null, 2));
  await rename(tmp, join(ROOT, "data/raw.json"));

  const per = {};
  for (const it of unique) per[it.sourceName] = (per[it.sourceName] || 0) + 1;
  const bad = dropped ? `, ${dropped} yaroqsiz` : "";
  console.log(`Yig'ildi: ${unique.length} ta (${all.length} xom, ${tooOld} eski, ${spamSource} spam manba${bad})`);
  for (const [k, v] of Object.entries(per).sort((a, b) => b[1] - a[1]).slice(0, 15)) {
    console.log(`  ${String(v).padStart(3)}  ${k}`);
  }
}

if (process.argv[1]?.endsWith("collect.mjs")) main();
