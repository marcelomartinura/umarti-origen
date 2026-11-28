/* Mi cuenta (compradores): ingreso, registro y panel con Supabase Auth + tabla "perfiles" */
(function () {
  'use strict';
  var B = document.body, $ = function (s, r) { return (r || document).querySelector(s); }, $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var cargando = $('#mc-cargando'), fuera = $('#mc-fuera'), dentro = $('#mc-dentro'), card = $('#acceso');
  if (!window.supabase) { cargando.textContent = 'No se pudo conectar. Revisá tu conexión a internet y recargá la página.'; return; }
  var sb = window.supabase.createClient(B.dataset.sbUrl, B.dataset.sbKey);
  var AQUI = location.origin + location.pathname;
  var VOLVER = new URLSearchParams(location.search).get('volver');
  var AQUI_VOLVER = AQUI + (VOLVER ? '?volver=' + encodeURIComponent(VOLVER) : '');
  var usuario = null, perfil = null, recuperando = /type=recovery/.test(location.hash) || /nueva-clave/.test(location.search);

  function leerLS(k) { try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch (e) { return []; } }
  function guardarLS(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* sin almacenamiento */ } }
  function msg(form, txt, tipo) { var m = $('.mc-msg', form); if (m) { m.textContent = txt || ''; m.className = 'mc-msg' + (tipo ? ' ' + tipo : ''); } }
  function ocupado(form, si) { var b = $('button[type=submit]', form); if (b) { b.disabled = si; } }
  function traducir(e) {
    var t = (e && e.message) || String(e);
    if (/Invalid login credentials/i.test(t)) return 'Correo o contraseña incorrectos.';
    if (/Email not confirmed/i.test(t)) return 'Todavía no confirmaste tu correo. Buscá el enlace que te mandamos (o pedí que te lo reenviemos).';
    if (/already registered|already been registered|User already/i.test(t)) return 'Ya hay una cuenta con ese correo. Probá ingresar o recuperar tu contraseña.';
    if (/Password should be|at least/i.test(t)) return 'La contraseña tiene que tener al menos 8 caracteres.';
    if (/rate limit|too many|security purposes/i.test(t)) return 'Hiciste muchos intentos seguidos. Esperá unos minutos y probá de nuevo.';
    if (/same.*password|different from the old/i.test(t)) return 'La nueva contraseña tiene que ser distinta de la anterior.';
    if (/Failed to fetch|NetworkError/i.test(t)) return 'No hay conexión. Revisá internet y probá de nuevo.';
    return 'No se pudo completar: ' + t;
  }

  /* ---------- acceso (sin sesión) ---------- */
  function panelAcceso(p) {
    $$('[data-panel]', card).forEach(function (x) { x.hidden = x.dataset.panel !== p; });
    $('.ac-tabs', card).hidden = !(p === 'in' || p === 'up');
    $$('.ac-tabs [data-tab]', card).forEach(function (b) { b.setAttribute('aria-selected', String(b.dataset.tab === p)); });
  }
  function mostrarFuera(p) { cargando.hidden = true; dentro.hidden = true; fuera.hidden = false; panelAcceso(p || 'in'); }
  $$('.ac-tabs [data-tab]', card).forEach(function (b) { b.addEventListener('click', function () { panelAcceso(b.dataset.tab); }); });
  $$('[data-ir]', card).forEach(function (b) { b.addEventListener('click', function () { panelAcceso(b.dataset.ir); }); });
  function aviso(t) { var a = $('#mc-aviso'); a.textContent = t; a.hidden = !t; }

  var fIn = $('[data-panel=in]', card), fUp = $('[data-panel=up]', card), fOlv = $('[data-panel=olvide]', card), fNueva = $('[data-panel=nueva]', card);
  fIn.addEventListener('submit', function (e) {
    e.preventDefault(); if (!fIn.checkValidity()) { fIn.reportValidity(); return; }
    ocupado(fIn, true); msg(fIn, 'Ingresando…');
    sb.auth.signInWithPassword({ email: fIn.email.value.trim(), password: fIn.pass.value }).then(function (r) {
      if (r.error) throw r.error; msg(fIn, '');
    }).catch(function (er) { msg(fIn, traducir(er), 'err'); }).then(function () { ocupado(fIn, false); });
  });
  var ultimoMail = '';
  fUp.addEventListener('submit', function (e) {
    e.preventDefault(); if (!fUp.checkValidity()) { fUp.reportValidity(); return; }
    ocupado(fUp, true); msg(fUp, 'Creando tu cuenta…');
    ultimoMail = fUp.email.value.trim();
    sb.auth.signUp({ email: ultimoMail, password: fUp.pass.value, options: {
      emailRedirectTo: AQUI_VOLVER, data: { nombre: fUp.nombre.value.trim(), pais: fUp.pais.value, novedades: fUp.novedades.checked } } })
      .then(function (r) {
        if (r.error) throw r.error;
        if (r.data && r.data.user && r.data.user.identities && !r.data.user.identities.length) throw new Error('User already registered');
        msg(fUp, '');
        if (!r.data.session) { $('[data-mail]', card).textContent = ultimoMail; panelAcceso('revisa'); }
      }).catch(function (er) { msg(fUp, traducir(er), 'err'); }).then(function () { ocupado(fUp, false); });
  });
  $('[data-reenviar]', card).addEventListener('click', function () {
    var b = this; b.disabled = true;
    sb.auth.resend({ type: 'signup', email: ultimoMail, options: { emailRedirectTo: AQUI } }).then(function (r) {
      b.textContent = r.error ? traducir(r.error) : 'Listo, te lo mandamos de nuevo';
    });
  });
  fOlv.addEventListener('submit', function (e) {
    e.preventDefault(); if (!fOlv.checkValidity()) { fOlv.reportValidity(); return; }
    ocupado(fOlv, true);
    sb.auth.resetPasswordForEmail(fOlv.email.value.trim(), { redirectTo: AQUI + '?nueva-clave' }).then(function (r) {
      if (r.error) throw r.error;
      msg(fOlv, 'Si hay una cuenta con ese correo, te llega un enlace en unos minutos.', 'ok');
    }).catch(function (er) { msg(fOlv, traducir(er), 'err'); }).then(function () { ocupado(fOlv, false); });
  });
  fNueva.addEventListener('submit', function (e) {
    e.preventDefault(); if (!fNueva.checkValidity()) { fNueva.reportValidity(); return; }
    ocupado(fNueva, true);
    sb.auth.updateUser({ password: fNueva.pass.value }).then(function (r) {
      if (r.error) throw r.error;
      recuperando = false; history.replaceState(null, '', location.pathname);
      entrar(r.data.user);
    }).catch(function (er) { msg(fNueva, traducir(er), 'err'); }).then(function () { ocupado(fNueva, false); });
  });

  /* ---------- panel (con sesión) ---------- */
  function secciones() {
    var k = (location.hash || '#resumen').slice(1);
    if (!$('[data-panel-sec="' + k + '"]')) k = 'resumen';
    $$('[data-panel-sec]').forEach(function (s) { s.hidden = s.dataset.panelSec !== k; });
    $$('.mc-nav [data-sec]').forEach(function (a) { a.toggleAttribute('aria-current', a.dataset.sec === k); });
  }
  window.addEventListener('hashchange', function () { if (usuario) { secciones(); window.scrollTo({ top: 0, behavior: 'smooth' }); } });

  function sincronizarFavoritos() {
    var local = leerLS('umarti-favoritos'), remoto = (perfil && perfil.favoritos) || [];
    var todos = remoto.concat(local.filter(function (x) { return remoto.indexOf(x) < 0; }));
    if (todos.length !== local.length) { guardarLS('umarti-favoritos', todos); document.dispatchEvent(new CustomEvent('umarti:favoritos')); }
    if (perfil && todos.length !== remoto.length) { perfil.favoritos = todos; sb.from('perfiles').update({ favoritos: todos }).eq('id', usuario.id).then(function () {}); }
    return todos;
  }
  document.addEventListener('umarti:favoritos', function () {
    if (!perfil) return;
    var l = leerLS('umarti-favoritos'); perfil.favoritos = l;
    sb.from('perfiles').update({ favoritos: l }).eq('id', usuario.id).then(function () {});
    contadores();
  });

  function contadores() {
    var favs = leerLS('umarti-favoritos'), cart = leerLS('umarti-carrito').reduce(function (n, x) { return n + (+x.cant || 0); }, 0);
    $('[data-n=favoritos]').textContent = favs.length;
    $('[data-n=carrito]').textContent = cart;
    $('[data-fav-vacio]').hidden = favs.length > 0;
    $('[data-fav-ver]').hidden = favs.length === 0;
    $('.mc-fav-txt').textContent = favs.length ? 'Tenés ' + (favs.length === 1 ? '1 producto guardado' : favs.length + ' productos guardados') + '. Quedan guardados en tu cuenta, así los ves en todos tus dispositivos.' : '';
  }

  function pintar() {
    var meta = usuario.user_metadata || {}, nombre = (perfil && perfil.nombre) || meta.nombre || '';
    var completo = [nombre, perfil && perfil.apellido].filter(Boolean).join(' ') || usuario.email;
    $$('[data-nombre]').forEach(function (x) { x.textContent = completo; });
    $$('[data-nombre-corto]').forEach(function (x) { x.textContent = nombre || 'de nuevo'; });
    $$('[data-mail]', dentro).forEach(function (x) { x.textContent = usuario.email; });
    $('[data-iniciales]').textContent = (completo.split(/\s+/).map(function (p) { return p[0]; }).join('').slice(0, 2) || '?').toUpperCase();
    var nov = $('[data-nov]'); if (nov) nov.hidden = !(perfil && perfil.novedades);
    var env = (perfil && perfil.envio) || {};
    $('[data-completa]').hidden = !!(env.calle && env.ciudad);
    var f = $('#mc-datos');
    if (perfil) {
      ['nombre', 'apellido', 'telefono', 'pais', 'tienda'].forEach(function (k) { if (f[k]) f[k].value = perfil[k] || (k === 'tienda' ? 'AR' : ''); });
      ['calle', 'depto', 'cp', 'ciudad', 'provincia', 'indicaciones'].forEach(function (k) { f[k].value = env[k] || ''; });
      f.novedades.checked = !!perfil.novedades;
    }
    guardarLS('umarti-cuenta', { nombre: nombre || usuario.email.split('@')[0] });
    document.dispatchEvent(new CustomEvent('umarti:cuenta'));
    contadores();
  }

  function volverSiCorresponde() {
    var v = new URLSearchParams(location.search).get('volver');
    if (v && /^\/[^\/]/.test(v)) { location.replace(v); return true; }
    return false;
  }
  function entrar(user) {
    if (volverSiCorresponde()) return;
    usuario = user;
    cargando.hidden = true; fuera.hidden = true; dentro.hidden = false;
    secciones();
    sb.from('perfiles').select('*').eq('id', user.id).maybeSingle().then(function (r) {
      perfil = r.data;
      if (!perfil) {  // por si el perfil no se creó al registrarse
        var m = user.user_metadata || {};
        return sb.from('perfiles').insert({ id: user.id, nombre: m.nombre || '', pais: m.pais || '', novedades: !!m.novedades }).select().single()
          .then(function (r2) { perfil = r2.data; });
      }
    }).then(function () { sincronizarFavoritos(); pintar(); });
  }
  function salir() {
    sb.auth.signOut().then(function () {
      try { localStorage.removeItem('umarti-cuenta'); localStorage.removeItem('umarti-favoritos'); } catch (e) { /* nada */ }
      document.dispatchEvent(new CustomEvent('umarti:favoritos'));
      document.dispatchEvent(new CustomEvent('umarti:cuenta'));
      usuario = perfil = null; history.replaceState(null, '', location.pathname); mostrarFuera('in');
    });
  }
  $$('[data-salir]').forEach(function (b) { b.addEventListener('click', salir); });

  var fDatos = $('#mc-datos');
  fDatos.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = fDatos, envio = {};
    ['calle', 'depto', 'cp', 'ciudad', 'provincia', 'indicaciones'].forEach(function (k) { envio[k] = f[k].value.trim(); });
    var cambios = { nombre: f.nombre.value.trim(), apellido: f.apellido.value.trim(), telefono: f.telefono.value.trim(), pais: f.pais.value,
      tienda: f.tienda.value || 'AR', novedades: f.novedades.checked, envio: envio, actualizado: new Date().toISOString() };
    ocupado(f, true); msg(f, 'Guardando…');
    sb.from('perfiles').update(cambios).eq('id', usuario.id).select().single().then(function (r) {
      if (r.error) throw r.error; perfil = r.data; pintar(); msg(f, 'Listo, guardamos tus datos.', 'ok');
    }).catch(function (er) { msg(f, traducir(er), 'err'); }).then(function () { ocupado(f, false); });
  });
  var fClave = $('#mc-clave');
  fClave.addEventListener('submit', function (e) {
    e.preventDefault(); if (!fClave.checkValidity()) { fClave.reportValidity(); return; }
    if (fClave.pass.value !== fClave.pass2.value) { msg(fClave, 'Las dos contraseñas no coinciden.', 'err'); return; }
    ocupado(fClave, true);
    sb.auth.updateUser({ password: fClave.pass.value }).then(function (r) {
      if (r.error) throw r.error; fClave.reset(); msg(fClave, 'Listo, cambiamos tu contraseña.', 'ok');
    }).catch(function (er) { msg(fClave, traducir(er), 'err'); }).then(function () { ocupado(fClave, false); });
  });

  /* ---------- arranque ---------- */
  sb.auth.onAuthStateChange(function (ev, sesion) {
    if (ev === 'PASSWORD_RECOVERY') { recuperando = true; mostrarFuera('nueva'); return; }
    if (ev === 'SIGNED_IN' && sesion && !recuperando && (!usuario || usuario.id !== sesion.user.id)) entrar(sesion.user);
    if (ev === 'SIGNED_OUT') { usuario = null; }
  });
  sb.auth.getSession().then(function (r) {
    var s = r.data && r.data.session;
    if (recuperando && s) { mostrarFuera('nueva'); return; }
    if (s) { entrar(s.user); return; }
    var q = new URLSearchParams(location.search);
    if (/error_description=/.test(location.hash)) aviso('El enlace venció o ya se usó. Pedí uno nuevo.');
    else if (q.get('desde') === 'cupones') aviso('Creá tu cuenta y te avisamos cuando haya cupones.');
    else if (q.get('motivo') === 'favoritos') aviso('Ingresá o creá tu cuenta gratis para guardar tus favoritos.');
    else if (q.get('motivo') === 'carrito') aviso('Ingresá o creá tu cuenta gratis para usar el carrito.');
    mostrarFuera(q.has('crear') ? 'up' : 'in');
  });
})();
