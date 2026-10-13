#!/usr/bin/env python3
"""Genera la Tienda, International Shop y las páginas de tema a partir de _fuente/tienda/catalogo.json

Uso:  python3 _fuente/construir_tienda.py
El catálogo sale de las pestañas Catálogo y Temas de la hoja 'Plan Ecommerce' (ver tienda/importar_hoja.py).
Genera: tienda/, tienda/<producto>/, international-shop/ y /<tema>/ (por ejemplo /mate/).
Los productos con "Hub de Oportunidades: Sí" también aparecen en Productos de exportación (lo hace construir.py).
"""
import html, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comun  # noqa: E402
from comun import escribir, slug, SITIO  # noqa: E402

esc = html.escape
CATALOGO = os.path.join(AQUI, "tienda", "catalogo.json")

SECTOR_HUB = {"Café, Té y Mate": "Alimentos y bebidas", "Bebidas": "Alimentos y bebidas", "Alimentos": "Alimentos y bebidas",
              "Regalos y Kits": "Manufacturas", "Moda": "Moda y textil", "Tecnología": "Tecnología", "Salud y Bienestar": "Salud",
              "Hogar y Cocina": "Manufacturas", "Herramientas y Jardín": "Manufacturas", "Limpieza e Higiene": "Manufacturas"}


def cargar():
    d = json.load(open(CATALOGO, encoding="utf-8"))
    return d["productos"], d["temas"]


def p_prod(p): return f"tienda/{p['slug']}/"


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


# ---------- piezas ----------
def precio(v, moneda):
    if v is None:
        return ""
    n = f"{v:,.0f}".replace(",", ".")
    return {"ars": f"$ {n}", "mxn": f"$ {n}", "usd": f"US$ {n}"}[moneda]


def foto(p, cb):
    if p.get("foto"):
        return f'<div class="prod-photo"><img src="{esc(p["foto"])}" alt="{esc(p["nombre"])}" loading="lazy"></div>'
    c1, c2 = cb.COLORES.get(p["categoria"], cb.COLORES["Alimentos"])
    return f'<div class="prod-photo"><div class="cover" data-glyph="{esc(p["nombre"][0])}" style="--c1:{c1};--c2:{c2}"><span>{esc(p["subcategoria"])}</span></div></div>'


def ships(p):
    out = []
    if p["tienda_ar"]: out.append('<span class="ship">Argentina</span>')
    if p["tienda_mx"]: out.append('<span class="ship">México</span>')
    if p["international"]: out.append('<span class="ship intl">Internacional</span>')
    return '<div class="ships">' + "".join(out) + "</div>"


def card(p, depth, cb, modo="local"):
    ej = '<span class="badge-ej">Ejemplo</span>' if p["estado"] == "Ejemplo" else ""
    if modo == "intl":
        pr = f'<span class="price">{precio(p["precio_usd"], "usd")}<small>USD</small></span>'
    else:
        pr = (f'<span class="price" data-pais-show="ar">{precio(p["precio_ars"], "ars")}<small>ARS</small></span>'
              f'<span class="price" data-pais-show="mx" hidden>{precio(p["precio_mxn"], "mxn")}<small>MXN</small></span>')
    attrs = f'data-ar="{int(p["tienda_ar"])}" data-mx="{int(p["tienda_mx"])}" ' if modo == "local" else ""
    return f'''        <a class="prod-card" href="{rel(depth, p_prod(p))}" {attrs}data-cat="{esc(p['categoria'])}" data-sub="{esc(p['subcategoria'])}">
          {ej}{foto(p, cb)}
          <div class="info">
            <span class="kick">{esc(p['subcategoria'])}</span>
            <h3>{esc(p['nombre'])}</h3>
            {ships(p)}
            {pr}
          </div>
        </a>'''


def page(depth, title, desc, main, css, jsonld=None, noindex=False):
    pre = rel(depth)
    links = "".join(f'\n  <link rel="stylesheet" href="{pre}assets/css/{c}.css">' for c in ["umarti"] + css)
    ld = f'\n  <script type="application/ld+json">\n{json.dumps(jsonld, ensure_ascii=False, indent=2)}\n  </script>' if jsonld else ""
    robots = '\n  <!-- Producto de ejemplo: se indexa cuando el estado pase a Publicado -->\n  <meta name="robots" content="noindex">' if noindex else ""
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

  <script src="{pre}assets/js/header.js"></script>
  <script src="{pre}assets/js/tienda.js"></script>
</body>
</html>
'''


def country_switch():
    return '<div class="country-switch" role="group" aria-label="País de compra"><button type="button" data-pais="ar" aria-pressed="true">Argentina</button><button type="button" data-pais="mx" aria-pressed="false">México</button></div>'


ICON = {
    "ok": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg>',
    "no": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    "pin": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
    "hub": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h14l-4-4M20 16H6l4 4"/></svg>',
    "tema": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19V5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2zM8 7h6"/></svg>',
}


# ---------- páginas ----------
def listado(productos, cb):
    d = 1
    locales = [p for p in productos if p["tienda_ar"] or p["tienda_mx"]]
    cats = []
    for p in locales:
        for v in (p["categoria"], p["subcategoria"]):
            if v not in cats:
                cats.append(v)
    chips = '<div class="chip-row" role="group" aria-label="Filtrar"><button type="button" data-filtro="" aria-pressed="true">Todo</button>' + "".join(
        f'<button type="button" data-filtro="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats) + "</div>"
    main = f'''    <div class="wrap">
{crumbs(d, [("Tienda", None)])}
      <div class="blog-head">
        <span class="eyebrow" style="color:var(--terra)">Tienda</span>
        <h1>Productos con origen</h1>
        <p>Productos seleccionados de Argentina y otros países, con envío en Argentina y en México. Elegí desde dónde comprás para ver precios y disponibilidad.</p>
      </div>
      <div class="shop-tools">{chips}{country_switch()}</div>
      <div class="prod-grid" id="shop-grid">
{chr(10).join(card(p, d, cb) for p in locales)}
        <p class="shop-empty" id="shop-empty">Todavía no hay productos de esta categoría disponibles en tu país.</p>
      </div>
      <p class="shop-note"><span id="shop-count"></span> · ¿Comprás desde otro país? Mirá <a href="{rel(d, 'international-shop/')}">International Shop</a>.</p>
      <div style="height:88px"></div>
    </div>'''
    return page(d, "Tienda Umarti Origen: productos con origen, con envío en Argentina y México",
                "Mates, bombillas, yerba y productos seleccionados de Argentina, con envío en Argentina y en México.", main, ["blog", "viajes", "tienda"])


def international(productos, cb):
    d = 1
    intl = [p for p in productos if p["international"]]
    paises = sorted({c for p in intl for c in p["paises_envio"]}, key=slug)
    main = f'''    <div class="wrap">
{crumbs(d, [("International Shop", None)])}
      <div class="blog-head">
        <span class="eyebrow" style="color:var(--intl)">International Shop</span>
        <h1>De Argentina al mundo</h1>
        <p>Productos argentinos con envío internacional. Precios en dólares estadounidenses; el costo del envío y los impuestos de importación dependen del país de destino.</p>
      </div>
      <div class="intl-band" style="margin-bottom:28px">
        <strong>Enviamos a</strong>
        <div class="countries">{"".join(f"<span>{esc(c)}</span>" for c in paises)}</div>
        <small style="color:var(--muted)">¿Tu país no está en la lista? Escribinos y vemos cómo hacértelo llegar.</small>
      </div>
      <div class="prod-grid">
{chr(10).join(card(p, d, cb, "intl") for p in intl)}
      </div>
      <p class="shop-note">¿Comprás por volumen para revender o distribuir? Mirá los <a href="{rel(d, 'productos-de-exportacion/')}">Productos de exportación</a> del Hub de Oportunidades.</p>
      <div style="height:88px"></div>
    </div>'''
    return page(d, "International Shop: productos argentinos con envío internacional | Umarti Origen",
                f"Mate, yerba y productos argentinos con envío a {', '.join(paises)}.", main, ["blog", "viajes", "tienda"])


def crumbs(depth, items):
    import construir_blog
    return construir_blog.crumbs(depth, items)


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
    return [n for s, n in sorted(out, key=lambda x: (-x[0], x[1]["fecha"]), reverse=False)]


def pagina_producto(p, productos, temas, notas, destinos, cb, cv):
    d = 2
    dest = next((x for x in destinos if x["slug"] == p.get("destino")), None)
    def bloque(pais, disp, valor, moneda, nombre_pais):
        if not disp:
            return f'<div data-pais-show="{pais}"{" hidden" if pais == "mx" else ""}><p class="buy-na">Todavía no está disponible para comprar en {nombre_pais}.</p></div>'
        if p.get("link_pago"):
            btn = f'<a class="btn-buy" href="{esc(p["link_pago"])}" rel="noopener">Comprar</a>'
        else:
            btn = '<a class="btn-buy" href="#" aria-disabled="true">Disponible muy pronto</a><p class="buy-hint">Estamos preparando la venta en línea de este producto.</p>'
        return f'<div data-pais-show="{pais}"{" hidden" if pais == "mx" else ""}><div class="buy-price">{precio(valor, moneda)}<small>{moneda.upper()}</small></div>{btn}</div>'
    avail = [
        (p["tienda_ar"], "Envío en Argentina"), (p["tienda_mx"], "Envío en México"),
        (p["international"], f'International Shop: US$ {p["precio_usd"]:,.0f} con envío a {", ".join(p["paises_envio"])}' if p["international"] else "International Shop"),
    ]
    avail_html = "".join(f'<li class="{"" if ok else "off"}">{ICON["ok" if ok else "no"]}<span>{esc(t)}</span></li>' for ok, t in avail)
    links = []
    if dest:
        links.append(f'<a class="link-card origen" href="{rel(d, f"viajes/{dest["pais"]}/{dest["slug"]}/")}"><span class="ic">{ICON["pin"]}</span><span><strong>Origen: {esc(p["region"])}, {esc(p["pais"])}</strong><small>Conocé el lugar en la guía de viaje de {esc(dest["nombre"])}</small></span></a>')
    elif p.get("region"):
        links.append(f'<div class="link-card origen"><span class="ic">{ICON["pin"]}</span><span><strong>Origen: {esc(p["region"])}, {esc(p["pais"])}</strong><small>Producto elaborado en {esc(p["pais"])}</small></span></div>')
    for t in temas:
        if t["clave"] in p["temas"]:
            links.append(f'<a class="link-card tema" href="{rel(d, t["clave"] + "/")}"><span class="ic">{ICON["tema"]}</span><span><strong>Todo sobre el {esc(t["nombre"].lower())}</strong><small>Guías, productos, destinos y más en un solo lugar</small></span></a>')
    if p["hub"]:
        links.append(f'<a class="link-card hub" href="{rel(d, "productos-de-exportacion/")}#{p["codigo"].lower()}"><span class="ic">{ICON["hub"]}</span><span><strong>¿Comprás por volumen?</strong><small>Este producto está en Productos de exportación del Hub de Oportunidades</small></span></a>')
    rel_notas = notas_relacionadas(p, notas)[:3]
    otros = [o for o in productos if o is not p and set(o["temas"]) & set(p["temas"])][:4]
    ej = '<span class="badge-ej" style="position:static;display:inline-block;margin-bottom:6px">Producto de ejemplo</span>' if p["estado"] == "Ejemplo" else ""
    main = f'''    <div class="wrap">
{crumbs(d, [("Tienda", "tienda/"), (p["categoria"], None), (p["subcategoria"], None), (p["nombre"], None)])}
      <section class="pdp">
        <div class="pdp-photo">{foto(p, cb)}</div>
        <div>
          {ej}
          <p class="kick post-kicker"><b>{esc(p['categoria'])}</b> · {esc(p['subcategoria'])}</p>
          <h1>{esc(p['nombre'])}</h1>
          <p class="lead">{esc(p['descripcion'])}</p>
          <div class="buy-box">
            <div class="buy-top"><span class="post-kicker">Comprás desde</span>{country_switch()}</div>
            <div style="margin-top:16px">
              {bloque("ar", p["tienda_ar"], p["precio_ars"], "ars", "Argentina")}
              {bloque("mx", p["tienda_mx"], p["precio_mxn"], "mxn", "México")}
            </div>
            <ul class="avail">{avail_html}</ul>
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
{chr(10).join(card(o, d, cb) for o in otros)}
        </div>
      </div>
    </section>'''}'''
    ld = None
    if p["estado"] == "Publicado":
        offers = []
        if p["tienda_ar"] and p["precio_ars"]: offers.append({"@type": "Offer", "price": p["precio_ars"], "priceCurrency": "ARS", "availability": "https://schema.org/InStock"})
        if p["tienda_mx"] and p["precio_mxn"]: offers.append({"@type": "Offer", "price": p["precio_mxn"], "priceCurrency": "MXN", "availability": "https://schema.org/InStock"})
        if p["international"] and p["precio_usd"]: offers.append({"@type": "Offer", "price": p["precio_usd"], "priceCurrency": "USD", "availability": "https://schema.org/InStock"})
        ld = {"@context": "https://schema.org", "@type": "Product", "name": p["nombre"], "description": p["descripcion"], "sku": p["codigo"],
              "category": f'{p["categoria"]} > {p["subcategoria"]}', "countryOfOrigin": p["pais"], "offers": offers}
        if p.get("foto"): ld["image"] = p["foto"]
        if SITIO: ld["url"] = f"{SITIO}/{p_prod(p)}"
    return page(d, f"{p['nombre']} | Tienda Umarti Origen", p["descripcion"], main, ["blog", "viajes", "tienda"], ld, noindex=p["estado"] != "Publicado")


def pagina_tema(t, productos, notas, destinos, cb, cv):
    d = 1
    prods = [p for p in productos if t["clave"] in p["temas"]]
    locales = [p for p in prods if p["tienda_ar"] or p["tienda_mx"]]
    intl = [p for p in prods if p["international"]]
    hub = [p for p in prods if p["hub"]]
    paises = sorted({c for p in intl for c in p["paises_envio"]}, key=slug)
    rel_notas = notas_relacionadas({"temas": [slug(e) for e in t["etiquetas"]]}, notas, etiquetas=set(t["etiquetas"]) | {slug(e) for e in t["etiquetas"]})
    dests = [x for s in t["destinos"] for x in destinos if x["slug"] == s]
    # búsquedas de la Mesa que piden estos productos (por posición arancelaria o por nombre)
    sys.path.insert(0, AQUI)
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
        <div class="v-head"><div><span class="tag-n">Tienda</span><h2 id="h-c">Comprá en tu país</h2><p>Envíos en Argentina y en México. Elegí desde dónde comprás.</p></div>{country_switch()}</div>
        <div class="prod-grid">
{chr(10).join(card(p, d, cb) for p in locales)}
        </div>
      </section>

      <section class="tema-sec" id="international" aria-labelledby="h-i">
        <div class="intl-band">
          <div class="v-head"><div><span class="tag-n">International Shop</span><h2 id="h-i">Desde Argentina al mundo</h2><p>Precios en dólares, con envío a:</p></div></div>
          <div class="countries">{"".join(f"<span>{esc(c)}</span>" for c in paises)}</div>
          <div class="prod-grid">
{chr(10).join(card(p, d, cb, "intl") for p in intl)}
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


def main():
    import construir_blog as cb
    import construir_viajes as cv
    import glob
    productos, temas = cargar()
    notas = sorted([cb.leer_nota(r) for r in glob.glob(os.path.join(AQUI, "blog", "notas", "*.md"))], key=lambda n: n["fecha"], reverse=True)
    destinos = cv.DESTINOS
    for p in productos:
        if p.get("destino") and not any(x["slug"] == p["destino"] for x in destinos):
            raise SystemExit(f"{p['codigo']}: el destino '{p['destino']}' no existe en Viajes")
    escribir("tienda/index.html", listado(productos, cb))
    escribir("international-shop/index.html", international(productos, cb))
    for p in productos:
        escribir(p_prod(p) + "index.html", pagina_producto(p, productos, temas, notas, destinos, cb, cv))
    for t in temas:
        escribir(t["clave"] + "/index.html", pagina_tema(t, productos, notas, destinos, cb, cv))


if __name__ == "__main__":
    main()
