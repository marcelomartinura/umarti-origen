"""Publicidad del sitio: los espacios (dónde aparece un aviso) y los avisos propios.

ESPACIOS: cada lugar del sitio donde puede ir publicidad, con un código fijo. Para cada uno se elige el modo:
  - "propio":  muestra un aviso de ANUNCIOS asignado a ese espacio (o la invitación "Anunciá en Umarti").
  - "adsense": muestra Google AdSense. Necesita ADSENSE_CLIENT (ca-pub-...) y el "adsense_slot" del bloque.
  - "codigo":  pega el código HTML que te da otra red o plataforma de venta de espacios (campo "codigo").
  - "apagado": no muestra nada.
Si un espacio en modo adsense o codigo todavía no tiene los datos cargados, muestra la invitación a anunciar.

ANUNCIOS: avisos propios o vendidos directamente. Se asignan a espacios con "espacios" (o con los formatos
viejos "en-nota" y "lateral" de las notas).

Campos:
  anunciante   nombre de la marca (se muestra como "Publicidad · <anunciante>")
  titulo       frase principal, corta
  texto        una oración
  imagen       ruta a la imagen (assets/img/publicidad/...) o vacío
  link         a dónde lleva el aviso (https://... o una página del sitio)
  cta          texto del botón ("Ver más", "Comprar", ...)
  espacios     códigos de ESPACIOS donde aparece (ej. ["nota-cabecera", "blog-portada-1"])
  formatos     (de antes) ["en-nota"] = nota-medio, ["lateral"] = nota-lateral
  categorias   categorías de la Tienda o temas de Negocios donde aparece; vacío = en todas las notas
  desde/hasta  fechas AAAA-MM-DD; vacío = sin límite
  activo       True o False
"""

ADSENSE_CLIENT = ""   # ej. "ca-pub-1234567890123456", cuando Google apruebe el sitio

ESPACIOS = {
    # código              nombre visible en el panel                  formato        modo
    "nota-cabecera":     dict(nombre="Nota · debajo del título",       formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "nota-medio":        dict(nombre="Nota · en medio del texto",      formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "nota-lateral":      dict(nombre="Nota · columna derecha",         formato="lateral",    modo="propio", adsense_slot="", codigo=""),
    "blog-portada-1":    dict(nombre="Blog · debajo de la destacada",  formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "blog-portada-2":    dict(nombre="Blog · antes de Opinión",        formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "recursos-portada":  dict(nombre="Recursos · portada",             formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "herramienta-1":     dict(nombre="Recursos · debajo de la herramienta", formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "herramienta-2":     dict(nombre="Recursos · columna derecha",     formato="lateral",    modo="propio", adsense_slot="", codigo=""),
    "viajes-1":          dict(nombre="Viajes · después de los destinos", formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "viajes-2":          dict(nombre="Viajes · después de Organizá tu viaje", formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "viajes-3":          dict(nombre="Viajes · al final",              formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "guia-1":            dict(nombre="Guía de destino · debajo de la presentación", formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "guia-2":            dict(nombre="Guía de destino · en medio de la guía", formato="horizontal", modo="propio", adsense_slot="", codigo=""),
    "guia-3":            dict(nombre="Guía de destino · al final de la página", formato="horizontal", modo="propio", adsense_slot="", codigo=""),
}

ANUNCIOS = [
    # {
    #     "anunciante": "Yerbatera Ejemplo",
    #     "titulo": "Yerba con estacionamiento natural",
    #     "texto": "Cosechada y estacionada en Misiones. Envíos a todo el país.",
    #     "imagen": "assets/img/publicidad/yerbatera.jpg",
    #     "link": "https://ejemplo.com",
    #     "cta": "Conocé la yerba",
    #     "formatos": ["en-nota", "lateral"],
    #     "categorias": ["Café, Té y Mate"],
    #     "desde": "2026-11-01", "hasta": "2026-12-31",
    #     "activo": True,
    # },
]
