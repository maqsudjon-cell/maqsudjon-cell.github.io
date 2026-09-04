// telegram.mjs — shu yugurishda chiqqan xabarlarni kanalga yuboradi.
//
// Sekretlar: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (ikkalasi ham repoda bor).
// Ikkalasi ham yo'q bo'lsa qadam jimgina o'tkazib yuboriladi.
//
// AI Lenta'dagidek dayjest kerak emas: IELTS xabari haftasiga bir nechta,
// shuning uchun har biri darhol yuboriladi.

import { readFile, writeFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SITE = "https://flarestamina.com";

const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT = process.env.TELEGRAM_CHAT_ID;

const esc = (s = "") =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

async function readJson(p, fallback) {
  try { return JSON.parse(await readFile(join(ROOT, p), "utf8")); } catch { return fallback; }
}

async function send(text) {
  const res = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      chat_id: CHAT,
      text,
      parse_mode: "HTML",
      disable_web_page_preview: false,
    }),
  });
  if (!res.ok) throw new Error(`${res.status}: ${(await res.text()).slice(0, 200)}`);
}

async function main() {
  if (!TOKEN || !CHAT) return console.log("Telegram sekretlari yo'q — o'tkazib yuborildi.");

  const last = await readJson("data/last-run.json", { slugs: [] });
  if (!last.slugs?.length) return console.log("Yangi xabar yo'q — Telegramga yuborilmadi.");

  const posts = await readJson("data/posts.json", []);
  const sent = new Set(await readJson("data/telegram-sent.json", []));

  const queue = last.slugs
    .filter((s) => !sent.has(s))
    .map((s) => posts.find((p) => p.slug === s))
    .filter(Boolean);

  if (!queue.length) return console.log("Hammasi yuborilgan.");

  let ok = 0;
  for (const p of queue) {
    const url = `${SITE}/news/x/${p.slug}/`;
    const points = p.points?.length
      ? `\n\n${p.points.map((x) => `• ${esc(x)}`).join("\n")}`
      : "";
    const text = `<b>${esc(p.title)}</b>\n\n${esc(p.summary)}${points}\n\n` +
      `Manba: ${esc(p.source.name)}\n${url}`;
    try {
      await send(text);
      sent.add(p.slug);
      ok++;
      await new Promise((r) => setTimeout(r, 1500));   // Telegram tezlik chegarasi
    } catch (e) {
      console.error(`  x ${p.slug}: ${e.message}`);
    }
  }

  await writeFile(join(ROOT, "data/telegram-sent.json"), JSON.stringify([...sent].slice(-500), null, 2));
  console.log(`Telegramga yuborildi: ${ok} ta`);
}

if (process.argv[1]?.endsWith("telegram.mjs")) main();
