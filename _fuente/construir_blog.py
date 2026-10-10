#!/usr/bin/env python3
"""Genera el blog a partir de las notas en _fuente/blog/notas/*.md

Uso:  python3 _fuente/construir_blog.py

Cada nota es un archivo .md con un encabezado así:
---
titulo: Cómo preparar un buen mate, paso a paso
resumen: Una o dos oraciones que aparecen en las tarjetas y en Google.
seccion: productos            (productos o negocios)
categoria: Café, Té y Mate    (solo productos: una categoría de la Tienda)
subcategoria: Mates y bombillas
tema: Comercio exterior       (solo negocios)
tags: mate, yerba mate, preparación   (dos o tres)
fecha: 2026-10-08
destacada: si                 (opcional)
---
y después el texto. Formato: ## título, ### subtítulo, **negrita**, [enlace](url),
listas con "- " o "1. ", tablas con |, y "> " para un recuadro de consejo.
"""
import glob, html, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comun  # noqa: E402
from comun import slug, fecha_larga, escribir, SITIO  # noqa: E402

esc = html.escape

# ---------- taxonomía: mismas categorías y subcategorías que la Tienda ----------
CATEGORIAS = {
    "Café, Té y Mate": ["Mates y bombillas", "Café", "Té", "Chocolate"],
    "Regalos y Kits": ["Kits de mate y café", "Regalos corporativos", "Personalizados"],
    "Bebidas": ["Vinos", "Cervezas y destilados", "Sin alcohol"],
    "Alimentos": ["Snacks", "Golosinas", "Alimentos diet", "Congelados"],
    "Salud y Bienestar": ["Odontología", "Cuidado personal", "Dispositivos médicos"],
    "Moda": ["Ropa de dama", "Ropa de caballero", "Zapatos", "Carteras"],
    "Tecnología": ["Accesorios", "Audio", "Hogar inteligente"],
    "Hogar y Cocina": ["Bazar y cocina", "Organización", "Deco"],
    "Herramientas y Jardín": ["Herramientas", "Jardín", "Construcción"],
    "Limpieza e Higiene": ["Limpieza", "Higiene personal"],
}
TIENDA_TEXTO = {
    "Café, Té y Mate": "Mates, bombillas, yerbas, cafés y tés seleccionados.",
    "Regalos y Kits": "Kits armados y regalos para empresas.",
    "Bebidas": "Vinos, cervezas, destilados y bebidas sin alcohol.",
    "Moda": "Ropa, calzado y carteras.",
}
TEMAS = ["Comercio exterior", "Mercados", "Ecommerce y ventas", "Cómo usar Umarti"]
COLORES = {
    "Café, Té y Mate": ("#5b7a43", "#33472a"), "Regalos y Kits": ("#c8922a", "#8a5e0c"),
    "Bebidas": ("#9a3445", "#5c1c27"), "Alimentos": ("#c8693e", "#8f3f1d"),
    "Salud y Bienestar": ("#4c8a86", "#2c5b58"), "Moda": ("#8a5878", "#4f2c45"),
    "Tecnología": ("#4b5d78", "#2b3648"), "Hogar y Cocina": ("#a8703f", "#6e4421"),
    "Herramientas y Jardín": ("#6b7a3a", "#424c22"), "Limpieza e Higiene": ("#4a8aa8", "#2a5a72"),
    "negocios": ("#3d87ab", "#225670"),
}

NOTAS_DIR = os.path.join(AQUI, "blog", "notas")


# ---------- lectura de notas ----------
def leer_nota(ruta):
    txt = open(ruta, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n(.*)", txt, re.S)
    if not m:
        raise SystemExit(f"Falta el encabezado --- en {ruta}")
    meta = {}
    for linea in m.group(1).splitlines():
        if ":" in linea:
            k, v = linea.split(":", 1)
            meta[k.strip()] = v.strip()
    n = dict(meta)
    n["slug"] = os.path.splitext(os.path.basename(ruta))[0]
    n["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    n["destacada"] = meta.get("destacada", "").lower() in ("si", "sí", "true")
    n["html"], n["toc"] = markdown(m.group(2))
    palabras = len(re.findall(r"\w+", m.group(2)))
    n["min"] = max(2, -(-palabras // 200))
    if n["seccion"] == "productos":
        cat, sub = n.get("categoria"), n.get("subcategoria")
        if cat not in CATEGORIAS or sub not in CATEGORIAS[cat]:
            raise SystemExit(f"{n['slug']}: categoría o subcategoría que no existe en la Tienda: {cat} / {sub}")
        n["etiqueta"], n["colores"] = sub, COLORES.get(cat, COLORES["Alimentos"])
    else:
        if n.get("tema") not in TEMAS:
            raise SystemExit(f"{n['slug']}: tema desconocido {n.get('tema')}. Opciones: {TEMAS}")
        n["etiqueta"], n["colores"] = n["tema"], COLORES["negocios"]
    n["glifo"] = n["etiqueta"][0]
    return n


def inline(t):
    t = esc(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    return t


def markdown(src):
    out, toc = [], []
    lines = src.strip("\n").split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        if ln.startswith("## "):
            title = ln[3:].strip(); hid = slug(title)
            toc.append((hid, title))
            out.append(f'<h2 id="{hid}">{inline(title)}</h2>'); i += 1; continue
        if ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:].strip())}</h3>"); i += 1; continue
        if ln.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i][1:].strip()); i += 1
            out.append(f'<aside class="tip"><p>{inline(" ".join(buf))}</p></aside>'); continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r":?-+:?", c) for c in r)]
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'); continue
        if re.match(r"- ", ln):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:]); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"); continue
        if re.match(r"\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i])); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>"); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"(#{2,3} |> |\||- |\d+\. )", lines[i]):
            buf.append(lines[i].strip()); i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out), toc


# ---------- direcciones ----------
def rel(depth, path=""):
    return ("../" * depth) + path if depth or path else "./"


def p_nota(n): return f"blog/{n['slug']}/"
def p_cat(cat): return f"blog/productos/{slug(cat)}/"
def p_sub(cat, sub): return f"blog/productos/{slug(cat)}/{slug(sub)}/"
def p_tema(t): return f"blog/negocios/{slug(t)}/"
def p_tag(t): return f"blog/etiqueta/{slug(t)}/"


# ---------- piezas ----------
def cover(n, cls=""):
    c1, c2 = n["colores"]
    return f'<div class="cover {cls}" data-glyph="{esc(n["glifo"])}" style="--c1:{c1};--c2:{c2}" aria-hidden="true"><span>{esc(n["etiqueta"])}</span></div>'


def kicker(n):
    sec = "Productos" if n["seccion"] == "productos" else "Negocios"
    return f'<p class="post-kicker"><b>{sec}</b> · {esc(n.get("categoria") or n.get("tema"))}</p>'


def card(n, depth):
    neg = " neg" if n["seccion"] == "negocios" else ""
    texto = esc(" ".join([n["titulo"], n["resumen"], n.get("categoria", ""), n.get("subcategoria", ""), n.get("tema", "")] + n["tags"]).lower())
    return f'''        <a class="post-card{neg}" href="{rel(depth, p_nota(n))}" data-texto="{texto}" data-sub="{esc(n.get('subcategoria') or n.get('tema'))}">
          {cover(n)}
          {kicker(n)}
          <h3>{esc(n['titulo'])}</h3>
          <p>{esc(n['resumen'])}</p>
          <span class="post-meta">{fecha_larga(n['fecha'])} · {n['min']} min de lectura</span>
        </a>'''


def grid(notas, depth, gid=None):
    gid_attr = f' id="{gid}"' if gid else ""
    empty = '\n        <p class="empty" id="b-empty">No hay notas con esa búsqueda.</p>' if gid else ""
    return f'      <div class="post-grid"{gid_attr}>\n' + "\n".join(card(n, depth) for n in notas) + empty + "\n      </div>"


def crumbs(depth, items):
    lis = [f'<li><a href="{rel(depth)}">Inicio</a></li>']
    for i, (nombre, path) in enumerate(items):
        last = i == len(items) - 1
        if last:
            lis.append(f'<li aria-current="page">{esc(nombre)}</li>')
        elif path:
            lis.append(f'<li><a href="{rel(depth, path)}">{esc(nombre)}</a></li>')
        else:
            lis.append(f"<li>{esc(nombre)}</li>")
    return '      <nav class="crumbs" aria-label="Ubicación">\n        <ol>' + "".join(lis) + "</ol>\n      </nav>"


def tabs(depth, actual):
    items = [("Todo", "blog/", "todo"), ("Productos", "blog/productos/", "productos"), ("Negocios", "blog/negocios/", "negocios")]
    out = [f'<a href="{rel(depth, p)}"{" aria-current=\"page\"" if k == actual else ""}>{t}</a>' for t, p, k in items]
    out.append(f'<a class="ghost" href="{rel(depth, "#viajes")}">Guías de viaje, en Viajes →</a>')
    return '        <nav class="tabs" aria-label="Secciones del blog">' + "".join(out) + "</nav>"


def list_tools():
    return '''      <div class="list-tools">
        <label class="list-search">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
          <input id="b-q" type="search" placeholder="Buscar en estas notas" aria-label="Buscar en estas notas">
        </label>
        <span class="list-count" id="b-count" aria-live="polite"></span>
      </div>'''


def chips_filtro(valores, conteo):
    btns = ['<button type="button" data-sub="" aria-pressed="true">Todas</button>']
    btns += [f'<button type="button" data-sub="{esc(v)}" aria-pressed="false">{esc(v)} <small>{conteo[v]}</small></button>' for v in valores]
    return '      <div class="cat-chips" role="group" aria-label="Filtrar">' + "".join(btns) + "</div>"


def store_band(depth, nombre, cat):
    texto = TIENDA_TEXTO.get(cat, f"Productos de {cat}.")
    return f'''      <div class="store-band">
        <p>{esc(nombre)} en la Tienda<small>{esc(texto)} La tienda abre pronto.</small></p>
        <a class="btn btn-primary" href="{rel(depth, '#tienda')}">Ver la Tienda</a>
      </div>'''


def page(depth, title, desc, main, jsonld=None, scripts=""):
    pre = rel(depth) if depth else ""
    canon = ""
    ld = f'\n  <script type="application/ld+json">\n{json.dumps(jsonld, ensure_ascii=False, indent=2)}\n  </script>' if jsonld else ""
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">{canon}
  <meta property="og:type" content="{'article' if jsonld and jsonld.get('@type') == 'Article' else 'website'}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
{comun.FUENTES}
  <link rel="stylesheet" href="{pre}assets/css/umarti.css">
  <link rel="stylesheet" href="{pre}assets/css/blog.css">{ld}
</head>
<body>

{comun.header(pre)}

  <main>
{main}
  </main>

{comun.footer(pre)}

  <script src="{pre}assets/js/header.js"></script>{scripts}
</body>
</html>
'''


# ---------- páginas ----------
def portada_blog(notas):
    d = 1
    prods = [n for n in notas if n["seccion"] == "productos"]
    negs = [n for n in notas if n["seccion"] == "negocios"]
    dest = next((n for n in prods if n["destacada"]), prods[0])
    ultimas = [n for n in notas if n is not dest][:4]
    side = "\n".join(f'''          <a class="side-item" href="{rel(d, p_nota(n))}">
            {cover(n)}
            <div><h3>{esc(n['titulo'])}</h3><small>{'Productos' if n['seccion'] == 'productos' else 'Negocios'} · {n['min']} min</small></div>
          </a>''' for n in ultimas)
    cats = [c for c in CATEGORIAS if any(n.get("categoria") == c for n in prods)]
    chips = "".join(f'<a href="{rel(d, p_cat(c))}" style="--c1:{COLORES[c][0]}"><span class="dot"></span>{esc(c)} <small>{sum(1 for n in prods if n.get("categoria") == c)}</small></a>' for c in cats)
    tags = sorted({t for n in notas for t in n["tags"]}, key=lambda t: slug(t))
    cloud = "".join(f'<a class="tag" href="{rel(d, p_tag(t))}">{esc(t)}</a>' for t in tags)
    main = f'''    <div class="wrap">
{crumbs(d, [("Blog", None)])}
      <div class="blog-head">
        <span class="eyebrow">Herramientas</span>
        <h1>Blog</h1>
        <p>Guías, recetas y consejos sobre los productos de la Tienda, y notas para hacer negocios entre países.</p>
{tabs(d, "todo")}
      </div>

      <section class="featured" aria-label="Nota destacada">
{card(dest, d).replace('class="post-card', 'class="post-card big', 1)}
        <div class="side-list">
          <h2>Lo último</h2>
{side}
        </div>
      </section>

      <section class="blk" aria-labelledby="h-prod">
        <div class="blk-head">
          <div><h2 id="h-prod">Todo sobre los productos</h2><p>Cada nota está vinculada a una categoría de la Tienda: si te interesa un producto, acá encontrás cómo elegirlo, usarlo y cuidarlo.</p></div>
          <a href="{rel(d, 'blog/productos/')}">Ver todas las notas de productos →</a>
        </div>
        <div class="cat-chips">{chips}</div>
{grid(prods[:6], d)}
      </section>
    </div>

    <section class="blk negocios" aria-labelledby="h-neg">
      <div class="wrap">
        <div class="blk-head">
          <div><h2 id="h-neg">Negocios</h2><p>Comercio exterior, mercados y herramientas para comprar y vender entre países.</p></div>
          <a href="{rel(d, 'blog/negocios/')}">Ver todas las notas de negocios →</a>
        </div>
{grid(negs[:4], d)}
      </div>
    </section>

    <div class="wrap">
      <section class="blk" aria-labelledby="h-tags">
        <div class="blk-head"><div><h2 id="h-tags">Explorá por etiqueta</h2></div></div>
        <div class="tag-cloud">{cloud}</div>
      </section>

      <div class="viajes-note">
        <div>
          <h2>¿Buscás guías de viaje?</h2>
          <p>Las notas sobre destinos viven en la sección Viajes, conectadas con estas: la guía de Misiones te lleva a la yerba mate, y la nota de yerba te lleva a Misiones.</p>
        </div>
        <a href="{rel(d, '#viajes')}">Ir a Viajes</a>
      </div>
    </div>'''
    return page(d, "Blog de Umarti Origen: guías de productos y notas de negocios",
                "Guías y consejos sobre mate, café, vinos, moda y más productos de la Tienda, y notas de comercio exterior para vender entre Argentina, México y el mundo.", main)


def listado(depth, title, desc, crumbs_items, eyebrow, h1, lead, tab, notas, extra_top="", chips_vals=None, conteo=None):
    chips = chips_filtro(chips_vals, conteo) if chips_vals and len(chips_vals) > 1 else ""
    main = f'''    <div class="wrap">
{crumbs(depth, crumbs_items)}
      <div class="blog-head">
        <span class="eyebrow">{esc(eyebrow)}</span>
        <h1>{esc(h1)}</h1>
        <p>{lead}</p>
{tabs(depth, tab) if tab else ""}
      </div>
{extra_top}
{chips}
{list_tools()}
      <div class="list-wrap">
{grid(notas, depth, "b-grid")}
      </div>
    </div>'''
    return page(depth, title, desc, main, scripts=f'\n  <script src="{rel(depth)}assets/js/blog.js"></script>')


def pagina_nota(n, notas):
    d = 2
    es_prod = n["seccion"] == "productos"
    if es_prod:
        cr = [("Blog", "blog/"), ("Productos", "blog/productos/"), (n["categoria"], p_cat(n["categoria"])), (n["subcategoria"], p_sub(n["categoria"], n["subcategoria"])), (n["titulo"], None)]
        kick = f'<p class="post-kicker"><b>Productos</b><a href="{rel(d, p_cat(n["categoria"]))}">{esc(n["categoria"])}</a><span>›</span><a href="{rel(d, p_sub(n["categoria"], n["subcategoria"]))}">{esc(n["subcategoria"])}</a></p>'
    else:
        cr = [("Blog", "blog/"), ("Negocios", "blog/negocios/"), (n["tema"], p_tema(n["tema"])), (n["titulo"], None)]
        kick = f'<p class="post-kicker"><b style="color:var(--sky)">Negocios</b><a href="{rel(d, p_tema(n["tema"]))}">{esc(n["tema"])}</a></p>'

    def score(o):
        s = 0
        if es_prod and o.get("subcategoria") == n.get("subcategoria"): s += 3
        if es_prod and o.get("categoria") == n.get("categoria"): s += 2
        if not es_prod and o.get("tema") == n.get("tema"): s += 2
        s += len(set(o["tags"]) & set(n["tags"]))
        if o["seccion"] == n["seccion"]: s += 1
        return s
    otras = sorted([o for o in notas if o is not n], key=lambda o: (score(o), o["fecha"]), reverse=True)
    relacionadas = otras[:3]

    toc = ""
    if len(n["toc"]) >= 2:
        toc = '<div class="box toc"><h2>En esta nota</h2><ol>' + "".join(f'<li><a href="#{h}">{esc(t)}</a></li>' for h, t in n["toc"]) + "</ol></div>"
    if es_prod:
        cat, sub = n["categoria"], n["subcategoria"]
        mismas = [o for o in notas if o is not n and o.get("categoria") == cat]
        box = f'''<div class="box store">
            <span class="soon">La tienda abre pronto</span>
            <strong>{esc(sub)} en la Tienda</strong>
            <p>{esc(TIENDA_TEXTO.get(cat, f"Productos de {cat}."))}</p>
            <a class="btn-line" href="{rel(d, '#tienda')}">Ver la Tienda →</a>
          </div>'''
        mas = ""
        if mismas:
            mas = f'<div class="box"><h2>Más sobre {esc(cat)}</h2><ul class="mini-list">' + "".join(f'<li><a href="{rel(d, p_nota(o))}">{esc(o["titulo"])}</a></li>' for o in mismas[:5]) + f'</ul><a class="all" href="{rel(d, p_cat(cat))}">Todas las notas de {esc(cat)}</a></div>'
    else:
        box = f'''<div class="box hub">
            <strong>Mesa de negociación</strong>
            <p>Decinos qué producto o servicio buscás. Si no está publicado, nuestro equipo lo busca y te responde en 5 días hábiles.</p>
            <a class="btn-line" href="{rel(d, 'mesa-de-negociacion/')}">Buscar en la Mesa →</a>
          </div>'''
        mismas = [o for o in notas if o is not n and o["seccion"] == "negocios"]
        mas = '<div class="box"><h2>Más de Negocios</h2><ul class="mini-list">' + "".join(f'<li><a href="{rel(d, p_nota(o))}">{esc(o["titulo"])}</a></li>' for o in mismas[:5]) + f'</ul><a class="all" href="{rel(d, "blog/negocios/")}">Todas las notas de Negocios</a></div>'

    tags = "".join(f'<a class="tag" href="{rel(d, p_tag(t))}">{esc(t)}</a>' for t in n["tags"])
    main = f'''    <div class="wrap">
{crumbs(d, cr)}
      <header class="post-head">
        {kick}
        <h1>{esc(n['titulo'])}</h1>
        <p class="lead">{esc(n['resumen'])}</p>
        <p class="post-meta"><span><time datetime="{n['fecha']}">{fecha_larga(n['fecha'])}</time></span><span>{n['min']} min de lectura</span><span>Equipo Umarti Origen</span></p>
      </header>
      {cover(n, "post-cover")}
      <div class="post-layout">
        <article class="prose">
{n['html']}
          <div class="post-tags" aria-label="Etiquetas">{tags}</div>
        </article>
        <aside class="post-aside">
          <div class="aside-sticky">
          {toc}
          {box}
          {mas}
          </div>
        </aside>
      </div>
    </div>
    <section class="related">
      <div class="wrap">
        <h2>También te puede interesar</h2>
{grid(relacionadas, d)}
      </div>
    </section>'''
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": n["titulo"], "description": n["resumen"],
          "datePublished": n["fecha"], "inLanguage": "es", "articleSection": n.get("categoria") or n.get("tema"),
          "keywords": ", ".join(n["tags"]),
          "author": {"@type": "Organization", "name": "Umarti Origen"},
          "publisher": {"@type": "Organization", "name": "Umarti Origen"}}
    if SITIO:
        ld["mainEntityOfPage"] = f"{SITIO}/{p_nota(n)}"
    return page(d, f"{n['titulo']} | Blog Umarti Origen", n["resumen"], main, ld)


def indice_js(notas):
    """Índice para que la Tienda muestre las notas de cada categoría y subcategoría."""
    data = [{k: n.get(k, "") for k in ("slug", "titulo", "resumen", "seccion", "categoria", "subcategoria", "tema", "fecha")}
            | {"tags": n["tags"], "url": p_nota(n)} for n in notas]
    return ("/* Generado por _fuente/construir_blog.py. Lo usa la Tienda para mostrar las notas de cada categoría. */\n"
            "window.BLOG_INDICE = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")


def main():
    notas = [leer_nota(r) for r in glob.glob(os.path.join(NOTAS_DIR, "*.md"))]
    notas.sort(key=lambda n: n["fecha"], reverse=True)
    prods = [n for n in notas if n["seccion"] == "productos"]
    negs = [n for n in notas if n["seccion"] == "negocios"]

    escribir("blog/index.html", portada_blog(notas))

    cats_con = [c for c in CATEGORIAS if any(n.get("categoria") == c for n in prods)]
    chips_cats = "".join(f'<a href="{rel(2, p_cat(c))}" style="--c1:{COLORES[c][0]}"><span class="dot"></span>{esc(c)} <small>{sum(1 for n in prods if n.get("categoria") == c)}</small></a>' for c in cats_con)
    escribir("blog/productos/index.html", listado(
        2, "Notas de productos: guías, recetas y consejos | Blog Umarti Origen",
        "Guías para elegir, usar y cuidar los productos de la Tienda: mate, café, vinos, moda y más.",
        [("Blog", "blog/"), ("Productos", None)], "Blog", "Productos",
        "Guías, recetas y consejos para elegir, usar y cuidar los productos de la Tienda, ordenados por categoría.",
        "productos", prods, extra_top=f'      <div class="cat-chips">{chips_cats}</div>'))

    for c in cats_con:
        ncat = [n for n in prods if n["categoria"] == c]
        subs = [s for s in CATEGORIAS[c] if any(n["subcategoria"] == s for n in ncat)]
        conteo = {s: sum(1 for n in ncat if n["subcategoria"] == s) for s in subs}
        escribir(p_cat(c) + "index.html", listado(
            3, f"{c}: guías y consejos | Blog Umarti Origen", f"Todas las notas sobre {c}: cómo elegir, preparar y cuidar cada producto.",
            [("Blog", "blog/"), ("Productos", "blog/productos/"), (c, None)], "Productos", c,
            f"Todas las notas sobre {esc(c)}, vinculadas a esta categoría de la Tienda.", None, ncat,
            extra_top=store_band(3, c, c), chips_vals=subs, conteo=conteo))
        for s in subs:
            nsub = [n for n in ncat if n["subcategoria"] == s]
            escribir(p_sub(c, s) + "index.html", listado(
                4, f"{s}: guías y consejos | Blog Umarti Origen", f"Notas sobre {s}: cómo elegir, usar y cuidar.",
                [("Blog", "blog/"), ("Productos", "blog/productos/"), (c, p_cat(c)), (s, None)], c, s,
                f"Todas las notas sobre {esc(s)}.", None, nsub, extra_top=store_band(4, s, c)))

    temas_con = [t for t in TEMAS if any(n.get("tema") == t for n in negs)]
    conteo_t = {t: sum(1 for n in negs if n["tema"] == t) for t in temas_con}
    escribir("blog/negocios/index.html", listado(
        2, "Notas de negocios y comercio exterior | Blog Umarti Origen",
        "Comercio exterior, mercados y herramientas para comprar y vender entre Argentina, México y el mundo.",
        [("Blog", "blog/"), ("Negocios", None)], "Blog", "Negocios",
        "Comercio exterior, mercados y herramientas para comprar y vender entre países.", "negocios", negs,
        chips_vals=temas_con, conteo=conteo_t))
    for t in temas_con:
        escribir(p_tema(t) + "index.html", listado(
            3, f"{t} | Blog Umarti Origen", f"Notas sobre {t}.",
            [("Blog", "blog/"), ("Negocios", "blog/negocios/"), (t, None)], "Negocios", t,
            f"Notas de la sección Negocios sobre {esc(t.lower())}.", None, [n for n in negs if n["tema"] == t]))

    for t in sorted({t for n in notas for t in n["tags"]}):
        escribir(p_tag(t) + "index.html", listado(
            3, f"Notas sobre {t} | Blog Umarti Origen", f"Todas las notas del blog con la etiqueta {t}.",
            [("Blog", "blog/"), ("#" + t, None)], "Etiqueta", "#" + t,
            f"Todas las notas con la etiqueta {esc(t)}.", None, [n for n in notas if t in n["tags"]]))

    for n in notas:
        escribir(p_nota(n) + "index.html", pagina_nota(n, notas))

    escribir("assets/data/blog-indice.js", indice_js(notas))


if __name__ == "__main__":
    main()
