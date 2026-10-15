#!/usr/bin/env python3
"""Convierte las pestañas Catálogo y Temas de la hoja 'Plan Ecommerce' en _fuente/tienda/catalogo.json

Uso:  python3 _fuente/tienda/importar_hoja.py catalogo_valores.json temas_valores.json envios_valores.json
Cada archivo es la respuesta de leer los valores de la pestaña desde la fila de encabezados
(rangos 'Catálogo'!A4:X, 'Temas'!A4:F y 'Envíos'!A4:H), con la forma {"values": [[encabezados], [fila], ...]}.
"""
import json, os, sys, unicodedata, re

AQUI = os.path.dirname(os.path.abspath(__file__))

CAMPOS_CATALOGO = {
    "Código": "codigo", "Producto": "nombre", "Descripción corta": "descripcion", "Categoría": "categoria",
    "Subcategoría": "subcategoria", "Temas": "temas", "País de origen": "pais", "Región de origen": "region",
    "Destino en Viajes": "destino", "Precio ARS": "precio_ars", "Precio MXN": "precio_mxn",
    "Precio USD (International Shop)": "precio_usd", "Tienda Argentina": "tienda_ar", "Tienda México": "tienda_mx",
    "International Shop": "international", "Países de envío internacional": "paises_envio",
    "Hub de Oportunidades": "hub", "Posición arancelaria": "hs", "Volumen para exportar": "volumen",
    "Vigencia en el Hub": "vigencia_hub", "Link de pago": "link_pago", "Foto (URL)": "fotos", "Fotos (URLs separadas por coma)": "fotos", "Estado": "estado",
    "Vendedor": "vendedor",
}
CAMPOS_ENVIOS = {"Zona": "zona", "Plazo de entrega": "plazo", "Costo de envío": "costo", "Transportista": "transportista",
                 "Seguimiento": "seguimiento", "Cambios y devoluciones": "devoluciones", "Impuestos y aduana": "impuestos", "Estado": "estado"}
CAMPOS_TEMAS = {"Clave": "clave", "Nombre": "nombre", "Bajada": "bajada", "Etiquetas del blog": "etiquetas",
                "Destinos en Viajes": "destinos", "Estado": "estado"}


def slug(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def lista(v):
    return [x.strip() for x in (v or "").split(",") if x.strip()]


def numero(v):
    v = (v or "").replace("$", "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(v) if "." in v else int(v)
    except ValueError:
        return None


def filas(path, campos):
    vals = json.load(open(path, encoding="utf-8")).get("values", [])
    if not vals:
        return []
    head = [campos.get(h.strip()) for h in vals[0]]
    out = []
    for r in vals[1:]:
        d = {k: (r[i].strip() if i < len(r) else "") for i, k in enumerate(head) if k}
        if any(d.values()):
            out.append(d)
    return out


def main(cat_path, tem_path, env_path=None):
    productos = []
    for d in filas(cat_path, CAMPOS_CATALOGO):
        if d.get("estado") not in ("Publicado", "Ejemplo") or not d.get("nombre"):
            continue
        for k in ("precio_ars", "precio_mxn", "precio_usd"):
            d[k] = numero(d.get(k))
        for k in ("tienda_ar", "tienda_mx", "international", "hub"):
            d[k] = d.get(k) == "Sí"
        d["temas"] = [slug(t) for t in lista(d.get("temas"))]
        d["paises_envio"] = lista(d.get("paises_envio"))
        d["hs"] = re.sub(r"\D", "", d.get("hs", ""))
        d["fotos"] = lista(d.get("fotos"))
        d["vendedor"] = d.get("vendedor") or "Umarti Origen"
        d["slug"] = slug(d["nombre"])
        productos.append(d)
    temas = []
    for t in filas(tem_path, CAMPOS_TEMAS):
        if t.get("estado") != "Publicado":
            continue
        t["clave"] = slug(t["clave"])
        t["etiquetas"] = lista(t.get("etiquetas"))
        t["destinos"] = lista(t.get("destinos"))
        temas.append(t)
    envios = []
    if env_path:
        for e in filas(env_path, CAMPOS_ENVIOS):
            e["slug"] = slug(e["zona"])
            envios.append(e)
    out = os.path.join(AQUI, "catalogo.json")
    json.dump({"productos": productos, "temas": temas, "envios": envios}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"ok {len(productos)} productos, {len(temas)} temas y {len(envios)} zonas de envío -> {os.path.relpath(out)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
