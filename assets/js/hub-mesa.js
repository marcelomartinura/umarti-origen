/* Hub: Mesa de Negocio de Oportunidades Comerciales Globales — buscador e "publicar búsqueda" (prototipo, no envía nada) */
(function () {
  'use strict';
  var H = window.Hub; if (!H) return;
  var D = H.D, $ = function (s) { return document.querySelector(s); };
  var form = $('#ia-form'), q = $('#ia-q'), pub = $('#ia-pub'), datos = $('#ia-datos'), res = $('#ia-res');
  if (!form) return;

  var STOP = ('para desde como tipo busco buscamos necesito necesitamos quiero queremos importar exportar comprar ' +
    'compra venta toneladas tonelada kilos kilo unidades contenedor contenedores por mes semana anio cada calidad entrega ' +
    'hacia con sin una uno unos unas los las del que mas').split(' ');
  function stems(t) {
    var out = {};
    H.norm(t).split(/[^a-z0-9]+/).forEach(function (w) {
      if (w.length < 4 || STOP.indexOf(w) > -1 || /^\d+$/.test(w)) return;
      out[w.slice(0, 5)] = 1;
    });
    return out;
  }
  function puntaje(qs, txt) { var s = stems(txt), n = 0; for (var k in qs) if (s[k]) n++; return n; }
  function paisEn(texto) {
    var t = H.norm(texto), hit = '';
    Array.prototype.forEach.call(document.querySelectorAll('#paises option'), function (o) { if (t.indexOf(H.norm(o.value)) > -1) hit = o.value; });
    return hit;
  }

  function buscar(texto) {
    var qs = stems(texto), hs = (texto.match(/\b\d{4}(\.?\d{2})?\b/) || [''])[0].replace('.', '');
    function rank(lista, campos) {
      return lista.map(function (o) {
        var p = puntaje(qs, campos(o));
        if (hs && o.hs && o.hs.slice(0, 4) === hs.slice(0, 4)) p += 3;
        return { o: o, p: p };
      }).filter(function (x) { return x.p > 0; }).sort(function (a, b) { return b.p - a.p; }).map(function (x) { return x.o; });
    }
    return {
      ofertas: rank(D.productos.concat(D.servicios), function (o) { return [o.nombre, o.claves, o.categoria, o.sector, o.detalle].join(' '); }).slice(0, 6),
      busquedas: rank(D.busquedas.filter(function (b) { return H.daysLeft(b.vence) >= 0; }), function (b) { return [b.nombre, b.sector].join(' '); }).slice(0, 3)
    };
  }

  function item(o) {
    var serv = o.kind === 'servicio';
    var meta = serv ? (o.categoria + ' · ' + o.pais) : ((o.categoria || o.sector) + ' · Origen: ' + o.pais + (o.vol ? ' · ' + o.vol : ''));
    return '<a class="ir" href="' + o.url + '"><span class="ir-k ' + (serv ? 's' : 'p') + '">' + (serv ? 'Servicio' : 'Producto') + '</span>' +
      '<b>' + esc(o.nombre) + '</b><small>' + esc(meta) + '</small><span class="ir-go">Ver y negociar →</span></a>';
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* ---------- publicar búsqueda ---------- */
  var venceDef = new Date(); venceDef.setDate(venceDef.getDate() + 90);
  $('#ia-vence').value = H.iso(venceDef);
  $('#ia-vence').min = H.iso(new Date());
  function togglePub() {
    datos.hidden = !pub.checked;
    ['ia-pais', 'ia-vence', 'ia-emp', 'ia-mail'].forEach(function (id) { $('#' + id).required = pub.checked; });
    $('#ia-go-txt').textContent = pub.checked ? 'Buscar y publicar' : 'Buscar';
    autoPais();
  }
  var paisAuto = true;
  $('#ia-pais').addEventListener('input', function () { paisAuto = false; });
  function autoPais() { if (pub.checked && (paisAuto || !$('#ia-pais').value)) { var x = paisEn(q.value); if (x) { $('#ia-pais').value = x; paisAuto = true; } } }
  pub.addEventListener('change', togglePub);
  q.addEventListener('change', autoPais);

  document.querySelectorAll('[data-ej]').forEach(function (b) {
    b.addEventListener('click', function () { q.value = b.dataset.ej; q.focus(); form.requestSubmit ? form.requestSubmit() : form.submit(); });
  });
  q.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : null; } });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var texto = q.value.trim(); if (!texto) return;
    autoPais();
    if (pub.checked && !form.checkValidity()) { form.reportValidity(); return; }
    var r = buscar(texto), html = '';
    if (r.ofertas.length) {
      html += '<h3>Encontramos ' + H.plural(r.ofertas.length, 'oferta que coincide', 'ofertas que coinciden') + '</h3><div class="ir-list">' + r.ofertas.map(item).join('') + '</div>';
    } else {
      html += '<div class="ir-none"><b>Todavía no hay ofertas publicadas que coincidan.</b><span>Dejá publicada tu búsqueda y nuestro equipo sale a buscarlo entre productores y proveedores: te respondemos en 5 días hábiles.</span></div>';
    }
    if (r.busquedas.length) {
      html += '<p class="ir-otros">Otros compradores buscan algo parecido: ' + r.busquedas.map(function (b) {
        return '<a href="../oportunidades-globales/#' + b.cod.toLowerCase() + '">' + esc(b.nombre) + ' (' + esc(b.pais) + ')</a>';
      }).join(', ') + '.</p>';
    }
    if (pub.checked) {
      var cod = 'UO-B-' + String(Math.floor(1000 + Math.random() * 9000));
      html = '<div class="ir-ok"><b>Tu búsqueda quedó publicada · ' + cod + '</b><span>Vigente hasta el ' + H.fecha($('#ia-vence').value) + '. ' +
        (r.ofertas.length ? 'Ya te mostramos las ofertas que coinciden.' : 'Si nadie la ofrece, te respondemos en 5 días hábiles a ' + esc($('#ia-mail').value) + '.') +
        '</span><em>Prototipo: por ahora la búsqueda se ve solo en tu pantalla y no se envía.</em></div>' + html;
    } else if (!r.ofertas.length) {
      html += '<button type="button" class="ir-pub" id="ir-pub">Dejar publicada mi búsqueda</button>';
    }
    res.innerHTML = html; res.hidden = false;
    var b = $('#ir-pub');
    if (b) b.addEventListener('click', function () { pub.checked = true; togglePub(); $('#ia-pais').focus(); });
    res.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });
})();
