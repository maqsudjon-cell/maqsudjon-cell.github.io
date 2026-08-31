/*!
 * ?logo=gradient — light rotating inside the mark.
 *
 * A conic gradient fills the star, masked by the same path the SVG draws, so
 * the silhouette is identical to the committed asset. The gradient angle
 * follows the pointer: one custom property write per frame, no geometry, no
 * canvas, no blur.
 */
import { createEngine, GEO, STOPS, REDUCED } from './pointer.js';

const CSS = `
.lg-conic{position:absolute;inset:0;z-index:3;pointer-events:none;opacity:0;
  will-change:opacity;transition:none;
  background:conic-gradient(from var(--lg-ang,0deg) at 50% 50%,${STOPS[0]},${STOPS[1]} 25%,${STOPS[2]} 50%,${STOPS[3]} 75%,${STOPS[0]} 100%)}
`;

export default function gradient(stage, svg, path) {
  if (REDUCED) return { destroy(){} };

  const d = path.getAttribute('d');
  const mask = "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='" +
    GEO.vb + "'><path fill='white' d='" + d.replace(/#/g, '') + "'/></svg>\")";

  const style = document.createElement('style');
  style.textContent = CSS;
  document.head.appendChild(style);

  const layer = document.createElement('div');
  layer.className = 'lg-conic';
  layer.setAttribute('aria-hidden', 'true');
  layer.style.webkitMaskImage = mask;
  layer.style.maskImage = mask;
  layer.style.webkitMaskSize = layer.style.maskSize = '100% 100%';
  layer.style.webkitMaskRepeat = layer.style.maskRepeat = 'no-repeat';
  stage.appendChild(layer);

  const eng = createEngine(stage, { near: 300 });
  let lastDeg = -999;

  eng.add(function (s) {
    const p = Math.max(0, s.power) + s.entrance * 0.9;
    const deg = Math.round((s.angle * 180 / Math.PI + 90) * 2) / 2;
    if (deg !== lastDeg) { stage.style.setProperty('--lg-ang', deg + 'deg'); lastDeg = deg; }
    layer.style.opacity = (0.3 + p * 0.7).toFixed(3);
  });

  return { destroy(){ eng.destroy(); style.remove(); layer.remove(); } };
}
