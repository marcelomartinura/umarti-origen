/* Botón de arrepentimiento (prototipo: todavía no envía datos) */
(function () {
  var f = document.getElementById('arr-form');
  if (!f) return;
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    f.querySelector('.arr-ok').hidden = false;
    f.querySelector('button[type=submit]').disabled = true;
  });
})();
