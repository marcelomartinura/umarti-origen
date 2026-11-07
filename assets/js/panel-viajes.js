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
    ['pais', 'ciudad', 'region', 'slug', 'resumen', 'dias', 'presupuesto', 'mejor_epoca', 'foto_pos', 'estado'].concat(CAMPOS.map(function (c) { return c[0]; })).forEach(function (k) { if (f[k]) f[k].value = actual[k] || (k === 'foto_pos' ? 'center' : ''); });
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
    items.push(['En detalle', bloques.length > 0]);
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
    ['pais', 'ciudad', 'region', 'slug', 'resumen', 'dias', 'presupuesto', 'mejor_epoca', 'foto_pos', 'estado'].concat(CAMPOS.map(function (c) { return c[0]; })).forEach(function (k) { d[k] = f[k].value.trim(); });
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
      msg.className = 'msg ok'; msg.textContent = d.estado === 'Publicado' ? 'Guardado. Se ve en el sitio en hasta 30 minutos.' : 'Guardado.';
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
    api.borrar(actual.id).then(function () { lista = lista.filter(function (x) { return x.id !== actual.id; }); C.toast('Destino eliminado.'); C.mostrar('#v-vlista'); pintar(); })
      .catch(function (er) { C.toast('No se pudo eliminar: ' + er.message, true); });
  });

  window.PanelViajes = { abrir: abrir };
})();
