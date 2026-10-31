#!/usr/bin/env python3
"""Genera el blog a partir de las notas en _fuente/blog/notas/*.md

Uso:  python3 _fuente/construir_blog.py

Cada nota es un archivo .md con un encabezado así:
---
titulo: Cómo preparar un buen mate, paso a paso
resumen: Una o dos oraciones que aparecen en las tarjetas y en Google.
seccion: productos            (productos, negocios u opinion)
categoria: Café, Té y Mate    (solo productos: una categoría de la Tienda)
subcategoria: Mates y bombillas
tema: Comercio exterior       (negocios; en opinion: Negocios o Experiencias)
autor: marcelo-uranga         (solo opinion: una clave de autores.py)
tags: mate, yerba mate, preparación   (dos o tres)
fecha: 2026-10-08
destacada: si                 (opcional)
borrador: si                  (opcional: se genera la página pero no aparece en el blog ni en Google)
---
y después el texto. Formato: ## título, ### subtítulo, **negrita**, *cursiva*, [enlace](url),
listas con "- " o "1. ", tablas con |, "> " para un recuadro de consejo, y fotos con
![descripción](assets/img/blog/foto.jpg "Epígrafe opcional") en una línea sola
(dos o más fotos seguidas se muestran una al lado de la otra).
Foto principal (opcional): imagen: assets/img/blog/foto.jpg  e  imagen_alt: descripción
  imagen_pos: center 70%   (opcional: qué parte de la foto se ve en las tarjetas; 0% arriba, 100% abajo)
"""
import glob, html, json, os, re, sys, urllib.parse

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comun  # noqa: E402
sys.path.insert(0, os.path.join(AQUI, "blog"))
from autores import AUTORES, TEMAS_OPINION  # noqa: E402
from publicidad import ANUNCIOS  # noqa: E402
import datetime  # noqa: E402
from comun import slug, fecha_larga, escribir, SITIO  # noqa: E402

esc = html.escape

# ---------- taxonomía: mismas categorías y subcategorías que la Tienda ----------
CATEGORIAS = {
    "Café, Té y Mate": ["Mates y bombillas", "Yerba", "Café y té"],
    "Regalos y Kits": ["Kits de mate y café", "Regalos corporativos", "Personalizados"],
    "Artículos regionales": ["Bolsos materos", "Marroquinería y riñoneras", "Juegos de asado", "Portatermos y llaveros"],
    "Alimentos y Bebidas": ["Vinos y destilados", "Dulces y snacks", "Otros alimentos"],
    "Hogar, Moda y más": ["Moda", "Hogar y cocina", "Salud y bienestar", "Tecnología"],
}
TIENDA_TEXTO = {
    "Café, Té y Mate": "Mates, bombillas, yerbas, cafés y tés seleccionados.",
    "Regalos y Kits": "Kits armados y regalos para empresas.",
    "Artículos regionales": "Bolsos materos, marroquinería, juegos de asado y artículos con identidad argentina.",
    "Alimentos y Bebidas": "Vinos, destilados, dulces y alimentos con origen.",
    "Hogar, Moda y más": "Moda, hogar, bienestar y tecnología.",
}
TEMAS = ["Comercio exterior", "Mercados", "Ecommerce y ventas", "Cómo usar Umarti"]
COLORES = {
    "Café, Té y Mate": ("#5b7a43", "#33472a"), "Regalos y Kits": ("#c8922a", "#8a5e0c"),
    "Artículos regionales": ("#8a5a3c", "#55341f"), "Alimentos y Bebidas": ("#9a3445", "#5c1c27"),
    "Hogar, Moda y más": ("#4b5d78", "#2b3648"),
    "Alimentos": ("#c8693e", "#8f3f1d"),  # color por defecto
    "negocios": ("#3d87ab", "#225670"),
    "opinion": ("#7a4a8c", "#4a2a5a"),
}
SECCION_NOMBRE = {"productos": "Productos", "negocios": "Negocios", "opinion": "Opinión"}

NOTAS_DIR = os.path.join(AQUI, "blog", "notas")


def destinos_de_nota(slug_nota):
    """Destinos de Viajes que enlazan esta nota (para mostrar 'Conocé el origen')."""
    sys.path.insert(0, os.path.join(AQUI, "viajes"))
    from destinos import DESTINOS, PAISES
    out = []
    for x in DESTINOS:
        if any(o.get("nota") == slug_nota for o in x["origen"]):
            out.append((x, PAISES[x["pais"]]["nombre"]))
    return out


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
    n["borrador"] = meta.get("borrador", "").lower() in ("si", "sí", "true")
    n["html"], n["toc"] = markdown(m.group(2))
    palabras = len(re.findall(r"\w+", m.group(2)))
    n["min"] = max(2, -(-palabras // 200))
    if n["seccion"] == "productos":
        cat, sub = n.get("categoria"), n.get("subcategoria")
        if cat not in CATEGORIAS or sub not in CATEGORIAS[cat]:
            raise SystemExit(f"{n['slug']}: categoría o subcategoría que no existe en la Tienda: {cat} / {sub}")
        n["etiqueta"], n["colores"] = sub, COLORES.get(cat, COLORES["Alimentos"])
    elif n["seccion"] == "opinion":
        if n.get("autor") not in AUTORES:
            raise SystemExit(f"{n['slug']}: autor desconocido {n.get('autor')}. Opciones: {list(AUTORES)}")
        if n.get("tema") not in TEMAS_OPINION:
            raise SystemExit(f"{n['slug']}: tema de opinión desconocido {n.get('tema')}. Opciones: {TEMAS_OPINION}")
        a = AUTORES[n["autor"]]
        n["etiqueta"], n["colores"] = a["columna"], COLORES["opinion"]
        n["glifo"] = a["iniciales"][0]
        return n
    else:
        if n.get("tema") not in TEMAS:
            raise SystemExit(f"{n['slug']}: tema desconocido {n.get('tema')}. Opciones: {TEMAS}")
        n["etiqueta"], n["colores"] = n["tema"], COLORES["negocios"]
    n["glifo"] = n["etiqueta"][0]
    return n


def inline(t):
    t = esc(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    return t


IMG_RE = re.compile(r'^!\[([^\]]*)\]\((\S+?)(?:\s+"([^"]*)")?\)\s*$')


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
        if IMG_RE.match(ln):
            figs = []
            while i < len(lines) and IMG_RE.match(lines[i]):
                alt, src, pie = IMG_RE.match(lines[i]).groups(); i += 1
                cap = f"<figcaption>{inline(pie)}</figcaption>" if pie else ""
                figs.append(f'<figure><img src="{{{{RAIZ}}}}{esc(src)}" alt="{esc(alt)}" loading="lazy">{cap}</figure>')
            cls = "post-figs" + (" duo" if len(figs) > 1 else "")
            out.append(f'<div class="{cls}">' + "".join(figs) + "</div>"); continue
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
        while i < len(lines) and lines[i].strip() and not re.match(r"(#{2,3} |> |\||- |\d+\. |!\[)", lines[i]):
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
def p_autor(a): return f"blog/autor/{a}/"
P_OPINION = "blog/opinion/"


# ---------- piezas ----------
def cover(n, cls="", depth=None):
    c1, c2 = n["colores"]
    if n.get("imagen") and depth is not None:
        pos = f' style="object-position:{esc(n["imagen_pos"])}"' if n.get("imagen_pos") else ""
        return f'<div class="cover has-photo {cls}" style="--c1:{c1};--c2:{c2}"><img src="{rel(depth, n["imagen"])}" alt="" loading="lazy"{pos}><span>{esc(n["etiqueta"])}</span></div>'
    return f'<div class="cover {cls}" data-glyph="{esc(n["glifo"])}" style="--c1:{c1};--c2:{c2}" aria-hidden="true"><span>{esc(n["etiqueta"])}</span></div>'


def kicker(n):
    sec = SECCION_NOMBRE[n["seccion"]]
    return f'<p class="post-kicker"><b>{sec}</b> · {esc(n.get("categoria") or n.get("tema"))}</p>'


def avatar(a, depth, cls="avatar"):
    if a["foto"]:
        return f'<img class="{cls}" src="{rel(depth, a["foto"])}" alt="{esc(a["nombre"])}" width="48" height="48">'
    return f'<span class="{cls}" aria-hidden="true">{esc(a["iniciales"])}</span>'


def meta_linea(n):
    autor = f'Por {AUTORES[n["autor"]]["nombre"]} · ' if n["seccion"] == "opinion" else ""
    return f'{autor}{fecha_larga(n["fecha"])} · {n["min"]} min de lectura'


def card(n, depth):
    neg = {"negocios": " neg", "opinion": " op"}.get(n["seccion"], "")
    texto = esc(" ".join([n["titulo"], n["resumen"], n.get("categoria", ""), n.get("subcategoria", ""), n.get("tema", "")] + n["tags"]).lower())
    return f'''        <a class="post-card{neg}" href="{rel(depth, p_nota(n))}" data-texto="{texto}" data-sub="{esc(n.get('subcategoria') or n.get('tema'))}">
          {cover(n, "", depth)}
          {kicker(n)}
          <h3>{esc(n['titulo'])}</h3>
          <p>{esc(n['resumen'])}</p>
          <span class="post-meta">{esc(meta_linea(n))}</span>
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
    items = [("Todo", "blog/", "todo"), ("Productos", "blog/productos/", "productos"), ("Negocios", "blog/negocios/", "negocios"), ("Opinión", P_OPINION, "opinion")]
    out = [f'<a href="{rel(depth, p)}"{" aria-current=\"page\"" if k == actual else ""}>{t}</a>' for t, p, k in items]
    out.append(f'<a class="ghost" href="{rel(depth, "viajes/")}">Guías de viaje, en Viajes →</a>')
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
        <p>{esc(nombre)} en la Tienda<small>{esc(texto)}</small></p>
        <a class="btn btn-primary" href="{rel(depth, 'argentina/tienda/' + slug(cat) + '/')}">Ver en la Tienda</a>
      </div>'''


def page(depth, title, desc, main, jsonld=None, scripts="", noindex=False, imagen=""):
    pre = rel(depth) if depth else ""
    canon = '\n  <meta name="robots" content="noindex">' if noindex else ""
    if imagen and SITIO:
        canon += f'\n  <meta property="og:image" content="{SITIO}/{imagen}">'
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


def columna_band(depth, opin, clave="marcelo-uranga", h="h2"):
    a = AUTORES[clave]
    suyas = [n for n in opin if n["autor"] == clave]
    if suyas:
        cuerpo = grid(suyas[:3], depth)
    else:
        cuerpo = f'''      <div class="col-empty">
        <strong>La primera columna llega pronto.</strong>
        <p>{esc(a["columna_bajada"])}</p>
      </div>'''
    return f'''      <div class="col-band">
        <a class="col-author" href="{rel(depth, p_autor(clave))}">
          {avatar(a, depth, "avatar xl")}
          <span class="col-name"><small>La columna de</small>{esc(a["nombre"])}</span>
          <span class="col-title">{esc(a["columna"])}</span>
          <span class="col-sub">{esc(a["columna_bajada"])}</span>
          <span class="col-more">Conocé al autor →</span>
        </a>
        <div class="col-list">
{cuerpo}
        </div>
      </div>'''


# ---------- publicidad ----------
def anuncio(n, formato, depth):
    """Aviso para un espacio de la nota; si no hay ninguno vigente, la invitación a anunciar."""
    hoy = datetime.date.today().isoformat()
    clave = n.get("categoria") or n.get("tema") or ""
    for a in ANUNCIOS:
        if not a.get("activo", True) or formato not in a.get("formatos", []):
            continue
        if a.get("categorias") and clave not in a["categorias"]:
            continue
        if (a.get("desde") and hoy < a["desde"]) or (a.get("hasta") and hoy > a["hasta"]):
            continue
        link = a["link"] if re.match(r"https?:", a["link"]) else rel(depth, a["link"])
        img = f'<img src="{rel(depth, a["imagen"])}" alt="" loading="lazy">' if a.get("imagen") else ""
        return f'''<aside class="ad ad-{formato}" aria-label="Publicidad">
            <span class="ad-label">Publicidad · {esc(a["anunciante"])}</span>
            <a class="ad-body" href="{esc(link)}" rel="sponsored noopener" target="_blank">{img}<span class="ad-txt"><strong>{esc(a["titulo"])}</strong><span>{esc(a["texto"])}</span><b>{esc(a.get("cta", "Ver más"))} →</b></span></a>
          </aside>'''
    return f'''<aside class="ad ad-{formato} ad-house" aria-label="Espacio publicitario">
            <span class="ad-label">Publicidad</span>
            <a class="ad-body" href="{rel(depth, 'publicidad/')}"><span class="ad-txt"><strong>Tu marca, acá</strong><span>Llegá a quienes leen sobre {esc(clave.lower() or "productos con origen")}. Este espacio está disponible.</span><b>Anunciá en Umarti →</b></span></a>
          </aside>'''


def con_anuncio(html_nota, aviso):
    """Inserta el aviso antes del segundo título de la nota (o al final si es corta)."""
    partes = html_nota.split("<h2 ", 2)
    if len(partes) == 3:
        return partes[0] + "<h2 " + partes[1] + aviso + "\n<h2 " + partes[2]
    return html_nota + aviso


# ---------- productos de la Tienda en las notas ----------
def productos_de_nota(n, depth, maximo=3):
    import construir_tienda as ct
    productos, _ = ct.cargar()
    def score(p):
        s = 0
        if p["subcategoria"] == n.get("subcategoria"): s += 3
        if p["categoria"] == n.get("categoria"): s += 1
        s += len(set(p["temas"]) & set(n["tags"]))
        return s
    elegidos = [p for p in sorted(productos, key=score, reverse=True) if score(p) > 0][:maximo]
    if not elegidos:
        return ""
    items = []
    for p in elegidos:
        pr, mon = ct.precio_principal(p)
        c1, c2 = COLORES.get(p["categoria"], COLORES["Alimentos"])
        if p.get("fotos"):
            media = f'<img src="{esc(p["fotos"][0])}" alt="" loading="lazy">'
        else:
            media = f'<span class="cover" data-glyph="{esc(p["nombre"][0])}" style="--c1:{c1};--c2:{c2}"></span>'
        ej = '<span class="np-ej">Ejemplo</span>' if p["estado"] == "Ejemplo" else ""
        items.append(f'''<a class="np-item" href="{rel(depth, ct.p_prod(p))}">
              <span class="np-media">{media}{ej}</span>
              <span class="np-info"><small>{esc(p["subcategoria"])}</small><strong>{esc(p["nombre"])}</strong><span class="np-price">{pr} <small>{mon}</small></span></span>
            </a>''')
    sub = n.get("subcategoria") or n.get("categoria")
    url_sub = "argentina/tienda/" + slug(n.get("categoria", "")) + "/?sub=" + urllib.parse.quote(sub)
    titulo = "Para tu mate, en la Tienda" if "mate" in n["tags"] else f"{sub} en la Tienda"
    return f'''<section class="note-prods" aria-labelledby="np-h">
            <div class="np-head"><h2 id="np-h">{esc(titulo)}</h2><a href="{rel(depth, url_sub)}">Ver todo en {esc(sub)} →</a></div>
            <div class="np-grid">
            {"".join(items)}
            </div>
          </section>'''


# ---------- páginas ----------
def portada_blog(notas):
    d = 1
    prods = [n for n in notas if n["seccion"] == "productos"]
    negs = [n for n in notas if n["seccion"] == "negocios"]
    opin = [n for n in notas if n["seccion"] == "opinion"]
    dest = next((n for n in prods if n["destacada"]), prods[0])
    ultimas = [n for n in notas if n is not dest][:4]
    side = "\n".join(f'''          <a class="side-item" href="{rel(d, p_nota(n))}">
            {cover(n, "", d)}
            <div><h3>{esc(n['titulo'])}</h3><small>{SECCION_NOMBRE[n['seccion']]} · {n['min']} min</small></div>
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
        <p>Guías, recetas y consejos sobre los productos de la Tienda, notas para hacer negocios entre países y columnas de opinión.</p>
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
      <section class="blk" aria-labelledby="h-op">
        <div class="blk-head">
          <div><h2 id="h-op">Opinión</h2><p>Columnas con nombre y apellido: miradas personales sobre negocios, emprender entre países y lo que pasa en el camino.</p></div>
          <a class="op-link" href="{rel(d, P_OPINION)}">Ver todas las columnas →</a>
        </div>
{columna_band(d, opin)}
      </section>

      <section class="blk" aria-labelledby="h-tags">
        <div class="blk-head"><div><h2 id="h-tags">Explorá por etiqueta</h2></div></div>
        <div class="tag-cloud">{cloud}</div>
      </section>

      <div class="viajes-note">
        <div>
          <h2>¿Buscás guías de viaje?</h2>
          <p>Las notas sobre destinos viven en la sección Viajes, conectadas con estas: la guía de Misiones te lleva a la yerba mate, y la nota de yerba te lleva a Misiones.</p>
        </div>
        <a href="{rel(d, 'viajes/')}">Ir a Viajes</a>
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
    es_op = n["seccion"] == "opinion"
    a = AUTORES.get(n.get("autor"))
    if es_op:
        cr = [("Blog", "blog/"), ("Opinión", P_OPINION), (n["titulo"], None)]
        kick = f'<p class="post-kicker"><b style="color:var(--plum)">Opinión</b><a href="{rel(d, P_OPINION)}">{esc(a["columna"])}</a><span>·</span><span>{esc(n["tema"])}</span></p>'
    elif es_prod:
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
        if es_op and o.get("autor") == n.get("autor"): s += 3
        s += len(set(o["tags"]) & set(n["tags"]))
        if o["seccion"] == n["seccion"]: s += 1
        return s
    otras = sorted([o for o in notas if o is not n and not o["borrador"]], key=lambda o: (score(o), o["fecha"]), reverse=True)
    relacionadas = otras[:3]

    toc = ""
    if len(n["toc"]) >= 2:
        toc = '<div class="box toc"><h2>En esta nota</h2><ol>' + "".join(f'<li><a href="#{h}">{esc(t)}</a></li>' for h, t in n["toc"]) + "</ol></div>"
    if es_op:
        redes = "".join(f'<a href="{esc(u)}" rel="noopener" target="_blank">{esc(r)}</a>' for r, u in a["redes"])
        box = f'''<div class="box author-mini">
            {avatar(a, d)}
            <div><small>La columna de</small><strong>{esc(a["nombre"])}</strong><span>{esc(a["rol"])}</span></div>
            <a class="btn-line" href="{rel(d, p_autor(n["autor"]))}">Conocé al autor →</a>
          </div>'''
        mismas = [o for o in notas if o is not n and o["seccion"] == "opinion" and not o["borrador"]]
        mas = ""
        if mismas:
            mas = '<div class="box"><h2>Más columnas</h2><ul class="mini-list">' + "".join(f'<li><a href="{rel(d, p_nota(o))}">{esc(o["titulo"])}</a></li>' for o in mismas[:5]) + f'</ul><a class="all" href="{rel(d, P_OPINION)}">Todas las columnas</a></div>'
    elif es_prod:
        cat, sub = n["categoria"], n["subcategoria"]
        mismas = [o for o in notas if o is not n and o.get("categoria") == cat]
        box = f'''<div class="box store">
            <strong>{esc(sub)} en la Tienda</strong>
            <p>{esc(TIENDA_TEXTO.get(cat, f"Productos de {cat}."))}</p>
            <a class="btn-line" href="{rel(d, 'argentina/tienda/' + slug(cat) + '/?sub=' + urllib.parse.quote(sub))}">Ver productos →</a>
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

    if n["borrador"]:
        tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in n["tags"])
    else:
        tags = "".join(f'<a class="tag" href="{rel(d, p_tag(t))}">{esc(t)}</a>' for t in n["tags"])
    dests = destinos_de_nota(n["slug"])
    origen = ""
    if dests:
        origen = '<div class="box" style="background:#e3f1ea;border-color:#cfe5d9"><h2>Conocé el origen</h2><ul class="mini-list">' + "".join(
            f'<li><a href="{rel(d, f"viajes/{x['pais']}/{x['slug']}/")}">{esc(x["nombre"])}, {esc(pn)}</a></li>' for x, pn in dests) + '</ul><a class="all" style="color:#1f5a3f" href="' + rel(d, "viajes/") + '">Todas las guías de viaje</a></div>'
    fecha_html = f'<span><time datetime="{n["fecha"]}">{fecha_larga(n["fecha"])}</time></span><span>{n["min"]} min de lectura</span>'
    if es_op:
        byline = f'''<div class="byline">{avatar(a, d)}<p><a href="{rel(d, p_autor(n["autor"]))}">{esc(a["nombre"])}</a><span class="post-meta">{fecha_html}</span></p></div>'''
        portada = ""
        firma = f'''<div class="author-box">
            {avatar(a, d, "avatar xl")}
            <div>
              <small>Sobre el autor</small>
              <h2><a href="{rel(d, p_autor(n["autor"]))}">{esc(a["nombre"])}</a></h2>
              <p>{esc(a["bio"][0])}</p>
            </div>
          </div>
          <p class="op-disclaimer">Las columnas de opinión expresan la mirada personal de su autor.</p>'''
    else:
        byline = f'<p class="post-meta">{fecha_html}<span>Equipo Umarti Origen</span></p>'
        portada = "" if n.get("imagen") else cover(n, "post-cover")
        firma = ""
    foto = ""
    if n.get("imagen"):
        foto = f'''
        <figure class="post-hero"><img src="{rel(d, n["imagen"])}" alt="{esc(n.get("imagen_alt", n["titulo"]))}"></figure>'''
    aviso = ""
    if n["borrador"]:
        aviso = '      <div class="draft-banner"><strong>Borrador.</strong> Esta nota no aparece en el blog ni en Google hasta que le quites la línea <code>borrador: si</code>.</div>\n'
    cuerpo = n["html"].replace("{{RAIZ}}", rel(d))
    if not n["borrador"]:
        cuerpo = con_anuncio(cuerpo, anuncio(n, "en-nota", d))
    tienda = productos_de_nota(n, d) if es_prod else ""
    lateral = anuncio(n, "lateral", d) if not n["borrador"] else ""
    main = f'''    <div class="wrap">
{crumbs(d, cr)}
{aviso}      <header class="post-head{' op' if es_op else ''}{' has-photo' if foto else ''}">
        <div class="post-head-text">
        {kick}
        <h1>{esc(n['titulo'])}</h1>
        <p class="lead">{esc(n['resumen'])}</p>
        {byline}
        </div>{foto}
      </header>
      {portada}
      <div class="post-layout">
        <article class="prose">
{cuerpo}
          {tienda}
          <div class="post-tags" aria-label="Etiquetas">{tags}</div>
          {firma}
        </article>
        <aside class="post-aside">
          <div class="aside-sticky">
          {toc}
          {box}
          {mas}
          {origen}
          {lateral}
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
          "author": ({"@type": "Person", "name": a["nombre"], "jobTitle": a["rol"]} | ({"url": f"{SITIO}/{p_autor(n['autor'])}"} if SITIO else {})) if es_op else {"@type": "Organization", "name": "Umarti Origen"},
          "publisher": {"@type": "Organization", "name": "Umarti Origen"}}
    if SITIO:
        ld["mainEntityOfPage"] = f"{SITIO}/{p_nota(n)}"
    if es_op:
        ld["articleSection"] = "Opinión"
    if n.get("imagen") and SITIO:
        ld["image"] = f"{SITIO}/{n['imagen']}"
    return page(d, f"{n['titulo']} | Blog Umarti Origen", n["resumen"], main, ld, noindex=n["borrador"], imagen=n.get("imagen", ""))


def pagina_publicidad():
    d = 1
    main = f'''    <div class="wrap">
{crumbs(d, [("Anunciá en Umarti", None)])}
      <div class="blog-head">
        <span class="eyebrow">Publicidad</span>
        <h1>Anunciá en Umarti</h1>
        <p>Mostrá tu marca a personas que leen sobre los productos que vendés: mate, café, vinos, alimentos regionales, comercio exterior y viajes.</p>
      </div>
      <div class="ad-formats">
        <div class="adf"><b>En la nota</b><p>Un aviso horizontal en medio del texto, donde más se lee. Ideal para presentar un producto o una promoción.</p></div>
        <div class="adf"><b>Lateral</b><p>Un aviso en la columna de la derecha, que acompaña al lector mientras recorre la nota.</p></div>
        <div class="adf"><b>Por categoría</b><p>Elegí en qué notas aparecés: solo en las de mate, en las de vinos, en las de comercio exterior o en todo el blog.</p></div>
      </div>
      <form class="ad-form" id="ad-form">
        <h2>Contanos qué querés anunciar</h2>
        <div class="ad-grid">
          <label>Nombre<input name="nombre" required></label>
          <label>Empresa o marca<input name="empresa" required></label>
          <label>Correo<input name="correo" type="email" required></label>
          <label>Teléfono o WhatsApp<input name="tel"></label>
          <label class="full">¿En qué notas te gustaría aparecer?<input name="categorias" placeholder="Por ejemplo: mate, café, comercio exterior"></label>
          <label class="full">Mensaje<textarea name="mensaje" rows="4"></textarea></label>
        </div>
        <button class="btn btn-primary" type="submit">Enviar consulta</button>
        <p class="ad-ok" hidden>¡Gracias! Te vamos a escribir para contarte formatos y precios. (Prototipo: el formulario todavía no envía datos.)</p>
      </form>
    </div>
    <script>
      document.getElementById('ad-form').addEventListener('submit', function (e) {{ e.preventDefault(); this.querySelector('.ad-ok').hidden = false; this.querySelector('button').disabled = true; }});
    </script>'''
    return page(d, "Anunciá en Umarti: publicidad en el blog | Umarti Origen",
                "Publicá tu marca en el blog de Umarti Origen, en las notas de mate, café, vinos, alimentos regionales, comercio exterior y viajes.", main)


def pagina_opinion(opin):
    d = 2
    cols = "\n".join(columna_band(d, opin, k) for k in AUTORES)
    temas_con = [t for t in TEMAS_OPINION if any(n["tema"] == t for n in opin)]
    lista = ""
    if opin:
        conteo = {t: sum(1 for n in opin if n["tema"] == t) for t in temas_con}
        chips = chips_filtro(temas_con, conteo) if len(temas_con) > 1 else ""
        lista = f'''
      <h2 class="sec-title">Todas las columnas</h2>
{chips}
{list_tools()}
      <div class="list-wrap">
{grid(opin, d, "b-grid")}
      </div>'''
    main = f'''    <div class="wrap">
{crumbs(d, [("Blog", "blog/"), ("Opinión", None)])}
      <div class="blog-head">
        <span class="eyebrow">Blog</span>
        <h1>Opinión</h1>
        <p>Columnas con nombre y apellido. Miradas personales sobre negocios, emprender entre países y las experiencias que hay detrás de Umarti.</p>
{tabs(d, "opinion")}
      </div>
{cols}
{lista}
    </div>'''
    return page(d, "Opinión: columnas sobre negocios y experiencias | Blog Umarti Origen",
                "Columnas de opinión sobre negocios, comercio entre Argentina y México, emprendimiento y experiencias personales.",
                main, scripts=f'\n  <script src="{rel(d)}assets/js/blog.js"></script>' if opin else "")


def pagina_autor(clave, opin):
    d = 3
    a = AUTORES[clave]
    suyas = [n for n in opin if n["autor"] == clave]
    bio = "".join(f"<p>{esc(x)}</p>" for x in a["bio"])
    redes = "".join(f'<a href="{esc(u)}" rel="noopener me" target="_blank">{esc(r)}</a>' for r, u in a["redes"])
    redes = f'<div class="author-links">{redes}</div>' if redes else ""
    if suyas:
        notas_html = f'''<h2 class="sec-title">Sus columnas</h2>
{grid(suyas, d)}'''
    else:
        notas_html = f'''<div class="col-empty"><strong>La primera columna de {esc(a["nombre"].split()[0])} llega pronto.</strong><p>Mientras tanto, podés recorrer las <a href="{rel(d, "blog/")}">notas del blog</a>.</p></div>'''
    main = f'''    <div class="wrap">
{crumbs(d, [("Blog", "blog/"), ("Opinión", P_OPINION), (a["nombre"], None)])}
      <section class="author-hero">
        {avatar(a, d, "avatar xxl")}
        <div>
          <span class="eyebrow">{esc(a["rol"])}</span>
          <h1>{esc(a["nombre"])}</h1>
          <p class="col-line">Columna <b>{esc(a["columna"])}</b> · {esc(a["columna_bajada"])}</p>
          <div class="author-bio">{bio}</div>
          {redes}
        </div>
      </section>
      <div class="list-wrap">
      {notas_html}
      </div>
    </div>'''
    persona = {"@type": "Person", "name": a["nombre"], "jobTitle": a["rol"], "description": " ".join(a["bio"]),
               "worksFor": {"@type": "Organization", "name": "Umarti"}}
    if a["redes"]:
        persona["sameAs"] = [u for _, u in a["redes"]]
    ld = {"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": persona}
    return page(d, f"{a['nombre']}: columna {a['columna']} | Blog Umarti Origen",
                f"{a['rol']}. {a['columna_bajada']} Todas sus columnas de opinión en el blog de Umarti Origen.", main, ld)


def indice_js(notas):
    """Índice para que la Tienda muestre las notas de cada categoría y subcategoría."""
    data = [{k: n.get(k, "") for k in ("slug", "titulo", "resumen", "seccion", "categoria", "subcategoria", "tema", "fecha")}
            | {"tags": n["tags"], "url": p_nota(n)} for n in notas]
    return ("/* Generado por _fuente/construir_blog.py. Lo usa la Tienda para mostrar las notas de cada categoría. */\n"
            "window.BLOG_INDICE = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")


def main():
    todas = [leer_nota(r) for r in glob.glob(os.path.join(NOTAS_DIR, "*.md"))]
    todas.sort(key=lambda n: n["fecha"], reverse=True)
    notas = [n for n in todas if not n["borrador"]]
    opin = [n for n in notas if n["seccion"] == "opinion"]
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

    escribir(P_OPINION + "index.html", pagina_opinion(opin))
    escribir("publicidad/index.html", pagina_publicidad())
    for k in AUTORES:
        escribir(p_autor(k) + "index.html", pagina_autor(k, opin))

    for n in todas:
        escribir(p_nota(n) + "index.html", pagina_nota(n, notas))

    escribir("assets/data/blog-indice.js", indice_js(notas))


if __name__ == "__main__":
    main()
