#!/usr/bin/env python3
"""Per-article cover images for /news/.

Every post used to share one og.png, so a link to any article looked like a
link to every other one. This draws a 1200x630 card in the paper palette:
the rail gradient across the top, the headline set in Inter, the category and
date in Plex Mono, and a field of dots whose layout is seeded by the slug — so
two posts never look alike, and nothing on the card claims to be a photograph.
"""
import hashlib, io, os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
PAPER, INK, MUTED, LINE = (255,255,255), (10,10,10), (92,92,92), (232,232,232)
RAIL = [(45,212,191), (56,189,248), (129,140,248), (232,121,249)]  # --rail
ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
FONTS = os.path.join(ROOT, 'assets', 'fonts')

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

def lerp(a, b, t):
    return tuple(round(a[i] + (b[i]-a[i]) * t) for i in range(3))

def rail_color(t):
    """Sample the four-stop gradient at 0..1 using the CSS stop positions."""
    stops = [0.0, 0.32, 0.64, 1.0]
    for i in range(3):
        if t <= stops[i+1]:
            span = stops[i+1] - stops[i]
            return lerp(RAIL[i], RAIL[i+1], (t - stops[i]) / span if span else 0)
    return RAIL[-1]

def draw_cover(title, category, date, slug, out_path):
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # rail across the top
    for x in range(W):
        d.line([(x, 0), (x, 10)], fill=rail_color(x / (W-1)))

    # dot field: a narrow strip down the right edge, clear of the headline
    seed = int(hashlib.sha256(slug.encode()).hexdigest()[:12], 16)
    rnd = seed
    for row in range(19):
        for col in range(5):
            rnd = (rnd * 1103515245 + 12345) & 0x7FFFFFFF
            if rnd % 100 < 28:
                continue
            cx, cy = 1074 + col * 18, 150 + row * 18
            t = row / 18
            r = 2 if rnd % 7 else 3
            d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=rail_color(t))

    # wordmark + category + date
    d.text((64, 62), 'flarestamina', font=font('Inter-Variable.ttf', 26), fill=INK)
    meta = category.upper()
    if date:
        meta += '   \u00b7   ' + date
    d.text((64, 100), meta, font=font('IBMPlexMono-Medium.ttf', 19), fill=MUTED)

    # headline — wrap by measured width, shrink until it fits four lines
    MAXW = 968
    def wrap(f):
        words, lines, cur = title.split(), [], ''
        for w in words:
            trial = (cur + ' ' + w).strip()
            if f.getlength(trial) <= MAXW or not cur:
                cur = trial
            else:
                lines.append(cur); cur = w
        if cur:
            lines.append(cur)
        return lines
    for size in (64, 56, 48, 42, 37):
        f = font('Inter-Variable.ttf', size)
        lines = wrap(f)
        if len(lines) <= 4:
            break
    lines = lines[:4]
    step = int(size * 1.20)
    y = 316 - (len(lines) * step) // 2      # vertically centred in the body area
    for ln in lines:
        d.text((64, y), ln, font=f, fill=INK)
        y += step

    # footer rule + url
    d.line([(64, H-96), (W-64, H-96)], fill=LINE, width=1)
    d.text((64, H-74), 'flarestamina.com/news', font=font('IBMPlexMono-Regular.ttf', 20), fill=MUTED)
    d.text((W-64-190, H-74), 'free IELTS practice', font=font('IBMPlexMono-Regular.ttf', 20), fill=MUTED)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, 'PNG', optimize=True)
    return out_path

if __name__ == '__main__':
    t, c, dt, s, o = sys.argv[1:6]
    print(draw_cover(t, c, dt, s, o))
