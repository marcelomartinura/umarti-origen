#!/usr/bin/env python3
"""Genera las páginas de acceso para vendedores: mi-tienda/ (Tienda y Cupones) y mi-empresa/ (Mercados Globales).

Uso:  python3 _fuente/construir_cuentas.py
Por ahora es un prototipo: los formularios no crean cuentas. Cuando haya dominio, se conectan a Supabase Auth
y a la validación de identidad.
"""
import html, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comun  # noqa: E402
from comun import escribir  # noqa: E402

esc = html.escape
PRE = "../"


def ic(path, size=22):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>'


I_USER = '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>'
I_ID = '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2.5"/><path d="M6 16c.7-1.5 1.8-2 3-2s2.3.5 3 2M14 10h4M14 13h3"/>'
I_SHOP = '<path d="M3 9l2-5h14l2 5M4 9v11h16V9M3 9h18M9 20v-6h6v6"/>'
I_BOX = '<path d="M3 8l9-5 9 5v8l-9 5-9-5zM3 8l9 5 9-5M12 13v8"/>'
I_TAG = '<path d="M20 12l-8 8-9-9V3h8z"/><circle cx="7.5" cy="7.5" r="1.5"/>'
I_GLOBE = '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>'
I_CHART = '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'
I_SERV = '<path d="M14 7l3-3 3 3-3 3M17 4v7a4 4 0 0 1-4 4H4"/><path d="M7 12l-3 3 3 3"/>'
I_SEARCH = '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>'
I_HAND = '<path d="M7 11l3-3 4 4 3-3 4 4-6 6-4-4-3 3-4-4z"/>'
I_CHECK = '<path d="m5 12 5 5 9-10"/>'

CONF = {
    "tienda": dict(
        ruta="mi-tienda/", modulo="Tienda", color="terra", titulo="Mi tienda",
        h1="Vendé con Umarti Origen",
        lead="Abrí tu tienda dentro de Umarti: publicá tus productos en la Tienda Argentina y en International Shop, y sumá cupones de tu comercio a la Cuponera.",
        puede=[(I_BOX, "Publicar tus productos", "En la Tienda Argentina, con fotos, precios y stock."),
               (I_GLOBE, "Vender al exterior", "Marcá qué productos van a International Shop y a qué países llegan."),
               (I_TAG, "Publicar cupones", "Descuentos de tu comercio en la Cuponera."),
               (I_CHART, "Seguir tus ventas", "Pedidos, consultas y favoritos de tus productos.")],
        ingresar="Ingresar a mi tienda", crear="Crear mi tienda",
        campos_crear=[("Nombre y apellido", "text", "name"), ("Nombre de tu tienda o marca", "text", "organization"),
                      ("País", "pais", ""), ("Correo", "email", "email"), ("Contraseña", "password", "new-password")],
        docs=["Documento de identidad (DNI, INE o pasaporte)", "Una selfie para confirmar que sos vos",
              "Tu identificación fiscal (CUIT, RFC o la de tu país)"],
        otra=("mi-empresa/", "¿Tu empresa exporta, importa o brinda servicios de comercio exterior?", "Ir a Mi empresa"),
        publicar={"cupon": "Para publicar tu cupón, ingresá o creá tu tienda."},
    ),
    "empresa": dict(
        ruta="mi-empresa/", modulo="Mercados Globales", color="sky", titulo="Mi empresa",
        h1="Tu empresa en Mercados Globales",
        lead="Registrá tu empresa para publicar productos de exportación, ofrecer servicios de comercio exterior y responder a las búsquedas de compradores de todo el mundo.",
        puede=[(I_BOX, "Publicar productos de exportación", "Con posición arancelaria, volumen y países de destino."),
               (I_SERV, "Ofrecer servicios", "Aduana, logística, seguros, certificaciones o asesoría."),
               (I_SEARCH, "Publicar búsquedas", "Pedí lo que necesitás en Oportunidades Globales."),
               (I_HAND, "Negociar en la Mesa", "Ofertas y contraofertas con condiciones claras. Próximamente."),
               (I_GLOBE, "Publicar servicios de viaje", "Alojamientos, excursiones, traslados y alquiler de autos en Umarti Viajes.")],
        ingresar="Ingresar a mi empresa", crear="Registrar mi empresa",
        campos_crear=[("Razón social", "text", "organization"), ("Identificación fiscal (CUIT, RFC u otra)", "text", ""),
                      ("País", "pais", ""), ("Tu empresa es…", "rol", ""), ("Nombre de quien la representa", "text", "name"),
                      ("Correo", "email", "email"), ("Contraseña", "password", "new-password")],
        docs=["Documento de identidad de quien representa a la empresa", "Una selfie para confirmar que sos vos",
              "Constancia de inscripción fiscal de la empresa", "Si exportás: habilitaciones o certificados del producto"],
        otra=("mi-tienda/", "¿Vendés al público o tenés un comercio con cupones?", "Ir a Mi tienda"),
        publicar={"producto": "Para publicar un producto de exportación, ingresá o registrá tu empresa.",
                  "empresa": "Para crear la página de tu empresa exportadora, ingresá o registrá tu empresa.",
                  "servicio": "Para ofrecer tus servicios, ingresá o registrá tu empresa.",
                  "viajes": "Para publicar tu alojamiento, excursión, traslado o alquiler de autos en Umarti Viajes, ingresá o registrá tu empresa."},
    ),
}
PAISES = ["Argentina", "México", "Chile", "Uruguay", "Colombia", "Perú", "Brasil", "España", "Estados Unidos", "Otro"]
ROLES = ["Productora o exportadora", "Importadora o compradora", "Proveedora de servicios de comercio exterior"]


def campo(i, lbl, tipo, auto):
    fid = f"c-{i}"
    if tipo == "pais":
        ctrl = f'<select id="{fid}" required><option value="">Elegí</option>{"".join(f"<option>{p}</option>" for p in PAISES)}</select>'
    elif tipo == "rol":
        ctrl = f'<select id="{fid}" required><option value="">Elegí</option>{"".join(f"<option>{r}</option>" for r in ROLES)}</select>'
    else:
        extra = ' minlength="8"' if tipo == "password" else ""
        ctrl = f'<input id="{fid}" type="{tipo}" required{extra}{f" autocomplete={chr(34)}{auto}{chr(34)}" if auto else ""}>'
    return f'<label class="ac-f" for="{fid}">{esc(lbl)}{ctrl}</label>'


def pagina(k):
    c = CONF[k]
    pasos = [(I_USER, "Creá tu cuenta", "Con tu correo y una contraseña."),
             (I_ID, "Validá tu identidad", "Para que todos sepan con quién están tratando."),
             (I_SHOP if k == "tienda" else I_GLOBE, "Publicá", "Tus publicaciones pasan por una revisión rápida y salen al aire.")]
    pasos_html = "".join(f'<li><span class="ac-n">{i + 1}</span><span class="ac-ic">{ic(p)}</span><div><b>{t}</b><small>{d}</small></div></li>' for i, (p, t, d) in enumerate(pasos))
    puede = "".join(f'<div class="ac-can"><span>{ic(p, 20)}</span><div><b>{t}</b><small>{d}</small></div></div>' for p, t, d in c["puede"])
    docs = "".join(f'<li>{ic(I_CHECK, 16)}{esc(x)}</li>' for x in c["docs"])
    crear = "".join(campo(i, *f) for i, f in enumerate(c["campos_crear"]))
    avisos = "".join(f'<p class="ac-aviso" data-publicar="{q}" hidden>{esc(t)}</p>' for q, t in c["publicar"].items())
    otra_url, otra_txt, otra_btn = c["otra"]
    main = f'''    <div class="wrap ac-wrap ac-{c['color']}">
      <nav class="crumbs" aria-label="Ubicación"><ol><li><a href="{PRE}">Inicio</a></li><li>{c['modulo']}</li><li aria-current="page">{c['titulo']}</li></ol></nav>
      <div class="ac-grid">
        <section class="ac-info">
          <span class="eyebrow">{c['modulo']} · {c['titulo']}</span>
          <h1>{c['h1']}</h1>
          <p class="ac-lead">{c['lead']}</p>
          <ol class="ac-pasos">{pasos_html}</ol>
          <h2>Qué vas a poder hacer</h2>
          <div class="ac-cans">{puede}</div>
          <div class="ac-docs">
            <b>{ic(I_ID, 18)} Para validar tu identidad vas a necesitar</b>
            <ul>{docs}</ul>
            <small>Tus documentos se usan solo para verificar tu identidad y no se publican. <a href="{PRE}legal/privacidad/">Política de privacidad</a>.</small>
          </div>
        </section>

        <aside class="ac-card" id="acceso">
          {avisos}
          <div class="ac-tabs" role="tablist">
            <button type="button" role="tab" aria-selected="true" data-tab="in">{c['ingresar']}</button>
            <button type="button" role="tab" aria-selected="false" data-tab="up">{c['crear']}</button>
          </div>
          <form class="ac-form" data-panel="in" novalidate>
            <label class="ac-f" for="in-mail">Correo<input id="in-mail" type="email" required autocomplete="email"></label>
            <label class="ac-f" for="in-pass">Contraseña<input id="in-pass" type="password" required autocomplete="current-password"></label>
            <button class="ac-btn" type="submit">{c['ingresar']}</button>
            <a class="ac-link" href="#" data-olvide>¿Olvidaste tu contraseña?</a>
          </form>
          <form class="ac-form" data-panel="up" hidden novalidate>
            {crear}
            <label class="ac-chk"><input type="checkbox" required> Acepto los <a href="{PRE}legal/terminos/">términos</a> y la <a href="{PRE}legal/privacidad/">política de privacidad</a>.</label>
            <button class="ac-btn" type="submit">{c['crear']}</button>
          </form>
          <div class="ac-ok" hidden>
            <span class="ac-tick">{ic(I_CHECK, 28)}</span>
            <h2 data-ok-t></h2>
            <p data-ok-p></p>
            <ol class="ac-next">
              <li class="hecho"><b>Cuenta creada</b></li>
              <li><b>Validación de identidad</b><small>Te va a llegar un correo con el enlace para subir tus documentos.</small></li>
              <li><b>Publicar</b><small>Una vez validada tu identidad, ya podés publicar.</small></li>
            </ol>
            <button class="ac-btn ghost" type="button" data-volver>Volver</button>
          </div>
          <p class="ac-proto">Prototipo: por ahora no se crean cuentas ni se envían datos.</p>
        </aside>
      </div>
      <a class="ac-otra" href="{PRE}{otra_url}"><span>{esc(otra_txt)}</span><b>{otra_btn} →</b></a>
    </div>'''
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{c['titulo']}: ingresá o creá tu cuenta | Umarti Origen</title>
  <meta name="description" content="{esc(c['lead'])}">
  <meta name="robots" content="noindex">
{comun.FUENTES}
  <link rel="stylesheet" href="{PRE}assets/css/umarti.css">
  <link rel="stylesheet" href="{PRE}assets/css/blog.css">
  <link rel="stylesheet" href="{PRE}assets/css/cuentas.css">
</head>
<body data-cuenta="{k}">

{comun.header(PRE).replace(f'href="{PRE}{c["ruta"]}"', f'href="{PRE}{c["ruta"]}" aria-current="page"')}

  <main>
{main}
  </main>

{comun.footer(PRE)}

  <script src="{PRE}assets/js/header.js"></script>
  <script src="{PRE}assets/js/cuentas.js"></script>
</body>
</html>
'''


I_HEART = '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>'
I_CART = '<path d="M3 4h2l2.4 11.2a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 2-1.5L21 8H6.2"/><circle cx="10" cy="20.5" r="1.2"/><circle cx="17" cy="20.5" r="1.2"/>'
I_PIN = '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>'
I_LOCK = '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>'
I_HOME = '<path d="M3 11l9-7 9 7M5 10v10h14V10"/>'


def pagina_cliente():
    """Mi cuenta: para compradores de la Tienda y usuarios de la Cuponera (Supabase Auth)."""
    from supabase_config import SUPABASE_URL, SUPABASE_KEY
    beneficios = [(I_HEART, "Tus favoritos en todos tus dispositivos", "Guardá productos y encontralos en la compu o en el celular."),
                  (I_BOX, "Tus pedidos en un solo lugar", "Seguí el estado de tus compras en la Tienda."),
                  (I_TAG, "Cupones guardados", "Guardá descuentos de la Cuponera para usarlos después."),
                  (I_PIN, "Comprá más rápido", "Tus datos de envío quedan listos para la próxima compra.")]
    ben = "".join(f'<div class="ac-can"><span>{ic(p, 20)}</span><div><b>{t}</b><small>{d}</small></div></div>' for p, t, d in beneficios)
    paises = "".join(f"<option>{p}</option>" for p in PAISES)
    tabs = [("resumen", I_HOME, "Resumen"), ("pedidos", I_BOX, "Mis pedidos"), ("favoritos", I_HEART, "Favoritos"),
            ("cupones", I_TAG, "Mis cupones"), ("datos", I_USER, "Mis datos"), ("seguridad", I_LOCK, "Seguridad")]
    nav = "".join(f'<a href="#{k}" data-sec="{k}">{ic(i, 18)}<span>{t}</span></a>' for k, i, t in tabs)
    main = f'''    <div class="wrap ac-wrap ac-sun">
      <nav class="crumbs" aria-label="Ubicación"><ol><li><a href="{PRE}">Inicio</a></li><li aria-current="page">Mi cuenta</li></ol></nav>

      <p class="mc-cargando" id="mc-cargando">Cargando tu cuenta…</p>

      <!-- Sin sesión: ingresar o crear cuenta -->
      <div class="ac-grid" id="mc-fuera" hidden>
        <section class="ac-info">
          <span class="eyebrow">Mi cuenta</span>
          <h1>Tu cuenta en Umarti Origen</h1>
          <p class="ac-lead">Para quienes compran en la Tienda y usan la Cuponera. Creá tu cuenta gratis con tu correo.</p>
          <div class="ac-cans">{ben}</div>
          <div class="mc-vende">
            <b>¿Vendés o tenés una empresa?</b>
            <span>Las cuentas para vender son otras: <a href="{PRE}mi-tienda/">Mi tienda</a> (productos y cupones) o <a href="{PRE}mi-empresa/">Mi empresa</a> (comercio exterior).</span>
          </div>
        </section>

        <aside class="ac-card" id="acceso">
          <p class="ac-aviso" id="mc-aviso" hidden></p>
          <div class="ac-tabs" role="tablist">
            <button type="button" role="tab" aria-selected="true" data-tab="in">Ingresar</button>
            <button type="button" role="tab" aria-selected="false" data-tab="up">Crear cuenta</button>
          </div>
          <form class="ac-form" data-panel="in" novalidate>
            <label class="ac-f">Correo<input name="email" type="email" required autocomplete="email"></label>
            <label class="ac-f">Contraseña<input name="pass" type="password" required autocomplete="current-password"></label>
            <button class="ac-btn" type="submit">Ingresar</button>
            <button class="ac-link" type="button" data-ir="olvide">¿Olvidaste tu contraseña?</button>
            <p class="mc-msg" role="status"></p>
          </form>
          <form class="ac-form" data-panel="up" hidden novalidate>
            <label class="ac-f">Nombre<input name="nombre" required autocomplete="given-name" maxlength="60"></label>
            <label class="ac-f">País<select name="pais" required><option value="">Elegí</option>{paises}</select></label>
            <label class="ac-f">Correo<input name="email" type="email" required autocomplete="email"></label>
            <label class="ac-f">Contraseña<input name="pass" type="password" required minlength="8" autocomplete="new-password"><small class="muted">Mínimo 8 caracteres.</small></label>
            <label class="ac-chk"><input type="checkbox" name="novedades"> Quiero recibir novedades, ofertas y cupones nuevos.</label>
            <label class="ac-chk"><input type="checkbox" required> Acepto los <a href="{PRE}legal/terminos/">términos</a> y la <a href="{PRE}legal/privacidad/">política de privacidad</a>.</label>
            <button class="ac-btn" type="submit">Crear mi cuenta</button>
            <p class="mc-msg" role="status"></p>
          </form>
          <form class="ac-form" data-panel="olvide" hidden novalidate>
            <h2 class="mc-h">Recuperá tu contraseña</h2>
            <p class="muted">Te mandamos un enlace a tu correo para elegir una nueva.</p>
            <label class="ac-f">Correo<input name="email" type="email" required autocomplete="email"></label>
            <button class="ac-btn" type="submit">Enviar enlace</button>
            <button class="ac-link" type="button" data-ir="in">← Volver a ingresar</button>
            <p class="mc-msg" role="status"></p>
          </form>
          <form class="ac-form" data-panel="nueva" hidden novalidate>
            <h2 class="mc-h">Elegí tu nueva contraseña</h2>
            <label class="ac-f">Nueva contraseña<input name="pass" type="password" required minlength="8" autocomplete="new-password"></label>
            <button class="ac-btn" type="submit">Guardar contraseña</button>
            <p class="mc-msg" role="status"></p>
          </form>
          <div class="ac-ok" data-panel="revisa" hidden>
            <span class="ac-tick">{ic(I_CHECK, 28)}</span>
            <h2>Revisá tu correo</h2>
            <p>Te mandamos un enlace a <b data-mail></b> para confirmar tu cuenta. Si no lo ves, fijate en correo no deseado.</p>
            <button class="ac-btn ghost" type="button" data-reenviar>Reenviar el correo</button>
            <button class="ac-link" type="button" data-ir="in">Ya lo confirmé: ingresar</button>
          </div>
        </aside>
      </div>

      <!-- Con sesión: panel del comprador -->
      <div class="mc-panel" id="mc-dentro" hidden>
        <aside class="mc-side">
          <div class="mc-yo"><span class="mc-av" data-iniciales></span><div><b data-nombre></b><small data-mail></small></div></div>
          <nav class="mc-nav" aria-label="Secciones de mi cuenta">{nav}</nav>
          <button class="mc-salir" type="button" data-salir>Cerrar sesión</button>
        </aside>
        <div class="mc-main">
          <section data-panel-sec="resumen">
            <h1 class="mc-hola">Hola, <span data-nombre-corto></span></h1>
            <p class="muted">Desde acá ves tus pedidos, favoritos y cupones, y cambiás tus datos.</p>
            <div class="mc-tiles">
              <a class="mc-tile" href="#pedidos"><span>{ic(I_BOX, 22)}</span><b data-n="pedidos">0</b><small>Pedidos</small></a>
              <a class="mc-tile" href="{PRE}favoritos/"><span>{ic(I_HEART, 22)}</span><b data-n="favoritos">0</b><small>Favoritos</small></a>
              <a class="mc-tile" href="{PRE}carrito/"><span>{ic(I_CART, 22)}</span><b data-n="carrito">0</b><small>En el carrito</small></a>
              <a class="mc-tile" href="#cupones"><span>{ic(I_TAG, 22)}</span><b data-n="cupones">0</b><small>Cupones</small></a>
            </div>
            <div class="mc-completa" data-completa hidden>
              <div><b>Completá tus datos de envío</b><small>Así la próxima compra es más rápida.</small></div>
              <a class="ac-btn" href="#datos">Completar</a>
            </div>
            <div class="mc-atajos">
              <a href="{PRE}argentina/tienda/"><b>Tienda Argentina</b><small>Productos con origen</small></a>
              <a href="{PRE}international-shop/"><b>International Shop</b><small>Envíos al mundo</small></a>
              <a href="{PRE}cupones/"><b>Cuponera</b><small>Descuentos de comercios</small></a>
              <a href="{PRE}viajes/"><b>Viajes</b><small>Guías de destinos</small></a>
            </div>
          </section>

          <section data-panel-sec="pedidos" hidden>
            <h1>Mis pedidos</h1>
            <div class="mc-vacio">{ic(I_BOX, 40)}<h2>Todavía no hiciste compras</h2><p>Cuando compres en la Tienda, vas a ver acá el estado de cada pedido y su seguimiento.</p><a class="ac-btn" href="{PRE}argentina/tienda/">Ir a la Tienda</a></div>
          </section>

          <section data-panel-sec="favoritos" hidden>
            <h1>Favoritos</h1>
            <p class="muted mc-fav-txt"></p>
            <div class="mc-vacio" data-fav-vacio>{ic(I_HEART, 40)}<h2>Todavía no guardaste favoritos</h2><p>Tocá el corazón en cualquier producto para guardarlo. Con tu cuenta, tus favoritos te siguen en todos tus dispositivos.</p><a class="ac-btn" href="{PRE}argentina/tienda/">Explorar la Tienda</a></div>
            <a class="ac-btn" data-fav-ver href="{PRE}favoritos/" hidden>Ver mis favoritos</a>
          </section>

          <section data-panel-sec="cupones" hidden>
            <h1>Mis cupones</h1>
            <div class="mc-vacio">{ic(I_TAG, 40)}<h2>La Cuponera abre muy pronto</h2><p>Estamos sumando los primeros comercios. Cuando haya cupones, vas a poder guardarlos acá{'<span data-nov> y, como pediste recibir novedades, te avisamos por correo</span>'}.</p><a class="ac-btn ghost" href="{PRE}cupones/">Conocé la Cuponera</a></div>
          </section>

          <section data-panel-sec="datos" hidden>
            <h1>Mis datos</h1>
            <form class="mc-form" id="mc-datos" novalidate>
              <fieldset><legend>Datos personales</legend>
                <label class="ac-f">Nombre<input name="nombre" maxlength="60" autocomplete="given-name"></label>
                <label class="ac-f">Apellido<input name="apellido" maxlength="60" autocomplete="family-name"></label>
                <label class="ac-f">Teléfono<input name="telefono" type="tel" maxlength="30" autocomplete="tel" placeholder="+54 9 11 …"></label>
                <label class="ac-f">País<select name="pais"><option value="">Elegí</option>{paises}</select></label>
              </fieldset>
              <fieldset><legend>Dirección de envío</legend>
                <label class="ac-f full">Calle y número<input name="calle" maxlength="120" autocomplete="address-line1"></label>
                <label class="ac-f">Piso / depto.<input name="depto" maxlength="40" autocomplete="address-line2"></label>
                <label class="ac-f">Código postal<input name="cp" maxlength="12" autocomplete="postal-code"></label>
                <label class="ac-f">Ciudad<input name="ciudad" maxlength="80" autocomplete="address-level2"></label>
                <label class="ac-f">Provincia o estado<input name="provincia" maxlength="80" autocomplete="address-level1"></label>
                <label class="ac-f full">Indicaciones para la entrega<input name="indicaciones" maxlength="160" placeholder="Ej.: timbre B, dejar en portería"></label>
              </fieldset>
              <fieldset><legend>Preferencias</legend>
                <label class="ac-f">Tienda<select name="tienda"><option value="AR">Tienda Argentina</option><option value="MX" disabled>Tienda México (próximamente)</option></select></label>
                <label class="ac-chk full"><input type="checkbox" name="novedades"> Quiero recibir novedades, ofertas y cupones nuevos.</label>
              </fieldset>
              <div class="mc-foot"><button class="ac-btn" type="submit">Guardar cambios</button><p class="mc-msg" role="status"></p></div>
            </form>
          </section>

          <section data-panel-sec="seguridad" hidden>
            <h1>Seguridad</h1>
            <form class="mc-form" id="mc-clave" novalidate>
              <fieldset><legend>Cambiar contraseña</legend>
                <label class="ac-f">Nueva contraseña<input name="pass" type="password" minlength="8" required autocomplete="new-password"></label>
                <label class="ac-f">Repetila<input name="pass2" type="password" minlength="8" required autocomplete="new-password"></label>
              </fieldset>
              <div class="mc-foot"><button class="ac-btn" type="submit">Cambiar contraseña</button><p class="mc-msg" role="status"></p></div>
            </form>
            <div class="mc-box"><b>Correo de la cuenta</b><span data-mail></span></div>
            <div class="mc-box"><b>¿Querés dar de baja tu cuenta?</b><span>Escribinos desde el correo de tu cuenta y la eliminamos junto con tus datos.</span></div>
            <button class="ac-btn ghost" type="button" data-salir>Cerrar sesión</button>
          </section>
        </div>
      </div>
    </div>'''
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mi cuenta | Umarti Origen</title>
  <meta name="description" content="Ingresá o creá tu cuenta en Umarti Origen para guardar favoritos, seguir tus pedidos y usar la Cuponera.">
  <meta name="robots" content="noindex">
{comun.FUENTES}
  <link rel="stylesheet" href="{PRE}assets/css/umarti.css">
  <link rel="stylesheet" href="{PRE}assets/css/blog.css">
  <link rel="stylesheet" href="{PRE}assets/css/cuentas.css">
</head>
<body data-cuenta="cliente" data-sb-url="{SUPABASE_URL}" data-sb-key="{SUPABASE_KEY}">

{comun.header(PRE)}

  <main>
{main}
  </main>

{comun.footer(PRE)}

  <script src="{PRE}assets/js/header.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.min.js"></script>
  <script src="{PRE}assets/js/mi-cuenta.js"></script>
</body>
</html>
'''


def main():
    escribir("mi-tienda/index.html", pagina("tienda"))
    escribir("mi-empresa/index.html", pagina("empresa"))
    escribir("mi-cuenta/index.html", pagina_cliente())


if __name__ == "__main__":
    main()
