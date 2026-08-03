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
