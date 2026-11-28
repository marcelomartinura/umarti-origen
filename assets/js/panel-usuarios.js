/* Panel · Usuarios registrados (función admin_usuarios) y suscriptores a novedades */
(function () {
  'use strict';
  var C = window.PanelComun; if (!C) return;
  var $ = C.$, $$ = C.$$, esc = C.esc, sb = C.sb, demo = C.demo;
  function ok(r) { if (r.error) throw r.error; return r.data; }
  var hoy = Date.now();
  var datosDemo = [
    { id: 'u1', correo: 'ana.perez@gmail.com', registrado: new Date(hoy - 864e5 * 12).toISOString(), ultimo_ingreso: new Date(hoy - 36e5 * 5).toISOString(), confirmado: true, es_admin: false, nombre: 'Ana', apellido: 'Pérez', telefono: '+54 9 11 5555 1234', pais: 'Argentina', tienda: 'AR', envio: { calle: 'Av. Corrientes 1234', ciudad: 'CABA', provincia: 'Buenos Aires', cp: '1043' }, novedades: true, favoritos: ['UM-0006', 'UM-0009'], suscripto: true },
    { id: 'u2', correo: 'carlos.mx@hotmail.com', registrado: new Date(hoy - 864e5 * 3).toISOString(), ultimo_ingreso: null, confirmado: false, es_admin: false, nombre: '', apellido: '', telefono: '', pais: 'México', tienda: 'AR', envio: {}, novedades: false, favoritos: [], suscripto: false },
    { id: 'u3', correo: 'urangamarcelo74@gmail.com', registrado: new Date(hoy - 864e5 * 14).toISOString(), ultimo_ingreso: new Date(hoy - 6e5).toISOString(), confirmado: true, es_admin: true, nombre: '', apellido: '', telefono: '', pais: '', tienda: 'AR', envio: {}, novedades: false, favoritos: [], suscripto: false }
  ];
  var api = demo ? {
    usuarios: function () { return Promise.resolve(datosDemo); },
    suscriptores: function () { return Promise.resolve([{ correo: 'lector@gmail.com', origen: 'portada', activo: true, creado: new Date().toISOString() }]); },
    productos: function () { return C.productos(); }
  } : {
    usuarios: function () { return sb.rpc('admin_usuarios').then(ok); },
    suscriptores: function () { return sb.from('suscriptores').select('correo,origen,activo,creado').order('creado', { ascending: false }).then(ok); },
    productos: function () { return C.productos(); }
  };

  var usuarios = [], suscriptores = [], nombres = {}, filtro = '', tab = 'usuarios';
  function fecha(d, conHora) {
    if (!d) return '—';
    var x = new Date(d);
    return x.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' }) + (conHora ? ' ' + x.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) : '');
  }
  function hace(d) {
    if (!d) return 'Nunca ingresó';
    var m = Math.round((Date.now() - new Date(d)) / 6e4);
    if (m < 60) return 'Hace ' + Math.max(1, m) + ' min';
    var h = Math.round(m / 60); if (h < 24) return 'Hace ' + h + ' h';
    var dd = Math.round(h / 24); if (dd < 30) return 'Hace ' + dd + (dd === 1 ? ' día' : ' días');
    return fecha(d);
  }
  function envioCompleto(u) { var e = u.envio || {}; return !!(e.calle && e.ciudad); }
  function nombreDe(u) { return [u.nombre, u.apellido].filter(Boolean).join(' '); }
  function activo30(u) { return u.ultimo_ingreso && (Date.now() - new Date(u.ultimo_ingreso)) < 864e5 * 30; }

  var FILTROS = [['', 'Todos'], ['confirmados', 'Confirmados'], ['pendientes', 'Sin confirmar'], ['activos', 'Activos (30 días)'], ['novedades', 'Reciben novedades'], ['envio', 'Con datos de envío']];
  $('#us-filtros').innerHTML = FILTROS.map(function (f) { return '<button type="button" data-f="' + f[0] + '" aria-pressed="' + (f[0] === '') + '">' + f[1] + ' <small></small></button>'; }).join('');
  $$('#us-filtros button').forEach(function (b) { b.addEventListener('click', function () { filtro = b.dataset.f; pintar(); }); });
  $('#us-q').addEventListener('input', pintar);
  $$('.us-tabs [data-tab]').forEach(function (b) {
    b.addEventListener('click', function () {
      tab = b.dataset.tab;
      $$('.us-tabs [data-tab]').forEach(function (x) { x.classList.toggle('on', x === b); });
      $$('#v-usuarios [data-panel]').forEach(function (p) { p.hidden = p.dataset.panel !== tab; });
    });
  });
  function pasa(u, f) {
    return !f || (f === 'confirmados' && u.confirmado) || (f === 'pendientes' && !u.confirmado) || (f === 'activos' && activo30(u)) ||
      (f === 'novedades' && u.suscripto) || (f === 'envio' && envioCompleto(u));
  }

  function abrir() {
    C.mostrar('#v-usuarios');
    $('#us-tabla').innerHTML = '<p class="vacio">Cargando usuarios…</p>';
    Promise.all([api.usuarios(), api.suscriptores().catch(function () { return []; }), api.productos().catch(function () { return []; })])
      .then(function (r) {
        usuarios = r[0] || []; suscriptores = r[1] || [];
        nombres = {}; (r[2] || []).forEach(function (p) { nombres[p.codigo] = p.nombre; });
        pintar(); pintarSus();
      })
      .catch(function (e) { $('#us-tabla').innerHTML = '<p class="vacio err">No se pudieron cargar los usuarios: ' + esc(e.message) + '</p>'; });
  }

  function kpis() {
    var semana = usuarios.filter(function (u) { return (Date.now() - new Date(u.registrado)) < 864e5 * 7; }).length;
    var items = [['Registrados', usuarios.length, ''], ['Nuevos esta semana', semana, ''], ['Activos (30 días)', usuarios.filter(activo30).length, ''],
      ['Con favoritos', usuarios.filter(function (u) { return (u.favoritos || []).length; }).length, ''], ['Compras', 0, 'se registran al activar el pago'],
      ['Suscriptores', suscriptores.filter(function (s) { return s.activo; }).length, 'a novedades']];
    $('#us-kpis').innerHTML = items.map(function (k) { return '<div class="us-kpi"><b>' + k[1] + '</b><span>' + esc(k[0]) + '</span>' + (k[2] ? '<small>' + esc(k[2]) + '</small>' : '') + '</div>'; }).join('');
  }

  function pintar() {
    kpis();
    var q = $('#us-q').value.trim().toLowerCase();
    $$('#us-filtros button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.f === filtro)); b.querySelector('small').textContent = usuarios.filter(function (u) { return pasa(u, b.dataset.f); }).length; });
    var xs = usuarios.filter(function (u) { return pasa(u, filtro) && (!q || [u.correo, nombreDe(u), u.pais, u.telefono].join(' ').toLowerCase().indexOf(q) >= 0); });
    $('#us-resumen').textContent = usuarios.length + (usuarios.length === 1 ? ' usuario registrado' : ' usuarios registrados');
    if (!xs.length) { $('#us-tabla').innerHTML = '<p class="vacio">' + (usuarios.length ? 'No hay usuarios con estos filtros.' : 'Todavía no se registró nadie.') + '</p>'; return; }
    $('#us-tabla').innerHTML = '<table class="ct us"><thead><tr><th>Usuario</th><th>País</th><th>Registro</th><th>Último ingreso</th><th>Actividad</th><th>Estado</th></tr></thead><tbody>' + xs.map(function (u) {
      var n = nombreDe(u), ini = ((n || u.correo).split(/[\s@.]+/).filter(Boolean).map(function (p) { return p[0]; }).join('').slice(0, 2)).toUpperCase();
      var act = [];
      if ((u.favoritos || []).length) act.push('<span class="us-pill fav">♥ ' + u.favoritos.length + '</span>');
      if (envioCompleto(u)) act.push('<span class="us-pill env">Envío</span>');
      if (u.suscripto) act.push('<span class="us-pill nov">Novedades</span>');
      act.push('<span class="us-pill cmp">0 compras</span>');
      return '<tr data-id="' + esc(u.id) + '"><td><div class="us-quien"><span class="us-av">' + esc(ini) + '</span><span><b>' + esc(n || 'Sin nombre') + (u.es_admin ? ' <em class="us-admin">Admin</em>' : '') + '</b><small>' + esc(u.correo) + '</small></span></div></td>' +
        '<td>' + esc(u.pais || '—') + '</td><td>' + fecha(u.registrado) + '</td><td>' + esc(hace(u.ultimo_ingreso)) + '</td>' +
        '<td><div class="us-act">' + act.join('') + '</div></td>' +
        '<td><span class="st ' + (u.confirmado ? 'st-publicado">Confirmado' : 'st-borrador">Sin confirmar') + '</span></td></tr>';
    }).join('') + '</tbody></table>';
    $$('#us-tabla tr[data-id]').forEach(function (tr) { tr.addEventListener('click', function () { detalle(usuarios.find(function (u) { return u.id === tr.dataset.id; })); }); });
  }

  function pintarSus() {
    var xs = suscriptores;
    $('#us-sus').innerHTML = !xs.length ? '<p class="vacio">Todavía no hay suscriptores. Se suman desde el formulario de la portada.</p>' :
      '<table class="ct us"><thead><tr><th>Correo</th><th>Desde</th><th>Origen</th><th>Estado</th></tr></thead><tbody>' + xs.map(function (s) {
        return '<tr><td><b>' + esc(s.correo) + '</b></td><td>' + fecha(s.creado) + '</td><td>' + esc(s.origen || '—') + '</td><td><span class="st ' + (s.activo ? 'st-publicado">Activo' : 'st-borrador">Dado de baja') + '</span></td></tr>';
      }).join('') + '</tbody></table>';
  }

  function detalle(u) {
    var box = $('#us-det'), e = u.envio || {}, n = nombreDe(u);
    var dir = [e.calle, e.depto, e.cp, e.ciudad, e.provincia].filter(Boolean).join(', ');
    var favs = (u.favoritos || []).map(function (c) { return '<li>' + esc(nombres[c] || c) + ' <small>' + esc(c) + '</small></li>'; }).join('');
    box.innerHTML = '<div class="us-det-card" role="dialog" aria-label="Detalle del usuario">' +
      '<button type="button" class="us-x" aria-label="Cerrar">×</button>' +
      '<div class="us-det-top"><span class="us-av big">' + esc(((n || u.correo)[0] || '?').toUpperCase()) + '</span><div><h2>' + esc(n || 'Sin nombre') + '</h2><a href="mailto:' + esc(u.correo) + '">' + esc(u.correo) + '</a></div></div>' +
      '<dl class="us-dl">' +
      '<dt>Estado</dt><dd>' + (u.confirmado ? 'Correo confirmado' : 'Todavía no confirmó el correo') + (u.es_admin ? ' · Administrador' : '') + '</dd>' +
      '<dt>Registro</dt><dd>' + fecha(u.registrado, true) + '</dd>' +
      '<dt>Último ingreso</dt><dd>' + (u.ultimo_ingreso ? fecha(u.ultimo_ingreso, true) : 'Nunca ingresó') + '</dd>' +
      '<dt>Teléfono</dt><dd>' + esc(u.telefono || '—') + '</dd>' +
      '<dt>País</dt><dd>' + esc(u.pais || '—') + ' · Tienda ' + esc(u.tienda || 'AR') + '</dd>' +
      '<dt>Envío</dt><dd>' + esc(dir || 'Sin datos de envío') + (e.indicaciones ? '<br><small>' + esc(e.indicaciones) + '</small>' : '') + '</dd>' +
      '<dt>Novedades</dt><dd>' + (u.suscripto ? 'Sí, quiere recibir novedades' : 'No') + '</dd>' +
      '<dt>Compras</dt><dd>Sin compras registradas</dd>' +
      '</dl>' +
      '<h3>Favoritos (' + (u.favoritos || []).length + ')</h3>' + (favs ? '<ul class="us-favs">' + favs + '</ul>' : '<p class="muted">No guardó productos.</p>') +
      '</div>';
    box.hidden = false;
    box.querySelector('.us-x').addEventListener('click', function () { box.hidden = true; });
    box.addEventListener('click', function (ev) { if (ev.target === box) box.hidden = true; }, { once: true });
  }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') $('#us-det').hidden = true; });

  function csv(filas) {
    return filas.map(function (f) { return f.map(function (v) { v = v == null ? '' : String(v); return /[",;\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }).join(','); }).join('\n');
  }
  $('#us-csv').addEventListener('click', function () {
    var txt, nombre;
    if (tab === 'suscriptores') {
      txt = csv([['correo', 'desde', 'origen', 'activo']].concat(suscriptores.map(function (s) { return [s.correo, fecha(s.creado), s.origen, s.activo ? 'sí' : 'no']; })));
      nombre = 'suscriptores-umarti.csv';
    } else {
      txt = csv([['nombre', 'apellido', 'correo', 'telefono', 'pais', 'registro', 'ultimo_ingreso', 'confirmado', 'novedades', 'favoritos', 'calle', 'depto', 'cp', 'ciudad', 'provincia']].concat(usuarios.map(function (u) {
        var e = u.envio || {};
        return [u.nombre, u.apellido, u.correo, u.telefono, u.pais, fecha(u.registrado, true), u.ultimo_ingreso ? fecha(u.ultimo_ingreso, true) : '', u.confirmado ? 'sí' : 'no', u.suscripto ? 'sí' : 'no', (u.favoritos || []).length, e.calle, e.depto, e.cp, e.ciudad, e.provincia];
      })));
      nombre = 'usuarios-umarti.csv';
    }
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob(['﻿' + txt], { type: 'text/csv;charset=utf-8' }));
    a.download = nombre; document.body.appendChild(a); a.click(); a.remove();
  });

  window.PanelUsuarios = { abrir: abrir };
})();
