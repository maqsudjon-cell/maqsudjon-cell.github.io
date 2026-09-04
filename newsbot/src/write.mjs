// write.mjs — klasterlarni o'zbekcha xabarga aylantiradi.
//
// Provayder AI_PROVIDER bilan tanlanadi: "gemini" (standart) yoki "anthropic".
// Kalit: GEMINI_API_KEY yoki ANTHROPIC_API_KEY.
//
// Kirish:  newsbot/data/clusters.json
// Chiqish: newsbot/data/posts.json (qo'shib boriladi), newsbot/data/seen.json

import { readFile, writeFile, rename } from "node:fs/promises";
import { storyKey, sameStory } from "./similar.mjs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

// Fayl yozilayotganda jarayon to'xtasa, oddiy writeFile faylni bo'shatib
// qoldiradi. Avval yonidagi vaqtinchalik faylga yozib, keyin o'rniga
// ko'chiramiz — fayl yo eski, yo yangi holatda bo'ladi.
async function writeAtomic(path, data) {
  const tmp = `${path}.tmp`;
  await writeFile(tmp, data);
  await rename(tmp, path);
}

const PROVIDER = process.env.AI_PROVIDER || "gemini";
const BATCH = 6;

// Kategoriyalar /news/ sahifasidagi filtr tugmalari bilan bir xil bo'lishi
// SHART — chipbar data-f qiymatlari bo'yicha ishlaydi.
const CATEGORIES = ["exam-update", "fees", "deadline", "guide"];

const SYSTEM = `Sen flarestamina.com uchun IELTS va xorijda ta'lim yangiliklarini
o'zbek tilida yozadigan muharrirsan. O'quvchilaring — O'zbekistondagi abituriyent,
talaba va IELTS topshirmoqchi bo'lganlar.

Senga bir voqea haqidagi sarlavhalar va qisqa tavsiflar beriladi. Vazifang —
o'sha voqeani o'zbekchada aniq yetkazish.

QAT'IY QOIDALAR:
1. Faqat berilgan matndagi ma'lumotdan foydalan. O'zingdan fakt, raqam, sana,
   narx yoki ism QO'SHMA. Bilganingni emas, berilganini yoz.
2. Har qanday raqam, narx va sana berilgan matnda aynan shunday turgan bo'lishi
   shart. Bu eng muhim qoida: noto'g'ri narx yoki muddat o'quvchiga pul va
   imkoniyat yo'qotadi. Ishonching komil bo'lmasa raqamni umuman yozma.
3. Manbada aytilmagan sabab, oqibat yoki maslahat qo'shma. "Bu talabalar uchun
   foydali" kabi o'z bahoingni yozma — faqat nima bo'lganini ayt.
4. Sarlavha 60 belgidan oshmasin, nuqta qo'yilmasin, hayajon belgisi bo'lmasin.
5. Xulosa (summary) — 2 yoki 3 ta jumla, jami 45 so'zgacha.
6. points — 2 tadan 4 tagacha qisqa fakt. Har biri bitta jumla, 12 so'zgacha.
   Sana yoki raqam bo'lsa shu yerda tursin. Har bir fakt berilgan matnda bo'lsin.
7. Reklama ohangi bo'lmasin: "ajoyib", "inqilobiy", "shoshiling" — ishlatma.
8. Kim nima qilgani va kim xabar bergani chalkashmasin.
9. Voqea O'zbekistonga aloqador bo'lmasa ham yozaver, lekin qaysi mamlakat
   haqida ekanini sarlavhada yoki birinchi jumlada aniq ko'rsat.
10. Ishonching komil bo'lmasa yoki matn yetarli bo'lmasa "skip": true qaytar.
    Bo'sh lenta yomon xabardan afzal.
11. Foydalanuvchi xabarining oxirida "ALLAQACHON CHIQQAN" ro'yxati beriladi.
    Voqea o'sha ro'yxatda bo'lsa — boshqa so'z bilan yozilgan bo'lsa ham —
    "skip": true qaytar.
12. Shu javobning o'zida ikkita element bir voqea haqida bo'lsa, faqat bittasini
    qoldir, qolganiga "skip": true qo'y.

category — faqat shu to'rttadan biri:
  "exam-update" — imtihon formati, sanasi, qoidasi, natijalari o'zgardi
  "fees"        — narx, to'lov, chegirma
  "deadline"    — grant, stipendiya, ariza muddati
  "guide"       — qolgan hammasi

Javobni faqat JSON massiv sifatida qaytar, boshqa hech narsa yozma:
[{"id":"<berilgan id>","title":"...","summary":"...","points":["...","..."],"category":"...","importance":1-5,"skip":false}]

importance — 5 = hamma bilishi kerak, 1 = mayda xabar.`;

// ---------- provayderlar ----------

// Bepul tarifda kunlik chegara HAR BIR MODEL uchun alohida. 429 kelganda
// keyingi modelga o'tamiz, aks holda o'sha yugurishdagi xabarlar yo'qoladi.
const GEMINI_MODELS = (process.env.GEMINI_MODEL || "gemini-3.5-flash,gemini-2.5-flash,gemini-flash-latest")
  .split(",").map((m) => m.trim()).filter(Boolean);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function geminiOnce(model, key, prompt) {
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,
    {
      method: "POST",
      headers: { "content-type": "application/json", "x-goog-api-key": key },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: SYSTEM }] },
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.2, responseMimeType: "application/json" },
      }),
    }
  );
  if (res.status === 429) {
    const err = new Error(`${model}: kunlik chegara tugadi`);
    err.quota = true;
    throw err;
  }
  if (!res.ok) throw new Error(`${model} ${res.status}: ${(await res.text()).slice(0, 160)}`);
  const j = await res.json();
  return j.candidates?.[0]?.content?.parts?.[0]?.text ?? "";
}

async function callGemini(prompt) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) throw new Error("GEMINI_API_KEY yo'q");
  let last;
  for (const model of GEMINI_MODELS) {
    for (let attempt = 0; attempt < 2; attempt++) {
      try { return await geminiOnce(model, key, prompt); }
      catch (e) {
        last = e;
        if (e.quota) break;
        if (attempt === 0) await sleep(3000);
      }
    }
    console.error(`  . ${last.message} — keyingi modelga o'tilmoqda`);
  }
  throw last;
}

async function callAnthropic(prompt) {
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) throw new Error("ANTHROPIC_API_KEY yo'q");
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": key,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: process.env.ANTHROPIC_MODEL || "claude-sonnet-5",
      max_tokens: 4000,
      temperature: 0.2,
      system: SYSTEM,
      messages: [{ role: "user", content: prompt }],
    }),
  });
  if (!res.ok) throw new Error(`Anthropic ${res.status}: ${(await res.text()).slice(0, 200)}`);
  const j = await res.json();
  return j.content?.[0]?.text ?? "";
}

const call = PROVIDER === "anthropic" ? callAnthropic : callGemini;

// ---------- tekshiruv ----------

// Matndagi har bir raqam manbada ham bo'lishi shart.
//
// O'zbekchada kasr vergul bilan ("3,5"), inglizchada nuqta bilan ("3.5").
// Inglizcha mingliklarni ham vergul ajratadi ("150,000"). Shuning uchun ikki
// xil normallashtirib solishtiramiz.
const asDecimal = (s) => s.replace(/\s/g, "").replace(/,/g, ".");
const asDigits = (s) => s.replace(/[\s.,]/g, "");

export function numbersAreGrounded(text, sourceText) {
  const nums = text.match(/\d[\d.,\s]*\d|\d/g) || [];
  const hayDecimal = asDecimal(sourceText);
  const hayDigits = asDigits(sourceText);

  return nums.every((raw) => {
    const n = raw.replace(/[.,\s]+$/, "");
    const dec = asDecimal(n);
    const dig = asDigits(n);
    if (dig.length <= 1) return true;             // "2 ta shahar" kabi mayda sonlar
    if (/^(19|20)\d\d$/.test(dig)) return true;   // yil
    return hayDecimal.includes(dec) || hayDigits.includes(dig);
  });
}

// Google sarlavhani ~60 belgida kesadi va bosilish darajasi tushadi. Model
// promptdagi cheklovni ba'zan e'tiborsiz qoldiradi, shuning uchun kod
// darajasida tekshiramiz.
export const TITLE_MAX = 60;

export async function shortenTitle(title, callFn) {
  const prompt = [
    "Quyidagi o'zbekcha yangilik sarlavhasi juda uzun.",
    `Uni ${TITLE_MAX} belgidan oshmaydigan qilib qayta yoz.`,
    "Ma'noni, kim va nima qilganini saqla. Raqam bo'lsa saqla.",
    "Nuqta qo'yma, hayajon belgisi ishlatma, tirnoq qo'shma.",
    "Faqat sarlavhaning o'zini qaytar, boshqa hech narsa yozma.",
    "",
    `Sarlavha: ${title}`,
  ].join("\n");
  try {
    const out = (await callFn(prompt)).trim().split("\n")[0].trim()
      .replace(/^["'«»]+|["'«».]+$/g, "").trim();
    // Har qanday yaxshilanish yo'qdan afzal: 80 → 64 ham qabul qilinadi.
    if (out && out.length >= 15 && out.length < title.length) return out;
  } catch (e) {
    console.error(`  . sarlavhani qisqartirib bo'lmadi: ${e.message}`);
  }
  return null;
}

function extractJson(text) {
  const start = text.indexOf("[");
  const end = text.lastIndexOf("]");
  if (start === -1 || end === -1) throw new Error("JSON topilmadi");
  return JSON.parse(text.slice(start, end + 1));
}

// Sahifa manzili uchun. O'zbekcha harflar lotin bo'lgani uchun translit shart
// emas, faqat apostrof va tinish belgilarini tozalaymiz.
const slugify = (s) =>
  s.toLowerCase()
    .replace(/[’‘'`]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 60);

// ---------- asosiy ----------

async function main() {
  const clusters = JSON.parse(await readFile(join(ROOT, "data/clusters.json"), "utf8"));
  if (!clusters.length) return console.log("Yangi klaster yo'q — LLM chaqirilmadi.");

  let posts = [];
  let seen = { urls: [], titles: [] };
  try { posts = JSON.parse(await readFile(join(ROOT, "data/posts.json"), "utf8")); } catch {}
  try { seen = JSON.parse(await readFile(join(ROOT, "data/seen.json"), "utf8")); } catch {}

  const written = [];

  // Nashr etilgan xabarlarning o'zbekcha matn imzosi. Inglizcha sarlavhalar
  // bo'yicha tekshiruv filter.mjs da bo'ldi, lekin turli nashrlar bir voqeani
  // butunlay boshqa so'zlar bilan yozadi. Model esa hammasini bitta o'zbekcha
  // shaklga keltiradi — oxirgi to'siq shu.
  const publishedKeys = posts.map(storyKey);

  for (let i = 0; i < clusters.length; i += BATCH) {
    const batch = clusters.slice(i, i + BATCH);
    const prompt = batch.map((c, n) => {
      const lead = c.items[0];
      const others = c.items.slice(1, 6).map((x) => `- ${x.sourceName}: ${x.title}`).join("\n");
      return [
        `### ${n}`,
        `id: ${lead.id}`,
        `Asosiy manba: ${lead.sourceName}`,
        `Sarlavha: ${lead.title}`,
        lead.summary ? `Tavsif: ${lead.summary.slice(0, 700)}` : "",
        // enrich.mjs ochib bergan asl maqola matni. Eng qimmatli qism:
        // Google News tavsif bermaydi, ya'ni busiz modelda sarlavhadan
        // boshqa hech narsa bo'lmaydi.
        lead.fulltext ? `Maqola matni:\n${lead.fulltext.slice(0, 1800)}` : "",
        others ? `Boshqa nashrlar:\n${others}` : "",
      ].filter(Boolean).join("\n");
    }).join("\n\n");

    const recent = posts.slice(0, 25)
      .map((p) => `- ${p.title} — ${p.summary.split(/\s+/).slice(0, 16).join(" ")}`)
      .join("\n");
    const full = recent ? `${prompt}\n\n### ALLAQACHON CHIQQAN\n${recent}` : prompt;

    let parsed;
    try { parsed = extractJson(await call(full)); }
    catch (e) { console.error(`  x LLM xatosi: ${e.message}`); continue; }

    for (const r of parsed) {
      const c = batch.find((x) => x.items[0].id === r.id);
      if (!c) continue;
      // Nima rad etilgani logda ko'rinib tursin: filtr juda qattiq bo'lib
      // qolsa yoki aksincha o'tkazib yuborsa, buni shu yerdan bilamiz.
      if (r.skip) { console.error(`  . model o'tkazmadi: ${c.items[0].title.slice(0, 70)}`); continue; }
      if (!r.title || !r.summary) continue;

      if (r.title.trim().length > TITLE_MAX) {
        const short = await shortenTitle(r.title.trim(), call);
        if (short) {
          console.error(`  . sarlavha qisqartirildi (${r.title.trim().length} → ${short.length})`);
          r.title = short;
        }
      }

      const sourceText = c.items.map((x) => `${x.title} ${x.summary || ""} ${x.fulltext || ""}`).join(" ");
      const points = (Array.isArray(r.points) ? r.points : [])
        .map((p) => String(p).trim()).filter(Boolean).slice(0, 4);
      const body = `${r.title} ${r.summary} ${points.join(" ")}`;
      if (!numbersAreGrounded(body, sourceText)) {
        console.error(`  x tashlandi (raqam manbada yo'q): ${r.title}`);
        continue;
      }

      const key = storyKey(r);
      if (publishedKeys.some((prev) => sameStory(key, prev))) {
        console.error(`  x tashlandi (bu voqea chiqib bo'lgan): ${r.title}`);
        continue;
      }
      publishedKeys.push(key);

      const lead = c.items[0];
      written.push({
        id: lead.id,
        slug: `${slugify(r.title)}-${lead.id.slice(0, 6)}`,
        title: r.title.trim(),
        summary: r.summary.trim(),
        points,
        category: CATEGORIES.includes(r.category) ? r.category : "guide",
        importance: Math.min(5, Math.max(1, Number(r.importance) || 3)),
        score: c.score,
        published: lead.published,
        created: new Date().toISOString(),
        coverage: c.items.length,
        source: {
          name: lead.sourceName,
          url: lead.url,
          title: lead.title,
          indirect: !!lead.indirect,
        },
        // Boshqa nashrlar — o'quvchi bir voqeani bir necha manbadan tekshira
        // olishi uchun. Google News havolalari (indirect) bu yerga tushmaydi.
        also: (() => {
          const seenName = new Set([lead.sourceName]);
          const out = [];
          for (const x of c.items.slice(1)) {
            if (seenName.has(x.sourceName) || x.indirect) continue;
            seenName.add(x.sourceName);
            out.push({ name: x.sourceName, url: x.url });
            if (out.length >= 6) break;
          }
          return out;
        })(),
        model: PROVIDER,
      });
    }
  }

  // Voqea nashr etilganda uning BARCHA nashrlaridagi sarlavhalarni eslab
  // qolamiz. Faqat bosh manbani eslasak, keyingi yugurishda o'sha voqeaga
  // boshqa nashr bosh bo'lib qoladi va xabar ikkinchi marta chiqib ketadi.
  const flat = (t) => t.toLowerCase().replace(/[^a-z0-9 ]/g, " ").replace(/\s+/g, " ").trim();
  for (const p of written) {
    const c = clusters.find((x) => x.items[0].id === p.id);
    for (const it of (c ? c.items : []).slice(0, 12)) {
      seen.urls.push(it.url);
      seen.titles.push(flat(it.title));
    }
  }
  seen.urls = seen.urls.slice(-12000);
  seen.titles = seen.titles.slice(-6000);

  posts = [...written, ...posts];

  await writeAtomic(join(ROOT, "data/posts.json"), JSON.stringify(posts, null, 2));
  await writeAtomic(join(ROOT, "data/seen.json"), JSON.stringify(seen, null, 2));
  await writeAtomic(
    join(ROOT, "data/last-run.json"),
    JSON.stringify({ at: new Date().toISOString(), slugs: written.map((p) => p.slug) }, null, 2)
  );

  console.log(`Yozildi: ${written.length} ta xabar (jami ${posts.length})`);
  for (const p of written) console.log(`  [${p.importance}] ${p.category} — ${p.title}`);
}

if (process.argv[1]?.endsWith("write.mjs")) main();
