#!/usr/bin/env python3
"""Trae los cupones cargados en el Panel (Supabase) y actualiza _fuente/cupones/cupones.json

Uso:  python3 _fuente/cupones/importar_cupones.py            (lee desde Supabase)
      python3 _fuente/cupones/importar_cupones.py filas.json (usa un archivo con las filas ya descargadas)

Solo se traen los cupones Publicados o de Ejemplo.
"""
import json, os, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
from supabase_config import SUPABASE_URL, SUPABASE_KEY  # noqa: E402

SALIDA = os.path.join(AQUI, "cupones.json")
CAMPOS = ["codigo", "titulo", "comercio", "categoria", "tipo", "cupon", "descuento", "descripcion", "condiciones", "pais",
          "ciudad", "vence", "link", "destacado", "exclusivo", "destino", "tema", "estado", "slug"]


def descargar():
    url = f"{SUPABASE_URL}/rest/v1/cupones?select=*&estado=in.(Publicado,Ejemplo)&order=orden.asc,creado.asc"
    req = urllib.request.Request(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    filas = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else descargar()
    out = []
    for f in filas:
        if f.get("estado") not in ("Publicado", "Ejemplo"):
            continue
        c = {k: f.get(k) for k in CAMPOS}
        for k in ("cupon", "descripcion", "condiciones", "ciudad", "link", "destino", "tema", "slug", "descuento"):
            c[k] = c[k] or ""
        c["vence"] = (c["vence"] or "2099-12-31")[:10]
        c["destacado"] = bool(c["destacado"]); c["exclusivo"] = bool(c["exclusivo"])
        out.append(c)
    nuevo = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    viejo = open(SALIDA, encoding="utf-8").read() if os.path.exists(SALIDA) else ""
    if nuevo != viejo:
        open(SALIDA, "w", encoding="utf-8").write(nuevo)
        print(f"ok {len(out)} cupones -> actualizado")
    else:
        print(f"ok {len(out)} cupones -> sin cambios")


if __name__ == "__main__":
    main()
