#!/usr/bin/env python3
"""Agrega ?v=<huella> a los CSS y JS propios en todas las páginas, para que el navegador
no use una versión vieja guardada después de cada cambio. Se corre al final de la construcción.

Uso:  python3 _fuente/versionar_assets.py
"""
import glob, hashlib, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cache = {}


def huella(ruta):
    if ruta not in _cache:
        try:
            _cache[ruta] = hashlib.md5(open(ruta, "rb").read()).hexdigest()[:8]
        except FileNotFoundError:
            _cache[ruta] = None
    return _cache[ruta]


PATRON = re.compile(r'((?:href|src)=")([^"?#]*?assets/(?:css|js|data)/[^"?#]+\.(?:css|js))(?:\?v=[0-9a-f]+)?(")')

def iconos(f, txt):
    """Agrega el ícono de la pestaña del navegador si la página no lo tiene."""
    if 'rel="icon"' in txt:
        return txt
    pre = "../" * (os.path.relpath(f, RAIZ).count(os.sep))
    links = (f'\n  <link rel="icon" href="{pre}favicon.ico" sizes="any">'
             f'\n  <link rel="icon" type="image/png" href="{pre}assets/img/marca/favicon-32.png">'
             f'\n  <link rel="apple-touch-icon" href="{pre}assets/img/marca/apple-touch-icon.png">')
    return re.sub(r'(<meta name="viewport"[^>]*>)', lambda m: m.group(1) + links, txt, count=1)


for f in glob.glob(os.path.join(RAIZ, "**", "*.html"), recursive=True):
    if os.sep + "_fuente" + os.sep in f:
        continue
    txt = iconos(f, open(f, encoding="utf-8").read())
    def cambiar(m):
        h = huella(os.path.normpath(os.path.join(os.path.dirname(f), m.group(2))))
        return f"{m.group(1)}{m.group(2)}?v={h}{m.group(3)}" if h else m.group(0)
    nuevo = PATRON.sub(cambiar, txt)
    if nuevo != open(f, encoding="utf-8").read():
        open(f, "w", encoding="utf-8").write(nuevo)
print("ok: versiones de CSS y JS e íconos actualizados")
