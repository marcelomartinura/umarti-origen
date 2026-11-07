#!/usr/bin/env python3
"""Trae lo cargado en el módulo Viajes del Panel (Supabase):
  - destinos      -> _fuente/viajes/destinos_panel.json
  - Organizá tu viaje (servicios y ofertas) -> _fuente/viajes/organiza_panel.json

Uso:  python3 _fuente/viajes/importar_destinos.py                          (lee desde Supabase)
      python3 _fuente/viajes/importar_destinos.py destinos.json [organiza.json] (archivos ya descargados;
      organiza.json = {"servicios": [...], "ofertas": [...]})

Solo se traen los destinos Publicados. Si un destino del Panel tiene la misma dirección (slug) que uno
de destinos.py, el del Panel lo reemplaza.
"""
import json, os, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
from supabase_config import SUPABASE_URL, SUPABASE_KEY  # noqa: E402

SALIDA = os.path.join(AQUI, "destinos_panel.json")
QUITAR = ("id", "creado")


def descargar(consulta="destinos?select=*&estado=eq.Publicado&order=orden.asc,creado.asc"):
    url = f"{SUPABASE_URL}/rest/v1/{consulta}"
    req = urllib.request.Request(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def guardar(ruta, datos, nombre):
    nuevo = json.dumps(datos, ensure_ascii=False, indent=1) + "\n"
    viejo = open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else ""
    if nuevo != viejo:
        open(ruta, "w", encoding="utf-8").write(nuevo)
        print(f"ok {nombre} -> actualizado")
    else:
        print(f"ok {nombre} -> sin cambios")


def organiza():
    if len(sys.argv) > 2:
        d = json.load(open(sys.argv[2], encoding="utf-8"))
    elif len(sys.argv) > 1:
        return
    else:
        d = {"servicios": descargar("viajes_servicios?select=*"),
             "ofertas": descargar("viajes_ofertas?select=*&estado=eq.Publicado&order=orden.asc,creado.asc")}
    d["ofertas"] = [{k: v for k, v in o.items() if k not in ("creado",)} for o in d.get("ofertas", []) if o.get("estado") == "Publicado"]
    for x in d.get("servicios", []):
        x.pop("actualizado", None)
    for o in d["ofertas"]:
        o.pop("actualizado", None)
    guardar(os.path.join(AQUI, "organiza_panel.json"), d, f"{len(d['ofertas'])} ofertas de Organizá tu viaje")


def main():
    organiza()
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
