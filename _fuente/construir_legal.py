#!/usr/bin/env python3
"""Genera las páginas legales: términos, privacidad, cookies y botón de arrepentimiento.

Uso:  python3 _fuente/construir_legal.py

IMPORTANTE: son borradores de trabajo. Completá DATOS con la información del titular del sitio
y hacé revisar los textos por un abogado antes de publicar. Mientras falte algún dato,
las páginas muestran un aviso de borrador.
"""
import html, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comun  # noqa: E402
from comun import escribir, DEFENSA_CONSUMIDOR  # noqa: E402

esc = html.escape

# ---------- datos del titular: completar ----------
DATOS = {
    "marca": "Umarti Origen",
    "razon_social": "",      # nombre de la persona o empresa titular
    "id_fiscal": "",         # CUIT (Argentina) o RFC (México)
    "domicilio": "",         # domicilio legal
    "email": "",             # correo para consultas legales y de privacidad
    "telefono": "",          # opcional
    "jurisdiccion": "los tribunales ordinarios de la Ciudad Autónoma de Buenos Aires, República Argentina",
    "actualizado": "2026-10-21",
}
FALTAN = [k for k in ("razon_social", "id_fiscal", "domicilio", "email") if not DATOS[k]]
NOMBRES = {"razon_social": "nombre o razón social del titular", "id_fiscal": "CUIT o RFC", "domicilio": "domicilio legal", "email": "correo de contacto"}


def d(k):
    if DATOS[k]:
        return esc(DATOS[k])
    return f'<mark class="falta">[completar: {NOMBRES.get(k, k)}]</mark>'


def page(slug, titulo, desc, cuerpo, toc):
    pre = "../../"
    aviso = ""
    if FALTAN:
        aviso = ('      <div class="draft-banner"><strong>Borrador legal.</strong> Faltan datos del titular ('
                 + ", ".join(NOMBRES[k] for k in FALTAN)
                 + '). Completalos y hacé revisar el texto por un abogado antes de publicar el sitio.</div>\n')
    indice = "".join(f'<li><a href="#{a}">{esc(t)}</a></li>' for a, t in toc)
    otras = [("terminos", "Términos y condiciones"), ("privacidad", "Política de privacidad"), ("cookies", "Política de cookies"), ("arrepentimiento", "Botón de arrepentimiento")]
    nav = "".join(f'<li><a href="../{s}/"{" aria-current=\"page\"" if s == slug else ""}>{t}</a></li>' for s, t in otras)
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(titulo)} | Umarti Origen</title>
  <meta name="description" content="{esc(desc)}">
{comun.FUENTES}
  <link rel="stylesheet" href="{pre}assets/css/umarti.css">
  <link rel="stylesheet" href="{pre}assets/css/blog.css">
  <link rel="stylesheet" href="{pre}assets/css/legal.css">
</head>
<body>

{comun.header(pre)}

  <main>
    <div class="wrap">
      <nav class="crumbs" aria-label="Ubicación"><ol><li><a href="{pre}">Inicio</a></li><li>Legal</li><li aria-current="page">{esc(titulo)}</li></ol></nav>
{aviso}      <header class="lg-head">
        <span class="eyebrow">Información legal</span>
        <h1>{esc(titulo)}</h1>
        <p class="muted">Última actualización: {comun.fecha_larga(DATOS["actualizado"])}</p>
      </header>
      <div class="lg-layout">
        <article class="prose lg-prose">
{cuerpo}
        </article>
        <aside class="lg-side">
          {f'<div class="box toc"><h2>En esta página</h2><ol>{indice}</ol></div>' if toc else ''}
          <div class="box"><h2>Legal</h2><ul class="mini-list">{nav}</ul></div>
        </aside>
      </div>
    </div>
  </main>

{comun.footer(pre)}

  <script src="{pre}assets/js/header.js"></script>{'''
  <script src="../../assets/js/legal.js"></script>''' if slug == "arrepentimiento" else ""}
</body>
</html>
'''


def secciones(items):
    """items: [(ancla, título, html)] -> (html, toc)"""
    out = "\n".join(f'          <h2 id="{a}">{esc(t)}</h2>\n{h}' for a, t, h in items)
    return out, [(a, t) for a, t, _ in items]


# ---------- Términos y condiciones ----------
def terminos():
    s, toc = secciones([
        ("titular", "Quiénes somos", f'''          <p>Este sitio, <b>{esc(DATOS["marca"])}</b>, es operado por {d("razon_social")}, {d("id_fiscal")}, con domicilio en {d("domicilio")}. Para cualquier consulta podés escribirnos a {d("email")}.</p>
          <p>Al usar el sitio aceptás estos términos. Si no estás de acuerdo con ellos, te pedimos que no lo uses.</p>'''),
        ("servicios", "Qué ofrece el sitio", '''          <ul>
            <li><b>Tienda:</b> venta de productos propios y de vendedores aliados, en el mercado local y en International Shop.</li>
            <li><b>Hub de Oportunidades:</b> un espacio para publicar y buscar productos y servicios de comercio exterior, con una Mesa de negociación.</li>
            <li><b>Cuponera:</b> descuentos de comercios aliados.</li>
            <li><b>Blog, Viajes y Recursos digitales:</b> contenido y herramientas de uso libre y gratuito.</li>
          </ul>'''),
        ("compras", "Compras en la Tienda", '''          <ul>
            <li><b>Precios:</b> los precios se muestran en la moneda de cada tienda e incluyen los impuestos que correspondan, salvo que se indique lo contrario. El costo de envío se informa antes de confirmar la compra.</li>
            <li><b>Disponibilidad:</b> las ventas están sujetas al stock disponible. Si un producto no está disponible después de tu compra, te avisamos y te devolvemos el dinero.</li>
            <li><b>Pago:</b> los pagos se procesan a través de plataformas de pago de terceros. No guardamos los datos de tu tarjeta.</li>
            <li><b>Envíos:</b> los plazos, costos y condiciones de cada zona están en la sección <a href="../../envios/">Envíos</a>.</li>
            <li><b>Productos de vendedores aliados:</b> cuando un producto lo vende un tercero, el nombre del vendedor figura en la página del producto. El vendedor es responsable del producto, de su descripción y de su garantía.</li>
          </ul>'''),
        ("arrepentimiento", "Derecho de arrepentimiento y devoluciones", f'''          <p>Si compraste a distancia (por internet), tenés derecho a arrepentirte de la compra dentro de los <b>10 días corridos</b> desde que recibiste el producto o desde que se celebró el contrato, lo último que ocurra, sin tener que dar explicaciones y sin costo, según el artículo 34 de la Ley 24.240 de Defensa del Consumidor y el artículo 1110 del Código Civil y Comercial de la Nación.</p>
          <p>Podés hacerlo desde el <a href="../arrepentimiento/">Botón de arrepentimiento</a>, sin necesidad de registrarte. Dentro de las 24 horas te enviamos un código de identificación de tu solicitud. El producto tiene que estar en las mismas condiciones en que lo recibiste. Los gastos de devolución corren por nuestra cuenta.</p>'''),
        ("garantia", "Garantía", '''          <p>Los productos nuevos tienen la garantía legal que establece la Ley 24.240 de Defensa del Consumidor. Si un producto llega dañado o con defectos, escribinos y lo resolvemos con un cambio, una reparación o la devolución del dinero.</p>'''),
        ("hub", "Hub de Oportunidades y Mesa de negociación", '''          <p>En el Hub, Umarti Origen pone en contacto a compradores y vendedores. Salvo que se acuerde lo contrario por escrito, no somos parte de las operaciones que surjan de ese contacto, no garantizamos su resultado y no intervenimos en los pagos. Cada parte es responsable de verificar a su contraparte, la mercadería, los permisos y las condiciones de la operación.</p>
          <p>Quien publica una oferta o una búsqueda declara que la información es verdadera y que tiene derecho a ofrecerla.</p>'''),
        ("cupones", "Cupones", '''          <p>Cada cupón tiene sus condiciones y su fecha de vencimiento, que figuran en el propio cupón. El comercio que lo ofrece es el responsable de respetarlo. Umarti Origen no responde por cambios o cancelaciones que el comercio haga sin aviso, aunque vamos a intervenir para ayudarte si eso pasa.</p>'''),
        ("herramientas", "Contenido y herramientas", '''          <p>Las notas, guías y calculadoras son informativas y de referencia. No reemplazan el asesoramiento de un profesional (contador, despachante de aduana, abogado). Las cotizaciones de monedas provienen de fuentes externas y pueden diferir de las de tu banco.</p>'''),
        ("afiliados", "Publicidad y enlaces de afiliados", '''          <p>El sitio puede mostrar avisos publicitarios y enlaces de afiliados. Si comprás a través de un enlace de afiliado, podemos recibir una comisión, sin costo adicional para vos. Los avisos y enlaces patrocinados se identifican como tales.</p>'''),
        ("propiedad", "Propiedad intelectual", '''          <p>Los textos, fotos, logos, diseños y herramientas del sitio pertenecen a Umarti Origen o a sus autores, y están protegidos por las leyes de propiedad intelectual. Podés compartir enlaces a nuestras páginas, pero no copiar el contenido sin autorización.</p>'''),
        ("responsabilidad", "Uso del sitio", '''          <p>Te comprometés a usar el sitio de buena fe: no publicar información falsa, no intentar acceder a áreas restringidas y no usarlo para actividades ilegales. Podemos dar de baja publicaciones que no cumplan estos términos.</p>
          <p>Hacemos lo posible para que el sitio funcione sin interrupciones y con información correcta, pero puede haber errores o demoras. Los corregimos apenas los detectamos.</p>'''),
        ("cambios", "Cambios en estos términos", '''          <p>Podemos actualizar estos términos. La fecha de la última actualización figura arriba. Los cambios no afectan a las compras ya realizadas.</p>'''),
        ("ley", "Ley aplicable y reclamos", f'''          <p>Estos términos se rigen por las leyes de la República Argentina. Para cualquier controversia son competentes {esc(DATOS["jurisdiccion"])}, sin perjuicio de los derechos que te otorga la ley de defensa del consumidor de elegir el tribunal de tu domicilio.</p>
          <p>Si tenés un reclamo, escribinos primero a {d("email")}. También podés iniciarlo en la <a href="{DEFENSA_CONSUMIDOR}" target="_blank" rel="noopener">Ventanilla Única Federal de Defensa de las y los Consumidores</a>.</p>'''),
    ])
    return page("terminos", "Términos y condiciones", "Condiciones de uso del sitio, compras, devoluciones, arrepentimiento, Hub de Oportunidades y cupones de Umarti Origen.", s, toc)


# ---------- Privacidad ----------
def privacidad():
    s, toc = secciones([
        ("responsable", "Responsable de tus datos", f'''          <p>El responsable de los datos personales que se recolectan en este sitio es {d("razon_social")}, {d("id_fiscal")}, con domicilio en {d("domicilio")}. Para cualquier consulta sobre tus datos escribinos a {d("email")}.</p>'''),
        ("datos", "Qué datos recolectamos", '''          <ul>
            <li><b>Datos que nos das:</b> nombre, correo, teléfono, empresa, país y mensajes, cuando completás un formulario (consultas, Mesa de negociación, publicación de productos, cupones o publicidad, botón de arrepentimiento).</li>
            <li><b>Datos de compra:</b> lo que compraste, la dirección de entrega y los datos necesarios para facturar. Los datos de tu tarjeta los procesa directamente la plataforma de pago; nosotros no los vemos ni los guardamos.</li>
            <li><b>Datos de navegación:</b> páginas visitadas, tipo de dispositivo y país aproximado, de forma agregada, a través de cookies y herramientas de medición (ver la <a href="../cookies/">Política de cookies</a>).</li>
            <li><b>Datos guardados en tu navegador:</b> tus favoritos se guardan solo en tu dispositivo y no nos llegan.</li>
          </ul>'''),
        ("finalidad", "Para qué los usamos", '''          <ul>
            <li>Responder tus consultas y gestionar tus compras, envíos, devoluciones y reclamos.</li>
            <li>Poner en contacto a compradores y vendedores en el Hub, cuando vos lo pedís.</li>
            <li>Mejorar el sitio a partir de estadísticas de uso.</li>
            <li>Enviarte novedades u ofertas, solo si nos diste tu consentimiento. Podés darte de baja en cualquier momento.</li>
          </ul>
          <p>No vendemos tus datos.</p>'''),
        ("terceros", "Con quién los compartimos", '''          <p>Solo con quienes nos ayudan a prestar el servicio y en la medida necesaria: proveedores de alojamiento y base de datos, plataformas de pago, empresas de envío, herramientas de medición y, en el Hub, la contraparte con la que pediste contactarte. Algunos de estos proveedores pueden almacenar datos fuera de tu país; en ese caso exigimos que los protejan con un nivel adecuado de seguridad.</p>
          <p>También podemos compartirlos si una autoridad competente lo exige por ley.</p>'''),
        ("conservacion", "Cuánto tiempo los guardamos", '''          <p>Mientras sean necesarios para la finalidad para la que los diste, y después durante los plazos que exigen las normas fiscales y de defensa del consumidor.</p>'''),
        ("derechos", "Tus derechos", f'''          <p>Podés pedir en cualquier momento <b>acceder</b> a tus datos, <b>rectificarlos</b>, <b>actualizarlos</b>, <b>cancelarlos o suprimirlos</b>, y <b>oponerte</b> a que los usemos con fines de publicidad. Escribinos a {d("email")} con tu nombre y lo que necesitás. Te respondemos dentro de los plazos legales.</p>
          <p><b>Si estás en Argentina:</b> el titular de los datos personales tiene la facultad de ejercer el derecho de acceso a ellos en forma gratuita a intervalos no inferiores a seis meses, salvo que se acredite un interés legítimo al efecto, conforme lo establecido en el artículo 14, inciso 3 de la Ley N° 25.326. La Agencia de Acceso a la Información Pública, en su carácter de Órgano de Control de la Ley N° 25.326, tiene la atribución de atender las denuncias y reclamos que interpongan quienes resulten afectados en sus derechos por incumplimiento de las normas vigentes en materia de protección de datos personales.</p>
          <p><b>Si estás en México:</b> podés ejercer tus derechos de acceso, rectificación, cancelación y oposición (derechos ARCO) en los términos de la Ley Federal de Protección de Datos Personales en Posesión de los Particulares, escribiendo al correo indicado.</p>'''),
        ("seguridad", "Seguridad", '''          <p>Usamos conexiones cifradas y proveedores con medidas de seguridad reconocidas. El acceso a la información está limitado a las personas que la necesitan para prestar el servicio.</p>'''),
        ("menores", "Menores de edad", '''          <p>El sitio no está dirigido a menores de 18 años. Si sos menor, pedile a una persona adulta que haga las compras o consultas por vos.</p>'''),
        ("cambios", "Cambios en esta política", '''          <p>Si cambiamos esta política, lo publicamos en esta página con la nueva fecha de actualización.</p>'''),
    ])
    return page("privacidad", "Política de privacidad", "Qué datos personales recolecta Umarti Origen, para qué los usa, con quién los comparte y cómo ejercer tus derechos en Argentina y México.", s, toc)


# ---------- Cookies ----------
def cookies():
    s, toc = secciones([
        ("que-son", "Qué son las cookies", '''          <p>Son pequeños archivos que un sitio guarda en tu navegador para recordar información, como tus preferencias o tu sesión. También usamos el almacenamiento local del navegador, que funciona de forma parecida.</p>'''),
        ("cuales", "Cuáles usamos", '''          <div class="table-wrap"><table>
            <thead><tr><th>Tipo</th><th>Para qué</th><th>Ejemplos</th></tr></thead>
            <tbody>
              <tr><td><b>Necesarias</b></td><td>Que el sitio funcione: recordar tus favoritos y mantener la sesión del panel de administración.</td><td>Favoritos de la Tienda, sesión del Panel</td></tr>
              <tr><td><b>De medición</b></td><td>Saber cuántas personas visitan cada página, de forma agregada, para mejorar el sitio.</td><td>Google Analytics (cuando se active)</td></tr>
              <tr><td><b>De publicidad</b></td><td>Mostrar avisos y medir su rendimiento.</td><td>Google AdSense u otras redes (cuando se activen)</td></tr>
              <tr><td><b>De afiliados</b></td><td>Que la tienda de destino sepa que llegaste desde nuestro enlace.</td><td>Enlaces de afiliados de tiendas y plataformas de viaje</td></tr>
            </tbody>
          </table></div>
          <p>Las de medición, publicidad y afiliados las colocan terceros, con sus propias políticas de privacidad.</p>'''),
        ("control", "Cómo controlarlas", '''          <p>Podés borrar o bloquear las cookies desde la configuración de tu navegador. Si bloqueás las necesarias, algunas funciones, como los favoritos, pueden dejar de funcionar.</p>'''),
    ])
    return page("cookies", "Política de cookies", "Qué cookies usa Umarti Origen y cómo podés controlarlas desde tu navegador.", s, toc)


# ---------- Botón de arrepentimiento ----------
def arrepentimiento():
    cuerpo = f'''          <p class="lead-lg">Si compraste en Umarti Origen y te arrepentiste, podés cancelar la compra dentro de los <b>10 días corridos</b> desde que recibiste el producto, sin dar explicaciones y sin costo.</p>
          <form class="arr-form" id="arr-form">
            <div class="arr-grid">
              <label>Nombre y apellido<input name="nombre" required autocomplete="name"></label>
              <label>Correo electrónico<input name="email" type="email" required autocomplete="email"></label>
              <label>Número de pedido<input name="pedido" required placeholder="Figura en el correo de tu compra"></label>
              <label>Fecha de compra<input name="fecha" type="date" required></label>
              <label class="full">Teléfono (opcional)<input name="tel" autocomplete="tel"></label>
              <label class="full">Comentario (opcional)<textarea name="comentario" rows="3"></textarea></label>
            </div>
            <button class="btn btn-primary" type="submit">Enviar solicitud de arrepentimiento</button>
            <div class="arr-ok" hidden role="status">
              <strong>Recibimos tu solicitud.</strong>
              <p>Dentro de las 24 horas te enviamos por correo el código de identificación de tu arrepentimiento y los pasos para la devolución. Si el producto ya te llegó, coordinamos el retiro sin costo.</p>
              <p class="muted small">Prototipo: el formulario todavía no envía datos.</p>
            </div>
          </form>
          <h2 id="como-funciona">Cómo funciona</h2>
          <ol>
            <li><b>Completás el formulario.</b> No hace falta registrarte ni tener una cuenta.</li>
            <li><b>Recibís un código.</b> Dentro de las 24 horas te enviamos por correo el código de identificación de tu solicitud.</li>
            <li><b>Devolvés el producto.</b> Tiene que estar en las mismas condiciones en que lo recibiste. Los gastos de devolución corren por nuestra cuenta.</li>
            <li><b>Te devolvemos el dinero</b> por el mismo medio de pago que usaste.</li>
          </ol>
          <p>Este derecho surge del artículo 34 de la Ley 24.240 de Defensa del Consumidor, del artículo 1110 del Código Civil y Comercial de la Nación y de la Resolución 424/2020 de la Secretaría de Comercio Interior.</p>
          <p>Si tenés un reclamo, también podés iniciarlo en la <a href="{DEFENSA_CONSUMIDOR}" target="_blank" rel="noopener">Ventanilla Única Federal de Defensa de las y los Consumidores</a>.</p>'''
    return page("arrepentimiento", "Botón de arrepentimiento", "Cancelá tu compra en Umarti Origen dentro de los 10 días corridos, sin registrarte y sin costo.", cuerpo, [])


def main():
    escribir("legal/terminos/index.html", terminos())
    escribir("legal/privacidad/index.html", privacidad())
    escribir("legal/cookies/index.html", cookies())
    escribir("legal/arrepentimiento/index.html", arrepentimiento())


if __name__ == "__main__":
    main()
