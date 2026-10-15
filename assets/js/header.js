/* Umarti Origen: menú y desplegables del encabezado */
(function () {
  var header = document.getElementById('site-header');
  var toggle = document.getElementById('menu-toggle');
  var menus = header.querySelectorAll('.has-menu');

  function closeAll(except) {
    menus.forEach(function (m) {
      if (m !== except) {
        m.classList.remove('open');
        var b = m.querySelector(':scope > .nav-btn');
        if (b) b.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Abrir y cerrar desplegables
  menus.forEach(function (m) {
    var btn = m.querySelector(':scope > .nav-btn');
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var willOpen = !m.classList.contains('open');
      closeAll(m);
      m.classList.toggle('open', willOpen);
      btn.setAttribute('aria-expanded', String(willOpen));
    });
  });

  // Menú del celular
  toggle.addEventListener('click', function () {
    var open = header.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    if (!open) closeAll();
  });

  // Cerrar al hacer clic afuera, al elegir un enlace o con Escape
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-menu')) closeAll();
  });
  header.querySelectorAll('.modules a').forEach(function (a) {
    a.addEventListener('click', function () {
      closeAll();
      header.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAll();
  });
})();

/* Contador de favoritos en el encabezado (se guardan en este navegador) */
(function () {
  var badge = document.getElementById('fav-count');
  if (!badge) return;
  function update() {
    var n = 0;
    try { n = JSON.parse(localStorage.getItem('umarti-favoritos') || '[]').length; } catch (e) { n = 0; }
    badge.textContent = n;
    badge.hidden = n === 0;
  }
  document.addEventListener('umarti:favoritos', update);
  window.addEventListener('storage', update);
  update();
})();
