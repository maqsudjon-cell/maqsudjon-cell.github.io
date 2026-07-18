/* Flarestamina News — community layer (Articles + Ideas & Advice)
 * Backend: Firestore REST, project pangeya-essay (public web key, same model as the essay lab).
 * Collections: articles {title,body,author,center,link,date,type}
 *              advice {text,author,date,likes}
 *              advice_comments {postId,text,author,date}
 * Seed articles: /news/articles-seed.json (repo-versioned, merged into the list).
 */
(function () {
  'use strict';

  var FS = 'https://firestore.googleapis.com/v1/projects/pangeya-essay/databases/(default)/documents';
  var KEY = 'AIzaSyBnmbg7CyLki-M1E4rxPevJ741yTykliDA';
  var LIKED_KEY = 'fs_advice_liked';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };

  /* ---------- helpers ---------- */
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function paras(s) {
    return String(s || '').split(/\n{2,}/).map(function (p) {
      return '<p>' + esc(p).replace(/\n/g, '<br>') + '</p>';
    }).join('');
  }
  function fmtDate(iso) {
    try {
      var d = new Date(iso);
      var m = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      return d.getDate() + ' ' + m[d.getMonth()] + ' ' + d.getFullYear();
    } catch (e) { return ''; }
  }
  function safeUrl(u) {
    u = String(u || '').trim();
    if (!u) return '';
    if (!/^https?:\/\//i.test(u)) u = 'https://' + u;
    try { new URL(u); return u; } catch (e) { return ''; }
  }
  function fv(doc, f) { // firestore field value
    var v = doc.fields && doc.fields[f];
    if (!v) return '';
    return v.stringValue != null ? v.stringValue :
           v.integerValue != null ? parseInt(v.integerValue, 10) :
           v.doubleValue != null ? v.doubleValue :
           v.booleanValue != null ? v.booleanValue : '';
  }
  function docId(doc) { var p = (doc.name || '').split('/'); return p[p.length - 1]; }

  // orderField null => no orderBy (avoids composite-index requirement when combined with a where filter)
  function runQuery(collection, orderField, limit, where) {
    var sq = { from: [{ collectionId: collection }], limit: limit };
    if (orderField) sq.orderBy = [{ field: { fieldPath: orderField }, direction: 'DESCENDING' }];
    if (where) sq.where = where;
    return fetch(FS + ':runQuery?key=' + KEY, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ structuredQuery: sq })
    }).then(function (r) { return r.json(); }).then(function (rows) {
      if (!Array.isArray(rows)) return [];
      return rows.filter(function (r) { return r.document; }).map(function (r) { return r.document; });
    });
  }
  function createDoc(collection, fields) {
    return fetch(FS + '/' + collection + '?key=' + KEY, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fields: fields })
    }).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); });
  }
  function user() {
    try { return (window.FSAuth && FSAuth.getUser()) || null; } catch (e) { return null; }
  }
  function userName() {
    var u = user();
    if (!u) return null;
    return ((u.first_name || '') + ' ' + (u.last_name || '')).trim() || 'Student';
  }
  function track(ev) {
    if (window.goatcounter && goatcounter.count) goatcounter.count({ path: 'event/' + ev, event: true });
  }

  /* ---------- mode switcher ---------- */
  var MODES = ['news', 'articles', 'ideas'];
  function setMode(m, push) {
    if (MODES.indexOf(m) < 0) m = 'news';
    MODES.forEach(function (x) {
      var sec = $('#mode-' + x);
      if (sec) sec.hidden = (x !== m);
      var btn = $('.modes button[data-m="' + x + '"]');
      if (btn) btn.classList.toggle('active', x === m);
    });
    if (push) { try { history.replaceState(null, '', m === 'news' ? '/news/' : '/news/#' + m); } catch (e) {} }
    if (m === 'articles') loadArticles();
    if (m === 'ideas') loadAdvice();
  }
  $$('.modes button').forEach(function (b) {
    b.addEventListener('click', function () { setMode(b.getAttribute('data-m'), true); });
  });

  /* ---------- ARTICLES ---------- */
  var articlesLoaded = false;
  function isBoth(a) { return !!(a.title_uz && a.body_uz); }
  // which language to show first: bilingual -> EN; else the article's own language
  function pickLang(a) { return isBoth(a) ? 'en' : (a.lang === 'uz' ? 'uz' : 'en'); }
  function aTitle(a, l) { return (l === 'uz' && a.title_uz) ? a.title_uz : a.title; }
  function aBody(a, l) { return (l === 'uz' && a.body_uz) ? a.body_uz : a.body; }

  function articleCard(a) {
    var l = pickLang(a);
    var title = aTitle(a, l), body = aBody(a, l);
    var linkText = a.link ? esc(a.link.replace(/^https?:\/\//i, '').replace(/\/$/, '')) : '';
    // The whole card becomes an <a> once the article has its own page — and an <a>
    // may not contain another <a>, so the author link renders as plain text there.
    var links = !a.link ? ''
      : a.slug ? '<span class="a-link">' + linkText + '</span>'
               : '<a class="a-link" href="' + esc(a.link) + '" target="_blank" rel="noopener nofollow ugc">' + linkText + '</a>';
    var badge = isBoth(a) ? '<span class="lang-badge">EN · UZ</span>'
                          : '<span class="lang-badge">' + (l === 'uz' ? 'UZ' : 'EN') + '</span>';
    if (a.featured) badge = '<span class="feat-badge">★ featured</span>' + badge;
    var inner =
      '<div class="meta"><span class="chip article">article</span>' + badge + '<time>' + esc(fmtDate(a.date)) + '</time></div>' +
      '<h2>' + esc(title) + '</h2>' +
      '<p class="sum">' + esc(body.slice(0, 180)) + (body.length > 180 ? '…' : '') + '</p>' +
      '<div class="a-author"><span class="a-ava">' + esc((a.author || '?').charAt(0).toUpperCase()) + '</span>' +
      '<div><b>' + esc(a.author) + '</b>' +
      (a.center ? '<i>' + esc(a.center) + '</i>' : '') + '</div>' + links + '</div>' +
      '<span class="a-read-btn">read article →</span>';
    // Once the generator has built the article its own page, link straight to it:
    // a real crawlable URL the author can share. Until then, fall back to the modal.
    if (a.slug) return '<a class="a-card" href="/news/a/' + esc(a.slug) + '/">' + inner + '</a>';
    return '<article class="a-card" data-aid="' + esc(a.id) + '">' + inner + '</article>';
  }

  function openArticle(a) {
    var l = pickLang(a);
    var links = a.link ? '<a href="' + esc(a.link) + '" target="_blank" rel="noopener nofollow ugc">' + esc(a.link) + '</a>' : '';
    var ov = document.createElement('div');
    ov.className = 'a-overlay';
    var toggle = isBoth(a)
      ? '<div class="a-lang"><button data-l="en" class="on">English</button><button data-l="uz">Oʻzbekcha</button></div>'
      : '';
    function render() {
      return '<div class="meta"><span class="chip article">article</span><time>' + esc(fmtDate(a.date)) + '</time></div>' +
        toggle +
        '<h1 class="a-h">' + esc(aTitle(a, l)) + '</h1>' +
        '<div class="a-author big"><span class="a-ava">' + esc((a.author || '?').charAt(0).toUpperCase()) + '</span>' +
        '<div><b>' + esc(a.author) + '</b>' + (a.center ? '<i>' + esc(a.center) + '</i>' : '') + '</div></div>' +
        '<div class="a-body a-b">' + paras(aBody(a, l)) + '</div>' +
        (links ? '<p class="a-foot">Author link: ' + links + '</p>' : '') +
        '<div class="a-share"><a href="https://t.me/share/url?url=' + encodeURIComponent('https://flarestamina.com/news/#articles') + '&text=' + encodeURIComponent('"' + aTitle(a, l) + '" — ' + a.author + ' (Flarestamina News)') + '" target="_blank" rel="noopener">↗ share on telegram</a></div>';
    }
    ov.innerHTML = '<div class="a-modal"><button class="a-close" aria-label="Close">✕</button><div class="a-inner">' + render() + '</div></div>';
    function close() { document.body.removeChild(ov); document.body.style.overflow = ''; }
    function bind() {
      $$('.a-lang button', ov).forEach(function (b) {
        b.addEventListener('click', function () {
          l = b.getAttribute('data-l');
          $('.a-inner', ov).innerHTML = render();
          bind();
        });
      });
    }
    ov.addEventListener('click', function (e) { if (e.target === ov) close(); });
    $('.a-close', ov).addEventListener('click', close);
    bind();
    document.body.appendChild(ov);
    document.body.style.overflow = 'hidden';
    track('article-read');
  }

  function loadArticles() {
    if (articlesLoaded) return;
    articlesLoaded = true;
    var box = $('#articles-list');
    box.innerHTML = '<p class="c-loading">loading articles…</p>';
    var all = [];
    var seedReq = fetch('/news/articles-seed.json').then(function (r) { return r.json(); })
      .then(function (j) { return (j.articles || []); }).catch(function () { return []; });
    // id -> slug map produced by .github/scripts/build_community.py
    var idxReq = fetch('/news/articles-index.json').then(function (r) { return r.json(); })
      .then(function (j) { return (j.articles || {}); }).catch(function () { return {}; });
    // paid "featured teacher" slots — author slugs listed in featured.json get pinned + starred
    var featReq = fetch('/news/featured.json').then(function (r) { return r.json(); })
      .then(function (j) { return (j.authors || []); }).catch(function () { return []; });
    var fsReq = runQuery('articles', 'date', 60).then(function (docs) {
      return docs.map(function (d) {
        return { id: docId(d), title: fv(d, 'title'), body: fv(d, 'body'),
                 title_uz: fv(d, 'title_uz'), body_uz: fv(d, 'body_uz'), lang: fv(d, 'lang'),
                 author: fv(d, 'author'), center: fv(d, 'center'), link: safeUrl(fv(d, 'link')),
                 date: fv(d, 'date'), hidden: fv(d, 'hidden') === true };
      }).filter(function (a) { return a.title && a.body && a.title !== '__test__' && !a.hidden; });
    }).catch(function () { return []; });
    Promise.all([seedReq, fsReq, idxReq, featReq]).then(function (res) {
      var idx = res[2] || {}, feat = res[3] || [];
      all = res[1].concat(res[0]);
      all.forEach(function (a) {
        if (idx[a.id]) { a.slug = idx[a.id].slug; a.author_slug = idx[a.id].author_slug; }
        a.featured = feat.indexOf(a.author_slug) >= 0;
      });
      all.sort(function (a, b) {
        if (a.featured !== b.featured) return a.featured ? -1 : 1;
        return (b.date || '').localeCompare(a.date || '');
      });
      if (!all.length) { box.innerHTML = '<p class="c-loading">No articles yet — be the first: <a href="/writearticle/">write one</a></p>'; return; }
      box.innerHTML = all.map(articleCard).join('');
      // only the not-yet-generated cards need the modal fallback
      $$('article.a-card[data-aid]', box).forEach(function (el) {
        el.addEventListener('click', function (e) {
          if (e.target.closest('.a-link')) return;
          var a = all.filter(function (x) { return String(x.id) === el.getAttribute('data-aid'); })[0];
          if (a) openArticle(a);
        });
      });
    });
  }

  /* ---------- IDEAS & ADVICE ---------- */
  var adviceLoaded = false;
  var likedMap = {};
  try { likedMap = JSON.parse(localStorage.getItem(LIKED_KEY) || '{}'); } catch (e) {}

  function adviceItem(d) {
    var id = docId(d);
    var likes = fv(d, 'likes') || 0;
    var liked = !!likedMap[id];
    return '<div class="adv" data-id="' + esc(id) + '">' +
      '<div class="adv-head"><span class="a-ava">' + esc((fv(d, 'author') || '?').charAt(0).toUpperCase()) + '</span>' +
      '<b>' + esc(fv(d, 'author') || 'Student') + '</b><time>' + esc(fmtDate(fv(d, 'date'))) + '</time></div>' +
      '<div class="adv-text">' + paras(fv(d, 'text')) + '</div>' +
      '<div class="adv-actions">' +
      '<button class="like' + (liked ? ' on' : '') + '" data-id="' + esc(id) + '">♥ <span>' + likes + '</span></button>' +
      '<button class="cbtn" data-id="' + esc(id) + '">💬 comments</button>' +
      '<a class="shr" href="https://t.me/share/url?url=' + encodeURIComponent('https://flarestamina.com/news/#ideas') + '&text=' + encodeURIComponent('"' + fv(d, 'text').slice(0, 160) + '" — ' + (fv(d, 'author') || 'Student') + ' (Flarestamina)') + '" target="_blank" rel="noopener">↗ share</a>' +
      '</div><div class="adv-comments" hidden></div></div>';
  }

  function loadAdvice(force) {
    if (adviceLoaded && !force) return;
    adviceLoaded = true;
    var box = $('#advice-list');
    box.innerHTML = '<p class="c-loading">loading…</p>';
    runQuery('advice', 'date', 100).then(function (docs) {
      docs = docs.filter(function (d) { return fv(d, 'text') && fv(d, 'hidden') !== true; });
      if (!docs.length) { box.innerHTML = '<p class="c-loading">No posts yet — write the first idea 👇</p>'; return; }
      box.innerHTML = docs.map(adviceItem).join('');
      bindAdvice(box);
    }).catch(function () { box.innerHTML = '<p class="c-loading">Could not load — refresh the page.</p>'; });
  }

  function bindAdvice(box) {
    $$('.like', box).forEach(function (b) {
      b.addEventListener('click', function () {
        var id = b.getAttribute('data-id');
        if (likedMap[id]) return;
        likedMap[id] = 1;
        try { localStorage.setItem(LIKED_KEY, JSON.stringify(likedMap)); } catch (e) {}
        b.classList.add('on');
        var n = $('span', b); n.textContent = (parseInt(n.textContent, 10) || 0) + 1;
        fetch(FS + ':commit?key=' + KEY, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ writes: [{ transform: {
            document: 'projects/pangeya-essay/databases/(default)/documents/advice/' + id,
            fieldTransforms: [{ fieldPath: 'likes', increment: { integerValue: '1' } }]
          } }] })
        }).catch(function () {});
        track('advice-like');
      });
    });
    $$('.cbtn', box).forEach(function (b) {
      b.addEventListener('click', function () {
        var wrapEl = b.closest('.adv');
        var cbox = $('.adv-comments', wrapEl);
        if (!cbox.hidden) { cbox.hidden = true; return; }
        cbox.hidden = false;
        loadComments(b.getAttribute('data-id'), cbox);
      });
    });
  }

  function commentRow(d) {
    return '<div class="cmt"><b>' + esc(fv(d, 'author') || 'Student') + '</b> ' +
      '<span>' + esc(fv(d, 'text')) + '</span><time>' + esc(fmtDate(fv(d, 'date'))) + '</time></div>';
  }
  function loadComments(postId, cbox) {
    cbox.innerHTML = '<p class="c-loading">loading…</p>';
    runQuery('advice_comments', null, 50, {
      fieldFilter: { field: { fieldPath: 'postId' }, op: 'EQUAL', value: { stringValue: postId } }
    }).then(function (docs) {
      docs = docs.filter(function (d) { return fv(d, 'hidden') !== true; });
      docs.sort(function (a, b) { return (fv(a, 'date') || '').localeCompare(fv(b, 'date') || ''); }); // oldest first
      var u = userName();
      var composer = u
        ? '<div class="c-compose"><input maxlength="500" placeholder="Write a comment…"><button>send</button></div>'
        : '<p class="c-signin"><a href="https://flarestamina.com/account/?return=' + encodeURIComponent('https://flarestamina.com/news/#ideas') + '">Sign in with FS Account</a> to comment</p>';
      cbox.innerHTML = (docs.map(commentRow).join('') || '<p class="c-loading">no comments yet</p>') + composer;
      if (u) {
        var inp = $('input', cbox), snd = $('button', cbox);
        function send() {
          var t = inp.value.trim();
          if (t.length < 2) return;
          snd.disabled = true;
          createDoc('advice_comments', {
            postId: { stringValue: postId },
            text: { stringValue: t },
            author: { stringValue: u },
            date: { stringValue: new Date().toISOString() }
          }).then(function () { loadComments(postId, cbox); track('advice-comment'); })
            .catch(function () { snd.disabled = false; });
        }
        snd.addEventListener('click', send);
        inp.addEventListener('keydown', function (e) { if (e.key === 'Enter') send(); });
      }
    }).catch(function () {
      cbox.innerHTML = '<p class="c-signin">Could not load comments — please refresh the page.</p>';
    });
  }

  /* composer */
  function initComposer() {
    var u = userName();
    var boxIn = $('#composer-in'), boxOut = $('#composer-signin');
    if (!boxIn) return;
    if (u) {
      boxIn.hidden = false; boxOut.hidden = true;
      $('#composer-who').textContent = u;
      var ta = $('#composer-text'), btn = $('#composer-send');
      btn.addEventListener('click', function () {
        var t = ta.value.trim();
        if (t.length < 10) { ta.focus(); return; }
        btn.disabled = true; btn.textContent = 'posting…';
        createDoc('advice', {
          text: { stringValue: t.slice(0, 2000) },
          author: { stringValue: u },
          date: { stringValue: new Date().toISOString() },
          likes: { integerValue: '0' }
        }).then(function () {
          ta.value = '';
          btn.disabled = false; btn.textContent = 'post';
          loadAdvice(true); track('advice-post');
        }).catch(function () {
          btn.disabled = false; btn.textContent = 'post';
          alert('Could not post — check your connection and try again.');
        });
      });
    } else {
      boxIn.hidden = true; boxOut.hidden = false;
    }
  }

  /* ---------- boot ---------- */
  initComposer();
  var h = (location.hash || '').replace('#', '');
  if (h === 'articles' || h === 'ideas') setMode(h, false);
  window.addEventListener('hashchange', function () {
    var m = (location.hash || '').replace('#', '');
    if (MODES.indexOf(m) >= 0) setMode(m, false);
  });
})();
