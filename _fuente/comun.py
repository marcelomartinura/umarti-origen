"""Piezas compartidas por los generadores: encabezado, pie, fuentes y utilidades."""
import os, re, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

# Cuando esté el dominio definitivo, completarlo (ej. "https://umartiorigen.com") para generar
# direcciones canónicas y migas de pan para Google.
SITIO = "https://umartiorigen.com"

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
         f'<span class="eco-chip eco-chip-pro"><img src="{img}ecosistema/logo-profesionales.svg" alt="Umarti Digital Profesionales" width="150" height="36"></span>', "Red de profesionales", ""),
        (None, f'<img class="eco-av" src="{img}ecosistema/avatar-motors.jpg" alt="" width="56" height="56">',
         f'<span class="eco-chip"><img src="{img}ecosistema/logo-motors.png" alt="Umarti Motors" width="96" height="37"></span>', "Marketplace de movilidad", "Próximamente"),
        ("https://www.umartiorigen.com", f'<img class="eco-av eco-av-origen" src="{img}ecosistema/avatar-origen.jpg" alt="" width="56" height="56">',
         f'<span class="eco-chip eco-chip-origen"><img src="{img}marca/icono.png" alt="" width="26" height="24"><span><b>Umarti</b><b>Origen</b></span></span>', "Tienda y Mercados Globales", ""),
    ]
    out = []
    for link, av, nombre, txt, pronto in items:
        cuerpo = f'{av}<span class="eco-txt"><span class="eco-name">{nombre}</span><small>{txt}</small>{f"<em>{pronto}</em>" if pronto else ""}</span>'
        propio = link and "umartiorigen.com" in link   # este mismo sitio: se abre en la misma pestaña
        attrs = "" if propio else ' target="_blank" rel="noopener"'
        out.append(f'<a class="eco-item" href="{link}"{attrs}>{cuerpo}</a>' if link else f'<div class="eco-item">{cuerpo}</div>')
    return f'''      <div class="eco-band" aria-label="Ecosistema Umarti">
        <span class="eco-tit">Ecosistema <b>Umarti</b></span>
        <div class="eco-items">{"".join(out)}</div>
      </div>'''


PROFESIONALES_URL = "https://profesionales.umartidigital.com/"


def banner_profesionales(prefijo, ubicacion, compacto=False):
    """Banner de Umarti Digital Profesionales (sitios web para negocios). `ubicacion` va en el link para medir de dónde llegan."""
    img = prefijo + "assets/img/"
    url = f"{PROFESIONALES_URL}?utm_source=umartiorigen&utm_medium=banner&utm_campaign={ubicacion}"
    chk = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    feats = [(chk + '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>', "Diseño a medida"),
             (chk + '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c.8-3.4 3.2-5 6-5s5.2 1.6 6 5M15 15c2.4 0 4.4 1.2 5.5 4"/></svg>', "Acompañamiento total"),
             (chk + '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>', "Rápido y accesible")]
    feat = "".join(f'<li>{i}<span>{t}</span></li>' for i, t in feats)
    return f'''      <aside class="bp{' bp-compacto' if compacto else ''}" aria-label="Umarti Digital Profesionales: sitios web para tu negocio">
        <a class="bp-in" href="{url}" target="_blank" rel="noopener">
          <span class="bp-txt">
            <span class="bp-logos"><img src="{img}marca/icono-blanco.png" alt="" width="30" height="27"><b>Umarti<br>Origen</b><i></i><img class="bp-pro" src="{img}banners/logo-profesionales-blanco.svg" alt="Umarti Digital Profesionales" width="150" height="36"></span>
            <strong>Tu <em>sitio web</em> como lo soñaste</strong>
            <span class="bp-sub">Te lo armamos sin que te ocupes de nada y a <mark>muy bajo costo</mark>, para que tu negocio tenga presencia en internet.</span>
            <ul class="bp-feat">{feat}</ul>
            <span class="bp-cta">Conocé Umarti Profesionales <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>
          </span>
          <span class="bp-img"><img src="{img}banners/profesionales-laptop.jpg" alt="" loading="lazy" width="676" height="660"></span>
        </a>
        <span class="bp-tag">Ecosistema Umarti</span>
      </aside>'''


FACEBOOK = "https://www.facebook.com/umartiorigen"
REDES = f'''
        <div class="foot-redes"><span>Seguinos</span>
          <a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Umarti Origen en Facebook" title="Facebook"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M13.5 21v-7.5h2.6l.4-3.1h-3v-2c0-.9.3-1.5 1.6-1.5h1.6V4.1c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4v2.3H7.9v3.1h2.6V21h3z"/></svg>Facebook</a>
        </div>'''


def footer(prefijo, tienda=False):
    """tienda=True agrega el botón de arrepentimiento y el link a Defensa del Consumidor (solo en las páginas de la Tienda)."""
    consumo = f'''
      <div class="foot-consumo">
        <a class="btn-arrep" href="{prefijo}legal/arrepentimiento/">Botón de arrepentimiento</a>
        <a class="def-cons" href="{DEFENSA_CONSUMIDOR}" target="_blank" rel="noopener">Defensa de las y los Consumidores. Para reclamos <b>ingrese aquí</b></a>
      </div>''' if tienda else ""
    return f'''  <footer>
    <div class="wrap foot foot-top">
      <div class="foot-marca">
        <a href="{prefijo or './'}" class="logo logo-foot" aria-label="Umarti Origen, ir al inicio"><img class="logo-ico" src="{prefijo}assets/img/marca/icono.png" alt="" width="259" height="236"><span class="logo-txt"><b>Umarti</b><b>Origen</b></span></a>
        <p>Tienda &amp; Mercados Globales</p>{REDES}
      </div>
{ecosistema(prefijo)}
    </div>
    <div class="wrap foot-legal">
      <nav aria-label="Información legal">
        <a href="{prefijo}legal/terminos/">Términos y Privacidad</a>
        <a href="{prefijo}legal/cookies/">Cookies</a>
        <a href="{prefijo}envios/">Envíos</a>
        <span class="foot-copy">© 2026 Umarti · <a href="{prefijo}publicidad/">Anunciá en Umarti</a></span>
      </nav>{consumo}
    </div>
  </footer>'''


def escribir(ruta_relativa, contenido):
    ruta = os.path.join(RAIZ, ruta_relativa)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    print("ok", ruta_relativa)
