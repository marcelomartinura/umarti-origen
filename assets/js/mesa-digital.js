/* Mesa de negociación: vista previa interactiva con datos de ejemplo (no envía nada) */
(function () {
  'use strict';
  var $ = function (s) { return document.querySelector(s); };
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var usd = new Intl.NumberFormat('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  var n0 = new Intl.NumberFormat('es-AR');
  var INCOTERMS = ['EXW', 'FOB', 'CIF', 'DAP', 'DDP'];
  var PAGOS = ['30% anticipo y 70% contra documentos', 'Carta de crédito', 'Transferencia al contado', '100% contra documentos'];
  var ETAPAS = ['Negociación', 'Acuerdo', 'Depósito', 'Cierre'];

  /* ---------- datos del ejemplo ---------- */
  var p = new URLSearchParams(location.search), B = window.MESA_BUSQUEDAS || {}, b = B[p.get('b')];
  var prod = b ? b.nombre : 'Yerba mate elaborada con palo';
  var destino = b ? b.pais : 'México';
  $('#md-titulo').textContent = prod;
  $('#md-sub').textContent = 'Comprador en ' + destino + ' · Vendedor en Argentina';

  var hoy = new Date(); hoy.setDate(hoy.getDate() + 45);
  var terms = { precio: 4.2, cantidad: 20000, incoterm: 'FOB', pago: PAGOS[0], entrega: hoy.toISOString().slice(0, 10) };
  var hist = [], turno = 'vendedor', estado = 'oferta', etapa = 0, quien = 'comprador';

  /* ---------- gastos según Incoterm ---------- */
  function gastos(t) {
    var valor = t.precio * t.cantidad;
    var V = 'Vendedor', C = 'Comprador', i = INCOTERMS.indexOf(t.incoterm);
    return [
      ['Despacho de exportación', 'USD 450', i === 0 ? C : V],
      ['Certificado de origen', 'USD 120', V],
      ['Flete internacional', 'USD 3.800', i >= 2 ? V : C],
      ['Seguro de la carga', 'USD ' + usd.format(valor * 0.005), i >= 2 ? V : C],
      ['Despacho e impuestos de importación', 'Según posición arancelaria', i === 4 ? V : C]
    ];
  }

  function fecha(iso) { var x = iso.split('-'); return x[2] + '/' + x[1] + '/' + x[0]; }

  /* ---------- ficha del trato ---------- */
  function ficha() {
    var t = terms, total = t.precio * t.cantidad;
    $('#md-cond').innerHTML = [
      ['Precio', 'USD ' + usd.format(t.precio) + ' / kg'],
      ['Cantidad', n0.format(t.cantidad) + ' kg'],
      ['Condición de entrega', t.incoterm + (t.incoterm === 'FOB' ? ' puerto de Buenos Aires' : '')],
      ['Forma de pago', t.pago],
      ['Fecha de entrega', fecha(t.entrega)],
      ['Total de la operación', 'USD ' + usd.format(total), 'tot']
    ].map(function (r) { return '<div' + (r[2] ? ' class="' + r[2] + '"' : '') + '><dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd></div>'; }).join('');
    $('#md-gastos').innerHTML = gastos(t).map(function (g) {
      return '<div><dt>' + g[0] + '<small>' + g[1] + '</small></dt><dd class="' + (g[2] === 'Vendedor' ? 'v' : 'c') + '">' + g[2] + '</dd></div>';
    }).join('');
    $('#md-nhist').textContent = hist.length;
    $('#md-hist').innerHTML = hist.map(function (h) {
      return '<li><b>' + h.de + '</b> · USD ' + usd.format(h.t.precio) + '/kg · ' + n0.format(h.t.cantidad) + ' kg · ' + h.t.incoterm + ' · ' + esc(h.t.pago) + ' <em>Congelada</em></li>';
    }).join('');
    var lbl = { oferta: 'Oferta del ' + quien, rechazada: 'Oferta rechazada', medio: 'Aceptada por el ' + turno2(), acuerdo: 'Pre-acuerdo', deposito: 'Depósito en garantía', cierre: 'Operación cerrada' };
    $('#md-estado').textContent = lbl[estado];
    $('#md-estado').className = 'md-estado e-' + estado;
    acciones();
    progreso();
  }
  function otro(x) { return x === 'vendedor' ? 'comprador' : 'vendedor'; }
  function turno2() { return turno; }

  function progreso() {
    Array.prototype.forEach.call(document.querySelectorAll('#md-prog li'), function (li, i) {
      li.className = i < etapa ? 'hecho' : i === etapa ? 'actual' : '';
    });
  }

  /* ---------- acciones según el estado ---------- */
  function acciones() {
    var a = $('#md-acc');
    if (estado === 'oferta') {
      a.innerHTML = '<p>Responde el <b>' + turno + '</b>:</p><div class="md-btns"><button class="ok" data-a="aceptar">Aceptar términos</button><button data-a="contra">Contraofertar</button><button class="no" data-a="rechazar">Rechazar</button></div>';
    } else if (estado === 'rechazada') {
      a.innerHTML = '<p>El ' + quien + ' puede hacer una nueva oferta.</p><div class="md-btns"><button data-a="nueva">Hacer nueva oferta</button></div>';
    } else if (estado === 'medio') {
      a.innerHTML = '<p>Falta que el <b>' + quien + '</b> confirme los mismos términos.</p><div class="md-btns"><button class="ok" data-a="confirmar">Aceptar términos (' + quien + ')</button></div>';
    } else if (estado === 'acuerdo') {
      a.innerHTML = '<div class="md-hoja"><b>Hoja de condiciones generada</b><span>La mesa quedó cerrada a nuevas ofertas.</span></div><div class="md-btns"><button class="ok" data-a="deposito">Dejar depósito en garantía (USD ' + usd.format(terms.precio * terms.cantidad * 0.05) + ')</button></div>';
    } else if (estado === 'deposito') {
      a.innerHTML = '<div class="md-hoja"><b>Depósito congelado como reserva</b><span>Se libera al vendedor cuando se confirma el embarque.</span></div><div class="md-btns"><button class="ok" data-a="cerrar">Confirmar cierre</button></div>';
    } else {
      a.innerHTML = '<div class="md-hoja ok"><b>¡Operación cerrada!</b><span>Así termina una negociación en la mesa.</span></div><div class="md-btns"><button data-a="reiniciar">Volver a empezar</button></div>';
    }
  }

  function form() {
    var o = function (arr, v) { return arr.map(function (x) { return '<option' + (x === v ? ' selected' : '') + '>' + esc(x) + '</option>'; }).join(''); };
    $('#md-acc').innerHTML = '<form class="md-contra" id="md-contra"><p>Contraoferta del <b>' + turno + '</b>. Los términos actuales quedan congelados.</p>' +
      '<label>Precio (USD/kg)<input name="precio" type="number" step="0.01" min="0" value="' + terms.precio + '"></label>' +
      '<label>Cantidad (kg)<input name="cantidad" type="number" step="500" min="0" value="' + terms.cantidad + '"></label>' +
      '<label>Condición de entrega<select name="incoterm">' + o(INCOTERMS, terms.incoterm) + '</select></label>' +
      '<label>Forma de pago<select name="pago">' + o(PAGOS, terms.pago) + '</select></label>' +
      '<label>Fecha de entrega<input name="entrega" type="date" value="' + terms.entrega + '"></label>' +
      '<div class="md-btns"><button class="ok" type="submit">Enviar contraoferta</button><button type="button" data-a="cancelar">Cancelar</button></div></form>';
    $('#md-contra').addEventListener('submit', function (e) {
      e.preventDefault();
      var f = new FormData(e.target);
      hist.unshift({ de: quien.charAt(0).toUpperCase() + quien.slice(1), t: terms });
      terms = { precio: +f.get('precio') || terms.precio, cantidad: +f.get('cantidad') || terms.cantidad, incoterm: f.get('incoterm'), pago: f.get('pago'), entrega: f.get('entrega') || terms.entrega };
      quien = turno; turno = otro(turno); estado = 'oferta';
      sistema('El ' + quien + ' envió una contraoferta: USD ' + usd.format(terms.precio) + '/kg, ' + n0.format(terms.cantidad) + ' kg, ' + terms.incoterm + '.');
      ficha();
    });
  }

  $('#md-acc').addEventListener('click', function (e) {
    var x = e.target.closest('[data-a]'); if (!x) return;
    var a = x.dataset.a;
    if (a === 'aceptar') { estado = 'medio'; sistema('El ' + turno + ' aceptó los términos.'); }
    else if (a === 'confirmar') { estado = 'acuerdo'; etapa = 1; sistema('Las dos partes aceptaron. Se generó la hoja de condiciones.'); }
    else if (a === 'rechazar') { estado = 'rechazada'; sistema('El ' + turno + ' rechazó la oferta.'); }
    else if (a === 'nueva' || a === 'contra') { if (a === 'nueva') { turno = quien; } return form(); }
    else if (a === 'deposito') { estado = 'deposito'; etapa = 2; sistema('El comprador dejó el depósito en garantía.'); }
    else if (a === 'cerrar') { estado = 'cierre'; etapa = 3; sistema('Operación cerrada.'); }
    else if (a === 'reiniciar') { location.reload(); return; }
    ficha();
  });

  /* ---------- chat ---------- */
  var msgs = $('#md-msgs');
  function msg(de, txt) {
    var d = document.createElement('div');
    d.className = 'md-msg ' + de;
    d.innerHTML = (de !== 'sis' ? '<small>' + (de === 'c' ? 'Comprador' : 'Vendedor') + '</small>' : '') + esc(txt);
    msgs.appendChild(d); msgs.scrollTop = msgs.scrollHeight;
  }
  function sistema(t) { msg('sis', t); }
  var RESP = {
    '¿El precio es FOB o CIF?': 'Es FOB puerto de Buenos Aires. Si preferís CIF, cambialo en la ficha y lo cotizo.',
    '¿Pueden enviar una muestra?': 'Sí, enviamos 2 kg de muestra por courier en 5 días hábiles.',
    '¿Qué certificados tienen?': 'Certificado de origen, análisis bromatológico y registro sanitario. Ya están subidos y verificados.',
    '¿Cuál es el plazo de entrega?': 'Unos 30 días desde la confirmación hasta el embarque.',
    '¿Aceptan carta de crédito?': 'Sí, podemos trabajar con carta de crédito irrevocable.'
  };
  $('#md-sug').innerHTML = Object.keys(RESP).map(function (k) { return '<button type="button">' + esc(k) + '</button>'; }).join('');
  $('#md-sug').addEventListener('click', function (e) {
    var x = e.target.closest('button'); if (!x) return;
    preguntar(x.textContent);
  });
  function preguntar(t) {
    msg('c', t);
    setTimeout(function () { msg('v', RESP[t] || 'Gracias, lo reviso y lo ajustamos en la ficha del trato.'); }, 600);
  }
  $('#md-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var v = $('#md-txt').value.trim(); if (!v) return;
    $('#md-txt').value = ''; preguntar(v);
  });

  sistema('El comprador abrió la mesa con una oferta formal' + (b && b.vol ? ' (volumen buscado: ' + b.vol + ')' : '') + '.');
  msg('c', 'Hola, nos interesa para importar a ' + destino + '. Dejé la oferta en la ficha.');
  msg('v', '¡Gracias! La reviso y te respondo por la ficha.');
  ficha();
})();
