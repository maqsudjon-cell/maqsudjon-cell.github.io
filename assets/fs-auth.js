/*!
 * FS Account — shared auth client for the FLARESTAMINA ecosystem.
 *
 * Usage on any tool page:
 *   <script src="https://flarestamina.com/assets/fs-auth.js"></script>
 *   <script>FSAuth.require();</script>
 *
 * API:
 *   FSAuth.getUser()   -> {first_name, last_name, phone} or null
 *   FSAuth.getToken()  -> JWT string or null
 *   FSAuth.require()   -> redirects to /account/?return=<url> if not signed in
 *   FSAuth.logout()    -> clears the session, goes to /account/
 *   FSAuth.save(token, user) -> stores a session (used by the account page)
 *
 * Session storage: localStorage key "fs_session" = {"token": "...", "user": {...}}
 * All tools live under flarestamina.com paths, so the session is shared.
 * The client only checks token expiry for UX; the server verifies the JWT
 * on every API call.
 */
(function () {
  'use strict';

  // ENFORCE=true: FS Account is mandatory. Signed-out students are redirected
  // to /account/ once; after that the session lives in localStorage and every
  // tool on flarestamina.com recognizes them. Set to false only for
  // emergencies (tools then fall back to the old name behavior).
  var ENFORCE = true;

  var KEY = 'fs_session';
  var ACCOUNT_URL = 'https://flarestamina.com/account/';

  function read() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return null;
      var s = JSON.parse(raw);
      if (!s || !s.token || !s.user) return null;
      return s;
    } catch (e) { return null; }
  }

  // Sessions are long-lived: the user object is what identifies the student.
  // The Firebase idToken inside expires after ~1h — that only matters for
  // server-verified calls, so an expired token does NOT log the student out.
  function session() {
    return read();
  }

  window.FSAuth = {
    API_BASE: 'https://pangeya-ai.vercel.app',

    getUser: function () {
      var s = session();
      return s ? s.user : null;
    },

    getToken: function () {
      var s = session();
      return s ? s.token : null;
    },

    // Returns a Promise of a non-expired Firebase idToken, refreshing it with
    // the stored refreshToken when needed. Resolves null if signed out or the
    // refresh fails (callers should degrade gracefully).
    getFreshToken: function () {
      var s = session();
      if (!s || !s.token) return Promise.resolve(null);
      var expired = true;
      try {
        var payload = JSON.parse(atob(s.token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
        expired = !payload.exp || (payload.exp * 1000) <= Date.now() + 60000;
      } catch (e) {}
      if (!expired) return Promise.resolve(s.token);
      if (!s.refreshToken) return Promise.resolve(null);
      var API_KEY = 'AIzaSyAqS59ek0seZ0rcSZb3RPhiwTzleIAZ-9E'; // public web app key
      return fetch('https://securetoken.googleapis.com/v1/token?key=' + API_KEY, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'grant_type=refresh_token&refresh_token=' + encodeURIComponent(s.refreshToken)
      }).then(function (r) { return r.json(); }).then(function (d) {
        if (!d.id_token) return null;
        window.FSAuth.save(d.id_token, s.user, d.refresh_token || s.refreshToken);
        return d.id_token;
      }).catch(function () { return null; });
    },

    // Search-engine crawlers must reach the real page content, not the
    // noindex /account/ gate — otherwise every tool page becomes unindexable.
    // The catalog is public content; the login is a product convenience, so
    // letting bots through is not cloaking.
    isBot: function () {
      try {
        return /bot|crawl|spider|slurp|bingpreview|google|yandex|duckduck|baidu|facebookexternalhit|embedly|quora|pinterest|vkshare|whatsapp|telegrambot|lighthouse|headlesschrome/i
          .test(navigator.userAgent || '');
      } catch (e) { return false; }
    },

    require: function () {
      if (session()) return true;
      if (!ENFORCE || this.isBot()) {
        try { console.info('[FSAuth] no session — enforcement skipped (transition or crawler)'); } catch (e) {}
        return true;
      }
      var ret = encodeURIComponent(location.href);
      location.replace(ACCOUNT_URL + '?return=' + ret);
      return false;
    },

    save: function (token, user, refreshToken) {
      try {
        localStorage.setItem(KEY, JSON.stringify({ token: token, user: user, refreshToken: refreshToken || null }));
      } catch (e) {}
    },

    logout: function () {
      try { localStorage.removeItem(KEY); } catch (e) {}
      location.href = ACCOUNT_URL;
    }
  };
})();
