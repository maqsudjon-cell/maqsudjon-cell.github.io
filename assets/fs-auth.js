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

  // ENFORCE=false: transition mode while the auth backend is being configured
  // (Vercel env vars + Supabase table). require() will NOT redirect, so tools
  // keep working for signed-out students. Flip to true once registration works.
  var ENFORCE = false;

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

  function tokenExpired(token) {
    try {
      var payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
      if (!payload.exp) return false;
      return (payload.exp * 1000) <= Date.now();
    } catch (e) { return true; }
  }

  function session() {
    var s = read();
    if (!s) return null;
    if (tokenExpired(s.token)) {
      try { localStorage.removeItem(KEY); } catch (e) {}
      return null;
    }
    return s;
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

    require: function () {
      if (session()) return true;
      if (!ENFORCE) {
        try { console.info('[FSAuth] no session — enforcement is off during transition'); } catch (e) {}
        return true;
      }
      var ret = encodeURIComponent(location.href);
      location.replace(ACCOUNT_URL + '?return=' + ret);
      return false;
    },

    save: function (token, user) {
      try { localStorage.setItem(KEY, JSON.stringify({ token: token, user: user })); } catch (e) {}
    },

    logout: function () {
      try { localStorage.removeItem(KEY); } catch (e) {}
      location.href = ACCOUNT_URL;
    }
  };
})();
