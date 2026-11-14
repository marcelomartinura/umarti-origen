#!/usr/bin/env python3
"""Genera las páginas del Hub de Oportunidades a partir de _fuente/datos.py.

Uso:  python3 _fuente/construir.py
Genera: oportunidades-globales/ (búsquedas, cómo funciona y buscar), mesa-de-negociacion/ (vista previa),
        productos-de-exportacion/index.html,
        servicios-de-comercio-exterior/index.html y assets/data/hub-datos.js
El encabezado se copia de index.html (la portada), así que cualquier cambio del menú se hace ahí.
"""
import html, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import comun  # noqa: E402
from datos import SECTORES, CATEGORIAS_SERVICIO, PRODUCTOS, SERVICIOS, BUSQUEDAS, PAISES, CC, EMPRESAS  # noqa: E402
from construir_blog import CATEGORIAS as CATS_TIENDA, COLORES as COLORES_CAT  # noqa: E402  (las mismas categorías de la Tienda)

# Los productos de la Tienda marcados "Hub de Oportunidades: Sí" en el Catálogo se suman a Productos de exportación
sys.path.insert(0, os.path.join(AQUI, "tienda"))
try:
    from construir_tienda import productos_para_hub  # noqa: E402
    PRODUCTOS = productos_para_hub() + list(PRODUCTOS)
except FileNotFoundError:
    pass

esc = html.escape
URL = {"producto": "../productos-de-exportacion/", "servicio": "../servicios-de-comercio-exterior/", "busqueda": "../oportunidades-globales/"}


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
    return f'''        <article class="op op--producto" id="{o['cod'].lower()}" data-kind="producto" data-codigo="{o['cod']}" data-sector="{esc(o['sector'])}" data-categoria="{esc(o.get('categoria', ''))}" data-pais="{esc(o['pais'])}" data-vence="{o['vence']}" data-info="{esc(info)}" data-texto="{texto(o['nombre'], o['hs'], hsfmt(o['hs']), o['cod'], o['sector'], o['pais'], o['region'], o['destinos'], o['claves'])}">
          <div class="op-top">
            <span class="op-code">{o['cod']}</span>
            <span class="op-chips">{'<span class="chip chip-review">Umarti</span>' if o.get('tienda_url') else ''}<span class="chip chip-hs" title="Posición arancelaria (Sistema Armonizado)">{('SA ' + hsfmt(o['hs'])) if o['hs'] else 'Posición a definir'}</span></span>
          </div>
          <h3 class="op-title">{esc(o['nombre'])}</h3>
          <p class="op-sector">{esc(o.get('categoria') or o['sector'])}</p>
          <dl class="op-meta">
{meta([("Origen", cc(o['pais']) + esc(o['pais']) + ' · ' + esc(o['region'])), ("Volumen disponible", esc(o['vol'])), ("Mercados de interés", esc(o['destinos']), 1)])}
          </dl>
          <div class="op-bottom">
            <span class="op-vence">Vigente hasta <time datetime="{o['vence']}">{fecha(o['vence'])}</time></span>
            <button class="op-cta" type="button" data-negociar>Negociar</button>
          </div>{f'{chr(10)}          <a class="op-link" href="../{o["tienda_url"]}">Comprar por unidad en la Tienda →</a>' if o.get('tienda_url') else ''}
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
          <a class="op-mesa" href="../mesa-de-negociacion/?b={b['cod']}">Abrir en la Mesa de negociación <span>Pronto</span></a>
        </article>'''


# ---------- piezas comunes ----------
def header(pre="../"):
    return comun.header(pre)


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
        <h3>Tu propuesta quedó registrada</h3>
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


def crumbs(actual, pre="../", medio=None):
    m = f'\n          <li><a href="{pre}{medio[1]}">{medio[0]}</a></li>' if medio else ""
    return f'''      <nav class="crumbs" aria-label="Ubicación">
        <ol>
          <li><a href="{pre}">Inicio</a></li>
          <li><a href="{pre}hub/">Hub de Oportunidades</a></li>{m}
          <li aria-current="page">{actual}</li>
        </ol>
      </nav>'''


def page(body_class, kind, title, desc, og_title, main, faqs, faq_title, dialogs, scripts, pre="../"):
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
  <link rel="stylesheet" href="{pre}assets/css/umarti.css">
  <link rel="stylesheet" href="{pre}assets/css/hub.css">
  <script type="application/ld+json">
{faq_jsonld(faqs)}
  </script>
</head>
<body class="{body_class}"{f' data-kind="{kind}"' if kind else ''} data-pre="{'' if pre == '../' else pre[3:]}">

{header(pre)}

  <main>
{main}

{faq_block(faqs, faq_title) if faqs else ''}
  </main>

{comun.footer(pre)}

{dialogs}
{NEG_DIALOG}

  <datalist id="paises">{"".join(f'<option value="{p}">' for p in PAISES)}</datalist>
  <div class="toast" id="toast" role="status"></div>

  <script src="{pre}assets/js/header.js"></script>
  <script src="{pre}assets/data/hub-datos.js"></script>
  <script src="{pre}assets/js/hub-comun.js"></script>
{scripts}
</body>
</html>
'''


# ---------- Oportunidades Globales ----------
def _faqs_og():
    return [
        ("¿Cómo funciona Oportunidades Globales?",
         "Ingresás el producto o servicio que estás buscando. El sistema lo cruza con lo publicado en Productos de exportación y en Servicios de Comercio Exterior. Si hay coincidencia, te vinculamos con esa oferta para empezar a negociar."),
        ("¿Qué pasa si lo que busco no está publicado?",
         "Nuestro equipo sale a buscarlo entre productores y proveedores, y te responde en un plazo de 5 días hábiles con lo que encontró. Mientras tanto, tu búsqueda queda publicada para que otros vendedores puedan ofrecerte su producto."),
        ("¿Qué es la posición arancelaria y por qué conviene indicarla?",
         "Es el código del Sistema Armonizado que identifica cada producto en el comercio internacional, igual en todos los países. Con ella, la mesa encuentra coincidencias aunque cada parte describa el producto con palabras distintas."),
        ("¿Quién ve mis datos de contacto?",
         "Nadie, mientras no decidas avanzar. En la mesa se publican el producto, el destino, el volumen y la vigencia; los datos de tu empresa se comparten solo cuando ambas partes aceptan negociar."),
    ]


def hero_og(pre, titulo="Oportunidades Globales", lead=None, botones=True):
    lead = lead or "Empresas de distintos países publican lo que están buscando. Si lo tenés, ofrecelo; si buscás algo, publicalo y lo cruzamos con lo que ofrecen productores y proveedores."
    btns = f'''
          <div class="og-btns">
            <a class="og-btn ghost" href="{pre}oportunidades-globales/como-funciona/">Cómo funciona</a>
            <a class="og-btn" href="{pre}oportunidades-globales/buscar/">{ICON_SEARCH} Buscar un producto</a>
          </div>''' if botones else ""
    return f'''      <div class="pres-banner og-banner" style="--pb-bg:#eef0f4;--pb-pos:center 60%">
        <img src="{pre}assets/img/hub-avion.jpg" alt="">
        <div class="pb-txt">
          <span class="eyebrow">Hub de Oportunidades</span>
          <h1>{titulo}</h1>
          <p>{lead}</p>{btns}
        </div>
      </div>'''


MESA_BAND = '''      <a class="mesa-band-og" href="{pre}mesa-de-negociacion/">
        <span class="mb-tag">Próximamente</span>
        <span class="mb-txt"><b>Mesa de negociación digital</b><small>Ofertas, contraofertas y acuerdos con reglas claras, identidad verificada y depósito en garantía.</small></span>
        <span class="mb-go">Ver cómo va a ser →</span>
      </a>'''


def oportunidades():
    activos = len(BUSQUEDAS)
    main = f'''    <div class="wrap">
{crumbs("Oportunidades Globales")}
{hero_og("../")}
      <div class="stats og-stats" aria-label="Resumen">
        <div class="stat"><strong id="stat-b">{activos}</strong><span>búsquedas activas</span></div>
        <div class="stat ok"><strong id="stat-m">–</strong><span>con coincidencia</span></div>
        <div class="stat plain"><strong id="stat-o">{len(PRODUCTOS) + len(SERVICIOS)}</strong><span>ofertas publicadas</span></div>
      </div>

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
{PROTO.format(txt="Las búsquedas y ofertas de estas páginas son ejemplos para mostrar cómo funciona. Lo que publiques ahora se ve solo en tu pantalla y no se envía.")}

      <div class="cards" id="list">
{chr(10).join(card_busqueda(b) for b in BUSQUEDAS)}
        <div class="empty" id="empty"><p>No hay búsquedas con estos filtros.</p><a class="text-link" href="buscar/">Publicá la tuya</a></div>
      </div>
{MESA_BAND.format(pre="../")}
    </div>'''
    return page("pg-mesa", None,
                "Oportunidades Globales: búsquedas de productos y servicios de comercio exterior | Umarti Origen",
                "Búsquedas de productos y servicios publicadas por empresas de distintos países. Si tenés lo que buscan, ofrecelo; si buscás algo, publicalo y lo cruzamos con productores y proveedores.",
                "Oportunidades Globales | Umarti Origen", main, _faqs_og(), "Lo que conviene saber", "",
                '  <script src="../assets/js/oportunidades.js"></script>')


def como_funciona():
    pre = "../../"
    main = f'''    <div class="wrap">
{crumbs("Cómo funciona", pre, ("Oportunidades Globales", "oportunidades-globales/"))}
{hero_og(pre, "Cómo funciona", "Publicás lo que buscás, el sistema lo cruza con lo que ofrecen productores y proveedores y, si todavía no está, nuestro equipo sale a buscarlo por vos.", False)}
      <section class="og-flow-wrap">
        <div class="flow">
          <span class="eyebrow">Cómo funciona</span>
          <h2>Así funciona</h2>
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
              <p>Te vinculamos con esa oferta para empezar a negociar.</p>
            </div>
            <div class="flow-out no">
              <strong><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>No hay coincidencia</strong>
              <p>Nuestro equipo realiza la búsqueda y te responde.</p>
              <span class="days">5<small>días hábiles</small></span>
            </div>
          </div>
        </div>

        <div class="og-side">
          <h2>¿Listo para empezar?</h2>
          <p>Publicá tu búsqueda en dos minutos. Tus datos de contacto no se publican.</p>
          <a class="og-btn" href="../buscar/">{ICON_SEARCH} Buscar un producto</a>
          <a class="text-link" href="../">Ver las búsquedas publicadas →</a>
        </div>
      </section>
{MESA_BAND.format(pre=pre)}
    </div>'''
    return page("pg-mesa", None, "Cómo funciona Oportunidades Globales | Umarti Origen",
                "Publicá el producto o servicio que buscás: lo cruzamos con productos de exportación y servicios de comercio exterior y, si no está, nuestro equipo lo busca y te responde en 5 días hábiles.",
                "Cómo funciona Oportunidades Globales | Umarti Origen", main, _faqs_og(), "Lo que conviene saber", "", "", pre)


def buscar():
    pre = "../../"
    main = f'''    <div class="wrap">
{crumbs("Buscar un producto o servicio", pre, ("Oportunidades Globales", "oportunidades-globales/"))}
      <section class="og-buscar" id="buscar" aria-label="Búsqueda de productos o servicios">
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
              <button class="btn-submit" type="submit">{ICON_SEARCH} Publicar búsqueda</button>
            </div>
          </form>
          <div id="search-result" hidden aria-live="polite"></div>
        </div>
      </section>
{PROTO.format(txt="Lo que publiques ahora se ve solo en tu pantalla y no se envía.")}
    </div>'''
    return page("pg-mesa", None, "Buscar un producto o servicio | Oportunidades Globales | Umarti Origen",
                "Publicá el producto o servicio que estás buscando y te mostramos al instante si ya hay una oferta que coincide.",
                "Buscar un producto o servicio | Umarti Origen", main, [], "", "",
                f'  <script src="{pre}assets/js/oportunidades.js"></script>', pre)


# ---------- Mesa de negociación (vista previa, próximamente) ----------
def mesa_digital():
    faqs = [
        ("¿Cuándo va a estar disponible la Mesa de negociación?", "Estamos construyéndola. Mientras tanto, podés publicar tu búsqueda en Oportunidades Globales y nuestro equipo pone en contacto a las partes."),
        ("¿Por qué hay que verificar la identidad?", "Para negociar operaciones de valor, las dos partes validan su identidad con su documento (DNI, INE o pasaporte). Así se evitan perfiles falsos y ofertas poco serias."),
        ("¿Qué es el depósito en garantía?", "Es un monto chico que el comprador deja en la plataforma para que su oferta sea vinculante. Si el vendedor acepta, queda congelado como reserva hasta el cierre."),
        ("¿Qué pasa cuando las dos partes aceptan?", "La mesa se cierra para nuevas ofertas y se genera la hoja de condiciones con todo lo acordado: precio, cantidad, forma de pago, entrega y quién paga cada gasto."),
    ]
    etapas = ["Negociación", "Acuerdo", "Depósito", "Cierre"]
    prog = "".join(f'<li data-etapa="{i}"><span>{i + 1}</span>{e}</li>' for i, e in enumerate(etapas))
    pasos = [("Oferta inicial", "El comprador abre la mesa con una propuesta formal: precio, cantidad, forma de pago y entrega."),
             ("Conversación y ajustes", "Se abre la sala. Las partes conversan, pero todo gira en torno a la ficha del trato, donde se modifican las condiciones."),
             ("Contraoferta", "El vendedor acepta, rechaza o contraoferta con un clic. Cada contraoferta congela los términos anteriores."),
             ("Pre-acuerdo", "Cuando los dos aceptan los términos, la mesa se cierra para nuevas ofertas y se genera la hoja de condiciones.")]
    pasos_html = "".join(f'<div class="md-paso"><span>{i + 1}</span><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(pasos))
    conf = [("Identidad verificada", "Las dos partes validan su identidad con DNI, INE o pasaporte y biometría antes de negociar operaciones de valor.", '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="m9 12 2 2 4-4"/>'),
            ("Depósito en garantía", "El comprador puede dejar un depósito para que su oferta sea vinculante. Si el vendedor acepta, queda como reserva.", '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2M12 12v3"/>'),
            ("Documentos verificados", "El vendedor sube certificados, habilitaciones y análisis; el sistema los revisa y le da la insignia de documentos verificados.", '<path d="M6 3h9l4 4v14H6zM14 3v5h5"/><path d="m9 14 2 2 4-4"/>')]
    conf_html = "".join(f'<div class="md-conf"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ic}</svg><h3>{t}</h3><p>{d}</p></div>' for t, d, ic in conf)
    busq = json.dumps({b["cod"]: {"nombre": b["nombre"], "pais": b["pais"], "vol": b["vol"]} for b in BUSQUEDAS}, ensure_ascii=False)
    main = f'''    <div class="wrap">
{crumbs("Mesa de negociación", "../", ("Oportunidades Globales", "oportunidades-globales/"))}
      <div class="md-head">
        <span class="md-pronto">Próximamente · Vista previa</span>
        <h1>Mesa de negociación</h1>
        <p>Negociar no debería ser un chat desordenado. En la mesa, cada oferta tiene sus condiciones a la vista, cada paso queda registrado y las dos partes saben siempre en qué etapa están.</p>
      </div>

      <section class="md-demo" aria-label="Vista previa de la mesa">
        <ol class="md-prog" id="md-prog">{prog}</ol>
        <div class="md-sala">
          <div class="md-chat">
            <div class="md-chat-head"><b id="md-titulo">Yerba mate elaborada</b><small id="md-sub">Comprador en México · Vendedor en Argentina</small></div>
            <div class="md-msgs" id="md-msgs" aria-live="polite"></div>
            <div class="md-sug" id="md-sug"></div>
            <form class="md-input" id="md-form"><input id="md-txt" placeholder="Escribí un mensaje…" autocomplete="off"><button type="submit">Enviar</button></form>
          </div>
          <aside class="md-ficha">
            <div class="md-ficha-h"><b>Ficha del trato</b><span class="md-estado" id="md-estado">Oferta del comprador</span></div>
            <dl class="md-cond" id="md-cond"></dl>
            <div class="md-gastos"><b>Gastos estimados y quién los paga</b><dl id="md-gastos"></dl></div>
            <div class="md-acc" id="md-acc"></div>
            <details class="md-hist"><summary>Ofertas anteriores (<span id="md-nhist">0</span>)</summary><ol id="md-hist"></ol></details>
          </aside>
        </div>
        <p class="md-nota">Vista previa con datos de ejemplo: probá contraofertar y aceptar los términos. No se envía nada.</p>
      </section>

      <section class="md-sec">
        <h2>Cómo va a funcionar</h2>
        <div class="md-pasos">{pasos_html}</div>
      </section>

      <section class="md-sec">
        <h2>Confianza y seguridad</h2>
        <div class="md-confs">{conf_html}</div>
      </section>

      <div class="viajes-note md-cta">
        <div><h2>Mientras tanto, publicá lo que buscás</h2><p>Nuestro equipo pone en contacto a las partes y acompaña la negociación.</p></div>
        <a href="../oportunidades-globales/buscar/">Buscar un producto</a>
      </div>
    </div>
    <script>window.MESA_BUSQUEDAS = {busq};</script>'''
    return page("pg-mesa", None, "Mesa de negociación (próximamente) | Umarti Origen",
                "Así va a ser la Mesa de negociación de Umarti: ofertas y contraofertas con condiciones claras, identidad verificada, depósito en garantía y hoja de condiciones.",
                "Mesa de negociación | Umarti Origen", main, faqs, "Sobre la Mesa de negociación", "",
                '  <script src="../assets/js/mesa-digital.js"></script>')


# ---------- Productos de exportación ----------
def productos():
    faqs = [
        ("¿Cómo publico un producto de exportación?",
         "Con el botón Publicar un producto. Indicá qué vendés, la posición arancelaria si la sabés, el origen, el volumen disponible y hasta cuándo está vigente. Revisamos cada publicación antes de mostrarla."),
        ("¿Qué significa que un producto tiene búsquedas en Oportunidades Globales?",
         "Que hay empresas de otros países que publicaron en Oportunidades Globales que buscan ese producto. Es la forma más directa de llegar a un comprador que ya está interesado."),
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
          <p>Productos de Argentina, México y otros países, listos para venderse a otros mercados. Cada uno muestra si ya hay empresas buscándolo en Oportunidades Globales.</p>
          <div class="head-actions">
            <a class="btn-accent" href="../mi-empresa/?publicar=producto">{ICON_PLUS} Publicar un producto</a>
            <a class="text-link" href="../oportunidades-globales/buscar/">¿Buscás algo que no está? Publicá tu búsqueda →</a>
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
          <label for="f-cat">Categoría</label>
          <select id="f-cat" data-filter="categoria"><option value="">Todas</option>{opts(list(CATS_TIENDA))}</select>
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
        <div class="empty" id="empty"><p>No hay productos con estos filtros.</p><a class="text-link" href="../oportunidades-globales/buscar/">Publicá tu búsqueda</a></div>
      </div>

      <div class="cross">
        <div>
          <h2>¿No encontrás el producto que buscás?</h2>
          <p>Publicalo en Oportunidades Globales. Si nadie lo ofrece, nuestro equipo lo busca y te responde en 5 días hábiles.</p>
        </div>
        <a href="../oportunidades-globales/buscar/">Publicar una búsqueda</a>
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
          <small>Revisamos cada publicación antes de mostrarla. Si coincide con una búsqueda de Oportunidades Globales, te avisamos.</small>
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
         "Con el botón Ofrecer mis servicios: creás la cuenta de tu empresa, validás tu identidad y publicás. Si tu servicio coincide con una búsqueda publicada en Oportunidades Globales, te avisamos."),
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
            <a class="btn-accent" href="../mi-empresa/?publicar=servicio">{ICON_PLUS} Ofrecer mis servicios</a>
            <a class="text-link" href="../oportunidades-globales/buscar/">¿Necesitás un servicio que no está? Publicá tu búsqueda →</a>
          </div>
        </div>
        <div class="stats" aria-label="Resumen">
          <div class="stat"><strong id="stat-n">{len(SERVICIOS)}</strong><span>servicios</span></div>
          <div class="stat plain"><strong id="stat-p">{len(paises)}</strong><span>países</span></div>
          <div class="stat ok"><strong id="stat-d">–</strong><span>búsquedas publicadas</span></div>
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
        <div class="empty" id="empty"><p>No hay servicios con estos filtros.</p><a class="text-link" href="../oportunidades-globales/buscar/">Publicá tu búsqueda</a></div>
      </div>

      <div class="cross">
        <div>
          <h2>¿No encontrás el servicio que necesitás?</h2>
          <p>Publicalo en Oportunidades Globales. Si nadie lo ofrece, nuestro equipo lo busca y te responde en 5 días hábiles.</p>
        </div>
        <a href="../oportunidades-globales/buscar/">Publicar una búsqueda</a>
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
          <small>Revisamos cada publicación antes de mostrarla. Si coincide con una búsqueda de Oportunidades Globales, te avisamos.</small>
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


# ---------- Hub: Mesa de Negocio de Oportunidades Comerciales Globales (portada del Hub) ----------
def _slug(t):
    import unicodedata
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


ICON_IA = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/><path d="M5 16l.6 1.4L7 18l-1.4.6L5 20l-.6-1.4L3 18l1.4-.6z"/></svg>'
ICON_CE = {
    "servicios": '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 17h13l3-5h2"/><path d="M5 17l-2-5h11l2 5"/><path d="M7 12V8h5l2 4"/><path d="M2 20c2 1 4 1 6 0s4-1 6 0 4 1 6 0"/></svg>',
    "recursos": '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="2.5" width="14" height="19" rx="2"/><path d="M8 6h8v3H8zM8 13h1M12 13h1M16 13h0M8 17h1M12 17h1M16 13v4"/></svg>',
    "blog": '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4h12a3 3 0 0 1 3 3v13H7a3 3 0 0 1-3-3z"/><path d="M8 8h7M8 12h7M8 16h4"/><circle cx="18.5" cy="5.5" r="3"/><path d="M15.5 5.5h6M18.5 2.5c1 1 1 5 0 6"/></svg>',
}
EJEMPLOS_IA = ["20 toneladas de yerba mate para España", "Despachante de aduana en México", "Vino Malbec por contenedor para Alemania"]


def crumbs_hub(actual=None, pre="../"):
    fin = f'\n          <li aria-current="page">{actual}</li>' if actual else ""
    hub = f'<li><a href="{pre}hub/">Hub de Oportunidades</a></li>' if actual else '<li aria-current="page">Hub de Oportunidades</li>'
    return f'''      <nav class="crumbs" aria-label="Ubicación">
        <ol>
          <li><a href="{pre}">Inicio</a></li>
          {hub}{fin}
        </ol>
      </nav>'''


def hub():
    pre = "../"
    cuenta = {}
    for o in PRODUCTOS:
        cuenta[o.get("categoria", "")] = cuenta.get(o.get("categoria", ""), 0) + 1
    tiles = []
    for c in CATS_TIENDA:
        col = COLORES_CAT.get(c, ("#4b5d78", "#2b3648"))
        n = cuenta.get(c, 0)
        foto = os.path.join(RAIZ, "assets", "img", "categorias", _slug(c) + ".jpg")
        img = f'<img src="{pre}assets/img/categorias/{_slug(c)}.jpg" alt="" loading="lazy">' if os.path.exists(foto) else ""
        tiles.append(f'''          <a class="hc-tile" href="{pre}productos-de-exportacion/?categoria={esc(c)}" style="--c1:{col[0]};--c2:{col[1]}">{img}
            <b>{esc(c)}</b><small>{plural_txt(n, "producto", "productos") if n else "Sé el primero en publicar"}</small>
          </a>''')
    tiles.append(f'''          <a class="hc-tile hc-serv" href="{pre}servicios-de-comercio-exterior/">
            <b>Servicios de comercio exterior</b><small>{plural_txt(len(SERVICIOS), "servicio", "servicios")}</small>
          </a>''')
    ejemplos = "".join(f'<button type="button" data-ej="{esc(e)}">{esc(e)}</button>' for e in EJEMPLOS_IA)
    main = f'''    <div class="wrap">
{crumbs_hub(None, pre)}
      <section class="mesa-hero">
        <div class="mh-txt">
          <span class="eyebrow">Hub de Oportunidades Globales</span>
          <h1>Mesa de Negocio de Oportunidades Comerciales Globales</h1>
          <p>Compradores, productores y proveedores de distintos países, en una misma mesa. Contanos qué necesitás o mostrá lo que exportás, y te conectamos.</p>
        </div>
        <img class="mh-img" src="{pre}assets/img/hub-mesa.svg" alt="Dos personas cierran un acuerdo con un apretón de manos sobre una mesa de negocios">
      </section>

      <div class="hub-main">
        <section class="hub-ia" aria-labelledby="ia-title">
          <h2 id="ia-title">¿Buscás importar productos o servicios?</h2>
          <p class="hia-lead">Escribilo con tus palabras: qué necesitás, cuánto y para qué país. Lo cruzamos con lo que ofrecen productores y proveedores de todo el mundo.</p>
          <form id="ia-form" class="hia-form" autocomplete="off">
            <div class="hia-box">
              <span class="hia-ico">{ICON_IA}</span>
              <label for="ia-q" class="sr">Qué estás buscando</label>
              <textarea id="ia-q" name="q" rows="2" maxlength="300" required placeholder="Ej.: Busco 20 toneladas de yerba mate para importar a España"></textarea>
              <button class="hia-go" type="submit">{ICON_SEARCH}<span id="ia-go-txt">Buscar</span></button>
            </div>
            <div class="hia-ej"><span>Probá con:</span>{ejemplos}</div>
            <label class="hia-pub">
              <input type="checkbox" id="ia-pub" name="publicar">
              <span class="sw" aria-hidden="true"></span>
              <span><b>¿Querés dejar publicada tu búsqueda?</b><small>La ven productores y proveedores de otros países y te pueden ofrecer lo que buscás. Tus datos de contacto no se publican.</small></span>
            </label>
            <div class="hia-datos" id="ia-datos" hidden>
              <div class="field"><label for="ia-pais">País de destino <span class="req">*</span></label><input id="ia-pais" name="pais" list="paises" placeholder="Ej.: España"></div>
              <div class="field"><label for="ia-vol">Volumen</label><input id="ia-vol" name="vol" maxlength="80" placeholder="Ej.: 5 toneladas por mes"></div>
              <div class="field"><label for="ia-vence">Vigente hasta <span class="req">*</span></label><input id="ia-vence" name="vence" type="date"></div>
              <div class="field"><label for="ia-emp">Empresa <span class="req">*</span></label><input id="ia-emp" name="empresa" maxlength="80" autocomplete="organization"></div>
              <div class="field"><label for="ia-mail">Correo <span class="req">*</span></label><input id="ia-mail" name="mail" type="email" autocomplete="email"></div>
            </div>
          </form>
          <div class="hia-res" id="ia-res" hidden aria-live="polite"></div>
        </section>

        <aside class="hub-exp" aria-labelledby="exp-title">
          <span class="he-tag">Exportadores</span>
          <h2 id="exp-title">¿Querés exportar tus productos?</h2>
          <p>Armá la página de tu empresa exportadora y que los compradores de otros países te encuentren.</p>
          <ul>
            <li>Quiénes son y qué producen</li>
            <li>Capacidad, certificaciones e Incoterms</li>
            <li>Mercados a los que ya venden</li>
          </ul>
          <a class="he-btn" href="{pre}empresas-exportadoras/">Publicar mi empresa</a>
          <a class="he-link" href="{pre}empresas-exportadoras/{EMPRESAS[0]['slug']}/">Ver una página de ejemplo →</a>
          <hr>
          <a class="he-link" href="{pre}oportunidades-globales/">Ver lo que están buscando los compradores →</a>
        </aside>
      </div>

      <section class="hub-cats" aria-labelledby="hc-title">
        <div class="hc-head">
          <h2 id="hc-title">Encontrá el producto o servicio</h2>
          <p>Productos listos para exportar, ordenados con las mismas categorías de la Tienda.</p>
        </div>
        <div class="hc-grid">
{chr(10).join(tiles)}
        </div>
      </section>

      <section class="hub-ce" aria-labelledby="ce-title">
        <div class="ce-head">
          <span class="ce-eye">Todo para operar con el mundo</span>
          <h2 id="ce-title">Comercio exterior, de punta a punta</h2>
          <p>Quién te ayuda, con qué herramientas y lo que conviene saber antes de exportar o importar.</p>
        </div>
        <div class="ce-grid">
          <a class="ce-card c1" href="{pre}servicios-de-comercio-exterior/">
            <span class="ce-ico">{ICON_CE["servicios"]}</span>
            <h3>Servicios de Comercio Exterior</h3>
            <p>Despachantes de aduana, transporte y logística, seguros de carga, certificaciones y consultoría.</p>
            <span class="ce-go">Ver {plural_txt(len(SERVICIOS), "servicio", "servicios")} →</span>
          </a>
          <a class="ce-card c2" href="{pre}recursos/#g-comercio-exterior">
            <span class="ce-ico">{ICON_CE["recursos"]}</span>
            <h3>Recursos Digitales de Comercio Exterior</h3>
            <p>Calculadora de exportación, conversor de monedas, calculadora de carga y más herramientas gratis.</p>
            <span class="ce-go">Usar las herramientas →</span>
          </a>
          <a class="ce-card c3" href="{pre}blog/negocios/">
            <span class="ce-ico">{ICON_CE["blog"]}</span>
            <h3>Blog de Negocios Internacionales</h3>
            <p>Incoterms, mercados, cómo exportar paso a paso y novedades del comercio internacional.</p>
            <span class="ce-go">Leer las notas →</span>
          </a>
        </div>
      </section>
{MESA_BAND.format(pre=pre)}
    </div>'''
    return page("pg-mesa pg-hub", None,
                "Mesa de Negocio de Oportunidades Comerciales Globales | Hub de Oportunidades | Umarti Origen",
                "Buscá productos y servicios para importar, publicá tu búsqueda o mostrá tu empresa exportadora. Compradores, productores y proveedores de distintos países en una misma mesa.",
                "Mesa de Negocio de Oportunidades Comerciales Globales | Umarti Origen", main, _faqs_og(), "Lo que conviene saber", "",
                f'  <script src="{pre}assets/js/hub-mesa.js"></script>', pre)


def plural_txt(n, uno, varios):
    return f"{n} {uno if n == 1 else varios}"


# ---------- Empresas exportadoras ----------
def _empresa_card(e, pre):
    return f'''          <a class="ee-card" href="{pre}empresas-exportadoras/{e['slug']}/">
            <span class="ee-av">{esc(e['nombre'][0])}</span>
            <span class="ee-txt"><b>{esc(e['nombre'])}</b><small>{cc(e['pais'])}{esc(e['region'])}, {esc(e['pais'])} · {esc(e['rubro'])}</small>
            <em>{esc(e['lema'])}</em></span>
            {'<span class="ee-ej">Ejemplo</span>' if e.get('ejemplo') else ''}
          </a>'''


def empresas():
    pre = "../"
    main = f'''    <div class="wrap">
{crumbs_hub("Empresas exportadoras", pre)}
      <section class="ee-hero">
        <div>
          <span class="eyebrow">Hub de Oportunidades</span>
          <h1>Empresas exportadoras</h1>
          <p>Cada empresa tiene su propia página: quiénes son, qué producen, cuánto pueden producir, con qué certificaciones y a qué mercados ya venden. Así un comprador de otro país conoce a la empresa, no solo un producto suelto.</p>
          <div class="og-btns">
            <a class="og-btn" href="{pre}mi-empresa/?publicar=empresa">{ICON_PLUS} Crear la página de mi empresa</a>
            <a class="og-btn ghost" href="{pre}empresas-exportadoras/{EMPRESAS[0]['slug']}/">Ver un ejemplo</a>
          </div>
        </div>
        <ol class="ee-pasos">
          <li><b>Registrás tu empresa</b><small>Validamos su identidad antes de publicar.</small></li>
          <li><b>Completás tu página</b><small>Historia, productos, capacidad, certificaciones y mercados.</small></li>
          <li><b>Te encuentran</b><small>Aparecés en las búsquedas de compradores y te escriben por la mesa.</small></li>
        </ol>
      </section>
      <div class="block-head"><div><h2>Directorio</h2><p>Empresas con página publicada.</p></div></div>
      <div class="ee-grid">
{chr(10).join(_empresa_card(e, pre) for e in EMPRESAS)}
      </div>
{PROTO.format(txt="La empresa de esta página es un ejemplo para mostrar cómo se ve. Todavía no hay empresas publicadas.")}
    </div>'''
    return page("pg-mesa pg-hub", None, "Empresas exportadoras | Hub de Oportunidades | Umarti Origen",
                "Páginas de empresas exportadoras de Argentina, México y otros países: qué producen, capacidad, certificaciones y mercados.",
                "Empresas exportadoras | Umarti Origen", main, [], "", "", "", pre)


def empresa_pagina(e):
    pre = "../../"
    prods = "".join(f'''
            <li><b>{esc(n)}</b><small>{('SA ' + hsfmt(hs) + ' · ') if hs else ''}{esc(pres)}</small>{f'<a href="{pre}productos-de-exportacion/#{cod.lower()}">Ver la oferta →</a>' if cod else ''}</li>''' for n, hs, pres, cod in e["productos"])
    certs = "".join(f"<li>{esc(c)}</li>" for c in e["certificaciones"])
    mercados = "".join(f'<li>{cc(m)}{esc(m)}</li>' for m in e["mercados"])
    anios = 2026 - e["desde"]
    info = f"{e['nombre']} · {e['region']}, {e['pais']}"
    main = f'''    <div class="wrap">
{crumbs_hub(esc(e['nombre']), pre).replace('<li aria-current="page">', f'<li><a href="{pre}empresas-exportadoras/">Empresas exportadoras</a></li>{chr(10)}          <li aria-current="page">')}
{PROTO.format(txt="Esta es una empresa de ejemplo para mostrar cómo se ve la página de una empresa exportadora.") if e.get("ejemplo") else ""}
      <article class="emp op" data-kind="producto" data-codigo="{e['slug']}" data-info="{esc(info)}">
        <header class="emp-hero">
          <span class="emp-av">{esc(e['nombre'][0])}</span>
          <div>
            <span class="eyebrow">{esc(e['rubro'])}</span>
            <h1 class="op-title">{esc(e['nombre'])}</h1>
            <p class="emp-lema">{esc(e['lema'])}</p>
            <p class="emp-loc">{cc(e['pais'])}{esc(e['region'])}, {esc(e['pais'])}<span>·</span>Identidad verificada</p>
          </div>
          <div class="emp-cta">
            <button class="og-btn" type="button" data-negociar>Contactar a la empresa</button>
            <small>Tus datos se comparten solo si las dos partes aceptan negociar.</small>
          </div>
        </header>
        <div class="emp-stats">
          <div><strong>{anios}</strong><span>años produciendo</span></div>
          <div><strong>{2026 - e['exporta_desde']}</strong><span>años exportando</span></div>
          <div><strong>{len(e['mercados'])}</strong><span>mercados</span></div>
          <div><strong>{esc(e['capacidad'])}</strong><span>capacidad</span></div>
        </div>
        <div class="emp-grid">
          <section class="emp-box emp-sobre"><h2>Quiénes somos</h2><p>{esc(e['sobre'])}</p>{'<p class="emp-mb">También fabricamos con la marca de tu empresa (marca blanca).</p>' if e.get('marca_blanca') else ''}</section>
          <section class="emp-box"><h2>Qué producimos</h2><ul class="emp-prods">{prods}
          </ul></section>
          <section class="emp-box"><h2>Capacidad y logística</h2>
            <dl class="emp-dl">
              <div><dt>Capacidad de producción</dt><dd>{esc(e['capacidad'])}</dd></div>
              <div><dt>Pedido mínimo</dt><dd>{esc(e['minimo'])}</dd></div>
              <div><dt>Plazo de entrega</dt><dd>{esc(e['entrega'])}</dd></div>
              <div><dt>Condiciones de entrega</dt><dd>{" · ".join(e['incoterms'])}</dd></div>
              <div><dt>Salida</dt><dd>{esc(", ".join(e['puertos']))}</dd></div>
            </dl>
          </section>
          <section class="emp-box"><h2>Certificaciones</h2><ul class="emp-chips">{certs}</ul>
            <h2 class="mt">Mercados donde ya vendemos</h2><ul class="emp-chips mk">{mercados}</ul></section>
        </div>
      </article>
    </div>'''
    return page("pg-mesa pg-hub", None, f"{e['nombre']}: empresa exportadora | Umarti Origen",
                f"{e['nombre']}, {e['rubro'].lower()} de {e['region']}, {e['pais']}. {e['lema']}",
                f"{e['nombre']} | Empresas exportadoras | Umarti Origen", main, [], "", "", "", pre)


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
    escribir("hub/index.html", hub())
    escribir("empresas-exportadoras/index.html", empresas())
    for e in EMPRESAS:
        escribir(f"empresas-exportadoras/{e['slug']}/index.html", empresa_pagina(e))
    escribir("oportunidades-globales/index.html", oportunidades())
    escribir("oportunidades-globales/como-funciona/index.html", como_funciona())
    escribir("oportunidades-globales/buscar/index.html", buscar())
    escribir("mesa-de-negociacion/index.html", mesa_digital())
    escribir("productos-de-exportacion/index.html", productos())
    escribir("servicios-de-comercio-exterior/index.html", servicios())
