/* Productos de exportación y Servicios de comercio exterior: filtros, búsquedas que coinciden y publicar (prototipo) */
(function () {
  var H = window.Hub, el = H.el;
  var kind = document.body.dataset.kind; // 'producto' o 'servicio'
  var pool = kind === 'servicio' ? H.D.servicios : H.D.productos;
  var list = document.getElementById('list');
  var ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h14l-4-4M20 16H6l4 4"/></svg>';

  /* Muestra cuántas búsquedas de la Mesa piden este producto o servicio */
  function renderDemand(card) {
    var old = card.querySelector('.op-status'); if (old) old.remove();
    var m = H.matchOferta(card.dataset.codigo);
    if (!m.length) return 0;
    var a = el('a', 'op-status st-match');
    a.href = '../mesa-de-negociacion/#' + m[0].cod.toLowerCase();
    a.insertAdjacentHTML('afterbegin', ICON);
    var t = el('div');
    t.appendChild(el('b', null, H.plural(m.length, 'búsqueda', 'búsquedas') + ' en la Mesa de negociación'));
    t.appendChild(el('span', null, 'Desde ' + m.map(function (b) { return b.pais; }).filter(function (v, i, arr) { return arr.indexOf(v) === i; }).join(', ') + '. Ver búsqueda'));
    a.appendChild(t);
    card.appendChild(a);
    return m.length;
  }

  var cards = Array.prototype.slice.call(list.querySelectorAll('.op'));
  cards.forEach(function (c) { H.updateVigencia(c); renderDemand(c); });
  var filters = H.setupFilters({ list: list });

  function updateStats() {
    var all = Array.prototype.slice.call(list.querySelectorAll('.op')).filter(function (c) { return !c.classList.contains('is-expired'); });
    var paises = {};
    all.forEach(function (c) { paises[c.dataset.pais] = 1; });
    document.getElementById('stat-n').textContent = all.length;
    document.getElementById('stat-p').textContent = Object.keys(paises).length;
    document.getElementById('stat-d').textContent = all.filter(function (c) { return c.querySelector('.op-status'); }).length;
  }
  updateStats();

  /* ---------- publicar ---------- */
  var dlg = document.getElementById('dlg-pub');
  var form = document.getElementById('pub-form');
  function openPub() {
    form.reset();
    var v = form.querySelector('[name="vence"]');
    if (v) { v.min = H.iso(H.today); v.value = H.iso(new Date(H.today.getTime() + 180 * 86400000)); }
    dlg.showModal();
    form.querySelector('input:not([type=hidden])').focus();
  }
  document.querySelectorAll('[data-publicar]').forEach(function (b) { b.addEventListener('click', openPub); });
  if (location.hash === '#publicar') setTimeout(openPub, 300);

  function nextCode() {
    var pre = kind === 'servicio' ? 'UO-S-' : 'UO-P-', max = 0;
    pool.forEach(function (o) { max = Math.max(max, parseInt(o.cod.slice(5), 10) || 0); });
    return pre + String(max + 1).padStart(4, '0');
  }

  function buildCard(o) {
    var a = el('article', 'op op--' + kind + ' is-new');
    a.id = o.cod.toLowerCase();
    a.dataset.kind = kind; a.dataset.codigo = o.cod; a.dataset.pais = o.pais;
    if (o.vence) a.dataset.vence = o.vence;
    if (kind === 'producto') a.dataset.sector = o.sector; else a.dataset.categoria = o.categoria;
    a.dataset.texto = [o.nombre, o.hs, H.hsFmt(o.hs), o.cod, o.sector || o.categoria, o.pais, o.region, o.destinos || o.cobertura, o.detalle].join(' ').toLowerCase();
    a.dataset.info = o.cod + (o.hs ? ' · SA ' + H.hsFmt(o.hs) : '') + (kind === 'servicio' ? ' · Base: ' : ' · Origen: ') + o.pais;
    var top = el('div', 'op-top');
    top.appendChild(el('span', 'op-code', o.cod));
    var chips = el('span', 'op-chips');
    chips.appendChild(el('span', 'chip chip-review', 'En revisión'));
    if (kind === 'producto') chips.appendChild(el('span', 'chip chip-hs', o.hs ? 'SA ' + H.hsFmt(o.hs) : 'Sin posición'));
    top.appendChild(chips); a.appendChild(top);
    a.appendChild(el('h3', 'op-title', o.nombre));
    a.appendChild(el('p', 'op-sector', o.sector || o.categoria));
    if (o.detalle) a.appendChild(el('p', 'op-desc', o.detalle));
    var dl = el('dl', 'op-meta');
    var rows = kind === 'producto'
      ? [['Origen', o.pais + (o.region ? ' · ' + o.region : '')], ['Volumen disponible', o.vol || 'A convenir'], ['Mercados de interés', o.destinos || 'A convenir', 'wide']]
      : [['Base', o.pais + (o.region ? ' · ' + o.region : '')], ['Cobertura', o.cobertura || 'A convenir', 'wide']];
    rows.forEach(function (r) { var w = el('div', r[2] || null); w.appendChild(el('dt', null, r[0])); w.appendChild(el('dd', null, r[1])); dl.appendChild(w); });
    a.appendChild(dl);
    var bottom = el('div', 'op-bottom');
    if (o.vence) {
      var v = el('span', 'op-vence', 'Vigente hasta '); var tm = el('time', null, H.fecha(o.vence)); tm.dateTime = o.vence; v.appendChild(tm);
      bottom.appendChild(v);
    } else bottom.appendChild(el('span', 'op-vence', 'Publicado hoy'));
    var cta = el('button', 'op-cta', kind === 'producto' ? 'Negociar' : 'Solicitar cotización'); cta.type = 'button'; cta.dataset.negociar = '';
    bottom.appendChild(cta); a.appendChild(bottom);
    return a;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var fd = new FormData(form);
    var o = { cod: nextCode(), kind: kind, nombre: fd.get('nombre').trim(), pais: fd.get('pais').trim(), region: (fd.get('region') || '').trim(), claves: '' };
    if (kind === 'producto') {
      o.hs = (fd.get('hs') || '').replace(/\D/g, '').slice(0, 6); o.sector = fd.get('sector');
      o.destinos = (fd.get('destinos') || '').trim(); o.vol = (fd.get('vol') || '').trim(); o.vence = fd.get('vence');
    } else {
      o.hs = ''; o.categoria = fd.get('categoria'); o.cobertura = (fd.get('cobertura') || '').trim(); o.detalle = (fd.get('detalle') || '').trim();
    }
    pool.push(o);
    var card = buildCard(o);
    list.insertBefore(card, list.firstChild);
    var n = renderDemand(card);
    dlg.close();
    filters.clear(); filters.refresh(); updateStats();
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    H.toast(n
      ? '¡Coincide con ' + H.plural(n, 'búsqueda', 'búsquedas') + ' de la Mesa! Quedó publicado como ' + o.cod + ', en revisión.'
      : 'Quedó publicado como ' + o.cod + ', en revisión.');
  });
})();
