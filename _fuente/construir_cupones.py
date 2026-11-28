#!/usr/bin/env python3
"""Genera la Cuponera a partir de _fuente/cupones/cupones.json (pestaña Cupones de la hoja 'Plan Ecommerce').

Uso:  python3 _fuente/construir_cupones.py
Genera cupones/ (portada) y cupones/<categoría>/, más assets/data/cupones-datos.js.
"""
import datetime, html, json, os, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comun  # noqa: E402
from comun import escribir, slug  # noqa: E402
sys.path.insert(0, os.path.join(AQUI, "tienda"))
from construir_tienda import barra_tienda  # noqa: E402

esc = html.escape
HOY = datetime.date.today()

ICONOS = {
    "Viajes": '<path d="M2 16l20-8-3-2-7 3-6-4-2 1 4 5-4 2-2-1-1 1z"/>',
    "Alojamientos": '<path d="M3 20V9l9-5 9 5v11"/><path d="M3 20h18M7 20v-6h4v6M15 12h3v3h-3z"/>',
    "Servicios": '<path d="M4 8h16v11H4zM9 8V5h6v3M4 13h16"/>',
    "Gastronomía": '<path d="M7 3v8a2 2 0 0 0 4 0V3M9 11v10M17 3c-2 0-3 2-3 6s1 5 3 5v7"/>',
    "Belleza y Spa": '<path d="M12 21c-4 0-7-3-7-7 3 0 5 1 7 4 2-3 4-4 7-4 0 4-3 7-7 7zM12 18c-2-3-2-7 0-11 2 4 2 8 0 11z"/>',
    "Productos": '<path d="M5 8h14l-1 13H6zM9 8V6a3 3 0 0 1 6 0v2"/>',
    "Digitales": '<path d="M7 3h10v18H7zM11 18h2"/>',
}
CATS = [
    ("Viajes", "viajes", ("#3f8a5c", "#1f5636"), "Excursiones, traslados y experiencias"),
    ("Alojamientos", "alojamientos", ("#2f7a8a", "#1b4f5a"), "Hoteles, cabañas, posadas y departamentos"),
    ("Gastronomía", "gastronomia", ("#c8693e", "#8f3f1d"), "Restaurantes, cafés, 2x1 y menús especiales"),
    ("Belleza y Spa", "belleza-y-spa", ("#b5577a", "#7a2f4e"), "Masajes, spa, estética y cuidado personal"),
    ("Servicios", "servicios", ("#3d87ab", "#225670"), "Seguros, asesorías y experiencias"),
    ("Productos", "productos", ("#c8922a", "#8a5e0c"), "Tienda Umarti y comercios aliados"),
    ("Digitales", "digitales", ("#7357a8", "#46337a"), "Suscripciones, apps y eSIM"),
]
CAT = {c[0]: c for c in CATS}

# Cupones de muestra para la demo a comercios (comercios ficticios; no son cupones reales ni se pueden usar)
_VENCE_DEMO = (datetime.date.today() + datetime.timedelta(days=45)).isoformat()
DEMO = [
    dict(codigo="DEMO-1", titulo="15% en excursiones a bodegas", comercio="Ruta del Vino Tours", categoria="Viajes", tipo="Código", cupon="RUTA15",
         descuento="15%", descripcion="Visitas guiadas con degustación en tres bodegas, con traslado incluido.",
         condiciones="Válido de lunes a viernes. No acumulable con otras promociones.", pais="Argentina", ciudad="Mendoza"),
    dict(codigo="DEMO-2", titulo="2x1 en empanadas los martes", comercio="La Salteña de Palermo", categoria="Gastronomía", tipo="Oferta", cupon="",
         descuento="2x1", descripcion="Empanadas salteñas al horno de barro.", condiciones="Solo los martes, en el local. Mostrá el cupón al pedir.",
         pais="Argentina", ciudad="Buenos Aires"),
    dict(codigo="DEMO-3", titulo="20% en tu primer masaje", comercio="Spa Agua Termal", categoria="Belleza y Spa", tipo="Código", cupon="SPA20",
         descuento="20%", descripcion="Masaje de 60 minutos con aceites esenciales y acceso al circuito de aguas.",
         condiciones="Con reserva previa. De lunes a jueves.", pais="México", ciudad="Querétaro"),
]
for _c in DEMO:
    _c.update(vence=_VENCE_DEMO, link="", destacado=False, exclusivo=_c["codigo"] == "DEMO-1", destino="", tema="", estado="Ejemplo", slug="")


def rel(depth, path=""):
    return ("../" * depth) + path if depth or path else "./"


def icon(cat, size=24):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICONOS[cat]}</svg>'


def iniciales(nombre):
    ps = [p for p in nombre.replace("del", "").replace("de", "").split() if p]
    return "".join(p[0] for p in ps[:2]).upper()


def dias(c):
    try:
        return (datetime.date.fromisoformat(c["vence"]) - HOY).days
    except ValueError:
        return 999


def fecha(iso):
    try:
        y, m, d = iso.split("-"); return f"{d}/{m}/{y}"
    except ValueError:
        return iso


def lugar(c):
    if c["pais"] == "En línea":
        return "En línea"
    return f'{c["ciudad"]}, {c["pais"]}' if c.get("ciudad") else c["pais"]


def art(c, cv, con_id=False):
    _, _, colores, _ = CAT[c["categoria"]]
    dest = next((x for x in cv.DESTINOS if x["slug"] == c.get("destino")), None)
    land = ""
    if dest:
        colores = dest["colores"]
        back, front = cv.PAISAJES[dest["paisaje"]]
        land = f'<svg class="land" viewBox="0 0 400 160" preserveAspectRatio="none" aria-hidden="true"><path d="{back}" opacity=".14"/><path d="{front}" opacity=".22"/></svg>'
    ide = f' id="art-{c["codigo"]}"' if con_id else ""
    return (f'<div class="art"{ide} style="--c1:{colores[0]};--c2:{colores[1]}" aria-hidden="true"><span class="ring"></span>{land}'
            f'<span class="ico">{icon(c["categoria"])}</span><span class="big">{esc(c["descuento"])}</span></div>')


def cta(c):
    if c["tipo"] == "Código" and c.get("cupon"):
        return f'<button class="cu-cta code" type="button" data-cupon="{c["codigo"]}">Ver código<span class="peel">{esc(c["cupon"][-2:])}</span></button>'
    return f'<button class="cu-cta" type="button" data-cupon="{c["codigo"]}">Ver descuento</button>'


def card(c, cv):
    d = dias(c)
    soon = 0 <= d <= 14
    if c["exclusivo"]:
        rib = '<div class="cu-ribbon excl"><b>★</b> Exclusivo Umarti</div>'
    elif soon:
        rib = '<div class="cu-ribbon">⏱ Vence pronto</div>'
    else:
        rib = ""
    texto = esc(" ".join([c["titulo"], c["comercio"], c["categoria"], c["descripcion"], c.get("ciudad", ""), c["pais"]]).lower())
    exp = f'<span class="cu-exp soon">Quedan {d} días</span>' if soon else f'<span class="cu-exp">Vence {fecha(c["vence"])}</span>'
    ej = '<span class="cu-ej">Ejemplo</span>' if c["estado"] == "Ejemplo" else ""
    return f'''        <article class="cupon{" cu-demo" if c["codigo"].startswith("DEMO") else ""}{" hot" if soon and not c["exclusivo"] else ""}" id="{c['codigo'].lower()}" data-cat="{esc(c['categoria'])}" data-pais="{esc(c['pais'])}" data-texto="{texto}">
          {rib}{art(c, cv, True)}
          <div class="cu-body"><span class="cu-logo">{esc(iniciales(c['comercio']))}</span><div><h3>{esc(c['titulo'])}</h3><p class="cu-merchant">{esc(c['comercio'])} · {esc(lugar(c))}</p></div></div>
          <div class="cu-meta"><span class="cu-tag{" oferta" if c["tipo"] == "Oferta" else ""}">{esc(c['tipo'])}</span>{exp}{ej}</div>
          {cta(c)}
        </article>'''


def slide(c, cv):
    excl = "<em>Exclusivo</em>" if c["exclusivo"] else ""
    ej = '<span class="cu-ej" style="margin:0;align-self:flex-start">Ejemplo</span>' if c["estado"] == "Ejemplo" else ""
    return f'''          <div class="cu-slide">
            <div class="txt">
              <div class="who"><span class="cu-logo">{esc(iniciales(c['comercio']))}</span>{esc(c['comercio'])}</div>
              <h2>{excl}{esc(c['titulo'])}</h2>
              {ej}
              {cta(c)}
            </div>
            {art(c, cv)}
          </div>'''


def barra(depth, actual, cats=None):
    cats = CATS if cats is None else cats
    if cats:
        links = [f'<a href="{rel(depth, "cupones/")}"{" aria-current=\"page\"" if actual == "" else ""}>Destacados</a>']
        links += [f'<a href="{rel(depth, "cupones/" + s + "/")}"{" aria-current=\"page\"" if actual == s else ""}>{n}</a>' for n, s, _, _ in cats]
    else:  # sin cupones publicados: la barra lleva a las partes de la página para comercios
        links = ['<a href="#como-se-ve">Así se ve un cupón</a>', '<a href="#como-publicar">Cómo publicar</a>', '<a href="#donde-aparece">Dónde aparece</a>']
    return f'''    <div class="cu-bar">
      <div class="wrap-wide">
        <a class="cu-brand" href="{rel(depth, 'cupones/')}"><span class="tk">%</span><span>Cuponera<small>Umarti Origen</small></span></a>
        <nav class="cu-nav" aria-label="Categorías de cupones">{"".join(links)}</nav>
        <a class="cu-pub" href="{rel(depth, 'mi-tienda/')}?publicar=cupon">Publicá tu cupón</a>
      </div>
    </div>'''


def tools(cats_presentes, conteo=True):
    chips = '<div class="cu-chips" role="group" aria-label="Categoría"><button type="button" data-cat-filter="" aria-pressed="true">Todos</button>' + "".join(
        f'<button type="button" data-cat-filter="{esc(n)}" aria-pressed="false">{esc(n)}</button>' for n in cats_presentes) + "</div>" if len(cats_presentes) > 1 else ""
    return f'''      <div class="cu-tools">
        <label class="cu-search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="cu-q" type="search" placeholder="Buscar cupones, comercios o ciudades" aria-label="Buscar cupones"></label>
        <select class="cu-sel" id="cu-pais" aria-label="País"><option value="">Todos los países</option><option>Argentina</option><option>México</option><option>En línea</option></select>
        {chips}
        <span class="v-count" id="cu-count"></span>
      </div>'''


def merchant_band(depth):
    return f'''      <section class="merchant-band" aria-labelledby="h-merch">
        <div>
          <span class="eyebrow" style="color:var(--cu)">Para comercios</span>
          <h2 id="h-merch">¿Tenés un comercio? Publicá tu cupón</h2>
          <p>Restaurantes, spas, alojamientos, tiendas, servicios o apps: sumá tu descuento a la Cuponera y llegá a viajeros y compradores de Argentina, México y el mundo.</p>
          <a class="cu-pub" href="{rel(depth, 'mi-tienda/')}?publicar=cupon">Publicá tu cupón</a>
          <small class="cu-pub-nota">Para publicar, creá tu cuenta y validá tu identidad.</small>
        </div>
        <ul>
          <li>Aparecés en la categoría y en la ciudad de tu comercio.</li>
          <li>Los cupones de viaje se muestran también en las guías de destino.</li>
          <li>Ves cuántas personas abrieron tu código.</li>
        </ul>
      </section>'''


def dialogos():
    cats = "".join(f"<option>{n}</option>" for n, _, _, _ in CATS)
    return f'''  <dialog class="cu-dlg" id="dlg-cupon" aria-label="Cupón"><div class="cu-dlg-body"></div></dialog>
  <dialog class="cu-dlg" id="dlg-pub" aria-labelledby="pub-t">
    <div class="head-pub" style="position:relative"><h2 id="pub-t">Publicá tu cupón</h2><p>Contanos de tu comercio y del descuento que querés ofrecer.</p><button class="x" type="button" data-close aria-label="Cerrar">×</button></div>
    <div class="in" style="padding:20px 24px 24px">
      <form>
        <div class="form-grid">
          <div class="field full"><label for="p-com">Comercio <span class="req">*</span></label><input id="p-com" required maxlength="80"></div>
          <div class="field"><label for="p-cat">Categoría <span class="req">*</span></label><select id="p-cat" required><option value="">Elegí</option>{cats}</select></div>
          <div class="field"><label for="p-desc">Descuento <span class="req">*</span></label><input id="p-desc" required placeholder="Ej.: 15% o 2x1"></div>
          <div class="field"><label for="p-ciu">Ciudad o en línea <span class="req">*</span></label><input id="p-ciu" required placeholder="Ej.: Querétaro"></div>
          <div class="field"><label for="p-mail">Correo <span class="req">*</span></label><input id="p-mail" type="email" required autocomplete="email"></div>
          <div class="field full"><label for="p-det">Detalle y condiciones</label><textarea id="p-det" placeholder="Qué incluye, días válidos, vencimiento."></textarea></div>
        </div>
        <div class="form-foot"><small>Revisamos cada cupón antes de publicarlo.</small><button class="cu-cta" style="width:auto;padding:0 22px" type="submit">Enviar cupón</button></div>
      </form>
      <div class="ok" hidden><h3>¡Recibimos tu cupón!</h3><p>En la versión final te escribimos para confirmarlo antes de publicarlo. En este prototipo no se envía nada.</p><button class="btn-line-dark" type="button" data-close>Cerrar</button></div>
    </div>
  </dialog>'''


def page(depth, title, desc, actual, main, cats=None, noindex=True):
    pre = rel(depth)
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
{'  <meta name="robots" content="noindex">' if noindex else ''}
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
{comun.FUENTES}
  <link rel="stylesheet" href="{pre}assets/css/umarti.css">
  <link rel="stylesheet" href="{pre}assets/css/blog.css">
  <link rel="stylesheet" href="{pre}assets/css/viajes.css">
  <link rel="stylesheet" href="{pre}assets/css/tienda.css">
  <link rel="stylesheet" href="{pre}assets/css/cupones.css">
</head>
<body data-prefix="{pre}">

{comun.header(pre)}
{barra(depth, actual, cats)}

  <main>
{main}
  </main>

{comun.footer(pre)}
{dialogos()}
  <div class="toast" id="toast" role="status"></div>
  <script src="{pre}assets/js/header.js"></script>
  <script src="{pre}assets/data/cupones-datos.js"></script>
  <script src="{pre}assets/js/cupones.js"></script>
</body>
</html>
'''


def cat_tiles(depth, cupones, cats):
    out = []
    for n, s, (c1, c2), sub in cats:
        k = sum(1 for c in cupones if c["categoria"] == n)
        out.append(f'<a class="cat-tile" href="{rel(depth, "cupones/" + s + "/")}" style="--c1:{c1};--c2:{c2}"><span class="ico">{icon(n)}</span><strong>{n}</strong><small>{k} cupones · {esc(sub)}</small></a>')
    return '<div class="cat-tiles">' + "".join(out) + "</div>"


def portada(cupones, cv, cats):
    d = 1
    dest = [c for c in cupones if c["destacado"]][:6]
    tienda = next((c for c in cupones if c["comercio"] == "Umarti Origen" and c["exclusivo"]), None)
    pronto = sorted([c for c in cupones if 0 <= dias(c) <= 30], key=dias)[:3]
    banner = ""
    if tienda:
        banner = f'''      <div class="cu-banner"><span class="cu-logo">UO</span><div><strong>{esc(tienda['titulo'])} en la Tienda Umarti</strong><small>{esc(tienda['descripcion'])}</small></div><button class="go" type="button" data-cupon="{tienda['codigo']}">Obtené el código</button></div>'''
    main = f'''    <div class="wrap">
      <section class="cu-hero" aria-label="Cupones destacados">
        <div class="cu-slider"><div class="cu-track">
{chr(10).join(slide(c, cv) for c in dest)}
        </div></div>
        <div class="cu-ctrl"><button class="arr" type="button" data-slide="-1" aria-label="Anterior">←</button><div class="cu-dots">{"".join("<span></span>" for _ in dest)}</div><button class="arr" type="button" data-slide="1" aria-label="Siguiente">→</button></div>
      </section>
{banner}
      <section class="cu-sec" aria-labelledby="h-pop">
        <h2 id="h-pop">Cupones populares de hoy</h2>
{tools([n for n, _, _, _ in cats])}
        <div class="cu-grid" id="cu-grid">
{chr(10).join(card(c, cv) for c in cupones)}
          <p class="cu-empty" id="cu-empty">No encontramos cupones con esa búsqueda.</p>
        </div>
      </section>
      <section class="cu-sec" aria-labelledby="h-cat">
        <h2 id="h-cat">Explorá por categoría</h2>
        {cat_tiles(d, cupones, cats)}
      </section>
{merchant_band(d)}
    </div>'''
    return page(d, "Cuponera Umarti: cupones de descuento en viajes, restaurantes, servicios y productos",
                "Cupones y códigos de descuento en viajes, restaurantes, servicios, productos y suscripciones digitales en Argentina, México y en línea.", "", main,
                cats=cats, noindex=any(c["estado"] == "Ejemplo" for c in cupones))


def portada_vacia(cv):
    d = 1
    tiles = "".join(f'<div class="cat-tile" style="--c1:{c1};--c2:{c2}"><span class="ico">{icon(n)}</span><strong>{n}</strong><small>{esc(sub)}</small></div>'
                    for n, s, (c1, c2), sub in CATS)
    partes = [("1", "El descuento, bien grande", "15%, 2x1, envío gratis: lo primero que se ve."),
              ("2", "Tu comercio y tu ciudad", "Con tus iniciales o logo, y dónde se usa el cupón."),
              ("3", "Código u oferta", "Un código para usar en tu web o caja, o una oferta que se muestra en el local."),
              ("4", "Vencimiento", "Cuando faltan pocos días, el cupón se marca como “Vence pronto”."),
              ("5", "Ver código", "Al tocarlo, tu cliente ve el código y las condiciones. Vos ves cuántas personas lo abrieron.")]
    anat = "".join(f'<li><b>{n}</b><span><strong>{esc(t)}</strong>{esc(x)}</span></li>' for n, t, x in partes)
    pasos = [("Creá tu tienda", "Desde Mi tienda, con tus datos y la validación de identidad, para que cada cupón sea de un comercio real."),
             ("Cargá tu cupón", "Descuento, código u oferta, condiciones, vencimiento y la ciudad o si es en línea."),
             ("Lo revisamos y se publica", "Revisamos cada cupón antes de publicarlo. Después lo podés pausar o editar cuando quieras.")]
    pasos_html = "".join(f'<li><span class="cv-n">{i}</span><h3>{esc(t)}</h3><p>{esc(x)}</p></li>' for i, (t, x) in enumerate(pasos, 1))
    faqs = [("¿Qué tipo de descuentos puedo publicar?", "Un código de descuento (por ejemplo, 15% con el código RUTA15) o una oferta que tu cliente muestra en el local (por ejemplo, 2x1 los martes). Sirve para comercios con local, servicios, tiendas en línea y apps."),
            ("¿Quiénes ven mi cupón?", "Las personas que entran a la Cuponera y, según la categoría, también quienes leen la guía de viaje de tu ciudad: los cupones de alojamientos, gastronomía y excursiones se muestran en los destinos."),
            ("¿Puedo cambiarlo o pausarlo?", "Sí. Desde tu tienda podés editar las condiciones, cambiar el vencimiento o pausarlo cuando quieras."),
            ("¿Cómo sé si funciona?", "Vas a ver cuántas personas abrieron tu código. Si el cupón lleva a tu web, conviene que el código sea exclusivo para la Cuponera, así medís las ventas que llegan desde acá.")]
    faq_html = "".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    main = f'''    <div class="wrap">
      <section class="cv-hero" aria-labelledby="h-cv">
        <div class="cv-hero-txt">
          <span class="cv-pill"><i></i>Muy pronto: estamos sumando los primeros comercios</span>
          <h1 id="h-cv">Descuentos de comercios de Argentina, México y en línea</h1>
          <p>La Cuponera de Umarti reúne cupones de restaurantes, alojamientos, excursiones, spas, servicios y tiendas. Todavía no hay cupones publicados: si tenés un comercio, podés ser de los primeros.</p>
          <div class="cv-acts">
            <a class="cu-pub big" href="{rel(d, 'mi-tienda/')}?publicar=cupon">Publicá tu cupón</a>
            <a class="cv-sec" href="{rel(d, 'mi-cuenta/')}?crear&desde=cupones">Creá tu cuenta y te avisamos</a>
          </div>
        </div>
        <div class="cv-hero-art" aria-hidden="true">
          <div class="cv-tk t1"><b>15%</b><span>Excursiones</span></div>
          <div class="cv-tk t2"><b>2x1</b><span>Gastronomía</span></div>
          <div class="cv-tk t3"><b>20%</b><span>Spa</span></div>
        </div>
      </section>

      <section class="cu-sec" id="como-se-ve" aria-labelledby="h-demo">
        <span class="eyebrow" style="color:var(--cu-dark)">Para comercios</span>
        <h2 id="h-demo">Así se vería tu cupón</h2>
        <p class="cv-lead">Estos son cupones de muestra, con comercios ficticios. Tocá <b>Ver código</b> para ver exactamente lo que ve tu cliente.</p>
        <div class="cv-demo">
          <div class="cu-grid cv-grid" id="cu-grid">
{chr(10).join(card(c, cv) for c in DEMO)}
          </div>
          <ol class="cv-anat">{anat}</ol>
        </div>
      </section>

      <section class="cu-sec" id="como-publicar" aria-labelledby="h-pasos">
        <h2 id="h-pasos">Cómo publicar tu cupón</h2>
        <ol class="cv-pasos">{pasos_html}</ol>
        <div class="cv-cta-line"><a class="cu-pub big" href="{rel(d, 'mi-tienda/')}?publicar=cupon">Empezar ahora</a><small>Para publicar, creá tu tienda y validá tu identidad.</small></div>
      </section>

      <section class="cu-sec" id="donde-aparece" aria-labelledby="h-cats">
        <h2 id="h-cats">Categorías donde podés publicar</h2>
        <div class="cat-tiles cv-tiles">{tiles}</div>
      </section>

      <section class="cu-sec cv-faq" aria-labelledby="h-faq">
        <h2 id="h-faq">Preguntas de comercios</h2>
        {faq_html}
      </section>
{merchant_band(d)}
    </div>'''
    return page(d, "Cuponera Umarti: publicá los cupones de descuento de tu comercio",
                "Publicá cupones y códigos de descuento de tu restaurante, alojamiento, excursión, spa, servicio o tienda en la Cuponera de Umarti Origen, para Argentina, México y en línea.",
                "", main, cats=[], noindex=False)


def pagina_cat(nombre, s, colores, sub, cupones, cv, cats):
    d = 2
    lista = [c for c in cupones if c["categoria"] == nombre]
    # Foto de la franja: assets/img/cupones/<categoría>.jpg (si existe)
    ruta = f"assets/img/cupones/{s}.jpg"
    foto = f'<img class="ch-foto ch-{s}" src="{rel(d, ruta)}" alt="">' if os.path.exists(os.path.join(comun.RAIZ, ruta)) else ""
    main = f'''    <div class="wrap">
{comun_crumbs(d, nombre)}
      <section class="cat-head{' has-foto' if foto else ''}" style="--c1:{colores[0]};--c2:{colores[1]}">{foto}<span class="ico">{icon(nombre)}</span><span class="eyebrow" style="color:#fff;opacity:.85">Cuponera</span><h1>Cupones de {nombre.lower()}</h1><p>{esc(sub)}. Tocá Ver código para obtener tu descuento.</p></section>
{tools([])}
      <div class="cu-grid" id="cu-grid">
{chr(10).join(card(c, cv) for c in lista)}
        <p class="cu-empty" id="cu-empty">No encontramos cupones con esa búsqueda.</p>
      </div>
      <section class="cu-sec" style="padding-top:56px" aria-labelledby="h-otras">
        <h2 id="h-otras">Otras categorías</h2>
        {cat_tiles(d, cupones, cats)}
      </section>
{merchant_band(d)}
    </div>'''
    return page(d, f"Cupones de descuento en {nombre.lower()} | Cuponera Umarti", f"Cupones y códigos de descuento en {nombre.lower()}: {sub.lower()}.", s, main,
                cats=cats, noindex=any(c["estado"] == "Ejemplo" for c in lista))


def comun_crumbs(depth, nombre):
    import construir_blog
    return construir_blog.crumbs(depth, [("Cuponera", "cupones/"), (nombre, None)])


def datos_js(cupones, cv):
    out = []
    for c in cupones:
        dest = next((x for x in cv.DESTINOS if x["slug"] == c.get("destino")), None)
        out.append(dict(codigo=c["codigo"], titulo=c["titulo"], comercio=c["comercio"], iniciales=iniciales(c["comercio"]),
                        lugar=lugar(c), descripcion=c["descripcion"], tipo=c["tipo"], cupon=c.get("cupon", ""),
                        condiciones=c.get("condiciones", ""), vence_txt=fecha(c["vence"]), link=c.get("link", ""),
                        destino_url=f'viajes/{dest["pais"]}/{dest["slug"]}/' if dest else "", destino_nombre=dest["nombre"] if dest else "",
                        tema=c.get("tema", ""), tema_url=(c["tema"] + "/") if c.get("tema") else "", ejemplo=c["estado"] == "Ejemplo", online=c["pais"] == "En línea"))
    return ("/* Generado por _fuente/construir_cupones.py a partir de la pestaña Cupones. */\n"
            "window.CUPONES = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")


def main():
    import construir_viajes as cv
    cupones = json.load(open(os.path.join(AQUI, "cupones", "cupones.json"), encoding="utf-8"))
    for c in cupones:
        if c["categoria"] not in CAT:
            raise SystemExit(f"{c['codigo']}: categoría desconocida {c['categoria']}")
    cupones = [c for c in cupones if dias(c) >= 0]  # los vencidos no se publican
    cats = [x for x in CATS if any(c["categoria"] == x[0] for c in cupones)]
    if cupones:
        escribir("assets/data/cupones-datos.js", datos_js(cupones, cv))
        escribir("cupones/index.html", portada(cupones, cv, cats))
    else:
        escribir("assets/data/cupones-datos.js", datos_js(DEMO, cv))
        escribir("cupones/index.html", portada_vacia(cv))
    for n, s, col, sub in CATS:
        ruta = os.path.join(comun.RAIZ, "cupones", s)
        if (n, s, col, sub) in cats:
            escribir(f"cupones/{s}/index.html", pagina_cat(n, s, col, sub, cupones, cv, cats))
        elif os.path.isdir(ruta):  # categoría sin cupones: no se publica una página vacía
            shutil.rmtree(ruta)


if __name__ == "__main__":
    main()
