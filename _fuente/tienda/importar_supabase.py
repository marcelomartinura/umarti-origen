#!/usr/bin/env python3
"""Trae los productos cargados en el Panel (Supabase) y actualiza _fuente/tienda/catalogo.json

Uso:  python3 _fuente/tienda/importar_supabase.py            (lee desde Supabase)
      python3 _fuente/tienda/importar_supabase.py filas.json (usa un archivo con las filas ya descargadas)

Solo se traen los productos en estado Publicado o Ejemplo. Los Borradores y Pausados quedan en el Panel.
Las pestañas Temas y Envíos siguen en catalogo.json sin cambios.
"""
import json, os, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
from supabase_config import SUPABASE_URL, SUPABASE_KEY  # noqa: E402

CATALOGO = os.path.join(AQUI, "catalogo.json")
CAMPOS = ["codigo", "nombre", "descripcion", "categoria", "subcategoria", "temas", "pais", "region", "destino",
          "precio_ars", "precio_mxn", "precio_usd", "tienda_ar", "tienda_mx", "international", "paises_envio",
          "hub", "hs", "volumen", "vigencia_hub", "link_pago", "fotos", "estado", "vendedor", "slug"]


def descargar():
    url = (f"{SUPABASE_URL}/rest/v1/productos?select=*&estado=in.(Publicado,Ejemplo)"
           "&order=orden.asc,creado.asc")
    req = urllib.request.Request(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def numero(v):
    if v in (None, ""):
        return None
    f = float(v)
    return int(f) if f.is_integer() else f


def convertir(fila):
    p = {k: fila.get(k) for k in CAMPOS}
    for k in ("precio_ars", "precio_mxn", "precio_usd"):
        p[k] = numero(p[k])
    for k in ("temas", "paises_envio", "fotos"):
        p[k] = p[k] or []
    for k in ("descripcion", "region", "destino", "hs", "volumen", "link_pago", "vendedor"):
        p[k] = p[k] or ""
    p["vigencia_hub"] = p["vigencia_hub"] or ""
    p["vendedor"] = p["vendedor"] or "Umarti Origen"
    return p


def main():
    filas = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else descargar()
    cat = json.load(open(CATALOGO, encoding="utf-8"))
    cat["productos"] = [convertir(f) for f in filas]
    nuevo = json.dumps(cat, ensure_ascii=False, indent=1)
    viejo = open(CATALOGO, encoding="utf-8").read()
    if nuevo.strip() != viejo.strip():
        open(CATALOGO, "w", encoding="utf-8").write(nuevo + "\n")
        print(f"ok {len(filas)} productos -> catálogo actualizado")
    else:
        print(f"ok {len(filas)} productos -> sin cambios")


if __name__ == "__main__":
    main()
