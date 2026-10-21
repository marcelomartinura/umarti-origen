/* Recursos digitales: conversor de monedas, calculadoras y tabla de talles */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var nf = function (d) { return new Intl.NumberFormat('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }); };
  var n0 = nf(0), n2 = nf(2);
  function num(id) { var v = parseFloat(($('#' + id) || {}).value); return isFinite(v) ? v : 0; }
  function plata(v, dec) { if (!isFinite(v)) return '—'; return (dec === 0 ? n0 : dec > 2 ? nf(dec) : n2).format(v); }
  function pct(v) { return isFinite(v) ? nf(1).format(v * 100) + '%' : '—'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function on(ids, fn) { ids.forEach(function (id) { var e = $('#' + id); if (e) { e.addEventListener('input', fn); e.addEventListener('change', fn); } }); }
  function kv(rows) { return '<dl class="kv">' + rows.map(function (r) { return '<div' + (r[2] ? ' class="' + r[2] + '"' : '') + '><dt>' + r[0] + '</dt><dd>' + r[1] + '</dd></div>'; }).join('') + '</dl>'; }

  /* ---------- pestañas ---------- */
  $$('.tabs-tool').forEach(function (tabs) {
    var btns = $$('[data-tab]', tabs);
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        btns.forEach(function (x) { x.setAttribute('aria-selected', String(x === b)); });
        var cont = tabs.parentNode;
        $$('[data-panel]', cont).forEach(function (p) { p.hidden = p.dataset.panel !== b.dataset.tab; });
        document.dispatchEvent(new CustomEvent('tab', { detail: b.dataset.tab }));
      });
    });
  });

  /* ---------- 1. Conversor de monedas ---------- */
  if ($('[data-tool="monedas"]')) (function () {
    var usd = null, dolar = {}, casa = 'oficial', act = { er: null, ar: null };
    var NOMBRES = { oficial: 'Oficial', bolsa: 'MEP', blue: 'Blue', tarjeta: 'Tarjeta', contadoconliqui: 'Contado con liquidación', mayorista: 'Mayorista', cripto: 'Cripto' };
    var de = $('#cv-de'), a = $('#cv-a');
    de.value = 'ARS'; a.value = 'MXN';
    function porUSD(c) {
      if (c === 'USD') return 1;
      if (c === 'ARS' && dolar[casa] && dolar[casa].venta) return dolar[casa].venta;
      return usd && usd[c];
    }
    function calc() {
      var tieneArs = de.value === 'ARS' || a.value === 'ARS';
      $('#cv-ars').hidden = !tieneArs || !Object.keys(dolar).length;
      var x = porUSD(de.value), y = porUSD(a.value), m = num('cv-monto');
      if (!x || !y) { if (usd) $('#cv-out').textContent = 'No hay cotización disponible para esa moneda.'; return; }
      var r = m / x * y;
      $('#cv-out').innerHTML = '<span class="from">' + plata(m, 2) + ' ' + de.value + ' =</span><b>' + plata(r, r >= 1000 ? 0 : 2) + ' ' + a.value + '</b>';
      var uno = y / x;
      var meta = '1 ' + de.value + ' = ' + plata(uno, uno < 0.01 ? 6 : uno < 1 ? 4 : 2) + ' ' + a.value;
      if (tieneArs && dolar[casa]) meta += ' · con dólar ' + NOMBRES[casa].toLowerCase() + ' a $ ' + plata(dolar[casa].venta, 2);
      var fechas = [act.ar && tieneArs ? 'dólar en Argentina ' + act.ar : '', act.er ? 'resto de las monedas ' + act.er : ''].filter(Boolean);
      $('#cv-meta').textContent = meta + (fechas.length ? '. Actualizado: ' + fechas.join(' · ') + '.' : '');
    }
    function hora(d) { return d.toLocaleString('es-AR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }); }
    on(['cv-monto', 'cv-de', 'cv-a'], calc);
    $('#cv-swap').addEventListener('click', function () { var t = de.value; de.value = a.value; a.value = t; calc(); });
    $$('[data-casa]').forEach(function (b) { b.addEventListener('click', function () { casa = b.dataset.casa; $$('[data-casa]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); }); calc(); }); });

    var p1 = fetch('https://open.er-api.com/v6/latest/USD').then(function (r) { return r.json(); }).then(function (j) {
      if (j.result !== 'success') throw new Error('sin datos');
      usd = j.rates; act.er = hora(new Date(j.time_last_update_unix * 1000));
      var filas = ['ARS', 'MXN', 'EUR', 'BRL', 'CLP', 'UYU', 'COP', 'PEN', 'CAD', 'GBP', 'CNY'].map(function (c) {
        var u = usd[c], m = usd.MXN; if (!u) return '';
        return '<tr><td><b>' + c + '</b></td><td>' + plata(u, u < 10 ? 4 : 2) + '</td><td>' + plata(u / m, u / m < 10 ? 4 : 2) + '</td></tr>';
      }).join('');
      $('#cv-tabla-mx tbody').innerHTML = filas;
    }).catch(function () { $('#cv-tabla-mx tbody').innerHTML = '<tr><td colspan="3">No se pudieron cargar las cotizaciones. Probá de nuevo en un rato.</td></tr>'; });

    var p2 = fetch('https://dolarapi.com/v1/dolares').then(function (r) { return r.json(); }).then(function (lista) {
      var ultima = 0;
      lista.forEach(function (x) { dolar[x.casa] = x; var t = Date.parse(x.fechaActualizacion); if (t > ultima) ultima = t; });
      if (ultima) act.ar = hora(new Date(ultima));
      var orden = ['oficial', 'bolsa', 'blue', 'tarjeta', 'contadoconliqui', 'mayorista', 'cripto'];
      $('#cv-tabla-ar tbody').innerHTML = orden.filter(function (k) { return dolar[k]; }).map(function (k) {
        var x = dolar[k];
        return '<tr><td><b>' + (NOMBRES[k] || x.nombre) + '</b></td><td>' + (x.compra ? '$ ' + plata(x.compra, 2) : '—') + '</td><td>$ ' + plata(x.venta, 2) + '</td></tr>';
      }).join('');
    }).catch(function () { $('#cv-tabla-ar tbody').innerHTML = '<tr><td colspan="3">No se pudo cargar el dólar en Argentina. Se usa la cotización oficial internacional.</td></tr>'; });

    Promise.all([p1.catch(function () {}), p2.catch(function () {})]).then(function () {
      if (!usd && !Object.keys(dolar).length) { $('#cv-out').textContent = 'No se pudieron cargar las cotizaciones. Revisá tu conexión y recargá la página.'; return; }
      calc();
    });
  })();

  /* ---------- 2a. Factoraje ---------- */
  if ($('[data-tool="factoraje"]')) (function () {
    function calc() {
      var monto = num('fa-monto'), dias = num('fa-dias');
      $('#fa-dias-v').textContent = dias + ' días';
      var of = ['a', 'b'].map(function (k) {
        var ant = num('fa-' + k + '-ant') / 100, tasa = num('fa-' + k + '-tasa') / 100;
        var anticipo = monto * ant, costo = anticipo * tasa * dias / 30;
        return { k: k.toUpperCase(), ant: ant, tasa: tasa, anticipo: anticipo, costo: costo, neto: anticipo - costo, resto: monto - anticipo, anual: tasa * 12 };
      });
      var mejor = of[0].costo <= of[1].costo ? 0 : 1;
      $('#fa-out').innerHTML = '<div class="cmp">' + of.map(function (o, i) {
        return '<div class="cmp-col' + (i === mejor ? ' win' : '') + '">' + (i === mejor ? '<span class="win-badge">Menor costo</span>' : '') +
          '<h3>Oferta ' + o.k + '</h3>' + kv([
            ['Te adelantan (' + pct(o.ant).replace(',0', '') + ')', plata(o.anticipo, 2)],
            ['Costo del factoraje', plata(o.costo, 2), 'neg'],
            ['Recibís hoy', plata(o.neto, 2), 'big'],
            ['Cobrás al vencimiento', plata(o.resto, 2)],
            ['Costo sobre la factura', pct(monto ? o.costo / monto : 0)],
            ['Tasa anual equivalente', pct(o.anual)]
          ]) + '</div>';
      }).join('') + '</div>' +
        '<p class="res-note">Ahorro con la oferta ' + of[mejor].k + ': <b>' + plata(Math.abs(of[0].costo - of[1].costo), 2) + '</b> por factura. Con una factura así por mes, son <b>' + plata(Math.abs(of[0].costo - of[1].costo) * 12, 2) + '</b> al año.</p>';
    }
    on(['fa-monto', 'fa-dias', 'fa-a-ant', 'fa-a-tasa', 'fa-b-ant', 'fa-b-tasa'], calc); calc();
  })();

  /* ---------- 2b. Precio de exportación ---------- */
  if ($('[data-tool="precio-export"]')) (function () {
    function calc() {
      var cant = Math.max(1, num('pe-cant')), base = num('pe-costo') * cant + num('pe-emb');
      var ganancia = base * num('pe-margen') / 100;
      var exw = base + ganancia;
      var fobSin = exw + num('pe-flete-int') + num('pe-desp');
      var dex = num('pe-dex') / 100, fob = dex < 1 ? fobSin / (1 - dex) : NaN;
      var cfr = fob + num('pe-flete');
      var s = num('pe-seg') / 100, cif = s < 1 ? cfr / (1 - s) : NaN;
      var filas = [
        ['EXW', 'En tu depósito', exw], ['FOB', 'Cargado en el puerto de salida', fob],
        ['CFR', 'Con flete hasta el puerto de destino', cfr], ['CIF', 'Con flete y seguro hasta destino', cif]];
      var max = cif || 1;
      $('#pe-out').innerHTML = '<table class="tbl res"><thead><tr><th>Incoterm</th><th>Total</th><th>Por unidad</th></tr></thead><tbody>' +
        filas.map(function (f) { return '<tr><td><b>' + f[0] + '</b><small>' + f[1] + '</small><span class="bar" style="width:' + Math.max(4, f[2] / max * 100) + '%"></span></td><td>' + plata(f[2], 2) + '</td><td>' + plata(f[2] / cant, 2) + '</td></tr>'; }).join('') +
        '</tbody></table>' + kv([
          ['Tu ganancia', plata(ganancia, 2), 'big'],
          ['Derechos de exportación', plata(fob - fobSin, 2)],
          ['Seguro de carga', plata(cif - cfr, 2)]]) +
        '<p class="res-note">Cotizá FOB si el comprador contrata el flete, y CIF si lo contratás vos. En la nota de Incoterms está la diferencia en detalle.</p>';
    }
    on(['pe-costo', 'pe-cant', 'pe-margen', 'pe-emb', 'pe-flete-int', 'pe-desp', 'pe-dex', 'pe-flete', 'pe-seg'], calc); calc();
  })();

  /* ---------- 2c. Precio puesto en destino ---------- */
  if ($('[data-tool="destino"]')) (function () {
    $('#pd-pais').addEventListener('change', function () { if (this.value !== '') $('#pd-iva').value = this.value; calc(); });
    function calc() {
      var cif = num('pd-cif'), cant = Math.max(1, num('pd-cant'));
      var arancel = cif * num('pd-arancel') / 100, otros = cif * num('pd-otros') / 100;
      var iva = (cif + arancel + otros) * num('pd-iva') / 100, gastos = num('pd-gastos');
      var total = cif + arancel + otros + iva + gastos;
      var partes = [['Mercadería (CIF)', cif, 'c1'], ['Arancel', arancel, 'c2'], ['Otros cargos aduaneros', otros, 'c3'], ['IVA de importación', iva, 'c4'], ['Despachante y gastos locales', gastos, 'c5']];
      $('#pd-out').innerHTML = '<div class="stack">' + partes.map(function (p) { return '<span class="' + p[2] + '" style="flex:' + Math.max(p[1], 0) + '" title="' + p[0] + '"></span>'; }).join('') + '</div>' +
        kv(partes.map(function (p) { return ['<i class="dot ' + p[2] + '"></i>' + p[0], plata(p[1], 2)]; }).concat([
          ['Costo total puesto en destino', plata(total, 2), 'big'],
          ['Por unidad', plata(total / cant, 2)],
          ['Por unidad sin IVA (si el comprador lo recupera)', plata((total - iva) / cant, 2)],
          ['Sobrecosto sobre el CIF', pct(cif ? (total - cif) / cif : 0)]]));
    }
    on(['pd-cif', 'pd-cant', 'pd-arancel', 'pd-iva', 'pd-otros', 'pd-gastos'], calc); calc();
  })();

  /* ---------- 3. Calculadora de carga ---------- */
  if ($('[data-tool="carga"]')) (function () {
    var UNIDADES = [
      ['Pallet americano', '120 × 100 cm, hasta 145 cm de carga', [120, 100, 145], 1000],
      ['Pallet europeo', '120 × 80 cm, hasta 145 cm de carga', [120, 80, 145], 1000],
      ['Contenedor 20 pies', '589 × 235 × 239 cm · 33 m³', [589, 235, 239], 28000],
      ['Contenedor 40 pies', '1203 × 235 × 239 cm · 67 m³', [1203, 235, 239], 26500],
      ['Contenedor 40 High Cube', '1203 × 235 × 269 cm · 76 m³', [1203, 235, 269], 26500]];
    function cuantas(esp, caja, girar) {
      var l = caja[0], a = caja[1], h = caja[2];
      var ori = girar ? [[l, a, h], [a, l, h], [l, h, a], [h, l, a], [a, h, l], [h, a, l]] : [[l, a, h], [a, l, h]];
      return ori.reduce(function (m, o) { return Math.max(m, Math.floor(esp[0] / o[0]) * Math.floor(esp[1] / o[1]) * Math.floor(esp[2] / o[2])); }, 0);
    }
    function calc() {
      var l = num('cg-l'), a = num('cg-a'), h = num('cg-h'), p = num('cg-p'), n = Math.max(1, Math.round(num('cg-n'))), girar = $('#cg-rot').checked;
      var vol = l * a * h / 1e6, aereo = l * a * h / 6000, courier = l * a * h / 5000;
      var factA = Math.max(p, aereo), factC = Math.max(p, courier);
      var wm = Math.max(vol * n, p * n / 1000);
      $('#cg-out').innerHTML = kv([
        ['Volumen total', plata(vol * n, 3) + ' m³'],
        ['Peso real total', plata(p * n, 1) + ' kg'],
        ['Peso volumétrico aéreo (÷ 6000)', plata(aereo * n, 1) + ' kg'],
        ['Peso volumétrico paquetería (÷ 5000)', plata(courier * n, 1) + ' kg'],
        ['Te cobran en avión', plata(factA * n, 1) + ' kg', 'big'],
        ['Te cobran en paquetería', plata(factC * n, 1) + ' kg', 'big'],
        ['Marítimo consolidado (por m³ o tonelada)', plata(wm, 2) + ' unidades de flete']]) +
        '<p class="res-note">' + (aereo > p ? 'Tu caja paga por volumen: con una caja más chica o mejor llena, el flete aéreo baja.' : 'Tu caja paga por peso real: el tamaño está bien aprovechado.') + '</p>';
      $('#cg-tabla tbody').innerHTML = UNIDADES.map(function (u) {
        var porVol = cuantas(u[2], [l, a, h], girar), porPeso = p > 0 ? Math.floor(u[3] / p) : Infinity, entran = Math.min(porVol, porPeso);
        var nec = entran > 0 ? Math.ceil(n / entran) : 0, ocup = entran > 0 ? Math.min(1, n / (nec * entran)) : 0;
        return '<tr><td><b>' + u[0] + '</b></td><td>' + u[1] + '</td><td>' + n0.format(porVol) + '</td><td>' + (isFinite(porPeso) ? n0.format(porPeso) + ' <small>(máx. ' + n0.format(u[3]) + ' kg)</small>' : '—') + '</td><td><b>' + n0.format(entran) + '</b></td><td>' +
          (entran ? 'Necesitás <b>' + nec + '</b> · ocupación ' + pct(ocup) : 'No entra') + '</td></tr>';
      }).join('');
    }
    on(['cg-l', 'cg-a', 'cg-h', 'cg-p', 'cg-n', 'cg-rot'], calc); calc();
  })();

  /* ---------- 4. Precio y margen ---------- */
  if ($('[data-tool="margen"]')) (function () {
    var modo = 'gano';
    document.addEventListener('tab', function (e) {
      modo = e.detail;
      $$('[data-modo]').forEach(function (x) { x.hidden = x.dataset.modo !== modo; });
      calc();
    });
    function calc() {
      var r = num('mg-pais') / 100, costo = num('mg-costo'), c = num('mg-com') / 100;
      var fijos = num('mg-fijo') + num('mg-envio') + num('mg-otros');
      var P;
      if (modo === 'pongo') {
        var m = num('mg-objetivo') / 100, den = (1 - m) / (1 + r) - c;
        if (den <= 0) { $('#mg-out').innerHTML = '<p class="res-alert">Con esa comisión no se puede llegar a esa ganancia. Bajá el porcentaje que querés ganar o buscá una comisión menor.</p>'; return; }
        P = (costo + fijos) / den;
      } else P = num('mg-precio');
      var neto = P / (1 + r), iva = P - neto, com = P * c, gan = neto - com - fijos - costo;
      var partes = [['Costo del producto', costo, 'c1'], ['Comisión', com, 'c2'], ['Envío, cargo fijo y otros', fijos, 'c3'], ['IVA', iva, 'c4'], [gan >= 0 ? 'Tu ganancia' : 'Pérdida', Math.abs(gan), gan >= 0 ? 'c5' : 'cneg']];
      $('#mg-out').innerHTML = (modo === 'pongo' ? '<div class="res-hero"><small>Precio de venta sugerido</small><b>$ ' + plata(Math.ceil(P), 0) + '</b><span>con IVA, redondeado hacia arriba</span></div>' :
        '<div class="res-hero' + (gan < 0 ? ' neg' : '') + '"><small>' + (gan >= 0 ? 'Ganás por cada venta' : 'Perdés por cada venta') + '</small><b>$ ' + plata(Math.abs(gan), 2) + '</b><span>margen ' + pct(neto ? gan / neto : 0) + ' · markup ' + pct(costo ? gan / costo : 0) + '</span></div>') +
        '<div class="stack">' + partes.map(function (p) { return '<span class="' + p[2] + '" style="flex:' + Math.max(p[1], 0) + '" title="' + p[0] + '"></span>'; }).join('') + '</div>' +
        kv(partes.map(function (p) { return ['<i class="dot ' + p[2] + '"></i>' + p[0], '$ ' + plata(p[1], 2) + ' <small>' + pct(P ? p[1] / P : 0) + '</small>']; }).concat([
          ['Precio al público', '$ ' + plata(P, 2), 'big'],
          ['Precio sin IVA', '$ ' + plata(neto, 2)]]));
    }
    on(['mg-pais', 'mg-costo', 'mg-precio', 'mg-objetivo', 'mg-com', 'mg-fijo', 'mg-envio', 'mg-otros'], calc); calc();
  })();

  /* ---------- 5. Talles: buscador por largo del pie ---------- */
  if ($('[data-tool="pie"]')) (function () {
    var sexo = 'm';
    $$('[data-pie]').forEach(function (b) { b.addEventListener('click', function () { sexo = b.dataset.pie; $$('[data-pie]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); }); calc(); }); });
    function calc() {
      var cm = num('tl-cm'), filas = window.TALLES_PIE[sexo];
      var mejor = filas.reduce(function (m, f) { return Math.abs(parseFloat(f[0]) - cm) < Math.abs(parseFloat(m[0]) - cm) ? f : m; }, filas[0]);
      var fuera = cm < parseFloat(filas[0][0]) - 0.5 || cm > parseFloat(filas[filas.length - 1][0]) + 0.5;
      $('#tl-out').innerHTML = fuera ? '<p class="res-alert">Ese largo queda fuera de la tabla. Revisá la medida o consultá la tabla del vendedor.</p>' :
        '<div class="sizes">' + [['Argentina', mejor[4]], ['México', mejor[1]], ['Estados Unidos', mejor[2]], ['Europa', mejor[3]]].map(function (s) { return '<div><small>' + s[0] + '</small><b>' + esc(s[1]) + '</b></div>'; }).join('') + '</div>' +
          '<p class="res-note">Para un pie de ' + plata(cm, 1) + ' cm. Si quedás entre dos números, elegí el más grande.</p>';
      var panel = sexo === 'm' ? 'cm' : 'ch';
      $$('[data-panel="' + panel + '"] tbody tr').forEach(function (tr) { tr.classList.toggle('on', !fuera && tr.firstChild.textContent === String(mejor[0])); });
    }
    on(['tl-cm'], calc); calc();
  })();
})();
