/*!
 * Shared pointer engine for the animated hero mark.
 *
 * One rAF loop, whichever variant is mounted. The loop stops itself when the
 * pointer is gone and everything has settled, and restarts on the next pointer
 * event, so an idle page never has a frame callback running.
 *
 * Nothing in here allocates inside the loop.
 */

export const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
export const COARSE  = matchMedia('(hover: none)').matches;

/* The committed mark, in its own 32x32 space. The viewBox is padded so the
   arms have room to extend without overflow tricks: the drawn mark is 32/58
   of the box, so a 140px box renders a ~77px mark. */
export const GEO = { vb: '-13 -13 58 58', c: 16, arm: 14.6, w: 1.85, wAt: 2.45 };

/* Our own --rail stops, nothing borrowed: teal, sky, indigo, fuchsia. */
export const STOPS = ['#2dd4bf', '#38bdf8', '#818cf8', '#e879f9'];

/* Arm axes in screen coordinates (y grows downward): top, right, bottom, left. */
const AXIS = [-Math.PI / 2, 0, Math.PI / 2, Math.PI];

const ENTRANCE_KEY = 'fs-logo-entrance';

export function createEngine(stage, opts) {
  opts = opts || {};
  const near = opts.near || 260;      // px at which the mark starts responding
  const lag  = opts.lag  || 0.12;     // follower easing, per §7.1

  const state = {
    active: false,
    power: 0,        // 0..1 proximity, spring-damped so release overshoots
    x: 0, y: 0,      // raw pointer, px from the mark centre
    fx: 0, fy: 0,    // eased follower, same units
    dist: 1e4,
    angle: 0,
    entrance: 0,     // one-shot flare, 0..1
    arm: [0, 0, 0, 0]
  };

  const subs = [];
  let raf = 0, cx = 0, cy = 0, measured = false;
  let visible = true, dead = false;
  let entranceStart = -1, entranceDone = false;
  let last = 0;

  function measure() {
    const r = stage.getBoundingClientRect();
    cx = r.left + r.width / 2;
    cy = r.top + r.height / 2;
    measured = true;
  }
  function invalidate() { measured = false; }

  function onPoint(e) {
    if (dead || REDUCED) return;
    if (!measured) measure();
    state.x = e.clientX - cx;
    state.y = e.clientY - cy;
    state.dist = Math.sqrt(state.x * state.x + state.y * state.y);
    state.angle = Math.atan2(state.y, state.x);
    state.active = true;
    start();
  }
  function onLeave() { state.active = false; start(); }

  /* Time-independent exponential approach, so a dropped frame does not
     change how fast anything moves. */
  function approach(cur, target, k, dt) {
    return cur + (target - cur) * (1 - Math.exp(-k * dt));
  }

  function frame(now) {
    raf = 0;
    const dt = last ? Math.min((now - last) / 1000, 0.05) : 0.016;
    last = now;

    // one-shot entrance flare, 600ms: 200ms out, 400ms back
    if (entranceStart >= 0) {
      const p = (now - entranceStart) / 600;
      if (p >= 1) { state.entrance = 0; entranceStart = -1; }
      else if (p < 0.333) { const t = p / 0.333; state.entrance = 1 - (1 - t) * (1 - t); }
      else { const t = (p - 0.333) / 0.667; state.entrance = 1 - (t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2); }
    }

    const target = state.active ? Math.max(0, 1 - state.dist / near) : 0;

    // Spring, not a tween: release retracts past rest and settles in ~700ms.
    const stiff = state.active ? 150 : 42;
    const damp  = state.active ? 22  : 8.2;
    state.vel = (state.vel || 0) + (target - state.power) * stiff * dt - (state.vel || 0) * damp * dt;
    state.power += state.vel * dt;
    if (state.power < -0.12) { state.power = -0.12; state.vel = 0; }

    // follower lags the pointer; when the pointer leaves it eases back to centre.
    // With nothing drawn (power at rest, pointer out of range) it snaps instead,
    // so a mouse crossing the far side of the page costs no frames.
    const tx = state.active ? state.x : 0;
    const ty = state.active ? state.y : 0;
    if (target <= 0.001 && state.power <= 0.004) { state.fx = tx; state.fy = ty; }
    else {
      const k = -Math.log(1 - lag) * 60;
      state.fx = approach(state.fx, tx, k, dt);
      state.fy = approach(state.fy, ty, k, dt);
    }

    // per-arm weight: every arm extends, the one facing the pointer extends most
    for (let i = 0; i < 4; i++) {
      let d = Math.cos(state.angle - AXIS[i]);
      state.arm[i] = state.active ? 0.7 + 0.3 * (d > 0 ? d : 0) : 0.85;
    }

    for (let i = 0; i < subs.length; i++) subs[i](state, dt);

    // Rest is measured against the targets, not against zero: a pointer that
    // has stopped moving over a settled mark needs no frames either.
    const rest = Math.abs(target - state.power) < 0.002 && Math.abs(state.vel) < 0.012 &&
                 Math.abs(tx - state.fx) < 0.5 && Math.abs(ty - state.fy) < 0.5;
    if (!dead && visible && (!rest || entranceStart >= 0)) {
      raf = requestAnimationFrame(frame);
    } else {
      state.power = target; state.vel = 0;
      state.fx = tx; state.fy = ty;
      for (let i = 0; i < subs.length; i++) subs[i](state, 0);
      last = 0;
    }
  }

  function start() {
    if (dead || REDUCED || !visible || raf) return;
    if (!last) last = performance.now();
    raf = requestAnimationFrame(frame);
  }
  function stop() { if (raf) { cancelAnimationFrame(raf); raf = 0; } last = 0; }

  function playEntrance() {
    if (entranceDone || REDUCED) return;
    entranceDone = true;
    try {
      if (sessionStorage.getItem(ENTRANCE_KEY)) return;
      sessionStorage.setItem(ENTRANCE_KEY, '1');
    } catch (e) { /* private mode: play it, just do not remember */ }
    entranceStart = performance.now();
    start();
  }

  const io = new IntersectionObserver(function (es) {
    visible = es[0].isIntersecting;
    if (!visible) { state.active = false; stop(); }
    else { measure(); if (COARSE || location.search.indexOf('entrance=1') > -1) playEntrance(); start(); }
  }, { threshold: 0.15 });
  io.observe(stage);

  const passive = { passive: true };
  addEventListener('pointermove', onPoint, passive);
  addEventListener('pointerdown', onPoint, passive);
  addEventListener('pointerup', onLeave, passive);
  addEventListener('pointercancel', onLeave, passive);
  document.addEventListener('pointerleave', onLeave, passive);
  addEventListener('scroll', invalidate, passive);
  addEventListener('resize', invalidate, passive);
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) { state.active = false; stop(); } else { invalidate(); start(); }
  });

  return {
    state: state,
    add: function (cb) { subs.push(cb); cb(state, 0); },
    kick: start,
    destroy: function () { dead = true; stop(); io.disconnect(); }
  };
}

/* Extension per arm, in mark units, for the current state. Shared by the
   variants that move the geometry rather than the light. */
export function armPath(state, maxPct) {
  const c = GEO.c, a = GEO.arm, w = GEO.w, wa = GEO.wAt;
  const p = state.power + state.entrance * 0.9;
  const e0 = a * (1 + maxPct * p * state.arm[0]);
  const e1 = a * (1 + maxPct * p * state.arm[1]);
  const e2 = a * (1 + maxPct * p * state.arm[2]);
  const e3 = a * (1 + maxPct * p * state.arm[3]);
  return 'M' + c + ' ' + (c - e0).toFixed(2) +
         'L' + (c + w) + ' ' + (c - wa) +
         'L' + (c + e1).toFixed(2) + ' ' + c +
         'L' + (c + w) + ' ' + (c + wa) +
         'L' + c + ' ' + (c + e2).toFixed(2) +
         'L' + (c - w) + ' ' + (c + wa) +
         'L' + (c - e3).toFixed(2) + ' ' + c +
         'L' + (c - w) + ' ' + (c - wa) + 'Z';
}
