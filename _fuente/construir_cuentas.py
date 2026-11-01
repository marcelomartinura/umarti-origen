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
               (I_HAND, "Negociar en la Mesa", "Ofertas y contraofertas con condiciones claras. Próximamente.")],
        ingresar="Ingresar a mi empresa", crear="Registrar mi empresa",
        campos_crear=[("Razón social", "text", "organization"), ("Identificación fiscal (CUIT, RFC u otra)", "text", ""),
                      ("País", "pais", ""), ("Tu empresa es…", "rol", ""), ("Nombre de quien la representa", "text", "name"),
                      ("Correo", "email", "email"), ("Contraseña", "password", "new-password")],
        docs=["Documento de identidad de quien representa a la empresa", "Una selfie para confirmar que sos vos",
              "Constancia de inscripción fiscal de la empresa", "Si exportás: habilitaciones o certificados del producto"],
        otra=("mi-tienda/", "¿Vendés al público o tenés un comercio con cupones?", "Ir a Mi tienda"),
        publicar={"producto": "Para publicar un producto de exportación, ingresá o registrá tu empresa.",
                  "servicio": "Para ofrecer tus servicios, ingresá o registrá tu empresa."},
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


def main():
    escribir("mi-tienda/index.html", pagina("tienda"))
    escribir("mi-empresa/index.html", pagina("empresa"))


if __name__ == "__main__":
    main()
