/*!
 * ?logo=bloom — the cheapest variant, and the safe fallback.
 *
 * The mark never moves and never blurs. A single large radial gradient drifts
 * behind the hero with pointer lag, blurred once at 40px, clipped to the hero
 * box. The mark blends in luminosity, so it keeps its own weight but takes the
 * hue of whatever bloom is passing under it — over the plain background there
 * is no saturation to take, so it looks exactly like the static mark.
 *
 * No canvas, no path morph. Only transform and opacity animate.
 */
import { createEngine, STOPS, REDUCED } from './pointer.js';

const AXIS = [-Math.PI / 2, 0, Math.PI / 2, Math.PI];

const CSS = `
html[data-logo="bloom"] .hero{position:relative;isolation:isolate;overflow:hidden}
html[data-logo="bloom"] .hero > .wrap{position:relative;z-index:1}
html[data-logo="bloom"] .logo-stage .spark{mix-blend-mode:luminosity}
.lg-field{position:absolute;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.lg-drift{position:absolute;left:50%;top:50%;width:26rem;height:26rem;margin:-13rem 0 0 -13rem;
  border-radius:50%;filter:blur(40px);opacity:0;will-change:transform,opacity;
  transform:translate3d(0,0,0) scale(.7)}
.lg-drift > i{position:absolute;inset:0;border-radius:50%;opacity:0;will-change:opacity}
`;

export default function bloom(stage, svg) {
  if (REDUCED) return { destroy(){} };

  const hero = stage.closest('.hero') || stage.parentNode;
  const style = document.createElement('style');
  style.textContent = CSS;
  document.head.appendChild(style);

  const field = document.createElement('div');
  field.className = 'lg-field';
  field.setAttribute('aria-hidden', 'true');
  const drift = document.createElement('div');
  drift.className = 'lg-drift';
  const blobs = STOPS.map(c => {
    const i = document.createElement('i');
    i.style.background = 'radial-gradient(circle at 50% 50%,' + c + ' 0%,' + c + '66 40%,transparent 72%)';
    drift.appendChild(i);
    return i;
  });
  field.appendChild(drift);
  hero.insertBefore(field, hero.firstChild);

  const eng = createEngine(stage, { near: 520, lag: 0.12 });
  const w = [0, 0, 0, 0];

  eng.add(function (s) {
    const p = Math.max(0, s.power) + s.entrance * 0.9;
    if (p < 0.004) { drift.style.opacity = '0'; return; }

    let sum = 0;
    for (let i = 0; i < 4; i++) {
      const d = Math.cos(s.angle - AXIS[i]);
      w[i] = d > 0 ? d * d : 0;
      sum += w[i];
    }
    if (sum < 1e-4) { w[0] = w[1] = w[2] = w[3] = 0.25; sum = 1; }
    for (let i = 0; i < 4; i++) blobs[i].style.opacity = (w[i] / sum).toFixed(3);

    drift.style.opacity = (p * 0.6).toFixed(3);
    drift.style.transform = 'translate3d(' + s.fx.toFixed(1) + 'px,' + s.fy.toFixed(1) + 'px,0) scale(' + (0.7 + p * 0.35).toFixed(3) + ')';
  });

  return { destroy(){ eng.destroy(); style.remove(); field.remove(); } };
}
