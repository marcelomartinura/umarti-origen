#!/usr/bin/env python3
"""Genera las páginas del Hub de Oportunidades a partir de _fuente/datos.py.

Uso:  python3 _fuente/construir.py
Genera: mesa-de-negociacion/index.html, productos-de-exportacion/index.html,
        servicios-de-comercio-exterior/index.html y assets/data/hub-datos.js
El encabezado se copia de index.html (la portada), así que cualquier cambio del menú se hace ahí.
"""
import html, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from datos import SECTORES, CATEGORIAS_SERVICIO, PRODUCTOS, SERVICIOS, BUSQUEDAS, PAISES, CC  # noqa: E402

esc = html.escape
URL = {"producto": "../productos-de-exportacion/", "servicio": "../servicios-de-comercio-exterior/", "busqueda": "../mesa-de-negociacion/"}


def fecha(d):
    y, m, dd = d.split("-")
    return f"{dd}/{m}/{y}"


def hsfmt(hs):
    return f"{hs[:4]}.{hs[4:]}" if hs else ""


def cc(pais):
    return f'<span class="cc">{CC.get(pais, pais[:2].upper())}</span>'


def meta(rows):
    out = []
    for r in rows:
        cls = ' class="wide"' if len(r) > 2 else ""
        out.append(f'            <div{cls}><dt>{r[0]}</dt><dd>{r[1]}</dd></div>')
    return "\n".join(out)


def texto(*partes):
    return esc(" ".join(p for p in partes if p).lower())


# ---------- tarjetas ----------
def card_producto(o):
    info = f"{o['cod']} · SA {hsfmt(o['hs'])} · Origen: {o['pais']}" if o["hs"] else f"{o['cod']} · Origen: {o['pais']}"
    return f'''        <article class="op op--producto" id="{o['cod'].lower()}" data-kind="producto" data-codigo="{o['cod']}" data-sector="{esc(o['sector'])}" data-pais="{esc(o['pais'])}" data-vence="{o['vence']}" data-info="{esc(info)}" data-texto="{texto(o['nombre'], o['hs'], hsfmt(o['hs']), o['cod'], o['sector'], o['pais'], o['region'], o['destinos'], o['claves'])}">
          <div class="op-top">
            <span class="op-code">{o['cod']}</span>
            <span class="op-chips"><span class="chip chip-hs" title="Posición arancelaria (Sistema Armonizado)">SA {hsfmt(o['hs'])}</span></span>
          </div>
          <h3 class="op-title">{esc(o['nombre'])}</h3>
          <p class="op-sector">{esc(o['sector'])}</p>
          <dl class="op-meta">
{meta([("Origen", cc(o['pais']) + esc(o['pais']) + ' · ' + esc(o['region'])), ("Volumen disponible", esc(o['vol'])), ("Mercados de interés", esc(o['destinos']), 1)])}
          </dl>
          <div class="op-bottom">
            <span class="op-vence">Vigente hasta <time datetime="{o['vence']}">{fecha(o['vence'])}</time></span>
            <button class="op-cta" type="button" data-negociar>Negociar</button>
          </div>
        </article>'''


def card_servicio(o):
    info = f"{o['cod']} · Base: {o['pais']}"
    return f'''        <article class="op op--servicio" id="{o['cod'].lower()}" data-kind="servicio" data-codigo="{o['cod']}" data-categoria="{esc(o['categoria'])}" data-pais="{esc(o['pais'])}" data-info="{esc(info)}" data-texto="{texto(o['nombre'], o['cod'], o['categoria'], o['pais'], o['region'], o['cobertura'], o['detalle'], o['claves'])}">
          <div class="op-top">
            <span class="op-code">{o['cod']}</span>
          </div>
          <h3 class="op-title">{esc(o['nombre'])}</h3>
          <p class="op-sector">{esc(o['categoria'])}</p>
          <p class="op-desc">{esc(o['detalle'])}</p>
          <dl class="op-meta">
{meta([("Base", cc(o['pais']) + esc(o['pais']) + ' · ' + esc(o['region'])), ("Cobertura", esc(o['cobertura']), 1)])}
          </dl>
          <div class="op-bottom">
            <span class="op-vence"></span>
            <button class="op-cta" type="button" data-negociar>Solicitar cotización</button>
          </div>
        </article>'''


def card_busqueda(b):
    hs_chip = f'<span class="chip chip-hs" title="Posición arancelaria (Sistema Armonizado)">SA {hsfmt(b["hs"])}</span>' if b["hs"] else ""
    kind = "Servicio" if b["tipo"] == "servicio" else "Producto"
    info = f"{b['cod']}" + (f" · SA {hsfmt(b['hs'])}" if b["hs"] else "") + f" · Destino: {b['pais']}"
    cta = "Ofrezco este servicio" if b["tipo"] == "servicio" else "Tengo este producto"
    return f'''        <article class="op op--busqueda" id="{b['cod'].lower()}" data-kind="busqueda" data-codigo="{b['cod']}" data-tipo="{b['tipo']}" data-pais="{esc(b['pais'])}" data-vence="{b['vence']}" data-info="{esc(info)}" data-texto="{texto(b['nombre'], b['hs'], hsfmt(b['hs']), b['cod'], b['sector'], b['pais'], b['origen'])}">
          <div class="op-top">
            <span class="op-code">{b['cod']}</span>
            <span class="op-chips"><span class="chip chip-kind">{kind}</span>{hs_chip}</span>
          </div>
          <h3 class="op-title">{esc(b['nombre'])}</h3>
          <p class="op-sector">{esc(b['sector'])}</p>
          <dl class="op-meta">
{meta([("Destino", cc(b['pais']) + esc(b['pais'])), ("Volumen", esc(b['vol'])), ("Origen preferido", esc(b['origen']), 1)])}
          </dl>
          <div class="op-bottom">
            <span class="op-vence">Vigente hasta <time datetime="{b['vence']}">{fecha(b['vence'])}</time></span>
            <button class="op-cta" type="button" data-negociar>{cta}</button>
          </div>
        </article>'''


# ---------- piezas comunes ----------
def header():
    s = open(os.path.join(RAIZ, "index.html"), encoding="utf-8").read()
    h = re.search(r'  <header class="site-header".*?</header>', s, re.S).group(0)

    def fix(m):
        v = m.group(1)
        if v.startswith(("http", "mailto:", "../")):
            return m.group(0)
        if v.startswith("#"):
            return f'href="../{v}"' if len(v) > 1 else 'href="../"'
        return f'href="../{v}"'
    return re.sub(r'href="([^"]*)"', fix, h)


def opts(items, values=None):
    values = values or items
    return "".join(f'<option value="{esc(v)}">{esc(t)}</option>' for t, v in zip(items, values))


ICON_SEARCH = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
ICON_PLUS = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>'
PROTO = '''      <p class="proto-note">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="flex:none;margin-top:3px"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></svg>
        <span><b>Prototipo.</b> {txt}</span>
      </p>'''

NEG_DIALOG = '''  <dialog id="dlg-neg" class="k-producto" aria-labelledby="neg-title">
    <div class="dlg-head">
      <div>
        <h2 id="neg-title">Negociar</h2>
        <p id="neg-sub"></p>
      </div>
      <button class="dlg-close" type="button" data-close aria-label="Cerrar">×</button>
    </div>
    <div class="dlg-body">
      <div id="neg-step-form">
        <div class="neg-summary" id="neg-summary"></div>
        <form id="neg-form">
          <div class="form-grid">
            <div class="field"><label for="n-nom">Nombre <span class="req">*</span></label><input id="n-nom" required maxlength="80" autocomplete="name"></div>
            <div class="field"><label for="n-emp">Empresa <span class="req">*</span></label><input id="n-emp" required maxlength="80" autocomplete="organization"></div>
            <div class="field"><label for="n-pais">País</label><input id="n-pais" list="paises" maxlength="60"></div>
            <div class="field"><label for="n-mail">Correo <span class="req">*</span></label><input id="n-mail" type="email" required autocomplete="email"></div>
            <div class="field full"><label for="n-msg">Tu propuesta</label><textarea id="n-msg" maxlength="800" placeholder="Volumen, precio de referencia, condiciones de entrega o lo que quieras plantear."></textarea></div>
          </div>
          <div class="form-foot">
            <small>Umarti revisa tu propuesta y pone en contacto a las partes.</small>
            <button class="btn-submit" type="submit">Enviar a la mesa</button>
          </div>
        </form>
      </div>
      <div class="success" id="neg-step-ok" hidden>
        <div class="tick"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg></div>
        <h3>Tu propuesta quedó en la mesa</h3>
        <p>En la versión final, acá recibís la confirmación y Umarti te contacta para coordinar la negociación. En este prototipo no se envía nada.</p>
        <button class="btn-submit" type="button" data-close>Volver</button>
      </div>
    </div>
  </dialog>'''


def faq_block(faqs, titulo):
    items = "\n".join(f'          <details>\n            <summary>{esc(q)}</summary>\n            <p>{esc(a)}</p>\n          </details>' for q, a in faqs)
    return f'''    <section class="faq">
      <div class="wrap faq-grid">
        <div>
          <span class="eyebrow">Preguntas frecuentes</span>
          <h2>{titulo}</h2>
        </div>
        <div>
{items}
        </div>
      </div>
    </section>'''


def faq_jsonld(faqs):
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
        ensure_ascii=False, indent=2)


def crumbs(actual):
    return f'''      <nav class="crumbs" aria-label="Ubicación">
        <ol>
          <li><a href="../">Inicio</a></li>
          <li>Hub de Oportunidades</li>
          <li aria-current="page">{actual}</li>
        </ol>
      </nav>'''


def page(body_class, kind, title, desc, og_title, main, faqs, faq_title, dialogs, scripts):
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <!-- Prototipo con datos de ejemplo: quitar esta línea cuando haya publicaciones reales -->
  <meta name="robots" content="noindex">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(og_title)}">
  <meta property="og:description" content="{esc(desc)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/css/umarti.css">
  <link rel="stylesheet" href="../assets/css/hub.css">
  <script type="application/ld+json">
{faq_jsonld(faqs)}
  </script>
</head>
<body class="{body_class}"{f' data-kind="{kind}"' if kind else ''}>

{header()}

  <main>
{main}

{faq_block(faqs, faq_title)}
  </main>

  <footer>
    <div class="wrap foot">
      <div>
        <a href="../" class="logo">Umarti <span style="color:var(--terra)">Origen</span></a>
        <p style="margin-top:8px">Tienda, comercio exterior y viajes.</p>
      </div>
      <ul class="eco">
        <li><strong>Umarti Origen</strong></li>
        <li>Umarti Movilidad</li>
        <li>Umarti Digital</li>
      </ul>
      <p>© 2026 Umarti</p>
    </div>
  </footer>

{dialogs}
{NEG_DIALOG}

  <datalist id="paises">{"".join(f'<option value="{p}">' for p in PAISES)}</datalist>
  <div class="toast" id="toast" role="status"></div>

  <script src="../assets/js/header.js"></script>
  <script src="../assets/data/hub-datos.js"></script>
  <script src="../assets/js/hub-comun.js"></script>
{scripts}
</body>
</html>
'''


# ---------- Mesa de negociación ----------
def mesa():
    faqs = [
        ("¿Cómo funciona la Mesa de negociación?",
         "Ingresás el producto o servicio que estás buscando. El sistema lo cruza con lo publicado en Productos de exportación y en Servicios de Comercio Exterior. Si hay coincidencia, te vinculamos con esa oferta para empezar a negociar."),
        ("¿Qué pasa si lo que busco no está publicado?",
         "Nuestro equipo sale a buscarlo entre productores y proveedores, y te responde en un plazo de 5 días hábiles con lo que encontró. Mientras tanto, tu búsqueda queda visible en la mesa para que otros vendedores puedan ofrecerte su producto."),
        ("¿Qué es la posición arancelaria y por qué conviene indicarla?",
         "Es el código del Sistema Armonizado que identifica cada producto en el comercio internacional, igual en todos los países. Con ella, la mesa encuentra coincidencias aunque cada parte describa el producto con palabras distintas."),
        ("¿Quién ve mis datos de contacto?",
         "Nadie, mientras no decidas avanzar. En la mesa se publican el producto, el destino, el volumen y la vigencia; los datos de tu empresa se comparten solo cuando ambas partes aceptan negociar."),
    ]
    activos = len(BUSQUEDAS)
    main = f'''    <div class="wrap">
{crumbs("Mesa de negociación")}

      <div class="page-head">
        <div>
          <span class="eyebrow">Hub de Oportunidades</span>
          <h1>Mesa de negociación</h1>
          <p>Contanos qué producto o servicio estás buscando. El sistema lo cruza con lo publicado en Productos de exportación y Servicios de Comercio Exterior y, si todavía no está, nuestro equipo sale a buscarlo por vos.</p>
        </div>
        <div class="stats" aria-label="Resumen">
          <div class="stat"><strong id="stat-b">{activos}</strong><span>búsquedas activas</span></div>
          <div class="stat ok"><strong id="stat-m">–</strong><span>con coincidencia</span></div>
          <div class="stat plain"><strong id="stat-o">{len(PRODUCTOS) + len(SERVICIOS)}</strong><span>ofertas publicadas</span></div>
        </div>
      </div>

      <section class="mesa-grid" id="buscar" aria-label="Búsqueda de productos o servicios">
        <div class="flow">
          <span class="eyebrow">Cómo funciona</span>
          <h2>Así trabaja la mesa</h2>
          <div class="flow-step">
            <span class="flow-num">1</span>
            <div><h3>Ingresás lo que buscás</h3><p>Un producto o un servicio, con el volumen y el país de destino.</p></div>
          </div>
          <div class="flow-step">
            <span class="flow-num">2</span>
            <div><h3>El sistema busca coincidencias</h3><p>Cruza tu búsqueda con los Productos de exportación y los Servicios de Comercio Exterior publicados.</p></div>
          </div>
          <div class="flow-split">
            <div class="flow-out yes">
              <strong><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg>Hay coincidencia</strong>
              <p>Te vinculamos con esa oferta y empieza la negociación.</p>
            </div>
            <div class="flow-out no">
              <strong><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>No hay coincidencia</strong>
              <p>Nuestro equipo realiza la búsqueda y te responde.</p>
              <span class="days">5<small>días hábiles</small></span>
            </div>
          </div>
        </div>

        <div class="search-card">
          <form id="search-form" autocomplete="on">
            <h2>Búsqueda de productos o servicios</h2>
            <p class="lead">Completá lo que necesitás y te mostramos al instante si ya hay una oferta que coincide.</p>
            <div class="kind-toggle" role="radiogroup" aria-label="Qué estás buscando">
              <label><input type="radio" name="tipo" value="producto" checked><span>Un producto</span></label>
              <label><input type="radio" name="tipo" value="servicio"><span>Un servicio</span></label>
            </div>
            <div class="form-grid">
              <div class="field full big-input">
                <label for="s-nombre"><span data-lbl>¿Qué producto estás buscando?</span> <span class="req">*</span></label>
                <input id="s-nombre" name="nombre" required maxlength="120">
                <p class="live-hint" id="live-hint" aria-live="polite"></p>
              </div>
              <div class="field" data-solo="producto">
                <label for="s-hs">Posición arancelaria</label>
                <input id="s-hs" name="hs" inputmode="numeric" maxlength="12" placeholder="Ej.: 1509.20">
                <p class="hint">Opcional. Si no la sabés, te ayudamos.</p>
              </div>
              <div class="field" data-solo="producto">
                <label for="s-sector">Sector <span class="req">*</span></label>
                <select id="s-sector" name="sector" required><option value="">Elegí un sector</option>{opts(SECTORES)}</select>
              </div>
              <div class="field full" data-solo="servicio" hidden>
                <label for="s-cat">Tipo de servicio <span class="req">*</span></label>
                <select id="s-cat" name="categoria" required disabled><option value="">Elegí un tipo de servicio</option>{opts(CATEGORIAS_SERVICIO)}</select>
              </div>
              <div class="field">
                <label for="s-pais">País de destino <span class="req">*</span></label>
                <input id="s-pais" name="pais" required list="paises" placeholder="Ej.: México">
              </div>
              <div class="field">
                <label for="s-origen">Origen preferido</label>
                <input id="s-origen" name="origen" maxlength="80" placeholder="Ej.: Argentina o sin preferencia">
              </div>
              <div class="field">
                <label for="s-vol">Volumen requerido</label>
                <input id="s-vol" name="vol" maxlength="80" placeholder="Ej.: 2 contenedores por mes">
              </div>
              <div class="field">
                <label for="s-vence">Vigente hasta <span class="req">*</span></label>
                <input id="s-vence" name="vence" type="date" required>
              </div>
              <p class="form-sep">Datos de contacto (no se publican)</p>
              <div class="field"><label for="s-emp">Empresa <span class="req">*</span></label><input id="s-emp" name="empresa" required maxlength="80" autocomplete="organization"></div>
              <div class="field"><label for="s-mail">Correo <span class="req">*</span></label><input id="s-mail" name="mail" type="email" required autocomplete="email"></div>
            </div>
            <div class="form-foot">
              <small>Si no hay coincidencia, te respondemos en 5 días hábiles al correo que indiques.</small>
              <button class="btn-submit" type="submit">{ICON_SEARCH} Buscar en la mesa</button>
            </div>
          </form>
          <div id="search-result" hidden aria-live="polite"></div>
        </div>
      </section>

      <div class="block-head" id="busquedas">
        <div>
          <h2>Búsquedas publicadas</h2>
          <p>Lo que empresas de distintos países están buscando ahora. Si tenés alguno de estos productos o servicios, ofrecelo.</p>
        </div>
      </div>
      <form class="filters" role="search" onsubmit="return false" style="grid-template-columns: 2.2fr 1fr 1.2fr">
        <div class="field search-field">
          <label for="f-q">Buscar</label>
          {ICON_SEARCH}
          <input id="f-q" type="search" data-filter="texto" placeholder="Producto, posición arancelaria o código" autocomplete="off">
        </div>
        <div class="field">
          <label for="f-tipo">Tipo</label>
          <select id="f-tipo" data-filter="tipo"><option value="">Todos</option><option value="producto">Productos</option><option value="servicio">Servicios</option></select>
        </div>
        <div class="field">
          <label for="f-pais">País de destino</label>
          <select id="f-pais" data-filter="pais" data-auto><option value="">Todos</option></select>
        </div>
        <div class="filters-row2">
          <div class="chips-filter" data-filter-chips="estado" role="group" aria-label="Estado">
            <button type="button" data-value="" aria-pressed="true">Todas</button>
            <button type="button" data-value="match" aria-pressed="false">Con coincidencia</button>
            <button type="button" data-value="buscando" aria-pressed="false">Nuestro equipo la busca</button>
          </div>
          <div class="row2-right">
            <span class="result-count" id="result-count" data-uno="búsqueda" data-varios="búsquedas" aria-live="polite"></span>
            <button type="button" class="link-btn" id="f-clear">Limpiar filtros</button>
          </div>
        </div>
      </form>
{PROTO.format(txt="Las búsquedas y ofertas de estas páginas son ejemplos para mostrar cómo funciona la mesa. Lo que publiques ahora se ve solo en tu pantalla y no se envía.")}

      <div class="cards" id="list">
{chr(10).join(card_busqueda(b) for b in BUSQUEDAS)}
        <div class="empty" id="empty"><p>No hay búsquedas con estos filtros.</p><a class="text-link" href="#buscar">Publicá la tuya</a></div>
      </div>
    </div>'''
    return page("pg-mesa", None,
                "Mesa de negociación: búsqueda de productos y servicios de comercio exterior | Umarti Origen",
                "Publicá el producto o servicio que buscás. Lo cruzamos con productos de exportación y servicios de comercio exterior y, si no está, nuestro equipo lo busca y te responde en 5 días hábiles.",
                "Mesa de negociación | Umarti Origen", main, faqs, "Lo que conviene saber antes de buscar", "",
                '  <script src="mesa.js"></script>')


# ---------- Productos de exportación ----------
def productos():
    faqs = [
        ("¿Cómo publico un producto de exportación?",
         "Con el botón Publicar un producto. Indicá qué vendés, la posición arancelaria si la sabés, el origen, el volumen disponible y hasta cuándo está vigente. Revisamos cada publicación antes de mostrarla."),
        ("¿Qué significa que un producto tiene búsquedas en la Mesa?",
         "Que hay empresas de otros países que publicaron en la Mesa de negociación que buscan ese producto. Es la forma más directa de llegar a un comprador que ya está interesado."),
        ("¿Quién ve mis datos de contacto?",
         "Nadie, mientras no decidas avanzar. Se publican el producto, el origen y el volumen; los datos de tu empresa se comparten solo cuando ambas partes aceptan negociar."),
    ]
    paises = sorted({p["pais"] for p in PRODUCTOS})
    main = f'''    <div class="wrap">
{crumbs("Productos de exportación")}

      <div class="page-head">
        <div>
          <span class="eyebrow">Hub de Oportunidades</span>
          <h1>Productos de exportación</h1>
          <p>Productos de Argentina, México y otros países, listos para venderse a otros mercados. Cada uno muestra si ya hay empresas buscándolo en la Mesa de negociación.</p>
          <div class="head-actions">
            <button class="btn-accent" type="button" data-publicar>{ICON_PLUS} Publicar un producto</button>
            <a class="text-link" href="../mesa-de-negociacion/#buscar">¿Buscás algo que no está? Pedilo en la Mesa →</a>
          </div>
        </div>
        <div class="stats" aria-label="Resumen">
          <div class="stat"><strong id="stat-n">{len(PRODUCTOS)}</strong><span>productos</span></div>
          <div class="stat plain"><strong id="stat-p">{len(paises)}</strong><span>países de origen</span></div>
          <div class="stat ok"><strong id="stat-d">–</strong><span>con compradores buscándolos</span></div>
        </div>
      </div>

      <form class="filters" role="search" onsubmit="return false">
        <div class="field search-field">
          <label for="f-q">Buscar</label>
          {ICON_SEARCH}
          <input id="f-q" type="search" data-filter="texto" placeholder="Producto, posición arancelaria o código" autocomplete="off">
        </div>
        <div class="field">
          <label for="f-sector">Sector</label>
          <select id="f-sector" data-filter="sector"><option value="">Todos</option>{opts(SECTORES)}</select>
        </div>
        <div class="field">
          <label for="f-pais">País de origen</label>
          <select id="f-pais" data-filter="pais" data-auto><option value="">Todos</option></select>
        </div>
        <div class="field">
          <label for="f-vig">Vigencia</label>
          <select id="f-vig" data-filter-vig><option value="">Todas las vigentes</option><option value="30">Vencen en 30 días</option><option value="90">Vencen en 90 días</option></select>
        </div>
        <div class="filters-row2">
          <div class="row2-right">
            <span class="result-count" id="result-count" data-uno="producto" data-varios="productos" aria-live="polite"></span>
            <button type="button" class="link-btn" id="f-clear">Limpiar filtros</button>
          </div>
        </div>
      </form>
{PROTO.format(txt="Los productos de esta página son ejemplos. Lo que publiques ahora se ve solo en tu pantalla y no se envía.")}

      <div class="cards" id="list">
{chr(10).join(card_producto(o) for o in PRODUCTOS)}
        <div class="empty" id="empty"><p>No hay productos con estos filtros.</p><a class="text-link" href="../mesa-de-negociacion/#buscar">Pedilo en la Mesa de negociación</a></div>
      </div>

      <div class="cross">
        <div>
          <h2>¿No encontrás el producto que buscás?</h2>
          <p>Publicalo en la Mesa de negociación. Si nadie lo ofrece, nuestro equipo lo busca y te responde en 5 días hábiles.</p>
        </div>
        <a href="../mesa-de-negociacion/#buscar">Ir a la Mesa de negociación</a>
      </div>
    </div>'''
    dialog = f'''  <dialog id="dlg-pub" class="k-producto" aria-labelledby="pub-title">
    <div class="dlg-head">
      <div><h2 id="pub-title">Publicar un producto de exportación</h2><p>Llegá a compradores de otros países que ya están buscando.</p></div>
      <button class="dlg-close" type="button" data-close aria-label="Cerrar">×</button>
    </div>
    <div class="dlg-body">
      <form id="pub-form">
        <div class="form-grid">
          <div class="field full"><label for="p-nombre">Producto <span class="req">*</span></label><input id="p-nombre" name="nombre" required maxlength="120" placeholder="Ej.: Aceite de oliva extra virgen, 500 ml"></div>
          <div class="field"><label for="p-hs">Posición arancelaria</label><input id="p-hs" name="hs" inputmode="numeric" maxlength="12" placeholder="Ej.: 1509.20"><p class="hint">Opcional. Si no la sabés, te ayudamos.</p></div>
          <div class="field"><label for="p-sector">Sector <span class="req">*</span></label><select id="p-sector" name="sector" required><option value="">Elegí un sector</option>{opts(SECTORES)}</select></div>
          <div class="field"><label for="p-pais">País de origen <span class="req">*</span></label><input id="p-pais" name="pais" required list="paises" placeholder="Ej.: Argentina"></div>
          <div class="field"><label for="p-region">Provincia o estado</label><input id="p-region" name="region" maxlength="60" placeholder="Ej.: San Juan"></div>
          <div class="field"><label for="p-dest">Mercados de interés</label><input id="p-dest" name="destinos" maxlength="120" placeholder="Ej.: México, España"></div>
          <div class="field"><label for="p-vol">Volumen disponible</label><input id="p-vol" name="vol" maxlength="80" placeholder="Ej.: 1 contenedor por mes"></div>
          <div class="field"><label for="p-vence">Vigente hasta <span class="req">*</span></label><input id="p-vence" name="vence" type="date" required></div>
          <p class="form-sep">Datos de contacto (no se publican)</p>
          <div class="field"><label for="p-emp">Empresa <span class="req">*</span></label><input id="p-emp" name="empresa" required maxlength="80" autocomplete="organization"></div>
          <div class="field"><label for="p-mail">Correo <span class="req">*</span></label><input id="p-mail" name="mail" type="email" required autocomplete="email"></div>
        </div>
        <div class="form-foot">
          <small>Revisamos cada publicación antes de mostrarla. Si coincide con una búsqueda de la Mesa, te avisamos.</small>
          <button class="btn-submit" type="submit">Publicar producto</button>
        </div>
      </form>
    </div>
  </dialog>'''
    return page("pg-productos", "producto",
                "Productos de exportación de Argentina, México y el mundo | Umarti Origen",
                "Catálogo de productos de exportación con posición arancelaria, origen, volumen y vigencia. Encontrá proveedores y mirá qué productos ya tienen compradores buscándolos.",
                "Productos de exportación | Umarti Origen", main, faqs, "Sobre los productos de exportación", dialog,
                '  <script src="../assets/js/catalogo.js"></script>')


# ---------- Servicios de comercio exterior ----------
def servicios():
    faqs = [
        ("¿Qué servicios se publican en esta sección?",
         "Todo lo que hace falta para comprar o vender entre países: despachantes y agentes de aduana, transporte y logística, seguros de carga, certificaciones y asesoría en comercio exterior."),
        ("¿Cómo pido una cotización?",
         "Con el botón Solicitar cotización de cada servicio. Contás qué necesitás y Umarti te pone en contacto con el proveedor."),
        ("Soy proveedor, ¿cómo ofrezco mis servicios?",
         "Con el botón Ofrecer mis servicios. Si tu servicio coincide con una búsqueda publicada en la Mesa de negociación, te avisamos."),
    ]
    paises = sorted({s["pais"] for s in SERVICIOS})
    chips = "\n".join(f'            <button type="button" data-value="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in CATEGORIAS_SERVICIO)
    main = f'''    <div class="wrap">
{crumbs("Servicios de Comercio Exterior")}

      <div class="page-head">
        <div>
          <span class="eyebrow">Hub de Oportunidades</span>
          <h1>Servicios de Comercio Exterior</h1>
          <p>Despachantes de aduana, transporte y logística, seguros, certificaciones y asesoría para comprar y vender entre países.</p>
          <div class="head-actions">
            <button class="btn-accent" type="button" data-publicar>{ICON_PLUS} Ofrecer mis servicios</button>
            <a class="text-link" href="../mesa-de-negociacion/#buscar">¿Necesitás un servicio que no está? Pedilo en la Mesa →</a>
          </div>
        </div>
        <div class="stats" aria-label="Resumen">
          <div class="stat"><strong id="stat-n">{len(SERVICIOS)}</strong><span>servicios</span></div>
          <div class="stat plain"><strong id="stat-p">{len(paises)}</strong><span>países</span></div>
          <div class="stat ok"><strong id="stat-d">–</strong><span>pedidos en la Mesa</span></div>
        </div>
      </div>

      <form class="filters" role="search" onsubmit="return false" style="grid-template-columns: 2.2fr 1.2fr">
        <div class="field search-field">
          <label for="f-q">Buscar</label>
          {ICON_SEARCH}
          <input id="f-q" type="search" data-filter="texto" placeholder="Servicio, ciudad o ruta" autocomplete="off">
        </div>
        <div class="field">
          <label for="f-pais">País</label>
          <select id="f-pais" data-filter="pais" data-auto><option value="">Todos</option></select>
        </div>
        <div class="filters-row2">
          <div class="chips-filter" data-filter-chips="categoria" role="group" aria-label="Tipo de servicio">
            <button type="button" data-value="" aria-pressed="true">Todos</button>
{chips}
          </div>
          <div class="row2-right">
            <span class="result-count" id="result-count" data-uno="servicio" data-varios="servicios" aria-live="polite"></span>
            <button type="button" class="link-btn" id="f-clear">Limpiar filtros</button>
          </div>
        </div>
      </form>
{PROTO.format(txt="Los servicios de esta página son ejemplos. Lo que publiques ahora se ve solo en tu pantalla y no se envía.")}

      <div class="cards" id="list">
{chr(10).join(card_servicio(s) for s in SERVICIOS)}
        <div class="empty" id="empty"><p>No hay servicios con estos filtros.</p><a class="text-link" href="../mesa-de-negociacion/#buscar">Pedilo en la Mesa de negociación</a></div>
      </div>

      <div class="cross">
        <div>
          <h2>¿No encontrás el servicio que necesitás?</h2>
          <p>Publicalo en la Mesa de negociación. Si nadie lo ofrece, nuestro equipo lo busca y te responde en 5 días hábiles.</p>
        </div>
        <a href="../mesa-de-negociacion/#buscar">Ir a la Mesa de negociación</a>
      </div>
    </div>'''
    dialog = f'''  <dialog id="dlg-pub" class="k-servicio" aria-labelledby="pub-title">
    <div class="dlg-head">
      <div><h2 id="pub-title">Ofrecer servicios de comercio exterior</h2><p>Llegá a empresas que necesitan exportar o importar.</p></div>
      <button class="dlg-close" type="button" data-close aria-label="Cerrar">×</button>
    </div>
    <div class="dlg-body">
      <form id="pub-form">
        <div class="form-grid">
          <div class="field full"><label for="p-nombre">Servicio <span class="req">*</span></label><input id="p-nombre" name="nombre" required maxlength="120" placeholder="Ej.: Transporte terrestre Argentina - Chile"></div>
          <div class="field"><label for="p-cat">Tipo de servicio <span class="req">*</span></label><select id="p-cat" name="categoria" required><option value="">Elegí un tipo</option>{opts(CATEGORIAS_SERVICIO)}</select></div>
          <div class="field"><label for="p-pais">País <span class="req">*</span></label><input id="p-pais" name="pais" required list="paises" placeholder="Ej.: Argentina"></div>
          <div class="field"><label for="p-region">Ciudad o región</label><input id="p-region" name="region" maxlength="60" placeholder="Ej.: Mendoza"></div>
          <div class="field"><label for="p-cob">Cobertura o rutas</label><input id="p-cob" name="cobertura" maxlength="120" placeholder="Ej.: Argentina ↔ Chile"></div>
          <div class="field full"><label for="p-det">Descripción breve</label><textarea id="p-det" name="detalle" maxlength="240" placeholder="Qué hacés y en qué te especializás."></textarea></div>
          <p class="form-sep">Datos de contacto (no se publican)</p>
          <div class="field"><label for="p-emp">Empresa <span class="req">*</span></label><input id="p-emp" name="empresa" required maxlength="80" autocomplete="organization"></div>
          <div class="field"><label for="p-mail">Correo <span class="req">*</span></label><input id="p-mail" name="mail" type="email" required autocomplete="email"></div>
        </div>
        <div class="form-foot">
          <small>Revisamos cada publicación antes de mostrarla. Si coincide con una búsqueda de la Mesa, te avisamos.</small>
          <button class="btn-submit" type="submit">Publicar servicio</button>
        </div>
      </form>
    </div>
  </dialog>'''
    return page("pg-servicios", "servicio",
                "Servicios de comercio exterior: aduana, logística, seguros y más | Umarti Origen",
                "Despachantes de aduana, transporte internacional, seguros de carga, certificaciones y asesoría para exportar e importar entre Argentina, México y el mundo.",
                "Servicios de Comercio Exterior | Umarti Origen", main, faqs, "Sobre los servicios de comercio exterior", dialog,
                '  <script src="../assets/js/catalogo.js"></script>')


def datos_js():
    def con(items, kind):
        out = []
        for o in items:
            d = dict(o); d["kind"] = kind; d["url"] = URL[kind] + "#" + o["cod"].lower()
            out.append(d)
        return out
    data = {"productos": con(PRODUCTOS, "producto"), "servicios": con(SERVICIOS, "servicio"), "busquedas": BUSQUEDAS}
    return ("/* Generado por _fuente/construir.py a partir de _fuente/datos.py. No editar a mano. */\n"
            "window.HUB_DATOS = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")


def escribir(ruta, contenido):
    ruta = os.path.join(RAIZ, ruta)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    open(ruta, "w", encoding="utf-8").write(contenido)
    print("ok", os.path.relpath(ruta, RAIZ))


if __name__ == "__main__":
    escribir("assets/data/hub-datos.js", datos_js())
    escribir("mesa-de-negociacion/index.html", mesa())
    escribir("productos-de-exportacion/index.html", productos())
    escribir("servicios-de-comercio-exterior/index.html", servicios())
