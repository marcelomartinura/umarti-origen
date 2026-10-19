/* Panel de Umarti Origen: ingreso, lista y editor de productos (Supabase) */
(function () {
  'use strict';
  var P = window.PANEL;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var ESTADOS = ['Publicado', 'Borrador', 'Pausado', 'Ejemplo'];
  var BUCKET = 'productos';

  /* ---------- conexión (Supabase, o datos de prueba con ?demo) ---------- */
  var demo = /[?&]demo\b/.test(location.search);
  var sb = null;
  if (!demo) {
    if (!window.supabase) { document.body.innerHTML = '<p style="padding:40px;font-family:sans-serif">No se pudo cargar la conexión con la base de datos. Revisá tu conexión a internet y recargá la página.</p>'; return; }
    sb = window.supabase.createClient(P.supabase.url, P.supabase.key);
  }
  var api = demo ? demoApi() : {
    sesion: function () { return sb.auth.getSession().then(function (r) { return r.data.session; }); },
    entrar: function (email, pass) { return sb.auth.signInWithPassword({ email: email, password: pass }); },
    registrar: function (email, pass) { return sb.auth.signUp({ email: email, password: pass, options: { emailRedirectTo: location.origin + location.pathname } }); },
    salir: function () { return sb.auth.signOut(); },
    esAdmin: function () { return sb.from('admins').select('email').limit(1).then(function (r) { return !r.error && r.data.length > 0; }); },
    listar: function () { return sb.from('productos').select('*').order('orden').order('creado').then(ok); },
    guardar: function (p, nuevo) {
      var q = nuevo ? sb.from('productos').insert(p) : sb.from('productos').update(p).eq('id', p.id);
      return q.select().single().then(ok);
    },
    borrar: function (id) { return sb.from('productos').delete().eq('id', id).then(ok); },
    subir: function (ruta, blob) {
      return sb.storage.from(BUCKET).upload(ruta, blob, { contentType: 'image/jpeg', upsert: false }).then(function (r) {
        if (r.error) throw r.error;
        return sb.storage.from(BUCKET).getPublicUrl(ruta).data.publicUrl;
      });
    },
    borrarFotos: function (urls) {
      var rutas = urls.map(rutaDeUrl).filter(Boolean);
      if (!rutas.length) return Promise.resolve();
      return sb.storage.from(BUCKET).remove(rutas);
    }
  };
  function ok(r) { if (r.error) throw r.error; return r.data; }
  function rutaDeUrl(u) { var m = String(u).match(/\/object\/public\/productos\/(.+)$/); return m ? decodeURIComponent(m[1]) : null; }

  /* Mercados locales abiertos: por ahora solo la Tienda Argentina */
  function localAbierto() { return document.querySelector('#f-prod [name=pais]').value === 'Argentina'; }

  /* ---------- utilidades ---------- */
  var toastEl = $('#toast'), tt;
  function toast(m, err) { toastEl.textContent = m; toastEl.className = 'toast show' + (err ? ' err' : ''); clearTimeout(tt); tt = setTimeout(function () { toastEl.className = 'toast'; }, 3800); }
  function slugify(t) { return String(t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 80); }
  function plata(v, m) {
    if (v === null || v === undefined || v === '') return '';
    var n = Number(v).toLocaleString('es-AR', { maximumFractionDigits: 2 });
    return (m === 'USD' ? 'US$ ' : '$ ') + n;
  }
  function precioPrincipal(p) {
    var mon = { 'Argentina': 'ARS', 'México': 'MXN' }[p.pais];
    if (mon === 'ARS' && p.tienda_ar && p.precio_ars != null) return [plata(p.precio_ars), 'ARS'];
    if (p.tienda_ar && p.precio_ars != null) return [plata(p.precio_ars), 'ARS'];
    if (p.precio_usd != null) return [plata(p.precio_usd, 'USD'), 'USD'];
    return ['Sin precio', ''];
  }
  function mostrar(id) { ['#v-login', '#v-noadmin', '#v-lista', '#v-editor'].forEach(function (v) { $(v).hidden = v !== id; }); window.scrollTo(0, 0); }

  /* ---------- ingreso ---------- */
  var modoAlta = false;
  $('#login-modo').addEventListener('click', function () {
    modoAlta = !modoAlta;
    $('#login-btn').textContent = modoAlta ? 'Crear contraseña' : 'Entrar';
    $('#login-sub').textContent = modoAlta ? 'Elegí una contraseña de al menos 8 caracteres. Te vamos a mandar un correo para confirmar tu cuenta.' : 'Con tu correo y tu contraseña.';
    $('#login-modo').textContent = modoAlta ? 'Ya tengo contraseña: entrar' : '¿Primera vez? Creá tu contraseña';
    $('#f-login [name=pass]').setAttribute('autocomplete', modoAlta ? 'new-password' : 'current-password');
    $('#login-msg').textContent = '';
  });
  $('#f-login').addEventListener('submit', function (e) {
    e.preventDefault();
    var f = e.target, email = f.email.value.trim().toLowerCase(), pass = f.pass.value, msg = $('#login-msg'), b = $('#login-btn');
    b.disabled = true; msg.className = 'msg'; msg.textContent = modoAlta ? 'Creando tu cuenta…' : 'Entrando…';
    (modoAlta ? api.registrar(email, pass) : api.entrar(email, pass)).then(function (r) {
      b.disabled = false;
      if (r.error) {
        var t = r.error.message || '';
        msg.className = 'msg err';
        msg.textContent = /Invalid login/i.test(t) ? 'El correo o la contraseña no coinciden.' :
          /not confirmed/i.test(t) ? 'Todavía no confirmaste tu correo. Buscá el mensaje de Supabase en tu bandeja (o en spam) y tocá el enlace.' :
          /already registered/i.test(t) ? 'Ese correo ya tiene cuenta. Volvé a "Entrar".' : 'No se pudo: ' + t;
        return;
      }
      if (modoAlta && !(r.data && r.data.session)) {
        msg.className = 'msg ok';
        msg.textContent = 'Listo. Te mandamos un correo para confirmar la cuenta. Después de confirmarla, volvé acá y entrá con tu contraseña.';
        return;
      }
      iniciar();
    });
  });
  function salir() { api.salir().then(function () { location.reload(); }); }
  $('#pn-salir').addEventListener('click', salir);
  $$('[data-salir]').forEach(function (b) { b.addEventListener('click', salir); });

  function iniciar() {
    api.sesion().then(function (s) {
      if (!s) { $('#pn-user').hidden = true; mostrar('#v-login'); return; }
      $('#pn-email').textContent = s.user.email; $('#pn-user').hidden = false;
      return api.esAdmin().then(function (si) {
        if (!si) { $('#noadmin-email').textContent = s.user.email; mostrar('#v-noadmin'); return; }
        cargarLista();
      });
    });
  }

  /* ---------- lista ---------- */
  var productos = [], filtroEstado = '';
  var selCat = $('#l-cat');
  Object.keys(P.categorias).forEach(function (c) { var o = document.createElement('option'); o.value = c; o.textContent = c; selCat.appendChild(o); });
  $('#l-estados').innerHTML = ['', 'Publicado', 'Borrador', 'Pausado', 'Ejemplo'].map(function (e) { return '<button type="button" data-estado="' + e + '" aria-pressed="' + (e === '' ? 'true' : 'false') + '">' + (e || 'Todos') + ' <small></small></button>'; }).join('');
  $$('#l-estados button').forEach(function (b) { b.addEventListener('click', function () { filtroEstado = b.dataset.estado; pintarLista(); }); });
  $('#l-q').addEventListener('input', pintarLista); selCat.addEventListener('change', pintarLista);
  $('#b-nuevo').addEventListener('click', function () { abrirEditor(null); });

  function cargarLista() {
    mostrar('#v-lista');
    $('#l-tabla').innerHTML = '<p class="vacio">Cargando productos…</p>';
    api.listar().then(function (d) { productos = d; pintarLista(); }).catch(function (e) { $('#l-tabla').innerHTML = '<p class="vacio err">No se pudieron cargar los productos: ' + esc(e.message) + '</p>'; });
  }
  function pintarLista() {
    var q = slugify($('#l-q').value).replace(/-/g, ' '), c = selCat.value;
    var cuenta = { '': productos.length }; ESTADOS.forEach(function (e) { cuenta[e] = productos.filter(function (p) { return p.estado === e; }).length; });
    $$('#l-estados button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.estado === filtroEstado)); b.querySelector('small').textContent = cuenta[b.dataset.estado]; });
    $('#l-resumen').textContent = productos.length + (productos.length === 1 ? ' producto' : ' productos') + ' · ' + cuenta.Publicado + ' publicados · ' + cuenta.Borrador + ' en borrador';
    var lista = productos.filter(function (p) {
      var txt = slugify([p.nombre, p.codigo, p.region, p.subcategoria].join(' ')).replace(/-/g, ' ');
      return (!filtroEstado || p.estado === filtroEstado) && (!c || p.categoria === c) && (!q || txt.indexOf(q) > -1);
    });
    if (!productos.length) { $('#l-tabla').innerHTML = '<div class="vacio"><b>Todavía no hay productos.</b><p>Tocá "Nuevo producto" para cargar el primero.</p></div>'; return; }
    if (!lista.length) { $('#l-tabla').innerHTML = '<p class="vacio">Ningún producto coincide con la búsqueda.</p>'; return; }
    $('#l-tabla').innerHTML = '<div class="row head"><span></span><span>Producto</span><span>Categoría</span><span>Precio</span><span>Dónde se vende</span><span>Estado</span></div>' +
      lista.map(function (p) {
        var pr = precioPrincipal(p);
        var donde = [p.tienda_ar && 'Local', p.international && 'Internacional', p.hub && 'HUB'].filter(Boolean).map(function (x) { return '<i>' + x + '</i>'; }).join('') || '<span class="muted">—</span>';
        var th = p.fotos && p.fotos[0] ? '<img src="' + esc(p.fotos[0]) + '" alt="" loading="lazy">' : '<span class="ph">' + esc((p.nombre || '?')[0]) + '</span>';
        return '<button type="button" class="row" data-id="' + p.id + '"><span class="th">' + th + '</span><span class="nm"><b>' + esc(p.nombre) + '</b><small>' + esc(p.codigo) + (p.region ? ' · ' + esc(p.region) : '') + '</small></span>' +
          '<span class="ct">' + esc(p.categoria) + '<small>' + esc(p.subcategoria) + '</small></span><span class="pr">' + esc(pr[0]) + ' <small>' + pr[1] + '</small></span><span class="dn">' + donde + '</span>' +
          '<span><em class="st st-' + slugify(p.estado) + '">' + esc(p.estado) + '</em></span></button>';
      }).join('');
    $$('#l-tabla .row[data-id]').forEach(function (r) { r.addEventListener('click', function () { abrirEditor(productos.filter(function (p) { return p.id === r.dataset.id; })[0]); }); });
  }

  /* ---------- editor ---------- */
  var f = $('#f-prod'), actual = null, fotos = [], aBorrar = [], paisesEnvio = [], sucio = false, slugManual = false;
  var selCatE = f.categoria, selSub = f.subcategoria;
  selCatE.innerHTML = Object.keys(P.categorias).map(function (c) { return '<option>' + esc(c) + '</option>'; }).join('');
  function llenarSubs(sel) { selSub.innerHTML = (P.categorias[selCatE.value] || []).map(function (s) { return '<option>' + esc(s) + '</option>'; }).join(''); if (sel) selSub.value = sel; }
  selCatE.addEventListener('change', function () { llenarSubs(); });
  f.pais.innerHTML = P.paises.map(function (p) { return '<option>' + esc(p) + '</option>'; }).join('');
  f.destino.innerHTML += P.destinos.map(function (d) { return '<option value="' + d.slug + '">' + esc(d.nombre) + ' (' + esc(d.pais) + ')</option>'; }).join('');
  $('#e-temas').innerHTML = P.temas.map(function (t) { return '<label class="chk"><input type="checkbox" value="' + esc(t.clave) + '">' + esc(t.nombre) + '</label>'; }).join('') || '<span class="muted">No hay temas creados.</span>';
  $('#l-paises').innerHTML = P.paises_envio.map(function (p) { return '<option value="' + esc(p) + '">'; }).join('');

  function vacio() {
    return { id: (crypto.randomUUID ? crypto.randomUUID() : String(Date.now())), nombre: '', descripcion: '', categoria: Object.keys(P.categorias)[0], subcategoria: '', temas: [], pais: 'Argentina', region: '', destino: '',
      precio_ars: null, precio_usd: null, tienda_ar: true, international: false, paises_envio: ['México'], hub: false, hs: '', volumen: '', vigencia_hub: null,
      link_pago: '', fotos: [], estado: 'Borrador', vendedor: 'Umarti Origen', slug: '' };
  }
  function abrirEditor(p, copia) {
    var nuevo = !p || copia;
    actual = nuevo ? Object.assign(vacio(), copia ? JSON.parse(JSON.stringify(p)) : {}) : p;
    if (copia) { actual.id = vacio().id; delete actual.codigo; actual.nombre = p.nombre + ' (copia)'; actual.slug = ''; actual.estado = 'Borrador'; actual.fotos = []; }
    actual._nuevo = nuevo;
    fotos = (actual.fotos || []).slice(); aBorrar = []; paisesEnvio = (actual.paises_envio || []).slice(); slugManual = !nuevo;
    ['nombre', 'descripcion', 'region', 'hs', 'volumen', 'link_pago', 'vendedor', 'slug'].forEach(function (k) { f[k].value = actual[k] || ''; });
    ['precio_ars', 'precio_usd'].forEach(function (k) { f[k].value = actual[k] == null ? '' : actual[k]; });
    ['tienda_ar', 'international', 'hub'].forEach(function (k) { f[k].checked = !!actual[k]; });
    selCatE.value = actual.categoria; llenarSubs(actual.subcategoria);
    f.pais.value = P.paises.indexOf(actual.pais) > -1 ? actual.pais : 'Otro';
    f.destino.value = actual.destino || ''; f.estado.value = actual.estado; f.vigencia_hub.value = actual.vigencia_hub || '';
    $$('#e-temas input').forEach(function (c) { c.checked = (actual.temas || []).indexOf(c.value) > -1; });
    $('#e-titulo').textContent = nuevo ? (copia ? 'Copia de producto' : 'Nuevo producto') : actual.nombre;
    $('#e-sub').textContent = nuevo ? 'Completá los datos y guardá. Podés dejarlo en Borrador hasta que esté listo.' : actual.codigo + ' · última edición ' + new Date(actual.actualizado).toLocaleString('es-AR', { dateStyle: 'medium', timeStyle: 'short' });
    $('#e-ver').hidden = nuevo || !(actual.estado === 'Publicado' || actual.estado === 'Ejemplo'); $('#e-ver').href = '../tienda/' + actual.slug + '/';
    $('#e-duplicar').hidden = nuevo; $('#e-borrar').hidden = nuevo;
    $('#e-msg').textContent = '';
    pintarFotos(); pintarPaises(); actualizar(); sucio = false;
    mostrar('#v-editor'); f.nombre.focus();
  }
  $('#e-volver').addEventListener('click', function () { if (sucio && !confirm('Tenés cambios sin guardar. ¿Salir igual?')) return; cargarLista(); });
  window.addEventListener('beforeunload', function (e) { if (sucio && !$('#v-editor').hidden) { e.preventDefault(); e.returnValue = ''; } });
  $('#e-duplicar').addEventListener('click', function () { abrirEditor(actual, true); toast('Copia lista para editar. Las fotos no se copian.'); });
  $('#e-borrar').addEventListener('click', function () {
    if (!confirm('¿Eliminar "' + actual.nombre + '"? Se borran también sus fotos. No se puede deshacer.')) return;
    api.borrar(actual.id).then(function () { return api.borrarFotos(actual.fotos || []); }).then(function () { sucio = false; toast('Producto eliminado.'); cargarLista(); })
      .catch(function (e) { toast('No se pudo eliminar: ' + e.message, true); });
  });

  f.addEventListener('input', function (e) {
    sucio = true;
    if (e.target.name === 'slug') slugManual = true;
    if (e.target.name === 'nombre' && !slugManual) f.slug.value = slugify(f.nombre.value);
    actualizar();
  });
  f.addEventListener('change', function () { sucio = true; actualizar(); });

  function leer() {
    var num = function (k) { var v = f[k].value.trim(); return v === '' ? null : Number(v); };
    return {
      id: actual.id, nombre: f.nombre.value.trim(), descripcion: f.descripcion.value.trim(), categoria: selCatE.value, subcategoria: selSub.value,
      temas: $$('#e-temas input:checked').map(function (c) { return c.value; }), pais: f.pais.value, region: f.region.value.trim(), destino: f.destino.value,
      precio_ars: num('precio_ars'), precio_usd: num('precio_usd'),
      tienda_ar: f.tienda_ar.checked && localAbierto(), international: f.international.checked, paises_envio: paisesEnvio.slice(),
      hub: f.hub.checked, hs: f.hs.value.replace(/\D/g, ''), volumen: f.volumen.value.trim(), vigencia_hub: f.vigencia_hub.value || null,
      link_pago: f.link_pago.value.trim(), fotos: fotos.slice(), estado: f.estado.value, vendedor: f.vendedor.value.trim() || 'Umarti Origen', slug: slugify(f.slug.value)
    };
  }
  function problemas(p) {
    var out = [];
    if (!p.nombre) out.push(['err', 'Falta el nombre.']);
    if (!p.slug) out.push(['err', 'Falta la dirección en el sitio.']);
    else if (productos.some(function (o) { return o.slug === p.slug && o.id !== p.id; })) out.push(['err', 'Ya hay otro producto con la dirección "' + p.slug + '".']);
    if (!p.tienda_ar && !p.international && !p.hub) out.push(['warn', 'No está marcado en ningún mercado: no se va a ver en ningún lado.']);
    else if (!p.tienda_ar && !p.international) out.push(['warn', 'Solo está en el HUB: no se va a poder comprar por unidad.']);
    if (p.tienda_ar && p.precio_ars == null) out.push(['err', 'Marcaste Mercado local pero falta el precio en ARS.']);
    if (p.international && p.precio_usd == null) out.push(['err', 'Marcaste Mercado internacional pero falta el precio en USD.']);
    if (p.international && !p.paises_envio.length) out.push(['warn', 'Mercado internacional sin países de envío.']);
    if (!p.fotos.length) out.push(['warn', 'Sin fotos: se va a mostrar un dibujo de color.']);
    if (!p.descripcion) out.push(['warn', 'Sin descripción.']);
    if (p.hub && !p.hs) out.push(['warn', 'En el Hub conviene cargar la posición arancelaria: mejora las coincidencias.']);
    return out;
  }
  function actualizar() {
    var p = leer();
    var abierto = localAbierto();
    f.tienda_ar.disabled = !abierto;
    $('#m-local-aviso').hidden = abierto;
    $('#m-local-aviso').textContent = abierto ? '' : 'La tienda local de ' + f.pais.value + ' todavía no está abierta. Por ahora vendelo por el Mercado internacional.';
    $$('.mercado').forEach(function (m) { var c = m.querySelector('.sw input'); m.classList.toggle('off', !c.checked || c.disabled); });
    $$('.count').forEach(function (c) { var el = f[c.dataset.for]; c.textContent = el.value.length + ' / ' + el.maxLength; });
    var pr = precioPrincipal(p);
    var media = p.fotos[0] ? '<img src="' + esc(p.fotos[0]) + '" alt="">' : '<span class="pv-ph">' + esc((p.nombre || '?')[0]) + '</span>';
    var zonas = [p.tienda_ar && 'Argentina', p.international && 'Internacional'].filter(Boolean).join(' · ');
    $('#e-preview').innerHTML = '<div class="pv-media">' + media + (p.estado === 'Ejemplo' ? '<em>Ejemplo</em>' : '') + '</div><div class="pv-info"><small>' + esc(p.subcategoria) + '</small><b>' + esc(p.nombre || 'Nombre del producto') + '</b>' +
      '<span class="pv-pr">' + esc(pr[0]) + ' <small>' + pr[1] + '</small></span>' + (zonas ? '<span class="pv-env">Envío disponible <b>' + esc(zonas) + '</b></span>' : '') + '</div>';
    var pb = problemas(p);
    $('#e-check').innerHTML = pb.length ? '<span class="lbl">Revisá antes de publicar</span><ul>' + pb.map(function (x) { return '<li class="' + x[0] + '">' + esc(x[1]) + '</li>'; }).join('') + '</ul>' : '<span class="lbl">Todo en orden</span><p class="muted small">El producto está completo.</p>';
  }

  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var p = leer(), pb = problemas(p).filter(function (x) { return x[0] === 'err'; });
    if (!p.subcategoria) pb.push(['err', 'Falta la subcategoría.']);
    if (pb.length) { $('#e-msg').className = 'msg err'; $('#e-msg').textContent = pb[0][1]; return; }
    var b = $('#e-guardar'); b.disabled = true; $('#e-msg').className = 'msg'; $('#e-msg').textContent = 'Guardando…';
    var nuevo = actual._nuevo;
    if (nuevo) { var max = productos.reduce(function (m, o) { return Math.max(m, o.orden || 0); }, 0); p.orden = max + 1; }
    api.guardar(p, nuevo).then(function (g) {
      return api.borrarFotos(aBorrar).then(function () { return g; });
    }).then(function (g) {
      b.disabled = false; sucio = false; aBorrar = [];
      var i = productos.map(function (o) { return o.id; }).indexOf(g.id);
      if (i > -1) productos[i] = g; else productos.push(g);
      toast(g.estado === 'Publicado' || g.estado === 'Ejemplo' ? 'Guardado. Aparece en el sitio en hasta 30 minutos.' : 'Guardado como ' + g.estado.toLowerCase() + '. No se ve en el sitio.');
      abrirEditor(g);
      $('#e-msg').className = 'msg ok'; $('#e-msg').textContent = 'Guardado ✓';
    }).catch(function (err) {
      b.disabled = false; $('#e-msg').className = 'msg err';
      $('#e-msg').textContent = /duplicate key.*slug/i.test(err.message) ? 'Ya existe otro producto con esa dirección.' : 'No se pudo guardar: ' + err.message;
    });
  });

  /* ---------- países de envío ---------- */
  function pintarPaises() {
    $('#e-paises').innerHTML = paisesEnvio.map(function (p, i) { return '<span class="tag">' + esc(p) + '<button type="button" data-i="' + i + '" aria-label="Quitar ' + esc(p) + '">×</button></span>'; }).join('') || '<span class="muted small">Ninguno todavía.</span>';
    $$('#e-paises button').forEach(function (b) { b.addEventListener('click', function () { paisesEnvio.splice(+b.dataset.i, 1); sucio = true; pintarPaises(); actualizar(); }); });
  }
  function agregarPais() {
    var v = $('#e-pais-nuevo').value.trim();
    if (v && paisesEnvio.indexOf(v) < 0) { paisesEnvio.push(v); sucio = true; }
    $('#e-pais-nuevo').value = ''; pintarPaises(); actualizar();
  }
  $('#e-pais-add').addEventListener('click', agregarPais);
  $('#e-pais-nuevo').addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); agregarPais(); } });

  /* ---------- fotos ---------- */
  function pintarFotos() {
    $('#e-fotos').innerHTML = fotos.map(function (u, i) {
      return '<figure class="foto' + (i === 0 ? ' main' : '') + '"><img src="' + esc(u) + '" alt="">' + (i === 0 ? '<em>Principal</em>' : '') +
        '<div class="ft-acts"><button type="button" data-a="izq" data-i="' + i + '" aria-label="Mover a la izquierda"' + (i === 0 ? ' disabled' : '') + '>‹</button>' +
        '<button type="button" data-a="der" data-i="' + i + '" aria-label="Mover a la derecha"' + (i === fotos.length - 1 ? ' disabled' : '') + '>›</button>' +
        '<button type="button" data-a="del" data-i="' + i + '" aria-label="Quitar foto">×</button></div></figure>';
    }).join('');
    $$('#e-fotos button').forEach(function (b) {
      b.addEventListener('click', function () {
        var i = +b.dataset.i;
        if (b.dataset.a === 'del') aBorrar.push(fotos.splice(i, 1)[0]);
        else { var j = b.dataset.a === 'izq' ? i - 1 : i + 1; var t = fotos[i]; fotos[i] = fotos[j]; fotos[j] = t; }
        sucio = true; pintarFotos(); actualizar();
      });
    });
  }
  function achicar(file) {
    return new Promise(function (res, rej) {
      var img = new Image(), url = URL.createObjectURL(file);
      img.onload = function () {
        var max = 1600, w = img.naturalWidth, h = img.naturalHeight, k = Math.min(1, max / Math.max(w, h));
        var c = document.createElement('canvas'); c.width = Math.round(w * k); c.height = Math.round(h * k);
        var ctx = c.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height); ctx.drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        c.toBlob(function (b) { b ? res(b) : rej(new Error('No se pudo procesar la imagen')); }, 'image/jpeg', 0.85);
      };
      img.onerror = function () { rej(new Error('El archivo no es una imagen válida')); };
      img.src = url;
    });
  }
  function subirArchivos(files) {
    files = Array.prototype.filter.call(files, function (x) { return /^image\//.test(x.type); });
    if (!files.length) return;
    var drop = $('#e-drop'); drop.classList.add('busy'); drop.querySelector('b').textContent = 'Subiendo ' + files.length + (files.length === 1 ? ' foto…' : ' fotos…');
    var base = (slugify(f.slug.value || f.nombre.value) || 'producto') + '-' + actual.id.slice(0, 8);
    Promise.all(files.map(function (file, i) {
      return achicar(file).then(function (blob) { return api.subir(base + '/' + Date.now() + '-' + i + '.jpg', blob); });
    })).then(function (urls) {
      fotos = fotos.concat(urls); sucio = true; pintarFotos(); actualizar();
      toast(urls.length === 1 ? 'Foto subida. Acordate de guardar.' : urls.length + ' fotos subidas. Acordate de guardar.');
    }).catch(function (e) { toast('No se pudo subir: ' + e.message, true); })
      .then(function () { drop.classList.remove('busy'); drop.querySelector('b').textContent = 'Arrastrá las fotos acá o tocá para elegirlas'; $('#e-file').value = ''; });
  }
  $('#e-file').addEventListener('change', function () { subirArchivos(this.files); });
  var drop = $('#e-drop');
  ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('over'); }); });
  ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('over'); }); });
  drop.addEventListener('drop', function (e) { subirArchivos(e.dataTransfer.files); });

  /* ---------- datos de prueba (solo con ?demo, para revisar el diseño sin conexión) ---------- */
  function demoApi() {
    var datos = [
      { id: 'a1', codigo: 'UM-0001', nombre: 'Mate de calabaza forrado en cuero', descripcion: 'Calabaza curada a mano, forrada en cuero con virola de alpaca.', categoria: 'Café, Té y Mate', subcategoria: 'Mates y bombillas', temas: ['mate'], pais: 'Argentina', region: 'Buenos Aires', destino: 'buenos-aires', precio_ars: 28000, precio_mxn: 650, precio_usd: 35, tienda_ar: true, tienda_mx: true, international: true, paises_envio: ['Estados Unidos', 'España', 'Chile'], hub: true, hs: '', volumen: '500 unidades por mes', vigencia_hub: '2027-12-31', link_pago: '', fotos: ['../assets/img/blog/mate-de-calabaza-forrado.jpg'], estado: 'Ejemplo', vendedor: 'Umarti Origen', slug: 'mate-de-calabaza-forrado-en-cuero', orden: 0, actualizado: new Date().toISOString() },
      { id: 'a2', codigo: 'UM-0002', nombre: 'Bombilla de acero inoxidable con resorte', descripcion: 'Filtro de resorte desmontable.', categoria: 'Café, Té y Mate', subcategoria: 'Mates y bombillas', temas: ['mate'], pais: 'Argentina', region: 'Buenos Aires', destino: '', precio_ars: 9000, precio_mxn: 220, precio_usd: 12, tienda_ar: true, tienda_mx: true, international: true, paises_envio: ['Estados Unidos'], hub: false, hs: '', volumen: '', vigencia_hub: null, link_pago: '', fotos: [], estado: 'Publicado', vendedor: 'Umarti Origen', slug: 'bombilla-de-acero-inoxidable-con-resorte', orden: 1, actualizado: new Date().toISOString() },
      { id: 'a3', codigo: 'UM-0005', nombre: 'Mate de palo santo', descripcion: '', categoria: 'Café, Té y Mate', subcategoria: 'Mates y bombillas', temas: [], pais: 'Argentina', region: 'Chaco', destino: '', precio_ars: null, precio_mxn: null, precio_usd: null, tienda_ar: true, tienda_mx: false, international: false, paises_envio: [], hub: false, hs: '', volumen: '', vigencia_hub: null, link_pago: '', fotos: ['../assets/img/blog/mate-palo-santo-galeria.jpg'], estado: 'Borrador', vendedor: 'Umarti Origen', slug: 'mate-de-palo-santo', orden: 2, actualizado: new Date().toISOString() }
    ];
    var logueado = /logueado/.test(location.search);
    var R = function (v) { return Promise.resolve(v); };
    return {
      sesion: function () { return R(logueado ? { user: { email: 'admin@umarti.com' } } : null); },
      entrar: function () { logueado = true; return R({ data: { session: {} } }); },
      registrar: function () { return R({ data: {} }); },
      salir: function () { logueado = false; return R(); },
      esAdmin: function () { return R(true); },
      listar: function () { return R(datos.slice()); },
      guardar: function (p, nuevo) { p.actualizado = new Date().toISOString(); if (nuevo) { p.codigo = 'UM-00' + (datos.length + 10); datos.push(p); } else { datos = datos.map(function (o) { return o.id === p.id ? Object.assign(o, p) : o; }); } return R(Object.assign({}, p)); },
      borrar: function (id) { datos = datos.filter(function (o) { return o.id !== id; }); return R(); },
      subir: function (ruta, blob) { return R(URL.createObjectURL(blob)); },
      borrarFotos: function () { return R(); }
    };
  }

  iniciar();
  if (sb) sb.auth.onAuthStateChange(function (ev) { if (ev === 'SIGNED_OUT') mostrar('#v-login'); });
})();
