"""Pushes changed URLs to IndexNow (Bing, Yandex, Seznam, Naver).

Google does not take part, but Yandex does and it has real share among
students here, so a new post or test can be crawled in minutes instead of
waiting for the next Googlebot pass. Ownership is proved by the key file at
the site root — do not delete /25435284112beaba0983abf75c9f8164.txt.

    python3 tools/site/indexnow.py                 # everything in sitemap.xml
    python3 tools/site/indexnow.py URL [URL ...]   # just these
"""
import json, os, re, sys, urllib.request

KEY = '25435284112beaba0983abf75c9f8164'
HOST = 'flarestamina.com'
ENDPOINT = 'https://api.indexnow.org/indexnow'
ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))


def from_sitemap():
    xml = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
    return re.findall(r'<loc>(.*?)</loc>', xml)


def submit(urls):
    urls = [u for u in urls if u.startswith(f'https://{HOST}')]
    if not urls:
        print('nothing to submit')
        return 0
    # the endpoint caps a batch at 10 000 URLs
    for i in range(0, len(urls), 10000):
        batch = urls[i:i + 10000]
        payload = json.dumps({'host': HOST, 'key': KEY,
                              'keyLocation': f'https://{HOST}/{KEY}.txt',
                              'urlList': batch}).encode()
        req = urllib.request.Request(ENDPOINT, data=payload,
                                     headers={'Content-Type': 'application/json; charset=utf-8'})
        with urllib.request.urlopen(req, timeout=45) as r:
            print(f'{r.status} {r.reason} — {len(batch)} URLs')
    return len(urls)


if __name__ == '__main__':
    submit(sys.argv[1:] or from_sitemap())
