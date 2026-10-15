/* Tienda: carrusel de fotos, favoritos, filtros y consultas (prototipo, sin envío de datos) */
(function () {
  var FAV_KEY = 'umarti-favoritos';

  function getFavs() {
    try { return JSON.parse(localStorage.getItem(FAV_KEY) || '[]'); } catch (e) { return []; }
  }
  function setFavs(list) {
    try { localStorage.setItem(FAV_KEY, JSON.stringify(list)); } catch (e) { /* sin almacenamiento */ }
    document.dispatchEvent(new CustomEvent('umarti:favoritos'));
  }

  var toastEl = document.getElementById('toast'), toastT;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg; toastEl.classList.add('show');
    clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('show'); }, 2600);
  }

  /* ---------- favoritos ---------- */
  function syncFavButtons() {
    var favs = getFavs();
    document.querySelectorAll('[data-fav]').forEach(function (b) {
      var on = favs.indexOf(b.dataset.fav) > -1;
      b.setAttribute('aria-pressed', String(on));
      b.setAttribute('aria-label', on ? 'Quitar de favoritos' : 'Guardar en favoritos');
    });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-fav]');
    if (!b) return;
    e.preventDefault(); e.stopPropagation();
    var favs = getFavs(), id = b.dataset.fav, i = favs.indexOf(id);
    if (i > -1) { favs.splice(i, 1); toast('Lo quitaste de favoritos'); }
    else { favs.push(id); toast('Guardado en favoritos'); }
    setFavs(favs);
    syncFavButtons();
    renderFavPage();
  });

  /* ---------- carrusel ---------- */
  function initCarousel(c) {
    if (c.dataset.ready) return;
    c.dataset.ready = '1';
    var track = c.querySelector('.car-track');
    var slides = track.querySelectorAll('.car-slide');
    var dots = c.querySelectorAll('.car-dot');
    var count = c.querySelector('.car-count');
    var prev = c.querySelector('.car-btn.prev'), next = c.querySelector('.car-btn.next');
    var host = c.closest('.pdp-photo');
    var thumbs = host ? host.querySelectorAll('.car-thumb') : [];
    function idx() { return Math.round(track.scrollLeft / Math.max(1, track.clientWidth)); }
    function update() {
      var i = idx();
      dots.forEach(function (d, k) { d.classList.toggle('on', k === i); });
      thumbs.forEach(function (t, k) { t.classList.toggle('on', k === i); });
      if (count) count.textContent = (i + 1) + '/' + slides.length;
      if (prev) prev.disabled = i === 0;
      if (next) next.disabled = i >= slides.length - 1;
    }
    function go(i) { track.scrollTo({ left: i * track.clientWidth }); }
    if (prev) prev.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); go(idx() - 1); });
    if (next) next.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); go(idx() + 1); });
    thumbs.forEach(function (t, k) { t.addEventListener('click', function () { go(k); }); });
    var raf;
    track.addEventListener('scroll', function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(update); });
    c.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') go(idx() + 1);
      if (e.key === 'ArrowLeft') go(idx() - 1);
    });
    update();
  }
  function initCarousels() { document.querySelectorAll('[data-carousel]').forEach(initCarousel); }

  /* ---------- filtro del listado ---------- */
  var grid = document.getElementById('shop-grid');
  var chips = document.querySelectorAll('[data-filtro]');
  var p = new URLSearchParams(location.search);
  var filtro = p.get('sub') || p.get('cat') || '';
  function applyFilter() {
    if (!grid) return;
    var n = 0;
    grid.querySelectorAll('.prod-card').forEach(function (c) {
      var ok = !filtro || c.dataset.cat === filtro || c.dataset.sub === filtro;
      c.classList.toggle('is-hidden', !ok);
      if (ok) n++;
    });
    chips.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.filtro === filtro)); });
    var cnt = document.getElementById('shop-count');
    if (cnt) cnt.textContent = n === 1 ? '1 producto' : n + ' productos';
    var empty = document.getElementById('shop-empty');
    if (empty) empty.classList.toggle('show', n === 0);
  }
  chips.forEach(function (b) { b.addEventListener('click', function () { filtro = b.dataset.filtro; applyFilter(); }); });

  /* ---------- consultas: precio por cantidad y conversar con el vendedor ---------- */
  var box = document.querySelector('[data-producto]');
  var producto = box ? box.dataset.producto : '';
  document.querySelectorAll('[data-dialog]').forEach(function (b) {
    b.addEventListener('click', function () {
      var d = document.getElementById(b.dataset.dialog);
      if (!d) return;
      var sub = d.querySelector('.dlg-head p');
      if (sub) sub.textContent = producto;
      var form = d.querySelector('form');
      form.reset(); form.hidden = false;
      document.getElementById(form.dataset.ok).hidden = true;
      d.showModal();
      var first = form.querySelector('input, textarea');
      if (first) first.focus();
    });
  });
  document.querySelectorAll('dialog').forEach(function (d) {
    d.addEventListener('click', function (e) { if (e.target === d || e.target.closest('[data-close]')) d.close(); });
    var form = d.querySelector('form');
    if (form) form.addEventListener('submit', function (e) {
      e.preventDefault();
      form.hidden = true;
      document.getElementById(form.dataset.ok).hidden = false;
    });
  });
  document.querySelectorAll('.btn-buy[aria-disabled="true"]').forEach(function (b) {
    b.addEventListener('click', function (e) { e.preventDefault(); });
  });

  /* ---------- página de favoritos ---------- */
  function renderFavPage() {
    var fg = document.getElementById('fav-grid');
    if (!fg || !window.TIENDA_INDICE) return;
    var pre = fg.dataset.prefix || '';
    var favs = getFavs();
    var items = window.TIENDA_INDICE.filter(function (x) { return favs.indexOf(x.codigo) > -1; });
    fg.textContent = '';
    items.forEach(function (x) {
      var a = document.createElement('article'); a.className = 'prod-card';
      var media = document.createElement('div'); media.className = 'prod-media';
      var link = document.createElement('a'); link.href = pre + x.url; link.style.display = 'block'; link.style.height = '100%';
      if (x.foto) {
        var img = document.createElement('img'); img.src = x.foto; img.alt = x.nombre;
        img.style.cssText = 'width:100%;height:100%;object-fit:cover'; link.appendChild(img);
      } else {
        var cv = document.createElement('div'); cv.className = 'cover'; cv.dataset.glyph = x.glifo;
        cv.style.cssText = '--c1:' + x.c1 + ';--c2:' + x.c2 + ';height:100%;border-radius:0;min-height:0';
        var sp = document.createElement('span'); sp.textContent = x.subcategoria; cv.appendChild(sp); link.appendChild(cv);
      }
      media.appendChild(link);
      var fb = document.createElement('button'); fb.className = 'fav'; fb.type = 'button'; fb.dataset.fav = x.codigo;
      fb.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>';
      media.appendChild(fb);
      a.appendChild(media);
      var info = document.createElement('a'); info.className = 'info'; info.href = pre + x.url;
      var k = document.createElement('span'); k.className = 'kick'; k.textContent = x.subcategoria; info.appendChild(k);
      var h = document.createElement('h3'); h.textContent = x.nombre; info.appendChild(h);
      var pr = document.createElement('span'); pr.className = 'price'; pr.textContent = x.precio + ' ';
      var sm = document.createElement('small'); sm.textContent = x.moneda; pr.appendChild(sm); info.appendChild(pr);
      var ev = document.createElement('span'); ev.className = 'envio'; ev.textContent = 'Envío disponible: ' + x.envio; info.appendChild(ev);
      a.appendChild(info);
      fg.appendChild(a);
    });
    var empty = document.getElementById('fav-empty');
    if (empty) empty.classList.toggle('show', items.length === 0);
    syncFavButtons();
  }

  initCarousels();
  applyFilter();
  renderFavPage();
  syncFavButtons();
})();
