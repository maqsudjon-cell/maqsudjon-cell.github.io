/*!
 * ?logo=flare — the default. The mark is a light source.
 *
 * Idle it is the solid brand colour and nothing moves. As the pointer nears,
 * the four arms extend by up to 18%, a hot core opens in the centre, and a
 * chromatic bloom expands behind the mark with its hue following the pointer
 * angle. A faint secondary sparkle crosses at 45 degrees and fades. Release
 * retracts the arms in ~700ms with a slight overshoot.
 *
 * Arm extension is a path morph, not four scaled arm paths: the mark has eight
 * vertices, so rebuilding `d` is a single attribute write per frame and the
 * waist stays exactly where it is. Scaling four separate arms leaves a visible
 * step where each arm meets the centre mass.
 */
import { createEngine, armPath, STOPS, REDUCED } from './pointer.js';

const AXIS = [-Math.PI / 2, 0, Math.PI / 2, Math.PI];
const RGB = STOPS.map(h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]);

const CSS = `
.lg-bloom{position:absolute;inset:-45%;z-index:1;pointer-events:none;contain:paint;
  transform:translate3d(0,0,0) scale(.55);will-change:transform,opacity;opacity:0}
.lg-blob{position:absolute;inset:0;border-radius:50%;opacity:0;filter:blur(24px);
  will-change:opacity;mix-blend-mode:normal}
.lg-core{opacity:0;transform-origin:16px 16px}
.lg-second{opacity:0;transform-origin:16px 16px}
`;

export default function flare(stage, svg, path) {
  if (REDUCED) return { destroy(){} };   // static mark only, no layers, no rAF
  const doc = document;
  const style = doc.createElement('style');
  style.textContent = CSS;
  doc.head.appendChild(style);

  const bloom = doc.createElement('div');
  bloom.className = 'lg-bloom';
  bloom.setAttribute('aria-hidden', 'true');
  const blobs = STOPS.map(c => {
    const b = doc.createElement('div');
    b.className = 'lg-blob';
    b.style.background = 'radial-gradient(circle at 50% 50%,' + c + ' 0%,' + c + '55 38%,transparent 70%)';
    bloom.appendChild(b);
    return b;
  });
  stage.insertBefore(bloom, svg);

  const NS = 'http://www.w3.org/2000/svg';
  const core = doc.createElementNS(NS, 'path');
  core.setAttribute('class', 'lg-core');
  core.setAttribute('d', path.getAttribute('d'));
  svg.appendChild(core);

  const second = doc.createElementNS(NS, 'path');
  second.setAttribute('class', 'lg-second');
  second.setAttribute('d', path.getAttribute('d'));
  svg.appendChild(second);

  // --fg changes when the theme toggle flips; read it then, not every frame.
  let fg = [10, 10, 10];
  function readFg() {
    const v = getComputedStyle(document.documentElement).getPropertyValue('--fg').trim();
    const m = v.match(/#([0-9a-f]{3,6})/i);
    if (!m) return;
    let h = m[1];
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    fg = [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  }
  readFg();
  new MutationObserver(readFg).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'class'] });

  const eng = createEngine(stage, { near: 280 });
  const w = [0, 0, 0, 0];
  let sparkAt = -1, lastPower = 0;

  eng.add(function (s, dt) {
    const p = Math.max(0, s.power) + s.entrance * 0.9;

    // geometry: arms reach, waist stays put
    path.setAttribute('d', armPath(s, 0.18));

    if (p < 0.004) {
      bloom.style.opacity = '0';
      core.style.opacity = '0';
      second.style.opacity = '0';
      path.style.fill = '';
      lastPower = p;
      return;
    }

    // hue follows the pointer angle across our four rail stops
    let sum = 0;
    for (let i = 0; i < 4; i++) {
      const d = Math.cos(s.angle - AXIS[i]);
      w[i] = d > 0 ? d * d : 0;
      sum += w[i];
    }
    if (sum < 1e-4) { w[0] = w[1] = w[2] = w[3] = 0.25; sum = 1; }

    let r = 0, g = 0, b = 0;
    for (let i = 0; i < 4; i++) {
      const k = w[i] / sum;
      blobs[i].style.opacity = (k * 0.9).toFixed(3);
      r += RGB[i][0] * k; g += RGB[i][1] * k; b += RGB[i][2] * k;
    }

    // bloom expands, never re-blurs: transform and opacity only
    bloom.style.opacity = (p * 0.85).toFixed(3);
    bloom.style.transform = 'translate3d(' + (s.fx * 0.06).toFixed(1) + 'px,' + (s.fy * 0.06).toFixed(1) + 'px,0) scale(' + (0.55 + p * 0.6).toFixed(3) + ')';

    // the mark itself takes the light
    const t = p * 0.85;
    path.style.fill = 'rgb(' + ((fg[0] + (r - fg[0]) * t) | 0) + ',' + ((fg[1] + (g - fg[1]) * t) | 0) + ',' + ((fg[2] + (b - fg[2]) * t) | 0) + ')';

    // hot core
    core.style.opacity = (p * 0.9).toFixed(3);
    core.style.fill = 'rgb(' + Math.min(255, (r + 90) | 0) + ',' + Math.min(255, (g + 90) | 0) + ',' + Math.min(255, (b + 90) | 0) + ')';
    core.style.transform = 'scale(' + (0.30 + p * 0.16).toFixed(3) + ')';

    // secondary sparkle: fires on a rising edge, crosses at 45 degrees, fades
    const now = performance.now();
    if (p > 0.42 && lastPower <= 0.42 && now - sparkAt > 900) sparkAt = now;
    lastPower = p;
    if (sparkAt > 0) {
      const q = (now - sparkAt) / 620;
      if (q >= 1) { sparkAt = -1; second.style.opacity = '0'; }
      else {
        const travel = -9 + q * 18;
        second.style.opacity = (Math.sin(q * Math.PI) * 0.55).toFixed(3);
        second.style.fill = 'rgb(' + (r | 0) + ',' + (g | 0) + ',' + (b | 0) + ')';
        second.style.transform = 'translate(' + travel.toFixed(2) + 'px,' + (-travel).toFixed(2) + 'px) rotate(45deg) scale(.3)';
      }
    }
  });

  return { destroy(){ eng.destroy(); style.remove(); bloom.remove(); core.remove(); second.remove(); } };
}
