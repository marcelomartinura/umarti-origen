/* Panel · módulo Viajes: lista y editor de destinos (tabla "destinos" y bucket "viajes" en Supabase) */
(function () {
  'use strict';
  var C = window.PanelComun; if (!C) return;
  var $ = C.$, $$ = C.$$, esc = C.esc, V = C.P.viajes, BUCKET = 'viajes';
  var CAMPOS = [
    ['por_que', 'Por qué ir', 'Un texto descriptivo sobre el destino: qué lo hace especial, su personalidad, para quién es.', 6],
    ['cuando_ir', 'Cuándo ir', 'Mejor época, clima por estación, temporada alta y baja, eventos.', 4],
    ['que_comer', 'Qué comer', 'Platos, bebidas y lugares típicos. Una lista con - funciona muy bien.', 4],
    ['donde_alojarse', 'Dónde alojarse', 'Barrios o zonas recomendadas y para quién conviene cada una.', 4],
    ['como_llegar', 'Cómo llegar', 'Aeropuertos, rutas, buses, distancias.', 3],
    ['como_moverse', 'Cómo moverse', 'Transporte público, taxis y apps, bici, a pie, auto.', 3],
    ['que_hacer', 'Qué hacer', 'Escribí cada lugar como "- **Nombre**: descripción" y se muestran como tarjetas.', 6],
    ['consejos', 'Consejos para tu viaje', 'Datos prácticos: pagos, seguridad, horarios, reservas.', 4]
  ];

  /* ---------- API ---------- */
  var demo = C.demo, sb = C.sb, datosDemo = [];
  function ok(r) { if (r.error) throw r.error; return r.data; }
  var api = demo ? {
    listar: function () { return Promise.resolve(datosDemo.slice()); },
    guardar: function (d, nuevo) { d.actualizado = new Date().toISOString(); if (nuevo) datosDemo.push(d); else datosDemo = datosDemo.map(function (o) { return o.id === d.id ? d : o; }); return Promise.resolve(d); },
    borrar: function (id) { datosDemo = datosDemo.filter(function (o) { return o.id !== id; }); return Promise.resolve(); },
    subir: function (ruta, blob) { return Promise.resolve(URL.createObjectURL(blob)); }
  } : {
    listar: function () { return sb.from('destinos').select('*').order('orden').order('creado').then(ok); },
    guardar: function (d, nuevo) { var q = nuevo ? sb.from('destinos').insert(d) : sb.from('destinos').update(d).eq('id', d.id); return q.select().single().then(ok); },
    borrar: function (id) { return sb.from('destinos').delete().eq('id', id).then(ok); },
    subir: function (ruta, blob, tipo) {
      return sb.storage.from(BUCKET).upload(ruta, blob, { contentType: tipo || 'image/jpeg', upsert: false }).then(function (r) {
        if (r.error) throw r.error;
        return sb.storage.from(BUCKET).getPublicUrl(ruta).data.publicUrl;
      });
    }
  };
  if (demo) {
    datosDemo = [{ id: 'd1', slug: 'buenos-aires', pais: 'Argentina', ciudad: 'Buenos Aires', region: 'Ciudad Autónoma de Buenos Aires', resumen: 'Barrios con identidad propia, cafés notables, tango y una de las escenas gastronómicas más intensas del continente.', tags: ['Cultura', 'Gastronomía', 'Urbano'], foto: '', foto_pos: 'center', dias: '3 a 4 días', mejor_epoca: 'Primavera y otoño', presupuesto: 'Medio', por_que: 'Buenos Aires es una ciudad para caminar.\n\nEs también la puerta de entrada a Argentina.', cuando_ir: '**Mejor época:** primavera y otoño.', que_comer: '- Asado\n- Pizza porteña\n- Medialunas', donde_alojarse: '- **Palermo**: parques y bares.', como_llegar: 'Ezeiza y Aeroparque.', como_moverse: 'Subte y colectivos con SUBE.', que_hacer: '- **San Telmo**: feria de los domingos.\n- **Recoleta**: cementerio y museos.', consejos: '- Se cena tarde.', faqs: [{ q: '¿Cuántos días?', a: '3 a 4 días.' }], detalle: [], notas: ['que-es-el-mate'], productos: [], categorias_tienda: ['Café, Té y Mate'], estado: 'Publicado', orden: 0, actualizado: new Date().toISOString() }];
  }

  /* ---------- lista ---------- */
  var lista = [];
  function abrir() {
    C.mostrar('#v-vlista');
    $('#vl-tabla').innerHTML = '<p class="vacio">Cargando destinos…</p>';
    api.listar().then(function (d) { lista = d; pintar(); }).catch(function (e) { $('#vl-tabla').innerHTML = '<p class="vacio err">No se pudieron cargar los destinos: ' + esc(e.message) + '</p>'; });
  }
  function pintar() {
    var q = $('#vl-q').value.trim().toLowerCase();
    var xs = lista.filter(function (d) { return !q || [d.ciudad, d.region, d.pais].join(' ').toLowerCase().indexOf(q) >= 0; });
    var pub = lista.filter(function (d) { return d.estado === 'Publicado'; }).length;
    $('#vl-resumen').textContent = lista.length + (lista.length === 1 ? ' destino' : ' destinos') + ' · ' + pub + ' publicados';
    if (!xs.length) { $('#vl-tabla').innerHTML = '<p class="vacio">' + (lista.length ? 'No hay destinos con esa búsqueda.' : 'Todavía no cargaste destinos. Tocá "+ Nuevo destino".') + '</p>'; return; }
    $('#vl-tabla').innerHTML = '<table><thead><tr><th></th><th>Destino</th><th>Tags</th><th>Secciones</th><th>Estado</th></tr></thead><tbody>' + xs.map(function (d) {
      var llenas = CAMPOS.filter(function (c) { return (d[c[0]] || '').trim(); }).length;
      return '<tr data-id="' + esc(d.id) + '"><td class="th">' + (d.foto ? '<img src="' + esc(d.foto) + '" alt="">' : '<span class="ph">' + esc((d.ciudad || '?')[0]) + '</span>') + '</td>' +
        '<td><b>' + esc(d.ciudad) + '</b><small>' + esc([d.region, d.pais].filter(Boolean).join(', ')) + '</small></td>' +
        '<td>' + (d.tags || []).map(function (t) { return '<span class="pill">' + esc(t) + '</span>'; }).join(' ') + '</td>' +
        '<td><small>' + llenas + ' de ' + CAMPOS.length + (d.detalle && d.detalle.length ? ' · ' + d.detalle.length + ' bloques' : '') + '</small></td>' +
        '<td><span class="est est-' + esc((d.estado || '').toLowerCase()) + '">' + esc(d.estado) + '</span></td></tr>';
    }).join('') + '</tbody></table>';
    $$('#vl-tabla tr[data-id]').forEach(function (tr) { tr.addEventListener('click', function () { editar(lista.find(function (d) { return d.id === tr.dataset.id; })); }); });
  }
  $('#vl-q').addEventListener('input', pintar);
  $('#vb-nuevo').addEventListener('click', function () { editar(null); });

  /* ---------- editor ---------- */
  var f = $('#f-dest'), actual = null, nuevo = false, foto = '', faqs = [], bloques = [], slugManual = false, sucio = false;
  $('#vl-paises').innerHTML = V.paises.map(function (p) { return '<option value="' + esc(p) + '">'; }).join('');
  f.presupuesto.innerHTML += V.presupuestos.map(function (p) { return '<option>' + p + '</option>'; }).join('');
  $('#ve-tags').innerHTML = V.tipos.map(function (t) { return '<label class="chk"><input type="checkbox" value="' + esc(t) + '"> ' + esc(t) + '</label>'; }).join('');
  $('#ve-cats').innerHTML = Object.keys(C.P.categorias).map(function (c) { return '<label class="chk"><input type="checkbox" value="' + esc(c) + '"> ' + esc(c) + '</label>'; }).join('');
  $('#ve-notas').innerHTML = V.notas.map(function (n) { return '<label class="chk" data-t="' + esc(n.titulo.toLowerCase()) + '"><input type="checkbox" value="' + esc(n.slug) + '"> ' + esc(n.titulo) + '</label>'; }).join('');
  $('#ve-notas-q').addEventListener('input', function () { var q = this.value.toLowerCase(); $$('#ve-notas label').forEach(function (l) { l.hidden = q && l.dataset.t.indexOf(q) < 0; }); });

  /* campos de texto con botones de formato */
  $('#ve-campos').innerHTML = CAMPOS.map(function (c) {
    return '<div class="ve-campo"><div class="ve-campo-h"><b>' + c[1] + '</b><span class="ve-tools" data-for="' + c[0] + '">' +
      '<button type="button" data-fmt="b" title="Negrita"><b>B</b></button><button type="button" data-fmt="i" title="Cursiva"><i>I</i></button>' +
      '<button type="button" data-fmt="ul" title="Lista">• Lista</button><button type="button" data-fmt="h" title="Subtítulo">Subtítulo</button>' +
      '<button type="button" data-fmt="a" title="Link">Link</button></span></div>' +
      '<textarea name="' + c[0] + '" rows="' + c[3] + '" placeholder="' + esc(c[2]) + '"></textarea></div>';
  }).join('');
  function formato(ta, fmt) {
    var a = ta.selectionStart, b = ta.selectionEnd, v = ta.value, sel = v.slice(a, b), out;
    if (fmt === 'b') out = '**' + (sel || 'texto') + '**';
    else if (fmt === 'i') out = '*' + (sel || 'texto') + '*';
    else if (fmt === 'a') { var u = prompt('Pegá el link (https://…)', 'https://'); if (!u) return; out = '[' + (sel || 'texto del link') + '](' + u + ')'; }
    else if (fmt === 'ul') out = (sel || 'elemento').split('\n').map(function (l) { return l.replace(/^[-•*]\s*/, '') ? '- ' + l.replace(/^[-•*]\s*/, '') : l; }).join('\n');
    else if (fmt === 'h') out = '### ' + (sel || 'Subtítulo').replace(/^#+\s*/, '');
    var pre = (fmt === 'ul' || fmt === 'h') && a > 0 && v[a - 1] !== '\n' ? '\n' : '';
    ta.value = v.slice(0, a) + pre + out + v.slice(b);
    ta.focus(); ta.selectionStart = a + pre.length; ta.selectionEnd = a + pre.length + out.length;
    sucio = true; indice();
  }
  f.addEventListener('click', function (e) {
    var bt = e.target.closest('[data-fmt]'); if (!bt) return;
    var tools = bt.closest('[data-for]'), ta = tools.dataset.for.indexOf('#') === 0 ? $(tools.dataset.for) : f[tools.dataset.for];
    formato(ta, bt.dataset.fmt);
  });

  function marcados(sel) { return $$(sel + ' input:checked').map(function (i) { return i.value; }); }
  function marcar(sel, vals) { $$(sel + ' input').forEach(function (i) { i.checked = (vals || []).indexOf(i.value) >= 0; }); }

  function editar(d) {
    nuevo = !d;
    actual = d ? JSON.parse(JSON.stringify(d)) : { id: demo ? 'n' + Date.now() : null, pais: 'Argentina', estado: 'Borrador', tags: [], faqs: [], detalle: [], notas: [], productos: [], categorias_tienda: [], foto_pos: 'center' };
    ['pais', 'ciudad', 'region', 'slug', 'resumen', 'dias', 'presupuesto', 'mejor_epoca', 'clima', 'requisitos', 'requisitos_fuente', 'moneda', 'corriente', 'huso', 'unidades', 'talles', 'foto_pos', 'estado'].concat(CAMPOS.map(function (c) { return c[0]; })).forEach(function (k) { if (f[k]) f[k].value = actual[k] || (k === 'foto_pos' ? 'center' : ''); });
    marcar('#ve-tags', actual.tags); marcar('#ve-cats', actual.categorias_tienda); marcar('#ve-notas', actual.notas);
    foto = actual.foto || ''; faqs = (actual.faqs || []).slice(); bloques = (actual.detalle || []).slice();
    slugManual = !!actual.slug; sucio = false;
    $('#ve-titulo').textContent = nuevo ? 'Nuevo destino' : actual.ciudad;
    $('#ve-sub').textContent = nuevo ? 'Completá lo que tengas: podés guardarlo como borrador y seguir después.' : 'Última edición: ' + new Date(actual.actualizado).toLocaleString('es-AR');
    $('#ve-borrar').hidden = nuevo; $('#ve-msg').textContent = '';
    $('#ve-ver').hidden = actual.estado !== 'Publicado'; $('#ve-ver').href = '../viajes/' + claveP(actual.pais) + '/' + actual.slug + '/';
    pintarFoto(); pintarFaqs(); pintarBloques(); productos(); actualizarSlug(); indice(); contar();
    C.mostrar('#v-veditor');
  }
  function productos() {
    $('#ve-prods').innerHTML = '<small class="muted">Cargando productos…</small>';
    C.productos().then(function (ps) {
      $('#ve-prods').innerHTML = ps.length ? ps.map(function (p) { return '<label class="chk"><input type="checkbox" value="' + esc(p.codigo) + '"> <b>' + esc(p.codigo) + '</b> ' + esc(p.nombre) + (p.estado && p.estado !== 'Publicado' ? ' <small>(' + esc(p.estado) + ')</small>' : '') + '</label>'; }).join('') : '<small class="muted">Todavía no hay productos.</small>';
      marcar('#ve-prods', actual.productos);
    }).catch(function () { $('#ve-prods').innerHTML = '<small class="muted">No se pudieron cargar los productos.</small>'; });
  }
  function claveP(p) { return C.slugify(p || 'pais'); }
  function actualizarSlug() {
    if (!slugManual) f.slug.value = C.slugify(f.ciudad.value);
    $('#ve-slug-pre').textContent = 'viajes/' + claveP(f.pais.value) + '/';
    $('#ve-det-leg').textContent = 'Conocé ' + (f.ciudad.value || 'el destino') + ' en detalle';
  }
  f.ciudad.addEventListener('input', actualizarSlug); f.pais.addEventListener('input', actualizarSlug);
  f.slug.addEventListener('input', function () { slugManual = true; });
  function contar() { $$('#f-dest .count').forEach(function (c) { var el = f[c.dataset.for]; c.textContent = el.value.length + ' / ' + el.maxLength; }); }
  f.addEventListener('input', function () { sucio = true; contar(); indice(); });

  function indice() {
    var items = [['Por qué ir', 'por_que'], ['Cuándo ir', 'cuando_ir'], ['Qué comer', 'que_comer'], ['Dónde alojarse', 'donde_alojarse'], ['Cómo llegar', 'como_llegar'], ['Cómo moverse', 'como_moverse'], ['Qué hacer', 'que_hacer'], ['Consejos', 'consejos']]
      .map(function (x) { return [x[0], !!f[x[1]].value.trim()]; });
    items.splice(1, 0, ['Datos prácticos', !!(f.moneda.value || f.corriente.value || f.unidades.value || f.talles.value).trim()]);
    items.splice(3, 0, ['Requisitos para viajar', !!f.requisitos.value.trim()]);
    items.push(['En detalle (página aparte)', bloques.length > 0]);
    items.push(['En la Tienda', marcados('#ve-cats').length + marcados('#ve-prods').length > 0]);
    items.push(['Preguntas frecuentes', faqs.some(function (q) { return q.q; })]);
    $('#ve-indice').innerHTML = items.map(function (x) { return '<li class="' + (x[1] ? 'ok' : '') + '">' + x[0] + '</li>'; }).join('');
  }

  /* foto principal */
  function achicarYSubir(file, carpeta) {
    var base = (f.slug.value || 'destino') + '/' + carpeta + '/' + Date.now();
    if (/^video\//.test(file.type)) {
      if (file.size > 50 * 1024 * 1024) return Promise.reject(new Error('El video pesa más de 50 MB. Subilo a YouTube y pegá el link.'));
      return api.subir(base + '.' + (file.name.split('.').pop() || 'mp4').toLowerCase(), file, file.type);
    }
    return C.achicar(file).then(function (blob) { return api.subir(base + '.jpg', blob, 'image/jpeg'); });
  }
  function pintarFoto() {
    $('#ve-foto').innerHTML = foto ? '<figure><img src="' + esc(foto) + '" alt="" style="object-position:' + esc(f.foto_pos.value) + '"><button type="button" id="ve-foto-del">Quitar</button></figure>' : '';
    var del = $('#ve-foto-del'); if (del) del.addEventListener('click', function () { foto = ''; sucio = true; pintarFoto(); });
  }
  f.foto_pos.addEventListener('change', pintarFoto);
  var fd = $('#ve-foto-drop');
  fd.querySelector('input').addEventListener('change', function () {
    var file = this.files[0]; if (!file) return;
    fd.classList.add('busy'); fd.querySelector('b').textContent = 'Subiendo…';
    achicarYSubir(file, 'principal').then(function (u) { foto = u; sucio = true; pintarFoto(); C.toast('Foto subida. Acordate de guardar.'); })
      .catch(function (e) { C.toast('No se pudo subir: ' + e.message, true); })
      .then(function () { fd.classList.remove('busy'); fd.querySelector('b').textContent = 'Subir foto principal'; fd.querySelector('input').value = ''; });
  });

  /* preguntas frecuentes */
  function pintarFaqs() {
    $('#ve-faqs').innerHTML = faqs.length ? faqs.map(function (q, i) {
      return '<div class="ve-faq"><input data-q="' + i + '" value="' + esc(q.q) + '" placeholder="Pregunta"><textarea data-a="' + i + '" rows="2" placeholder="Respuesta">' + esc(q.a) + '</textarea><button type="button" class="x" data-del="' + i + '" aria-label="Quitar pregunta">×</button></div>';
    }).join('') : '<p class="muted">Sin preguntas todavía.</p>';
  }
  $('#ve-faqs').addEventListener('input', function (e) {
    var t = e.target; if (t.dataset.q) faqs[+t.dataset.q].q = t.value; if (t.dataset.a) faqs[+t.dataset.a].a = t.value;
  });
  $('#ve-faqs').addEventListener('click', function (e) { var b = e.target.closest('[data-del]'); if (b) { faqs.splice(+b.dataset.del, 1); sucio = true; pintarFaqs(); indice(); } });
  $('#ve-faq-add').addEventListener('click', function () { faqs.push({ q: '', a: '' }); pintarFaqs(); $('#ve-faqs [data-q="' + (faqs.length - 1) + '"]').focus(); });

  /* bloques "en detalle" */
  var NOMBRE = { texto: 'Texto', foto: 'Foto', video: 'Video' };
  function pintarBloques() {
    $('#ve-bloques').innerHTML = bloques.length ? bloques.map(function (b, i) {
      var cuerpo = '';
      if (b.tipo === 'texto') cuerpo = '<input data-k="titulo" value="' + esc(b.titulo || '') + '" placeholder="Subtítulo (opcional)">' +
        '<span class="ve-tools" data-for="#ve-b' + i + '"><button type="button" data-fmt="b"><b>B</b></button><button type="button" data-fmt="i"><i>I</i></button><button type="button" data-fmt="ul">• Lista</button><button type="button" data-fmt="a">Link</button></span>' +
        '<textarea id="ve-b' + i + '" data-k="texto" rows="5" placeholder="Escribí el texto…">' + esc(b.texto || '') + '</textarea>';
      else if (b.tipo === 'foto') cuerpo = (b.url ? '<img class="ve-b-img" src="' + esc(b.url) + '" alt="">' : '<label class="drop sm"><input type="file" accept="image/*" data-up="' + i + '" hidden><b>Elegir foto</b></label>') +
        '<input data-k="pie" value="' + esc(b.pie || '') + '" placeholder="Epígrafe (opcional)">';
      else cuerpo = '<input data-k="url" value="' + esc(b.url || '') + '" placeholder="Link de YouTube o Vimeo">' +
        '<label class="drop sm"><input type="file" accept="video/mp4,video/webm,video/quicktime" data-up="' + i + '" hidden><b>' + (b.url && !/youtu|vimeo/.test(b.url) ? 'Video subido · cambiar' : 'O subir un video (hasta 50 MB)') + '</b></label>' +
        '<input data-k="pie" value="' + esc(b.pie || '') + '" placeholder="Epígrafe (opcional)">';
      return '<div class="ve-bloque" data-i="' + i + '"><div class="ve-bloque-h"><b>' + NOMBRE[b.tipo] + '</b><span>' +
        '<button type="button" data-mv="-1"' + (i === 0 ? ' disabled' : '') + ' aria-label="Subir">↑</button><button type="button" data-mv="1"' + (i === bloques.length - 1 ? ' disabled' : '') + ' aria-label="Bajar">↓</button>' +
        '<button type="button" data-quitar aria-label="Quitar">×</button></span></div>' + cuerpo + '</div>';
    }).join('') : '<p class="muted">Todavía no hay bloques.</p>';
  }
  $$('[data-bloque]').forEach(function (b) { b.addEventListener('click', function () { bloques.push({ tipo: b.dataset.bloque }); sucio = true; pintarBloques(); indice(); }); });
  $('#ve-bloques').addEventListener('input', function (e) {
    var k = e.target.dataset.k, el = e.target.closest('.ve-bloque'); if (!k || !el) return; bloques[+el.dataset.i][k] = e.target.value;
  });
  $('#ve-bloques').addEventListener('click', function (e) {
    var el = e.target.closest('.ve-bloque'); if (!el) return; var i = +el.dataset.i;
    var mv = e.target.closest('[data-mv]'); if (mv) { var j = i + +mv.dataset.mv; var t = bloques[i]; bloques[i] = bloques[j]; bloques[j] = t; sucio = true; pintarBloques(); }
    if (e.target.closest('[data-quitar]')) { bloques.splice(i, 1); sucio = true; pintarBloques(); indice(); }
  });
  $('#ve-bloques').addEventListener('change', function (e) {
    var inp = e.target; if (!inp.dataset.up) return; var file = inp.files[0]; if (!file) return; var i = +inp.dataset.up;
    var lbl = inp.closest('.drop'); lbl.classList.add('busy'); lbl.querySelector('b').textContent = 'Subiendo…';
    achicarYSubir(file, 'detalle').then(function (u) { bloques[i].url = u; sucio = true; pintarBloques(); C.toast('Archivo subido. Acordate de guardar.'); })
      .catch(function (er) { C.toast('No se pudo subir: ' + er.message, true); pintarBloques(); });
  });
  $('#ve-cats').addEventListener('change', indice); $('#ve-prods').addEventListener('change', indice);

  /* guardar */
  function leer() {
    var d = Object.assign({}, actual);
    ['pais', 'ciudad', 'region', 'slug', 'resumen', 'dias', 'presupuesto', 'mejor_epoca', 'clima', 'requisitos', 'requisitos_fuente', 'moneda', 'corriente', 'huso', 'unidades', 'talles', 'foto_pos', 'estado'].concat(CAMPOS.map(function (c) { return c[0]; })).forEach(function (k) { d[k] = f[k].value.trim(); });
    d.slug = C.slugify(d.slug || d.ciudad);
    d.tags = marcados('#ve-tags'); d.categorias_tienda = marcados('#ve-cats'); d.notas = marcados('#ve-notas'); d.productos = marcados('#ve-prods');
    d.foto = foto;
    d.faqs = faqs.filter(function (q) { return q.q.trim(); }).map(function (q) { return { q: q.q.trim(), a: (q.a || '').trim() }; });
    d.detalle = bloques.filter(function (b) { return b.texto || b.titulo || b.url; });
    delete d.actualizado; delete d.creado; if (nuevo && !demo) delete d.id;
    return d;
  }
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = leer(), msg = $('#ve-msg');
    if (!d.pais || !d.ciudad) { msg.className = 'msg err'; msg.textContent = 'Completá el país y la ciudad.'; return; }
    if (d.estado === 'Publicado' && !d.resumen) { msg.className = 'msg err'; msg.textContent = 'Para publicar, agregá un resumen.'; return; }
    $('#ve-guardar').disabled = true; msg.className = 'msg'; msg.textContent = 'Guardando…';
    api.guardar(d, nuevo).then(function (g) {
      actual = g; nuevo = false; sucio = false; $('#ve-borrar').hidden = false;
      C.publicar(); msg.className = 'msg ok'; msg.textContent = d.estado === 'Publicado' ? 'Guardado. Se ve en el sitio en unos minutos.' : 'Guardado.';
      $('#ve-titulo').textContent = g.ciudad;
      var i = lista.findIndex(function (x) { return x.id === g.id; }); if (i >= 0) lista[i] = g; else lista.push(g);
      $('#ve-ver').hidden = d.estado !== 'Publicado'; $('#ve-ver').href = '../viajes/' + claveP(g.pais) + '/' + g.slug + '/';
    }).catch(function (er) {
      msg.className = 'msg err';
      msg.textContent = /duplicate|unique/i.test(er.message) ? 'Ya hay un destino con esa dirección. Cambiala.' : 'No se pudo guardar: ' + er.message;
    }).then(function () { $('#ve-guardar').disabled = false; });
  });
  $('#ve-volver').addEventListener('click', function () { if (sucio && !confirm('Tenés cambios sin guardar. ¿Salir igual?')) return; C.mostrar('#v-vlista'); pintar(); });
  $('#ve-borrar').addEventListener('click', function () {
    if (!confirm('¿Eliminar ' + actual.ciudad + '? Esta acción no se puede deshacer.')) return;
    api.borrar(actual.id).then(function () { lista = lista.filter(function (x) { return x.id !== actual.id; }); C.toast('Destino eliminado.'); C.publicar(); C.mostrar('#v-vlista'); pintar(); })
      .catch(function (er) { C.toast('No se pudo eliminar: ' + er.message, true); });
  });

  /* ================= Organizá tu viaje ================= */
  var SERVS = [['alojamiento', 'Alojamiento'], ['vuelos', 'Vuelos'], ['seguro', 'Seguro médico'], ['autos', 'Autos'], ['excursiones', 'Excursiones'], ['paquetes', 'Paquetes'], ['traslados', 'Traslados y transporte'], ['gastronomia', 'Dónde comer']];
  var apiO = demo ? (function () {
    var serv = SERVS.map(function (x) { return { clave: x[0], bajada: '', contenido: '', activo: false }; });
    var ofs = [{ id: 'o1', servicio: 'vuelos', tipo: 'aliado', nombre: 'Despegar', etiqueta: 'Vuelos', descripcion: 'Buscá y compará vuelos.', link: 'https://www.despegar.com/vuelos/', destinos: [], estado: 'Publicado', orden: 0 },
      { id: 'o2', servicio: 'alojamiento', tipo: 'propio', nombre: 'Cabañas del Bosque', etiqueta: 'Cabaña', descripcion: 'Cabañas para 4 personas a 5 minutos del lago.', link: '', ubicacion: 'Villa La Angostura', precio_desde: '$ 80.000 la noche', whatsapp: '+5491112345678', destinos: ['bariloche'], cupon_codigo: 'UMARTI10', cupon_texto: '10% en estadías de 3 noches o más', estado: 'Borrador', orden: 1 }];
    var R = function (v) { return Promise.resolve(v); };
    return { servicios: function () { return R(serv); }, guardarServ: function (x) { serv = serv.map(function (o) { return o.clave === x.clave ? x : o; }); return R(x); },
      ofertas: function () { return R(ofs.slice()); }, guardar: function (o, nuevo) { if (nuevo) { o.id = 'o' + Date.now(); ofs.push(o); } else ofs = ofs.map(function (x) { return x.id === o.id ? o : x; }); return R(o); },
      borrar: function (id) { ofs = ofs.filter(function (x) { return x.id !== id; }); return R(); } };
  })() : {
    servicios: function () { return sb.from('viajes_servicios').select('*').then(ok); },
    guardarServ: function (x) { return sb.from('viajes_servicios').upsert(x).select().single().then(ok); },
    ofertas: function () { return sb.from('viajes_ofertas').select('*').order('orden').order('creado').then(ok); },
    guardar: function (o, nuevo) { var q = nuevo ? sb.from('viajes_ofertas').insert(o) : sb.from('viajes_ofertas').update(o).eq('id', o.id); return q.select().single().then(ok); },
    borrar: function (id) { return sb.from('viajes_ofertas').delete().eq('id', id).then(ok); }
  };
  var servs = [], ofs = [], servAct = 'alojamiento';
  function nombreServ(k) { return (SERVS.find(function (x) { return x[0] === k; }) || [k, k])[1]; }
  function abrirOrg() {
    C.mostrar('#v-vorg');
    $('#vo-tabla').innerHTML = '<p class="vacio">Cargando…</p>';
    Promise.all([apiO.servicios(), apiO.ofertas()]).then(function (r) { servs = r[0]; ofs = r[1]; pintarOrg(); })
      .catch(function (e) { $('#vo-tabla').innerHTML = '<p class="vacio err">No se pudo cargar: ' + esc(e.message) + '</p>'; });
  }
  function pintarOrg() {
    $('#vo-servs').innerHTML = SERVS.map(function (x) {
      var n = ofs.filter(function (o) { return o.servicio === x[0]; }).length;
      return '<button type="button" role="tab" aria-selected="' + (x[0] === servAct) + '" data-serv="' + x[0] + '">' + x[1] + ' <small>' + n + '</small></button>';
    }).join('');
    $('#vo-titulo').textContent = nombreServ(servAct);
    $('#vo-nota').textContent = servAct === 'vuelos' || servAct === 'paquetes' ? 'Este servicio no tiene página: en el sitio la tarjeta dice "Ver más" y lleva directo al link del primer aliado publicado. Cargá acá tu link de afiliado.' :
      (servAct === 'alojamiento' || servAct === 'gastronomia') ? 'Las opciones propias tienen que tener al menos un destino: en el sitio se buscan por destino.' : '';
    var sc = servs.find(function (x) { return x.clave === servAct; }) || { clave: servAct };
    var fs = $('#f-serv'); fs.activo.checked = !!sc.activo; fs.bajada.value = sc.bajada || ''; fs.contenido.value = sc.contenido || ''; $('#vo-msg').textContent = '';
    var xs = ofs.filter(function (o) { return o.servicio === servAct; });
    var nombres = {}; destPanel.forEach(function (d) { nombres[d.slug] = d.nombre; });
    $('#vo-tabla').innerHTML = xs.length ? '<table><thead><tr><th>Nombre</th><th>Tipo</th><th>Destinos</th><th>Cupón</th><th>Estado</th></tr></thead><tbody>' + xs.map(function (o) {
      return '<tr data-id="' + esc(o.id) + '"><td><b>' + esc(o.nombre) + '</b><small>' + esc(o.etiqueta || '') + '</small></td><td><span class="pill ' + (o.tipo === 'aliado' ? 'al' : '') + '">' + (o.tipo === 'aliado' ? 'Aliado' : 'Propia') + '</span></td>' +
        '<td><small>' + ((o.destinos || []).map(function (s) { return esc(nombres[s] || s); }).join(', ') || 'Todos') + '</small></td><td><small>' + esc(o.cupon_codigo || '—') + '</small></td>' +
        '<td><span class="st st-' + esc((o.estado || '').toLowerCase()) + '">' + esc(o.estado) + '</span></td></tr>';
    }).join('') + '</tbody></table>' : '<p class="vacio">Todavía no hay opciones para ' + esc(nombreServ(servAct).toLowerCase()) + '. Sumá un aliado (programa de afiliados) o una opción propia.</p>';
    $$('#vo-tabla tr[data-id]').forEach(function (tr) { tr.addEventListener('click', function () { editarOferta(ofs.find(function (o) { return o.id === tr.dataset.id; })); }); });
  }
  $('#vo-servs').addEventListener('click', function (e) { var b = e.target.closest('[data-serv]'); if (b) { servAct = b.dataset.serv; pintarOrg(); } });
  $('#f-serv').addEventListener('submit', function (e) {
    e.preventDefault(); var fs = e.target, m = $('#vo-msg');
    var x = { clave: servAct, activo: fs.activo.checked, bajada: fs.bajada.value.trim(), contenido: fs.contenido.value.trim() };
    m.className = 'msg'; m.textContent = 'Guardando…';
    apiO.guardarServ(x).then(function (g) { var i = servs.findIndex(function (s) { return s.clave === g.clave; }); if (i >= 0) servs[i] = g; else servs.push(g); C.publicar(); m.className = 'msg ok'; m.textContent = 'Guardado.'; })
      .catch(function (er) { m.className = 'msg err'; m.textContent = 'No se pudo guardar: ' + er.message; });
  });
  $('#vo-cont').addEventListener('input', function () {});
  $('#f-serv').addEventListener('click', function (e) { var bt = e.target.closest('[data-fmt]'); if (bt) formato($('#vo-cont'), bt.dataset.fmt); });

  /* editor de opción */
  var fo = $('#f-oferta'), oAct = null, oNuevo = false, oFoto = '';
  fo.servicio.innerHTML = SERVS.map(function (x) { return '<option value="' + x[0] + '">' + x[1] + '</option>'; }).join('');
  var destPanel = C.P.destinos.slice();
  function pintarDestOpts() { $('#vf-destinos').innerHTML = destPanel.map(function (d) { return '<label class="chk"><input type="checkbox" value="' + esc(d.slug) + '"> ' + esc(d.nombre) + '</label>'; }).join('') || '<small class="muted">Todavía no hay destinos cargados.</small>'; }
  pintarDestOpts();
  if (!demo) sb.from('destinos').select('slug,ciudad,estado').order('ciudad').then(function (r) { if (!r.error) { destPanel = r.data.map(function (d) { return { slug: d.slug, nombre: d.ciudad + (d.estado !== 'Publicado' ? ' (borrador)' : '') }; }); pintarDestOpts(); } });
  function tipoUI() {
    var al = fo.tipo.value === 'aliado';
    $('#vf-propio').hidden = al;
    $('#vf-link-lbl').textContent = al ? 'Link de afiliado' : 'Link para reservar (opcional)';
    fo.link.required = al;
  }
  fo.tipo.addEventListener('change', tipoUI);
  function editarOferta(o, tipo) {
    oNuevo = !o;
    oAct = o ? JSON.parse(JSON.stringify(o)) : { servicio: servAct, tipo: tipo || 'propio', estado: 'Borrador', destinos: [] };
    ['servicio', 'tipo', 'nombre', 'etiqueta', 'descripcion', 'link', 'ubicacion', 'precio_desde', 'whatsapp', 'email', 'cupon_codigo', 'cupon_texto', 'estado'].forEach(function (k) { fo[k].value = oAct[k] || ''; });
    marcar('#vf-destinos', oAct.destinos); oFoto = oAct.foto || ''; pintarOFoto(); tipoUI();
    $('#vf-titulo').textContent = oNuevo ? (oAct.tipo === 'aliado' ? 'Nuevo aliado' : 'Nueva opción propia') : oAct.nombre;
    $('#vf-sub').textContent = nombreServ(oAct.servicio); $('#vf-msg').textContent = ''; $('#vf-borrar').hidden = oNuevo;
    C.mostrar('#v-voferta');
  }
  function pintarOFoto() {
    $('#vf-foto').innerHTML = oFoto ? '<figure><img src="' + esc(oFoto) + '" alt=""><button type="button" id="vf-foto-del">Quitar</button></figure>' : '';
    var d = $('#vf-foto-del'); if (d) d.addEventListener('click', function () { oFoto = ''; pintarOFoto(); });
  }
  var vfd = $('#vf-foto-drop');
  vfd.querySelector('input').addEventListener('change', function () {
    var file = this.files[0]; if (!file) return; vfd.classList.add('busy'); vfd.querySelector('b').textContent = 'Subiendo…';
    C.achicar(file).then(function (blob) { return api.subir('organiza/' + fo.servicio.value + '/' + Date.now() + '.jpg', blob, 'image/jpeg'); })
      .then(function (u) { oFoto = u; pintarOFoto(); C.toast('Foto subida. Acordate de guardar.'); })
      .catch(function (er) { C.toast('No se pudo subir: ' + er.message, true); })
      .then(function () { vfd.classList.remove('busy'); vfd.querySelector('b').textContent = 'Subir foto'; vfd.querySelector('input').value = ''; });
  });
  fo.addEventListener('submit', function (e) {
    e.preventDefault(); var m = $('#vf-msg');
    var o = Object.assign({}, oAct);
    ['servicio', 'tipo', 'nombre', 'etiqueta', 'descripcion', 'link', 'ubicacion', 'precio_desde', 'whatsapp', 'email', 'cupon_codigo', 'cupon_texto', 'estado'].forEach(function (k) { o[k] = fo[k].value.trim(); });
    o.destinos = marcados('#vf-destinos'); o.foto = o.tipo === 'aliado' ? '' : oFoto;
    if (!o.nombre) { m.className = 'msg err'; m.textContent = 'Poné un nombre.'; return; }
    if (o.tipo === 'propio' && (o.servicio === 'alojamiento' || o.servicio === 'gastronomia') && !o.destinos.length) { m.className = 'msg err'; m.textContent = 'Elegí al menos un destino.'; return; }
    if (o.tipo === 'aliado' && !/^https?:\/\//.test(o.link)) { m.className = 'msg err'; m.textContent = 'Pegá el link de afiliado (empieza con https://).'; return; }
    if (o.tipo === 'propio' && o.estado === 'Publicado' && !o.link && !o.whatsapp && !o.email) { m.className = 'msg err'; m.textContent = 'Para publicar, agregá al menos un link, un WhatsApp o un correo.'; return; }
    delete o.creado; delete o.actualizado; if (oNuevo && !demo) delete o.id;
    $('#vf-guardar').disabled = true; m.className = 'msg'; m.textContent = 'Guardando…';
    apiO.guardar(o, oNuevo).then(function (g) {
      var i = ofs.findIndex(function (x) { return x.id === g.id; }); if (i >= 0) ofs[i] = g; else ofs.push(g);
      oAct = g; oNuevo = false; $('#vf-borrar').hidden = false; $('#vf-titulo').textContent = g.nombre;
      C.publicar(); m.className = 'msg ok'; m.textContent = g.estado === 'Publicado' ? 'Guardado. Se ve en el sitio en unos minutos.' : 'Guardado.';
    }).catch(function (er) { m.className = 'msg err'; m.textContent = 'No se pudo guardar: ' + er.message; })
      .then(function () { $('#vf-guardar').disabled = false; });
  });
  $('#vf-volver').addEventListener('click', function () { servAct = fo.servicio.value || servAct; C.mostrar('#v-vorg'); pintarOrg(); });
  $('#vf-borrar').addEventListener('click', function () {
    if (!confirm('¿Eliminar ' + oAct.nombre + '?')) return;
    apiO.borrar(oAct.id).then(function () { ofs = ofs.filter(function (x) { return x.id !== oAct.id; }); C.mostrar('#v-vorg'); pintarOrg(); C.toast('Eliminado.'); C.publicar(); })
      .catch(function (er) { C.toast('No se pudo eliminar: ' + er.message, true); });
  });
  $('#vo-add-aliado').addEventListener('click', function () { editarOferta(null, 'aliado'); });
  $('#vo-add-propio').addEventListener('click', function () { editarOferta(null, 'propio'); });

  /* subpestañas Destinos / Organizá */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-vsub]'); if (!b) return;
    if (b.dataset.vsub === 'organiza') abrirOrg(); else abrir();
  });

  window.PanelViajes = { abrir: abrir };
})();
