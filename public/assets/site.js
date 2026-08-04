/* Bilingual PT/EN toggle.
   The choice is stored in localStorage so it survives navigation between pages.
   This file is loaded in <head> without defer so data-lang is set before first
   paint, which avoids a flash of the wrong language. */
(function () {
  var KEY = 'caroco-lang';

  function stored() {
    try {
      var s = localStorage.getItem(KEY);
      if (s === 'pt' || s === 'en') return s;
    } catch (e) {}
    return null;
  }

  function preferred() {
    return stored() ||
      ((navigator.language || '').toLowerCase().indexOf('en') === 0 ? 'en' : 'pt');
  }

  function apply(lang, persist) {
    var root = document.documentElement;
    root.setAttribute('data-lang', lang);
    root.setAttribute('lang', lang);
    if (persist) {
      try { localStorage.setItem(KEY, lang); } catch (e) {}
    }
    var pt = document.getElementById('btn-pt');
    var en = document.getElementById('btn-en');
    if (pt) pt.setAttribute('aria-pressed', String(lang === 'pt'));
    if (en) en.setAttribute('aria-pressed', String(lang === 'en'));
  }

  /* Runs before the body exists, so it only touches <html>. */
  apply(preferred(), false);

  /* Called by the PT/EN buttons. */
  window.setLang = function (lang) { apply(lang, true); };

  /* Re-run once the buttons exist so their pressed state matches. */
  document.addEventListener('DOMContentLoaded', function () {
    apply(preferred(), false);
  });
})();

/* Cloudflare Web Analytics.
   Cookieless, no fingerprinting, no personal data, so the site needs no consent
   banner and the legal footer stays as is.

   It lives here rather than as a <script> tag pasted into all eight pages, so
   there is one place to change it. The token is not a secret: it ships in the
   HTML of every public page by design.

   Previously this was Cloudflare's "automatic" edge injection, set to exclude EU
   visitors, which meant that for a Portuguese association it recorded almost
   nothing and failed silently. Installing the beacon here keeps it in version
   control where a change is visible in a diff. */
(function () {
  var s = document.createElement('script');
  s.type = 'module';
  s.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  s.setAttribute('data-cf-beacon', '{"token": "b9f379bfe2c04b469ce2a2a8ae755188"}');
  document.head.appendChild(s);
})();
