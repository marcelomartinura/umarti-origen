/* Hub de Oportunidades: filtros, coincidencias, publicar y negociar (prototipo, sin servidor) */
(function () {
  var DAY = 86400000;
  var today = new Date(); today.setHours(0, 0, 0, 0);

  var board = document.getElementById('board');
  var lists = { venta: document.getElementById('list-venta'), compra: document.getElementById('list-compra') };
  var f = {
    q: document.getElementById('f-q'),
    sector: document.getElementById('f-sector'),
    pais: document.getElementById('f-pais'),
    vig: document.getElementById('f-vig'),
    clear: document.getElementById('f-clear'),
    seg: document.querySelectorAll('.seg button')
  };
  var ver = 'todo';

  function cards() { return Array.prototype.slice.call(board.querySelectorAll('.op')); }
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function daysLeft(card) { return Math.round((new Date(card.dataset.vence + 'T00:00:00') - today) / DAY); }
  function plural(n, uno, varios) { return n + ' ' + (n === 1 ? uno : varios); }
  function hsFmt(hs) { return hs ? hs.slice(0, 4) + '.' + hs.slice(4) : ''; }

  /* Vigencia: marca las que vencen pronto y oculta las vencidas */
  function updateVigencia(card) {
    var d = daysLeft(card);
    var el = card.querySelector('.op-vence');
    if (d < 0) { card.classList.add('is-expired'); return; }
    if (d <= 30) {
      el.classList.add('pronto');
      el.textContent = d === 0 ? 'Vence hoy' : 'Vence en ' + plural(d, 'día', 'días');
    }
  }

  /* Coincidencias: cruza ventas y compras por los primeros 4 dígitos de la posición arancelaria */
  function updateMatches() {
    var all = cards().filter(function (c) { return !c.classList.contains('is-expired'); });
    all.forEach(function (c) {
      var old = c.querySelector('.op-match'); if (old) old.remove();
      var hs4 = (c.dataset.hs || '').slice(0, 4);
      if (!hs4) return;
      var otros = all.filter(function (o) { return o.dataset.tipo !== c.dataset.tipo && (o.dataset.hs || '').slice(0, 4) === hs4; });
      if (!otros.length) return;
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'op-match'; b.dataset.hs4 = hs4;
      b.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h14l-4-4M20 16H6l4 4"/></svg>';
      var t = document.createElement('b');
      t.textContent = 'Coincide con ' + (c.dataset.tipo === 'venta'
        ? plural(otros.length, 'búsqueda de compra', 'búsquedas de compra')
        : plural(otros.length, 'oferta de venta', 'ofertas de venta'));
      var v = document.createElement('span'); v.textContent = 'Ver';
      b.appendChild(t); b.appendChild(v);
      c.appendChild(b);
    });
  }

  function fillPaises() {
    var current = f.pais.value;
    var set = {};
    cards().forEach(function (c) { if (!c.classList.contains('is-expired')) set[c.dataset.pais] = 1; });
    var paises = Object.keys(set).sort(function (a, b) { return a.localeCompare(b, 'es'); });
    f.pais.length = 1;
    paises.forEach(function (p) { var o = document.createElement('option'); o.textContent = p; f.pais.appendChild(o); });
    f.pais.value = paises.indexOf(current) > -1 ? current : '';
    return paises.length;
  }

  function updateStats() {
    var act = cards().filter(function (c) { return !c.classList.contains('is-expired'); });
    document.getElementById('stat-v').textContent = act.filter(function (c) { return c.dataset.tipo === 'venta'; }).length;
    document.getElementById('stat-c').textContent = act.filter(function (c) { return c.dataset.tipo === 'compra'; }).length;
    document.getElementById('stat-p').textContent = fillPaises();
  }

  /* Filtros */
  function apply() {
    var tokens = norm(f.q.value).split(/\s+/).filter(Boolean);
    var sector = f.sector.value, pais = f.pais.value, vig = parseInt(f.vig.value, 10);
    var n = { venta: 0, compra: 0 };
    cards().forEach(function (c) {
      var ok = !c.classList.contains('is-expired');
      if (ok && tokens.length) {
        var txt = norm(c.dataset.texto);
        ok = tokens.every(function (t) { return txt.indexOf(t) > -1; });
      }
      if (ok && sector) ok = c.dataset.sector === sector;
      if (ok && pais) ok = c.dataset.pais === pais;
      if (ok && vig) ok = daysLeft(c) <= vig;
      c.classList.toggle('is-hidden', !ok);
      if (ok) n[c.dataset.tipo]++;
    });
    board.classList.toggle('solo-venta', ver === 'venta');
    board.classList.toggle('solo-compra', ver === 'compra');
    document.getElementById('count-v').textContent = n.venta;
    document.getElementById('count-c').textContent = n.compra;
    document.getElementById('empty-venta').classList.toggle('show', n.venta === 0);
    document.getElementById('empty-compra').classList.toggle('show', n.compra === 0);
    var partes = [];
    if (ver !== 'compra') partes.push(plural(n.venta, 'oferta', 'ofertas'));
    if (ver !== 'venta') partes.push(plural(n.compra, 'búsqueda', 'búsquedas'));
    document.getElementById('result-count').textContent = 'Mostrando ' + partes.join(' y ');
    syncUrl();
  }

  function setVer(v) {
    ver = v;
    f.seg.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.ver === v)); });
  }

  function syncUrl() {
    var p = new URLSearchParams();
    if (f.q.value.trim()) p.set('q', f.q.value.trim());
    if (f.sector.value) p.set('sector', f.sector.value);
    if (f.pais.value) p.set('pais', f.pais.value);
    if (ver !== 'todo') p.set('ver', ver);
    var qs = p.toString();
    try { history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash); } catch (e) { /* vista previa sin historial */ }
  }

  function readUrl() {
    var p = new URLSearchParams(location.search);
    if (p.get('q')) f.q.value = p.get('q');
    if (p.get('sector')) f.sector.value = p.get('sector');
    if (p.get('pais')) f.pais.value = p.get('pais');
    if (['venta', 'compra'].indexOf(p.get('ver')) > -1) setVer(p.get('ver'));
  }

  function clearFilters() {
    f.q.value = ''; f.sector.value = ''; f.pais.value = ''; f.vig.value = '';
    setVer('todo'); apply();
  }

  [f.sector, f.pais, f.vig].forEach(function (el) { el.addEventListener('change', apply); });
  f.q.addEventListener('input', apply);
  f.clear.addEventListener('click', clearFilters);
  f.seg.forEach(function (b) { b.addEventListener('click', function () { setVer(b.dataset.ver); apply(); }); });

  /* Clic en una coincidencia: filtra por esa posición arancelaria */
  board.addEventListener('click', function (e) {
    var m = e.target.closest('.op-match');
    if (m) {
      f.q.value = m.dataset.hs4; f.sector.value = ''; f.pais.value = ''; f.vig.value = '';
      setVer('todo'); apply();
      document.getElementById('oportunidades').scrollIntoView({ behavior: 'smooth' });
      return;
    }
    var n = e.target.closest('[data-negociar]');
    if (n) openNeg(n.closest('.op'));
  });

  /* Ventanas */
  function closeDlg(d) { if (d.open) d.close(); }
  document.querySelectorAll('dialog').forEach(function (d) {
    d.addEventListener('click', function (e) {
      if (e.target === d || e.target.closest('[data-close]')) closeDlg(d);
    });
  });

  var toastEl = document.getElementById('toast'), toastTimer;
  function toast(msg) {
    toastEl.textContent = msg; toastEl.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 4200);
  }

  /* Publicar */
  var dPub = document.getElementById('dlg-pub');
  var pubForm = document.getElementById('pub-form');
  var COPY = {
    venta: { title: 'Ingresá tus productos', sub: 'Publicá tu oferta de venta en la mesa de negociación.', ph: 'Ej.: Vino Malbec embotellado, 750 ml', extra: 'Ej.: México, España' },
    compra: { title: 'Ingresá el producto que te interesa', sub: 'Publicá tu búsqueda de compra y te acercamos a quienes lo venden.', ph: 'Ej.: Miel orgánica certificada', extra: 'Ej.: Argentina o sin preferencia' }
  };
  function setTipo(t) {
    dPub.className = 'dlg-' + t;
    document.getElementById('pub-title').textContent = COPY[t].title;
    document.getElementById('pub-sub').textContent = COPY[t].sub;
    document.getElementById('p-prod').placeholder = COPY[t].ph;
    document.getElementById('p-extra').placeholder = COPY[t].extra;
    dPub.querySelectorAll('[data-lbl-venta]').forEach(function (el) { el.hidden = t !== 'venta'; });
    dPub.querySelectorAll('[data-lbl-compra]').forEach(function (el) { el.hidden = t !== 'compra'; });
    pubForm.querySelector('input[value="' + t + '"]').checked = true;
  }
  function isoDate(d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function openPub(t) {
    pubForm.reset();
    setTipo(t);
    var v = document.getElementById('p-vence');
    v.min = isoDate(today);
    v.value = isoDate(new Date(today.getTime() + 90 * DAY));
    dPub.showModal();
    document.getElementById('p-prod').focus();
  }
  document.querySelectorAll('[data-publicar]').forEach(function (b) {
    b.addEventListener('click', function () { openPub(b.dataset.publicar); });
  });
  pubForm.querySelectorAll('input[name="tipo"]').forEach(function (r) {
    r.addEventListener('change', function () { setTipo(r.value); });
  });

  function nextCode(t) {
    var pre = t === 'venta' ? 'UO-V-' : 'UO-C-', max = 0;
    cards().forEach(function (c) {
      if (c.dataset.codigo.indexOf(pre) === 0) max = Math.max(max, parseInt(c.dataset.codigo.slice(5), 10) || 0);
    });
    return pre + String(max + 1).padStart(4, '0');
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function buildCard(d) {
    var a = el('article', 'op op--' + d.tipo + ' is-new');
    a.id = d.cod.toLowerCase();
    a.dataset.tipo = d.tipo; a.dataset.hs = d.hs; a.dataset.sector = d.sector;
    a.dataset.pais = d.pais; a.dataset.vence = d.vence; a.dataset.codigo = d.cod;
    a.dataset.texto = [d.prod, d.hs, hsFmt(d.hs), d.cod, d.sector, d.pais, d.extra].join(' ').toLowerCase();

    var top = el('div', 'op-top');
    top.appendChild(el('span', 'op-code', d.cod));
    var chips = el('span', 'op-chips');
    chips.appendChild(el('span', 'chip chip-review', 'En revisión'));
    chips.appendChild(el('span', 'chip chip-hs', d.hs ? 'SA ' + hsFmt(d.hs) : 'Sin posición'));
    top.appendChild(chips);
    a.appendChild(top);
    a.appendChild(el('h3', 'op-title', d.prod));
    a.appendChild(el('p', 'op-sector', d.sector));

    var dl = el('dl', 'op-meta');
    var rows = d.tipo === 'venta'
      ? [['Origen', d.pais], ['Mercados de interés', d.extra || 'A convenir'], ['Volumen disponible', d.vol || 'A convenir']]
      : [['Destino', d.pais], ['Origen preferido', d.extra || 'Sin preferencia'], ['Volumen requerido', d.vol || 'A convenir']];
    rows.forEach(function (r) {
      var w = el('div'); w.appendChild(el('dt', null, r[0])); w.appendChild(el('dd', null, r[1])); dl.appendChild(w);
    });
    a.appendChild(dl);

    var bottom = el('div', 'op-bottom');
    var ven = el('span', 'op-vence', 'Vigente hasta ');
    var tm = el('time', null, d.vence.split('-').reverse().join('/')); tm.dateTime = d.vence;
    ven.appendChild(tm);
    bottom.appendChild(ven);
    var cta = el('button', 'op-cta', d.tipo === 'venta' ? 'Negociar' : 'Tengo este producto');
    cta.type = 'button'; cta.dataset.negociar = '';
    bottom.appendChild(cta);
    a.appendChild(bottom);
    return a;
  }

  pubForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var fd = new FormData(pubForm);
    var t = fd.get('tipo');
    var d = {
      tipo: t, cod: nextCode(t),
      prod: fd.get('prod').trim(), hs: (fd.get('hs') || '').replace(/\D/g, '').slice(0, 6),
      sector: fd.get('sector'), pais: fd.get('pais').trim(), extra: fd.get('extra').trim(),
      vol: fd.get('vol').trim(), vence: fd.get('vence')
    };
    var card = buildCard(d);
    lists[t].insertBefore(card, lists[t].firstChild);
    updateVigencia(card);
    closeDlg(dPub);
    updateMatches(); updateStats();
    clearFilters();
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    toast((t === 'venta' ? 'Tu oferta' : 'Tu búsqueda') + ' quedó en la mesa como ' + d.cod + ', en revisión.');
  });

  /* Negociar */
  var dNeg = document.getElementById('dlg-neg');
  function openNeg(card) {
    var t = card.dataset.tipo;
    dNeg.className = 'dlg-' + t;
    document.getElementById('neg-title').textContent = t === 'venta' ? 'Negociar esta oferta' : 'Ofrecer tu producto';
    document.getElementById('neg-sub').textContent = t === 'venta'
      ? 'Contanos quién sos y qué te interesa comprar.'
      : 'Contale al comprador qué podés ofrecerle.';
    var s = document.getElementById('neg-summary');
    s.textContent = '';
    s.appendChild(el('strong', null, card.querySelector('.op-title').textContent));
    var info = [card.dataset.codigo];
    if (card.dataset.hs) info.push('SA ' + hsFmt(card.dataset.hs));
    info.push((t === 'venta' ? 'Origen: ' : 'Destino: ') + card.dataset.pais);
    s.appendChild(el('span', null, info.join(' · ')));
    document.getElementById('neg-form').reset();
    document.getElementById('neg-step-form').hidden = false;
    document.getElementById('neg-step-ok').hidden = true;
    dNeg.showModal();
    document.getElementById('n-nom').focus();
  }
  document.getElementById('neg-form').addEventListener('submit', function (e) {
    e.preventDefault();
    document.getElementById('neg-step-form').hidden = true;
    document.getElementById('neg-step-ok').hidden = false;
  });

  /* Inicio */
  cards().forEach(updateVigencia);
  updateMatches();
  updateStats();
  readUrl();
  apply();
  if (location.hash.length > 1) {
    var target = document.getElementById(location.hash.slice(1));
    if (target && target.classList.contains('op')) target.classList.add('is-new');
  }
})();
