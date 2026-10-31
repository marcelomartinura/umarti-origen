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
from destinos import PAISES, DESTINOS  # noqa: E402
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
    ("Seguro de viaje", '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="m9 12 2 2 4-4"/>'),
    ("Autos", '<path d="M5 17h14M5 17a2 2 0 1 1 0 .01M19 17a2 2 0 1 1 0 .01M3 13l2-6h14l2 6v4H3z"/>'),
    ("Excursiones", '<circle cx="12" cy="12" r="9"/><path d="m15 9-2 6-4 0 2-6z"/>'),
    ("Paquetes", '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>'),
]


def portada():
    d = 1
    paises = [(k, v, [x for x in DESTINOS if x["pais"] == k]) for k, v in PAISES.items()]
    country_cards = "\n".join(f'''          <a class="country-card" href="{rel(d, p_pais(k))}">{vcover(v['colores'], 'montana' if k == 'argentina' else 'cerros', v['nombre'], f"{len(ds)} destinos")}</a>''' for k, v, ds in paises)
    tipos_pres = {t for x in DESTINOS for t in x["tipos"]}
    origenes = []
    for x in DESTINOS:
        for o in x["origen"][:1]:
            origenes.append(f'<a class="origin" href="{rel(d, p_dest(x))}"><small>{esc(x["nombre"])}</small><strong>{esc(o["producto"])}</strong><span>{esc(o["texto"])}</span></a>')
    servicios = "".join(f'<div class="service"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ic}</svg><strong>{n}</strong><small>Próximamente</small></div>' for n, ic in SERVICIOS)
    main = f'''    <div class="wrap">
{crumbs(d, [("Viajes", None)])}
      <section class="v-hero">
        <div>
          <span class="eyebrow">Umarti Viajes</span>
          <h1>Los lugares detrás de <em>cada producto</em></h1>
          <p class="lead">Guías de destinos de Argentina y México para planificar tu próximo viaje: cuándo ir, qué hacer, qué probar y cómo llevarte sus sabores a casa.</p>
          <form class="v-search" role="search" onsubmit="document.getElementById('destinos').scrollIntoView({{behavior:'smooth'}});return false">
            <label><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="v-q" type="search" placeholder="¿Adónde querés ir?" aria-label="Buscar destino"></label>
            <button type="submit">Explorar destinos</button>
          </form>
        </div>
        <div class="country-stack">
{country_cards}
        </div>
      </section>

      <section class="v-section" id="destinos" aria-labelledby="h-dest">
        <div class="v-head">
          <div><h2 id="h-dest">Explorá destinos</h2><p>Cada guía reúne lo esencial para planificar: la mejor época, cómo llegar, los imperdibles y los sabores del lugar.</p></div>
        </div>
        <div class="v-tools">{chips(tipos_pres)}<span class="v-count" id="v-count"></span></div>
        <div class="dest-grid" id="dest-grid">
{chr(10).join(dest_card(x, d) for x in DESTINOS)}
        </div>
      </section>
    </div>

    <section class="mesa-band" aria-labelledby="h-mesa">
      <div class="wrap">
        <span class="eyebrow">Del destino a tu mesa</span>
        <h2 id="h-mesa">Cada lugar tiene un sabor para llevarte</h2>
        <p>Viajar a Mendoza es conocer el Malbec; recorrer Misiones es entender la yerba mate. Por eso cada guía se conecta con los productos de ese lugar en la Tienda y con las notas del Blog.</p>
        <div class="origin-grid">{"".join(origenes)}</div>
      </div>
    </section>

    <div class="wrap">
      <section class="v-section" aria-labelledby="h-org">
        <div class="v-head"><div><h2 id="h-org">Organizá todo tu viaje</h2><p>Muy pronto vas a poder reservar con nuestros aliados. Mientras tanto, pedinos una propuesta a medida.</p></div></div>
        <div class="services">{servicios}</div>
{planner()}
      </section>
    </div>'''
    return page(d, "Viajes por Argentina y México: guías de destinos | Umarti Origen",
                "Guías de viaje de Buenos Aires, Mendoza, Bariloche, Ushuaia, Salta, Iguazú, Ciudad de México y Querétaro: cuándo ir, cómo llegar, qué hacer y qué probar.", main)


def pagina_pais(k):
    d = 2
    v = PAISES[k]
    ds = [x for x in DESTINOS if x["pais"] == k]
    tipos_pres = {t for x in ds for t in x["tipos"]}
    filas = "".join(f'<tr><td><a href="{rel(d, p_dest(x))}">{esc(x["nombre"])}</a></td><td>{esc(x["mejor_epoca"])}</td><td>{esc(x["clima"])}</td><td>{esc(x["dias"])}</td></tr>' for x in ds)
    main = f'''    <div class="wrap">
{crumbs(d, [("Viajes", "viajes/"), (v['nombre'], None)])}
      <div class="blog-head">
        <span class="eyebrow" style="color:var(--green)">Destinos</span>
        <h1>Viajar por {esc(v['nombre'])}</h1>
        <p>{esc(v['lead'])}</p>
        <div class="facts-row">
          <div class="fact"><small>Destinos</small><b>{len(ds)} guías</b></div>
          <div class="fact"><small>Moneda</small><b>{esc(v['moneda'])}</b></div>
          <div class="fact"><small>Idioma</small><b>{esc(v['idioma'])}</b></div>
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
        <div><h2>¿Querés que te armemos el recorrido?</h2><p>Contanos qué te gusta y te enviamos una propuesta a medida por {esc(v['nombre'])}.</p></div>
        <a class="btn-green" href="{rel(d, 'viajes/')}#planificar">Armar mi viaje</a>
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
    plan_box = f'''<div class="box plan-box"><strong>Armá tu viaje a {esc(x['nombre'])}</strong><p>Te enviamos una propuesta con recorrido, alojamiento y experiencias.</p><a class="btn-green" href="{rel(d, 'viajes/')}?destino={quote(x['nombre'])}#planificar">Pedir propuesta</a></div>'''
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


def destinos_por_nota():
    """Para el blog: qué destinos enlazan cada nota (así la nota muestra 'Conocé el origen')."""
    out = {}
    for x in DESTINOS:
        for o in x["origen"]:
            if o.get("nota"):
                out.setdefault(o["nota"], []).append(x)
    return out


def main():
    for x in DESTINOS:
        assert x["pais"] in PAISES and x["paisaje"] in PAISAJES, x["slug"]
        assert all(t in TIPOS for t in x["tipos"]), x["slug"]
        for o in x["origen"]:
            if o.get("nota") and o["nota"] not in NOTAS:
                raise SystemExit(f"{x['slug']}: la nota '{o['nota']}' no existe en el blog")
    escribir("viajes/index.html", portada())
    for k in PAISES:
        escribir(f"viajes/{k}/index.html", pagina_pais(k))
    for x in DESTINOS:
        escribir(p_dest(x) + "index.html", pagina_destino(x))


if __name__ == "__main__":
    main()
