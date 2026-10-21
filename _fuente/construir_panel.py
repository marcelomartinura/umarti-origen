#!/usr/bin/env python3
"""Genera el Panel de administración en panel/index.html

Uso:  python3 _fuente/construir_panel.py

El panel es una página privada (no aparece en Google) que lee y guarda en Supabase.
Las listas de categorías, temas y destinos salen de las mismas fuentes que el sitio.
"""
import json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "viajes"))
import comun  # noqa: E402
from comun import escribir  # noqa: E402
from construir_blog import CATEGORIAS  # noqa: E402
from destinos import DESTINOS, PAISES  # noqa: E402
from supabase_config import SUPABASE_URL, SUPABASE_KEY  # noqa: E402

cat = json.load(open(os.path.join(AQUI, "tienda", "catalogo.json"), encoding="utf-8"))
DATOS = {
    "supabase": {"url": SUPABASE_URL, "key": SUPABASE_KEY},
    "categorias": CATEGORIAS,
    "temas": [{"clave": t["clave"], "nombre": t["nombre"]} for t in cat.get("temas", [])],
    "destinos": [{"slug": d["slug"], "nombre": d["nombre"], "pais": PAISES[d["pais"]]["nombre"]} for d in DESTINOS],
    "paises": ["Argentina", "México", "Uruguay", "Paraguay", "Chile", "Brasil", "Otro"],
    "paises_envio": ["México", "Estados Unidos", "España", "Chile", "Uruguay", "Colombia", "Perú", "Canadá", "Brasil", "Italia", "Alemania"],
}

MODULOS = [("productos", "Productos", True), ("publicidad", "Publicidad", False), ("cupones", "Cupones", False),
           ("hub", "HUB", False), ("viajes", "Viajes", False)]

botonera = "".join(
    f'<button type="button" class="mod{" on" if activo else ""}" data-mod="{k}"{"" if activo else " disabled"}>{n}'
    f'{"" if activo else "<small>Pronto</small>"}</button>' for k, n, activo in MODULOS)

html = f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Panel · Umarti Origen</title>
  <meta name="robots" content="noindex, nofollow">
{comun.FUENTES}
  <link rel="stylesheet" href="../assets/css/panel.css">
</head>
<body>
  <header class="pn-top">
    <a class="pn-logo" href="../"><img src="../assets/img/marca/icono-blanco.png" alt="" width="259" height="236"><span>Umarti <span>Origen</span></span><small>Panel</small></a>
    <nav class="pn-mods" aria-label="Módulos">{botonera}</nav>
    <div class="pn-user" id="pn-user" hidden>
      <span id="pn-email"></span>
      <a href="../" target="_blank" rel="noopener">Ver sitio ↗</a>
      <button type="button" id="pn-salir">Salir</button>
    </div>
  </header>

  <main class="pn-main">
    <!-- Ingreso -->
    <section class="pn-login" id="v-login" hidden>
      <form class="card" id="f-login">
        <h1>Entrá al Panel</h1>
        <p class="muted" id="login-sub">Con tu correo y tu contraseña.</p>
        <label>Correo<input type="email" name="email" autocomplete="email" required></label>
        <label>Contraseña<input type="password" name="pass" autocomplete="current-password" minlength="8" required></label>
        <button class="btn pri" type="submit" id="login-btn">Entrar</button>
        <p class="msg" id="login-msg" role="status"></p>
        <p class="muted small"><button type="button" class="link" id="login-modo">¿Primera vez? Creá tu contraseña</button></p>
      </form>
    </section>

    <!-- Sin permiso -->
    <section class="pn-login" id="v-noadmin" hidden>
      <div class="card"><h1>Tu cuenta no tiene permiso</h1><p class="muted">Entraste como <b id="noadmin-email"></b>, pero esa cuenta no está habilitada para editar. Pedile al administrador que la agregue.</p><button class="btn" type="button" data-salir>Salir</button></div>
    </section>

    <!-- Lista de productos -->
    <section id="v-lista" hidden>
      <div class="pn-head">
        <div><h1>Productos</h1><p class="muted" id="l-resumen"></p></div>
        <button class="btn pri" type="button" id="b-nuevo">+ Nuevo producto</button>
      </div>
      <div class="pn-filtros">
        <input type="search" id="l-q" placeholder="Buscar por nombre, código o región" aria-label="Buscar">
        <div class="chips" id="l-estados" role="group" aria-label="Estado"></div>
        <select id="l-cat" aria-label="Categoría"><option value="">Todas las categorías</option></select>
      </div>
      <div class="pn-tabla" id="l-tabla"></div>
      <p class="pn-nota">Los cambios que guardás aparecen en el sitio en hasta 30 minutos. Solo se publican los productos en estado <b>Publicado</b> (y los de <b>Ejemplo</b>, mientras armás el catálogo).</p>
    </section>

    <!-- Editor -->
    <section id="v-editor" hidden>
      <div class="pn-head">
        <div>
          <button type="button" class="link back" id="e-volver">← Productos</button>
          <h1 id="e-titulo">Nuevo producto</h1>
          <p class="muted" id="e-sub"></p>
        </div>
      </div>
      <form id="f-prod" class="pn-editor" novalidate>
        <div class="pn-form">
          <fieldset class="card">
            <legend>Producto</legend>
            <label class="full"><span>Nombre <em>*</em></span><input name="nombre" required maxlength="90" placeholder="Por ejemplo: Mate de calabaza forrado en cuero"></label>
            <label class="full">Descripción<textarea name="descripcion" rows="3" maxlength="400" placeholder="Una o dos oraciones: material, origen, qué lo hace especial."></textarea><small class="count" data-for="descripcion"></small></label>
            <label><span>Categoría <em>*</em></span><select name="categoria" required></select></label>
            <label><span>Subcategoría <em>*</em></span><select name="subcategoria" required></select></label>
            <div class="full"><span class="lbl">Temas</span><div class="checks" id="e-temas"></div><small class="muted">El producto aparece también en la página de cada tema que marques.</small></div>
            <label>Vendedor<input name="vendedor" placeholder="Umarti Origen"></label>
            <label>Dirección en el sitio<span class="slug-wrap"><span>argentina/tienda/</span><input name="slug" required pattern="[a-z0-9-]+"><span>/</span></span></label>
          </fieldset>

          <fieldset class="card">
            <legend>Fotos</legend>
            <div class="fotos" id="e-fotos"></div>
            <label class="drop" id="e-drop">
              <input type="file" id="e-file" accept="image/jpeg,image/png,image/webp" multiple hidden>
              <b>Arrastrá las fotos acá o tocá para elegirlas</b>
              <small>JPG, PNG o WebP. Se achican solas a 1600 px. La primera es la principal: usá las flechas para ordenarlas.</small>
            </label>
          </fieldset>

          <fieldset class="card">
            <legend>Origen</legend>
            <label>País<select name="pais"></select></label>
            <label>Región o provincia<input name="region" placeholder="Por ejemplo: Misiones"></label>
            <label class="full">Guía de viaje relacionada<select name="destino"><option value="">Ninguna</option></select><small class="muted">Se muestra como "Conocé el origen" en la página del producto.</small></label>
          </fieldset>

          <fieldset class="card">
            <legend>Dónde se vende</legend>
            <div class="mercado" id="m-local">
              <div class="m-head">
                <label class="sw"><input type="checkbox" name="tienda_ar"><span></span><b>Mercado local</b></label>
                <small class="m-sub">Tienda Argentina · se vende y se envía dentro del país</small>
              </div>
              <label class="precio">Precio en pesos argentinos<span class="money"><i>$</i><input name="precio_ars" type="number" min="0" step="1" inputmode="decimal"><i>ARS</i></span></label>
              <p class="m-aviso" id="m-local-aviso" hidden></p>
            </div>
            <div class="mercado" id="m-intl">
              <div class="m-head">
                <label class="sw"><input type="checkbox" name="international"><span></span><b>Mercado internacional</b></label>
                <small class="m-sub">International Shop · envíos al exterior, incluido México</small>
              </div>
              <label class="precio">Precio en dólares<span class="money"><i>US$</i><input name="precio_usd" type="number" min="0" step="0.01" inputmode="decimal"><i>USD</i></span></label>
              <div class="full envio-intl"><span class="lbl">Países a los que enviás</span><div class="tags" id="e-paises"></div>
                <div class="tag-add"><input id="e-pais-nuevo" list="l-paises" placeholder="Agregar país"><datalist id="l-paises"></datalist><button type="button" class="btn sm" id="e-pais-add">Agregar</button></div></div>
            </div>
            <div class="mercado" id="m-hub">
              <div class="m-head">
                <label class="sw"><input type="checkbox" name="hub"><span></span><b>HUB</b></label>
                <small class="m-sub">Hub de Oportunidades · venta por volumen para exportar</small>
              </div>
              <div class="hub-campos">
                <label>Posición arancelaria<input name="hs" placeholder="Por ejemplo: 090300" inputmode="numeric"></label>
                <label>Volumen disponible<input name="volumen" placeholder="Por ejemplo: 20 toneladas por mes"></label>
                <label>Vigencia de la oferta<input name="vigencia_hub" type="date"></label>
              </div>
            </div>
            <label class="full">Link de pago (opcional)<input name="link_pago" type="url" placeholder="https://… (Mercado Pago, Stripe, etc.)"><small class="muted">Mientras no haya carrito, el botón Comprar lleva a este link.</small></label>
          </fieldset>
        </div>

        <aside class="pn-side">
          <div class="card pub">
            <label>Estado<select name="estado">
              <option value="Borrador">Borrador: no se ve en el sitio</option>
              <option value="Publicado">Publicado: visible en el sitio</option>
              <option value="Pausado">Pausado: oculto temporalmente</option>
              <option value="Ejemplo">Ejemplo: visible, marcado como ejemplo</option>
            </select></label>
            <button class="btn pri" type="submit" id="e-guardar">Guardar</button>
            <p class="msg" id="e-msg" role="status"></p>
            <div class="side-acts">
              <a class="link" id="e-ver" target="_blank" rel="noopener" hidden>Ver en el sitio ↗</a>
              <button type="button" class="link" id="e-duplicar" hidden>Duplicar</button>
              <button type="button" class="link danger" id="e-borrar" hidden>Eliminar</button>
            </div>
          </div>
          <div class="card prev">
            <span class="lbl">Así se ve en la Tienda</span>
            <div class="pv" id="e-preview"></div>
          </div>
          <div class="card check" id="e-check"></div>
        </aside>
      </form>
    </section>
  </main>

  <div class="toast" id="toast" role="status" aria-live="polite"></div>

  <script>window.PANEL = {json.dumps(DATOS, ensure_ascii=False)};</script>
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.min.js"></script>
  <script src="../assets/js/panel.js"></script>
</body>
</html>
'''

escribir("panel/index.html", html)
