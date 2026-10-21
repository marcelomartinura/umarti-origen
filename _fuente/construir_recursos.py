#!/usr/bin/env python3
"""Genera Recursos digitales: la portada recursos/ y una página por herramienta.

Uso:  python3 _fuente/construir_recursos.py

Las herramientas funcionan en el navegador (assets/js/recursos.js). Solo el conversor de monedas
consulta datos en vivo: dolarapi.com (dólar en Argentina) y open.er-api.com (resto de las monedas).
"""
import html, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comun  # noqa: E402
from comun import escribir, SITIO  # noqa: E402

esc = html.escape

# ---------- catálogo de herramientas ----------
# (clave, nombre, bajada, grupo, ícono, lista)
HERRAMIENTAS = [
    ("conversor-de-monedas", "Conversor de monedas", "Pesos argentinos, mexicanos, dólares y más, con el dólar oficial, MEP y blue en vivo.", "Comercio exterior", "moneda", True),
    ("calculadora-de-exportacion", "Calculadora financiera de exportación", "Factoraje, precio de exportación EXW, FOB y CIF, y precio puesto en destino.", "Comercio exterior", "export", True),
    ("calculadora-de-carga", "Calculadora de carga", "Peso volumétrico y cuántas cajas entran en un pallet o en un contenedor.", "Comercio exterior", "caja", True),
    ("calculadora-de-precio-y-margen", "Calculadora de precio y margen", "Cuánto ganás de verdad con cada venta, o qué precio poner para ganar lo que querés.", "Vender en línea", "margen", True),
    ("tabla-de-talles", "Tabla de talles", "Equivalencias de ropa y calzado entre Argentina, México, Estados Unidos y Europa.", "Moda", "talle", True),
    ("buscador-de-posicion-arancelaria", "Buscador de posición arancelaria", "Encontrá el código de tu producto para exportar o importar.", "Comercio exterior", "lupa", False),
    ("incoterms-interactivo", "Incoterms interactivo", "Qué paga y qué riesgo asume cada parte, tramo por tramo.", "Comercio exterior", "ruta", False),
    ("documentos-para-exportar", "Documentos para exportar", "La lista de papeles según origen, destino y tipo de producto.", "Comercio exterior", "doc", False),
    ("cotizacion-proforma", "Cotización y factura proforma", "Completá los datos y descargá un PDF listo para enviar.", "Vender en línea", "doc", False),
    ("conversor-de-unidades", "Conversor de unidades", "Kilos y libras, centímetros y pulgadas, litros y galones.", "Vender en línea", "regla", False),
    ("enlace-de-whatsapp", "Enlace de WhatsApp y QR", "Para que tus clientes te escriban con un toque.", "Vender en línea", "chat", False),
]
GRUPOS = [("Comercio exterior", "Para exportar, importar y negociar con otros países."),
          ("Vender en línea", "Para poner precios, cobrar y atender a tus clientes."),
          ("Moda", "Para comprar y vender ropa y calzado sin errores de talle.")]

ICONOS = {
    "moneda": '<circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.6-1-1.7-1.5-3-1.5-1.7 0-3 .9-3 2.2 0 3 6 1.6 6 4.6 0 1.3-1.3 2.2-3 2.2-1.4 0-2.6-.6-3.2-1.6M12 6v2M12 16v2"/>',
    "export": '<path d="M3 17h18M5 17l1.5-5h11L19 17M8 12V7h8v5M12 3v4"/>',
    "caja": '<path d="M3 8l9-5 9 5v8l-9 5-9-5zM3 8l9 5 9-5M12 13v8"/>',
    "margen": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "talle": '<path d="M8 3l4 2 4-2 5 3-2 4-2-1v12H7V9L5 10 3 6z"/>',
    "lupa": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "ruta": '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h7a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h7"/>',
    "doc": '<path d="M6 3h9l4 4v14H6zM14 3v5h5M9 13h6M9 17h6"/>',
    "regla": '<path d="M3 17 17 3l4 4L7 21zM7 13l2 2M10 10l2 2M13 7l2 2"/>',
    "chat": '<path d="M4 19l1.5-4A8 8 0 1 1 9 18.5z"/>',
}


def icono(k, size=26):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONOS[k]}</svg>'


def rel(depth, path=""):
    return ("../" * depth) + path if depth or path else "./"


def crumbs(depth, items):
    lis = [f'<li><a href="{rel(depth)}">Inicio</a></li>']
    for nombre, path in items:
        lis.append(f'<li><a href="{rel(depth, path)}">{esc(nombre)}</a></li>' if path else f'<li aria-current="page">{esc(nombre)}</li>')
    return '      <nav class="crumbs" aria-label="Ubicación"><ol>' + "".join(lis) + "</ol></nav>"


def page(depth, title, desc, main, jsonld=None):
    pre = rel(depth)
    canon = f'\n  <link rel="canonical" href="{SITIO}/{"" if depth == 0 else ""}">' if False else ""
    lds = jsonld if isinstance(jsonld, list) else ([jsonld] if jsonld else [])
    ld = "".join(f'\n  <script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, indent=2)}\n  </script>' for x in lds)
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">{canon}
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
{comun.FUENTES}
  <link rel="stylesheet" href="{pre}assets/css/umarti.css">
  <link rel="stylesheet" href="{pre}assets/css/blog.css">
  <link rel="stylesheet" href="{pre}assets/css/recursos.css">{ld}
</head>
<body data-prefix="{pre}">

{comun.header(pre)}

  <main>
{main}
  </main>

{comun.footer(pre)}

  <script src="{pre}assets/js/header.js"></script>
  <script src="{pre}assets/js/recursos.js"></script>
</body>
</html>
'''


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def app_ld(nombre, desc):
    return {"@context": "https://schema.org", "@type": "WebApplication", "name": nombre, "description": desc,
            "applicationCategory": "BusinessApplication", "operatingSystem": "Cualquiera (navegador)", "inLanguage": "es",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}


def pagina_herramienta(clave, cuerpo, faqs, relacionadas, aviso):
    h = next(x for x in HERRAMIENTAS if x[0] == clave)
    d = 2
    rels = "".join(f'<li><a href="{rel(d, url)}">{esc(t)}</a></li>' for t, url in relacionadas)
    otras = [x for x in HERRAMIENTAS if x[5] and x[0] != clave][:4]
    otras_html = "".join(f'<a class="rc-mini" href="{rel(d, "recursos/" + x[0] + "/")}"><span class="rc-ico">{icono(x[4], 20)}</span><span><b>{esc(x[1])}</b><small>{esc(x[2])}</small></span></a>' for x in otras)
    faq_html = "".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    main = f'''    <div class="wrap">
{crumbs(d, [("Recursos digitales", "recursos/"), (h[1], None)])}
      <header class="rc-head">
        <span class="rc-ico big">{icono(h[4], 30)}</span>
        <div>
          <span class="eyebrow">{esc(h[3])}</span>
          <h1>{esc(h[1])}</h1>
          <p>{esc(h[2])}</p>
        </div>
      </header>
{cuerpo}
      <p class="rc-aviso">{aviso}</p>
      <div class="rc-bottom">
        <section class="rc-faq" aria-labelledby="faq-h">
          <h2 id="faq-h">Preguntas frecuentes</h2>
          {faq_html}
        </section>
        <aside class="rc-side">
          {f'<div class="box"><h2>Para leer</h2><ul class="mini-list">{rels}</ul></div>' if rels else ''}
          <div class="box"><h2>Otras herramientas</h2><div class="rc-minis">{otras_html}</div><a class="all" href="{rel(d, 'recursos/')}">Todos los recursos</a></div>
        </aside>
      </div>
    </div>'''
    return page(d, f"{h[1]} gratis | Recursos Umarti Origen", h[2], main, [app_ld(h[1], h[2]), faq_ld(faqs)])


# ---------- portada ----------
def portada():
    d = 1
    bloques = []
    for g, bajada in GRUPOS:
        cards = []
        for k, n, b, gr, ic, lista in HERRAMIENTAS:
            if gr != g:
                continue
            if lista:
                cards.append(f'<a class="rc-card" href="{k}/"><span class="rc-ico">{icono(ic)}</span><h3>{esc(n)}</h3><p>{esc(b)}</p><span class="rc-go">Abrir →</span></a>')
            else:
                cards.append(f'<div class="rc-card soon"><span class="rc-ico">{icono(ic)}</span><h3>{esc(n)}</h3><p>{esc(b)}</p><span class="rc-go">Próximamente</span></div>')
        bloques.append(f'''      <section class="rc-grupo" aria-labelledby="g-{comun.slug(g)}">
        <div class="blk-head"><div><h2 id="g-{comun.slug(g)}">{esc(g)}</h2><p>{esc(bajada)}</p></div></div>
        <div class="rc-grid">{"".join(cards)}</div>
      </section>''')
    main = f'''    <div class="wrap">
{crumbs(d, [("Recursos digitales", None)])}
      <div class="blog-head">
        <span class="eyebrow">Herramientas</span>
        <h1>Recursos digitales</h1>
        <p>Calculadoras y tablas gratuitas para vender en línea, exportar e importar. Funcionan en tu navegador, sin registrarte.</p>
      </div>
{chr(10).join(bloques)}
      <div class="viajes-note" style="margin-top:8px">
        <div><h2>¿Qué herramienta te falta?</h2><p>Si hay un cálculo que hacés todas las semanas para vender o exportar, contanos. Lo sumamos a la lista.</p></div>
        <a href="{rel(d, 'mesa-de-negociacion/')}">Escribinos en la Mesa</a>
      </div>
    </div>'''
    itemlist = {"@context": "https://schema.org", "@type": "ItemList", "name": "Recursos digitales de Umarti Origen",
                "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x[1]} for i, x in enumerate(h for h in HERRAMIENTAS if h[5])]}
    return page(d, "Recursos digitales: calculadoras para vender y exportar | Umarti Origen",
                "Conversor de monedas con dólar oficial, MEP y blue, calculadora de exportación, de carga, de precio y margen, y tabla de talles. Gratis.",
                main, itemlist)


# ---------- 1. Conversor de monedas ----------
MONEDAS = [("ARS", "Peso argentino"), ("MXN", "Peso mexicano"), ("USD", "Dólar estadounidense"), ("EUR", "Euro"),
           ("BRL", "Real brasileño"), ("CLP", "Peso chileno"), ("UYU", "Peso uruguayo"), ("COP", "Peso colombiano"),
           ("PEN", "Sol peruano"), ("CAD", "Dólar canadiense"), ("GBP", "Libra esterlina"), ("CNY", "Yuan chino")]


def conversor():
    opts = "".join(f'<option value="{c}">{c} · {esc(n)}</option>' for c, n in MONEDAS)
    cuerpo = f'''      <section class="tool card-tool" data-tool="monedas">
        <div class="cv-row">
          <label class="fld grow">Monto<input id="cv-monto" type="number" min="0" step="any" value="1000" inputmode="decimal"></label>
          <label class="fld">De<select id="cv-de">{opts}</select></label>
          <button type="button" class="cv-swap" id="cv-swap" aria-label="Invertir monedas">⇄</button>
          <label class="fld">A<select id="cv-a">{opts}</select></label>
        </div>
        <div class="cv-ars" id="cv-ars" hidden>
          <span class="lbl">Dólar en Argentina</span>
          <div class="seg" role="radiogroup" aria-label="Tipo de dólar">
            <button type="button" data-casa="oficial" aria-pressed="true">Oficial</button>
            <button type="button" data-casa="bolsa" aria-pressed="false">MEP</button>
            <button type="button" data-casa="blue" aria-pressed="false">Blue</button>
            <button type="button" data-casa="tarjeta" aria-pressed="false">Tarjeta</button>
          </div>
        </div>
        <output class="cv-out" id="cv-out" aria-live="polite">Cargando cotizaciones…</output>
        <p class="cv-meta" id="cv-meta"></p>
      </section>

      <div class="rc-two">
        <section class="tool" aria-labelledby="h-ar">
          <h2 id="h-ar" class="tool-h">Dólar hoy en Argentina</h2>
          <div class="tbl-wrap"><table class="tbl" id="cv-tabla-ar"><thead><tr><th>Tipo</th><th>Compra</th><th>Venta</th></tr></thead><tbody><tr><td colspan="3">Cargando…</td></tr></tbody></table></div>
        </section>
        <section class="tool" aria-labelledby="h-mx">
          <h2 id="h-mx" class="tool-h">Monedas frente al dólar y al peso mexicano</h2>
          <div class="tbl-wrap"><table class="tbl" id="cv-tabla-mx"><thead><tr><th>Moneda</th><th>1 USD =</th><th>1 MXN =</th></tr></thead><tbody><tr><td colspan="3">Cargando…</td></tr></tbody></table></div>
        </section>
      </div>
      <p class="cv-fuentes">Fuentes: dólar en Argentina de <a href="https://dolarapi.com" rel="noopener" target="_blank">DolarApi</a>; resto de las monedas de <a href="https://www.exchangerate-api.com" rel="noopener" target="_blank">Rates by Exchange Rate API</a>.</p>'''
    faqs = [
        ("¿Qué diferencia hay entre el dólar oficial, el MEP y el blue?", "El oficial es el que fija el mercado regulado por el Banco Central. El MEP (o dólar bolsa) se obtiene comprando y vendiendo bonos, de forma legal. El blue es el del mercado informal. El dólar tarjeta es el oficial más los impuestos que se cobran a las compras en el exterior."),
        ("¿Con qué dólar se calcula un peso argentino a otra moneda?", "Elegís el tipo de dólar arriba y el conversor pasa primero de pesos argentinos a dólares con esa cotización, y después de dólares a la moneda de destino."),
        ("¿Cada cuánto se actualizan las cotizaciones?", "El dólar en Argentina se actualiza varias veces por día. El resto de las monedas, una vez por día. Abajo del resultado ves la hora de la última actualización."),
        ("¿Sirve para operaciones de comercio exterior?", "Sirve como referencia. Para una operación real, usá la cotización que te informe tu banco o tu despachante el día de la operación."),
    ]
    return pagina_herramienta("conversor-de-monedas", cuerpo, faqs,
                              [("Primeros pasos para exportar de Argentina a México", "blog/primeros-pasos-para-exportar-de-argentina-a-mexico/"),
                               ("Incoterms explicados: FOB, CIF, EXW", "blog/incoterms-explicados-fob-cif-exw/")],
                              "Las cotizaciones son de referencia y pueden diferir de las de tu banco o casa de cambio.")


# ---------- 2. Calculadora financiera de exportación ----------
def exportacion():
    cuerpo = '''      <div class="tabs-tool" role="tablist" aria-label="Cálculos">
        <button type="button" role="tab" aria-selected="true" data-tab="fact">Factoraje</button>
        <button type="button" role="tab" aria-selected="false" data-tab="precio">Precio de exportación</button>
        <button type="button" role="tab" aria-selected="false" data-tab="destino">Precio puesto en destino</button>
      </div>

      <section class="tool split" data-tool="factoraje" data-panel="fact">
        <div class="inputs">
          <p class="tool-intro">El factoraje te adelanta el cobro de una factura de exportación a cambio de una comisión. Compará dos ofertas.</p>
          <label class="fld">Monto de la factura (USD)<input id="fa-monto" type="number" min="0" step="any" value="100000" inputmode="decimal"></label>
          <label class="fld">Plazo hasta el cobro (días)<input id="fa-dias" type="range" min="15" max="180" step="15" value="30"><span class="range-val" id="fa-dias-v">30 días</span></label>
          <div class="ofertas">
            <fieldset><legend>Oferta A</legend>
              <label class="fld">Anticipo (%)<input id="fa-a-ant" type="number" min="1" max="100" step="1" value="80"></label>
              <label class="fld">Tasa mensual (%)<input id="fa-a-tasa" type="number" min="0" step="0.05" value="2"></label>
            </fieldset>
            <fieldset><legend>Oferta B</legend>
              <label class="fld">Anticipo (%)<input id="fa-b-ant" type="number" min="1" max="100" step="1" value="90"></label>
              <label class="fld">Tasa mensual (%)<input id="fa-b-tasa" type="number" min="0" step="0.05" value="1.5"></label>
            </fieldset>
          </div>
        </div>
        <div class="results" id="fa-out" aria-live="polite"></div>
      </section>

      <section class="tool split" data-tool="precio-export" data-panel="precio" hidden>
        <div class="inputs">
          <p class="tool-intro">Partí del costo de tu producto y sumá los gastos de cada tramo. Todo en la misma moneda (por ejemplo, USD).</p>
          <div class="grid2">
            <label class="fld">Costo por unidad<input id="pe-costo" type="number" min="0" step="any" value="10"></label>
            <label class="fld">Cantidad de unidades<input id="pe-cant" type="number" min="1" step="1" value="1000"></label>
            <label class="fld">Margen de ganancia (%)<input id="pe-margen" type="number" min="0" step="0.5" value="25"></label>
            <label class="fld">Embalaje y etiquetado (total)<input id="pe-emb" type="number" min="0" step="any" value="300"></label>
            <label class="fld">Flete hasta el puerto (total)<input id="pe-flete-int" type="number" min="0" step="any" value="400"></label>
            <label class="fld">Despacho y gastos en origen (total)<input id="pe-desp" type="number" min="0" step="any" value="500"></label>
            <label class="fld">Derechos de exportación (%)<input id="pe-dex" type="number" min="0" step="0.5" value="0"><small>Si tu producto los paga en Argentina, se calculan sobre el valor FOB.</small></label>
            <label class="fld">Flete internacional (total)<input id="pe-flete" type="number" min="0" step="any" value="1800"></label>
            <label class="fld">Seguro de carga (% del CIF)<input id="pe-seg" type="number" min="0" step="0.05" value="0.5"></label>
          </div>
        </div>
        <div class="results" id="pe-out" aria-live="polite"></div>
      </section>

      <section class="tool split" data-tool="destino" data-panel="destino" hidden>
        <div class="inputs">
          <p class="tool-intro">Lo que le cuesta de verdad al comprador cuando la mercadería llega a su país. Usalo para negociar.</p>
          <div class="grid2">
            <label class="fld">Valor CIF de la mercadería<input id="pd-cif" type="number" min="0" step="any" value="15000"></label>
            <label class="fld">Cantidad de unidades<input id="pd-cant" type="number" min="1" step="1" value="1000"></label>
            <label class="fld">País de destino<select id="pd-pais"><option value="16">México (IVA 16%)</option><option value="21">Argentina (IVA 21%)</option><option value="19">Chile (IVA 19%)</option><option value="0">Estados Unidos (sin IVA federal)</option><option value="21">España (IVA 21%)</option><option value="">Otro</option></select></label>
            <label class="fld">Arancel de importación (%)<input id="pd-arancel" type="number" min="0" step="0.5" value="10"><small>Depende de la posición arancelaria y de los acuerdos entre países.</small></label>
            <label class="fld">IVA o impuesto de importación (%)<input id="pd-iva" type="number" min="0" step="0.5" value="16"></label>
            <label class="fld">Otros cargos aduaneros (%)<input id="pd-otros" type="number" min="0" step="0.05" value="0.8"><small>En México, por ejemplo, el DTA.</small></label>
            <label class="fld">Despachante, almacenaje y flete local (total)<input id="pd-gastos" type="number" min="0" step="any" value="900"></label>
          </div>
        </div>
        <div class="results" id="pd-out" aria-live="polite"></div>
      </section>'''
    faqs = [
        ("¿Qué es el factoraje de exportación?", "Es una forma de cobrar antes una factura que tu comprador del exterior te pagará más adelante. Una empresa te adelanta un porcentaje del monto y te cobra una comisión mensual por ese anticipo."),
        ("¿Qué diferencia hay entre el precio EXW, FOB y CIF?", "EXW es el precio en tu depósito. FOB incluye llevar la mercadería hasta el puerto y despacharla. CIF suma el flete internacional y el seguro hasta el puerto de destino. Cada uno corresponde a un Incoterm distinto."),
        ("¿Sobre qué valor se calcula el arancel de importación?", "En la mayoría de los países, incluido México, sobre el valor en aduana, que suele ser el CIF. El IVA de importación se calcula sobre el CIF más el arancel y los otros cargos."),
        ("¿Los resultados reemplazan a un despachante?", "No. Son una estimación para planificar y negociar. Los aranceles, impuestos y beneficios por acuerdos dependen de la posición arancelaria exacta de tu producto."),
    ]
    return pagina_herramienta("calculadora-de-exportacion", cuerpo, faqs,
                              [("Incoterms explicados: FOB, CIF, EXW", "blog/incoterms-explicados-fob-cif-exw/"),
                               ("Qué es la posición arancelaria", "blog/que-es-la-posicion-arancelaria/"),
                               ("Primeros pasos para exportar de Argentina a México", "blog/primeros-pasos-para-exportar-de-argentina-a-mexico/")],
                              "Cálculos de referencia. Confirmá aranceles, impuestos y costos con tu despachante antes de cotizar.")


# ---------- 3. Calculadora de carga ----------
def carga():
    cuerpo = '''      <section class="tool split" data-tool="carga">
        <div class="inputs">
          <p class="tool-intro">Cargá las medidas de una caja y cuántas vas a mandar.</p>
          <div class="grid3">
            <label class="fld">Largo (cm)<input id="cg-l" type="number" min="1" step="any" value="40"></label>
            <label class="fld">Ancho (cm)<input id="cg-a" type="number" min="1" step="any" value="30"></label>
            <label class="fld">Alto (cm)<input id="cg-h" type="number" min="1" step="any" value="25"></label>
          </div>
          <div class="grid2">
            <label class="fld">Peso por caja (kg)<input id="cg-p" type="number" min="0" step="any" value="8"></label>
            <label class="fld">Cantidad de cajas<input id="cg-n" type="number" min="1" step="1" value="50"></label>
          </div>
          <label class="chk-line"><input type="checkbox" id="cg-rot" checked> Las cajas se pueden girar y apoyar de costado</label>
        </div>
        <div class="results" id="cg-out" aria-live="polite"></div>
      </section>
      <section class="tool" aria-labelledby="h-cont">
        <h2 id="h-cont" class="tool-h">¿Cuántas cajas entran?</h2>
        <div class="tbl-wrap"><table class="tbl" id="cg-tabla"><thead><tr><th>Unidad de carga</th><th>Medidas internas</th><th>Cajas por volumen</th><th>Cajas por peso</th><th>Entran</th><th>Para tus cajas</th></tr></thead><tbody></tbody></table></div>
        <p class="tool-nota">Cálculo por acomodo en filas parejas, sin mezclar orientaciones. En la práctica, un buen estibado puede sumar algunas cajas más.</p>
      </section>'''
    faqs = [
        ("¿Qué es el peso volumétrico?", "Es el peso que las transportistas le asignan a un envío según el espacio que ocupa. Se calcula multiplicando largo por ancho por alto en centímetros y dividiendo por un factor: 6000 en carga aérea y 5000 en la mayoría de las paqueterías."),
        ("¿Me cobran el peso real o el volumétrico?", "El mayor de los dos. Por eso conviene usar cajas del tamaño justo: una caja grande y liviana paga como si fuera pesada."),
        ("¿Cómo se cobra el flete marítimo?", "En carga suelta (LCL) se cobra por metro cúbico o por tonelada, lo que sea mayor: una tonelada equivale a un metro cúbico. Si llenás un contenedor (FCL), pagás el contenedor completo."),
        ("¿Qué medidas tiene un contenedor de 20 y de 40 pies?", "Por dentro, un contenedor de 20 pies mide unos 5,9 × 2,35 × 2,39 m (33 m³) y uno de 40 pies, unos 12 × 2,35 × 2,39 m (67 m³). El de 40 High Cube tiene 30 cm más de alto."),
    ]
    return pagina_herramienta("calculadora-de-carga", cuerpo, faqs,
                              [("Primeros pasos para exportar de Argentina a México", "blog/primeros-pasos-para-exportar-de-argentina-a-mexico/"),
                               ("Incoterms explicados: FOB, CIF, EXW", "blog/incoterms-explicados-fob-cif-exw/")],
                              "Medidas y límites de referencia. Cada transportista y naviera tiene sus propios máximos.")


# ---------- 4. Calculadora de precio y margen ----------
def margen():
    cuerpo = '''      <div class="tabs-tool" role="tablist" aria-label="Modo">
        <button type="button" role="tab" aria-selected="true" data-tab="gano">Tengo el precio: ¿cuánto gano?</button>
        <button type="button" role="tab" aria-selected="false" data-tab="pongo">Quiero ganar: ¿qué precio pongo?</button>
      </div>
      <section class="tool split" data-tool="margen">
        <div class="inputs">
          <label class="fld">Dónde vendés<select id="mg-pais">
            <option value="21">Argentina, discriminando IVA (21%)</option>
            <option value="16">México, con IVA (16%)</option>
            <option value="0">Sin IVA (monotributo, RESICO u otro régimen)</option>
          </select></label>
          <div class="grid2">
            <label class="fld">Costo del producto<input id="mg-costo" type="number" min="0" step="any" value="5000"><small>Sin IVA.</small></label>
            <label class="fld" data-modo="gano">Precio de venta al público<input id="mg-precio" type="number" min="0" step="any" value="12000"><small>Lo que paga el cliente, con IVA.</small></label>
            <label class="fld" data-modo="pongo" hidden>Ganancia que querés (%)<input id="mg-objetivo" type="number" min="0" max="90" step="1" value="30"><small>Sobre el precio sin IVA.</small></label>
            <label class="fld">Comisión del marketplace o de la pasarela (%)<input id="mg-com" type="number" min="0" step="0.1" value="13"><small>Sobre el precio final.</small></label>
            <label class="fld">Cargo fijo por venta<input id="mg-fijo" type="number" min="0" step="any" value="0"></label>
            <label class="fld">Envío a tu cargo<input id="mg-envio" type="number" min="0" step="any" value="0"></label>
            <label class="fld">Empaque y otros gastos<input id="mg-otros" type="number" min="0" step="any" value="200"></label>
          </div>
        </div>
        <div class="results" id="mg-out" aria-live="polite"></div>
      </section>'''
    faqs = [
        ("¿Qué diferencia hay entre margen y markup?", "El margen es la ganancia como porcentaje del precio de venta. El markup es la ganancia como porcentaje del costo. Un producto que cuesta 100 y se vende a 150 tiene un markup del 50% y un margen del 33%."),
        ("¿Por qué la comisión se calcula sobre el precio con IVA?", "Porque la mayoría de los marketplaces y pasarelas de pago cobran su comisión sobre el total que paga el cliente."),
        ("¿Cómo se trata el IVA en el cálculo?", "Si discriminás IVA, la parte de IVA del precio no es tuya: se la pagás al Estado. La calculadora la descuenta. Es un cálculo simplificado que no considera el IVA que recuperás de tus compras; para eso, consultá a tu contador."),
        ("¿Qué comisión cobra cada marketplace?", "Cambia según la plataforma, la categoría y el plan. Revisá la tabla vigente de la tuya y cargala en el campo de comisión."),
    ]
    return pagina_herramienta("calculadora-de-precio-y-margen", cuerpo, faqs,
                              [("Cómo usar la Mesa de negociación", "blog/como-usar-la-mesa-de-negociacion/")],
                              "Cálculo simplificado de referencia. Para tu situación impositiva, consultá a tu contador.")


# ---------- 5. Tabla de talles ----------
CALZADO_M = [  # cm, MX, US, EU, AR
    (22, "22", "5", "35", "34"), (22.5, "22.5", "5.5", "35.5", "34.5"), (23, "23", "6", "36", "35"),
    (23.5, "23.5", "6.5", "37", "36"), (24, "24", "7", "37.5", "36.5"), (24.5, "24.5", "7.5", "38", "37"),
    (25, "25", "8", "38.5", "37.5"), (25.5, "25.5", "8.5", "39", "38"), (26, "26", "9", "40", "39"),
    (26.5, "26.5", "9.5", "40.5", "39.5"), (27, "27", "10", "41", "40")]
CALZADO_H = [
    (24, "24", "6", "39", "38"), (24.5, "24.5", "6.5", "39.5", "38.5"), (25, "25", "7", "40", "39"),
    (25.5, "25.5", "7.5", "40.5", "39.5"), (26, "26", "8", "41", "40"), (26.5, "26.5", "8.5", "42", "41"),
    (27, "27", "9", "42.5", "41.5"), (27.5, "27.5", "9.5", "43", "42"), (28, "28", "10", "44", "43"),
    (28.5, "28.5", "10.5", "44.5", "43.5"), (29, "29", "11", "45", "44"), (30, "30", "12", "46.5", "45.5")]
ROPA_M = [  # letra, AR, MX, US, EU, busto, cintura, cadera
    ("XS", "1 · 36", "ECH · 3", "0–2", "34", "80–84", "62–66", "86–90"),
    ("S", "2 · 38–40", "CH · 5", "4–6", "36–38", "85–89", "67–71", "91–95"),
    ("M", "3 · 42", "M · 7–9", "8–10", "40", "90–94", "72–76", "96–100"),
    ("L", "4 · 44–46", "G · 11–13", "12–14", "42–44", "95–101", "77–83", "101–107"),
    ("XL", "5 · 48", "EG · 15", "16", "46", "102–108", "84–90", "108–114"),
    ("XXL", "6 · 50", "EEG · 17", "18–20", "48–50", "109–115", "91–97", "115–121")]
ROPA_H = [  # letra, AR, MX, US, EU, pecho, cintura, cintura pulgadas
    ("XS", "1 · 44", "ECH · 32", "34", "44", "84–88", "70–74", "28"),
    ("S", "2 · 46", "CH · 34", "36", "46", "89–94", "75–80", "30"),
    ("M", "3 · 48", "M · 36", "38–40", "48–50", "95–102", "81–88", "32"),
    ("L", "4 · 50", "G · 38", "42–44", "52–54", "103–110", "89–96", "34–36"),
    ("XL", "5 · 52", "EG · 40", "46", "56", "111–118", "97–104", "38"),
    ("XXL", "6 · 54", "EEG · 42", "48–50", "58–60", "119–126", "105–112", "40–42")]


def tabla(cab, filas, cls=""):
    th = "".join(f"<th>{esc(c)}</th>" for c in cab)
    trs = "".join("<tr>" + "".join(f"<td>{esc(str(c))}</td>" for c in f) + "</tr>" for f in filas)
    return f'<div class="tbl-wrap"><table class="tbl {cls}"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def talles():
    datos = {"m": [list(map(str, r)) for r in CALZADO_M], "h": [list(map(str, r)) for r in CALZADO_H]}
    cab_c = ["Largo del pie (cm)", "México", "Estados Unidos", "Europa", "Argentina"]
    cuerpo = f'''      <section class="tool split" data-tool="pie">
        <div class="inputs">
          <h2 class="tool-h">¿Qué número calzás?</h2>
          <p class="tool-intro">Pará sobre una hoja, marcá el talón y la punta del dedo más largo y medí la distancia en centímetros.</p>
          <div class="seg" role="radiogroup" aria-label="Calzado de">
            <button type="button" data-pie="m" aria-pressed="true">Mujer</button>
            <button type="button" data-pie="h" aria-pressed="false">Hombre</button>
          </div>
          <label class="fld">Largo de tu pie (cm)<input id="tl-cm" type="number" min="18" max="33" step="0.1" value="24"></label>
        </div>
        <div class="results" id="tl-out" aria-live="polite"></div>
      </section>
      <script>window.TALLES_PIE = {json.dumps(datos)};</script>

      <div class="tabs-tool" role="tablist" aria-label="Tablas">
        <button type="button" role="tab" aria-selected="true" data-tab="cm">Calzado mujer</button>
        <button type="button" role="tab" aria-selected="false" data-tab="ch">Calzado hombre</button>
        <button type="button" role="tab" aria-selected="false" data-tab="rm">Ropa mujer</button>
        <button type="button" role="tab" aria-selected="false" data-tab="rh">Ropa hombre</button>
      </div>
      <section class="tool" data-panel="cm">{tabla(cab_c, CALZADO_M, "hl")}</section>
      <section class="tool" data-panel="ch" hidden>{tabla(cab_c, CALZADO_H, "hl")}</section>
      <section class="tool" data-panel="rm" hidden>{tabla(["Talle", "Argentina", "México", "Estados Unidos", "Europa", "Busto (cm)", "Cintura (cm)", "Cadera (cm)"], ROPA_M, "hl")}</section>
      <section class="tool" data-panel="rh" hidden>{tabla(["Talle", "Argentina", "México", "Estados Unidos", "Europa", "Pecho (cm)", "Cintura (cm)", "Pantalón (pulgadas)"], ROPA_H, "hl")}</section>'''
    faqs = [
        ("¿Cómo convierto un número de calzado de Argentina a México?", "México numera el calzado por el largo del pie en centímetros. Medí tu pie y buscá la fila con ese largo: ahí ves el número de Argentina, México, Estados Unidos y Europa."),
        ("¿El talle argentino es igual al europeo?", "Se parecen, pero el argentino suele ser un número menos que el europeo. Un 37 de Argentina equivale aproximadamente a un 38 europeo."),
        ("¿Qué significan CH, G y EG en México?", "Son los talles de ropa con letras en México: CH es chico (S), M es mediano, G es grande (L), EG es extra grande (XL) y EEG es doble extra grande (XXL)."),
        ("¿Las tablas sirven para todas las marcas?", "Son una guía. Cada marca tiene su propia horma: si está entre dos talles, revisá la tabla del vendedor o elegí el más grande."),
    ]
    return pagina_herramienta("tabla-de-talles", cuerpo, faqs,
                              [("Guía de talles: cómo medirte para acertar en tu compra", "blog/guia-de-talles-como-medirte/")],
                              "Equivalencias orientativas. Las medidas pueden variar según la marca y el modelo.")


def main():
    escribir("recursos/index.html", portada())
    escribir("recursos/conversor-de-monedas/index.html", conversor())
    escribir("recursos/calculadora-de-exportacion/index.html", exportacion())
    escribir("recursos/calculadora-de-carga/index.html", carga())
    escribir("recursos/calculadora-de-precio-y-margen/index.html", margen())
    escribir("recursos/tabla-de-talles/index.html", talles())


if __name__ == "__main__":
    main()
