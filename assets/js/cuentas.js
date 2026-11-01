/* Mi tienda / Mi empresa: pestañas Ingresar / Crear y confirmación (prototipo, no crea cuentas) */
(function () {
  'use strict';
  var card = document.getElementById('acceso'); if (!card) return;
  var tienda = document.body.dataset.cuenta === 'tienda';
  var tabs = card.querySelectorAll('[data-tab]'), forms = card.querySelectorAll('form'), ok = card.querySelector('.ac-ok');
  function mostrar(t) {
    tabs.forEach(function (b) { b.setAttribute('aria-selected', String(b.dataset.tab === t)); });
    forms.forEach(function (f) { f.hidden = f.dataset.panel !== t; });
    ok.hidden = true; card.querySelector('.ac-tabs').hidden = false;
  }
  tabs.forEach(function (b) { b.addEventListener('click', function () { mostrar(b.dataset.tab); }); });
  var q = new URLSearchParams(location.search);
  if (q.get('publicar')) {
    var av = card.querySelector('[data-publicar="' + q.get('publicar') + '"]'); if (av) av.hidden = false;
  }
  if (q.get('crear') !== null) mostrar('up');
  forms.forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.checkValidity()) { f.reportValidity(); return; }
      var crear = f.dataset.panel === 'up';
      forms.forEach(function (x) { x.hidden = true; });
      card.querySelector('.ac-tabs').hidden = true;
      ok.hidden = false;
      ok.querySelector('[data-ok-t]').textContent = crear ? (tienda ? '¡Tu tienda está creada!' : '¡Tu empresa está registrada!') : 'Ingresaste';
      ok.querySelector('[data-ok-p]').textContent = crear
        ? 'Te enviamos un correo para confirmar tu dirección. El próximo paso es validar tu identidad.'
        : 'En la versión final, acá vas a ver tu panel con tus publicaciones, consultas y ventas.';
      ok.querySelector('.ac-next').hidden = !crear;
    });
  });
  card.querySelector('[data-volver]').addEventListener('click', function () { mostrar('in'); });
  card.querySelector('[data-olvide]').addEventListener('click', function (e) {
    e.preventDefault();
    this.textContent = 'Te enviaremos un enlace a tu correo para crear una nueva contraseña.';
  });
})();
