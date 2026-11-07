#!/usr/bin/env python3
"""Trae los destinos cargados en el Panel (Supabase) y actualiza _fuente/viajes/destinos_panel.json

Uso:  python3 _fuente/viajes/importar_destinos.py            (lee desde Supabase)
      python3 _fuente/viajes/importar_destinos.py filas.json (usa un archivo con las filas ya descargadas)

Solo se traen los destinos Publicados. Si un destino del Panel tiene la misma dirección (slug) que uno
de destinos.py, el del Panel lo reemplaza.
"""
import json, os, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
from supabase_config import SUPABASE_URL, SUPABASE_KEY  # noqa: E402

SALIDA = os.path.join(AQUI, "destinos_panel.json")
QUITAR = ("id", "creado")


def descargar():
    url = f"{SUPABASE_URL}/rest/v1/destinos?select=*&estado=eq.Publicado&order=orden.asc,creado.asc"
    req = urllib.request.Request(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    filas = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else descargar()
    filas = [{k: v for k, v in f.items() if k not in QUITAR} for f in filas if f.get("estado") == "Publicado"]
    nuevo = json.dumps(filas, ensure_ascii=False, indent=1) + "\n"
    viejo = open(SALIDA, encoding="utf-8").read() if os.path.exists(SALIDA) else ""
    if nuevo != viejo:
        open(SALIDA, "w", encoding="utf-8").write(nuevo)
        print(f"ok {len(filas)} destinos -> actualizado")
    else:
        print(f"ok {len(filas)} destinos -> sin cambios")


if __name__ == "__main__":
    main()
