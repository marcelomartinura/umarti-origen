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

/* Carrito (se guarda en este navegador) y su contador en el encabezado */
(function () {
  var KEY = 'umarti-carrito';
  function leer() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function guardar(l) { try { localStorage.setItem(KEY, JSON.stringify(l)); } catch (e) { /* sin almacenamiento */ } document.dispatchEvent(new Event('umarti:carrito')); }
  function contar() { return leer().reduce(function (n, x) { return n + (+x.cant || 0); }, 0); }
  window.UmartiCarrito = {
    leer: leer, guardar: guardar, contar: contar,
    agregar: function (item, cant) {
      var l = leer(), x = l.filter(function (i) { return i.codigo === item.codigo; })[0];
      if (x) { x.cant = Math.min(99, (+x.cant || 0) + cant); Object.assign(x, item, { cant: x.cant }); }
      else { item.cant = cant; l.push(item); }
      guardar(l);
    }
  };
  var badge = document.getElementById('cart-count');
  if (!badge) return;
  function update() { var n = contar(); badge.textContent = n > 99 ? '99+' : n; badge.hidden = n === 0; }
  document.addEventListener('umarti:carrito', update);
  window.addEventListener('storage', update);
  update();
})();

/* Selector de país de la Tienda: se cierra al tocar afuera o con Escape */
(function () {
  var sels = document.querySelectorAll('.pais-sel');
  if (!sels.length) return;
  document.addEventListener('click', function (e) {
    sels.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') sels.forEach(function (d) { d.open = false; });
  });
})();

/* Mi cuenta: si la persona ya ingresó en este navegador, el encabezado la saluda */
(function () {
  var txt = document.querySelector('[data-cuenta-txt]');
  if (!txt) return;
  function pintar() {
    var c = null;
    try { c = JSON.parse(localStorage.getItem('umarti-cuenta') || 'null'); } catch (e) { c = null; }
    var n = c && c.nombre ? String(c.nombre).split(' ')[0].slice(0, 14) : '';
    txt.textContent = n ? 'Hola, ' + n : 'Mi cuenta';
  }
  document.addEventListener('umarti:cuenta', pintar);
  window.addEventListener('storage', pintar);
  pintar();
})();

/* Sesión: favoritos y carrito son para personas que ingresaron con su cuenta.
   Si no hay sesión, se lleva a Mi cuenta y, al ingresar, se vuelve a la página donde estaba. */
(function () {
  var CLAVE = 'sb-tkrnwboyynvbellqnzle-auth-token';
  function activa() {
    try { var s = JSON.parse(localStorage.getItem(CLAVE) || 'null'); return !!(s && (s.refresh_token || s.access_token)); } catch (e) { return false; }
  }
  var pre = document.body.dataset.prefix || (document.querySelector('link[href*="assets/css/umarti.css"]') || { getAttribute: function () { return 'assets/'; } }).getAttribute('href').split('assets/')[0];
  function aCuenta(motivo, volver) {
    location.href = pre + 'mi-cuenta/?motivo=' + motivo + '&volver=' + encodeURIComponent(volver || (location.pathname + location.search + location.hash));
  }
  window.UmartiSesion = { activa: activa, pedir: aCuenta };
  // páginas de favoritos y carrito: sin sesión, primero ingresar
  var ruta = location.pathname;
  if (!activa() && /\/(favoritos|carrito)\/(index\.html)?$/.test(ruta)) { aCuenta(/favoritos/.test(ruta) ? 'favoritos' : 'carrito'); return; }
  window.addEventListener('click', function (e) {
    if (activa()) return;
    var fav = e.target.closest('[data-fav]'), cart = e.target.closest('#cart-add');
    var link = e.target.closest('a[href]');
    var destino = link && /(^|\/)(favoritos|carrito)\/?$/.test(link.getAttribute('href')) ? (/favoritos/.test(link.getAttribute('href')) ? 'favoritos' : 'carrito') : '';
    if (!fav && !cart && !destino) return;
    e.preventDefault(); e.stopImmediatePropagation();
    if (destino) aCuenta(destino, link.pathname); else aCuenta(fav ? 'favoritos' : 'carrito');
  }, true);
})();
