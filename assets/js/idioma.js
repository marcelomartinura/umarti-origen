/* Ver en inglés: traducción automática con Google Translate (International Shop, Viajes, Recursos digitales).
   La elección se guarda en la cookie googtrans y se mantiene mientras se navega por esas secciones. */
(function () {
  'use strict';
  var activo = /(?:^|;\s*)googtrans=\/es\/en/.test(document.cookie);
  var ofrece = document.body.hasAttribute('data-en');
  if (!ofrece && !activo) return;

  function cookie(valor) {
    var h = location.hostname, partes = h.split('.'), vence = valor ? '' : '; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    var doms = [''];
    for (var i = 0; i < partes.length - 1; i++) doms.push('; domain=.' + partes.slice(i).join('.'));
    doms.forEach(function (d) { document.cookie = 'googtrans=' + (valor || '') + '; path=/' + d + vence; });
  }

  // Marcas que no se traducen
  Array.prototype.forEach.call(document.querySelectorAll('.logo, .ts-brand, .footer-brand'), function (e) { e.classList.add('notranslate'); });

  var acc = document.querySelector('.user-actions');
  if (acc) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'icon-link lang-btn notranslate';
    b.setAttribute('translate', 'no');
    b.setAttribute('aria-label', activo ? 'Ver en español' : 'View in English');
    b.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/></svg><span>' + (activo ? 'Español' : 'English') + '</span>';
    b.addEventListener('click', function () { cookie(activo ? null : '/es/en'); location.reload(); });
    acc.insertBefore(b, acc.firstChild);
  }

  if (!activo) return;
  document.documentElement.classList.add('ver-en');
  var el = document.createElement('div'); el.id = 'gt-el'; el.hidden = true; document.body.appendChild(el);
  window.umartiGT = function () {
    new google.translate.TranslateElement({ pageLanguage: 'es', includedLanguages: 'en', autoDisplay: false }, 'gt-el');
  };
  var s = document.createElement('script');
  s.src = 'https://translate.google.com/translate_a/element.js?cb=umartiGT';
  document.body.appendChild(s);
})();
