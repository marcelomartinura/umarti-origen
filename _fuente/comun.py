"""Piezas compartidas por los generadores: encabezado, pie, fuentes y utilidades."""
import os, re, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

# Cuando esté el dominio definitivo, completarlo (ej. "https://umartiorigen.com") para generar
# direcciones canónicas y migas de pan para Google.
SITIO = ""

FUENTES = '''  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'''

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def slug(texto):
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def fecha_larga(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} de {MESES[int(m) - 1]} de {y}"


def header(prefijo):
    """Copia el encabezado de la portada y ajusta los enlaces relativos a la profundidad de la página."""
    s = open(os.path.join(RAIZ, "index.html"), encoding="utf-8").read()
    h = re.search(r'  <header class="site-header".*?</header>', s, re.S).group(0)

    def fix(m):
        v = m.group(1)
        if v.startswith(("http", "mailto:", "/")):
            return m.group(0)
        if v == "#":
            return f'href="{prefijo or "./"}"'
        return f'href="{prefijo}{v}"'
    return re.sub(r'href="([^"]*)"', fix, h)


def footer(prefijo):
    return f'''  <footer>
    <div class="wrap foot">
      <div>
        <a href="{prefijo or './'}" class="logo">Umarti <span style="color:var(--terra)">Origen</span></a>
        <p style="margin-top:8px">Tienda, comercio exterior y viajes.</p>
      </div>
      <ul class="eco">
        <li><strong>Umarti Origen</strong></li>
        <li>Umarti Movilidad</li>
        <li>Umarti Digital</li>
      </ul>
      <p>© 2026 Umarti · <a href="{prefijo}publicidad/">Anunciá en Umarti</a></p>
    </div>
  </footer>'''


def escribir(ruta_relativa, contenido):
    ruta = os.path.join(RAIZ, ruta_relativa)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    print("ok", ruta_relativa)
