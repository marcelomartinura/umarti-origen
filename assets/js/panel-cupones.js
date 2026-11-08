/* Panel · módulo Cupones (tabla "cupones" en Supabase) */
(function () {
  'use strict';
  var C = window.PanelComun; if (!C) return;
  var $ = C.$, $$ = C.$$, esc = C.esc, CU = C.P.cupones, sb = C.sb, demo = C.demo;
  function ok(r) { if (r.error) throw r.error; return r.data; }
  var datosDemo = [
    { id: 'c1', codigo: 'CU-0016', titulo: '20% en tu primer masaje descontracturante', comercio: 'Spa Agua Termal', categoria: 'Belleza y Spa', tipo: 'Código', cupon: 'SPA20', descuento: '20%', descripcion: 'Masaje de 60 minutos.', condiciones: 'Con reserva previa.', pais: 'México', ciudad: 'Querétaro', vence: '2027-01-31', link: '', destacado: true, exclusivo: true, destino: '', tema: '', estado: 'Ejemplo', slug: 'spa', orden: 0 },
    { id: 'c2', codigo: 'CU-0004', titulo: '2x1 en empanadas los martes', comercio: 'La Salteña de Palermo', categoria: 'Gastronomía', tipo: 'Oferta', cupon: '', descuento: '2x1', descripcion: 'Empanadas salteñas.', condiciones: 'Solo los martes.', pais: 'Argentina', ciudad: 'Buenos Aires', vence: '2026-12-15', link: '', destacado: false, exclusivo: false, destino: 'buenos-aires', tema: '', estado: 'Publicado', slug: 'x', orden: 1 }
  ];
  var api = demo ? {
    listar: function () { return Promise.resolve(datosDemo.slice()); },
    guardar: function (c, nuevo) { if (nuevo) { c.id = 'n' + Date.now(); c.codigo = 'CU-00' + (datosDemo.length + 20); datosDemo.push(c); } else datosDemo = datosDemo.map(function (x) { return x.id === c.id ? c : x; }); return Promise.resolve(c); },
    borrar: function (id) { datosDemo = datosDemo.filter(function (x) { return x.id !== id; }); return Promise.resolve(); },
    destinos: function () { return Promise.resolve([{ slug: 'buenos-aires', ciudad: 'Buenos Aires', estado: 'Publicado' }]); }
  } : {
    listar: function () { return sb.from('cupones').select('*').order('orden').order('creado').then(ok); },
    guardar: function (c, nuevo) { var q = nuevo ? sb.from('cupones').insert(c) : sb.from('cupones').update(c).eq('id', c.id); return q.select().single().then(ok); },
    borrar: function (id) { return sb.from('cupones').delete().eq('id', id).then(ok); },
    destinos: function () { return sb.from('destinos').select('slug,ciudad,estado').order('ciudad').then(ok); }
  };

  /* ---------- lista ---------- */
  var lista = [], filtroEstado = '';
  var selCat = $('#cl-cat');
  CU.categorias.forEach(function (c) { var o = document.createElement('option'); o.value = c; o.textContent = c; selCat.appendChild(o); });
  $('#cl-estados').innerHTML = ['', 'Publicado', 'Borrador', 'Pausado', 'Ejemplo'].map(function (e) { return '<button type="button" data-estado="' + e + '" aria-pressed="' + (e === '') + '">' + (e || 'Todos') + ' <small></small></button>'; }).join('');
  $$('#cl-estados button').forEach(function (b) { b.addEventListener('click', function () { filtroEstado = b.dataset.estado; pintar(); }); });
  $('#cl-q').addEventListener('input', pintar); selCat.addEventListener('change', pintar);
  $('#cb-nuevo').addEventListener('click', function () { editar(null); });

  function vencido(c) { return c.vence && c.vence < new Date().toISOString().slice(0, 10); }
  function fecha(d) { if (!d) return '—'; var p = d.slice(0, 10).split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }
  function abrir() {
    C.mostrar('#v-clista');
    $('#cl-tabla').innerHTML = '<p class="vacio">Cargando cupones…</p>';
    api.listar().then(function (d) { lista = d; pintar(); }).catch(function (e) { $('#cl-tabla').innerHTML = '<p class="vacio err">No se pudieron cargar los cupones: ' + esc(e.message) + '</p>'; });
  }
  function pintar() {
    var q = $('#cl-q').value.trim().toLowerCase(), cat = selCat.value;
    $$('#cl-estados button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.estado === filtroEstado)); b.querySelector('small').textContent = lista.filter(function (c) { return !b.dataset.estado || c.estado === b.dataset.estado; }).length; });
    var xs = lista.filter(function (c) {
      return (!filtroEstado || c.estado === filtroEstado) && (!cat || c.categoria === cat) &&
        (!q || [c.titulo, c.comercio, c.codigo, c.cupon, c.ciudad].join(' ').toLowerCase().indexOf(q) >= 0);
    });
    var pub = lista.filter(function (c) { return c.estado === 'Publicado'; }).length;
    $('#cl-resumen').textContent = lista.length + ' cupones · ' + pub + ' publicados · ' + lista.filter(vencido).length + ' vencidos';
    if (!xs.length) { $('#cl-tabla').innerHTML = '<p class="vacio">' + (lista.length ? 'No hay cupones con estos filtros.' : 'Todavía no hay cupones. Tocá "+ Nuevo cupón".') + '</p>'; return; }
    $('#cl-tabla').innerHTML = '<table class="ct"><thead><tr><th></th><th>Cupón</th><th>Categoría</th><th>Dónde</th><th>Vence</th><th>Estado</th></tr></thead><tbody>' + xs.map(function (c) {
      return '<tr data-id="' + esc(c.id) + '"><td><span class="cbig">' + esc(c.descuento || '%') + '</span></td>' +
        '<td><b>' + esc(c.titulo) + '</b><small>' + esc(c.codigo) + ' · ' + esc(c.comercio) + (c.tipo === 'Código' && c.cupon ? ' · <code>' + esc(c.cupon) + '</code>' : '') + (c.destacado ? ' · ★' : '') + '</small></td>' +
        '<td>' + esc(c.categoria) + '</td><td><small>' + esc([c.ciudad, c.pais].filter(Boolean).join(', ')) + '</small></td>' +
        '<td' + (vencido(c) ? ' class="venc"' : '') + '>' + fecha(c.vence) + (vencido(c) ? '<small>Vencido</small>' : '') + '</td>' +
        '<td><span class="st st-' + esc((c.estado || '').toLowerCase()) + '">' + esc(c.estado) + '</span></td></tr>';
    }).join('') + '</tbody></table>';
    $$('#cl-tabla tr[data-id]').forEach(function (tr) { tr.addEventListener('click', function () { editar(lista.find(function (c) { return c.id === tr.dataset.id; })); }); });
  }

  /* ---------- editor ---------- */
  var f = $('#f-cupon'), actual = null, nuevo = false, sucio = false;
  var CAMPOS = ['titulo', 'comercio', 'categoria', 'tipo', 'cupon', 'descuento', 'descripcion', 'condiciones', 'pais', 'ciudad', 'vence', 'link', 'destino', 'tema', 'estado'];
  f.categoria.innerHTML = CU.categorias.map(function (c) { return '<option>' + esc(c) + '</option>'; }).join('');
  f.pais.innerHTML = CU.paises.map(function (c) { return '<option>' + esc(c) + '</option>'; }).join('');
  f.tema.innerHTML += C.P.temas.map(function (t) { return '<option value="' + esc(t.clave) + '">' + esc(t.nombre) + '</option>'; }).join('');
  api.destinos().then(function (ds) {
    f.destino.innerHTML = '<option value="">Ninguno</option>' + ds.map(function (d) { return '<option value="' + esc(d.slug) + '">' + esc(d.ciudad) + (d.estado !== 'Publicado' ? ' (borrador)' : '') + '</option>'; }).join('');
    if (actual) f.destino.value = actual.destino || '';
  }).catch(function () {});

  function editar(c, copia) {
    nuevo = !c || !!copia;
    var hoy = new Date(); hoy.setMonth(hoy.getMonth() + 3);
    actual = c ? JSON.parse(JSON.stringify(c)) : { categoria: CU.categorias[0], tipo: 'Código', pais: 'Argentina', estado: 'Borrador', vence: hoy.toISOString().slice(0, 10), destacado: false, exclusivo: false };
    if (copia) { delete actual.id; delete actual.codigo; actual.estado = 'Borrador'; actual.titulo = actual.titulo + ' (copia)'; }
    CAMPOS.forEach(function (k) { f[k].value = actual[k] == null ? '' : String(actual[k]).slice(0, k === 'vence' ? 10 : 9999); });
    f.destacado.checked = !!actual.destacado; f.exclusivo.checked = !!actual.exclusivo;
    $('#ce-titulo').textContent = nuevo ? 'Nuevo cupón' : actual.titulo;
    $('#ce-sub').textContent = nuevo ? 'El código (CU-…) se asigna solo al guardar.' : actual.codigo + (vencido(actual) ? ' · vencido: no se muestra en el sitio' : '');
    $('#ce-borrar').hidden = nuevo; $('#ce-duplicar').hidden = nuevo; $('#ce-msg').textContent = ''; sucio = false;
    tipoUI(); preview();
    C.mostrar('#v-ceditor');
  }
  function tipoUI() { $('#ce-cod').hidden = f.tipo.value !== 'Código'; }
  f.tipo.addEventListener('change', tipoUI);
  f.addEventListener('input', function () { sucio = true; preview(); });
  f.addEventListener('change', preview);
  function preview() {
    $('#ce-prev').innerHTML = '<div class="cpv-top"><b>' + esc(f.descuento.value || '%') + '</b>' + (f.exclusivo.checked ? '<em>Exclusivo Umarti</em>' : '') + '</div>' +
      '<div class="cpv-body"><strong>' + esc(f.titulo.value || 'Título del cupón') + '</strong><small>' + esc([f.comercio.value || 'Comercio', [f.ciudad.value, f.pais.value].filter(Boolean).join(', ')].filter(Boolean).join(' · ')) + '</small>' +
      '<span class="cpv-tag">' + esc(f.tipo.value) + '</span> <span class="cpv-v">Vence ' + fecha(f.vence.value) + '</span>' +
      (f.tipo.value === 'Código' ? '<div class="cpv-code">' + esc((f.cupon.value || 'CODIGO').toUpperCase()) + '</div>' : '') + '</div>';
  }
  function slugify(t) { return C.slugify(t); }
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var c = Object.assign({}, actual), m = $('#ce-msg');
    CAMPOS.forEach(function (k) { c[k] = f[k].value.trim(); });
    c.cupon = c.tipo === 'Código' ? c.cupon.toUpperCase() : '';
    c.destacado = f.destacado.checked; c.exclusivo = f.exclusivo.checked;
    c.vence = c.vence || null;
    c.slug = slugify(c.comercio + ' ' + c.titulo);
    if (!c.titulo || !c.comercio || !c.descuento || !c.vence) { m.className = 'msg err'; m.textContent = 'Completá título, comercio, descuento y vencimiento.'; return; }
    if (c.tipo === 'Código' && !c.cupon) { m.className = 'msg err'; m.textContent = 'Poné el código del cupón (o cambiá el tipo a Oferta).'; return; }
    delete c.creado; delete c.actualizado; if (nuevo) { delete c.id; delete c.codigo; }
    $('#ce-guardar').disabled = true; m.className = 'msg'; m.textContent = 'Guardando…';
    api.guardar(c, nuevo).then(function (g) {
      var i = lista.findIndex(function (x) { return x.id === g.id; }); if (i >= 0) lista[i] = g; else lista.push(g);
      actual = g; nuevo = false; sucio = false;
      $('#ce-titulo').textContent = g.titulo; $('#ce-sub').textContent = g.codigo; $('#ce-borrar').hidden = false; $('#ce-duplicar').hidden = false;
      C.publicar(); m.className = 'msg ok'; m.textContent = (g.estado === 'Publicado' || g.estado === 'Ejemplo') ? 'Guardado. Se ve en la Cuponera en unos minutos.' : 'Guardado.';
    }).catch(function (er) { m.className = 'msg err'; m.textContent = 'No se pudo guardar: ' + er.message; })
      .then(function () { $('#ce-guardar').disabled = false; });
  });
  $('#ce-volver').addEventListener('click', function () { if (sucio && !confirm('Tenés cambios sin guardar. ¿Salir igual?')) return; C.mostrar('#v-clista'); pintar(); });
  $('#ce-duplicar').addEventListener('click', function () { editar(actual, true); });
  $('#ce-borrar').addEventListener('click', function () {
    if (!confirm('¿Eliminar el cupón "' + actual.titulo + '"?')) return;
    api.borrar(actual.id).then(function () { lista = lista.filter(function (x) { return x.id !== actual.id; }); C.toast('Cupón eliminado.'); C.publicar(); C.mostrar('#v-clista'); pintar(); })
      .catch(function (er) { C.toast('No se pudo eliminar: ' + er.message, true); });
  });

  window.PanelCupones = { abrir: abrir };
})();
