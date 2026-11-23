// Nameless Google News items (no `name`, title without " - Publisher") must
// not throw, and one bad item or feed must not drop the rest.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  applyGoogleWeights,
  itemsFromFeed,
  loadSource,
  selectItems,
  sourceLabel,
} from "./collect.mjs";

const NOW = Date.parse("2026-11-23T12:00:00.000Z");
const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

const FIXTURE = `<?xml version="1.0"?>
<rss><channel>
  <item>
    <title>IELTS fee rises in Tashkent this month</title>
    <link>https://news.google.com/rss/articles/CBMiNoPublisher</link>
    <pubDate>Mon, 23 Nov 2026 11:00:00 GMT</pubDate>
    <description>Students pay more for the test.</description>
  </item>
  <item>
    <title>Cambridge updates the on-screen English test - Reuters</title>
    <link>https://news.google.com/rss/articles/CBMiReuters</link>
    <pubDate>Mon, 23 Nov 2026 10:30:00 GMT</pubDate>
    <description>Format change announced.</description>
  </item>
  <item>
    <title>University World News changes the English rule - The Times-Picayune</title>
    <link>https://news.google.com/rss/articles/CBMiHyphen</link>
    <pubDate>Mon, 23 Nov 2026 10:00:00 GMT</pubDate>
    <description>Last separator is the publisher.</description>
  </item>
  <item>
    <title>Best IELTS coaching classes near you - Shiksha</title>
    <link>https://news.google.com/rss/articles/CBMiShiksha</link>
    <pubDate>Mon, 23 Nov 2026 09:30:00 GMT</pubDate>
    <description>Spam listicle.</description>
  </item>
  <item>
    <title>IELTS registration deadline moved -    </title>
    <link>https://news.google.com/rss/articles/CBMiBlank</link>
    <pubDate>Mon, 23 Nov 2026 09:00:00 GMT</pubDate>
    <description>Publisher suffix is empty.</description>
  </item>
  <item>
    <title>Broken &#x110000; entity should not abort the feed</title>
    <link>https://news.google.com/rss/articles/CBMiBroken</link>
    <pubDate>Mon, 23 Nov 2026 08:30:00 GMT</pubDate>
  </item>
  <item>
    <title>PTE Academic fee change announced today</title>
    <link>https://news.google.com/rss/articles/CBMiBadDate</link>
    <pubDate>not-a-real-date</pubDate>
    <description>Invalid date must not throw.</description>
  </item>
  <item>
    <title>Short - BBC</title>
    <link>https://news.google.com/rss/articles/CBMiShort</link>
    <pubDate>Mon, 23 Nov 2026 08:00:00 GMT</pubDate>
    <description>Suffix is too close to the start to be a publisher.</description>
  </item>
</channel></rss>`;

const BLOCKS = ["Shiksha", "YouTube", "Careers360"];

test("sourceLabel falls back from configured name to feed host, then item host", () => {
  assert.equal(sourceLabel({ name: "  Google News: IELTS  " }, "https://news.google.com/x"), "Google News: IELTS");
  assert.equal(sourceLabel({ name: "  ", url: "https://www.thepienews.com/feed/" }, "https://example.com/a"), "thepienews.com");
  assert.equal(sourceLabel({}, "https://www.news.google.com/rss/articles/x"), "news.google.com");
  assert.equal(sourceLabel({}, "not a url"), "Unknown");
});

test("nameless Google News items without a publisher suffix do not throw", () => {
  const nameless = { id: "gn-ielts", q: "IELTS", when: "10d" };
  const items = itemsFromFeed(FIXTURE, nameless, { google: true });
  const byUrl = Object.fromEntries(items.map((it) => [it.url, it]));

  const plain = byUrl["https://news.google.com/rss/articles/CBMiNoPublisher"];
  assert.ok(plain, "item without a publisher suffix is kept");
  assert.equal(plain.sourceName, "news.google.com");
  assert.equal(plain.title, "IELTS fee rises in Tashkent this month");
  assert.equal(typeof plain.sourceName, "string");
  assert.ok(plain.sourceName.trim());

  const reuters = byUrl["https://news.google.com/rss/articles/CBMiReuters"];
  assert.equal(reuters.sourceName, "Reuters");
  assert.equal(reuters.title, "Cambridge updates the on-screen English test");

  const hyphen = byUrl["https://news.google.com/rss/articles/CBMiHyphen"];
  assert.equal(hyphen.sourceName, "The Times-Picayune");
  assert.equal(hyphen.title, "University World News changes the English rule");

  const blank = byUrl["https://news.google.com/rss/articles/CBMiBlank"];
  assert.equal(blank.sourceName, "news.google.com");
  assert.equal(blank.title, "IELTS registration deadline moved -");

  const short = byUrl["https://news.google.com/rss/articles/CBMiShort"];
  assert.equal(short.sourceName, "news.google.com");
  assert.equal(short.title, "Short - BBC");

  assert.equal(byUrl["https://news.google.com/rss/articles/CBMiBroken"], undefined);
  const badDate = byUrl["https://news.google.com/rss/articles/CBMiBadDate"];
  assert.ok(badDate);
  assert.equal(Number.isNaN(Date.parse(badDate.published)), false);
});

test("configured googleNews name is used when the title has no publisher", () => {
  const src = { id: "gn-ielts", name: "Google News: IELTS" };
  const items = itemsFromFeed(FIXTURE, src, { google: true });
  const plain = items.find((it) => it.url.endsWith("CBMiNoPublisher"));
  const reuters = items.find((it) => it.url.endsWith("CBMiReuters"));
  assert.equal(plain.sourceName, "Google News: IELTS");
  assert.equal(reuters.sourceName, "Reuters");
  assert.equal(plain.source, "gn-ielts");
});

test("missing sourceName is still filtered against blockDomains", () => {
  const namedSpam = itemsFromFeed(FIXTURE, { id: "gn-ielts", name: "Google News: IELTS" }, { google: true });
  const selected = selectItems(namedSpam, { maxAgeHours: 336, blockDomains: BLOCKS }, NOW);
  const urls = selected.items.map((it) => it.url);
  assert.equal(urls.some((u) => u.endsWith("CBMiShiksha")), false);
  assert.ok(urls.some((u) => u.endsWith("CBMiNoPublisher")));
  assert.equal(selected.spamSource >= 1, true);

  const fallbackSpam = itemsFromFeed(
    `<rss><channel><item>
      <title>Grant calls open for students</title>
      <link>https://news.google.com/rss/articles/CBMiNamedSpam</link>
      <pubDate>Mon, 23 Nov 2026 11:00:00 GMT</pubDate>
    </item></channel></rss>`,
    { id: "gn-scholar", name: "Shiksha" },
    { google: true },
  );
  const blocked = selectItems(fallbackSpam, { maxAgeHours: 336, blockDomains: BLOCKS }, NOW);
  assert.equal(blocked.items.length, 0);
  assert.equal(blocked.spamSource, 1);

  const emptyName = {
    title: "IELTS centres reopen",
    url: "https://www.youtube.com/watch?v=abc",
    sourceName: "   ",
    published: "2026-11-23T11:00:00.000Z",
    source: "gn-ielts",
    weight: 1,
  };
  const hostBlocked = selectItems([emptyName], { maxAgeHours: 48, blockDomains: BLOCKS }, NOW);
  assert.equal(hostBlocked.items.length, 0);
  assert.equal(hostBlocked.spamSource, 1);
  assert.equal(emptyName.sourceName, "youtube.com");

  const kept = {
    title: "Visa rule changed",
    url: "https://kun.uz/news/1",
    sourceName: undefined,
    published: "2026-11-23T11:00:00.000Z",
    source: "kun",
    weight: 3,
  };
  const hostKept = selectItems([kept], { maxAgeHours: 48, blockDomains: BLOCKS }, NOW);
  assert.equal(hostKept.items.length, 1);
  assert.equal(hostKept.items[0].sourceName, "kun.uz");
});

test("one bad item and one bad feed do not fail the rest", async () => {
  const good = {
    title: "Chevening applications open",
    url: "https://www.theguardian.com/education/chevening",
    sourceName: "The Guardian",
    published: "2026-11-23T11:00:00.000Z",
    source: "gn-scholar",
    weight: 1,
    local: false,
  };
  const evil = {
    get sourceName() { throw new Error("boom"); },
    published: "2026-11-23T11:00:00.000Z",
    url: "https://example.com/evil",
    source: "gn-ielts",
  };
  const old = { ...good, url: "https://example.com/old", published: "2020-01-01T00:00:00.000Z", sourceName: "BBC" };
  const selected = selectItems([evil, old, good, null], { maxAgeHours: 336, blockDomains: BLOCKS }, NOW);
  assert.equal(selected.items.length, 1);
  assert.equal(selected.items[0].url, good.url);
  assert.equal(selected.tooOld, 1);
  assert.equal(selected.dropped, 2);

  const settled = (await Promise.all([
    loadSource("gn-edu-uz", async () => { throw new Error("HTTP 429"); }),
    loadSource("xabar", async () => { throw new Error("fetch failed"); }),
    loadSource("gn-ielts", async () => [good]),
    loadSource("empty", async () => null),
  ])).flat();
  assert.deepEqual(settled, [good]);
});

test("google weights and indirect flag stay on the publisher name", () => {
  const items = itemsFromFeed(FIXTURE, { id: "gn-ielts-uz", name: "Google News: IELTS Uzbekistan", local: true }, { google: true });
  applyGoogleWeights(items, { publishers: { Reuters: 5, "The Guardian": 4 } });
  const reuters = items.find((it) => it.sourceName === "Reuters");
  const plain = items.find((it) => it.url.endsWith("CBMiNoPublisher"));
  assert.equal(reuters.weight, 7);
  assert.equal(reuters.indirect, true);
  assert.equal(plain.weight, 3);
  assert.equal(plain.indirect, true);
  assert.equal(plain.sourceName, "Google News: IELTS Uzbekistan");

  const rss = itemsFromFeed(
    `<rss><channel><item>
      <title>ICEF Monitor outlook - not a publisher suffix</title>
      <link>https://monitor.icef.com/2026/11/outlook/</link>
      <pubDate>Mon, 23 Nov 2026 11:00:00 GMT</pubDate>
    </item></channel></rss>`,
    { id: "icef", name: "ICEF Monitor", url: "https://monitor.icef.com/feed/", weight: 3, primary: true },
  );
  applyGoogleWeights(rss, { publishers: { "ICEF Monitor": 5 } });
  assert.equal(rss[0].title, "ICEF Monitor outlook - not a publisher suffix");
  assert.equal(rss[0].sourceName, "ICEF Monitor");
  assert.equal(rss[0].weight, 3);
  assert.equal(rss[0].indirect, undefined);
  assert.equal(rss[0].primary, true);
});

test("every googleNews entry in sources.json has a name", async () => {
  const cfg = JSON.parse(await readFile(join(ROOT, "sources.json"), "utf8"));
  assert.ok(Array.isArray(cfg.googleNews) && cfg.googleNews.length > 0);
  for (const q of cfg.googleNews) {
    assert.equal(typeof q.name, "string", q.id);
    assert.ok(q.name.trim(), q.id);
  }
});
