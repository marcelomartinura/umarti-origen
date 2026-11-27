/* Panel · módulo Blog (tabla "blog_notas" en Supabase; fotos en el bucket "blog") */
(function () {
  'use strict';
  var C = window.PanelComun; if (!C) return;
  var $ = C.$, $$ = C.$$, esc = C.esc, sb = C.sb, demo = C.demo, P = C.P, B = P.blog;
  var BUCKET = 'blog';
  function ok(r) { if (r.error) throw r.error; return r.data; }

  var datosDemo = [
    { id: 'n1', slug: 'que-es-el-mate', titulo: 'Qué es el mate: origen, tradición y cómo se toma', resumen: 'Una infusión de origen guaraní que se volvió símbolo de amistad.', seccion: 'productos', categoria: 'Café, Té y Mate', subcategoria: 'Mates y bombillas', tema: '', autor: '', tags: ['mate', 'yerba mate', 'historia'], fecha: '2026-10-18', imagen: 'assets/img/blog/mate-galeria-de-piedra.jpg', imagen_alt: 'Mate', imagen_pos: '', cuerpo: 'El mate es una infusión.\n\n## De dónde viene\n\nTexto.', destacada: true, estado: 'Publicado' },
    { id: 'n2', slug: 'por-que-empezamos-por-el-origen', titulo: 'Por qué empezamos por el origen', resumen: 'Detrás de cada producto hay un lugar.', seccion: 'opinion', categoria: '', subcategoria: '', tema: 'Negocios', autor: 'marcelo-uranga', tags: ['emprender'], fecha: '2026-10-18', imagen: '', imagen_alt: '', imagen_pos: '', cuerpo: 'Texto corto.\n\n> **Borrador:** reescribilo con tu voz.', destacada: false, estado: 'Borrador' }
  ];
  var api = demo ? {
    listar: function () { return Promise.resolve(datosDemo.slice()); },
    guardar: function (n, nuevo) { if (nuevo) { n.id = 'x' + Date.now(); datosDemo.push(n); } else datosDemo = datosDemo.map(function (x) { return x.id === n.id ? n : x; }); return Promise.resolve(n); },
    borrar: function (id) { datosDemo = datosDemo.filter(function (x) { return x.id !== id; }); return Promise.resolve(); },
    borrarVarias: function (ids) { datosDemo = datosDemo.filter(function (x) { return ids.indexOf(x.id) < 0; }); return Promise.resolve(); },
    subir: function (ruta, blob) { return Promise.resolve(URL.createObjectURL(blob)); }
  } : {
    listar: function () { return sb.from('blog_notas').select('*').order('fecha', { ascending: false }).order('creado', { ascending: false }).then(ok); },
    guardar: function (n, nuevo) { var q = nuevo ? sb.from('blog_notas').insert(n) : sb.from('blog_notas').update(n).eq('id', n.id); return q.select().single().then(ok); },
    borrar: function (id) { return sb.from('blog_notas').delete().eq('id', id).then(ok); },
    borrarVarias: function (ids) { return sb.from('blog_notas').delete().in('id', ids).then(ok); },
    subir: function (ruta, blob) {
      return sb.storage.from(BUCKET).upload(ruta, blob, { contentType: 'image/jpeg', upsert: false }).then(function (r) {
        if (r.error) throw r.error;
        return sb.storage.from(BUCKET).getPublicUrl(ruta).data.publicUrl;
      });
    }
  };

  var SECCION = { productos: 'Productos', negocios: 'Negocios', opinion: 'Opinión' };
  function verFoto(u) { return !u ? '' : /^(https?:|blob:)/.test(u) ? u : '../' + u; }
  function palabras(t) { return (String(t || '').replace(/!\[[^\]]*\]\([^)]*\)/g, ' ').match(/[\wáéíóúñü]+/gi) || []).length; }
  function fecha(d) { if (!d) return '—'; var p = d.slice(0, 10).split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }

  /* Lo que le falta a una nota para quedar completa: [texto, grave] */
  function faltantes(n) {
    var out = [], w = palabras(n.cuerpo);
    if (!n.titulo) out.push(['Título', true]);
    if (!n.resumen || n.resumen.length < 60) out.push([n.resumen ? 'Resumen muy corto' : 'Resumen', true]);
    if (!w) out.push(['Texto', true]);
    else if (w < 350) out.push(['Texto corto (' + w + ' palabras)', false]);
    if (w && !/^## /m.test(n.cuerpo || '')) out.push(['Subtítulos', false]);
    if (!n.imagen) out.push(['Foto de portada', false]);
    else if (!n.imagen_alt) out.push(['Descripción de la foto', false]);
    if (!n.tags || n.tags.length < 2) out.push(['Etiquetas', false]);
    if (/\*\*Borrador:\*\*/.test(n.cuerpo || '')) out.push(['Quitar el aviso de borrador', true]);
    return out;
  }

  /* ---------- lista ---------- */
  var lista = [], filtroEstado = '', marcadas = {};
  $('#bl-estados').innerHTML = ['', 'Publicado', 'Borrador', 'Incompletas'].map(function (e) { return '<button type="button" data-estado="' + e + '" aria-pressed="' + (e === '') + '">' + (e || 'Todas') + ' <small></small></button>'; }).join('');
  $$('#bl-estados button').forEach(function (b) { b.addEventListener('click', function () { filtroEstado = b.dataset.estado; pintar(); }); });
  $('#bl-q').addEventListener('input', pintar); $('#bl-sec').addEventListener('change', pintar);
  $('#bb-nueva').addEventListener('click', function () { editar(null); });

  function pasa(n, e) { return !e || (e === 'Incompletas' ? faltantes(n).length > 0 : n.estado === e); }
  function abrir() {
    C.mostrar('#v-blista');
    $('#bl-tabla').innerHTML = '<p class="vacio">Cargando notas…</p>';
    api.listar().then(function (d) { lista = d; pintar(); }).catch(function (e) { $('#bl-tabla').innerHTML = '<p class="vacio err">No se pudieron cargar las notas: ' + esc(e.message) + '</p>'; });
  }
  function pintar() {
    var q = $('#bl-q').value.trim().toLowerCase(), sec = $('#bl-sec').value;
    $$('#bl-estados button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.estado === filtroEstado)); b.querySelector('small').textContent = lista.filter(function (n) { return pasa(n, b.dataset.estado); }).length; });
    var xs = lista.filter(function (n) {
      return pasa(n, filtroEstado) && (!sec || n.seccion === sec) &&
        (!q || [n.titulo, n.resumen, n.categoria, n.subcategoria, n.tema, (n.tags || []).join(' ')].join(' ').toLowerCase().indexOf(q) >= 0);
    });
    var pub = lista.filter(function (n) { return n.estado === 'Publicado'; }).length;
    $('#bl-resumen').textContent = lista.length + ' notas · ' + pub + ' publicadas · ' + lista.filter(function (n) { return faltantes(n).length; }).length + ' para completar';
    Object.keys(marcadas).forEach(function (id) { if (!lista.some(function (n) { return n.id === id; })) delete marcadas[id]; });
    barraSel();
    if (!xs.length) { $('#bl-tabla').innerHTML = '<p class="vacio">' + (lista.length ? 'No hay notas con estos filtros.' : 'Todavía no hay notas. Tocá "+ Nueva nota".') + '</p>'; return; }
    $('#bl-tabla').innerHTML = '<table class="ct bl"><thead><tr><th class="bl-chk"><input type="checkbox" id="bl-todas" aria-label="Marcar todas"></th><th></th><th>Nota</th><th>Sección</th><th>Fecha</th><th>Para completar</th><th>Estado</th></tr></thead><tbody>' + xs.map(function (n) {
      var fx = faltantes(n);
      var foto = n.imagen ? '<img class="bl-th" src="' + esc(verFoto(n.imagen)) + '" alt="">' : '<span class="bl-th bl-ph">' + esc((n.titulo || '?')[0]) + '</span>';
      return '<tr data-id="' + esc(n.id) + '"' + (marcadas[n.id] ? ' class="sel"' : '') + '><td class="bl-chk"><input type="checkbox" data-sel="' + esc(n.id) + '"' + (marcadas[n.id] ? ' checked' : '') + ' aria-label="Marcar"></td><td>' + foto + '</td>' +
        '<td><b>' + esc(n.titulo || 'Sin título') + '</b><small>' + palabras(n.cuerpo) + ' palabras' + (n.destacada ? ' · ★ Destacada' : '') + '</small></td>' +
        '<td>' + esc(SECCION[n.seccion] || n.seccion) + '<small>' + esc(n.seccion === 'productos' ? n.subcategoria : n.tema) + '</small></td>' +
        '<td>' + fecha(n.fecha) + '</td>' +
        '<td>' + (fx.length ? '<div class="bl-falta">' + fx.map(function (x) { return '<span class="' + (x[1] ? 'grave' : '') + '">' + esc(x[0]) + '</span>'; }).join('') + '</div>' : '<span class="bl-ok">✓ Completa</span>') + '</td>' +
        '<td><span class="st st-' + esc((n.estado || '').toLowerCase()) + '">' + esc(n.estado) + '</span></td></tr>';
    }).join('') + '</tbody></table>';
    $$('#bl-tabla tr[data-id]').forEach(function (tr) { tr.addEventListener('click', function (e) { if (e.target.closest('.bl-chk')) return; editar(lista.find(function (n) { return n.id === tr.dataset.id; })); }); });
    $$('#bl-tabla [data-sel]').forEach(function (c) {
      c.addEventListener('change', function () { if (c.checked) marcadas[c.dataset.sel] = true; else delete marcadas[c.dataset.sel]; c.closest('tr').classList.toggle('sel', c.checked); barraSel(); });
    });
    $$('#bl-tabla td.bl-chk').forEach(function (td) { td.addEventListener('click', function (e) { if (e.target === td) { var c = td.querySelector('input'); c.checked = !c.checked; c.dispatchEvent(new Event('change')); } }); });
    var todas = $('#bl-todas'), visibles = xs.map(function (n) { return n.id; });
    todas.checked = visibles.length > 0 && visibles.every(function (id) { return marcadas[id]; });
    todas.addEventListener('change', function () { visibles.forEach(function (id) { if (todas.checked) marcadas[id] = true; else delete marcadas[id]; }); pintar(); });
  }
  function barraSel() {
    var ids = Object.keys(marcadas), bar = $('#bl-sel');
    bar.hidden = !ids.length;
    $('#bl-sel-n').textContent = ids.length === 1 ? '1 nota marcada' : ids.length + ' notas marcadas';
  }
  $('#bl-sel-limpiar').addEventListener('click', function () { marcadas = {}; pintar(); });
  $('#bl-sel-borrar').addEventListener('click', function () {
    var ids = Object.keys(marcadas); if (!ids.length) return;
    var ns = lista.filter(function (n) { return marcadas[n.id]; }), pub = ns.filter(function (n) { return n.estado === 'Publicado'; }).length;
    var txt = '¿Eliminar ' + (ns.length === 1 ? 'la nota "' + ns[0].titulo + '"' : 'estas ' + ns.length + ' notas') + '?' +
      (pub ? '\n\n' + (pub === 1 && ns.length === 1 ? 'Está publicada: se quita' : pub + (pub === 1 ? ' está publicada y se quita' : ' están publicadas y se quitan')) + ' del blog.' : '') + '\n\nNo se puede deshacer.';
    if (!confirm(txt)) return;
    var b = $('#bl-sel-borrar'); b.disabled = true; b.textContent = 'Eliminando…';
    api.borrarVarias(ids).then(function () {
      lista = lista.filter(function (n) { return !marcadas[n.id]; }); marcadas = {};
      C.toast(ids.length === 1 ? 'Nota eliminada.' : ids.length + ' notas eliminadas.'); C.publicar(); pintar();
    }).catch(function (er) { C.toast('No se pudieron eliminar: ' + er.message, true); })
      .then(function () { b.disabled = false; b.textContent = 'Eliminar'; });
  });

  /* ---------- editor ---------- */
  var f = $('#f-nota'), actual = null, nuevo = false, sucio = false, imagen = '', slugTocado = false, vista = 'escribir';
  var CAMPOS = ['titulo', 'resumen', 'slug', 'seccion', 'categoria', 'subcategoria', 'tema', 'autor', 'fecha', 'imagen_alt', 'imagen_pos', 'cuerpo', 'estado'];
  f.categoria.innerHTML = Object.keys(P.categorias).map(function (c) { return '<option>' + esc(c) + '</option>'; }).join('');
  f.autor.innerHTML = Object.keys(B.autores).map(function (k) { return '<option value="' + esc(k) + '">' + esc(B.autores[k]) + '</option>'; }).join('');
  function subs() {
    var v = f.subcategoria.value;
    f.subcategoria.innerHTML = (P.categorias[f.categoria.value] || []).map(function (s) { return '<option>' + esc(s) + '</option>'; }).join('');
    if (v && (P.categorias[f.categoria.value] || []).indexOf(v) >= 0) f.subcategoria.value = v;
  }
  function temas() {
    var v = f.tema.value, xs = f.seccion.value === 'opinion' ? B.temas_opinion : B.temas;
    f.tema.innerHTML = xs.map(function (t) { return '<option>' + esc(t) + '</option>'; }).join('');
    if (xs.indexOf(v) >= 0) f.tema.value = v;
  }
  function seccionUI() {
    var s = f.seccion.value;
    $('#be-cat-l').hidden = $('#be-sub-l').hidden = s !== 'productos';
    $('#be-tema-l').hidden = s === 'productos';
    $('#be-autor-l').hidden = s !== 'opinion';
    temas();
  }
  f.categoria.addEventListener('change', subs);
  f.seccion.addEventListener('change', seccionUI);

  function editar(n) {
    nuevo = !n;
    actual = n ? JSON.parse(JSON.stringify(n)) : { seccion: 'productos', categoria: Object.keys(P.categorias)[0], estado: 'Borrador', fecha: new Date().toISOString().slice(0, 10), tags: [], destacada: false, cuerpo: '' };
    f.seccion.value = actual.seccion; f.categoria.value = actual.categoria || Object.keys(P.categorias)[0]; subs(); seccionUI();
    CAMPOS.forEach(function (k) { if (f[k]) f[k].value = actual[k] == null ? '' : String(actual[k]).slice(0, k === 'fecha' ? 10 : 99999); });
    if (!actual.autor) f.autor.value = Object.keys(B.autores)[0];
    f.tags.value = (actual.tags || []).join(', ');
    f.destacada.checked = !!actual.destacada;
    imagen = actual.imagen || ''; slugTocado = !nuevo; sucio = false;
    f.slug.readOnly = !nuevo && actual.estado === 'Publicado';
    $('#be-slug-nota').textContent = f.slug.readOnly ? 'Ya está publicada: la dirección no se cambia para no romper los enlaces.' : 'Se arma sola con el título. Solo minúsculas, números y guiones.';
    $('#be-titulo').textContent = nuevo ? 'Nueva nota' : (actual.titulo || 'Nota');
    $('#be-sub').textContent = nuevo ? 'Empezá por el título; podés guardarla como Borrador y seguir después.' : SECCION[actual.seccion] + ' · ' + fecha(actual.fecha);
    $('#be-borrar').hidden = nuevo; $('#be-msg').textContent = '';
    verLink(); cambiarVista('escribir'); pintarFoto(); revisar();
    C.mostrar('#v-beditor');
  }
  function verLink() {
    var a = $('#be-ver'); a.hidden = nuevo || !actual || actual.estado !== 'Publicado';
    if (!a.hidden) a.href = '../blog/' + actual.slug + '/';
  }

  f.titulo.addEventListener('input', function () { if (!slugTocado && !f.slug.readOnly) f.slug.value = C.slugify(f.titulo.value); });
  f.slug.addEventListener('input', function () { slugTocado = true; f.slug.value = f.slug.value.toLowerCase().replace(/[^a-z0-9-]/g, '-'); });
  f.addEventListener('input', function () { sucio = true; revisar(); });
  f.addEventListener('change', revisar);

  function datos() {
    var n = Object.assign({}, actual);
    CAMPOS.forEach(function (k) { n[k] = f[k].value; });
    ['titulo', 'resumen', 'slug', 'imagen_alt'].forEach(function (k) { n[k] = n[k].trim(); });
    n.slug = C.slugify(n.slug || n.titulo);
    n.tags = f.tags.value.split(',').map(function (t) { return t.trim().toLowerCase(); }).filter(Boolean).slice(0, 6);
    n.destacada = f.destacada.checked; n.imagen = imagen;
    if (n.seccion === 'productos') { n.tema = ''; n.autor = ''; } else { n.categoria = ''; n.subcategoria = ''; if (n.seccion !== 'opinion') n.autor = ''; }
    n.fecha = n.fecha || new Date().toISOString().slice(0, 10);
    return n;
  }
  function revisar() {
    $$('.count', f).forEach(function (c) { var el = f[c.dataset.for]; c.textContent = el.value.length + ' / ' + el.maxLength; });
    var n = datos(), fx = faltantes(n), w = palabras(n.cuerpo);
    $('#be-palabras').textContent = w + ' palabras · ' + Math.max(2, Math.ceil(w / 200)) + ' min de lectura';
    $('#be-check').innerHTML = fx.length ? fx.map(function (x) { return '<li class="' + (x[1] ? 'grave' : '') + '">' + esc(x[0]) + '</li>'; }).join('') : '<li class="ok">Tiene todo: título, resumen, foto, texto con subtítulos y etiquetas.</li>';
    if (vista === 'previa') previa();
  }

  /* ---------- texto: barra de formato ---------- */
  var ta = $('#be-cuerpo');
  function envolver(antes, despues, ejemplo) {
    var a = ta.selectionStart, b = ta.selectionEnd, sel = ta.value.slice(a, b) || ejemplo;
    ta.setRangeText(antes + sel + despues, a, b, 'end');
    ta.selectionStart = a + antes.length; ta.selectionEnd = a + antes.length + sel.length;
    ta.focus(); ta.dispatchEvent(new Event('input', { bubbles: true }));
  }
  function linea(prefijo, ejemplo) {
    var a = ta.selectionStart, b = ta.selectionEnd, v = ta.value;
    var ini = v.lastIndexOf('\n', a - 1) + 1, sel = v.slice(ini, b) || ejemplo;
    var txt = sel.split('\n').map(function (l, i) { return (typeof prefijo === 'function' ? prefijo(i) : prefijo) + l.replace(/^(#{2,3} |- |\d+\. |> )/, ''); }).join('\n');
    ta.setRangeText(txt, ini, b, 'end');
    ta.focus(); ta.dispatchEvent(new Event('input', { bubbles: true }));
  }
  $$('#be-barra [data-md]').forEach(function (b) {
    b.addEventListener('click', function () {
      var m = b.dataset.md;
      if (m === 'b') envolver('**', '**', 'texto en negrita');
      else if (m === 'i') envolver('*', '*', 'texto en cursiva');
      else if (m === 'h2') linea('## ', 'Subtítulo');
      else if (m === 'h3') linea('### ', 'Subtítulo chico');
      else if (m === 'ul') linea('- ', 'Elemento de la lista');
      else if (m === 'ol') linea(function (i) { return (i + 1) + '. '; }, 'Primer paso');
      else if (m === 'tip') linea('> ', '**Consejo:** texto del recuadro.');
      else if (m === 'link') {
        var u = prompt('Pegá la dirección del enlace (https://… o una página del sitio, por ejemplo ../que-es-el-mate/)');
        if (u) envolver('[', '](' + u.trim() + ')', 'texto del enlace');
      }
    });
  });

  /* ---------- vista previa (mismas reglas que el blog) ---------- */
  function inline(t) {
    return esc(t).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/(^|[^\w*])\*([^*\s][^*]*?)\*(?![\w*])/g, '$1<em>$2</em>')
      .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="#" title="$2">$1</a>');
  }
  var IMG = /^!\[([^\]]*)\]\((\S+?)(?:\s+"([^"]*)")?\)\s*$/;
  function markdown(src) {
    var L = String(src || '').replace(/\r/g, '').split('\n'), out = [], i = 0;
    while (i < L.length) {
      var l = L[i];
      if (!l.trim()) { i++; continue; }
      if (/^## /.test(l)) { out.push('<h2>' + inline(l.slice(3)) + '</h2>'); i++; continue; }
      if (/^### /.test(l)) { out.push('<h3>' + inline(l.slice(4)) + '</h3>'); i++; continue; }
      if (IMG.test(l)) {
        var figs = [];
        while (i < L.length && IMG.test(L[i])) { var m = L[i].match(IMG); figs.push('<figure><img src="' + esc(verFoto(m[2])) + '" alt="' + esc(m[1]) + '">' + (m[3] ? '<figcaption>' + inline(m[3]) + '</figcaption>' : '') + '</figure>'); i++; }
        out.push('<div class="figs' + (figs.length > 1 ? ' duo' : '') + '">' + figs.join('') + '</div>'); continue;
      }
      if (/^>/.test(l)) { var q = []; while (i < L.length && /^>/.test(L[i])) { q.push(L[i].replace(/^>\s?/, '')); i++; } out.push('<aside class="tip"><p>' + inline(q.join(' ')) + '</p></aside>'); continue; }
      if (/^\|/.test(l)) {
        var rows = []; while (i < L.length && /^\|/.test(L[i])) { rows.push(L[i].trim().replace(/^\||\|$/g, '').split('|').map(function (c) { return c.trim(); })); i++; }
        var body = rows.slice(1).filter(function (r) { return !r.every(function (c) { return /^:?-+:?$/.test(c); }); });
        out.push('<table><thead><tr>' + rows[0].map(function (c) { return '<th>' + inline(c) + '</th>'; }).join('') + '</tr></thead><tbody>' + body.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + inline(c) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table>'); continue;
      }
      if (/^- /.test(l)) { var ul = []; while (i < L.length && /^- /.test(L[i])) { ul.push('<li>' + inline(L[i].slice(2)) + '</li>'); i++; } out.push('<ul>' + ul.join('') + '</ul>'); continue; }
      if (/^\d+\. /.test(l)) { var ol = []; while (i < L.length && /^\d+\. /.test(L[i])) { ol.push('<li>' + inline(L[i].replace(/^\d+\. /, '')) + '</li>'); i++; } out.push('<ol>' + ol.join('') + '</ol>'); continue; }
      var buf = []; while (i < L.length && L[i].trim() && !/^(#{2,3} |> |\||- |\d+\. |!\[)/.test(L[i])) { buf.push(L[i].trim()); i++; }
      out.push('<p>' + inline(buf.join(' ')) + '</p>');
    }
    return out.join('\n');
  }
  function previa() {
    var n = datos();
    $('#be-previa').innerHTML = (imagen ? '<img class="pv-portada" src="' + esc(verFoto(imagen)) + '" alt="">' : '') +
      '<h1>' + esc(n.titulo || 'Título de la nota') + '</h1><p class="pv-resumen">' + esc(n.resumen) + '</p>' + (markdown(n.cuerpo) || '<p class="muted">Todavía no hay texto.</p>');
  }
  function cambiarVista(v) {
    vista = v;
    $$('.be-tabs [data-vista]').forEach(function (b) { b.classList.toggle('on', b.dataset.vista === v); });
    ta.hidden = v !== 'escribir'; $('#be-barra').hidden = v !== 'escribir'; $('#be-previa').hidden = v !== 'previa';
    if (v === 'previa') previa();
  }
  $$('.be-tabs [data-vista]').forEach(function (b) { b.addEventListener('click', function () { cambiarVista(b.dataset.vista); }); });

  /* ---------- fotos ---------- */
  function carpeta() { return (C.slugify(f.slug.value || f.titulo.value) || 'nota') + '/'; }
  function subirFoto(file) {
    if (!file || !/^image\//.test(file.type)) return Promise.reject(new Error('Elegí una imagen (JPG, PNG o WebP).'));
    return C.achicar(file, true).then(function (blob) { return api.subir(carpeta() + Date.now() + '-um.jpg', blob); });
  }
  function pintarFoto() {
    $('#be-foto').innerHTML = imagen ? '<figure><img src="' + esc(verFoto(imagen)) + '" alt="" style="object-position:' + esc(f.imagen_pos.value || 'center') + '"><button type="button" id="be-foto-del">Quitar</button></figure>' : '';
    var del = $('#be-foto-del'); if (del) del.addEventListener('click', function () { imagen = ''; sucio = true; pintarFoto(); revisar(); });
  }
  f.imagen_pos.addEventListener('change', pintarFoto);
  var drop = $('#be-foto-drop'), inp = drop.querySelector('input');
  function portada(file) {
    drop.classList.add('busy'); drop.querySelector('b').textContent = 'Subiendo…';
    subirFoto(file).then(function (u) { imagen = u; sucio = true; pintarFoto(); revisar(); C.toast('Foto subida. Acordate de guardar.'); })
      .catch(function (e) { C.toast('No se pudo subir: ' + e.message, true); })
      .then(function () { drop.classList.remove('busy'); drop.querySelector('b').textContent = 'Subir foto de portada'; inp.value = ''; });
  }
  inp.addEventListener('change', function () { portada(inp.files[0]); });
  ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('over'); }); });
  ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('over'); }); });
  drop.addEventListener('drop', function (e) { portada(e.dataTransfer.files[0]); });

  var ftx = $('#be-foto-texto');
  ftx.addEventListener('change', function () {
    var file = ftx.files[0]; if (!file) return;
    var pos = ta.selectionStart, lbl = ftx.parentNode;
    lbl.classList.add('busy');
    subirFoto(file).then(function (u) {
      var alt = (prompt('Describí la foto en pocas palabras (para Google y accesibilidad):', '') || '').replace(/[\[\]]/g, '').trim() || 'Foto';
      var pie = (prompt('Epígrafe opcional (el texto que va debajo de la foto). Dejalo vacío si no querés.', '') || '').replace(/"/g, "'").trim();
      var v = ta.value, antes = v.slice(0, pos), md = '![' + alt + '](' + u + (pie ? ' "' + pie + '"' : '') + ')';
      var pre = !antes || /\n\n$/.test(antes) ? '' : /\n$/.test(antes) ? '\n' : '\n\n';
      ta.setRangeText(pre + md + '\n\n', pos, pos, 'end'); ta.focus(); ta.dispatchEvent(new Event('input', { bubbles: true }));
      C.toast('Foto agregada al texto.');
    }).catch(function (e) { C.toast('No se pudo subir: ' + e.message, true); })
      .then(function () { lbl.classList.remove('busy'); ftx.value = ''; });
  });

  /* ---------- guardar / borrar ---------- */
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var n = datos(), m = $('#be-msg');
    if (!n.titulo || !n.slug) { m.className = 'msg err'; m.textContent = 'Poné el título de la nota.'; return; }
    if (n.estado === 'Publicado') {
      var graves = faltantes(n).filter(function (x) { return x[1]; });
      if (graves.length) { m.className = 'msg err'; m.textContent = 'Para publicarla falta: ' + graves.map(function (x) { return x[0].toLowerCase(); }).join(', ') + '. Podés guardarla como Borrador mientras tanto.'; return; }
    }
    if (lista.some(function (x) { return x.slug === n.slug && x.id !== n.id; })) { m.className = 'msg err'; m.textContent = 'Ya hay otra nota con esa dirección. Cambiá el título o la dirección.'; return; }
    delete n.creado; if (nuevo) delete n.id;
    n.actualizado = new Date().toISOString();
    $('#be-guardar').disabled = true; m.className = 'msg'; m.textContent = 'Guardando…';
    api.guardar(n, nuevo).then(function (g) {
      var i = lista.findIndex(function (x) { return x.id === g.id; }); if (i >= 0) lista[i] = g; else lista.unshift(g);
      actual = g; nuevo = false; sucio = false; slugTocado = true;
      f.slug.readOnly = g.estado === 'Publicado';
      $('#be-titulo').textContent = g.titulo; $('#be-sub').textContent = SECCION[g.seccion] + ' · ' + fecha(g.fecha); $('#be-borrar').hidden = false; verLink();
      C.publicar(); m.className = 'msg ok'; m.textContent = g.estado === 'Publicado' ? 'Guardada. Se ve en el blog en unos minutos.' : 'Guardada como borrador (no se ve en el sitio).';
    }).catch(function (er) { m.className = 'msg err'; m.textContent = 'No se pudo guardar: ' + er.message; })
      .then(function () { $('#be-guardar').disabled = false; });
  });
  $('#be-volver').addEventListener('click', function () { if (sucio && !confirm('Tenés cambios sin guardar. ¿Salir igual?')) return; C.mostrar('#v-blista'); pintar(); });
  $('#be-borrar').addEventListener('click', function () {
    if (!confirm('¿Eliminar la nota "' + actual.titulo + '"? Si está publicada, se quita del blog.')) return;
    api.borrar(actual.id).then(function () { lista = lista.filter(function (x) { return x.id !== actual.id; }); C.toast('Nota eliminada.'); C.publicar(); C.mostrar('#v-blista'); pintar(); })
      .catch(function (er) { C.toast('No se pudo eliminar: ' + er.message, true); });
  });

  window.PanelBlog = { abrir: abrir };
})();
