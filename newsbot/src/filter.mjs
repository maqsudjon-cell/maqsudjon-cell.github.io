// filter.mjs — xom xabarlardan IELTS va xorijda ta'limga aloqadorlarini ajratadi,
// bir voqea haqidagilarini bitta klasterga yig'adi va eng muhimini tanlaydi.
//
// Kirish:  newsbot/data/raw.json, newsbot/data/seen.json
// Chiqish: newsbot/data/clusters.json

import { readFile, writeFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

const MAX_PER_RUN = Number(process.env.MAX_PER_RUN || 5);
const CLUSTER_MIN = 0.26;   // bundan past o'xshashlik — boshqa voqea

// Chegara — lentaning sifati shu raqamda hal bo'ladi.
//
// AI yangiliklarida kuniga yuzlab voqea bo'ladi, IELTS'da esa haftasiga bir
// nechta. Chegarasiz lenta bo'sh kunlarda "Study in Italy without IELTS"
// turidagi axlat bilan to'ladi. Shuning uchun hech narsa chiqmagani
// yomon xabar chiqqanidan afzal: past ball — nashr yo'q.
const MIN_SCORE = Number(process.env.MIN_SCORE || 30);

const norm = (s) =>
  s.toLowerCase()
    .replace(/[’‘'`]/g, "")
    .replace(/[^a-z0-9Ѐ-ӿ ]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();

// ---------- mavzu lug'ati ----------
//
// Ro'yxatlar norm() bilan bir xil shaklga keltiriladi, aks holda apostrofli
// o'zbekcha atamalar ("ta'lim") hech qachon topilmaydi.

// Imtihonning o'zi — eng qimmatli signal.
const EXAM_RAW = [
  "ielts", "toefl", "pte academic", "duolingo english test", "det",
  "cambridge english", "british council", "idp education", "idp ielts",
  "cefr", "multilevel", "band score", "one skill retake", "osr",
  "computer delivered", "computer based test", "test centre", "test center",
  "english proficiency test", "english language test", "language proficiency",
  "speaking test", "writing task", "listening test", "reading test",
  "test taker", "exam fee", "test fee", "score report", "trf",
  "pte", "ets", "ielts indicator", "test day", "exam date", "registration",
  "retake", "remark", "enquiry on results", "results release", "test format",
  "language centre", "exam board", "ofqual", "proficiency requirement",
];

// Viza va til talabi — imtihon bilan bir xil darajada muhim.
const VISA_RAW = [
  "student visa", "study permit", "study visa", "ukvi", "graduate route",
  "english language requirement", "language requirement", "visa rule",
  "international student", "immigration rule", "study abroad",
];

// Grant va muddat.
const GRANT_RAW = [
  "scholarship", "fellowship", "chevening", "erasmus mundus", "erasmus",
  "stipendium hungaricum", "turkiye burslari", "fulbright", "daad",
  "csc scholarship", "global korea scholarship", "gks", "el yurt umidi",
  "application deadline", "applications open", "call for applications",
  "fully funded", "tuition waiver",
];

// Talabaga TEGADIGAN o'zgarish belgisi. Bularsiz xabar nashr etilmaydi.
//
// Sohaviy tahlil ("International students prove a fiscal win for the
// Netherlands") IELTS'ga aloqador, lekin o'quvchi undan hech narsa qila
// olmaydi. Nashrga faqat biror narsa O'ZGARGAN xabar chiqadi: narx, sana,
// qoida, format, ariza oynasi.
const ACTION_RAW = [
  "announce", "announced", "announces", "opens", "opened", "open for",
  "deadline", "applications", "apply by", "launch", "launched", "launches",
  "introduce", "introduces", "introduced", "change", "changes", "changed",
  "new rule", "new requirement", "from september", "from january", "effective",
  "raise", "raises", "raised", "increase", "increases", "increased",
  "cut", "cuts", "reduce", "reduced", "ban", "bans", "banned",
  "suspend", "suspended", "resume", "resumed", "scrap", "scrapped",
  "replace", "replaces", "extend", "extended", "require", "requires",
  "fee", "fees", "price", "cost", "accept", "accepts", "recognise", "recognize",
  "now available", "goes digital", "closes", "closed", "reopen",
  // o'zbekcha va ruscha
  "elon qilindi", "boshlandi", "ochildi", "yakunlanadi", "muddat", "oshirildi",
  "kamaytirildi", "ozgardi", "ozgartirildi", "joriy etildi", "tasdiqlandi",
  "bekor qilindi", "toxtatildi", "qabul boshlandi", "arizalar",
  "объявлен", "открыт", "начался", "срок", "изменен", "повышен", "снижен",
  "приостановлен", "введен", "утвержден", "прием заявок",
];

// O'zbek nashrlari uchun alohida yo'lak: ular "IELTS" so'zini ishlatmasdan
// ham bizga kerakli xabar beradi ("xorijda ta'lim granti e'lon qilindi").
const UZ_RAW = [
  "ielts", "toefl", "cefr", "multilevel", "sertifikat",
  "chet tili", "ingliz tili", "til imtihoni", "til sertifikati",
  "xorijda talim", "xorijda oqish", "chet elda oqish",
  "stipendiya", "grant", "oquv granti", "davlat granti",
  "abituriyent", "abiturientlar", "magistratura", "bakalavriat",
  "dtm", "attestatsiya", "qabul imtihoni", "kirish imtihoni",
  "talim vazirligi", "oliy talim", "universitet qabuli",
  "el yurt umidi", "vazirlar mahkamasi qarori talim",
  // o'zbek kirill (UzA, Gazeta.uz, Xabar.uz kirillda yozadi)
  "таълим", "олий таълим", "ўқиш", "ўқув", "имтиҳон", "стипендия", "грант",
  "абитуриент", "магистратура", "бакалавриат", "сертификат", "чет тили",
  "инглиз тили", "хорижда таълим", "университет", "қабул", "ДТМ",
  "таълим вазирлиги", "малака", "тил имтиҳони",
  // ruscha (Sputnik, ru so'rovlari)
  "стипендия", "грант", "образование за рубежом", "поступление", "экзамен",
  "английский язык", "сертификат", "магистратура", "абитуриент",
];

const prep = (list) => [...new Set(list.map(norm).filter(Boolean))];
const EXAM = prep(EXAM_RAW), VISA = prep(VISA_RAW), GRANT = prep(GRANT_RAW);
const UZ = prep(UZ_RAW), ACTION = prep(ACTION_RAW);

// O'zbek tili qo'shimchali: "grant" matnda "grantlar", "grantga" bo'lib keladi.
// Butun so'z bo'yicha qidirish bularni topmaydi, shuning uchun uzun atamalarda
// so'z BOSHIga qaraymiz. Qisqa atamalar butun so'z bo'yicha qoladi, aks holda
// "det" har qanday so'zning boshini ushlab olardi.
const PREFIX_MIN = 5;

function hits(hay, terms) {
  const toks = hay.split(" ").filter(Boolean);
  let n = 0;
  for (const term of terms) {
    if (term.includes(" ")) {
      if (hay.includes(term)) n++;
    } else if (term.length >= PREFIX_MIN) {
      // Undosh almashinuvi: unli qo'shimcha oldidan k→g, q→g', p→b.
      const stem = /[kqp]$/.test(term) ? term.slice(0, -1) : term;
      if (toks.some((t) => t.startsWith(term) || t.startsWith(stem))) n++;
    } else if (toks.includes(term)) {
      n++;
    }
  }
  return n;
}

// ---------- axlat ----------
//
// "IELTS" so'zi bilan trafik yig'adigan sahifalar. Google News "IELTS"
// natijalarining chorak qismi shular — chiqarib tashlanmasa lenta shulardan
// iborat bo'lib qoladi.
const JUNK = [
  /\bwithout\s+ielts\b/i,
  /\bno\s+ielts\b/i,
  /\bielts\s+(waiver|exemption)\b/i,
  /\bstudy in\b.{0,40}\bwithout\b/i,
  /\b(best|top)\s+\d+\b/i,
  /\b\d+\s+(tips|tricks|ways|reasons|mistakes|secrets|hacks)\b/i,
  /\bband\s*[6-9](\.5)?\b.{0,30}\b(tips|tricks|secrets|hacks|guide|strategy)\b/i,
  /\b(coaching|tuition)\s+(centre|center|institute|classes|academy)\b/i,
  /\bhow to (score|get|crack|prepare|pass)\b/i,
  /\b(sample|practice|mock)\s+(test|questions|answers|essay)\b/i,
  /\b(cue card|speaking topics? for)\b/i,
  // Birja shovqini. IDP aksiyalari IELTS xabari emas — markaz yopilishi esa
  // xabar, shuning uchun quyida alohida istisno bor.
  /\b(shares?|stock|nasdaq|asx|price target|buyback|dividend|analyst rating)\b/i,
  /\b(horoscope|lottery|betting|casino)\b/i,
  /\b(admission open|apply now|enroll now|limited seats)\b/i,
  /^watch\b/i,
];

// Birja qoidasidan istisno: gap markaz yoki ish o'rni haqida bo'lsa, bu
// haqiqiy xabar ("IDP cuts test venues" — nomzodlarga to'g'ridan-to'g'ri tegadi).
const STOCK_EXCEPTION = /\b(test (venue|centre|center)s?|close[sd]? .{0,20}centres?|cuts? jobs|redundanc)/i;

// Sohaviy iqtisod xabarlari. ICEF Monitor va The PIE News talabaga emas,
// universitet va agentlarga yozadi: "commencements", "market outlook",
// "fiscal contribution". Bular IELTS'ga aloqador, lekin o'quvchi uchun
// yangilik emas — shuning uchun jarima.
const TRADE = /\b(commencements?|enrol(l)?ment (forecast|projection|data)|market (share|outlook|report)|sector|recruit(ment|ers?)|agents?|revenue|fiscal|economic (impact|contribution)|survey (finds|shows)|report (finds|shows)|projected)\b/i;

// Tadqiqotchi va mutaxassislarga mo'ljallangan dasturlar — bizning
// o'quvchimiz (abituriyent, bakalavr, magistr) ariza bera olmaydi.
const NOT_FOR_STUDENTS = /\b(postdoc\w*|phd fellowship|researchers? program|early[- ]career|professional fellowship|journalis\w+|entrepreneurs?|civil servants?|mid[- ]career)\b/i;

// Imtihonni O'TKAZADIGAN tashkilotlar. Ular e'lon qilgan o'zgarish —
// format, narx, vosita, markaz — to'g'ridan-to'g'ri imtihon topshiruvchiga
// tegadi. Boshqa hech kimning IELTS mahsuloti bizga yangilik emas.
const PROVIDER = /\b(british council|idp\b|idp education|cambridge (english|assessment)|pearson|ets\b|educational testing service|duolingo|ielts\.org|ofqual)\b/i;

// Kitob, kurs, ilova e'lonlari. Rasmiy tashkilotdan bo'lsa — yangilik
// ("Pearson launches Official PTE AI Practice"), o'quv markazidan bo'lsa —
// reklama ("Banglay IELTS Launches Grammar Book").
const PRODUCT = /\b(launch\w*|releas\w+|unveil\w+|introduc\w+)\b.{0,60}\b(book|course|app|platform|tool|programme|program|practice|service)\b/i;

// Grant xabari faqat O'QISH haqida bo'lsa bizga tegishli.
//
// "Frontier Fellowship" AI maslahatchilarini tayyorlaydigan 12 haftalik
// dastur — grant lug'ati bo'yicha o'tadi, lekin IELTS o'quvchisiga aloqasi
// yo'q. O'lchandi: u 25 ball olib, haqiqatan foydali PTE xabaridan (20)
// YUQORI turdi. Diplom/universitet belgisisiz grant xabari jarima oladi.
const DEGREE = /\b(master'?s?|bachelor'?s?|undergraduate|postgraduate|phd|doctoral|degree|universit\w+|tuition|semester|academic year|study programme|study program|scholarship for students)\b|magistratura|bakalavr|universitet|stipendiya|o'qish/i;

// Aksincha — aynan bizning o'quvchimizga atalgan.
const FOR_STUDENTS = /\b(master'?s?|undergraduate|bachelor'?s?|graduate stud|school leavers?|abituriyent|talabalar|students? in uzbekistan)\b/i;

// O'zbekistonga tegishlimi? Manba mahalliy bo'lmasa ham, matnda O'zbekiston
// tilga olinsa bu xabar bizniki.
const UZ_GEO = /\b(uzbek\w*|tashkent|toshkent|samarkand|samarqand)\b|узбек|ташкент|ўзбек/i;

// Boshqa mamlakatga bog'langan xabarlar. Bloklamaymiz — jarima beramiz:
// Hindistondagi o'zgarish ba'zan global o'zgarishning belgisi bo'ladi, lekin
// o'zbek o'quvchisiga to'g'ridan-to'g'ri tegmaydi. Grant chaqiruvlari esa
// mamlakat bo'yicha ochiladi: "Chevening (Nicaragua)" bizga umuman kerak emas.
const FAR_GEO = new RegExp(
  "\\b(" + [
    "indian students?", "in india", "india's", "vietnam", "nigeria", "pakistan",
    "bangladesh", "nepal", "philippines", "sri lanka", "ghana", "kenya", "ethiopia",
    "rwanda", "uganda", "tanzania", "zambia", "zimbabwe", "malawi", "cameroon",
    "nicaragua", "guatemala", "honduras", "peru", "colombia", "bolivia", "ecuador",
    "kazakhstan", "kyrgyz\\w*", "tajikistan", "turkmenistan", "azerbaijan", "armenia",
    "georgia", "moldova", "ukraine", "belarus", "mongolia", "cambodia", "laos",
    "myanmar", "thailand", "indonesia", "malaysia", "new zealand",
    "iran", "iranian\\w*", "iraq", "afghanistan", "syria", "sudan", "yemen",
    "egypt", "morocco", "algeria", "tunisia", "brazil", "argentina", "chile",
    "mexico", "venezuela", "haiti", "african students?", "for africans?",
  ].join("|") + ")\\b|области|край\\b|республике",
  "i"
);

// O'zbek nashrlaridagi qo'llanma va fikr sarlavhalari — yangilik emas.
//
// DIQQAT: yolg'iz savol belgisi bo'yicha rad etmang. Bu qoida ilgari shunday
// edi va "IELTS test fee increased: how much does it cost now?" — yugurishdagi
// eng qimmatli xabarni — axlatga chiqarib yubordi. O'zbek nashrlari haqiqiy
// yangilikni ham savol sarlavhasi bilan beradi.
const UZ_SKIP = [
  /\b(qanday qilib|nima uchun|nega)\b.*\?\s*$/i,
  /\b\d+\s*(ta\s+)?(tamoyil|maslahat|usul|sabab|qadam|sir|xato)\b/i,
  /\b(qo['’]llanma|yo['’]riqnoma|kolonka|intervyu|reportaj)\b/i,
];

const cleanTitle = (t) =>
  t.replace(/^(exclusive|analysis|update \d+|breaking|opinion|explainer)\s*[|:-]\s*/i, "")
   .replace(/\s*[|—–-]\s*(reuters|bbc|the guardian|the pie news|icef monitor)[^|]*$/i, "")
   .trim();

const STOP = new Set(
  ("a an the of for to in on at by with from and or as is are was were be been it its this that " +
   "new now says say said after before over under into out up down more most than what how why " +
   "will can could would should may might s t re ve ll amid your our their his her uchun bilan " +
   "va ham bu shu uni unga ular bir har qanday keyin oldin haqida boyicha")
    .split(" ")
);

function stem(w) {
  if (w.length > 5 && w.endsWith("ing")) return w.slice(0, -3);
  if (w.length > 5 && w.endsWith("ed")) return w.slice(0, -2);
  if (w.length > 4 && w.endsWith("es")) return w.slice(0, -2);
  if (w.length > 3 && w.endsWith("s")) return w.slice(0, -1);
  return w;
}

const tokens = (s) =>
  new Set(norm(s).split(" ").filter((w) => w.length > 2 && !STOP.has(w)).map(stem));

function overlap(a, b) {
  let n = 0;
  for (const x of a) if (b.has(x)) n++;
  return n;
}

// Har bir so'zning og'irligi — qanchalik kam uchrasa, shuncha ko'p ma'no beradi.
// "ielts" bugungi o'nlab sarlavhada bor, "hungaricum" esa bitta voqeada.
function buildIdf(docs) {
  const df = new Map();
  for (const d of docs) for (const t of d) df.set(t, (df.get(t) || 0) + 1);
  const n = docs.length;
  const idf = new Map();
  for (const [t, c] of df) idf.set(t, Math.log(n / (c + 1)) + 1);
  return idf;
}

function vectorize(toks, idf) {
  const v = new Map();
  let sq = 0;
  for (const t of toks) {
    const w = idf.get(t) ?? 1;
    v.set(t, w);
    sq += w * w;
  }
  return { v, norm: Math.sqrt(sq) || 1 };
}

function cosine(a, b) {
  const [small, big] = a.v.size < b.v.size ? [a, b] : [b, a];
  let dot = 0;
  for (const [t, w] of small.v) {
    const o = big.v.get(t);
    if (o) dot += w * o;
  }
  return dot / (a.norm * b.norm);
}

// Klaster markazi — a'zolar vektorlarining o'rtachasi. Yangi xabar shu markazga
// solishtiriladi: bitta chetdagi a'zo orqali zanjirlanish bo'lmaydi.
function centroidOf(vecs) {
  const sum = new Map();
  for (const { v } of vecs) for (const [t, w] of v) sum.set(t, (sum.get(t) || 0) + w);
  let sq = 0;
  for (const [t, w] of sum) {
    const avg = w / vecs.length;
    sum.set(t, avg);
    sq += avg * avg;
  }
  return { v: sum, norm: Math.sqrt(sq) || 1 };
}

// ---------- aloqadorlik ----------

export function relevance(item) {
  const hay = `${norm(item.title)} ${norm(item.summary || "")}`;
  const titleHay = norm(item.title);

  const exam = hits(titleHay, EXAM) * 2 + hits(hay, EXAM);
  const visa = hits(titleHay, VISA) * 2 + hits(hay, VISA);
  const grant = hits(titleHay, GRANT) * 2 + hits(hay, GRANT);
  const uz = item.local ? hits(titleHay, UZ) * 2 + hits(hay, UZ) : 0;
  const act = hits(titleHay, ACTION) * 2 + hits(hay, ACTION);

  return { exam, visa, grant, uz, act, total: exam + visa + grant + uz };
}

export function isJunk(item) {
  for (const re of JUNK) {
    if (!re.test(item.title)) continue;
    // Birja qoidasi yagona istisnoga ega.
    if (re.source.includes("nasdaq") && STOCK_EXCEPTION.test(item.title)) continue;
    return true;
  }
  if (item.local && UZ_SKIP.some((re) => re.test(item.title))) return true;
  return false;
}

function scoreCluster(c) {
  const lead = c.items[0];
  const text = c.items.map((i) => `${i.title} ${i.summary || ""}`).join(" ");
  let s = 0;

  // Mavzuga mosligi — asosiy ulush. Manba obro'si emas, xabarning o'zi hal
  // qiladi: ICEF Monitor'ning sohaviy tahlili ham, kichik nashrning PTE
  // formati haqidagi xabari ham bir xil o'lchovga tushadi.
  s += Math.min(c.rel.exam, 6) * 5;
  s += Math.min(c.rel.visa, 4) * 3;
  s += Math.min(c.rel.grant, 4) * 3;
  s += Math.min(c.rel.uz, 6) * 4;
  s += Math.min(c.rel.act, 3) * 4;             // biror narsa o'zgargani

  s += Math.min(lead.weight, 5) * 2;           // manba ishonchi — kichik ulush
  s += Math.min(c.items.length - 1, 4) * 7;    // nechta nashr yozgan
  if (c.items.some((i) => i.primary)) s += 6;
  if (c.items.some((i) => i.official)) s += 12; // rasmiy manba (GOV.UK, UzA)
  if (c.items.some((i) => i.local)) s += 16;    // o'zbek nashri yozgan

  if (UZ_GEO.test(text)) s += 26;               // matnda O'zbekiston bor
  else if (FAR_GEO.test(text)) s -= 22;         // boshqa mamlakatga bog'langan

  if (TRADE.test(text)) s -= 18;
  if (c.rel.grant > 0 && !DEGREE.test(text)) s -= 16;   // o'qish haqida emas
  if (PROVIDER.test(text)) s += 12;                     // imtihon egasining e'loni
  else if (PRODUCT.test(text)) s -= 14;                 // begona mahsulot reklamasi
  if (NOT_FOR_STUDENTS.test(text)) s -= 14;
  if (FOR_STUDENTS.test(text)) s += 8;
  if (c.items.every((i) => i.indirect)) s -= 10; // faqat Google News havolasi

  const ageD = (Date.now() - Date.parse(lead.published)) / 86400_000;
  s -= Math.max(0, ageD - 3) * 3;               // eskirgani uchun jarima
  return Math.round(s * 10) / 10;
}

async function readJson(p, fallback) {
  try { return JSON.parse(await readFile(join(ROOT, p), "utf8")); } catch { return fallback; }
}

async function main() {
  const raw = await readJson("data/raw.json", []);
  const seen = await readJson("data/seen.json", { urls: [], titles: [] });
  const seenUrls = new Set(seen.urls);
  const seenTitles = seen.titles.map((t) => tokens(t));

  let junked = 0;
  const fresh = raw.filter((it) => {
    if (seenUrls.has(it.url)) return false;
    if (isJunk(it)) { junked++; return false; }
    return tokens(it.title).size >= 2;
  });

  const scored = fresh
    .map((it) => {
      it.title = cleanTitle(it.title);
      return { it, rel: relevance(it), toks: tokens(it.title) };
    })
    // Mahalliy nashrga past bo'sag'a: ular kam yozadi, lekin yozgani qimmatli.
    .filter((x) => (x.it.local ? x.rel.total >= 2 : x.rel.total >= 3))
    // Hech narsa o'zgarmagan xabar lentaga tushmaydi (ACTION_RAW izohiga qarang).
    .filter((x) => x.rel.act >= 1 || x.rel.exam >= 3);

  const idf = buildIdf(scored.map((x) => x.toks));
  for (const x of scored) x.vec = vectorize(x.toks, idf);

  let clusters = [];
  for (const x of scored) {
    let best = null, bestSim = CLUSTER_MIN;
    for (const c of clusters) {
      if (overlap(c.toks, x.toks) < 2) continue;
      const sim = cosine(c.centroid, x.vec);
      if (sim > bestSim) { bestSim = sim; best = c; }
    }
    if (best) {
      best.members.push(x);
      for (const k of ["exam", "visa", "grant", "uz"]) best.rel[k] = Math.max(best.rel[k], x.rel[k]);
      best.centroid = centroidOf(best.members.map((m) => m.vec));
      for (const t of x.toks) best.toks.add(t);
    } else {
      clusters.push({ members: [x], rel: { ...x.rel }, centroid: x.vec, toks: new Set(x.toks) });
    }
  }

  // Voqea allaqachon chiqqanmi? Klasterning istalgan a'zosi ilgari nashr
  // etilgan sarlavhaga o'xshasa — bu o'sha voqea, boshqa nashrning so'zi bilan.
  const alreadyPublished = (c) =>
    c.members.some((m) =>
      seenTitles.some((prev) => overlap(m.toks, prev) / Math.min(m.toks.size, prev.size || 1) >= 0.5)
    );

  const repeats = clusters.filter(alreadyPublished).length;
  clusters = clusters.filter((c) => !alreadyPublished(c));

  for (const c of clusters) {
    c.items = c.members.map((m) => m.it);
    delete c.members;
    delete c.centroid;
    delete c.toks;
    // Bosh manba: avvalo havolasi asl maqolaga olib boradigani, keyin obro'lisi.
    const rank = (x) => (x.indirect ? 0 : 40) + x.weight + (x.official ? 6 : 0) + (x.primary ? 5 : 0);
    c.items.sort((a, b) => rank(b) - rank(a));
    c.score = scoreCluster(c);
  }

  clusters.sort((a, b) => b.score - a.score);
  const strong = clusters.filter((c) => c.score >= MIN_SCORE);
  const picked = strong.slice(0, MAX_PER_RUN);

  await writeFile(join(ROOT, "data/clusters.json"), JSON.stringify(picked, null, 2));

  console.log(
    `Xom: ${raw.length} → yangi: ${fresh.length} (${junked} axlat) → mavzuga oid: ${scored.length}` +
    ` → klaster: ${clusters.length + repeats} (${repeats} takror)` +
    ` → ${MIN_SCORE}+ ball: ${strong.length} → tanlandi: ${picked.length}\n`
  );
  for (const c of clusters.slice(0, 12)) {
    const lead = c.items[0];
    const mark = c.score >= MIN_SCORE ? "+" : " ";
    console.log(`  ${mark}[${String(c.score).padStart(6)}] ${lead.sourceName}${c.items.length > 1 ? ` +${c.items.length - 1}` : ""}`);
    console.log(`             ${lead.title.slice(0, 92)}`);
  }
}

// Himoyasiz import butun filtrni ishga tushirib yuborardi.
if (process.argv[1]?.endsWith("filter.mjs")) main();
