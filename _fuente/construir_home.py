#!/usr/bin/env python3
"""Genera el contenido de la portada (index.html, entre <main> y </main>).

Uso:  python3 _fuente/construir_home.py
El encabezado y el pie de index.html se mantienen a mano (son la base de todo el sitio);
este script solo reemplaza el cuerpo de la portada, con datos reales: categorías y cantidad de productos
de la Tienda, destinos con foto y las últimas notas del blog.
"""
import glob, html, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comun  # noqa: E402
from comun import slug  # noqa: E402
import construir_blog as cb  # noqa: E402
import construir_viajes as cv  # noqa: E402

esc = html.escape
INDEX = os.path.join(comun.RAIZ, "index.html")


def svg(path, size=24, sw=1.7):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>')


ICONO_CAT = {
    "Café, Té y Mate": '<path d="M6 10h10v4a5 5 0 0 1-10 0z"/><path d="M16 11h1.5a2 2 0 0 1 0 4H16M9 3l2 6M8 21h8"/>',
    "Regalos y Kits": '<rect x="3" y="9" width="18" height="12" rx="1"/><path d="M3 13h18M12 9v12M12 9c-2-4-6-4-6-1.5S10 9 12 9c2 0 6 0 6-1.5S14 5 12 9"/>',
    "Artículos Regionales": '<path d="M6 8h12l-1 13H7z"/><path d="M9 8a3 3 0 0 1 6 0"/><path d="M8.5 13h7M8 16.5h8"/>',
    "Bebidas": '<path d="M8 3h3v4l1.5 2v12h-6V9L8 7z"/><path d="M16 9h3v3a2 2 0 0 1-3 0zM17.5 14v7M16 21h3"/>',
    "Alimentos": '<path d="M4 12h16a8 8 0 0 1-16 0z"/><path d="M12 12c0-4 2-6 5-6-1 3-3 5-5 6zM12 12c-1-3-3-4-5-4 0 2 2 4 5 4"/>',
    "Salud y Bienestar": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/><path d="M7 12h3l1-2 2 4 1-2h3"/>',
    "Moda": '<path d="M9 3 4 6l2 4 2-1v12h8V9l2 1 2-4-5-3a3 3 0 0 1-6 0z"/>',
    "Tecnología": '<rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2 19h20"/>',
    "Herramientas y Jardín": '<path d="M12 21v-7M12 14c0-4 3-6 6-6 0 4-3 6-6 6zM12 16c0-3-2-5-5-5 0 3 2 5 5 5"/><path d="M8 21h8"/>',
    "Hogar y Cocina": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>',
    "Limpieza e Higiene": '<path d="M9 8h5l1 3v9a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1v-9z"/><path d="M10 8V5h4l3-1M14 5v3"/>',
    "Productos para viajes": '<rect x="4" y="8" width="16" height="12" rx="2"/><path d="M9 8V5h6v3M4 13h16"/>',
    "Deportes y aire libre": '<circle cx="6" cy="16" r="3.5"/><circle cx="18" cy="16" r="3.5"/><path d="M6 16l4-7h5l3 7M10 9 8.5 6H7M14 9l-1.5-3H15"/>',
}
I = {
    "tienda": '<path d="M3 9l2-5h14l2 5M4 9v11h16V9M3 9h18M9 20v-6h6v6"/>',
    "intl": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "comex": '<path d="M2 17h20l-2 4H4zM5 17V9h14v8M9 9V5h6v4"/>',
    "viajes": '<path d="M2 16l20-8-3-2-7 3-6-4-2 1 4 5-4 2-2-1-1 1z"/>',
    "cupon": '<path d="M20 12l-8 8-9-9V3h8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "blog": '<path d="M4 4h12l4 4v12H4z"/><path d="M8 10h8M8 14h8M8 18h5"/>',
    "buscar": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "flecha": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "hub": '<path d="M7 11l3-3 4 4 3-3 4 4-6 6-4-4-3 3-4-4z"/>',
    "box": '<path d="M3 8l9-5 9 5v8l-9 5-9-5zM3 8l9 5 9-5M12 13v8"/>',
    "serv": '<path d="M14 7l3-3 3 3-3 3M17 4v7a4 4 0 0 1-4 4H4"/><path d="M7 12l-3 3 3 3"/>',
    "empresa": '<path d="M3 21V8l6-4v17M9 21h12V11l-6-3"/><path d="M13 13h4M13 17h4"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "ruta": '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h7a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h7"/>',
}


def conteos():
    cat = json.load(open(os.path.join(AQUI, "tienda", "catalogo.json"), encoding="utf-8"))
    out = {}
    for p in cat.get("productos", []) + cat.get("afiliados", []):
        if p.get("estado", "Publicado") in ("Publicado",) or "estado" not in p:
            out[p.get("categoria")] = out.get(p.get("categoria"), 0) + 1
    return out


def destinos_con_foto(n=4):
    con = [d for d in cv.destacados() if (d.get("panel") or {}).get("foto")]
    resto = [d for d in cv.DESTINOS if (d.get("panel") or {}).get("foto") and d not in con]
    return (con + resto)[:n]


def notas(n=4):
    todas = [cb.leer_nota(r) for r in glob.glob(os.path.join(cb.NOTAS_DIR, "*.md"))]
    todas = [x for x in todas if not x["borrador"]]
    todas.sort(key=lambda x: (bool(x.get("imagen")), x["fecha"]), reverse=True)
    return todas[:n]


def img_nota(x):
    u = x.get("imagen") or ""
    return u if re.match(r"https?://", u) else u


def seccion_de(x):
    return {"productos": x.get("categoria") or "Productos", "negocios": x.get("tema") or "Negocios", "opinion": "Opinión"}[x["seccion"]]


def main_html():
    cuenta = conteos()
    tiles = []
    for c in cb.CATEGORIAS:
        c1, c2 = cb.COLORES.get(c, ("#c8693e", "#8f3f1d"))
        n = cuenta.get(c, 0)
        txt = "Muy pronto" if not n else f"{n} producto" + ("" if n == 1 else "s")
        tiles.append(f'<a class="h-cat" href="argentina/tienda/{slug(c)}/" style="--c1:{c1};--c2:{c2}">'
                     f'<span class="h-cat-ic">{svg(ICONO_CAT.get(c, I["box"]), 26)}</span><b>{esc(c)}</b><small>{txt}</small></a>')
    dest = destinos_con_foto(4)
    dest_html = "".join(
        f'<a class="h-dest" href="{cv.p_dest(d)}"><img src="{esc(d["panel"]["foto"])}" alt="" loading="lazy" '
        f'style="object-position:{esc(d["panel"].get("foto_pos") or "center")}">'
        f'<span class="h-dest-txt"><small>{esc(cv.PAISES[d["pais"]]["nombre"])}</small><b>{esc(d["nombre"])}</b></span></a>' for d in dest)
    ns = notas(4)
    destacada, otras = (ns[0], ns[1:]) if ns else (None, [])
    blog_feat = ""
    if destacada:
        x = destacada
        im = f'<img src="{esc(img_nota(x))}" alt="" loading="lazy">' if x.get("imagen") else '<span class="h-ph"></span>'
        blog_feat = (f'<a class="h-nota-feat" href="{cb.p_nota(x)}"><span class="h-nota-img">{im}</span>'
                     f'<span class="h-nota-body"><small>{esc(seccion_de(x))}</small><b>{esc(x["titulo"])}</b><p>{esc(x["resumen"])}</p>'
                     f'<span class="h-leer">Leer la nota {svg(I["flecha"], 16, 2)}</span></span></a>')
    blog_list = "".join(
        f'<a class="h-nota" href="{cb.p_nota(x)}">'
        + (f'<img src="{esc(img_nota(x))}" alt="" loading="lazy">' if x.get("imagen") else f'<span class="h-ph sm">{svg(I["blog"], 22)}</span>')
        + f'<span><small>{esc(seccion_de(x))}</small><b>{esc(x["titulo"])}</b></span></a>' for x in otras)
    # "collage" del blog: las portadas de las notas como fotos sueltas sobre la mesa
    fotos = [img_nota(x) for x in notas(8) if x.get("imagen")][:3]
    collage = "".join(f'<span class="h-polaroid p{i}"><img src="{esc(u)}" alt="" loading="lazy"></span>' for i, u in enumerate(fotos))

    return f'''  <main class="home">
    <!-- 1. Portada -->
    <section class="h-hero">
      <div class="wrap h-hero-grid">
        <div class="h-hero-txt">
          <span class="h-eyebrow">Tienda · Comercio exterior · Viajes</span>
          <h1>Productos con origen, <em>oportunidades globales</em> y destinos para descubrir.</h1>
          <p>Umarti Origen une una tienda con productos de Argentina y del mundo, un hub para hacer negocios entre países y guías para conocer los lugares de donde viene cada cosa. Empezamos por Argentina y México, y vamos sumando países.</p>
          <div class="h-ctas">
            <a class="btn btn-primary" href="argentina/tienda/">Ir a la Tienda</a>
            <a class="btn btn-ghost" href="hub/">Hub de Oportunidades</a>
          </div>
          <nav class="h-atajos" aria-label="Accesos rápidos">
            <a href="#h-tienda">{svg(I["tienda"], 18)}Tienda</a>
            <a href="international-shop/">{svg(I["intl"], 18)}International Shop</a>
            <a href="#h-comex">{svg(I["comex"], 18)}Comercio exterior</a>
            <a href="#h-viajes">{svg(I["viajes"], 18)}Destinos</a>
            <a href="#h-cupones">{svg(I["cupon"], 18)}Cupones</a>
            <a href="#h-blog">{svg(I["blog"], 18)}Blog</a>
          </nav>
        </div>
        <div class="h-hero-img">
          <img src="assets/img/home/portada.jpg" alt="Umarti Origen: tienda, comercio exterior, viajes, blog, recursos digitales y cupones" width="1672" height="941">
          <span class="h-sticker s1">🇦🇷 Tienda Argentina</span>
          <span class="h-sticker s2">{svg(I["intl"], 16)} Envíos al mundo</span>
          <span class="h-sticker s3">{svg(I["pin"], 16)} Argentina · México</span>
        </div>
      </div>
    </section>

    <!-- 2. Tienda -->
    <section class="h-sec" id="h-tienda" aria-labelledby="h-tienda-t">
      <div class="wrap">
        <div class="h-tienda">
          <div class="h-tienda-foto">
            <img src="assets/img/home/tienda.jpg" alt="Mate, termo, café y una laptop con la tienda en línea" loading="lazy">
            <span class="h-badge">{svg(I["tienda"], 18)} Tienda online</span>
          </div>
          <div class="h-tienda-txt">
            <span class="h-eyebrow terra">Tienda</span>
            <h2 id="h-tienda-t">Productos con origen, para tu día a día y tus viajes.</h2>
            <form class="h-buscar" action="argentina/tienda/productos/" method="get" role="search">
              {svg(I["buscar"], 20, 2)}
              <input type="search" name="q" placeholder="Buscá mates, termos, vinos, regalos…" aria-label="Buscar en la Tienda">
              <button type="submit">Buscar</button>
            </form>
            <div class="h-tienda-ctas">
              <a class="btn btn-primary" href="argentina/tienda/">Ir a la Tienda {svg(I["flecha"], 18, 2)}</a>
              <a class="h-intl" href="international-shop/">
                <span class="h-intl-ic">{svg(I["intl"], 24)}</span>
                <span><b>International Shop</b><small>Productos de distintos países con envío internacional · Shop in English</small></span>
                {svg(I["flecha"], 18, 2)}
              </a>
            </div>
          </div>
        </div>
        <div class="h-cats">{"".join(tiles)}</div>
      </div>
    </section>

    <!-- 3. Comercio exterior -->
    <section class="h-sec" id="h-comex" aria-labelledby="h-comex-t">
      <div class="wrap">
        <div class="h-comex">
          <img class="h-comex-bg" src="assets/img/home/comercio-exterior.jpg" alt="" loading="lazy">
          <div class="h-comex-txt">
            <span class="h-eyebrow sky">Mercados Globales</span>
            <h2 id="h-comex-t">Comercio exterior</h2>
            <p>Conectamos productos y oportunidades en mercados globales: publicá lo que buscás, encontrá proveedores y cerrá negocios entre países.</p>
            <a class="btn h-btn-naranja" href="hub/">{svg(I["intl"], 20)} Oportunidades comerciales {svg(I["flecha"], 18, 2)}</a>
          </div>
          <div class="h-comex-links">
            <a href="hub/"><span>{svg(I["hub"], 22)}</span><b>Hub de Oportunidades Globales</b><small>Publicá qué buscás y te conectamos</small></a>
            <a href="productos-de-exportacion/"><span>{svg(I["box"], 22)}</span><b>Productos de exportación</b><small>Listos para vender a otros mercados</small></a>
            <a href="servicios-de-comercio-exterior/"><span>{svg(I["serv"], 22)}</span><b>Servicios de comercio exterior</b><small>Aduana, logística, seguros y asesoría</small></a>
            <a href="empresas-exportadoras/"><span>{svg(I["empresa"], 22)}</span><b>Empresas exportadoras</b><small>Conocé quién produce y exporta</small></a>
          </div>
        </div>
      </div>
    </section>

    <!-- 4. Destinos -->
    <section class="h-sec" id="h-viajes" aria-labelledby="h-viajes-t">
      <div class="wrap">
        <div class="h-head">
          <div><span class="h-eyebrow sun">Viajes</span><h2 id="h-viajes-t">Destinos para conocer el origen</h2>
          <p>Guías de ciudades, pueblos mágicos y destinos naturales de Argentina y México: cuándo ir, qué comer, dónde dormir y cómo llegar.</p></div>
          <a class="h-ver" href="viajes/destinos/">Ver todos los destinos {svg(I["flecha"], 16, 2)}</a>
        </div>
        <div class="h-viajes">
          <a class="h-viaje-big" href="viajes/destinos/">
            <img src="assets/img/home/viajes-avion.jpg" alt="Ala de avión sobre las nubes al atardecer" loading="lazy">
            <span class="h-viaje-txt"><small>{svg(I["viajes"], 16)} Destinos</small><b>Elegí tu próximo viaje</b><span>Argentina, México y más países</span></span>
          </a>
          <a class="h-viaje-alto" href="viajes/#organiza">
            <img src="assets/img/home/viajes-playa.jpg" alt="Atardecer en el mar con pelícanos" loading="lazy">
            <span class="h-viaje-txt"><small>{svg(I["ruta"], 16)} Organizá tu viaje</small><b>Vuelos, alojamiento y seguro</b></span>
          </a>
          <div class="h-dests">{dest_html}</div>
        </div>
      </div>
    </section>

    <!-- 5. Cupones -->
    <section class="h-sec" id="h-cupones" aria-labelledby="h-cupones-t">
      <div class="wrap">
        <div class="h-cupones">
          <div class="h-cupones-txt">
            <span class="h-eyebrow sun">Cuponera</span>
            <h2 id="h-cupones-t">Descuentos de comercios, <em>muy pronto</em>.</h2>
            <p>Restaurantes, alojamientos, excursiones, spas, servicios y tiendas de Argentina, México y en línea. Estamos sumando los primeros comercios.</p>
            <div class="h-ctas">
              <a class="btn btn-primary" href="mi-tienda/?publicar=cupon">Publicá tu cupón</a>
              <a class="btn btn-ghost" href="cupones/">Conocé la Cuponera</a>
            </div>
          </div>
          <div class="h-cupones-art" aria-hidden="true">
            <span class="h-cup-card c1"><img src="assets/img/home/cupon-viajes.jpg" alt="" loading="lazy"></span>
            <span class="h-cup-card c2"><img src="assets/img/home/cupon-ticket.jpg" alt="" loading="lazy"></span>
            <span class="h-cup-tk"><b>15%</b><small>Viajes</small></span>
          </div>
        </div>
      </div>
    </section>

    <!-- 6. Blog -->
    <section class="h-sec h-sec-ult" id="h-blog" aria-labelledby="h-blog-t">
      <div class="wrap">
        <div class="h-blog-head">
          <div class="h-collage" aria-hidden="true">{collage}<span class="h-cinta"></span></div>
          <div>
            <span class="h-eyebrow terra">Blog</span>
            <h2 id="h-blog-t">Historias, guías y negocios con origen</h2>
            <p>Cómo elegir y cuidar cada producto, de dónde viene, y todo lo que hace falta para vender a otros países.</p>
            <a class="h-ver" href="blog/">Ir al blog {svg(I["flecha"], 16, 2)}</a>
          </div>
        </div>
        <div class="h-blog">
          {blog_feat}
          <div class="h-notas">{blog_list}</div>
        </div>
      </div>
    </section>
  </main>'''


def main():
    s = open(INDEX, encoding="utf-8").read()
    a, b = s.index("  <main"), s.index("</main>") + len("</main>")
    s = s[:a] + main_html() + s[b:]
    if "assets/css/home.css" not in s:
        s = re.sub(r'(<link rel="stylesheet" href="assets/css/umarti\.css[^"]*">)', r'\1\n  <link rel="stylesheet" href="assets/css/home.css">', s, count=1)
    open(INDEX, "w", encoding="utf-8").write(s)
    print("ok portada")


if __name__ == "__main__":
    main()
