"""Pulls the JSON-LD and the page logic out of a pre-redesign page, and
rewires that logic from the page's own .uilang toggle to the site-wide one
in paper.js. Everything else in the logic is left exactly as it was.
"""
import re, sys, os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))


def rewire(js):
    n = 0
    # language now comes from the shared toggle
    js, k = re.subn(r"var ui\s*=\s*'uz';\s*try\s*\{\s*ui\s*=\s*localStorage\.getItem\('fs_lang'\)\s*\|\|\s*'uz';\s*\}\s*catch\s*\(e\)\s*\{\}",
                    "var ui=(window.FSPaper&&FSPaper.locale())||'en';", js)
    n += k
    # its own toggle buttons are gone
    js, k = re.subn(r"\n\s*document\.querySelectorAll\('\.uilang button'\)\.forEach\(function\s*\(?b\)?\s*\{\s*b\.classList\.toggle\('on',\s*b\.getAttribute\('data-ui'\)\s*===\s*ui\);?\s*\}\);?", "", js)
    n += k
    js, k = re.subn(r"document\.querySelectorAll\('\.uilang button'\)\.forEach\(function\s*\(b\)\s*\{\s*b\.addEventListener\('click',\s*function\s*\(\)\s*\{[^}]*?ui\s*=\s*b\.getAttribute\('data-ui'\);\s*try\s*\{\s*localStorage\.setItem\('fs_lang',\s*ui\);?\s*\}\s*catch\s*\(e\)\s*\{\}\s*(\w+)\(\);\s*\}\);\s*\}\);",
                    r"document.addEventListener('fs:lang',function(e){ui=e.detail.locale;\1();});", js, flags=re.S)
    n += k
    # paper.js owns <html lang>
    js, k = re.subn(r"\n\s*document\.documentElement\.setAttribute\('lang',\s*ui\);", "", js)
    n += k
    return js, n


def go(name):
    src = os.path.join(ROOT, name, 'index.html')
    s = open(src, encoding='utf-8').read()
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    if ld:
        open(os.path.join(ROOT, 'tools/site', name + '-ld.json'), 'w', encoding='utf-8').write(ld.group(1).strip())
    js = [m.group(1) for m in re.finditer(r'<script(?![^>]*src)(?![^>]*ld\+json)[^>]*>(.*?)</script>', s, re.S)]
    if len(js) > 1:
        out, n = rewire(js[-1])
        open(os.path.join(ROOT, 'tools/site', name + '-logic.js'), 'w', encoding='utf-8').write(out)
        print(f'  {name}: ld={bool(ld)} logic={len(out)}b rewires={n}')
        if 'uilang' in out or 'fs_lang' in out:
            print(f'    !! {name} still references uilang/fs_lang — check by hand')
    else:
        print(f'  {name}: ld={bool(ld)} (no page logic)')


for n in sys.argv[1:]:
    go(n)
