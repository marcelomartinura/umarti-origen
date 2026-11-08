"""Estampa la marca de agua de Umarti Origen en fotos de productos.

Uso: python3 _fuente/tienda/marca_agua.py foto1.jpg [foto2.jpg ...] [--sufijo]
Con --sufijo guarda como <nombre>-um.jpg (así el panel sabe que ya tiene marca); si no, sobrescribe.
La misma marca y proporciones las usa el panel al subir fotos (assets/js/panel.js).
"""
import os, sys
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MARCA = os.path.join(RAIZ, "assets", "img", "marca", "marca-agua.png")
ANCHO, OPACIDAD = 0.56, 0.5   # ancho relativo a la foto y opacidad


def estampar(ruta, destino):
    im = Image.open(ruta).convert("RGB")
    m = Image.open(MARCA).convert("RGBA")
    w = int(im.width * ANCHO); h = int(m.height * w / m.width)
    m = m.resize((w, h), Image.LANCZOS)
    a = m.getchannel("A").point(lambda v: int(v * OPACIDAD)); m.putalpha(a)
    im.paste(m, ((im.width - w) // 2, (im.height - h) // 2), m)
    im.save(destino, "JPEG", quality=88)


if __name__ == "__main__":
    suf = "--sufijo" in sys.argv
    for r in [x for x in sys.argv[1:] if not x.startswith("--")]:
        d = r[:-4] + "-um.jpg" if suf else r
        estampar(r, d); print(d)
