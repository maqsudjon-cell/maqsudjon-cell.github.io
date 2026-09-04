#!/usr/bin/env python3
"""covers.py — lenta xabarlari uchun muqova rasmi.

Chizma .github/scripts/build_community.py dagi og_image bilan bir xil "paper"
uslubda: oq fon, to'rt burchakli uchqun, mono kicker, Inter sarlavha va
gradient chiziq. Ikkalasi bir xil ko'rinishda qolishi kerak.

Faqat YETISHMAYOTGAN rasmlarni chizadi — har yugurishda hammasini qayta
chizish git tarixini shishiradi (ailenta'da PNG muqovalar 9 soatda 145 MB
bergan; shuning uchun bu yerda ham rasm bir marta chiziladi).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_SANS = os.path.join(ROOT, 'assets/fonts/Inter-Variable.ttf')
FONT_MONO = os.path.join(ROOT, 'assets/fonts/IBMPlexMono-Regular.ttf')
DATA = os.path.join(ROOT, 'newsbot/data/posts.json')
OUT = os.path.join(ROOT, 'news/x')

KICKER = {
    'exam-update': 'I M T I H O N',
    'fees':        'N A R X',
    'deadline':    'M U D D A T',
    'guide':       'F O Y D A L I',
}


def inter(size, weight='Medium'):
    from PIL import ImageFont
    f = ImageFont.truetype(FONT_SANS, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def cover(post, path):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    FG, MUTED, SUBTLE = '#0a0a0a', '#5c5c5c', '#8a8a8a'
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)

    # to'rt uchli uchqun — favicon.svg bilan bir xil nisbatda
    cx, cy, s_ = 72 + 28, 64 + 28, 28
    waist = s_ * 0.153
    d.polygon([(cx, cy - s_), (cx + waist, cy - waist), (cx + s_, cy), (cx + waist, cy + waist),
               (cx, cy + s_), (cx - waist, cy + waist), (cx - s_, cy), (cx - waist, cy - waist)], fill=FG)

    fk = ImageFont.truetype(FONT_MONO, 16)
    d.text((72, 196), KICKER.get(post.get('category'), 'L E N T A'), font=fk, fill=SUBTLE)

    title = post['title']
    size = 64 if len(title) <= 34 else (52 if len(title) <= 52 else 44)
    ft = inter(size, 'Medium')
    lines, cur = [], ''
    for w in title.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=ft) > W - 200 and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    lines = lines[:4]
    y = 232
    for ln in lines:
        d.text((72, y), ln, font=ft, fill=FG)
        y += int(size * 1.16)

    # gradient chiziq: teal -> sky -> indigo -> fuchsia
    stops = [(0.0, (45, 212, 191)), (0.32, (56, 189, 248)), (0.64, (129, 140, 248)), (1.0, (232, 121, 249))]
    rail_y, rail_w = min(y + 22, H - 150), 280
    for i in range(rail_w):
        t = i / (rail_w - 1)
        for j in range(len(stops) - 1):
            a0, c0 = stops[j]; a1, c1 = stops[j + 1]
            if a0 <= t <= a1:
                k = (t - a0) / (a1 - a0)
                col = tuple(int(c0[n] + (c1[n] - c0[n]) * k) for n in range(3))
                break
        d.rectangle([72 + i, rail_y, 72 + i, rail_y + 3], fill=col)

    fr = inter(20, 'Regular')
    d.text((72, H - 78), ('Manba: ' + post['source']['name'])[:64], font=fr, fill=MUTED)
    url = 'flarestamina.com/news/lenta'
    d.text((W - 72 - d.textlength(url, font=inter(20, 'Medium')), H - 78), url,
           font=inter(20, 'Medium'), fill=FG)

    img.save(path, 'PNG', optimize=True)


def main():
    try:
        posts = json.load(open(DATA, encoding='utf8'))
    except Exception:
        print('posts.json yo\'q — muqova chizilmadi')
        return
    made = 0
    for p in posts[:120]:
        d = os.path.join(OUT, p['slug'])
        if not os.path.isdir(d):
            continue
        path = os.path.join(d, 'cover.png')
        if os.path.exists(path):
            continue
        try:
            cover(p, path)
            made += 1
        except Exception as e:
            print(f'  . {p["slug"]}: {e}', file=sys.stderr)
    print(f'Muqova: {made} ta yangi rasm')


if __name__ == '__main__':
    main()
