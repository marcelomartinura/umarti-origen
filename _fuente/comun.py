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
    h = re.sub(r'src="(assets/[^"]*)"', lambda m: f'src="{prefijo}{m.group(1)}"', h)
    return re.sub(r'href="([^"]*)"', fix, h)


DEFENSA_CONSUMIDOR = "https://www.argentina.gob.ar/produccion/defensadelconsumidor/formulario"


def ecosistema(prefijo):
    """Franja del Ecosistema Umarti al pie de todas las páginas."""
    img = prefijo + "assets/img/"
    items = [
        ("https://www.umartidigital.com", f'<img class="eco-av" src="{img}ecosistema/avatar-digital.jpg" alt="" width="56" height="56">',
         f'<img class="eco-logo" src="{img}ecosistema/logo-digital.png" alt="Umarti Digital" width="120" height="38">', "Consultoría y evolución digital", ""),
        ("https://profesionales.umartidigital.com/", f'<img class="eco-av" src="{img}ecosistema/avatar-digital.jpg" alt="" width="56" height="56">',
         "<b>Umarti Digital</b><b>Profesionales</b>", "Red de profesionales", ""),
        (None, f'<img class="eco-av" src="{img}ecosistema/avatar-motors.jpg" alt="" width="56" height="56">',
         "<b>Umarti Motors</b>", "Marketplace de movilidad", "Próximamente"),
        (None, f'<span class="eco-av eco-av-ico"><img src="{img}marca/icono.png" alt="" width="40" height="36"></span>',
         "<b>Umarti Origen</b>", "Tienda y Mercados Globales", "Próximamente"),
    ]
    out = []
    for link, av, nombre, txt, pronto in items:
        cuerpo = f'{av}<span class="eco-txt"><span class="eco-name">{nombre}</span><small>{txt}</small>{f"<em>{pronto}</em>" if pronto else ""}</span>'
        out.append(f'<a class="eco-item" href="{link}" target="_blank" rel="noopener">{cuerpo}</a>' if link else f'<div class="eco-item">{cuerpo}</div>')
    return f'''    <div class="wrap">
      <div class="eco-band" aria-label="Ecosistema Umarti">
        <span class="eco-tit">Ecosistema<br><b>Umarti</b></span>
        <div class="eco-items">{"".join(out)}</div>
      </div>
    </div>'''


def footer(prefijo):
    return f'''  <footer>
{ecosistema(prefijo)}
    <div class="wrap foot">
      <div>
        <a href="{prefijo or './'}" class="logo logo-foot" aria-label="Umarti Origen, ir al inicio"><img class="logo-ico" src="{prefijo}assets/img/marca/icono.png" alt="" width="259" height="236"><span class="logo-txt"><b>Umarti</b><b>Origen</b></span></a>
        <p style="margin-top:8px">Tienda, comercio exterior y viajes.</p>
      </div>
      <p>© 2026 Umarti · <a href="{prefijo}publicidad/">Anunciá en Umarti</a></p>
    </div>
    <div class="wrap foot-legal">
      <nav aria-label="Información legal">
        <a href="{prefijo}legal/terminos/">Términos y condiciones</a>
        <a href="{prefijo}legal/privacidad/">Privacidad</a>
        <a href="{prefijo}legal/cookies/">Cookies</a>
        <a href="{prefijo}envios/">Envíos</a>
      </nav>
      <div class="foot-consumo">
        <a class="btn-arrep" href="{prefijo}legal/arrepentimiento/">Botón de arrepentimiento</a>
        <a class="def-cons" href="{DEFENSA_CONSUMIDOR}" target="_blank" rel="noopener">Defensa de las y los Consumidores. Para reclamos <b>ingrese aquí</b></a>
      </div>
    </div>
  </footer>'''


def escribir(ruta_relativa, contenido):
    ruta = os.path.join(RAIZ, ruta_relativa)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    print("ok", ruta_relativa)
