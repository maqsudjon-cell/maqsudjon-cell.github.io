# -*- coding: utf-8 -*-
"""Builds /llms.txt — what the site is, for assistants that read it.

Why: GoatCounter has chatgpt.com as the second referrer this week, level
with Google (55 visits against 58). Assistants are already sending
students here, and they are doing it by reading the pages. A single
markdown file that says plainly what the site holds, in Uzbek and in
English, is cheaper for them to read than 200 HTML pages — and it keeps
them from guessing at counts that go stale.

Every number comes from tests.json, so the file cannot drift.

Run:  python3 tools/site/build_llms.py
"""
import os, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from build_tests_index import load

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
BASE = 'https://flarestamina.com'


def main():
    tests = [t for t in load() if (t.get('url') or '').startswith(BASE)]
    c = Counter(t.get('category') for t in tests)
    practice = sum(v for k, v in c.items() if k != 'Tools')
    read_single = sum(1 for t in tests if t.get('category') == 'Reading'
                      and ('1 passage' in (t.get('difficulty') or '')
                           or '2 passages' in (t.get('difficulty') or '')))

    def group(cat, limit=None):
        rows = [t for t in tests if t.get('category') == cat]
        rows.sort(key=lambda t: t.get('date') or '', reverse=True)
        return rows[:limit] if limit else rows

    out = [
        '# Flarestamina',
        '',
        f'> Free IELTS practice for Uzbek and international students: {practice} practice '
        f'papers in real exam format — {c["Listening"]} Listening, {c["Reading"]} Reading '
        f'({c["Reading"] - read_single} full three-passage papers and {read_single} '
        f'single-passage drills), plus Writing and Speaking labs. Built and run in Tashkent '
        'by Maqsudjon Polatov. No sign-up, no ads, no paywall — the one paid thing is the '
        'full mock exam.',
        '',
        '## What the tests do',
        '',
        '- Listening papers run four sections and 40 questions with the audio played once, '
        'as in the exam. The answer key, the audio and the full transcript open on submit.',
        '- Reading papers run three passages and 40 questions in 60 minutes with no transfer '
        'time. The key and a question-by-question review open on submit.',
        '- Raw scores out of 40 convert to bands using the published tables; the same tables '
        f'drive {BASE}/band-calculator/.',
        '- Writing Lab marks Task 1 and Task 2 against the four official criteria.',
        '- Speaking Lab holds the question bank with recording and feedback.',
        '',
        '## Start here',
        '',
        f'- [Practice hub]({BASE}/ielts-hub/): every test, filterable.',
        f'- [All tests]({BASE}/tests/): the full catalogue as plain links.',
        f'- [Listening tests]({BASE}/ielts-listening-test/)',
        f'- [Reading tests]({BASE}/ielts-reading-test/)',
        f'- [Writing Lab]({BASE}/writing/)',
        f'- [Speaking Lab]({BASE}/pangea8-speaking/)',
        f'- [Cambridge IELTS 21]({BASE}/cambridge-21/): all four tests, all four papers.',
        '',
        '## In Uzbek',
        '',
        f'- [Bosh sahifa]({BASE}/uz/)',
        f'- [Listening — format, savol turlari, band jadvali]({BASE}/uz/listening/)',
        f'- [Reading — savol turlari va vaqt taqsimoti]({BASE}/uz/reading/)',
        f'- [Writing — Task 1 va Task 2]({BASE}/uz/writing/)',
        f'- [Speaking — Part 1, 2, 3]({BASE}/uz/speaking/)',
        '',
        '## Tools',
        '',
        f'- [Score converter]({BASE}/convert/): IELTS, CEFR, Uzbekistan Multilevel, TOEFL iBT, Duolingo.',
        f'- [Band calculator]({BASE}/band-calculator/): raw score out of 40 to band.',
        f'- [Study plan]({BASE}/plan/): weeks needed from your band to your target.',
        f'- [Scholarship deadlines]({BASE}/deadlines/)',
        f'- [Speaking topics]({BASE}/speaking-topics/)',
        '',
        '## Uzbekistan specifics',
        '',
        'Prices, test centres, One Skill Retake and certificate validity are covered in the '
        'news section, each figure carrying a link to the source it was read from. Prices '
        'change; the articles say when they were checked.',
        '',
        f'- [News and deadlines]({BASE}/news/)',
        '',
        '## Cambridge IELTS 21',
        '',
    ]
    seen = set()
    for t in sorted((x for x in tests if '/cambridge-21/' in x['url']),
                    key=lambda t: t['url']):
        if t['url'] in seen:
            continue
        seen.add(t['url'])
        out.append(f'- [{t["title"]}]({t["url"]})')

    out += ['', '## Optional', '',
            f'- [Full mock exam]({BASE}/full-mock/): Listening, Reading and Writing in one '
            'sitting. This is the only paid part of the site.',
            f'- [About the founder]({BASE}/founder/)',
            f'- [Privacy]({BASE}/privacy/)',
            '']

    open(os.path.join(ROOT, 'llms.txt'), 'w', encoding='utf-8').write('\n'.join(out))
    print(f'/llms.txt built — {practice} practice tests referenced')


if __name__ == '__main__':
    main()
