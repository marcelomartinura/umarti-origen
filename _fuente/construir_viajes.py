#!/usr/bin/env python3
"""Genera la sección Viajes a partir de _fuente/viajes/destinos.py

Uso:  python3 _fuente/construir_viajes.py
Genera viajes/index.html, una página por país y una guía por destino.
"""
import glob, html, json, os, sys
from urllib.parse import quote

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "viajes"))
import comun  # noqa: E402
from comun import escribir, slug, SITIO  # noqa: E402
from destinos import PAISES, DESTINOS, CONTINENTES, DESTACADOS, DESPEGAR_URL  # noqa: E402
import construir_blog  # noqa: E402

esc = html.escape
TIPOS = ["Aventura", "Cultura", "Gastronomía", "Montaña", "Naturaleza", "Nieve", "Urbano", "Vino"]

# títulos de las notas del blog, para enlazarlas desde los destinos
NOTAS = {}
for r in glob.glob(os.path.join(AQUI, "blog", "notas", "*.md")):
    n = construir_blog.leer_nota(r)
    NOTAS[n["slug"]] = n

PAISAJES = {
    "montana": ['M0 160 L0 104 L48 70 L80 92 L132 34 L178 86 L214 60 L262 108 L312 52 L360 96 L400 76 L400 160Z',
                'M0 160 L0 130 L70 100 L120 124 L190 92 L250 128 L320 104 L400 126 L400 160Z'],
    "ciudad": ['M0 160V112h22V92h16v20h14V66h22v46h16V98h14V52h10V36h6v16h10v60h18V82h26v30h16V70h20v42h22V90h18v22h14V76h26v36h16V96h14v64Z',
               'M0 160V134h40v-12h30v12h50v-8h40v8h60v-14h40v14h60v-6h40v6h40v26Z'],
    "agua": ['M0 112 Q50 92 100 112 T200 112 T300 112 T400 112 V160 H0Z',
             'M0 132 Q50 116 100 132 T200 132 T300 132 T400 132 V160 H0Z'],
    "cerros": ['M0 160 L0 114 Q60 64 120 104 Q170 52 232 100 Q292 70 340 106 Q372 90 400 110 V160Z',
               'M0 160 L0 134 Q80 110 150 130 Q220 108 290 132 Q350 118 400 134 V160Z'],
}


def rel(depth, path=""):
    return ("../" * depth) + path if depth or path else "./"


def p_pais(p): return f"viajes/{p}/"
def p_dest(d): return f"viajes/{d['pais']}/{d['slug']}/"


def vcover(colores, paisaje, titulo="", sub="", sun=True):
    c1, c2 = colores
    back, front = PAISAJES[paisaje]
    t = f"<b>{esc(titulo)}</b>" if titulo else ""
    s = f"<small>{esc(sub)}</small>" if sub else ""
    sol = '<span class="sun"></span>' if sun else ""
    return (f'<div class="vcover" style="--c1:{c1};--c2:{c2}">{sol}'
            f'<svg class="land" viewBox="0 0 400 160" preserveAspectRatio="none" aria-hidden="true">'
            f'<path d="{back}" opacity=".16"/><path d="{front}" opacity=".24"/></svg>{t}{s}</div>')


def dest_card(d, depth):
    pais = PAISES[d["pais"]]["nombre"]
    tipos = "".join(f'<span class="tipo">{esc(t)}</span>' for t in d["tipos"])
    texto = esc(" ".join([d["nombre"], d["region"], pais, d["resumen"]] + d["tipos"]).lower())
    return f'''        <a class="dest-card" href="{rel(depth, p_dest(d))}" data-tipos="{esc('|'.join(d['tipos']))}" data-texto="{texto}">
          {vcover(d['colores'], d['paisaje'], d['nombre'], f"{d['region']}, {pais}" if d['region'] != d['nombre'] else pais)}
          <div class="body">
            <div class="tipos">{tipos}</div>
            <p>{esc(d['resumen'])}</p>
            <div class="facts"><span><b>Ideal:</b> {esc(d['dias'])}</span><span><b>Presupuesto:</b> {esc(d['presupuesto'])}</span></div>
          </div>
        </a>'''


def chips(tipos_presentes):
    btns = ['<button type="button" data-tipo="" aria-pressed="true">Todos</button>']
    btns += [f'<button type="button" data-tipo="{esc(t)}" aria-pressed="false">{esc(t)}</button>' for t in TIPOS if t in tipos_presentes]
    return '<div class="chip-row" role="group" aria-label="Filtrar por tipo de viaje"><span>Filtrar por:</span>' + "".join(btns) + "</div>"


def crumbs(depth, items):
    return construir_blog.crumbs(depth, items)


def page(depth, title, desc, main, jsonld=None):
    pre = rel(depth)
    ld = f'\n  <script type="application/ld+json">\n{json.dumps(jsonld, ensure_ascii=False, indent=2)}\n  </script>' if jsonld else ""
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
{comun.FUENTES}
  <link rel="stylesheet" href="{pre}assets/css/umarti.css">
  <link rel="stylesheet" href="{pre}assets/css/blog.css">
  <link rel="stylesheet" href="{pre}assets/css/viajes.css">{ld}
</head>
<body>

{comun.header(pre)}

  <main>
{main}
  </main>

{comun.footer(pre)}

  <script src="{pre}assets/js/header.js"></script>
  <script src="{pre}assets/js/viajes.js"></script>
</body>
</html>
'''


ICON_CHECK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg>'


def planner():
    dl = "".join(f'<option value="{esc(d["nombre"])}">' for d in DESTINOS)
    intereses = "".join(f'<label><input type="checkbox" name="intereses" value="{esc(t)}"><span>{esc(t)}</span></label>' for t in TIPOS)
    return f'''      <section class="planner" id="planificar" aria-labelledby="h-plan">
        <div class="planner-info">
          <span class="eyebrow">Planificá tu viaje</span>
          <h2 id="h-plan">Armá tu viaje a medida</h2>
          <p>Contanos adónde querés ir y cómo te gusta viajar. Te enviamos una propuesta con recorrido, alojamiento y experiencias.</p>
          <ul>
            <li>{ICON_CHECK}<span>Itinerario por días, pensado para tus intereses.</span></li>
            <li>{ICON_CHECK}<span>Sugerencias de alojamiento según tu presupuesto.</span></li>
            <li>{ICON_CHECK}<span>Los sabores y productos de cada lugar, para disfrutar allá y llevarte a casa.</span></li>
          </ul>
        </div>
        <div class="planner-card">
          <div id="plan-step-form">
            <form id="plan-form">
              <div class="form-grid">
                <div class="field"><label for="pl-dest">Destino soñado <span class="req">*</span></label><input id="pl-dest" required list="destinos-dl" placeholder="Ej.: Mendoza o Bariloche"></div>
                <div class="field"><label for="pl-mes">¿Cuándo?</label><input id="pl-mes" type="month"></div>
                <div class="field"><label for="pl-dias">Días de viaje</label><input id="pl-dias" type="number" min="1" max="60" placeholder="Ej.: 7"></div>
                <div class="field"><label for="pl-quien">¿Con quién viajás?</label><select id="pl-quien"><option>Solo o sola</option><option>En pareja</option><option>En familia</option><option>Con amigos</option><option>Viaje de trabajo</option></select></div>
                <div class="field full"><label for="pl-pres">Presupuesto por persona (USD)</label><select id="pl-pres"><option>Hasta 500</option><option>500 a 1.000</option><option selected>1.000 a 2.500</option><option>2.500 a 5.000</option><option>Más de 5.000</option></select></div>
                <div class="field full"><span class="label" style="display:block;font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:8px">Lo que más te interesa</span><div class="interest-chips">{intereses}</div></div>
                <div class="field"><label for="pl-nombre">Nombre <span class="req">*</span></label><input id="pl-nombre" required maxlength="80" autocomplete="name"></div>
                <div class="field"><label for="pl-mail">Correo <span class="req">*</span></label><input id="pl-mail" type="email" required autocomplete="email"></div>
              </div>
              <div class="form-foot">
                <small>Prototipo: por ahora el formulario no envía datos.</small>
                <button class="btn-green" type="submit">Pedir mi propuesta</button>
              </div>
            </form>
            <datalist id="destinos-dl">{dl}</datalist>
          </div>
          <div class="planner-ok" id="plan-step-ok" hidden>
            <div class="tick"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg></div>
            <h3>¡Gracias!</h3>
            <p>En la versión final, acá queda registrado tu pedido y te escribimos con una propuesta a medida. En este prototipo no se envía nada.</p>
            <button class="btn-green" type="button" id="plan-again">Armar otro viaje</button>
          </div>
        </div>
      </section>'''


SERVICIOS = [
    ("Alojamiento", '<path d="M4 21V7l8-4 8 4v14"/><path d="M9 21v-6h6v6M9 10h.01M15 10h.01"/>'),
    ("Vuelos", '<path d="M2 16l20-8-3-2-7 3-6-4-2 1 4 5-4 2-2-1-1 1z"/>'),
    ("Seguro médico", '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="m9 12 2 2 4-4"/>'),
    ("Autos", '<path d="M5 17h14M5 17a2 2 0 1 1 0 .01M19 17a2 2 0 1 1 0 .01M3 13l2-6h14l2 6v4H3z"/>'),
    ("Excursiones", '<circle cx="12" cy="12" r="9"/><path d="m15 9-2 6-4 0 2-6z"/>'),
    ("Paquetes", '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>'),
    ("Traslados y transporte", '<rect x="4" y="3" width="16" height="14" rx="3"/><path d="M4 11h16M8 21l1.5-4M16 21l-1.5-4M8 14h.01M16 14h.01"/>'),
]


def aviso(depth, n):
    """Espacio publicitario de Viajes: viajes-1, viajes-2 o viajes-3 (ver _fuente/publicidad.py)."""
    import avisos
    return avisos.espacio(f"viajes-{n}", depth, "viajes", "Viajes").replace('class="ad ', 'class="ad v-ad ', 1)


def organiza(d):
    def tarjeta(n, ic):
        svg = f'<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ic}</svg>'
        k = CLAVES_SERV[n]
        if serv_abierto(k):
            return f'<a class="service on" href="{rel(d, p_serv(k))}">{svg}<strong>{n}</strong><small>Ver opciones →</small></a>'
        return f'<a class="service" href="{rel(d, p_serv(k))}">{svg}<strong>{n}</strong><small>Próximamente</small></a>'
    servicios = "".join(tarjeta(n, ic) for n, ic in SERVICIOS)
    return f'''      <section class="v-section" id="organiza" aria-labelledby="h-org">
        <div class="v-head"><div><h2 id="h-org">Organizá tu viaje</h2><p>Reservá con nuestros aliados y resolvé tus dudas antes de salir.</p></div></div>
        <div class="services">{servicios}</div>
        <a class="hz-link" href="{rel(d, 'recursos/diferencia-horaria/')}"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg><span><b>Diferencia horaria:</b> ¿qué hora es en tu destino?</span><em>Calcular →</em></a>
        <div class="org-cols">
          <div class="org-card org-reserva">
            <span class="eyebrow">Reservá</span>
            <h3>Vuelos, hoteles y paquetes</h3>
            <p>Buscá y compará vuelos, alojamiento, autos y paquetes en Despegar, nuestro aliado para reservar tu viaje.</p>
            <ul>
              <li>{ICON_CHECK}<span>Vuelos y hoteles en todo el mundo.</span></li>
              <li>{ICON_CHECK}<span>Paquetes con vuelo y alojamiento.</span></li>
              <li>{ICON_CHECK}<span>Autos, traslados y asistencia al viajero.</span></li>
            </ul>
            <a class="btn-green" href="{esc(link_aliado("vuelos", DESPEGAR_URL))}" target="_blank" rel="sponsored noopener">Buscar</a>
          </div>
          <div class="org-card org-asist">
            <img src="{rel(d, 'assets/img/viajes/avatar-umarti.jpg')}" alt="Asistente de viajes de Umarti">
            <div>
              <span class="eyebrow">Asistencia</span>
              <h3>Tu asistente de viaje</h3>
              <p>Muy pronto vas a poder consultarnos lo que necesites: qué ver, cómo moverte, qué llevar y qué probar en cada destino.</p>
              <span class="org-pronto">Próximamente</span>
            </div>
          </div>
        </div>
      </section>'''


def recomendaciones(d):
    notas = [n for n in NOTAS.values() if not n.get("borrador") and ("Viajes" in n.get("tags", []) or n.get("seccion") == "viajes")]
    cards = []
    for n in notas[:3]:
        cards.append(f'<a class="reco" href="{rel(d, "blog/" + n["slug"] + "/")}"><span class="reco-tag">Nota</span><h3>{esc(n["titulo"])}</h3><p>{esc(n.get("resumen", ""))}</p><b>Leer más →</b></a>')
    for tag, t, txt in [("Experiencia", "Historias de viaje", "Lo que viví en cada lugar: recorridos, encuentros y sabores."),
                        ("Tip", "Consejos prácticos", "Qué llevar, cómo moverte, cuándo ir y cómo ahorrar."),
                        ("Reseña", "Lugares que recomiendo", "Hoteles, restaurantes y experiencias que valen la pena.")][:3 - len(cards)]:
        cards.append(f'<div class="reco reco-pronto"><span class="reco-tag">{tag}</span><h3>{t}</h3><p>{txt}</p><b>Próximamente</b></div>')
    return f'''      <section class="v-section" aria-labelledby="h-reco">
        <div class="v-head"><div><h2 id="h-reco">Mis recomendaciones y tips</h2><p>Experiencias, consejos y lugares que recomiendo para inspirar tu próximo destino.</p></div>
          <a class="v-more" href="{rel(d, 'blog/opinion/')}">Ver columnas →</a></div>
        <div class="reco-grid">{"".join(cards)}</div>
      </section>'''


def tienda_viajeros(d):
    items = [("Mochilas y bolsos", '<path d="M7 8V6a5 5 0 0 1 10 0v2"/><rect x="5" y="8" width="14" height="13" rx="3"/><path d="M9 13h6"/>'),
             ("Organizadores de equipaje", '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V4h8v3M3 13h18"/>'),
             ("Adaptadores y tecnología", '<path d="M9 2v6M15 2v6M6 8h12v4a6 6 0 0 1-12 0zM12 18v4"/>'),
             ("Accesorios de viaje", '<circle cx="12" cy="12" r="9"/><path d="m15 9-2 6-4 0 2-6z"/>')]
    its = "".join(f'<div class="tv-item"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ic}</svg><span>{n}</span></div>' for n, ic in items)
    return f'''      <section class="v-section tienda-viajeros" aria-labelledby="h-tv">
        <span class="tv-badge">En construcción</span>
        <h2 id="h-tv">Tienda para viajeros</h2>
        <p>Estamos armando una selección de productos para tu próxima aventura.</p>
        <div class="tv-items">{its}</div>
        <a class="tv-cta" href="{rel(d, 'oportunidades-globales/buscar/')}">¿Tenés productos para viajeros? Escribinos →</a>
      </section>'''


def destacados():
    if DESTACADOS:
        por_slug = {x["slug"]: x for x in DESTINOS}
        return [por_slug[s] for s in DESTACADOS if s in por_slug][:8]
    return DESTINOS[:8]


def pagina_todos():
    d = 2
    tipos_pres = {t for x in DESTINOS for t in x["tipos"]}
    main = f'''    <div class="wrap">
{crumbs(d, [("Viajes", "viajes/"), ("Todos los destinos", None)])}
      <section class="v-section" id="destinos" aria-labelledby="h-dest" style="margin-top:18px">
        <div class="v-head"><div><h1 id="h-dest" style="font-size:clamp(2rem,4.4vw,2.9rem)">Todos los destinos</h1><p>Buscá por nombre o filtrá por tipo de viaje.</p></div></div>
        <form class="v-search v-search-sm" role="search" onsubmit="return false">
          <label><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="v-q" type="search" placeholder="¿Adónde querés ir?" aria-label="Buscar destino"></label>
        </form>
        <div class="v-tools">{chips(tipos_pres)}<span class="v-count" id="v-count"></span></div>
        <div class="dest-grid dest-grid-4" id="dest-grid">
{chr(10).join(dest_card(x, d) for x in DESTINOS)}
        </div>
      </section>
    </div>'''
    return page(d, "Todos los destinos | Umarti Viajes", "Todas las guías de destinos de Umarti Viajes: buscá por nombre o filtrá por tipo de viaje.", main)


def portada():
    d = 1
    paises = [(k, v, [x for x in DESTINOS if x["pais"] == k]) for k, v in PAISES.items()]
    cont_cards = []
    for ck, cn, cb in CONTINENTES:
        ps = [(k, v, ds) for k, v, ds in paises if v.get("continente") == ck and ds]
        if ps:
            links = "".join(f'<a href="{rel(d, p_pais(k))}"><b>{esc(v["nombre"])}</b><small>{len(ds)} destino{"" if len(ds) == 1 else "s"}</small></a>' for k, v, ds in ps)
            n = sum(len(ds) for _, _, ds in ps)
            cont_cards.append(f'''<div class="cont-card on"><div class="cc-top"><h3>{cn}</h3><span>{n} destino{"" if n == 1 else "s"}</span></div><p>{esc(cb)}</p><div class="cc-paises">{links}</div></div>''')
        else:
            cont_cards.append(f'''<div class="cont-card"><div class="cc-top"><h3>{cn}</h3><span>Próximamente</span></div><p>{esc(cb)}</p></div>''')
    tipos_pres = {t for x in DESTINOS for t in x["tipos"]}
    origenes = []
    for x in DESTINOS:
        for o in x["origen"][:1]:
            origenes.append(f'<div class="origin"><small>{esc(x["nombre"])}</small><strong>{esc(o["producto"])}</strong><span>{esc(o["texto"])}</span><em>Próximamente</em></div>')
    main = f'''    <div class="wrap">
{crumbs(d, [("Viajes", None)])}
      <section class="v-hero v-hero-foto">
        <img class="vh-foto" src="{rel(d, 'assets/img/viajes/playa-mate-atardecer.jpg')}" alt="">
        <div class="vh-txt">
          <span class="eyebrow">Umarti Viajes</span>
          <h1>El mundo, <em>con buen sabor</em></h1>
          <p class="lead">Guías de destinos para planificar tu próximo viaje: cuándo ir, cómo llegar, qué hacer, qué probar y qué traerte de recuerdo.</p>
          <form class="v-search" role="search" action="{rel(d, 'viajes/destinos/')}" method="get">
            <label><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input name="q" type="search" placeholder="¿Adónde querés ir?" aria-label="Buscar destino"></label>
            <button type="submit">Explorar destinos</button>
          </form>
        </div>
      </section>

      <section class="v-section" aria-labelledby="h-cont">
        <div class="v-head"><div><h2 id="h-cont">Elegí tu continente</h2><p>Empezamos por América y vamos sumando destinos de todo el mundo.</p></div></div>
        <div class="cont-grid">{"".join(cont_cards)}</div>
      </section>

      <section class="v-section" id="destinos" aria-labelledby="h-dest">
        <div class="v-head">
          <div><h2 id="h-dest">Destinos destacados</h2><p>Cada guía reúne lo esencial para planificar: la mejor época, cómo llegar, los imperdibles y los sabores del lugar.</p></div>
          <a class="v-more" href="{rel(d, 'viajes/destinos/')}">Ver todos los destinos →</a>
        </div>
        <div class="v-tools">{chips({t for x in destacados() for t in x["tipos"]})}<span class="v-count" id="v-count"></span></div>
        <div class="dest-grid dest-grid-4" id="dest-grid">
{chr(10).join(dest_card(x, d) for x in destacados())}
        </div>
        <div class="v-more-row"><a class="v-more-btn" href="{rel(d, 'viajes/destinos/')}">Ver todos los destinos</a></div>
      </section>
{aviso(d, 1)}
    </div>

    <section class="mesa-band" aria-labelledby="h-mesa">
      <div class="wrap">
        <span class="eyebrow">Del destino a tu mesa <span class="mesa-pronto">Próximamente</span></span>
        <h2 id="h-mesa">Cada lugar tiene un sabor para llevarte</h2>
        <p>Viajar a Mendoza es conocer el Malbec; recorrer Misiones es entender la yerba mate. Por eso cada guía se conecta con los productos de ese lugar en la Tienda y con las notas del Blog.</p>
        <div class="origin-grid">{"".join(origenes)}</div>
      </div>
    </section>

    <div class="wrap">
{organiza(d)}
{aviso(d, 2)}
{recomendaciones(d)}
{tienda_viajeros(d)}
{aviso(d, 3)}
    </div>'''
    return page(d, "Viajes: guías de destinos para planificar tu viaje | Umarti Origen",
                "Guías de viaje por continente y país: cuándo ir, cómo llegar, qué hacer, qué probar y qué traerte de recuerdo.", main)


def pais_fotos(d, v):
    """Foto de la presentación del país (opcional), esfumada hacia el texto."""
    fs = v.get("fotos") or []
    return "".join(f'        <img class="ph-foto ph-foto-2" src="{rel(d, f[0])}" alt="{esc(f[1])}"' + (f' style="object-position:{f[2]}"' if len(f) > 2 else "") + '>\n' for f in fs[:1])


def pagina_pais(k):
    d = 2
    v = PAISES[k]
    ds = [x for x in DESTINOS if x["pais"] == k]
    tipos_pres = {t for x in ds for t in x["tipos"]}
    filas = "".join(f'<tr><td><a href="{rel(d, p_dest(x))}">{esc(x["nombre"])}</a></td><td>{esc(x["mejor_epoca"])}</td><td>{esc(x["clima"])}</td><td>{esc(x["dias"])}</td></tr>' for x in ds)
    main = f'''    <div class="wrap">
{crumbs(d, [("Viajes", "viajes/"), (v['nombre'], None)])}
      <div class="{'pais-hero' if v.get('fotos') else 'blog-head'}">
{pais_fotos(d, v)}
        <div class="ph-txt">
        <span class="eyebrow" style="color:var(--green)">Destinos</span>
        <h1>Viajar por {esc(v['nombre'])}</h1>
        <p>{esc(v['lead'])}</p>
        <div class="facts-row">
          <div class="fact"><small>Destinos</small><b>{len(ds)} guías</b></div>
          <div class="fact"><small>Moneda</small><b>{esc(v['moneda'])}</b></div>
          <div class="fact"><small>Idioma</small><b>{esc(v['idioma'])}</b></div>
        </div>
        <div class="ph-salida">
          <a class="ph-volver" href="{rel(d, 'viajes/')}">← Ver otros destinos</a>
          {"".join(f'<a class="ph-pais" href="{rel(d, p_pais(o))}">Ir a {esc(PAISES[o]["nombre"])}</a>' for o in PAISES if o != k)}
        </div>
        </div>
      </div>

      <section class="v-section" aria-labelledby="h-d">
        <div class="v-head"><div><h2 id="h-d">Destinos de {esc(v['nombre'])}</h2></div></div>
        <div class="v-tools">{chips(tipos_pres)}<span class="v-count" id="v-count"></span></div>
        <div class="dest-grid" id="dest-grid">
{chr(10).join(dest_card(x, d) for x in ds)}
        </div>
      </section>

      <section aria-labelledby="h-when">
        <div class="v-head"><div><h2 id="h-when">¿Cuándo conviene ir?</h2><p>La mejor época para cada destino de {esc(v['nombre'])}, de un vistazo.</p></div></div>
        <div class="when-table"><table><thead><tr><th>Destino</th><th>Mejor época</th><th>Clima</th><th>Días ideales</th></tr></thead><tbody>{filas}</tbody></table></div>
      </section>

      <div class="cta-band">
        <div><h2>¿Listo para viajar a {esc(v['nombre'])}?</h2><p>Reservá vuelos, hoteles, autos y paquetes con nuestros aliados.</p></div>
        <a class="btn-green" href="{rel(d, 'viajes/')}#organiza">Organizá tu viaje</a>
      </div>
    </div>'''
    ld = {"@context": "https://schema.org", "@type": "Country", "name": v["nombre"], "description": v["lead"]}
    return page(d, f"Viajar por {v['nombre']}: destinos y cuándo ir | Umarti Viajes",
                f"Guías de viaje de {v['nombre']}: {', '.join(x['nombre'] for x in ds)}. Mejor época, clima y días recomendados para cada destino.", main, ld)


def faqs(x):
    return [
        (f"¿Cuál es la mejor época para viajar a {x['nombre']}?", f"{x['mejor_epoca']}. {x['clima']}"),
        (f"¿Cuántos días se necesitan para conocer {x['nombre']}?", f"Recomendamos {x['dias']} para recorrer lo esencial sin apuro."),
        (f"¿Cómo llegar a {x['nombre']}?", x["como_llegar"]),
        (f"¿Cómo moverse en {x['nombre']}?", x["como_moverse"]),
    ]


def pagina_destino(x):
    d = 3
    v = PAISES[x["pais"]]
    secciones = [("por-que-ir", "Por qué ir"), ("cuando-ir", "Cuándo ir"), ("como-llegar", "Cómo llegar y moverse"),
                 ("que-hacer", "Qué hacer"), ("que-probar", "Qué probar"), ("consejos", "Consejos"), ("preguntas", "Preguntas frecuentes")]
    toc = '<div class="box toc"><h2>En esta guía</h2><ol>' + "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in secciones) + "</ol></div>"
    items = []
    for o in x["origen"]:
        links = ""
        if o.get("nota") and o["nota"] in NOTAS:
            links += f'<a href="{rel(d, "blog/" + o["nota"] + "/")}">Leer: {esc(NOTAS[o["nota"]]["titulo"])}</a>'
        links += f'<a href="{rel(d, "argentina/tienda/" + slug(o["categoria"]) + "/")}">Ver {esc(o["categoria"])} en la Tienda</a>'
        items.append(f'<div class="origin-item"><strong>{esc(o["producto"])}</strong><p>{esc(o["texto"])}</p>{links}</div>')
    origen_box = f'<div class="box origin-box"><h2>De {esc(x["nombre"])} a tu mesa</h2>{"".join(items)}</div>'
    plan_box = f'''<div class="box plan-box"><strong>Organizá tu viaje a {esc(x['nombre'])}</strong><p>Vuelos, hoteles, autos y paquetes con nuestros aliados.</p><a class="btn-green" href="{rel(d, 'viajes/')}#organiza">Ver opciones</a></div>'''
    musts = "".join(f'<div class="must"><strong>{esc(n)}</strong><span>{esc(t)}</span></div>' for n, t in x["imperdibles"])
    sabores = "".join(f"<li>{esc(s)}</li>" for s in x["sabores"])
    consejos = "".join(f"<li>{esc(c)}</li>" for c in x["consejos"])
    fq = faqs(x)
    faq_html = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in fq)
    intro = "".join(f"<p>{esc(p)}</p>" for p in x["intro"])
    tipos = "".join(f'<span class="tipo">{esc(t)}</span>' for t in x["tipos"])
    otros = [o for o in DESTINOS if o is not x and o["pais"] == x["pais"]][:3]
    if len(otros) < 3:
        otros += [o for o in DESTINOS if o is not x and o not in otros][:3 - len(otros)]
    main = f'''    <div class="wrap">
{crumbs(d, [("Viajes", "viajes/"), (v['nombre'], p_pais(x['pais'])), (x['nombre'], None)])}
      <section class="d-hero">
        <div>
          <a class="chip-pais" href="{rel(d, p_pais(x['pais']))}">{esc(x['region'])}, {esc(v['nombre'])}</a>
          <h1>{esc(x['nombre'])}</h1>
          <p class="lead">{esc(x['resumen'])}</p>
          <div class="tipos">{tipos}</div>
          <div class="d-facts">
            <div><small>Mejor época</small><b>{esc(x['mejor_epoca'].split(';')[0])}</b></div>
            <div><small>Días ideales</small><b>{esc(x['dias'])}</b></div>
            <div><small>Presupuesto</small><b>{esc(x['presupuesto'])}</b></div>
          </div>
        </div>
        {vcover(x['colores'], x['paisaje'])}
      </section>

      <div class="post-layout">
        <article class="prose">
          <h2 id="por-que-ir">Por qué ir a {esc(x['nombre'])}</h2>
          {intro}
          <h2 id="cuando-ir">Cuándo ir</h2>
          <p><strong>Mejor época:</strong> {esc(x['mejor_epoca'])}.</p>
          <p><strong>Clima:</strong> {esc(x['clima'])}</p>
          <h2 id="como-llegar">Cómo llegar y moverse</h2>
          <p>{esc(x['como_llegar'])}</p>
          <p>{esc(x['como_moverse'])}</p>
          <h2 id="que-hacer">Qué hacer en {esc(x['nombre'])}</h2>
          <div class="must-grid">{musts}</div>
          <h2 id="que-probar">Qué probar</h2>
          <ul>{sabores}</ul>
          <h2 id="consejos">Consejos para tu viaje</h2>
          <ul>{consejos}</ul>
          <h2 id="preguntas">Preguntas frecuentes</h2>
          <div class="faq-list">{faq_html}</div>
        </article>
        <aside class="post-aside">
          <div class="aside-sticky">
          {toc}
          {origen_box}
          {plan_box}
          </div>
        </aside>
      </div>
    </div>
    <section class="related">
      <div class="wrap">
        <h2>Otros destinos</h2>
        <div class="dest-grid">
{chr(10).join(dest_card(o, d) for o in otros)}
        </div>
      </div>
    </section>'''
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "TouristDestination", "name": x["nombre"], "description": x["resumen"],
         "touristType": x["tipos"], "containedInPlace": {"@type": "Country", "name": v["nombre"]},
         "includesAttraction": [{"@type": "TouristAttraction", "name": n, "description": t} for n, t in x["imperdibles"]]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}]}
    if SITIO:
        ld["@graph"][0]["url"] = f"{SITIO}/{p_dest(x)}"
    return page(d, f"Guía de viaje de {x['nombre']}: qué hacer, cuándo ir y qué probar | Umarti Viajes",
                f"{x['resumen']} Mejor época, cómo llegar, imperdibles y consejos para viajar a {x['nombre']}.", main, ld)


# ---------- Guías cargadas desde el Panel ----------
import re as _re


def _inline(t):
    t = esc(t)
    t = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = _re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = _re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def md(texto):
    """Formato simple del Panel: párrafos separados por una línea en blanco, '- ' para listas,
    '### ' para subtítulos, **negrita**, *cursiva* y [texto](https://link)."""
    out, lista, parrafo = [], [], []

    def cerrar():
        if lista:
            out.append("<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in lista) + "</ul>")
            lista.clear()

    def cerrar_p():
        if parrafo:
            out.append("<p>" + "<br>".join(_inline(l) for l in parrafo) + "</p>")
            parrafo.clear()
    for linea in (texto or "").replace("\r", "").split("\n"):
        l = linea.strip()
        if not l:
            cerrar_p(); cerrar(); continue
        if l.startswith(("- ", "* ", "• ")):
            cerrar_p(); lista.append(l[2:].strip()); continue
        if l.startswith("#"):
            cerrar_p(); cerrar(); out.append(f"<h3>{_inline(l.lstrip('#').strip())}</h3>"); continue
        cerrar(); parrafo.append(l)
    cerrar_p(); cerrar()
    return "\n".join(out)


_LUGAR = r"^\*\*(.+?)\*\*\s*[:—-]\s*(.+)$"


def md_lugares(texto):
    """'Qué hacer': si todo es una lista de '- **Lugar**: descripción', se muestra como tarjetas."""
    lineas = [l.strip() for l in (texto or "").split("\n") if l.strip()]
    if lineas and all(l.startswith("- ") and _re.match(_LUGAR, l[2:]) for l in lineas):
        cards = "".join(f'<div class="must"><strong>{esc(m.group(1))}</strong><span>{_inline(m.group(2))}</span></div>'
                        for m in (_re.match(_LUGAR, l[2:]) for l in lineas))
        return f'<div class="must-grid">{cards}</div>'
    return md(texto)


def video_html(url):
    u = (url or "").strip()
    m = _re.search(r"(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)([\w-]{6,})", u)
    if m:
        return f'<div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/{m.group(1)}" title="Video" loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>'
    m = _re.search(r"vimeo\.com/(\d+)", u)
    if m:
        return f'<div class="vid"><iframe src="https://player.vimeo.com/video/{m.group(1)}" title="Video" loading="lazy" allow="fullscreen; picture-in-picture" allowfullscreen></iframe></div>'
    if u:
        return f'<div class="vid"><video src="{esc(u)}" controls preload="metadata" playsinline></video></div>'
    return ""


def detalle_html(bloques):
    out = []
    for b in bloques or []:
        t = b.get("tipo")
        cap = f"<figcaption>{esc(b['pie'])}</figcaption>" if b.get("pie") else ""
        if t == "texto" and (b.get("texto") or b.get("titulo")):
            out.append((f"<h3>{esc(b['titulo'])}</h3>" if b.get("titulo") else "") + md(b.get("texto", "")))
        elif t == "foto" and b.get("url"):
            out.append(f'<figure class="d-fig"><img src="{esc(b["url"])}" alt="{esc(b.get("pie", ""))}" loading="lazy">{cap}</figure>')
        elif t == "video" and b.get("url"):
            out.append(f'<figure class="d-fig">{video_html(b["url"])}{cap}</figure>')
    return "\n".join(out)


def _catalogo():
    try:
        return json.load(open(os.path.join(AQUI, "tienda", "catalogo.json"), encoding="utf-8")).get("productos", [])
    except FileNotFoundError:
        return []


def _pesos(v):
    return format(int(v), ",").replace(",", ".")


def pagina_destino_panel(x):
    d = 3
    v = PAISES[x["pais"]]
    f = x["panel"]
    n = x["nombre"]
    secciones = [("por-que-ir", f"Por qué ir a {n}", "Por qué ir", "por_que", md),
                 ("cuando-ir", "Cuándo ir", "Cuándo ir", "cuando_ir", md),
                 ("que-comer", "Qué comer", "Qué comer", "que_comer", md),
                 ("donde-alojarse", "Dónde alojarse", "Dónde alojarse", "donde_alojarse", md),
                 ("como-llegar", "Cómo llegar", "Cómo llegar", "como_llegar", md),
                 ("como-moverse", "Cómo moverse", "Cómo moverse", "como_moverse", md),
                 ("que-hacer", f"Qué hacer en {n}", "Qué hacer", "que_hacer", md_lugares),
                 ("consejos", "Consejos para tu viaje", "Consejos", "consejos", md)]
    cuerpo, toc = [], []
    base = rel(d, p_dest(x))
    enlaces = {"por_que": (f"{base}en-detalle/", f"Conocé {n} en detalle: fotos, videos e historias"),
               "que_comer": (f"{base}donde-comer/", f"Dónde comer en {n}: restaurantes y cupones"),
               "donde_alojarse": (f"{base}donde-alojarse/", f"Dónde alojarse en {n}: hoteles, cabañas y cupones")}
    for ancla, titulo, corto, campo, fn in secciones:
        extra = clima_html(f.get("clima"), n) if campo == "cuando_ir" else ""
        if campo == "por_que":
            u, _ = enlaces[campo]
            extra += (f'<a class="d-destacado" href="{u}"><span class="dd-ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8a2 2 0 0 1 2-2h2l2-2h6l2 2h2a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><circle cx="12" cy="13" r="4"/></svg></span>'
                      f'<span class="dd-txt"><b>Conocé {esc(n)} en detalle</b><small>Fotos, videos e historias del destino</small></span><em>Ver →</em></a>')
        elif campo in enlaces:
            u, t = enlaces[campo]
            extra += f'<a class="d-mas" href="{u}">{esc(t)} →</a>'
        if campo == "como_llegar":
            extra += f'<a class="d-mas" href="{rel(d, p_serv("vuelos"))}?destino={x["slug"]}">Buscar vuelos a {esc(n)} →</a>'
        if campo == "consejos":
            cuerpo.append(f'<div class="ad-fila">{aviso_guia(d, 2)}</div>')
        if (f.get(campo) or "").strip() or extra:
            cuerpo.append(f'<h2 id="{ancla}">{esc(titulo)}</h2>\n{fn(f.get(campo) or "")}{extra}')
            toc.append((ancla, corto))
        if campo == "por_que":
            dp = datos_practicos(x, d)
            if dp:
                cuerpo.append(dp)
                toc.append(("datos-practicos", "Datos prácticos"))
        if campo == "cuando_ir" and (f.get("requisitos") or "").strip():
            fuente = (f.get("requisitos_fuente") or "").strip()
            fh = ""
            if fuente:
                fh = (f'<p class="d-fuente">Fuente: <a href="{esc(fuente)}" target="_blank" rel="noopener">{esc(fuente.split("//")[-1].split("/")[0])}</a>. Verificá siempre antes de viajar: los requisitos pueden cambiar.</p>'
                      if fuente.startswith("http") else f'<p class="d-fuente">Fuente: {esc(fuente)}. Verificá siempre antes de viajar: los requisitos pueden cambiar.</p>')
            cuerpo.append(f'<section class="d-requisitos" id="requisitos"><h2>Requisitos para viajar a {esc(n)}</h2>{md(f["requisitos"])}{fh}</section>')
            toc.append(("requisitos", "Requisitos para viajar"))
    org = organiza_destino(x, d)
    if org:
        cuerpo.append(org)
        toc.append(("organiza", "Organizá tu viaje"))
    prods = [p for p in _catalogo() if p.get("codigo") in (f.get("productos") or [])]
    cats = f.get("categorias_tienda") or []
    if prods or cats:
        cards = "".join(
            f'<a class="d-prod" href="{rel(d, "argentina/tienda/" + p["slug"] + "/")}">'
            + (f'<img src="{esc(p["fotos"][0])}" alt="" loading="lazy">' if p.get("fotos") else '<span class="d-prod-ph"></span>')
            + f'<span><b>{esc(p["nombre"])}</b>'
            + (f'<small>$ {_pesos(p["precio_ars"])} ARS</small>' if p.get("precio_ars") and p.get("tienda_ar") else "")
            + "</span></a>" for p in prods)
        links = ""
        for c in cats:
            cat, _, sub = c.partition(" › ")
            url = rel(d, "argentina/tienda/" + slug(cat) + "/") + (f"?sub={quote(sub)}" if sub else "")
            links += f'<a class="d-cat" href="{url}">{esc(sub or cat)} →</a>'
        cuerpo.append(f'<section class="d-tienda" id="en-la-tienda"><h2>Llevate {esc(n)} a casa</h2><p>Productos con origen para disfrutar antes o después del viaje.</p>'
                      + (f'<div class="d-prods">{cards}</div>' if cards else "") + (f'<div class="d-cats">{links}</div>' if links else "") + "</section>")
        toc.append(("en-la-tienda", "En la Tienda"))
    fq = [(q.get("q", ""), q.get("a", "")) for q in (f.get("faqs") or []) if q.get("q")]
    if fq:
        cuerpo.append('<h2 id="preguntas">Preguntas frecuentes</h2><div class="faq-list">'
                      + "".join(f"<details><summary>{esc(q)}</summary>{md(a)}</details>" for q, a in fq) + "</div>")
        toc.append(("preguntas", "Preguntas frecuentes"))
    toc_html = '<div class="box toc"><h2>En esta guía</h2><ol>' + "".join(f'<li><a href="#{a}">{esc(t)}</a></li>' for a, t in toc) + "</ol></div>"
    notas = [NOTAS[s] for s in (f.get("notas") or []) if s in NOTAS]
    notas_box = ""
    if notas:
        notas_box = '<div class="box d-notas"><h2>Para leer antes de viajar</h2>' + "".join(
            f'<a href="{rel(d, "blog/" + nt["slug"] + "/")}">{esc(nt["titulo"])}</a>' for nt in notas) + "</div>"
    plan_box = (f'<div class="box plan-box"><strong>Organizá tu viaje a {esc(n)}</strong><p>Vuelos, hoteles, autos y paquetes con nuestros aliados.</p>'
                f'<a class="btn-green" href="{rel(d, "viajes/")}#organiza">Ver opciones</a></div>')
    tipos = "".join(f'<span class="tipo">{esc(t)}</span>' for t in x["tipos"])
    hechos = [(k, val) for k, val in (("Mejor época", (x.get("mejor_epoca") or "").split(";")[0]), ("Días ideales", x.get("dias")),
                                      ("Presupuesto", x.get("presupuesto"))) if val]
    facts = "".join(f"<div><small>{k}</small><b>{esc(val)}</b></div>" for k, val in hechos)
    portada = (f'<figure class="d-foto"><img src="{esc(f["foto"])}" alt="{esc(n)}" style="object-position:{esc(f.get("foto_pos") or "center")}"></figure>'
               if f.get("foto") else vcover(x["colores"], x["paisaje"]))
    otros = [o for o in DESTINOS if o is not x and o["pais"] == x["pais"]][:3]
    if len(otros) < 3:
        otros += [o for o in DESTINOS if o is not x and o not in otros][:3 - len(otros)]
    region = f"{esc(x['region'])}, {esc(v['nombre'])}" if x["region"] and x["region"] != n else esc(v["nombre"])
    main = "\n".join([
        '    <div class="wrap">',
        crumbs(d, [("Viajes", "viajes/"), (v["nombre"], p_pais(x["pais"])), (n, None)]),
        '      <section class="d-hero">',
        f'        <div><a class="chip-pais" href="{rel(d, p_pais(x["pais"]))}">{region}</a>',
        f'          <h1>{esc(n)}</h1><p class="lead">{esc(x["resumen"])}</p>',
        f'          <div class="tipos">{tipos}</div></div>',
        f'        {portada}',
        '      </section>',
        f'      <div class="ad-fila ad-guia1">{aviso_guia(d, 1)}</div>',
        '      <div class="post-layout">',
        '        <article class="prose">', "\n".join(cuerpo), '        </article>',
        f'        <aside class="post-aside"><div class="aside-sticky">{toc_html}{notas_box}{plan_box}</div></aside>',
        '      </div>',
        '    </div>',
        '    <section class="related"><div class="wrap"><h2>Otros destinos</h2><div class="dest-grid">',
        "\n".join(dest_card(o, d) for o in otros),
        '    </div></div></section>',
        f'    <div class="wrap"><div class="ad-fila ad-guia3">{aviso_guia(d, 3)}</div></div>'])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "TouristDestination", "name": n, "description": x["resumen"], "touristType": x["tipos"],
         "containedInPlace": {"@type": "Country", "name": v["nombre"]}}]}
    if f.get("foto"):
        ld["@graph"][0]["image"] = f["foto"]
    if fq:
        ld["@graph"].append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]})
    if SITIO:
        ld["@graph"][0]["url"] = f"{SITIO}/{p_dest(x)}"
    return page(d, f"Guía de viaje de {n}: qué hacer, cuándo ir y qué comer | Umarti Viajes",
                f"{x['resumen']} Cuándo ir, dónde alojarse, qué hacer y consejos para viajar a {n}.", main, ld)



# ---------- Organizá tu viaje (servicios y ofertas cargados desde el Panel) ----------
CLAVES_SERV = {"Alojamiento": "alojamiento", "Vuelos": "vuelos", "Seguro médico": "seguro", "Autos": "autos",
               "Excursiones": "excursiones", "Paquetes": "paquetes", "Traslados y transporte": "traslados"}
INTRO_SERV = {
    "alojamiento": ("Dónde dormir", "Hoteles, cabañas y departamentos. Reservá con nuestros aliados o directo con alojamientos de cada destino."),
    "vuelos": ("Volar", "Buscá tu vuelo, conocé lo que conviene saber antes de volar y llegá conectado."),
    "seguro": ("Viajar tranquilo", "Seguro médico y asistencia al viajero para cubrir imprevistos de salud, equipaje y más. En algunos países, como Argentina, es obligatorio."),
    "autos": ("Moverte a tu ritmo", "Alquilá un auto con nuestros aliados o con empresas locales de cada destino."),
    "excursiones": ("Qué hacer", "Excursiones, visitas guiadas y actividades en cada destino."),
    "paquetes": ("Todo en uno", "Paquetes con vuelo y alojamiento para resolver el viaje de una vez."),
    "traslados": ("Del aeropuerto al hotel", "Traslados y transporte en el destino, con aliados y empresas locales."),
}
PUBLICA_SERV = {"alojamiento": "¿Tenés un hotel, una cabaña o un departamento?", "autos": "¿Tenés una empresa de alquiler de autos?",
                "excursiones": "¿Organizás excursiones o actividades?", "traslados": "¿Ofrecés traslados o transporte?"}

try:
    ORG = json.load(open(os.path.join(AQUI, "viajes", "organiza_panel.json"), encoding="utf-8"))
except FileNotFoundError:
    ORG = {"servicios": [], "ofertas": []}
SERV_CONF = {s["clave"]: s for s in ORG.get("servicios", [])}


def p_serv(k):
    return f"viajes/organiza/{k}/"


def ofertas_de(k, destino=None):
    xs = [o for o in ORG.get("ofertas", []) if o.get("servicio") == k]
    if destino:
        xs = [o for o in xs if not o.get("destinos") or destino in o["destinos"]]
    return xs


def serv_abierto(k):
    return bool(ofertas_de(k)) or bool(SERV_CONF.get(k, {}).get("activo"))


def link_aliado(k, defecto):
    a = next((o for o in ofertas_de(k) if o.get("tipo") == "aliado" and o.get("link")), None)
    return a["link"] if a else defecto


def _cupon(o):
    if not (o.get("cupon_codigo") or o.get("cupon_texto")):
        return ""
    cod = f'<button type="button" class="of-code" data-copiar="{esc(o["cupon_codigo"])}" title="Copiar código">{esc(o["cupon_codigo"])}</button>' if o.get("cupon_codigo") else ""
    return f'<div class="of-cupon"><span>{esc(o.get("cupon_texto") or "Cupón de descuento")}</span>{cod}</div>'


def oferta_card(o, d):
    nombres = {x["slug"]: x["nombre"] for x in DESTINOS}
    dest = " · ".join(nombres.get(s, s) for s in o.get("destinos") or []) or "Todos los destinos"
    if o.get("tipo") == "aliado":
        return (f'<div class="of-aliado" data-destinos="{esc("|".join(o.get("destinos") or []))}">'
                f'<div><span class="of-tag">{esc(o.get("etiqueta") or "Aliado")}</span><h3>{esc(o["nombre"])}</h3><p>{esc(o.get("descripcion", ""))}</p>{_cupon(o)}</div>'
                f'<a class="btn-green" href="{esc(o.get("link") or "#")}" target="_blank" rel="sponsored noopener">Buscar en {esc(o["nombre"])}</a></div>')
    foto = f'<img src="{esc(o["foto"])}" alt="" loading="lazy">' if o.get("foto") else '<span class="of-ph"></span>'
    contactos = ""
    if o.get("link"):
        contactos += f'<a class="btn-green sm" href="{esc(o["link"])}" target="_blank" rel="noopener">Ver y reservar</a>'
    if o.get("whatsapp"):
        num = "".join(ch for ch in o["whatsapp"] if ch.isdigit())
        contactos += f'<a class="of-wa" href="https://wa.me/{num}" target="_blank" rel="noopener">WhatsApp</a>'
    if o.get("email"):
        contactos += f'<a class="of-mail" href="mailto:{esc(o["email"])}">Correo</a>'
    return (f'<article class="of-card" data-destinos="{esc("|".join(o.get("destinos") or []))}">{foto}<div class="of-body">'
            f'<span class="of-tag">{esc(o.get("etiqueta") or "")}</span><h3>{esc(o["nombre"])}</h3>'
            f'<small class="of-donde">{esc(o.get("ubicacion") or dest)}</small><p>{esc(o.get("descripcion", ""))}</p>'
            + (f'<b class="of-precio">Desde {esc(o["precio_desde"])}</b>' if o.get("precio_desde") else "")
            + _cupon(o) + f'<div class="of-acts">{contactos}</div></div></article>')


def _cupones_viaje():
    try:
        cs = json.load(open(os.path.join(AQUI, "cupones", "cupones.json"), encoding="utf-8"))
    except FileNotFoundError:
        return []
    return [c for c in cs if c.get("categoria") == "Viajes" and c.get("estado", "Publicado") in ("Publicado", "Ejemplo")]


def pagina_servicio(nombre, icono):
    k = CLAVES_SERV[nombre]
    d = 3
    conf = SERV_CONF.get(k, {})
    eyebrow, intro = INTRO_SERV[k]
    xs = ofertas_de(k)
    aliados = [o for o in xs if o.get("tipo") == "aliado"]
    propios = [o for o in xs if o.get("tipo") != "aliado"]
    usados = sorted({s for o in xs for s in (o.get("destinos") or [])}, key=lambda s: next((x["nombre"] for x in DESTINOS if x["slug"] == s), s))
    nombres = {x["slug"]: x["nombre"] for x in DESTINOS}
    filtro = ""
    if usados:
        filtro = ('<div class="chip-row of-filtro" role="group" aria-label="Filtrar por destino"><span>Destino:</span><button type="button" data-dest="" aria-pressed="true">Todos</button>'
                  + "".join(f'<button type="button" data-dest="{esc(s)}" aria-pressed="false">{esc(nombres.get(s, s))}</button>' for s in usados) + "</div>")
    cont = md(conf.get("contenido", "")) if (conf.get("contenido") or "").strip() else ""
    cups = _cupones_viaje()
    cup_html = ""
    if cups:
        cup_html = ('<section class="v-section of-sec"><div class="v-head"><div><h2>Cupones de viaje</h2><p>Descuentos de comercios y aliados para tu viaje.</p></div>'
                    f'<a class="v-more" href="{rel(d, "cupones/viajes/")}">Ver todos los cupones →</a></div><div class="of-cups">'
                    + "".join(f'<a class="of-cup" href="{rel(d, "cupones/viajes/")}#{esc(c["codigo"].lower())}"><b>{esc(c.get("descuento", ""))}</b><span>{esc(c["titulo"])}</span><small>{esc(c.get("comercio", ""))}</small></a>' for c in cups[:4])
                    + "</div></section>")
    vacio = "" if xs or cont else '<div class="of-vacio"><b>Próximamente</b><p>Estamos sumando aliados y opciones para este servicio.</p></div>'
    publica = ""
    if k in PUBLICA_SERV:
        publica = (f'<a class="of-publica" href="{rel(d, "mi-empresa/")}?publicar=viajes"><span><b>{PUBLICA_SERV[k]}</b>'
                   '<small>Publicalo en Umarti Viajes y llegá a quienes están planificando su viaje.</small></span><em>Publicar →</em></a>')
    otros = "".join(f'<a href="{rel(d, p_serv(CLAVES_SERV[n]))}"{" aria-current=\"page\"" if n == nombre else ""}>{n}</a>' for n, _ in SERVICIOS)
    main = f'''    <div class="wrap">
{crumbs(d, [("Viajes", "viajes/"), ("Organizá tu viaje", "viajes/#organiza"), (nombre, None)])}
      <nav class="of-nav" aria-label="Servicios">{otros}</nav>
      <section class="of-hero">
        <span class="of-ico"><svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{icono}</svg></span>
        <div><span class="eyebrow">{eyebrow}</span><h1>{esc(nombre)}</h1><p>{esc(conf.get("bajada") or intro)}</p></div>
      </section>
      {filtro}
      {vacio}
      {'<section class="of-sec"><div class="of-aliados">' + "".join(oferta_card(o, d) for o in aliados) + "</div></section>" if aliados else ""}
      {'<section class="of-sec"><h2>Opciones en cada destino</h2><div class="of-grid">' + "".join(oferta_card(o, d) for o in propios) + "</div></section>" if propios else ""}
      {'<section class="of-sec prose of-info">' + cont + "</section>" if cont else ""}
      {cup_html}
      {publica}
      <div class="ad-fila">{aviso(d, 3)}</div>
    </div>'''
    return page(d, f"{nombre}: organizá tu viaje | Umarti Viajes", f"{intro}", main)


def organiza_destino(x, d):
    """Accesos a Organizá tu viaje desde la guía de un destino."""
    items = []
    for n, ic in SERVICIOS:
        k = CLAVES_SERV[n]
        if k in ("alojamiento", "vuelos"):
            continue
        xs = ofertas_de(k, x["slug"])
        loc = sum(1 for o in xs if o.get("tipo") != "aliado")
        sub = (f"{loc} opción{'' if loc == 1 else 'es'} local{'' if loc == 1 else 'es'}" if loc else "Con nuestros aliados") if xs else "Próximamente"
        items.append(f'<a class="od-item{"" if xs else " pronto"}" href="{rel(d, p_serv(k))}?destino={x["slug"]}"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ic}</svg><span><b>{n}</b><small>{sub}</small></span></a>')
    tz = PAISES.get(x["pais"], {}).get("tz")
    items.append(f'<a class="od-item" href="{rel(d, "recursos/diferencia-horaria/")}{"?a=" + quote(tz) + "&n=" + quote(x["nombre"]) if tz else ""}"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg><span><b>Diferencia horaria</b><small>¿Qué hora es en {esc(x["nombre"])}?</small></span></a>')
    return f'<section class="d-organiza" id="organiza"><h2>Organizá tu viaje a {esc(x["nombre"])}</h2><div class="od-grid">{"".join(items)}</div></section>'


def aviso_guia(depth, n):
    import avisos
    return avisos.espacio(f"guia-{n}", depth, "viajes", "Viajes")


def _utc(tz):
    try:
        import datetime
        from zoneinfo import ZoneInfo
        off = datetime.datetime.now(ZoneInfo(tz)).utcoffset().total_seconds() / 3600
        h = int(off) if off == int(off) else off
        return "UTC" + ("+" if off >= 0 else "−") + str(abs(h)).replace(".5", ":30")
    except Exception:
        return ""


def datos_practicos(x, d):
    """Moneda, corriente, huso horario, unidades y talles, cada uno con su recurso digital."""
    f = x.get("panel") or {}
    v = PAISES.get(x["pais"], {})
    tz = f.get("huso") or v.get("tz") or ""
    import construir_recursos as cr
    pais_corr = v.get("nombre") if any(p == v.get("nombre") for p, *_ in cr.CORRIENTE) else ""
    items = [
        ("Moneda", f.get("moneda") or v.get("moneda") or "", "recursos/conversor-de-monedas/", "Convertir monedas", "moneda"),
        ("Corriente eléctrica", f.get("corriente") or "", "recursos/enchufes-y-corriente/" + (f"?a={quote(pais_corr)}" if pais_corr else ""), "¿Necesito adaptador?", "enchufe"),
        ("Huso horario", (f"{_utc(tz)} · " if tz else "") + (tz.split("/")[-1].replace("_", " ") if tz else ""), "recursos/diferencia-horaria/" + (f"?a={quote(tz)}&n={quote(x['nombre'])}" if tz else ""), "Ver la diferencia horaria", "reloj"),
        ("Unidades de medida", f.get("unidades") or "", "recursos/conversor-de-unidades/", "Convertir unidades", "regla"),
        ("Sistema de talles", f.get("talles") or "", "recursos/tabla-de-talles/", "Ver tabla de talles", "talle"),
    ]
    items = [i for i in items if i[1].strip()]
    if not items:
        return ""
    cards = "".join(f'<a class="dp-item" href="{rel(d, u)}"><span class="dp-ico">{cr.icono(ic, 22)}</span><span class="dp-txt"><small>{t}</small><b>{esc(val)}</b><em>{cta} →</em></span></a>'
                    for t, val, u, cta, ic in items)
    return f'<section class="d-practicos" id="datos-practicos"><h2>Datos prácticos</h2><div class="dp-grid">{cards}</div></section>'


def clima_html(codigo, nombre):
    c = (codigo or "").strip()
    if not c:
        return ""
    if "<iframe" in c or "<script" in c or "<a " in c:
        cuerpo = c
    else:
        m = _re.search(r"(\d+-\d+)", c)
        if not m:
            return ""
        lid = m.group(1)
        cuerpo = (f'<iframe src="https://www.yr.no/en/content/{lid}/card.html" title="Pronóstico del tiempo en {esc(nombre)}" loading="lazy"></iframe>'
                  f'<a class="clima-mas" href="https://www.yr.no/en/forecast/daily-table/{lid}" target="_blank" rel="noopener">Pronóstico de 9 días en yr.no ↗</a>')
    return f'<div class="clima" id="clima"><span class="lbl-clima">El clima hoy en {esc(nombre)}</span>{cuerpo}</div>'


# ---------- Páginas de cada destino: en detalle, dónde comer, dónde alojarse ----------
SUBPAGINAS = [("en-detalle", "En detalle"), ("donde-comer", "Dónde comer"), ("donde-alojarse", "Dónde alojarse")]


def _cupones_destino(x, cats):
    try:
        cs = json.load(open(os.path.join(AQUI, "cupones", "cupones.json"), encoding="utf-8"))
    except FileNotFoundError:
        return []
    return [c for c in cs if c.get("categoria") in cats and c.get("estado", "Publicado") in ("Publicado", "Ejemplo")
            and (c.get("destino") == x["slug"] or (c.get("ciudad") or "").lower() == x["nombre"].lower())]


def pagina_sub(x, clave):
    d = 4
    v = PAISES[x["pais"]]
    f = x.get("panel") or {}
    n = x["nombre"]
    titulo = {"en-detalle": f"Conocé {n} en detalle", "donde-comer": f"Dónde comer en {n}", "donde-alojarse": f"Dónde alojarse en {n}"}[clave]
    bajada = {"en-detalle": f"Fotos, videos e historias para conocer {n} antes de viajar.",
              "donde-comer": f"Restaurantes, bares y cafés recomendados, con cupones de descuento.",
              "donde-alojarse": f"Barrios recomendados, hoteles, cabañas y departamentos, con cupones de descuento."}[clave]
    partes = []
    if clave == "en-detalle":
        det = detalle_html(f.get("detalle"))
        if det:
            partes.append(f'<article class="prose sub-prose">{det}</article>')
        else:
            partes.append(f'<article class="prose sub-prose">{md(f.get("por_que", "")) or "".join(f"<p>{esc(p)}</p>" for p in x.get("intro", []))}</article>')
            partes.append(f'<div class="of-vacio"><b>Próximamente</b><p>Muy pronto vas a encontrar acá más fotos, videos e historias de {esc(n)}.</p></div>')
    else:
        serv = "gastronomia" if clave == "donde-comer" else "alojamiento"
        texto = f.get("que_comer" if clave == "donde-comer" else "donde_alojarse") or ""
        if texto.strip():
            partes.append(f'<article class="prose sub-prose">{md(texto)}</article>')
        xs = ofertas_de(serv, x["slug"])
        aliados = [o for o in xs if o.get("tipo") == "aliado"]
        propios = [o for o in xs if o.get("tipo") != "aliado"]
        if propios:
            partes.append(f'<section class="of-sec"><h2>{"Restaurantes recomendados" if serv == "gastronomia" else "Alojamientos recomendados"}</h2><div class="of-grid">'
                          + "".join(oferta_card(o, d) for o in propios) + "</div></section>")
        if aliados:
            partes.append('<section class="of-sec"><div class="of-aliados">' + "".join(oferta_card(o, d) for o in aliados) + "</div></section>")
        cups = _cupones_destino(x, ["Gastronomía"] if serv == "gastronomia" else ["Viajes"])
        if cups:
            partes.append('<section class="of-sec"><h2>Cupones de descuento</h2><div class="of-cups">'
                          + "".join(f'<a class="of-cup" href="{rel(d, "cupones/")}#{esc(c["codigo"].lower())}"><b>{esc(c.get("descuento", ""))}</b><span>{esc(c["titulo"])}</span><small>{esc(c.get("comercio", ""))}</small></a>' for c in cups)
                          + "</div></section>")
        if not (propios or aliados or cups):
            partes.append(f'<div class="of-vacio"><b>Próximamente</b><p>Estamos sumando {"restaurantes" if serv == "gastronomia" else "alojamientos"} y cupones en {esc(n)}.</p></div>')
        pregunta = "¿Tenés un restaurante, bar o café?" if serv == "gastronomia" else "¿Tenés un hotel, una cabaña o un departamento?"
        partes.append(f'<a class="of-publica" href="{rel(d, "mi-empresa/")}?publicar=viajes"><span><b>{pregunta}</b><small>Publicalo en la guía de {esc(n)} y sumá un cupón de descuento.</small></span><em>Publicar →</em></a>')
    nav = f'<a href="{rel(d, p_dest(x))}">Guía de {esc(n)}</a>' + "".join(
        f'<a href="{rel(d, p_dest(x) + k + "/")}"{" aria-current=\"page\"" if k == clave else ""}>{t}</a>' for k, t in SUBPAGINAS)
    foto = f.get("foto")
    hero_bg = f' style="--sub-foto:url(\'{esc(foto)}\')"' if foto else ""
    main = f'''    <div class="wrap">
{crumbs(d, [("Viajes", "viajes/"), (v["nombre"], p_pais(x["pais"])), (n, p_dest(x)), (titulo.split(" en ")[0] if " en " in titulo else "En detalle", None)])}
      <nav class="of-nav" aria-label="Guía de {esc(n)}">{nav}</nav>
      <section class="sub-hero{" has-foto" if foto else ""}"{hero_bg}>
        <div><span class="eyebrow">{esc(n)} · {esc(v["nombre"])}</span><h1>{esc(titulo)}</h1><p>{esc(bajada)}</p></div>
      </section>
      {"".join(partes)}
      <a class="d-volver" href="{rel(d, p_dest(x))}">← Volver a la guía de {esc(n)}</a>
      <div class="ad-fila">{aviso(d, 3)}</div>
    </div>'''
    return page(d, f"{titulo} | Umarti Viajes", f"{bajada}", main)


def destinos_por_nota():
    """Para el blog: qué destinos enlazan cada nota (así la nota muestra 'Conocé el origen')."""
    out = {}
    for x in DESTINOS:
        for o in x["origen"]:
            if o.get("nota"):
                out.setdefault(o["nota"], []).append(x)
        for nt in (x.get("panel") or {}).get("notas") or []:
            if x not in out.setdefault(nt, []):
                out[nt].append(x)
    return out


def main():
    for x in DESTINOS:
        assert x["pais"] in PAISES, x["slug"]
        if x["paisaje"] not in PAISAJES:
            x["paisaje"] = "ciudad"
        x["tipos"] = [t for t in x["tipos"] if t in TIPOS]
        for o in x["origen"]:
            if o.get("nota") and o["nota"] not in NOTAS:
                raise SystemExit(f"{x['slug']}: la nota '{o['nota']}' no existe en el blog")
    escribir("viajes/index.html", portada())
    escribir("viajes/destinos/index.html", pagina_todos())
    for nombre, ic in SERVICIOS:
        escribir(p_serv(CLAVES_SERV[nombre]) + "index.html", pagina_servicio(nombre, ic))
    for k in PAISES:
        escribir(f"viajes/{k}/index.html", pagina_pais(k))
    for x in DESTINOS:
        escribir(p_dest(x) + "index.html", pagina_destino_panel(x) if x.get("panel") else pagina_destino(x))
        if x.get("panel"):
            for k, _ in SUBPAGINAS:
                escribir(p_dest(x) + k + "/index.html", pagina_sub(x, k))


if __name__ == "__main__":
    main()
