#!/usr/bin/env python3
"""Cover cards for the practice tests, so a shared link is not a bare URL.

Test pages carry no Open Graph tags at all, which means a link posted to
Telegram — where nearly every visitor comes from — renders as plain text. This
draws the same paper-palette card the news posts use, tuned for a test: the
skill in mono caps, the test name large, and what the reader gets underneath.
"""
import hashlib, os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
PAPER, INK, MUTED, LINE = (255,255,255), (10,10,10), (92,92,92), (232,232,232)
RAIL = [(45,212,191), (56,189,248), (129,140,248), (232,121,249)]
FONTS = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'fonts')

def font(n, s): return ImageFont.truetype(os.path.join(FONTS, n), s)
def lerp(a, b, t): return tuple(round(a[i] + (b[i]-a[i]) * t) for i in range(3))

def rail_color(t):
    stops = [0.0, 0.32, 0.64, 1.0]
    for i in range(3):
        if t <= stops[i+1]:
            sp = stops[i+1] - stops[i]
            return lerp(RAIL[i], RAIL[i+1], (t - stops[i]) / sp if sp else 0)
    return RAIL[-1]

def draw_test_cover(title, skill, sub, seed_key, out):
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)
    for x in range(W):
        d.line([(x, 0), (x, 10)], fill=rail_color(x / (W-1)))

    rnd = int(hashlib.sha256(seed_key.encode()).hexdigest()[:12], 16)
    for row in range(19):
        for col in range(5):
            rnd = (rnd * 1103515245 + 12345) & 0x7FFFFFFF
            if rnd % 100 < 28: continue
            cx, cy = 1074 + col*18, 150 + row*18
            r = 2 if rnd % 7 else 3
            d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=rail_color(row/18))

    d.text((64, 62), 'flarestamina', font=font('Inter-Variable.ttf', 26), fill=INK)
    d.text((64, 100), skill.upper(), font=font('IBMPlexMono-Medium.ttf', 19), fill=MUTED)

    MAXW = 968
    def wrap(f):
        words, lines, cur = title.split(), [], ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if f.getlength(t) <= MAXW or not cur: cur = t
            else: lines.append(cur); cur = w
        if cur: lines.append(cur)
        return lines
    for size in (66, 58, 50, 44, 38):
        f = font('Inter-Variable.ttf', size)
        lines = wrap(f)
        if len(lines) <= 3: break
    lines = lines[:3]
    step = int(size * 1.20)
    y = 300 - (len(lines) * step) // 2
    for ln in lines:
        d.text((64, y), ln, font=f, fill=INK); y += step

    d.text((64, y + 14), sub, font=font('Inter-Variable.ttf', 26), fill=MUTED)

    d.line([(64, H-96), (W-64, H-96)], fill=LINE, width=1)
    d.text((64, H-74), 'flarestamina.com', font=font('IBMPlexMono-Regular.ttf', 20), fill=MUTED)
    d.text((W-64-250, H-74), 'free · no sign-up', font=font('IBMPlexMono-Regular.ttf', 20), fill=MUTED)

    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    img.save(out, 'PNG', optimize=True)
    return out

if __name__ == '__main__':
    print(draw_test_cover(*sys.argv[1:6]))
