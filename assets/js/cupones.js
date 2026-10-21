/* Cuponera: carrusel de destacados, filtros, ver y copiar código, publicar cupón (prototipo) */
(function () {
  var DATA = {};
  (window.CUPONES || []).forEach(function (c) { DATA[c.codigo] = c; });
  var pre = document.body.dataset.prefix || '';

  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  var toastEl = document.getElementById('toast'), tt;
  function toast(m) { if (!toastEl) return; toastEl.textContent = m; toastEl.classList.add('show'); clearTimeout(tt); tt = setTimeout(function () { toastEl.classList.remove('show'); }, 2400); }

  /* ---------- carrusel de destacados ---------- */
  var track = document.querySelector('.cu-track');
  if (track) {
    var slides = track.querySelectorAll('.cu-slide');
    var dots = document.querySelectorAll('.cu-dots span');
    var idx = function () {
      var c = track.scrollLeft + track.clientWidth / 2, best = 0, d = Infinity;
      slides.forEach(function (s, i) { var m = s.offsetLeft + s.clientWidth / 2, k = Math.abs(m - c); if (k < d) { d = k; best = i; } });
      return best;
    };
    var go = function (i) { i = (i + slides.length) % slides.length; var s = slides[i]; track.scrollTo({ left: s.offsetLeft - (track.clientWidth - s.clientWidth) / 2 }); };
    var upd = function () { var i = idx(); dots.forEach(function (d, k) { d.classList.toggle('on', k === i); }); };
    document.querySelectorAll('[data-slide]').forEach(function (b) { b.addEventListener('click', function () { go(idx() + parseInt(b.dataset.slide, 10)); }); });
    var r; track.addEventListener('scroll', function () { cancelAnimationFrame(r); r = requestAnimationFrame(upd); });
    var auto = setInterval(function () { go(idx() + 1); }, 6000);
    track.addEventListener('pointerdown', function () { clearInterval(auto); });
    document.querySelectorAll('[data-slide]').forEach(function (b) { b.addEventListener('click', function () { clearInterval(auto); }); });
    setTimeout(function () { go(0); upd(); }, 50);
  }

  /* ---------- filtros ---------- */
  var grid = document.getElementById('cu-grid');
  if (grid) {
    var q = document.getElementById('cu-q'), pais = document.getElementById('cu-pais');
    var chips = document.querySelectorAll('[data-cat-filter]');
    var cat = '';
    var apply = function () {
      var t = q ? norm(q.value).trim() : '', n = 0;
      grid.querySelectorAll('.cupon').forEach(function (c) {
        var ok = (!t || norm(c.dataset.texto).indexOf(t) > -1) && (!cat || c.dataset.cat === cat) && (!pais || !pais.value || c.dataset.pais === pais.value);
        c.classList.toggle('is-hidden', !ok); if (ok) n++;
      });
      chips.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.catFilter === cat)); });
      var e = document.getElementById('cu-empty'); if (e) e.classList.toggle('show', n === 0);
      var cnt = document.getElementById('cu-count'); if (cnt) cnt.textContent = n === 1 ? '1 cupón' : n + ' cupones';
    };
    chips.forEach(function (b) { b.addEventListener('click', function () { cat = b.dataset.catFilter; apply(); }); });
    if (q) q.addEventListener('input', apply);
    if (pais) pais.addEventListener('change', apply);
    var hq = document.getElementById('cu-q-top');
    if (hq) hq.addEventListener('input', function () { q.value = hq.value; apply(); });
    apply();
  }

  /* ---------- ventana del cupón ---------- */
  var dlg = document.getElementById('dlg-cupon');
  function abrir(cod) {
    var c = DATA[cod]; if (!c || !dlg) return;
    var box = dlg.querySelector('.cu-dlg-body'); box.textContent = '';
    var art = document.getElementById('art-' + cod);
    if (art) { var a = art.cloneNode(true); a.removeAttribute('id'); box.appendChild(a); }
    var x = el('button', 'x', '×'); x.type = 'button'; x.setAttribute('aria-label', 'Cerrar'); x.dataset.close = ''; box.appendChild(x);
    var inn = el('div', 'in');
    var who = el('div', 'who'); who.appendChild(el('span', 'cu-logo', c.iniciales));
    var wt = el('div'); wt.appendChild(el('strong', null, c.comercio)); wt.appendChild(el('div', 'cu-merchant', c.lugar)); who.appendChild(wt);
    inn.appendChild(who);
    inn.appendChild(el('h2', null, c.titulo));
    inn.appendChild(el('p', 'desc', c.descripcion));
    if (c.tipo === 'Código' && c.cupon) {
      var cb = el('div', 'code-box'); cb.appendChild(el('code', null, c.cupon));
      var cp = el('button', null, 'Copiar código'); cp.type = 'button';
      cp.addEventListener('click', function () {
        var done = function () { cp.textContent = '¡Copiado!'; toast('Código copiado: ' + c.cupon); };
        if (navigator.clipboard) navigator.clipboard.writeText(c.cupon).then(done, done); else done();
      });
      cb.appendChild(cp); inn.appendChild(cb);
    } else {
      inn.appendChild(el('div', 'no-code', c.online ? 'No necesitás código: el descuento se aplica al entrar desde este cupón.' : 'No necesitás código: mostrá este cupón en el local.'));
    }
    var conds = el('div', 'conds');
    [['Condiciones', c.condiciones], ['Vence', c.vence_txt], ['Dónde', c.lugar]].forEach(function (r) {
      if (!r[1]) return; var p = el('p'); p.appendChild(el('b', null, r[0] + ': ')); p.appendChild(document.createTextNode(r[1])); conds.appendChild(p);
    });
    if (c.ejemplo) conds.appendChild(el('p', null, 'Cupón de ejemplo: el comercio es ficticio y el código no es válido.'));
    inn.appendChild(conds);
    var acts = el('div', 'acts');
    if (c.link) { var l = el('a', 'pri', 'Ir al sitio'); l.href = /^https?:/.test(c.link) ? c.link : pre + c.link; if (/^https?:/.test(c.link)) { l.target = '_blank'; l.rel = 'noopener'; } acts.appendChild(l); }
    if (c.destino_url) { var dl = el('a', 'sec', 'Guía de viaje de ' + c.destino_nombre); dl.href = pre + c.destino_url; acts.appendChild(dl); }
    if (c.tema) { var tl = el('a', 'sec', 'Todo sobre el ' + c.tema); tl.href = pre + (c.tema_url || c.tema + '/'); acts.appendChild(tl); }
    if (acts.children.length) inn.appendChild(acts);
    box.appendChild(inn);
    dlg.showModal();
    try { history.replaceState(null, '', '#' + cod.toLowerCase()); } catch (e) { /* vista previa */ }
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-cupon]');
    if (b) { e.preventDefault(); abrir(b.dataset.cupon); }
  });
  document.querySelectorAll('dialog').forEach(function (d) {
    d.addEventListener('click', function (e) { if (e.target === d || e.target.closest('[data-close]')) d.close(); });
    d.addEventListener('close', function () { try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { /* vista previa */ } });
  });
  if (location.hash.length > 1) {
    var h = location.hash.slice(1).toUpperCase();
    if (DATA[h]) setTimeout(function () { abrir(h); }, 200);
  }

  /* ---------- publicá tu cupón ---------- */
  var pub = document.getElementById('dlg-pub');
  function abrirPub() {
    if (!pub) return;
    var f = pub.querySelector('form'); f.reset(); f.hidden = false; pub.querySelector('.ok').hidden = true; pub.showModal();
  }
  document.querySelectorAll('[data-publicar]').forEach(function (b) { b.addEventListener('click', abrirPub); });
  if (pub) pub.querySelector('form').addEventListener('submit', function (e) { e.preventDefault(); this.hidden = true; pub.querySelector('.ok').hidden = false; });
  if (location.hash === '#publicar') setTimeout(abrirPub, 200);
})();
