/* Tienda: país de compra (Argentina o México), filtros del listado */
(function () {
  var KEY = 'umarti-pais';
  var pais = 'ar';
  try { pais = localStorage.getItem(KEY) || 'ar'; } catch (e) { /* sin almacenamiento */ }
  var p = new URLSearchParams(location.search);
  if (p.get('pais') === 'mx' || p.get('pais') === 'ar') pais = p.get('pais');

  function setPais(v) {
    pais = v;
    try { localStorage.setItem(KEY, v); } catch (e) { /* sin almacenamiento */ }
    document.querySelectorAll('.country-switch button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.pais === v)); });
    document.querySelectorAll('[data-pais-show]').forEach(function (el) { el.hidden = el.dataset.paisShow !== v; });
    document.querySelectorAll('.prod-card[data-ar]').forEach(function (c) {
      c.classList.toggle('no-pais', c.dataset[v] !== '1');
    });
    applyFilter();
  }

  /* filtro por categoría o subcategoría en el listado */
  var grid = document.getElementById('shop-grid');
  var chips = document.querySelectorAll('[data-filtro]');
  var filtro = p.get('sub') || p.get('cat') || '';
  function applyFilter() {
    if (!grid) return;
    var n = 0;
    grid.querySelectorAll('.prod-card').forEach(function (c) {
      var ok = (!filtro || c.dataset.cat === filtro || c.dataset.sub === filtro) && !c.classList.contains('no-pais');
      c.classList.toggle('is-hidden', !ok);
      if (ok) n++;
    });
    chips.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.filtro === filtro)); });
    var cnt = document.getElementById('shop-count');
    if (cnt) cnt.textContent = n === 1 ? '1 producto' : n + ' productos';
    var empty = document.getElementById('shop-empty');
    if (empty) empty.classList.toggle('show', n === 0);
  }
  chips.forEach(function (b) { b.addEventListener('click', function () { filtro = b.dataset.filtro; applyFilter(); }); });

  document.querySelectorAll('.country-switch button').forEach(function (b) {
    b.addEventListener('click', function () { setPais(b.dataset.pais); });
  });
  document.querySelectorAll('.btn-buy[aria-disabled="true"]').forEach(function (b) {
    b.addEventListener('click', function (e) { e.preventDefault(); });
  });
  setPais(pais);
})();
