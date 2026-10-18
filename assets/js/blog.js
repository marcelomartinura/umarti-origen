/* Blog: buscador y filtro por subcategoría o tema en los listados */
(function () {
  var grid = document.getElementById('b-grid');
  if (!grid) return;
  var q = document.getElementById('b-q');
  var chips = document.querySelectorAll('button[data-sub]');
  var count = document.getElementById('b-count');
  var empty = document.getElementById('b-empty');
  var sub = '';

  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }

  function apply() {
    var tokens = q ? norm(q.value).split(/\s+/).filter(Boolean) : [];
    var n = 0;
    grid.querySelectorAll('.post-card').forEach(function (c) {
      var t = norm(c.dataset.texto);
      var ok = tokens.every(function (k) { return t.indexOf(k) > -1; }) && (!sub || c.dataset.sub === sub);
      c.classList.toggle('is-hidden', !ok);
      if (ok) n++;
    });
    if (count) count.textContent = n === 1 ? '1 nota' : n + ' notas';
    if (empty) empty.classList.toggle('show', n === 0);
    chips.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.sub === sub)); });
    var p = new URLSearchParams();
    if (q && q.value.trim()) p.set('q', q.value.trim());
    if (sub) p.set('sub', sub);
    try { history.replaceState(null, '', location.pathname + (p.toString() ? '?' + p : '')); } catch (e) { /* vista previa */ }
  }

  chips.forEach(function (b) { b.addEventListener('click', function () { sub = b.dataset.sub; apply(); }); });
  if (q) q.addEventListener('input', apply);
  var p = new URLSearchParams(location.search);
  if (q && p.get('q')) q.value = p.get('q');
  if (p.get('sub')) sub = p.get('sub');
  apply();
})();
