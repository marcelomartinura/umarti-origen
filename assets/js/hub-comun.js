/* Hub de Oportunidades: funciones compartidas (coincidencias, filtros, ventanas, negociación) */
(function () {
  var DAY = 86400000;
  var today = new Date(); today.setHours(0, 0, 0, 0);
  var D = window.HUB_DATOS || { productos: [], servicios: [], busquedas: [] };

  /* ---------- utilidades ---------- */
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function plural(n, uno, varios) { return n + ' ' + (n === 1 ? uno : varios); }
  function hsFmt(hs) { return hs ? hs.slice(0, 4) + '.' + hs.slice(4) : ''; }
  function iso(d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function fecha(isoStr) { return isoStr.split('-').reverse().join('/'); }
  function parse(isoStr) { return new Date(isoStr + 'T00:00:00'); }
  function daysLeft(isoStr) { return Math.round((parse(isoStr) - today) / DAY); }
  function addBusinessDays(isoStr, n) {
    var d = parse(isoStr);
    while (n > 0) { d.setDate(d.getDate() + 1); if (d.getDay() !== 0 && d.getDay() !== 6) n--; }
    return d;
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  /* ---------- coincidencias ---------- */
  var STOP = ('para desde como tipo producto productos servicio servicios busco buscamos necesito necesitamos otros otras ' +
    'fresco fresca frescos frescas natural mexico argentina chile brasil espana china alemania uruguay estados unidos ' +
    'importar exportar compra venta calidad entrega').split(' ');
  function stems(text) {
    var out = {};
    norm(text).split(/[^a-z0-9]+/).forEach(function (t) {
      if (t.length < 4 || STOP.indexOf(t) > -1 || /^\d+$/.test(t)) return;
      out[t.slice(0, 5)] = 1;
    });
    return out;
  }
  function overlap(a, b) { for (var k in a) if (b[k]) return true; return false; }

  /* Para una búsqueda, devuelve los productos o servicios publicados que coinciden */
  function matchBusqueda(b) {
    var pool = b.tipo === 'servicio' ? D.servicios : D.productos;
    var bs = stems(b.nombre);
    var hs4 = (b.hs || '').slice(0, 4);
    return pool.filter(function (o) {
      if (hs4.length === 4 && o.hs && o.hs.slice(0, 4) === hs4) return true;
      return overlap(bs, stems(o.nombre + ' ' + (o.claves || '')));
    });
  }
  /* Para un producto o servicio, devuelve las búsquedas de la mesa que lo piden */
  function matchOferta(cod) {
    return D.busquedas.filter(function (b) {
      return daysLeft(b.vence) >= 0 && matchBusqueda(b).some(function (o) { return o.cod === cod; });
    });
  }

  /* ---------- vigencia ---------- */
  function updateVigencia(card) {
    if (!card.dataset.vence) return;
    var d = daysLeft(card.dataset.vence);
    var v = card.querySelector('.op-vence');
    if (d < 0) { card.classList.add('is-expired'); return; }
    if (v && d <= 30) { v.classList.add('pronto'); v.textContent = d === 0 ? 'Vence hoy' : 'Vence en ' + plural(d, 'día', 'días'); }
  }

  /* ---------- filtros guiados por atributos data-filter ---------- */
  function setupFilters(opts) {
    var list = opts.list;
    var q = document.querySelector('[data-filter="texto"]');
    var selects = Array.prototype.slice.call(document.querySelectorAll('select[data-filter]'));
    var vig = document.querySelector('[data-filter-vig]');
    var chipGroup = document.querySelector('[data-filter-chips]');
    var chipAttr = chipGroup ? chipGroup.dataset.filterChips : null;
    var chipVal = '';
    var countEl = document.getElementById('result-count');
    var emptyEl = document.getElementById('empty');

    function cards() { return Array.prototype.slice.call(list.querySelectorAll('.op')); }

    function setChip(v) {
      chipVal = v;
      if (!chipGroup) return;
      chipGroup.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.value === v)); });
    }

    function apply() {
      var tokens = q ? norm(q.value).split(/\s+/).filter(Boolean) : [];
      var n = 0;
      cards().forEach(function (c) {
        var ok = !c.classList.contains('is-expired');
        if (ok && tokens.length) { var t = norm(c.dataset.texto); ok = tokens.every(function (k) { return t.indexOf(k) > -1; }); }
        selects.forEach(function (s) { if (ok && s.value) ok = c.dataset[s.dataset.filter] === s.value; });
        if (ok && vig && vig.value) ok = daysLeft(c.dataset.vence) <= parseInt(vig.value, 10);
        if (ok && chipVal) ok = c.dataset[chipAttr] === chipVal;
        c.classList.toggle('is-hidden', !ok);
        if (ok) n++;
      });
      if (countEl) countEl.textContent = 'Mostrando ' + plural(n, countEl.dataset.uno, countEl.dataset.varios);
      if (emptyEl) emptyEl.classList.toggle('show', n === 0);
      sync();
    }

    function sync() {
      var p = new URLSearchParams();
      if (q && q.value.trim()) p.set('q', q.value.trim());
      selects.forEach(function (s) { if (s.value) p.set(s.dataset.filter, s.value); });
      if (chipVal) p.set(chipAttr, chipVal);
      var qs = p.toString();
      try { history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash); } catch (e) { /* vista previa */ }
    }

    function fillSelect(s) {
      if (!s.hasAttribute('data-auto')) return;
      var set = {};
      cards().forEach(function (c) { if (!c.classList.contains('is-expired')) set[c.dataset[s.dataset.filter]] = 1; });
      var cur = s.value; s.length = 1;
      Object.keys(set).sort(function (a, b) { return a.localeCompare(b, 'es'); }).forEach(function (v) {
        var o = document.createElement('option'); o.textContent = v; s.appendChild(o);
      });
      s.value = set[cur] ? cur : '';
    }

    function refresh() { selects.forEach(fillSelect); apply(); }

    function clear() {
      if (q) q.value = ''; selects.forEach(function (s) { s.value = ''; }); if (vig) vig.value = '';
      setChip(''); apply();
    }

    if (q) q.addEventListener('input', apply);
    selects.forEach(function (s) { s.addEventListener('change', apply); });
    if (vig) vig.addEventListener('change', apply);
    if (chipGroup) chipGroup.querySelectorAll('button').forEach(function (b) {
      b.addEventListener('click', function () { setChip(b.dataset.value); apply(); });
    });
    var clr = document.getElementById('f-clear'); if (clr) clr.addEventListener('click', clear);

    /* valores iniciales desde la dirección */
    selects.forEach(fillSelect);
    var p = new URLSearchParams(location.search);
    if (q && p.get('q')) q.value = p.get('q');
    selects.forEach(function (s) { if (p.get(s.dataset.filter)) s.value = p.get(s.dataset.filter); });
    if (chipAttr && p.get(chipAttr)) setChip(p.get(chipAttr));
    apply();
    return { apply: apply, refresh: refresh, clear: clear, setQuery: function (v) { clear(); if (q) q.value = v; apply(); } };
  }

  /* ---------- aviso flotante ---------- */
  var toastEl, toastTimer;
  function toast(msg) {
    toastEl = toastEl || document.getElementById('toast');
    if (!toastEl) return;
    toastEl.textContent = msg; toastEl.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 4500);
  }

  /* ---------- ventanas ---------- */
  document.querySelectorAll('dialog').forEach(function (d) {
    d.addEventListener('click', function (e) { if (e.target === d || e.target.closest('[data-close]')) d.close(); });
  });

  /* ---------- negociación ---------- */
  var NEG = {
    producto: ['Negociar este producto', 'Contanos quién sos y qué te interesa comprar.'],
    servicio: ['Solicitar cotización', 'Contale al proveedor qué necesitás.'],
    busqueda: ['Ofrecer lo que buscan', 'Contale a quien publicó la búsqueda qué podés ofrecerle.']
  };
  function openNeg(o) {
    var d = document.getElementById('dlg-neg');
    if (!d) return;
    d.className = 'k-' + o.kind;
    document.getElementById('neg-title').textContent = NEG[o.kind][0];
    document.getElementById('neg-sub').textContent = NEG[o.kind][1];
    var s = document.getElementById('neg-summary'); s.textContent = '';
    s.appendChild(el('strong', null, o.titulo));
    s.appendChild(el('span', null, o.info));
    document.getElementById('neg-form').reset();
    document.getElementById('neg-step-form').hidden = false;
    document.getElementById('neg-step-ok').hidden = true;
    d.showModal();
    document.getElementById('n-nom').focus();
  }
  var negForm = document.getElementById('neg-form');
  if (negForm) negForm.addEventListener('submit', function (e) {
    e.preventDefault();
    document.getElementById('neg-step-form').hidden = true;
    document.getElementById('neg-step-ok').hidden = false;
  });
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-negociar]');
    if (!b) return;
    var c = b.closest('.op');
    if (c) openNeg({ kind: c.dataset.kind, titulo: c.querySelector('.op-title').textContent, info: c.dataset.info });
  });

  window.Hub = {
    D: D, today: today, norm: norm, plural: plural, hsFmt: hsFmt, iso: iso, fecha: fecha, daysLeft: daysLeft,
    addBusinessDays: addBusinessDays, el: el, matchBusqueda: matchBusqueda, matchOferta: matchOferta,
    updateVigencia: updateVigencia, setupFilters: setupFilters, toast: toast, openNeg: openNeg
  };
})();
