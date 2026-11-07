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

  /* ---------- 6. Nomenclatura dental ---------- */
  if ($('[data-tool="dental"]')) (function () {
    var NOM_P = ['', 'Incisivo central', 'Incisivo lateral', 'Canino', 'Primer premolar', 'Segundo premolar', 'Primer molar', 'Segundo molar', 'Tercer molar'];
    var NOM_T = ['', 'Incisivo central', 'Incisivo lateral', 'Canino', 'Primer molar', 'Segundo molar'];
    var LADO = { 1: ['superior', 'derecho'], 2: ['superior', 'izquierdo'], 3: ['inferior', 'izquierdo'], 4: ['inferior', 'derecho'] };
    var PAL = { 1: function (x) { return x + '┘'; }, 2: function (x) { return '└' + x; }, 3: function (x) { return '┌' + x; }, 4: function (x) { return x + '┐'; } };
    var LET = 'ABCDEFGHIJKLMNOPQRST';
    function info(fdi) {
      var q = Math.floor(fdi / 10), n = fdi % 10, temp = q > 4, qb = temp ? q - 4 : q;
      var max = temp ? 5 : 8, uni;
      var idx = qb === 1 ? max - n : qb === 2 ? max + n - 1 : qb === 3 ? 3 * max - n : 3 * max + n - 1;
      uni = temp ? LET[idx] : String(idx + 1);
      var nom = (temp ? NOM_T : NOM_P)[n] + ' ' + LADO[qb][0] + ' ' + LADO[qb][1];
      return { fdi: String(fdi), uni: uni, pal: PAL[qb](temp ? 'ABCDE'[n - 1] : n), nom: nom, temp: temp, q: q, arc: LADO[qb][0], lado: LADO[qb][1] };
    }
    function lista(temp) {
      var max = temp ? 5 : 8, b = temp ? 4 : 0, sup = [], inf = [];
      for (var i = max; i >= 1; i--) sup.push((1 + b) * 10 + i);
      for (i = 1; i <= max; i++) sup.push((2 + b) * 10 + i);
      for (i = max; i >= 1; i--) inf.push((4 + b) * 10 + i);
      for (i = 1; i <= max; i++) inf.push((3 + b) * 10 + i);
      return [sup, inf];
    }
    var dent = 'p', sel = null, od = $('#dn-odonto'), out = $('#dn-out');
    function tipo(n) { n = n % 10; return dent === 't' ? (n <= 2 ? 'inc' : n === 3 ? 'can' : 'mol') : (n <= 2 ? 'inc' : n === 3 ? 'can' : n <= 5 ? 'pre' : 'mol'); }
    function dibujar() {
      var f = lista(dent === 't');
      od.innerHTML = f.map(function (fila, k) {
        return '<div class="od-fila ' + (k ? 'inf' : 'sup') + '"><span class="od-lbl">' + (k ? 'Inferior' : 'Superior') + '</span><div class="od-dientes">' + fila.map(function (x, i) {
          return (i === fila.length / 2 ? '<span class="od-medio"></span>' : '') + '<button type="button" class="od-d ' + tipo(x) + (x === sel ? ' on' : '') + '" data-fdi="' + x + '" title="' + esc(info(x).nom) + '"><i></i><span>' + x + '</span></button>';
        }).join('') + '</div></div>';
      }).join('') + '<div class="od-lados"><span>Derecha del paciente</span><span>Izquierda del paciente</span></div>';
    }
    function mostrar() {
      if (!sel) { out.innerHTML = '<p class="res-note">Elegí un diente para ver sus equivalencias.</p>'; return; }
      var d = info(sel);
      out.innerHTML = '<div class="res-hero"><small>' + (d.temp ? 'Diente temporal' : 'Diente permanente') + '</small><b style="font-size:1.6rem">' + esc(d.nom) + '</b></div>' +
        '<div class="dn-cods"><div><small>FDI</small><b>' + d.fdi + '</b></div><div><small>Universal</small><b>' + d.uni + '</b></div><div><small>Palmer</small><b>' + d.pal + '</b></div></div>' +
        kv([['Arcada', d.arc], ['Lado del paciente', d.lado], ['Cuadrante FDI', String(d.q)]]);
    }
    function elegir(fdi) { sel = fdi; dibujar(); mostrar(); }
    od.addEventListener('click', function (e) { var b = e.target.closest('[data-fdi]'); if (b) elegir(+b.dataset.fdi); });
    $$('[data-dent]').forEach(function (b) {
      b.addEventListener('click', function () {
        dent = b.dataset.dent; sel = null;
        $$('[data-dent]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        dibujar(); mostrar();
      });
    });
    $('#dn-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var v = ($('#dn-in').value || '').trim().toUpperCase(), sis = $('#dn-sis').value, fdi = null;
      var todos = lista(false)[0].concat(lista(false)[1], lista(true)[0], lista(true)[1]);
      todos.forEach(function (x) { var d = info(x); if ((sis === 'fdi' && d.fdi === v) || (sis === 'uni' && d.uni === v)) fdi = x; });
      if (!fdi) { out.innerHTML = '<div class="res-alert">No encontramos "' + esc(v) + '" en el sistema ' + (sis === 'fdi' ? 'FDI' : 'Universal') + '. Probá con un número válido: FDI 11 a 48 o 51 a 85; Universal 1 a 32 o A a T.</div>'; return; }
      var temp = info(fdi).temp;
      if ((dent === 't') !== temp) { dent = temp ? 't' : 'p'; $$('[data-dent]').forEach(function (x) { x.setAttribute('aria-pressed', String(x.dataset.dent === dent)); }); }
      elegir(fdi);
    });
    function tabla(temp) {
      var f = lista(temp), xs = f[0].slice(0, f[0].length / 2).concat(f[0].slice(f[0].length / 2), f[1].slice(f[1].length / 2), f[1].slice(0, f[1].length / 2));
      xs.sort(function (a, b) { return a - b; });
      return '<table class="tbl"><thead><tr><th>Diente</th><th>FDI</th><th>Universal</th><th>Palmer</th></tr></thead><tbody>' + xs.map(function (x) { var d = info(x); return '<tr><td>' + esc(d.nom) + '</td><td>' + d.fdi + '</td><td>' + d.uni + '</td><td>' + d.pal + '</td></tr>'; }).join('') + '</tbody></table>';
    }
    $('#dn-tp').innerHTML = tabla(false); $('#dn-tt').innerHTML = tabla(true);
    dibujar(); mostrar();
  })();

  /* ---------- 7. Diferencia horaria ---------- */
  if ($('[data-tool="horario"]')) (function () {
    var de = $('#hz-de'), a = $('#hz-a'), local = Intl.DateTimeFormat().resolvedOptions().timeZone;
    var q = new URLSearchParams(location.search);
    a.value = q.get('a') && a.querySelector('option[value="' + q.get('a') + '"]') ? q.get('a') : 'America/Argentina/Buenos_Aires';
    if (q.get('de') && de.querySelector('option[value="' + q.get('de') + '"]')) de.value = q.get('de');
    function zona(sel) { return sel.value || local; }
    function nombre(sel) { return sel.value ? sel.options[sel.selectedIndex].text.split(',')[0] : 'Donde estás'; }
    function offset(tz, d) {
      var p = new Intl.DateTimeFormat('en-US', { timeZone: tz, hourCycle: 'h23', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric' }).formatToParts(d);
      var o = {}; p.forEach(function (x) { o[x.type] = +x.value; });
      return (Date.UTC(o.year, o.month - 1, o.day, o.hour, o.minute) - Math.floor(d.getTime() / 60000) * 60000) / 60000;
    }
    function hora(tz, d) { return new Intl.DateTimeFormat('es-AR', { timeZone: tz, hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).format(d); }
    function dia(tz, d) { return new Intl.DateTimeFormat('es-AR', { timeZone: tz, weekday: 'long', day: 'numeric', month: 'long' }).format(d); }
    function fmtDif(m) {
      var h = Math.floor(Math.abs(m) / 60), mm = Math.abs(m) % 60;
      return h + (h === 1 ? ' hora' : ' horas') + (mm ? ' y ' + mm + ' minutos' : '');
    }
    function pintar() {
      var now = new Date(), z1 = zona(de), z2 = zona(a);
      $('#hz-r1').innerHTML = '<b>' + hora(z1, now) + '</b><span>' + esc(dia(z1, now)) + '</span><small>' + esc(de.value ? nombre(de) : 'Tu zona: ' + local.replace(/_/g, ' ')) + '</small>';
      $('#hz-r2').innerHTML = '<b>' + hora(z2, now) + '</b><span>' + esc(dia(z2, now)) + '</span><small>' + esc((q.get('n') && a.value === q.get('a')) ? q.get('n') : nombre(a)) + '</small>';
      var dif = offset(z2, now) - offset(z1, now), dest = (q.get('n') && a.value === q.get('a')) ? q.get('n') : nombre(a);
      $('#hz-dif').innerHTML = dif === 0 ? '<b>Tienen la misma hora.</b>' : '<b>' + esc(dest) + ' está ' + fmtDif(dif) + (dif > 0 ? ' adelante' : ' atrás') + '</b><span>' + (dif > 0 ? 'Allá ya es más tarde que donde estás.' : 'Allá todavía es más temprano que donde estás.') + '</span>';
      var filas = '<thead><tr><th>' + esc(dest) + '</th><th>' + esc(de.value ? nombre(de) : 'Donde estás') + '</th></tr></thead><tbody>';
      [7, 9, 12, 15, 18, 21].forEach(function (h) {
        var m = ((h * 60 - dif) % 1440 + 1440) % 1440, dd = h * 60 - dif < 0 ? ' (día anterior)' : h * 60 - dif >= 1440 ? ' (día siguiente)' : '';
        filas += '<tr><td>' + String(h).padStart(2, '0') + ':00</td><td>' + String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0') + dd + '</td></tr>';
      });
      $('#hz-tabla').innerHTML = filas + '</tbody>';
    }
    de.addEventListener('change', pintar); a.addEventListener('change', pintar);
    $('#hz-swap').addEventListener('click', function () { var t = de.value; de.value = a.value; a.value = t || 'America/Argentina/Buenos_Aires'; q.delete('n'); pintar(); });
    pintar(); setInterval(pintar, 30000);
  })();

  /* ---------- 8. Conversor de unidades ---------- */
  if ($('[data-tool="unidades"]')) (function () {
    var U = {
      longitud: [['km', 'Kilómetros', 1000], ['m', 'Metros', 1], ['cm', 'Centímetros', 0.01], ['mi', 'Millas', 1609.344], ['yd', 'Yardas', 0.9144], ['ft', 'Pies', 0.3048], ['in', 'Pulgadas', 0.0254]],
      peso: [['kg', 'Kilos', 1], ['g', 'Gramos', 0.001], ['lb', 'Libras', 0.45359237], ['oz', 'Onzas', 0.028349523125], ['t', 'Toneladas', 1000]],
      volumen: [['l', 'Litros', 1], ['ml', 'Mililitros', 0.001], ['gal', 'Galones (EE. UU.)', 3.785411784], ['galuk', 'Galones (Reino Unido)', 4.54609], ['floz', 'Onzas líquidas', 0.0295735295625], ['pt', 'Pintas (Reino Unido)', 0.56826125]],
      temperatura: [['c', 'Grados Celsius'], ['f', 'Grados Fahrenheit'], ['k', 'Kelvin']],
      velocidad: [['kmh', 'Kilómetros por hora', 1], ['mph', 'Millas por hora', 1.609344], ['ms', 'Metros por segundo', 3.6], ['kn', 'Nudos', 1.852]],
      superficie: [['m2', 'Metros cuadrados', 1], ['ha', 'Hectáreas', 10000], ['km2', 'Kilómetros cuadrados', 1e6], ['ft2', 'Pies cuadrados', 0.09290304], ['ac', 'Acres', 4046.8564224]]
    };
    var DEF = { longitud: ['km', 'mi'], peso: ['kg', 'lb'], volumen: ['l', 'gal'], temperatura: ['c', 'f'], velocidad: ['kmh', 'mph'], superficie: ['m2', 'ft2'] };
    var RAP = { longitud: [['km', 'mi', [1, 5, 10, 100]], ['cm', 'in', [1, 10, 30]]], peso: [['kg', 'lb', [1, 5, 23]], ['g', 'oz', [100, 250]]], volumen: [['l', 'gal', [1, 10, 50]], ['ml', 'floz', [100, 500]]], temperatura: [['c', 'f', [-5, 0, 15, 25, 35]]], velocidad: [['kmh', 'mph', [50, 100, 120]]], superficie: [['m2', 'ft2', [1, 50, 100]]] };
    var tipo = 'longitud', de = $('#un-de'), a = $('#un-a'), v = $('#un-v');
    var fmt = function (x) { var ab = Math.abs(x); return new Intl.NumberFormat('es-AR', { maximumFractionDigits: ab >= 100 ? 1 : ab >= 1 ? 3 : 5 }).format(x); };
    function conv(x, u1, u2) {
      if (tipo === 'temperatura') { var c = u1 === 'c' ? x : u1 === 'f' ? (x - 32) * 5 / 9 : x - 273.15; return u2 === 'c' ? c : u2 === 'f' ? c * 9 / 5 + 32 : c + 273.15; }
      var f = function (k) { return U[tipo].filter(function (u) { return u[0] === k; })[0][2]; };
      return x * f(u1) / f(u2);
    }
    function nom(k) { return U[tipo].filter(function (u) { return u[0] === k; })[0][1]; }
    function cargar() {
      var o = U[tipo].map(function (u) { return '<option value="' + u[0] + '">' + u[1] + '</option>'; }).join('');
      de.innerHTML = o; a.innerHTML = o; de.value = DEF[tipo][0]; a.value = DEF[tipo][1]; calc();
    }
    function calc() {
      var x = parseFloat(v.value); if (!isFinite(x)) x = 0;
      $('#un-out').innerHTML = '<span class="from">' + fmt(x) + ' ' + esc(nom(de.value).toLowerCase()) + ' =</span><b>' + fmt(conv(x, de.value, a.value)) + '</b> <span>' + esc(nom(a.value).toLowerCase()) + '</span>';
      $('#un-tabla').innerHTML = '<tbody>' + RAP[tipo].map(function (r) { return r[2].map(function (n) { var save = [de.value, a.value]; return '<tr><td>' + fmt(n) + ' ' + esc(nom(r[0]).toLowerCase()) + '</td><td>' + fmt(conv(n, r[0], r[1])) + ' ' + esc(nom(r[1]).toLowerCase()) + '</td></tr>'; }).join(''); }).join('') + '</tbody>';
    }
    $$('[data-u]').forEach(function (b) { b.addEventListener('click', function () { tipo = b.dataset.u; $$('[data-u]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); }); cargar(); }); });
    [v, de, a].forEach(function (e) { e.addEventListener('input', calc); e.addEventListener('change', calc); });
    $('#un-swap').addEventListener('click', function () { var t = de.value; de.value = a.value; a.value = t; calc(); });
    var q = new URLSearchParams(location.search).get('tipo'); if (q && U[q]) { var bq = $('[data-u="' + q + '"]'); if (bq) { bq.click(); return; } }
    cargar();
  })();

  /* ---------- 9. Enchufes y corriente ---------- */
  if ($('[data-tool="enchufes"]')) (function () {
    var D = window.CORRIENTE, T = window.TIPOS_ENCHUFE, de = $('#en-de'), a = $('#en-a');
    var q = new URLSearchParams(location.search);
    de.value = q.get('de') && D[q.get('de')] ? q.get('de') : 'México';
    a.value = q.get('a') && D[q.get('a')] ? q.get('a') : 'Argentina';
    function grupo(v) { return v <= 130 ? 'bajo' : 'alto'; }
    function pintar() {
      var x = D[de.value], y = D[a.value];
      var comunes = y.t.filter(function (t) { return x.t.indexOf(t) >= 0; });
      var adapt = comunes.length === 0, trafo = grupo(x.v) !== grupo(y.v);
      var card = function (p, d) { return '<div class="en-pais"><small>' + esc(p) + '</small><b>' + d.v + ' V · ' + d.hz + ' Hz</b><div class="en-tipos">' + d.t.map(function (t) { return '<span title="' + esc(T[t] || '') + '">' + t + '</span>'; }).join('') + '</div></div>'; };
      var html = '<div class="en-cmp">' + card(de.value, x) + card(a.value, y) + '</div><ul class="en-res">';
      html += '<li class="' + (adapt ? 'si' : 'no') + '"><b>' + (adapt ? 'Necesitás adaptador' : comunes.length === y.t.length ? 'No necesitás adaptador' : 'Puede que necesites adaptador') + '</b><span>' +
        (adapt ? 'En ' + esc(a.value) + ' se usan enchufes tipo ' + y.t.join(', ') + ': ' + y.t.map(function (t) { return t + ': ' + esc(T[t]); }).join(' · ') + '.' :
          comunes.length === y.t.length ? 'Tus enchufes entran en los tomacorrientes de ' + esc(a.value) + '.' : 'Los tipo ' + comunes.join(', ') + ' coinciden, pero en ' + esc(a.value) + ' también hay tipo ' + y.t.filter(function (t) { return comunes.indexOf(t) < 0; }).join(', ') + '. Llevá un adaptador universal por las dudas.') + '</span></li>';
      html += '<li class="' + (trafo ? 'si' : 'no') + '"><b>' + (trafo ? 'Revisá el voltaje de tus aparatos' : 'El voltaje es compatible') + '</b><span>' +
        (trafo ? 'En ' + esc(a.value) + ' hay ' + y.v + ' V y en ' + esc(de.value) + ' ' + x.v + ' V. Los cargadores que dicen "100-240V" funcionan sin problema; los aparatos de un solo voltaje (secadores, planchitas, pavas) necesitan transformador.' : 'Los dos países tienen un voltaje parecido (' + x.v + ' V y ' + y.v + ' V): tus aparatos funcionan igual.') + '</span></li></ul>';
      $('#en-out').innerHTML = html;
    }
    de.addEventListener('change', pintar); a.addEventListener('change', pintar);
    $('#en-swap').addEventListener('click', function () { var t = de.value; de.value = a.value; a.value = t; pintar(); });
    pintar();
  })();

  /* ---------- filtro de la portada ---------- */
  var fb = $$('.rc-filtros [data-grupo]');
  fb.forEach(function (b) {
    b.addEventListener('click', function () {
      var g = b.dataset.grupo;
      fb.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      $$('section.rc-grupo').forEach(function (s) { s.hidden = !!g && s.dataset.grupo !== g; });
    });
  });
})();
