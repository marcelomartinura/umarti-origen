/* Viajes: filtro de destinos y planificador (prototipo, sin envío) */
(function () {
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }

  /* ---------- filtro de destinos ---------- */
  var grid = document.getElementById('dest-grid');
  if (grid) {
    var q = document.getElementById('v-q');
    var chips = document.querySelectorAll('[data-tipo]');
    var count = document.getElementById('v-count');
    var tipo = '';
    var apply = function () {
      var t = q ? norm(q.value).trim() : '';
      var n = 0;
      grid.querySelectorAll('.dest-card').forEach(function (c) {
        var ok = (!t || norm(c.dataset.texto).indexOf(t) > -1) && (!tipo || c.dataset.tipos.split('|').indexOf(tipo) > -1);
        c.classList.toggle('is-hidden', !ok);
        if (ok) n++;
      });
      if (count) count.textContent = n === 1 ? '1 destino' : n + ' destinos';
      chips.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.tipo === tipo)); });
    };
    chips.forEach(function (b) { b.addEventListener('click', function () { tipo = b.dataset.tipo; apply(); }); });
    if (q) q.addEventListener('input', apply);
    var p = new URLSearchParams(location.search);
    if (p.get('tipo')) tipo = p.get('tipo');
    if (q && p.get('q')) q.value = p.get('q');
    apply();
  }

  /* ---------- planificador ---------- */
  var form = document.getElementById('plan-form');
  if (form) {
    var p2 = new URLSearchParams(location.search);
    var dest = document.getElementById('pl-dest');
    if (p2.get('destino') && dest) dest.value = p2.get('destino');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var nombre = (document.getElementById('pl-nombre').value || '').trim().split(' ')[0];
      document.getElementById('plan-step-form').hidden = true;
      var ok = document.getElementById('plan-step-ok');
      ok.hidden = false;
      var h = ok.querySelector('h3');
      h.textContent = nombre ? '¡Gracias, ' + nombre + '!' : '¡Gracias!';
      ok.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    var again = document.getElementById('plan-again');
    if (again) again.addEventListener('click', function () {
      form.reset();
      document.getElementById('plan-step-form').hidden = false;
      document.getElementById('plan-step-ok').hidden = true;
    });
  }
})();
