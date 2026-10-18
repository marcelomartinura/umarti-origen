"""Espacios de publicidad del blog.

Cada nota tiene dos espacios:
  - "en-nota": horizontal, en el medio del texto.
  - "lateral": en la columna de la derecha (abajo de la nota en el celular).

Para publicar un aviso, agregá un diccionario a ANUNCIOS. Si un espacio no tiene aviso,
se muestra la invitación "Anunciá en Umarti".

Campos:
  anunciante   nombre de la marca (se muestra como "Publicidad · <anunciante>")
  titulo       frase principal, corta
  texto        una oración
  imagen       ruta a la imagen (assets/img/publicidad/...) o vacío
  link         a dónde lleva el aviso (https://... o una página del sitio)
  cta          texto del botón ("Ver más", "Comprar", ...)
  formatos     ["en-nota"], ["lateral"] o los dos
  categorias   categorías de la Tienda o temas de Negocios donde aparece; vacío = en todas las notas
  desde/hasta  fechas AAAA-MM-DD; vacío = sin límite
  activo       True o False
"""

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
