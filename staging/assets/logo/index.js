/*!
 * Variant loader. ?logo=flare|bloom|gradient|dots — flare when the parameter is
 * absent or invalid. Only the selected variant is fetched.
 *
 * prefers-reduced-motion: nothing loads at all. The committed SVG in the page
 * is the static, no-JS, reduced-motion mark, and it is already on screen.
 */
import { REDUCED } from './pointer.js';

const VARIANTS = { flare: 1, bloom: 1, gradient: 1, dots: 1 };

const stage = document.getElementById('logoStage');
if (stage) {
  let name = new URLSearchParams(location.search).get('logo');
  if (!name || !VARIANTS[name]) name = 'flare';
  document.documentElement.dataset.logo = name;

  const link = document.getElementById('logoSwitch');
  if (link) {
    link.querySelectorAll('a').forEach(function (a) {
      if (a.dataset.v === name) a.setAttribute('aria-current', 'true');
    });
  }

  if (!REDUCED) {
    import('./' + name + '.js').then(function (m) {
      m.default(stage, stage.querySelector('svg'), stage.querySelector('path'));
      document.documentElement.classList.add('js-ready');
    }).catch(function (e) { console.warn('[logo] variant failed:', e); });
  }
}
