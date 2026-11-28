/* Portada: suscripción a novedades por correo (función "suscribir" en Supabase) */
(function () {
  'use strict';
  var f = document.getElementById('h-sus'); if (!f) return;
  var msg = document.querySelector('.h-sus-msg');
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var correo = f.correo.value.trim();
    if (!f.checkValidity() || !correo) { msg.textContent = 'Escribí un correo válido.'; msg.className = 'h-sus-msg err'; return; }
    var b = f.querySelector('button'); b.disabled = true; msg.textContent = 'Enviando…'; msg.className = 'h-sus-msg';
    fetch(f.dataset.url + '/rest/v1/rpc/suscribir', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: f.dataset.key, Authorization: 'Bearer ' + f.dataset.key },
      body: JSON.stringify({ p_correo: correo, p_origen: 'portada' })
    }).then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
      .then(function (ok) {
        if (ok === true) { f.reset(); msg.textContent = '¡Listo! Ya estás suscripto. Te vamos a escribir con las novedades.'; msg.className = 'h-sus-msg ok'; }
        else { msg.textContent = 'Revisá el correo: parece que no es válido.'; msg.className = 'h-sus-msg err'; }
      })
      .catch(function () { msg.textContent = 'No se pudo enviar. Probá de nuevo en un rato.'; msg.className = 'h-sus-msg err'; })
      .then(function () { b.disabled = false; });
  });
})();
