#!/usr/bin/env python3
"""Genera la Tienda, International Shop, las páginas de tema, envíos y favoritos a partir de _fuente/tienda/catalogo.json

Uso:  python3 _fuente/construir_tienda.py
El catálogo sale de las pestañas Catálogo, Temas y Envíos de la hoja 'Plan Ecommerce' (ver tienda/importar_hoja.py).
Genera, por país de origen (hoy solo Argentina):
  argentina/                     portada del país
  argentina/tienda/              tienda local, y argentina/tienda/<producto>/
  argentina/envios/              envíos dentro del país
y además, para todos los países: <tema>/ (por ejemplo mate/), international-shop/, international-shop/envios/, envios/ (índice) y favoritos/.
Los productos con "Hub de Oportunidades: Sí" también aparecen en Productos de exportación (lo hace construir.py).
"""
from urllib.parse import quote
import glob, html, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comun  # noqa: E402
from comun import escribir, slug, SITIO  # noqa: E402

esc = html.escape
CATALOGO = os.path.join(AQUI, "tienda", "catalogo.json")

SECTOR_HUB = {"Café, Té y Mate": "Alimentos y bebidas", "Bebidas": "Alimentos y bebidas", "Alimentos": "Alimentos y bebidas",
              "Regalos y Kits": "Manufacturas", "Moda": "Moda y textil", "Tecnología": "Tecnología", "Salud y Bienestar": "Salud",
              "Hogar y Cocina": "Manufacturas", "Herramientas y Jardín": "Manufacturas", "Limpieza e Higiene": "Manufacturas"}
MONEDA_PAIS = {"Argentina": "ars", "México": "mxn"}
# Mercados locales abiertos: país -> (campo que lo activa, campo de precio, moneda).
# México todavía no tiene tienda local: sus compradores usan International Shop.
# Cuando abra, se agrega ("México": ("tienda_mx", "precio_mxn", "mxn")) y listo.
TIENDAS_LOCALES = {"Argentina": ("tienda_ar", "precio_ars", "ars")}


def en_tienda_local(p):
    return any(p.get(flag) for flag, _, _ in TIENDAS_LOCALES.values())


def cargar():
    d = json.load(open(CATALOGO, encoding="utf-8"))
    return d["productos"], d["temas"]


def cargar_envios():
    return json.load(open(CATALOGO, encoding="utf-8")).get("envios", [])


PAIS_SLUG = {"Argentina": "argentina", "México": "mexico"}


def p_pais(pais="Argentina"): return PAIS_SLUG.get(pais, "argentina") + "/"
def p_tienda(pais="Argentina"): return p_pais(pais) + "tienda/"
def p_prod(p): return f"{p_tienda(p['pais'])}{p['slug']}/"
def p_tema(t): return f"{t['clave']}/"   # los temas son contenido global
def p_envio(slug_zona):
    """Envíos internacionales viven en International Shop; los locales, en la carpeta del país."""
    return "international-shop/envios/" if slug_zona == "internacional" else f"{slug_zona}/envios/"


def productos_para_hub():
    """Productos del Catálogo marcados para el Hub, con el formato de Productos de exportación."""
    productos, _ = cargar()
    out = []
    for p in productos:
        if not p["hub"]:
            continue
        out.append(dict(cod=p["codigo"], nombre=p["nombre"], hs=p["hs"], sector=SECTOR_HUB.get(p["categoria"], "Manufacturas"),
                        pais=p["pais"], region=p["region"] or p["pais"], destinos=", ".join(p["paises_envio"]) or "A convenir",
                        vol=p["volumen"] or "A convenir", vence=p["vigencia_hub"] or "2027-12-31",
                        claves=" ".join(p["temas"] + [p["subcategoria"], p["descripcion"]]), tienda_url=p_prod(p)))
    return out


def rel(depth, path=""):
    return ("../" * depth) + path if depth or path else "./"


# ---------- precios y envíos ----------
def precio(v, moneda):
    if v is None:
        return ""
    n = f"{v:,.0f}".replace(",", ".")
    return {"ars": f"$ {n}", "mxn": f"$ {n}", "usd": f"US$ {n}"}[moneda]


def precio_principal(p):
    """Precio en la moneda del país de origen; si no hay, el de International Shop."""
    m = MONEDA_PAIS.get(p["pais"])
    if m and p.get(f"precio_{m}") is not None and p.get(f"tienda_{m[:2]}"):
        return precio(p[f"precio_{m}"], m), m.upper()
    for flag, campo, m in TIENDAS_LOCALES.values():
        if p.get(flag) and p.get(campo) is not None:
            return precio(p[campo], m), m.upper()
    return precio(p["precio_usd"], "usd"), "USD"


def zonas(p):
    """Zonas con envío disponible, empezando por el país de origen."""
    z = []
    nacionales = [(pais, flag, campo, mon) for pais, (flag, campo, mon) in TIENDAS_LOCALES.items()]
    nacionales.sort(key=lambda x: x[0] != p["pais"])
    for nombre, flag, campo, mon in nacionales:
        if p.get(flag):
            z.append(dict(nombre=nombre, slug=slug(nombre), precio=precio(p.get(campo), mon), moneda=mon.upper(), detalle=""))
    if p.get("international"):
        z.append(dict(nombre="Internacional", slug="internacional", precio=precio(p.get("precio_usd"), "usd"), moneda="USD",
                      detalle=("A " + ", ".join(p["paises_envio"])) if p["paises_envio"] else ""))
    return z


# ---------- fotos y carrusel ----------
ICON_TRUCK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h11v10H3zM14 9h4l3 3v4h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/></svg>'
ICON_HEART = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>'
ICON_CAM = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg>'


def slides(p, cb, cv):
    if p.get("fotos"):
        return [f'<img src="{esc(u)}" alt="{esc(p["nombre"])}, foto {i + 1}" loading="lazy">' for i, u in enumerate(p["fotos"])]
    c1, c2 = cb.COLORES.get(p["categoria"], cb.COLORES["Alimentos"])
    out = [f'<div class="cover" data-glyph="{esc(p["nombre"][0])}" style="--c1:{c1};--c2:{c2}"><span>{esc(p["subcategoria"])}</span></div>']
    dest = next((x for x in cv.DESTINOS if x["slug"] == p.get("destino")), None)
    if dest:
        out.append(cv.vcover(dest["colores"], dest["paisaje"], f"Origen: {p['region']}", p["pais"]))
    out.append(f'<div class="slide-soon">{ICON_CAM}<span>Pronto, las fotos reales de este producto</span></div>')
    return out


def carousel(p, cb, cv, href=None, grande=False):
    s = slides(p, cb, cv)
    def envolver(x):
        return f'<a href="{href}" tabindex="-1">{x}</a>' if href else x
    items = "".join(f'<div class="car-slide">{envolver(x)}</div>' for x in s)
    dots = "".join(f'<span class="car-dot{" on" if i == 0 else ""}"></span>' for i in range(len(s))) if len(s) > 1 else ""
    flechas = ('<button class="car-btn prev" type="button" aria-label="Foto anterior">‹</button>'
               '<button class="car-btn next" type="button" aria-label="Foto siguiente">›</button>') if len(s) > 1 else ""
    contador = f'<span class="car-count">1/{len(s)}</span>' if grande and len(s) > 1 else ""
    thumbs = ""
    if grande and len(s) > 1:
        thumbs = '<div class="car-thumbs">' + "".join(
            f'<button type="button" class="car-thumb{" on" if i == 0 else ""}" aria-label="Ver foto {i + 1}">{x}</button>' for i, x in enumerate(s)) + "</div>"
    main = (f'<div class="carousel{" big" if grande else ""}" data-carousel tabindex="0" aria-label="Fotos de {esc(p["nombre"])}">'
            f'<div class="car-track">{items}</div>{flechas}<div class="car-dots">{dots}</div>{contador}</div>')
    return (main, thumbs) if grande else main


def fav(p):
    return f'<button class="fav" type="button" data-fav="{esc(p["codigo"])}" aria-pressed="false" aria-label="Guardar en favoritos">{ICON_HEART}</button>'


def card(p, depth, cb, cv, modo="local"):
    href = rel(depth, p_prod(p))
    ej = '<span class="badge-ej">Ejemplo</span>' if p["estado"] == "Ejemplo" else ""
    if modo == "intl":
        pr, mon = precio(p["precio_usd"], "usd"), "USD"
    else:
        pr, mon = precio_principal(p)
    zs = " · ".join(z["nombre"] for z in zonas(p))
    return f'''        <article class="prod-card" data-cat="{esc(p['categoria'])}" data-sub="{esc(p['subcategoria'])}">
          <div class="prod-media">{ej}{fav(p)}{carousel(p, cb, cv, href)}</div>
          <a class="info" href="{href}">
            <span class="kick">{esc(p['subcategoria'])}</span>
            <h3>{esc(p['nombre'])}</h3>
            <span class="price">{pr}<small>{mon}</small></span>
            <span class="envio">{ICON_TRUCK}<span>Envío disponible <b>{esc(zs)}</b></span></span>
          </a>
        </article>'''


def page(depth, title, desc, main, css, jsonld=None, noindex=False, extra=""):
    pre = rel(depth)
    links = "".join(f'\n  <link rel="stylesheet" href="{pre}assets/css/{c}.css">' for c in ["umarti"] + css)
    ld = f'\n  <script type="application/ld+json">\n{json.dumps(jsonld, ensure_ascii=False, indent=2)}\n  </script>' if jsonld else ""
    robots = '\n  <!-- Contenido de ejemplo o en preparación: se indexa cuando pase a Publicado -->\n  <meta name="robots" content="noindex">' if noindex else ""
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">{robots}
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
{comun.FUENTES}{links}{ld}
</head>
<body>

{comun.header(pre)}

  <main>
{main}
  </main>

{comun.footer(pre)}
{extra}
  <div class="toast" id="toast" role="status"></div>
  <script src="{pre}assets/js/header.js"></script>
  <script src="{pre}assets/data/tienda-indice.js"></script>
  <script src="{pre}assets/js/tienda.js"></script>
</body>
</html>
'''


def crumbs(depth, items):
    import construir_blog
    return construir_blog.crumbs(depth, items)


ICON = {
    "pin": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
    "hub": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h14l-4-4M20 16H6l4 4"/></svg>',
    "tema": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19V5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2zM8 7h6"/></svg>',
    "box": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/></svg>',
    "msg": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v11H8l-4 4z"/></svg>',
}

DIALOGOS = '''  <dialog id="dlg-cant" aria-labelledby="cant-title">
    <div class="dlg-head"><div><h2 id="cant-title">Consultar precio por cantidad</h2><p id="cant-sub"></p></div><button class="dlg-close" type="button" data-close aria-label="Cerrar">×</button></div>
    <div class="dlg-body">
      <form id="cant-form" data-ok="cant-ok">
        <div class="form-grid">
          <div class="field"><label for="c-cant">Cantidad <span class="req">*</span></label><input id="c-cant" type="number" min="2" required placeholder="Ej.: 50"></div>
          <div class="field"><label for="c-dest">País de entrega <span class="req">*</span></label><input id="c-dest" required placeholder="Ej.: México"></div>
          <div class="field"><label for="c-nom">Nombre <span class="req">*</span></label><input id="c-nom" required autocomplete="name"></div>
          <div class="field"><label for="c-emp">Empresa</label><input id="c-emp" autocomplete="organization"></div>
          <div class="field full"><label for="c-mail">Correo <span class="req">*</span></label><input id="c-mail" type="email" required autocomplete="email"></div>
          <div class="field full"><label for="c-msg">Comentarios</label><textarea id="c-msg" placeholder="Fechas, personalización o lo que necesites."></textarea></div>
        </div>
        <div class="form-foot"><small>Te respondemos por correo con un precio para esa cantidad.</small><button class="btn-buy small" type="submit">Enviar consulta</button></div>
      </form>
      <div class="dlg-ok" id="cant-ok" hidden><h3>¡Consulta enviada!</h3><p>En la versión final te llega la cotización por correo. En este prototipo no se envía nada.</p><button class="btn-line-dark" type="button" data-close>Volver al producto</button></div>
    </div>
  </dialog>
  <dialog id="dlg-conv" aria-labelledby="conv-title">
    <div class="dlg-head"><div><h2 id="conv-title">Conversá con el vendedor</h2><p id="conv-sub"></p></div><button class="dlg-close" type="button" data-close aria-label="Cerrar">×</button></div>
    <div class="dlg-body">
      <form id="conv-form" data-ok="conv-ok">
        <div class="form-grid">
          <div class="field"><label for="v-nom">Nombre <span class="req">*</span></label><input id="v-nom" required autocomplete="name"></div>
          <div class="field"><label for="v-mail">Correo <span class="req">*</span></label><input id="v-mail" type="email" required autocomplete="email"></div>
          <div class="field full"><label for="v-msg">Tu mensaje <span class="req">*</span></label><textarea id="v-msg" required placeholder="Preguntá lo que quieras sobre el producto."></textarea></div>
        </div>
        <div class="form-foot"><small>No hace falta estar conectado: el vendedor te responde por correo.</small><button class="btn-buy small" type="submit">Enviar mensaje</button></div>
      </form>
      <div class="dlg-ok" id="conv-ok" hidden><h3>¡Mensaje enviado!</h3><p>En la versión final, el vendedor recibe tu mensaje y te responde por correo. En este prototipo no se envía nada.</p><button class="btn-line-dark" type="button" data-close>Volver al producto</button></div>
    </div>
  </dialog>'''


# ---------- páginas ----------
def listado(productos, cb, cv):
    d = 2
    locales = [p for p in productos if en_tienda_local(p)]
    cats = []
    for p in locales:
        for v in (p["categoria"], p["subcategoria"]):
            if v not in cats:
                cats.append(v)
    chips = '<div class="chip-row" role="group" aria-label="Filtrar"><button type="button" data-filtro="" aria-pressed="true">Todo</button>' + "".join(
        f'<button type="button" data-filtro="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats) + "</div>"
    main = f'''    <div class="wrap">
{crumbs(d, [("Argentina", p_pais()), ("Tienda", None)])}
      <div class="blog-head">
        <span class="eyebrow" style="color:var(--terra)">Tienda Argentina</span>
        <h1>Productos con origen</h1>
        <p>Productos seleccionados de Argentina, con envío a todo el país. Si comprás desde el exterior, los encontrás en <a href="{rel(d, 'international-shop/')}">International Shop</a>.</p>
      </div>
      <div class="shop-tools">{chips}<span class="v-count" id="shop-count"></span></div>
      <div class="prod-grid" id="shop-grid">
{chr(10).join(card(p, d, cb, cv) for p in locales)}
        <p class="shop-empty" id="shop-empty">Todavía no hay productos en esta categoría.</p>
      </div>
      <p class="shop-note">¿Comprás desde otro país? Mirá <a href="{rel(d, 'international-shop/')}">International Shop</a>. · <a href="{rel(d, p_envio('argentina'))}">Condiciones de envío</a></p>
      <div style="height:88px"></div>
    </div>'''
    main = barra_tienda(d, "tienda") + main
    return page(d, "Tienda Argentina | Umarti Origen: mates, yerba y productos con origen",
                "Mates, bombillas, yerba y productos seleccionados de Argentina, con envío en Argentina y al exterior, incluido México.", main, ["blog", "viajes", "tienda"])


ILUSTRACION_INTL = '''<svg viewBox="0 0 440 330" role="img" aria-label="Un paquete viaja desde Argentina, sobre el globo, hacia otros países">
  <defs>
    <radialGradient id="is-mar" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#eef6fc"/><stop offset="1" stop-color="#c9e0f2"/></radialGradient>
    <clipPath id="is-globo"><circle cx="205" cy="185" r="118"/></clipPath>
  </defs>
  <circle cx="205" cy="180" r="140" fill="#74acdf" opacity=".10"/>
  <circle cx="205" cy="185" r="118" fill="url(#is-mar)" stroke="#2f6f8f" stroke-width="2.5"/>
  <g clip-path="url(#is-globo)" fill="#e7dcc6" stroke="#b9a98d" stroke-width="1.2">
    <path d="M150 150c14-8 34-6 42 6 8 12 4 26 10 38 6 14 2 30-6 44-6 10-8 24-14 34-4 8-12 6-12-2 0-14-6-26-12-38-8-16-20-26-20-44 0-16 2-30 12-38z"/>
    <path d="M118 78c18-10 46-14 66-6 14 6 10 20-2 24-14 4-22 14-36 14-14 0-26-8-34-16-6-6-4-12 6-16z"/>
    <path d="M250 96c16-10 40-8 58 4 16 10 26 28 18 40-8 12-26 8-38 16-12 8-10 26-24 30-14 4-24-10-26-24-2-12 4-22 0-34-4-14 0-24 12-32z"/>
  </g>
  <g clip-path="url(#is-globo)" fill="none" stroke="#2f6f8f" stroke-width="1.2" opacity=".35">
    <ellipse cx="205" cy="185" rx="48" ry="118"/><ellipse cx="205" cy="185" rx="92" ry="118"/>
    <path d="M87 145h236M87 185h236M87 225h236"/>
  </g>
  <path d="M182 262c-96-40-74-196 70-214 54-7 98 10 126 30" fill="none" stroke="#b4532a" stroke-width="2.5" stroke-dasharray="7 8" stroke-linecap="round"/>
  <g transform="translate(250 48) rotate(8)">
    <path d="M-14 0h22l10-9h6l-5 9h9l4-4h4l-3 6 3 6h-4l-4-4h-9l5 9h-6L8 4h-22z" fill="#1f1a14"/>
  </g>
  <g transform="translate(176 230)">
    <path d="M0 0v42" stroke="#5a3d27" stroke-width="2.5" stroke-linecap="round"/>
    <rect x="1" y="0" width="36" height="24" rx="2" fill="#74acdf"/><rect x="1" y="8" width="36" height="8" fill="#fff"/>
    <circle cx="19" cy="12" r="3" fill="#f6b40e" stroke="#85340a" stroke-width=".6"/>
    <circle cx="0" cy="44" r="4" fill="#b4532a"/>
  </g>
  <g transform="translate(366 58)">
    <path d="M0 14 26 0l26 14v30L26 58 0 44z" fill="#c9965d"/>
    <path d="M0 14l26 14 26-14M26 28v30" fill="none" stroke="#8c6236" stroke-width="1.5"/>
    <path d="M13 7l26 14v10" fill="none" stroke="#f3e2c3" stroke-width="5"/>
  </g>
</svg>'''


def international(productos, cb, cv):
    d = 1
    intl = [p for p in productos if p["international"]]
    paises = sorted({c for p in intl for c in p["paises_envio"]}, key=slug)
    main = f'''    <div class="wrap">
{crumbs(d, [("International Shop", None)])}
      <section class="is-hero">
        <div class="is-txt">
          <span class="eyebrow" style="color:var(--intl)">International Shop</span>
          <h1>De Argentina al mundo</h1>
          <p>Productos argentinos con envío internacional. Precios en dólares; el costo del envío y los impuestos de importación dependen del país de destino.</p>
          <a class="text-link" href="{rel(d, p_envio('internacional'))}">Ver las condiciones de envío internacional</a>
        </div>
        <div class="is-art">{ILUSTRACION_INTL}</div>
      </section>
      <ol class="is-pasos" aria-label="Cómo funciona">
        <li><span>1</span><div><b>Elegís desde tu país</b><small>Productos con origen, elegidos en Argentina.</small></div></li>
        <li><span>2</span><div><b>Pagás en dólares</b><small>Con medios de pago internacionales.</small></div></li>
        <li><span>3</span><div><b>Te llega a tu casa</b><small>Envío internacional con seguimiento.</small></div></li>
      </ol>
      <div class="prod-grid">
{chr(10).join(card(p, d, cb, cv, "intl") for p in intl)}
      </div>
      <p class="shop-note">¿Comprás por volumen para revender o distribuir? Mirá los <a href="{rel(d, 'productos-de-exportacion/')}">Productos de exportación</a> del Hub de Oportunidades.</p>
      <div style="height:88px"></div>
    </div>'''
    return page(d, "International Shop: productos argentinos con envío internacional | Umarti Origen",
                f"Mate, yerba y productos argentinos con envío a {', '.join(paises)}.", main, ["blog", "viajes", "tienda"])


def notas_relacionadas(p_or_tema, notas, etiquetas=None):
    tags = set(etiquetas or p_or_tema.get("temas", []))
    out = []
    for n in notas:
        s = 0
        if n.get("subcategoria") and n.get("subcategoria") == p_or_tema.get("subcategoria"): s += 3
        if n.get("categoria") and n.get("categoria") == p_or_tema.get("categoria"): s += 1
        s += 2 * len(tags & set(slug(t) for t in n["tags"])) + len(tags & set(n["tags"]))
        if s:
            out.append((s, n))
    return [n for s, n in sorted(out, key=lambda x: -x[0])]


def pagina_producto(p, productos, temas, notas, cb, cv):
    d = 3
    dest = next((x for x in cv.DESTINOS if x["slug"] == p.get("destino")), None)
    pr, mon = precio_principal(p)
    galeria = carousel(p, cb, cv, grande=True)
    def fila(z):
        det = f'<small class="zd">{esc(z["detalle"])}</small>' if z["detalle"] else ""
        return (f'<li><a class="zona" href="{rel(d, p_envio(z["slug"]))}">{esc(z["nombre"])}</a>'
                f'<span class="zp">{z["precio"]} <small>{z["moneda"]}</small></span>{det}</li>')
    filas = "".join(fila(z) for z in zonas(p))
    if p.get("link_pago"):
        comprar = f'<a class="btn-buy" href="{esc(p["link_pago"])}" rel="noopener">Comprar</a>'
    else:
        comprar = '<a class="btn-buy" href="#" aria-disabled="true">Disponible muy pronto</a><p class="buy-hint">Estamos preparando la venta en línea de este producto.</p>'
    comprar += f'<a class="buy-seguro" href="{rel(d, "legal/arrepentimiento/")}">{ICON_LOCK}<span><b>Comprá seguro:</b> pago protegido y 10 días para arrepentirte.</span></a>'
    links = []
    if dest:
        links.append(f'<a class="link-card origen" href="{rel(d, f"viajes/{dest["pais"]}/{dest["slug"]}/")}"><span class="ic">{ICON["pin"]}</span><span><strong>Origen: {esc(p["region"])}, {esc(p["pais"])}</strong><small>Conocé el lugar en la guía de viaje de {esc(dest["nombre"])}</small></span></a>')
    elif p.get("region"):
        links.append(f'<div class="link-card origen"><span class="ic">{ICON["pin"]}</span><span><strong>Origen: {esc(p["region"])}, {esc(p["pais"])}</strong><small>Producto elaborado en {esc(p["pais"])}</small></span></div>')
    for t in temas:
        if t["clave"] in p["temas"]:
            links.append(f'<a class="link-card tema" href="{rel(d, p_tema(t))}"><span class="ic">{ICON["tema"]}</span><span><strong>Todo sobre el {esc(t["nombre"].lower())}</strong><small>Guías, productos, destinos y más en un solo lugar</small></span></a>')
    if p["hub"]:
        links.append(f'<a class="link-card hub" href="{rel(d, "productos-de-exportacion/")}#{p["codigo"].lower()}"><span class="ic">{ICON["hub"]}</span><span><strong>¿Comprás para revender o exportar?</strong><small>Este producto está en Productos de exportación del Hub de Oportunidades</small></span></a>')
    rel_notas = notas_relacionadas(p, notas)[:3]
    otros = [o for o in productos if o is not p and set(o["temas"]) & set(p["temas"])][:4]
    ej = '<span class="badge-ej" style="position:static;display:inline-block;margin-bottom:6px">Producto de ejemplo</span>' if p["estado"] == "Ejemplo" else ""
    main = f'''    <div class="wrap">
{crumbs(d, [("Argentina", p_pais(p["pais"])), ("Tienda", p_tienda(p["pais"])), (p["categoria"], None), (p["subcategoria"], None), (p["nombre"], None)])}
      <section class="pdp">
        <div class="pdp-photo">
          <div class="prod-media">{fav(p)}{galeria[0]}</div>
          {galeria[1]}
        </div>
        <div>
          {ej}
          <p class="kick post-kicker"><b>{esc(p['categoria'])}</b> · {esc(p['subcategoria'])}</p>
          <h1>{esc(p['nombre'])}</h1>
          <p class="lead">{esc(p['descripcion'])}</p>
          <div class="buy-box" data-producto="{esc(p['nombre'])}">
            <div class="buy-price">{pr}<small>{mon}</small></div>
            <div class="envio-box">
              <p class="envio-title">{ICON_TRUCK}<span>Envío disponible</span></p>
              <ul class="zonas">{filas}</ul>
            </div>
            {comprar}
            <button class="btn-outline" type="button" data-dialog="dlg-cant">{ICON["box"]}<span>Consultar precio por cantidad</span></button>
          </div>
          <div class="seller">
            <div class="seller-av">{esc(p['vendedor'][0])}</div>
            <div><small>Vendido por</small><strong>{esc(p['vendedor'])}</strong></div>
            <button class="btn-outline small" type="button" data-dialog="dlg-conv">{ICON["msg"]}<span>Conversá con el vendedor</span></button>
          </div>
          <div class="link-cards">{"".join(links)}</div>
        </div>
      </section>
    </div>
    {"" if not rel_notas else f'''<section class="related">
      <div class="wrap">
        <h2>Aprendé a usarlo y cuidarlo</h2>
{cb.grid(rel_notas, d)}
      </div>
    </section>'''}
    {"" if not otros else f'''<section class="related">
      <div class="wrap">
        <h2>Completá tu ronda</h2>
        <div class="prod-grid">
{chr(10).join(card(o, d, cb, cv) for o in otros)}
        </div>
      </div>
    </section>'''}'''
    ld = None
    if p["estado"] == "Publicado":
        offers = []
        if p["tienda_ar"] and p["precio_ars"]: offers.append({"@type": "Offer", "price": p["precio_ars"], "priceCurrency": "ARS", "availability": "https://schema.org/InStock"})
        if p["international"] and p["precio_usd"]: offers.append({"@type": "Offer", "price": p["precio_usd"], "priceCurrency": "USD", "availability": "https://schema.org/InStock"})
        ld = {"@context": "https://schema.org", "@type": "Product", "name": p["nombre"], "description": p["descripcion"], "sku": p["codigo"],
              "category": f'{p["categoria"]} > {p["subcategoria"]}', "countryOfOrigin": p["pais"], "offers": offers,
              "brand": {"@type": "Brand", "name": p["vendedor"]}}
        if p.get("fotos"): ld["image"] = p["fotos"]
        if SITIO: ld["url"] = f"{SITIO}/{p_prod(p)}"
    if en_tienda_local(p):
        main = barra_tienda(d, "tienda", p["pais"]) + main
    return page(d, f"{p['nombre']} | Tienda Umarti Origen", p["descripcion"], main, ["blog", "viajes", "tienda"], ld,
                noindex=p["estado"] != "Publicado", extra=DIALOGOS)


def pagina_tema(t, productos, notas, cb, cv):
    d = 1
    prods = [p for p in productos if t["clave"] in p["temas"]]
    locales = [p for p in prods if en_tienda_local(p)]
    intl = [p for p in prods if p["international"]]
    hub = [p for p in prods if p["hub"]]
    paises = sorted({c for p in intl for c in p["paises_envio"]}, key=slug)
    rel_notas = notas_relacionadas({"temas": [slug(e) for e in t["etiquetas"]]}, notas, etiquetas=set(t["etiquetas"]) | {slug(e) for e in t["etiquetas"]})
    dests = [x for s in t["destinos"] for x in cv.DESTINOS if x["slug"] == s]
    from datos import BUSQUEDAS
    claves = {slug(w)[:5] for p in prods for w in re.findall(r"\w{4,}", p["nombre"])} | {slug(t["nombre"])[:5]}
    hs4 = {p["hs"][:4] for p in prods if p["hs"]}
    busq = [b for b in BUSQUEDAS if b["tipo"] == "producto" and ((b["hs"] and b["hs"][:4] in hs4) or ({slug(w)[:5] for w in re.findall(r"\w{4,}", b["nombre"])} & claves))]
    nav = [("comprar", "Comprar"), ("international", "International Shop"), ("aprender", "Aprender"), ("viajar", "Viajar al origen"), ("empresas", "Para empresas")]
    hub_items = "".join(f'<a class="hub-item" href="{rel(d, "productos-de-exportacion/")}#{p["codigo"].lower()}"><small>Producto de exportación</small><strong>{esc(p["nombre"])}</strong><span>{esc(p["volumen"] or "Volumen a convenir")}</span></a>' for p in hub)
    hub_items += "".join(f'<a class="hub-item" href="{rel(d, "mesa-de-negociacion/")}#{b["cod"].lower()}"><small>Búsqueda en la Mesa · {esc(b["pais"])}</small><strong>{esc(b["nombre"])}</strong><span>{esc(b["vol"])}</span></a>' for b in busq)
    c1, c2 = cb.COLORES.get("Café, Té y Mate")
    main = f'''    <div class="wrap">
{crumbs(d, [(t["nombre"], None)])}
      <section class="tema-hero" data-glyph="{esc(t['nombre'][0])}" style="--c1:{c1};--c2:{c2}">
        <span class="eyebrow">Todo sobre el {esc(t['nombre'].lower())}</span>
        <h1>{esc(t['nombre'])}</h1>
        <p>{esc(t['bajada'])}</p>
      </section>
      <nav class="tema-nav" aria-label="Secciones">{"".join(f'<a href="#{a}">{n}</a>' for a, n in nav)}</nav>

      <section class="tema-sec" id="comprar" aria-labelledby="h-c">
        <div class="v-head"><div><span class="tag-n">Tienda</span><h2 id="h-c">Comprá</h2><p>Cada producto muestra a dónde se envía.</p></div><a class="text-link" href="{rel(d, p_envio('argentina'))}">Condiciones de envío</a></div>
        <div class="prod-grid">
{chr(10).join(card(p, d, cb, cv) for p in locales)}
        </div>
      </section>

      <section class="tema-sec" id="international" aria-labelledby="h-i">
        <div class="intl-band">
          <div class="v-head"><div><span class="tag-n">International Shop</span><h2 id="h-i">Desde Argentina al mundo</h2><p>Precios en dólares, con envío a:</p></div></div>
          <div class="countries">{"".join(f"<span>{esc(c)}</span>" for c in paises)}</div>
          <div class="prod-grid">
{chr(10).join(card(p, d, cb, cv, "intl") for p in intl)}
          </div>
        </div>
      </section>

      <section class="tema-sec" id="aprender" aria-labelledby="h-a">
        <div class="v-head"><div><span class="tag-n">Blog</span><h2 id="h-a">Aprendé</h2><p>Cómo preparar, cuidar y elegir.</p></div><a class="text-link" href="{rel(d, 'blog/etiqueta/' + slug(t['etiquetas'][0]) + '/')}">Ver todas las notas</a></div>
{cb.grid(rel_notas[:6], d)}
      </section>

      <section class="tema-sec" id="viajar" aria-labelledby="h-v">
        <div class="v-head"><div><span class="tag-n">Viajes</span><h2 id="h-v">Viajá al origen</h2><p>Los lugares donde el {esc(t['nombre'].lower())} es parte de todos los días.</p></div></div>
        <div class="dest-grid">
{chr(10).join(cv.dest_card(x, d) for x in dests)}
        </div>
      </section>

      <section class="tema-sec" id="empresas" aria-labelledby="h-e">
        <div class="hub-band">
          <div>
            <span class="eyebrow" style="color:#e3a33b">Hub de Oportunidades</span>
            <h2 id="h-e">Para empresas e importadores</h2>
            <p>Si comprás por volumen para revender o distribuir, estos productos están disponibles para exportación. Y si buscás algo que no está, publicalo en la Mesa de negociación: si nadie lo ofrece, nuestro equipo lo busca y te responde en 5 días hábiles.</p>
            <div class="acts"><a class="pri" href="{rel(d, 'productos-de-exportacion/')}">Ver productos de exportación</a><a class="sec" href="{rel(d, 'mesa-de-negociacion/')}#buscar">Publicar una búsqueda</a></div>
          </div>
          <div class="hub-list">{hub_items}</div>
        </div>
      </section>
    </div>'''
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"Todo sobre el {t['nombre'].lower()}", "description": t["bajada"]}
    return page(d, f"Todo sobre el {t['nombre'].lower()}: comprar, aprender y viajar al origen | Umarti Origen",
                t["bajada"], main, ["blog", "viajes", "tienda"], ld)


CAMPOS_ENVIO = [("plazo", "Plazo de entrega"), ("costo", "Costo de envío"), ("transportista", "Transportista"),
                ("seguimiento", "Seguimiento del pedido"), ("devoluciones", "Cambios y devoluciones"), ("impuestos", "Impuestos y aduana")]


def pagina_envio(e, envios, productos):
    d = 2
    titulo = "Envíos internacionales" if e["slug"] == "internacional" else f"Envíos a {e['zona']}"
    borrador = e.get("estado") != "Publicado"
    aviso = '<div class="draft-note">Estamos terminando de definir estas condiciones. Lo que figura como <b>A confirmar</b> se actualiza pronto.</div>' if borrador else ""
    items = "".join(
        f'<div class="cond{" pend" if e.get(k, "") in ("", "A confirmar") else ""}"><small>{n}</small><b>{esc(e.get(k) or "A confirmar")}</b></div>'
        for k, n in CAMPOS_ENVIO if not (k == "impuestos" and e.get(k) == "No aplica"))
    extra = ""
    if e["slug"] == "internacional":
        paises = sorted({c for p in productos if p["international"] for c in p["paises_envio"]}, key=slug)
        extra = f'<h2>Países a los que enviamos</h2><div class="countries">{"".join(f"<span>{esc(c)}</span>" for c in paises)}</div><p class="muted">Cada producto indica a qué países se envía. Los impuestos de importación los define el país de destino.</p>'
    otras = "".join(f'<a class="zona" href="{rel(d, p_envio(o["slug"]))}">{esc(o["zona"])}</a>' for o in envios if o is not e)
    main = f'''    <div class="wrap envio-page">
{crumbs(d, [("International Shop", "international-shop/"), ("Envíos", None)] if e["slug"] == "internacional" else [(e["zona"], p_pais(e["zona"])), ("Envíos", None)])}
      <div class="blog-head">
        <span class="eyebrow" style="color:var(--terra)">Condiciones de envío</span>
        <h1>{esc(titulo)}</h1>
        <p>Cómo llegan tus compras{"" if e["slug"] == "internacional" else " dentro de " + esc(e["zona"])}: plazos, costos, seguimiento y cambios.</p>
      </div>
      {aviso}
      <div class="conds">{items}</div>
      {extra}
      <p class="muted" style="margin-top:28px">Otras zonas: <span class="zonas-inline">{otras}</span></p>
      <div style="height:88px"></div>
    </div>'''
    if e["slug"] != "internacional":
        main = barra_tienda(d, "envios", e["zona"]) + main
    return page(d, f"{titulo}: condiciones | Umarti Origen", f"Plazos, costos, seguimiento y cambios de los {titulo.lower()} de Umarti Origen.",
                main, ["blog", "viajes", "tienda"], noindex=borrador)


BANDERA = {
    "Argentina": '<svg class="bandera" viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="20" fill="#74acdf"/><rect y="6.67" width="30" height="6.66" fill="#fff"/><circle cx="15" cy="10" r="2.3" fill="#f6b40e" stroke="#85340a" stroke-width=".4"/></svg>',
}
ICON_LOCK = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>'


def barra_tienda(d, actual, pais="Argentina"):
    """Barra propia de la tienda del país: Tienda, Envíos, Cupones y Guía de viajes."""
    items = [("tienda", "Tienda", p_tienda(pais)), ("envios", "Envíos", p_envio(slug(pais))),
             ("cupones", "Cupones", "cupones/"), ("viajes", "Guía de viajes", f"viajes/{slug(pais)}/")]
    links = "".join(f'<a href="{rel(d, u)}"{" aria-current=\"page\"" if k == actual else ""}>{t}</a>' for k, t, u in items)
    return f'''    <div class="ts-bar">
      <div class="wrap-wide">
        <a class="ts-marca" href="{rel(d, p_pais(pais))}">{BANDERA.get(pais, "")}<span><b>Tienda {esc(pais)}</b><small>Umarti Origen</small></span></a>
        <nav class="ts-nav" aria-label="Tienda {esc(pais)}">{links}</nav>
        <a class="ts-seguro" href="{rel(d, 'legal/arrepentimiento/')}">{ICON_LOCK}Comprá seguro</a>
      </div>
    </div>
'''


def portada_pais(productos, temas, cb, cv, pais="Argentina"):
    d = 1
    locales = [p for p in productos if p["pais"] == pais and en_tienda_local(p)]
    def tile(p):
        c1, c2 = cb.COLORES.get(p["categoria"], cb.COLORES["Alimentos"])
        media = (f'<img src="{esc(p["fotos"][0])}" alt="" loading="lazy">' if p.get("fotos")
                 else f'<span class="cover" data-glyph="{esc(p["nombre"][0])}" style="--c1:{c1};--c2:{c2}"></span>')
        pr, mon = precio_principal(p)
        return f'<a class="vt-item" href="{rel(d, p_prod(p))}"><span class="vt-media">{media}</span><span class="vt-tag"><b>{esc(p["nombre"])}</b><small>{pr} {mon}</small></span></a>'
    vidriera = "".join(tile(p) for p in locales[:3])
    pasillos = []
    for p in locales:
        if p["subcategoria"] not in [x[0] for x in pasillos]:
            pasillos.append((p["subcategoria"], p["categoria"]))
    pas_html = "".join(f'<a class="pasillo" href="{rel(d, p_tienda(pais) + "?sub=" + quote(sub))}"><small>Pasillo</small><b>{esc(sub)}</b><span>{(lambda n: f"{n} producto" + ("" if n == 1 else "s"))(sum(1 for p in locales if p["subcategoria"] == sub))}</span></a>' for sub, _ in pasillos)
    main = barra_tienda(d, "", pais) + f'''    <section class="ts-hero">
      <div class="ts-toldo" aria-hidden="true"></div>
      <div class="wrap ts-fachada">
        <div class="ts-txt">
          <span class="ts-cartel" aria-hidden="true">Abierto</span>
          <span class="eyebrow">{BANDERA.get(pais, "")} Umarti Origen</span>
          <h1>Tienda {esc(pais)}</h1>
          <p>Mates, yerba y kits de regalo con historia, elegidos uno por uno y enviados a todo el país.</p>
          <div class="ts-ctas">
            <a class="btn btn-primary" href="{rel(d, p_tienda(pais))}">Entrá a la tienda</a>
            <a class="text-link" href="{rel(d, p_envio(slug(pais)))}">Cómo llegan los envíos</a>
          </div>
        </div>
        <div class="ts-vidriera" aria-label="En la vidriera">
          <span class="vt-label">En la vidriera</span>
          <div class="vt-items">{vidriera}</div>
        </div>
      </div>
    </section>
    <div class="wrap">
      <ul class="ts-confianza" aria-label="Comprá seguro">
        <li>{ICON_LOCK}<span><b>Pago protegido</b> con plataformas seguras</span></li>
        <li>{ICON_TRUCK}<span><b>Envío a todo el país</b> con seguimiento</span></li>
        <li>{ICON["box"]}<span><b>10 días para arrepentirte</b>, sin costo</span></li>
      </ul>
      <section class="ts-pasillos" aria-labelledby="h-pas">
        <div class="blk-head"><div><h2 id="h-pas">Recorré la tienda</h2><p>Elegí un pasillo o mirá todo el catálogo.</p></div><a class="text-link" href="{rel(d, p_tienda(pais))}">Ver todos los productos →</a></div>
        <div class="pasillos">{pas_html}</div>
      </section>
      <section class="pais-dest" aria-labelledby="h-dest">
        <div class="blk-head"><div><h2 id="h-dest">Destacados</h2></div></div>
        <div class="prod-grid">
{chr(10).join(card(p, d, cb, cv) for p in locales[:4])}
        </div>
      </section>
      <p class="shop-note">¿Comprás desde otro país? Entrá a <a href="{rel(d, 'international-shop/')}">International Shop</a>.</p>
      <div style="height:72px"></div>
    </div>'''
    return page(d, f"Tienda {pais} | Umarti Origen: mates, yerba y kits de regalo", f"Comprá mates, yerba y kits de regalo de {pais}, con envío a todo el país y compra segura.", main, ["blog", "viajes", "tienda"])


def indice_envios(envios):
    d = 1
    cards = "".join(f'<a class="link-card tema" href="{rel(d, p_envio(e["slug"]))}"><span class="ic">{ICON_TRUCK}</span><span><strong>{esc("Envíos internacionales" if e["slug"] == "internacional" else "Envíos a " + e["zona"])}</strong><small>Plazos, costos, seguimiento y cambios</small></span></a>' for e in envios)
    main = f'''    <div class="wrap envio-page">
{crumbs(d, [("Envíos", None)])}
      <div class="blog-head"><span class="eyebrow" style="color:var(--terra)">Condiciones de envío</span><h1>Envíos</h1><p>Elegí la zona para ver cómo llegan tus compras.</p></div>
      <div class="link-cards" style="max-width:560px">{cards}</div>
      <div style="height:88px"></div>
    </div>'''
    return page(d, "Envíos | Umarti Origen", "Condiciones de envío de Umarti Origen para Argentina e internacional.", main, ["blog", "viajes", "tienda"],
                noindex=all(e.get("estado") != "Publicado" for e in envios))


def pagina_favoritos():
    d = 1
    main = f'''    <div class="wrap">
{crumbs(d, [("Favoritos", None)])}
      <div class="blog-head"><span class="eyebrow" style="color:var(--terra)">Tu lista</span><h1>Favoritos</h1><p>Los productos que guardaste con el corazón. Se guardan en este navegador.</p></div>
      <div class="prod-grid" id="fav-grid" data-prefix="{rel(d)}"></div>
      <p class="shop-empty" id="fav-empty">Todavía no guardaste productos. Tocá el corazón de cualquier producto para sumarlo acá. <a href="{rel(d, p_tienda())}">Ir a la Tienda</a></p>
      <div style="height:88px"></div>
    </div>'''
    return page(d, "Mis favoritos | Umarti Origen", "Productos guardados en favoritos.", main, ["blog", "viajes", "tienda"], noindex=True)


def indice_js(productos, cb):
    data = []
    for p in productos:
        pr, mon = precio_principal(p)
        c1, c2 = cb.COLORES.get(p["categoria"], cb.COLORES["Alimentos"])
        data.append(dict(codigo=p["codigo"], nombre=p["nombre"], url=p_prod(p), precio=pr, moneda=mon, subcategoria=p["subcategoria"],
                         foto=(p["fotos"][0] if p.get("fotos") else ""), c1=c1, c2=c2, glifo=p["nombre"][0],
                         envio=" · ".join(z["nombre"] for z in zonas(p)), ejemplo=p["estado"] == "Ejemplo"))
    return ("/* Generado por _fuente/construir_tienda.py. Lo usa la página de Favoritos. */\n"
            "window.TIENDA_INDICE = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")


def main():
    import construir_blog as cb
    import construir_viajes as cv
    productos, temas = cargar()
    envios = cargar_envios()
    notas = sorted([cb.leer_nota(r) for r in glob.glob(os.path.join(AQUI, "blog", "notas", "*.md"))], key=lambda n: n["fecha"], reverse=True)
    for p in productos:
        if p.get("destino") and not any(x["slug"] == p["destino"] for x in cv.DESTINOS):
            raise SystemExit(f"{p['codigo']}: el destino '{p['destino']}' no existe en Viajes")
    escribir("assets/data/tienda-indice.js", indice_js(productos, cb))
    escribir(p_tienda() + "index.html", listado(productos, cb, cv))
    escribir(p_pais() + "index.html", portada_pais(productos, temas, cb, cv))
    escribir("international-shop/index.html", international(productos, cb, cv))
    for p in productos:
        escribir(p_prod(p) + "index.html", pagina_producto(p, productos, temas, notas, cb, cv))
    for t in temas:
        escribir(p_tema(t) + "index.html", pagina_tema(t, productos, notas, cb, cv))
    escribir("envios/index.html", indice_envios(envios))
    for e in envios:
        escribir(p_envio(e["slug"]) + "index.html", pagina_envio(e, envios, productos))
    escribir("favoritos/index.html", pagina_favoritos())


if __name__ == "__main__":
    main()
