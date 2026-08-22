/*!
 * Flarestamina — paper design system behaviour.
 *
 * Pairs with /assets/paper.css. Handles the four things every page needs:
 * theme, language, the mobile sheet and the header hairline. Everything is
 * opt-in through markup, so a page that has no language toggle simply does
 * not get one.
 *
 * Markup contract:
 *   #tgl              theme button, containing #ico-moon and #ico-sun
 *   [data-lang="en"]  language buttons
 *   [data-i18n="key"]      elements whose textContent is swapped
 *   [data-i18n-html="key"] elements whose innerHTML is swapped (links inside copy)
 *   [data-i18n-ph="key"]   inputs whose placeholder is swapped
 *   #burger + #sheet  mobile menu
 *   .hdr              sticky header (gets .on once scrolled)
 *   #acct             sign-in link, replaced by the student's first name
 *   .reveal           fades in on scroll
 *   #yy               current year
 *
 * A page supplies its Uzbek strings as window.FS_UZ = { key: 'matn' }.
 * English is read out of the DOM, so it never has to be repeated in JS.
 */
(function () {
  'use strict';

  var d = document, root = d.documentElement;

  /* ---- theme ------------------------------------------------------------
     Three keys, because pages written at different times read different
     ones. Always write all three or the theme flips as students navigate. */
  var THEME_KEYS = ['fs-paper-theme', 'theme', 'p8-theme'];
  function isDark() { return root.classList.contains('dark') || root.dataset.theme === 'dark'; }
  function syncThemeIco() {
    var dark = isDark(), moon = d.getElementById('ico-moon'), sun = d.getElementById('ico-sun');
    if (moon) moon.style.display = dark ? 'none' : 'block';
    if (sun) sun.style.display = dark ? 'block' : 'none';
    var meta = d.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', dark ? '#000000' : '#ffffff');
  }
  function setTheme(dark) {
    root.classList.toggle('dark', dark);
    root.dataset.theme = dark ? 'dark' : 'light';
    try { THEME_KEYS.forEach(function (k) { localStorage.setItem(k, dark ? 'dark' : 'light'); }); } catch (e) {}
    syncThemeIco();
  }
  syncThemeIco();
  var tgl = d.getElementById('tgl');
  if (tgl) tgl.addEventListener('click', function () { setTheme(!isDark()); });

  /* ---- language ---------------------------------------------------------
     fs-lang is the site-wide key. Some older pages wrote fs_lang; read it as
     a fallback so those students keep their choice. */
  var EN = {}, UZ = window.FS_UZ || {};
  d.querySelectorAll('[data-i18n]').forEach(function (el) { EN[el.getAttribute('data-i18n')] = el.textContent; });
  d.querySelectorAll('[data-i18n-html]').forEach(function (el) { EN[el.getAttribute('data-i18n-html')] = el.innerHTML; });
  d.querySelectorAll('[data-i18n-ph]').forEach(function (el) { EN[el.getAttribute('data-i18n-ph')] = el.placeholder; });

  var locale = 'en';
  try {
    var s = localStorage.getItem('fs-lang') || localStorage.getItem('fs_lang');
    if (s === 'uz' || s === 'en') locale = s;
  } catch (e) {}

  function applyI18n() {
    var tbl = locale === 'uz' ? UZ : EN;
    root.lang = locale;
    d.querySelectorAll('[data-i18n]').forEach(function (el) {
      var v = tbl[el.getAttribute('data-i18n')];
      if (v) el.textContent = v;
    });
    d.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var v = tbl[el.getAttribute('data-i18n-html')];
      if (v) el.innerHTML = v;   /* author-written strings from FS_UZ only */
    });
    d.querySelectorAll('[data-i18n-ph]').forEach(function (el) {
      var v = tbl[el.getAttribute('data-i18n-ph')];
      if (v) el.placeholder = v;
    });
    d.querySelectorAll('[data-lang]').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-lang') === locale);
    });
    d.dispatchEvent(new CustomEvent('fs:lang', { detail: { locale: locale } }));
  }
  d.querySelectorAll('[data-lang]').forEach(function (b) {
    b.addEventListener('click', function () {
      locale = b.getAttribute('data-lang');
      try {
        localStorage.setItem('fs-lang', locale);
        localStorage.setItem('fs_lang', locale);
      } catch (e) {}
      applyI18n();
    });
  });

  /* ---- header + mobile sheet ---- */
  var hdr = d.querySelector('.hdr');
  if (hdr) {
    var onScroll = function () { hdr.classList.toggle('on', window.scrollY > 8); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }
  var burger = d.getElementById('burger'), sheet = d.getElementById('sheet');
  if (burger && sheet) {
    burger.addEventListener('click', function () {
      var open = !sheet.classList.contains('on');
      sheet.classList.toggle('on', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    sheet.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') { sheet.classList.remove('on'); burger.setAttribute('aria-expanded', 'false'); }
    });
  }

  /* ---- signed-in student ---- */
  var acct = d.getElementById('acct');
  if (acct && window.FSAuth) {
    var u = FSAuth.getUser();
    if (u && u.first_name) {
      acct.textContent = u.first_name;
      acct.className = 'hi';
      acct.href = 'https://flarestamina.com/ielts-hub/results.html';
      acct.removeAttribute('data-i18n');
      delete EN['signin'];
    }
  }

  /* ---- year ---- */
  var yy = d.getElementById('yy');
  if (yy) yy.textContent = new Date().getFullYear();

  /* ---- reveal on scroll -------------------------------------------------
     Geometry rather than IntersectionObserver, plus a timeout backstop:
     content must never be left invisible because an observer did not fire. */
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var reveals = [].slice.call(d.querySelectorAll('.reveal'));
  if (reveals.length) {
    if (reduce) {
      reveals.forEach(function (el) { el.classList.add('in'); });
    } else {
      reveals.forEach(function (el, i) { el.style.transitionDelay = (i % 4) * 60 + 'ms'; });
      var ticking = false;
      var check = function () {
        ticking = false;
        var h = window.innerHeight || root.clientHeight;
        for (var i = reveals.length - 1; i >= 0; i--) {
          if (reveals[i].getBoundingClientRect().top < h * 0.92) {
            reveals[i].classList.add('in');
            reveals.splice(i, 1);
          }
        }
      };
      var queue = function () { if (!ticking) { ticking = true; requestAnimationFrame(check); } };
      check();
      window.addEventListener('scroll', queue, { passive: true });
      window.addEventListener('resize', queue);
      window.addEventListener('load', queue);
      setTimeout(function () { reveals.forEach(function (el) { el.classList.add('in'); }); }, 4000);
    }
  }

  applyI18n();

  window.FSPaper = { setTheme: setTheme, isDark: isDark, locale: function () { return locale; } };
})();
