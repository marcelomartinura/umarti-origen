/* Panel · módulo Afiliados: carga rápida de productos de Amazon México, Mercado Libre y AliExpress.
   Se guardan en la tabla "productos" con tipo = 'afiliado'. En el sitio se ven mezclados en la Tienda,
   con una tarjeta más chica, y nunca dicen "afiliado". */
(function () {
  'use strict';
  var C = window.PanelComun; if (!C) return;
  var $ = C.$, $$ = C.$$, esc = C.esc, sb = C.sb, demo = C.demo, P = C.P;
  function ok(r) { if (r.error) throw r.error; return r.data; }

  var PLAT = {
    'amazon-mx': { n: 'Amazon México', pais: 'México', ar: false, intl: true, mon: 'MXN' },
    'ml-ar': { n: 'Mercado Libre Argentina', pais: 'Argentina', ar: true, intl: false, mon: 'ARS' },
    'ml-mx': { n: 'Mercado Libre México', pais: 'México', ar: false, intl: true, mon: 'MXN' },
    'aliexpress': { n: 'AliExpress', pais: 'Otro', ar: false, intl: true, mon: 'USD' }
  };
  function platDe(url) {
    var h = ''; try { h = new URL(url).hostname; } catch (e) { return ''; }
    if (/amazon\.com\.mx$|amzn\.to$|(^|\.)a\.co$|amazon\./.test(h)) return 'amazon-mx';
    if (/mercadolibre\.com\.ar$/.test(h)) return 'ml-ar';
    if (/mercadolibre\.com\.mx$/.test(h)) return 'ml-mx';
    if (/aliexpress\./.test(h)) return 'aliexpress';
    if (/meli\.la$|mercadolibre/.test(h)) return '';   // acortador de Mercado Libre: se sabe el país al leerlo
    return null;                                          // tienda no soportada
  }

  var datosDemo = [
    { id: 'a1', codigo: 'UM-0101', tipo: 'afiliado', plataforma_afiliado: 'amazon-mx', url_afiliado: 'https://amzn.to/ejemplo', nombre: 'Termo de acero inoxidable 1 L con pico cebador', categoria: 'Café, Té y Mate', subcategoria: 'Mates y bombillas', fotos: [], precio_ars: null, precio_mxn: null, precio_usd: null, tienda_ar: false, international: true, tienda_mx: false, estado: 'Publicado', orden: 0 },
    { id: 'a2', codigo: 'UM-0102', tipo: 'afiliado', plataforma_afiliado: 'ml-ar', url_afiliado: 'https://meli.la/ejemplo', nombre: 'Yerba mate orgánica 1 kg', categoria: 'Café, Té y Mate', subcategoria: 'Yerba', fotos: [], precio_ars: 9800, precio_mxn: null, precio_usd: null, tienda_ar: true, international: false, tienda_mx: false, estado: 'Borrador', orden: 0 }
  ];
  var api = demo ? {
    listar: function () { return Promise.resolve(datosDemo.map(function (x) { return Object.assign({}, x); })); },
    guardar: function (p, nuevo) {
      if (nuevo) { p.id = 'n' + Date.now() + Math.random(); p.codigo = 'UM-0' + (200 + datosDemo.length); datosDemo.push(p); }
      else datosDemo = datosDemo.map(function (x) { return x.id === p.id ? p : x; });
      return Promise.resolve(Object.assign({}, p));
    },
    borrar: function (id) { datosDemo = datosDemo.filter(function (x) { return x.id !== id; }); return Promise.resolve(); },
    sincronizar: function () { return new Promise(function (r) { setTimeout(function () { r({ ok: true, revisados: 1, precios: 1, pausados: 0, reactivados: 0, sin_leer: 0 }); }, 500); }); },
    leer: function (url) { var pl = platDe(url) || 'ml-mx'; return new Promise(function (r) { setTimeout(function () { r({ ok: true, plataforma: pl, titulo: pl === 'amazon-mx' ? '' : 'Producto de ejemplo leído del link', imagen: '', precio: null, moneda: '' }); }, 300); }); }
  } : {
    listar: function () {
      return Promise.all([
        sb.from('productos').select('*').eq('tipo', 'afiliado').order('orden').order('creado', { ascending: false }).then(ok),
        sb.from('afiliados_sync').select('*').then(function (r) { return r.data || []; })
      ]).then(function (x) { sync = {}; x[1].forEach(function (s) { sync[s.producto_id] = s; }); return x[0]; });
    },
    sincronizar: function () { return sb.functions.invoke('sincronizar-afiliados', { body: {} }).then(function (r) { if (r.error) throw r.error; return r.data; }); },
    guardar: function (p, nuevo) { var q = nuevo ? sb.from('productos').insert(p) : sb.from('productos').update(p).eq('id', p.id); return q.select().single().then(ok); },
    borrar: function (id) { return sb.from('productos').delete().eq('id', id).eq('tipo', 'afiliado').then(ok); },
    leer: function (url) { return sb.functions.invoke('leer-link', { body: { url: url } }).then(function (r) { if (r.error) throw r.error; return r.data; }); }
  };

  var filas = [], filtroPl = '', $tabla = $('#af-tabla'), sync = {};
  function esML(p) { return /^ml-/.test(p.plataforma_afiliado || ''); }
  function hace(iso) {
    var m = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
    return m < 2 ? 'recién' : m < 60 ? 'hace ' + m + ' min' : m < 1440 ? 'hace ' + Math.round(m / 60) + ' h' : 'hace ' + Math.round(m / 1440) + ' días';
  }
  function estadoSync(f) {
    var p = f.p; if (!esML(p) || f.nuevo) return '';
    if (p.pausado_por_sync) return '<span class="af-sync off">⏸ Pausado solo: sin stock o pausada en Mercado Libre. Se reactiva cuando vuelva a estar disponible.</span>';
    var s = sync[p.id];
    if (!s) return '<span class="af-sync">🔄 Precio y stock se sincronizan con Mercado Libre cada 4 horas.</span>';
    return '<span class="af-sync' + (s.resultado === 'sin-leer' ? ' warn' : '') + '">🔄 Revisado ' + hace(s.revisado) + ' · ' + esc(s.nota) + '</span>';
  }
  var cats = Object.keys(P.categorias);

  /* ---------- abrir y listar ---------- */
  function abrir() {
    C.mostrar('#v-afiliados');
    $tabla.innerHTML = '<p class="vacio">Cargando…</p>';
    api.listar().then(function (d) { filas = d.map(function (p) { return { p: p, sucio: false, nuevo: false }; }); pintar(); })
      .catch(function (e) { $tabla.innerHTML = '<p class="vacio err">No se pudieron cargar: ' + esc(e.message) + '</p>'; });
  }
  $('#af-filtro-pl').innerHTML = [['', 'Todas']].concat(Object.keys(PLAT).map(function (k) { return [k, PLAT[k].n]; })).map(function (x) {
    return '<button type="button" data-pl="' + x[0] + '" aria-pressed="' + (x[0] === '') + '">' + esc(x[1]) + ' <small></small></button>';
  }).join('');
  $$('#af-filtro-pl button').forEach(function (b) { b.addEventListener('click', function () { filtroPl = b.dataset.pl; pintar(); }); });
  $('#af-q').addEventListener('input', pintar);

  function moneda(p) { return p.precio_usd != null ? 'USD' : p.precio_mxn != null ? 'MXN' : p.precio_ars != null ? 'ARS' : (PLAT[p.plataforma_afiliado] || {}).mon || 'USD'; }
  function precio(p) { var v = p.precio_usd != null ? p.precio_usd : p.precio_mxn != null ? p.precio_mxn : p.precio_ars; return v == null ? '' : v; }
  function opts(xs, v) { return xs.map(function (x) { return '<option' + (x === v ? ' selected' : '') + '>' + esc(x) + '</option>'; }).join(''); }

  function fila(f, i) {
    var p = f.p, pl = PLAT[p.plataforma_afiliado], foto = (p.fotos || [])[0] || '', esAmazon = p.plataforma_afiliado === 'amazon-mx';
    return '<tr data-i="' + i + '" class="' + (f.sucio ? 'sucio' : '') + (f.cargando ? ' cargando' : '') + '">' +
      '<td class="af-foto"><span class="af-img">' + (foto ? '<img src="' + esc(foto) + '" alt="" referrerpolicy="no-referrer">' : '<em>Sin foto</em>') + '</span>' +
        '<input data-k="foto" value="' + esc(foto) + '" placeholder="Link de la foto" aria-label="Link de la foto"></td>' +
      '<td class="af-tit"><textarea data-k="nombre" rows="2" maxlength="140" placeholder="' + (f.cargando ? 'Leyendo el link…' : 'Título que se ve en tu sitio') + '" aria-label="Título">' + esc(p.nombre || '') + '</textarea>' +
        '<small><span class="af-pl af-' + esc(p.plataforma_afiliado || 'x') + '">' + esc(pl ? pl.n : 'Tienda sin detectar') + '</span>' + (p.codigo ? ' · ' + esc(p.codigo) : '') +
        ' · <a href="' + esc(p.url_afiliado) + '" target="_blank" rel="noopener">Abrir link ↗</a>' + (f.aviso ? ' · <span class="af-aviso">' + esc(f.aviso) + '</span>' : '') + estadoSync(f) + '</small></td>' +
      '<td class="af-cat"><select data-k="categoria" aria-label="Categoría">' + opts(cats, p.categoria) + '</select>' +
        '<select data-k="subcategoria" aria-label="Subcategoría">' + opts(P.categorias[p.categoria] || [], p.subcategoria) + '</select></td>' +
      '<td class="af-pre">' + (esAmazon ? '<span class="muted af-np">Ver precio<small>Amazon no permite precio fijo</small></span>' :
        '<input data-k="precio" type="number" min="0" step="0.01" value="' + esc(precio(p)) + '" placeholder="' + (esML(p) ? 'Automático' : 'Opcional') + '" aria-label="Precio"' + (esML(p) ? ' readonly title="Se actualiza solo desde Mercado Libre"' : '') + '>' +
        '<select data-k="moneda" aria-label="Moneda">' + opts(['ARS', 'MXN', 'USD'], moneda(p)) + '</select>') + '</td>' +
      '<td class="af-donde">' +
        '<label><input type="checkbox" data-k="tienda_ar"' + (p.tienda_ar ? ' checked' : '') + '> Tienda Argentina</label>' +
        '<label><input type="checkbox" data-k="international"' + (p.international ? ' checked' : '') + '> International Shop</label>' +
        '<label class="muted" title="Se va a ver cuando abra la Tienda México"><input type="checkbox" data-k="tienda_mx"' + (p.tienda_mx ? ' checked' : '') + '> Tienda México <small>(pronto)</small></label></td>' +
      '<td class="af-est"><select data-k="estado" aria-label="Estado">' + opts(['Borrador', 'Publicado', 'Pausado'], p.estado) + '</select></td>' +
      '<td class="af-acc"><button type="button" class="ic-btn del" data-borrar title="Eliminar" aria-label="Eliminar">🗑</button></td></tr>';
  }

  function pintar() {
    var q = $('#af-q').value.trim().toLowerCase();
    $$('#af-filtro-pl button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.pl === filtroPl));
      b.querySelector('small').textContent = filas.filter(function (f) { return !b.dataset.pl || f.p.plataforma_afiliado === b.dataset.pl; }).length;
    });
    var pub = filas.filter(function (f) { return f.p.estado === 'Publicado'; }).length, sucios = filas.filter(function (f) { return f.sucio; }).length;
    $('#af-guardar').disabled = !sucios;
    $('#af-guardar').textContent = sucios ? 'Guardar cambios (' + sucios + ')' : 'Guardar cambios';
    var vis = filas.map(function (f, i) { return [f, i]; }).filter(function (x) {
      var p = x[0].p; return (!filtroPl || p.plataforma_afiliado === filtroPl) && (!q || [p.nombre, p.codigo].join(' ').toLowerCase().indexOf(q) >= 0);
    });
    if (!vis.length) { $tabla.innerHTML = '<p class="vacio">' + (filas.length ? 'No hay productos con estos filtros.' : 'Todavía no cargaste productos. Pegá uno o varios links arriba.') + '</p>'; return; }
    $tabla.innerHTML = '<p class="af-cuenta muted">' + filas.length + ' productos · ' + pub + ' publicados' + (sucios ? ' · <b>' + sucios + ' sin guardar</b>' : '') + '</p>' +
      '<table class="ct af"><thead><tr><th>Foto</th><th>Título</th><th>Categoría</th><th>Precio</th><th>Dónde se ve</th><th>Estado</th><th></th></tr></thead><tbody>' +
      vis.map(function (x) { return fila(x[0], x[1]); }).join('') + '</tbody></table>';
  }

  /* ---------- edición en la tabla ---------- */
  function setCampo(f, k, el) {
    var p = f.p;
    if (k === 'foto') { p.fotos = el.value.trim() ? [el.value.trim()] : []; }
    else if (k === 'precio' || k === 'moneda') {
      var tr = el.closest('tr'), v = tr.querySelector('[data-k="precio"]').value, m = tr.querySelector('[data-k="moneda"]').value;
      p.precio_ars = p.precio_mxn = p.precio_usd = null;
      if (v !== '') p['precio_' + m.toLowerCase()] = Number(v);
    }
    else if (el.type === 'checkbox') p[k] = el.checked;
    else p[k] = el.value;
    if (k === 'categoria') p.subcategoria = (P.categorias[p.categoria] || [''])[0];
    f.sucio = true;
  }
  $tabla.addEventListener('input', function (e) {
    var el = e.target, tr = el.closest('tr[data-i]'); if (!tr || !el.dataset.k) return;
    var f = filas[+tr.dataset.i]; setCampo(f, el.dataset.k, el); tr.classList.add('sucio');
    if (el.dataset.k === 'foto') { var sp = tr.querySelector('.af-img'); sp.innerHTML = el.value ? '<img src="' + esc(el.value) + '" alt="" referrerpolicy="no-referrer">' : '<em>Sin foto</em>'; }
    var n = filas.filter(function (x) { return x.sucio; }).length;
    $('#af-guardar').disabled = !n; $('#af-guardar').textContent = 'Guardar cambios (' + n + ')';
  });
  $tabla.addEventListener('change', function (e) {
    var el = e.target, tr = el.closest('tr[data-i]'); if (!tr || !el.dataset.k) return;
    if (el.dataset.k === 'categoria') { setCampo(filas[+tr.dataset.i], 'categoria', el); pintar(); }
  });
  $tabla.addEventListener('click', function (e) {
    var b = e.target.closest('[data-borrar]'); if (!b) return;
    var i = +b.closest('tr').dataset.i, f = filas[i];
    if (!confirm('¿Eliminar "' + (f.p.nombre || f.p.url_afiliado) + '"? No se puede deshacer.')) return;
    (f.nuevo ? Promise.resolve() : api.borrar(f.p.id)).then(function () {
      filas.splice(i, 1); pintar(); if (!f.nuevo) { C.toast('Eliminado.'); C.publicar(); }
    }).catch(function (err) { C.toast('No se pudo eliminar: ' + err.message, true); });
  });

  /* ---------- carga rápida: pegar links ---------- */
  function nuevaFila(url) {
    var pl = platDe(url), def = PLAT[pl] || {};
    var p = { tipo: 'afiliado', url_afiliado: url, plataforma_afiliado: pl || '', nombre: '', descripcion: '', categoria: cats[0], subcategoria: (P.categorias[cats[0]] || [''])[0],
      fotos: [], precio_ars: null, precio_mxn: null, precio_usd: null, tienda_ar: !!def.ar, international: def.intl !== false, tienda_mx: false,
      estado: 'Borrador', pais: def.pais || 'Otro', vendedor: def.n || '', temas: [], paises_envio: [],
      slug: 'af-' + Math.random().toString(36).slice(2, 10), orden: 0 };
    return { p: p, sucio: true, nuevo: true, cargando: true };
  }
  function completar(f) {
    return api.leer(f.p.url_afiliado).then(function (r) {
      f.cargando = false;
      if (r && r.plataforma && PLAT[r.plataforma] && r.plataforma !== f.p.plataforma_afiliado) {
        var def = PLAT[r.plataforma]; f.p.plataforma_afiliado = r.plataforma; f.p.pais = def.pais; f.p.vendedor = def.n; f.p.tienda_ar = def.ar; f.p.international = def.intl;
      }
      if (r && r.titulo && !f.p.nombre) f.p.nombre = r.titulo;
      if (r && r.imagen && !(f.p.fotos || []).length && f.p.plataforma_afiliado !== 'amazon-mx') f.p.fotos = [r.imagen];
      if (r && r.precio && f.p.plataforma_afiliado !== 'amazon-mx' && /^(ARS|MXN|USD)$/.test(r.moneda)) f.p['precio_' + r.moneda.toLowerCase()] = r.precio;
      if (!r || !r.ok || !r.titulo) f.aviso = 'No se pudo leer el link: completá el título a mano';
      else if (f.p.plataforma_afiliado === 'amazon-mx') f.aviso = 'Foto: pegá la de SiteStripe de Amazon';
    }).catch(function () { f.cargando = false; f.aviso = 'No se pudo leer el link: completá el título a mano'; });
  }
  $('#af-agregar').addEventListener('click', function () {
    var links = $('#af-links').value.split(/\s+/).map(function (s) { return s.trim(); }).filter(function (s) { return /^https?:\/\//.test(s); });
    var malos = links.filter(function (u) { return platDe(u) === null; });
    links = links.filter(function (u) { return platDe(u) !== null; });
    var ya = filas.map(function (f) { return f.p.url_afiliado; });
    var repetidos = links.filter(function (u) { return ya.indexOf(u) >= 0; });
    links = links.filter(function (u, i) { return ya.indexOf(u) < 0 && links.indexOf(u) === i; });
    var msg = [];
    if (malos.length) msg.push(malos.length + ' de otra tienda (no se agregaron)');
    if (repetidos.length) msg.push(repetidos.length + ' ya estaban en la tabla');
    if (!links.length) { $('#af-estado-carga').textContent = msg.join(' · ') || 'Pegá al menos un link.'; return; }
    var nuevas = links.map(nuevaFila);
    filas = nuevas.concat(filas); filtroPl = ''; pintar();
    $('#af-links').value = '';
    $('#af-estado-carga').textContent = 'Leyendo ' + nuevas.length + ' link' + (nuevas.length === 1 ? '' : 's') + '…' + (msg.length ? ' · ' + msg.join(' · ') : '');
    // de a 3 por vez para no saturar
    var cola = nuevas.slice(), activos = 0;
    function siguiente() {
      if (!cola.length) { if (!activos) { $('#af-estado-carga').textContent = 'Listo: revisá los títulos y tocá "Guardar cambios".'; } return; }
      var f = cola.shift(); activos++;
      completar(f).then(function () { activos--; pintar(); siguiente(); });
    }
    for (var k = 0; k < 3; k++) siguiente();
  });

  /* ---------- sincronizar con Mercado Libre ahora ---------- */
  $('#af-sync').addEventListener('click', function () {
    if (filas.some(function (f) { return f.sucio; })) { C.toast('Primero guardá los cambios pendientes.', true); return; }
    var b = this; b.disabled = true; b.textContent = 'Sincronizando…';
    api.sincronizar().then(function (r) {
      C.toast('Listo: ' + r.revisados + ' revisados · ' + r.precios + ' precios actualizados · ' + r.pausados + ' pausados · ' + r.reactivados + ' reactivados' + (r.sin_leer ? ' · ' + r.sin_leer + ' sin leer' : '') + '.');
      abrir();
    }).catch(function (e) { C.toast('No se pudo sincronizar: ' + e.message, true); })
      .then(function () { b.disabled = false; b.textContent = 'Sincronizar precios ahora'; });
  });

  /* ---------- guardar todo ---------- */
  var CAMPOS = ['tipo', 'url_afiliado', 'plataforma_afiliado', 'nombre', 'descripcion', 'categoria', 'subcategoria', 'fotos', 'precio_ars', 'precio_mxn', 'precio_usd',
    'tienda_ar', 'international', 'tienda_mx', 'estado', 'pais', 'vendedor', 'temas', 'paises_envio', 'slug', 'orden'];
  $('#af-guardar').addEventListener('click', function () {
    var sucios = filas.filter(function (f) { return f.sucio; });
    var sinTit = sucios.filter(function (f) { return !String(f.p.nombre || '').trim() && f.p.estado === 'Publicado'; });
    if (sinTit.length) { C.toast('Hay ' + sinTit.length + ' producto(s) publicados sin título. Escribilo o dejalos en Borrador.', true); return; }
    var b = $('#af-guardar'); b.disabled = true; b.textContent = 'Guardando…';
    Promise.all(sucios.map(function (f) {
      var d = {}; CAMPOS.forEach(function (k) { if (k in f.p) d[k] = f.p[k]; });
      if (!d.nombre) d.nombre = 'Producto sin título';
      if (!f.nuevo) d.id = f.p.id;
      return api.guardar(d, f.nuevo).then(function (g) { f.p = g; f.sucio = false; f.nuevo = false; f.aviso = ''; return true; })
        .catch(function (e) { f.aviso = 'No se guardó: ' + e.message; return false; });
    })).then(function (rs) {
      var bien = rs.filter(Boolean).length;
      pintar();
      if (bien) { C.toast(bien === rs.length ? 'Guardado. Los publicados aparecen en el sitio en unos minutos.' : 'Se guardaron ' + bien + ' de ' + rs.length + '. Revisá los que tienen aviso.', bien !== rs.length); C.publicar(); }
      else C.toast('No se pudo guardar. Revisá los avisos en la tabla.', true);
    });
  });
  window.addEventListener('beforeunload', function (e) { if (filas.some(function (f) { return f.sucio; })) { e.preventDefault(); e.returnValue = ''; } });

  window.PanelAfiliados = { abrir: abrir };
})();
