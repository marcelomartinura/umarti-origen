/* Mesa de negociación: búsqueda de productos o servicios con coincidencias automáticas (prototipo, sin servidor) */
(function () {
  var H = window.Hub, el = H.el;
  var PLAZO = 5; // días hábiles para que el equipo responda
  var list = document.getElementById('list');
  var ICON_OK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg>';
  var ICON_CLOCK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>';

  function offerInfo(o) {
    var parts = [o.cod];
    if (o.hs) parts.push('SA ' + H.hsFmt(o.hs));
    parts.push((o.kind === 'servicio' ? 'Base: ' : 'Origen: ') + o.pais);
    return parts.join(' · ');
  }

  /* Estado de cada búsqueda: con coincidencia o en búsqueda por el equipo */
  function renderStatus(card, b) {
    var old = card.querySelector('.op-status'); if (old) old.remove();
    var m = H.matchBusqueda(b);
    card.dataset.estado = m.length ? 'match' : 'buscando';
    var box = el('div', 'op-status ' + (m.length ? 'st-match' : 'st-search'));
    box.insertAdjacentHTML('afterbegin', m.length ? ICON_OK : ICON_CLOCK);
    var txt = el('div');
    if (m.length) {
      txt.appendChild(el('b', null, 'Coincide con ' + H.plural(m.length, b.tipo === 'servicio' ? 'servicio publicado' : 'producto publicado', b.tipo === 'servicio' ? 'servicios publicados' : 'productos publicados')));
      var ul = el('ul');
      m.forEach(function (o) { var li = el('li'); var a = el('a', null, o.nombre); a.href = o.url; li.appendChild(a); ul.appendChild(li); });
      txt.appendChild(ul);
    } else {
      var limite = H.addBusinessDays(b.publicada, PLAZO);
      var vencido = limite < H.today;
      txt.appendChild(el('b', null, 'Nuestro equipo la está buscando'));
      txt.appendChild(el('span', null, vencido ? 'Búsqueda en curso. Si tenés este producto, ofrecelo.' : 'Respuesta antes del ' + H.fecha(H.iso(limite))));
    }
    box.appendChild(txt);
    card.appendChild(box);
  }

  function busquedaDeCard(c) {
    return H.D.busquedas.filter(function (b) { return b.cod === c.dataset.codigo; })[0];
  }

  /* Tarjetas iniciales */
  Array.prototype.slice.call(list.querySelectorAll('.op')).forEach(function (c) {
    H.updateVigencia(c);
    var b = busquedaDeCard(c); if (b) renderStatus(c, b);
  });
  var filters = H.setupFilters({ list: list });

  function updateStats() {
    var act = H.D.busquedas.filter(function (b) { return H.daysLeft(b.vence) >= 0; });
    document.getElementById('stat-b').textContent = act.length;
    document.getElementById('stat-m').textContent = act.filter(function (b) { return H.matchBusqueda(b).length; }).length;
    document.getElementById('stat-o').textContent = H.D.productos.length + H.D.servicios.length;
  }
  updateStats();

  /* ---------- formulario de búsqueda ---------- */
  var form = document.getElementById('search-form');
  var result = document.getElementById('search-result');
  var nombre = document.getElementById('s-nombre');
  var hs = document.getElementById('s-hs');
  var hint = document.getElementById('live-hint');
  var vence = document.getElementById('s-vence');

  function tipo() { return form.querySelector('input[name="tipo"]:checked').value; }

  function setTipo() {
    var t = tipo();
    form.querySelectorAll('[data-solo]').forEach(function (n) {
      var on = n.dataset.solo === t;
      n.hidden = !on;
      n.querySelectorAll('select, input').forEach(function (i) { i.disabled = !on; });
    });
    nombre.placeholder = t === 'servicio' ? 'Ej.: Despachante de aduana para importar a México' : 'Ej.: Aceite de oliva extra virgen';
    form.querySelector('[data-lbl]').textContent = t === 'servicio' ? '¿Qué servicio estás buscando?' : '¿Qué producto estás buscando?';
    liveHint();
  }

  var t0;
  function liveHint() {
    clearTimeout(t0);
    t0 = setTimeout(function () {
      var v = nombre.value.trim();
      hint.className = 'live-hint'; hint.textContent = '';
      if (v.length < 3 && hs.value.replace(/\D/g, '').length < 4) return;
      var m = H.matchBusqueda({ tipo: tipo(), nombre: v, hs: hs.disabled ? '' : hs.value.replace(/\D/g, '') });
      if (m.length) {
        hint.className = 'live-hint ok';
        hint.innerHTML = ICON_OK;
        hint.appendChild(document.createTextNode(' Hay ' + H.plural(m.length, 'coincidencia', 'coincidencias') + ' en ' + (tipo() === 'servicio' ? 'Servicios de Comercio Exterior' : 'Productos de exportación')));
      } else {
        hint.className = 'live-hint no';
        hint.innerHTML = ICON_CLOCK;
        hint.appendChild(document.createTextNode(' Todavía no está publicado: nuestro equipo lo buscará por vos'));
      }
    }, 220);
  }

  function resetForm() {
    form.reset();
    vence.min = H.iso(H.today);
    vence.value = H.iso(new Date(H.today.getTime() + 90 * 86400000));
    hint.className = 'live-hint'; hint.textContent = '';
    setTipo();
    form.hidden = false; result.hidden = true; result.textContent = '';
  }

  form.querySelectorAll('input[name="tipo"]').forEach(function (r) { r.addEventListener('change', setTipo); });
  nombre.addEventListener('input', liveHint);
  hs.addEventListener('input', liveHint);

  function nextCode() {
    var max = 0;
    H.D.busquedas.forEach(function (b) { max = Math.max(max, parseInt(b.cod.slice(5), 10) || 0); });
    return 'UO-B-' + String(max + 1).padStart(4, '0');
  }

  function buildCard(b) {
    var a = el('article', 'op op--busqueda is-new');
    a.id = b.cod.toLowerCase();
    a.dataset.kind = 'busqueda'; a.dataset.codigo = b.cod; a.dataset.tipo = b.tipo;
    a.dataset.pais = b.pais; a.dataset.vence = b.vence;
    a.dataset.texto = [b.nombre, b.hs, H.hsFmt(b.hs), b.cod, b.sector, b.pais, b.origen].join(' ').toLowerCase();
    a.dataset.info = b.cod + (b.hs ? ' · SA ' + H.hsFmt(b.hs) : '') + ' · Destino: ' + b.pais;
    var top = el('div', 'op-top');
    top.appendChild(el('span', 'op-code', b.cod));
    var chips = el('span', 'op-chips');
    chips.appendChild(el('span', 'chip chip-review', 'En revisión'));
    chips.appendChild(el('span', 'chip chip-kind', b.tipo === 'servicio' ? 'Servicio' : 'Producto'));
    if (b.hs) chips.appendChild(el('span', 'chip chip-hs', 'SA ' + H.hsFmt(b.hs)));
    top.appendChild(chips); a.appendChild(top);
    a.appendChild(el('h3', 'op-title', b.nombre));
    a.appendChild(el('p', 'op-sector', b.sector));
    var dl = el('dl', 'op-meta');
    [['Destino', b.pais], ['Volumen', b.vol || 'A convenir'], ['Origen preferido', b.origen || 'Sin preferencia', 'wide']].forEach(function (r) {
      var w = el('div', r[2] || null); w.appendChild(el('dt', null, r[0])); w.appendChild(el('dd', null, r[1])); dl.appendChild(w);
    });
    a.appendChild(dl);
    var bottom = el('div', 'op-bottom');
    var v = el('span', 'op-vence', 'Vigente hasta ');
    var tm = el('time', null, H.fecha(b.vence)); tm.dateTime = b.vence; v.appendChild(tm);
    bottom.appendChild(v);
    var cta = el('button', 'op-cta', b.tipo === 'servicio' ? 'Ofrezco este servicio' : 'Tengo este producto');
    cta.type = 'button'; cta.dataset.negociar = '';
    bottom.appendChild(cta); a.appendChild(bottom);
    return a;
  }

  function showResult(b, m, mail) {
    form.hidden = true; result.hidden = false; result.textContent = '';
    var wrap = el('div', 'result ' + (m.length ? 'yes' : 'no'));
    var ic = el('div', 'result-icon');
    ic.innerHTML = m.length
      ? '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg>'
      : '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>';
    wrap.appendChild(ic);
    var p = el('p');
    if (m.length) {
      wrap.appendChild(el('h2', null, '¡Hay coincidencia!'));
      p.textContent = 'Encontramos ' + H.plural(m.length, 'oferta publicada', 'ofertas publicadas') + ' que responde' + (m.length === 1 ? '' : 'n') + ' a tu búsqueda. Te vinculamos con quien la publicó para que empiece la negociación.';
      wrap.appendChild(p);
      var ml = el('div', 'match-list');
      m.forEach(function (o) {
        var it = el('div', 'match-item');
        it.style.setProperty('--op-accent', o.kind === 'servicio' ? 'var(--mustard)' : 'var(--terra)');
        var info = el('div');
        info.appendChild(el('strong', null, o.nombre));
        info.appendChild(el('small', null, offerInfo(o)));
        it.appendChild(info);
        var acts = el('div', 'acts');
        var link = el('a', null, 'Ver oferta'); link.href = o.url; acts.appendChild(link);
        var neg = el('button', 'btn-submit', 'Iniciar negociación'); neg.type = 'button';
        neg.style.padding = '10px 18px'; neg.style.fontSize = '0.9rem';
        neg.addEventListener('click', function () { H.openNeg({ kind: o.kind, titulo: o.nombre, info: offerInfo(o) }); });
        acts.appendChild(neg);
        it.appendChild(acts);
        ml.appendChild(it);
      });
      wrap.appendChild(ml);
    } else {
      var limite = H.addBusinessDays(b.publicada, PLAZO);
      wrap.appendChild(el('h2', null, 'Todavía no tenemos este ' + (b.tipo === 'servicio' ? 'servicio' : 'producto')));
      p.textContent = 'Nuestro equipo va a buscarlo entre productores y proveedores, y te va a responder en un plazo de ' + PLAZO + ' días hábiles.';
      wrap.appendChild(p);
      var dl = el('div', 'deadline');
      dl.appendChild(el('strong', null, H.fecha(H.iso(limite)).slice(0, 5)));
      dl.appendChild(el('span', null, 'Fecha límite de respuesta. Te escribimos a ' + mail + ' con lo que encontremos.'));
      wrap.appendChild(dl);
    }
    var note = el('p');
    note.appendChild(document.createTextNode('Tu búsqueda quedó publicada en la mesa como '));
    note.appendChild(el('span', 'code', b.cod));
    note.appendChild(document.createTextNode(', así otros vendedores también pueden verla.'));
    note.style.color = 'var(--muted)'; note.style.fontSize = '0.92rem'; note.style.marginBottom = '18px';
    wrap.appendChild(note);
    var foot = el('div', 'result-foot');
    var again = el('button', 'link-btn', 'Hacer otra búsqueda'); again.type = 'button';
    again.addEventListener('click', resetForm);
    var see = el('a', 'text-link', 'Ver mi búsqueda en la mesa'); see.href = '#' + b.cod.toLowerCase();
    foot.appendChild(see); foot.appendChild(again);
    wrap.appendChild(foot);
    result.appendChild(wrap);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var fd = new FormData(form);
    var t = fd.get('tipo');
    var b = {
      cod: nextCode(), tipo: t, nombre: fd.get('nombre').trim(),
      hs: t === 'producto' ? (fd.get('hs') || '').replace(/\D/g, '').slice(0, 6) : '',
      sector: t === 'producto' ? fd.get('sector') : fd.get('categoria'),
      pais: fd.get('pais').trim(), origen: (fd.get('origen') || '').trim(), vol: (fd.get('vol') || '').trim(),
      publicada: H.iso(H.today), vence: fd.get('vence')
    };
    H.D.busquedas.unshift(b);
    var m = H.matchBusqueda(b);
    var card = buildCard(b);
    list.insertBefore(card, list.firstChild);
    renderStatus(card, b);
    filters.clear(); filters.refresh();
    updateStats();
    showResult(b, m, fd.get('mail'));
    document.getElementById('buscar').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  resetForm();
})();
