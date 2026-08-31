/*!
 * ?logo=dots — the Vercel-style treatment, adapted to a star.
 *
 * Positions come from logo-dots.json, generated offline by gen-dots.py. The
 * runtime never rasterizes anything: it reads 61 polar-sampled coordinates and
 * draws circles. Dots within 110px of the pointer take hue and brightness, the
 * rest stay at rest.
 *
 * The colour strings are built once into a lookup table, so the frame loop
 * allocates nothing.
 */
import { createEngine, GEO, STOPS, REDUCED } from './pointer.js';

const R_HOT = 110;
const HUES = 24, LEVELS = 10;

const RGB = STOPS.map(h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]);

export default function dots(stage, svg) {
  if (REDUCED) return { destroy(){} };

  const cv = document.createElement('canvas');
  cv.setAttribute('aria-hidden', 'true');
  cv.style.cssText = 'position:absolute;inset:0;z-index:3;pointer-events:none;width:100%;height:100%;opacity:0;transition:opacity .25s';
  stage.appendChild(cv);
  const ctx = cv.getContext('2d');

  let xs, ys, rs, n = 0, size = 0, dpr = 1, scale = 1, off = 0;
  let palette = null, eng = null, fg = '#0a0a0a';

  function readFg() {
    fg = getComputedStyle(document.documentElement).getPropertyValue('--fg').trim() || '#0a0a0a';
    palette = null;
  }

  /* HUES x LEVELS colour strings, built once per theme. Level 0 is the mark's
     own colour, level LEVELS-1 is the fully lit stop. */
  function buildPalette() {
    const probe = document.createElement('canvas').getContext('2d');
    probe.fillStyle = fg;
    const hex = probe.fillStyle;
    const f = [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
    const out = new Array(HUES * LEVELS);
    for (let h = 0; h < HUES; h++) {
      const u = h / HUES * 4;
      const i0 = Math.floor(u) % 4, i1 = (i0 + 1) % 4, k = u - Math.floor(u);
      const r = RGB[i0][0] + (RGB[i1][0] - RGB[i0][0]) * k;
      const g = RGB[i0][1] + (RGB[i1][1] - RGB[i0][1]) * k;
      const b = RGB[i0][2] + (RGB[i1][2] - RGB[i0][2]) * k;
      for (let l = 0; l < LEVELS; l++) {
        const t = l / (LEVELS - 1);
        out[h * LEVELS + l] = 'rgb(' +
          ((f[0] + (Math.min(255, r + 40) - f[0]) * t) | 0) + ',' +
          ((f[1] + (Math.min(255, g + 40) - f[1]) * t) | 0) + ',' +
          ((f[2] + (Math.min(255, b + 40) - f[2]) * t) | 0) + ')';
      }
    }
    palette = out;
  }

  function resize() {
    const r = stage.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2.5);
    size = Math.round(r.width);
    cv.width = Math.round(size * dpr);
    cv.height = Math.round(size * dpr);
    const vb = GEO.vb.split(' ').map(Number);      // -13 -13 58 58
    scale = size / vb[2];
    off = -vb[0];
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function draw(s) {
    if (!palette) buildPalette();
    ctx.clearRect(0, 0, size, size);
    const p = Math.max(0, s.power) + s.entrance * 0.9;
    // pointer position in stage-local px
    const px = size / 2 + s.fx, py = size / 2 + s.fy;
    let hue = ((s.angle + Math.PI) / (2 * Math.PI) * HUES) | 0;
    if (hue < 0) hue = 0; else if (hue >= HUES) hue = HUES - 1;
    const base = hue * LEVELS;

    for (let i = 0; i < n; i++) {
      const cx = (xs[i] + off) * scale;
      const cy = (ys[i] + off) * scale;
      let lvl = 0, grow = 0;
      if (p > 0.004 && s.active) {
        const dx = cx - px, dy = cy - py;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < R_HOT) {
          const t = (1 - d / R_HOT) * p;
          lvl = (t * (LEVELS - 1) + 0.5) | 0;
          grow = t * 0.4;
        }
      } else if (s.entrance > 0.004) {
        lvl = (s.entrance * (LEVELS - 1) + 0.5) | 0;
        grow = s.entrance * 0.35;
      }
      ctx.fillStyle = palette[base + lvl];
      ctx.beginPath();
      ctx.arc(cx, cy, rs[i] * scale * (1 + grow), 0, 6.2832);
      ctx.fill();
    }
  }

  fetch('/staging/assets/logo/logo-dots.json').then(r => r.json()).then(function (data) {
    n = data.dots.length;
    xs = new Float32Array(n); ys = new Float32Array(n); rs = new Float32Array(n);
    for (let i = 0; i < n; i++) { xs[i] = data.dots[i][0]; ys[i] = data.dots[i][1]; rs[i] = data.dots[i][2]; }
    readFg();
    resize();
    // the dot matrix replaces the solid mark; the real SVG stays in the DOM
    svg.style.visibility = 'hidden';
    cv.style.opacity = '1';
    addEventListener('resize', function () { resize(); draw(eng.state); }, { passive: true });
    new MutationObserver(function () { readFg(); draw(eng.state); })
      .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'class'] });
    eng = createEngine(stage, { near: 300 });
    eng.add(draw);
  }).catch(function () { /* no JSON, no canvas: the solid SVG stays as it is */ });

  return { destroy(){ if (eng) eng.destroy(); cv.remove(); svg.style.visibility = ''; } };
}
