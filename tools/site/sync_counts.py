# -*- coding: utf-8 -*-
"""Rewrites the hardcoded test counts on the homepage from tests.json.

Why this exists: the same number is typed into the homepage mock, the hub
title and the hub description, and it goes stale every time a test is
added. The hub spent months telling students it had 112 tests while it
had 144, and the homepage mock still said 113. Nobody notices, because
nobody re-reads their own hero.

Marked spans carry the count so this can find them without guessing:
    <i data-count="all">144</i>  <em data-count="listening">78</em>

Run after adding tests:  python3 tools/site/sync_counts.py
"""
import os, re, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from build_tests_index import load

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))


def main():
    tests = [t for t in load() if (t.get('url') or '').startswith('https://flarestamina.com')]
    c = Counter(t.get('category') for t in tests)
    counts = {
        'all': sum(v for k, v in c.items() if k != 'Tools'),
        'listening': c['Listening'],
        'reading': c['Reading'],
    }

    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    before = s
    for key, n in counts.items():
        s = re.sub(rf'(<(\w+) data-count="{key}">)\d+(</\2>)', rf'\g<1>{n}\g<3>', s)
    if s == before:
        print('nothing to sync — are the data-count attributes still there?')
        return 1
    open(p, 'w', encoding='utf-8').write(s)
    print('homepage counts: ' + ', '.join(f'{k}={v}' for k, v in counts.items()))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
