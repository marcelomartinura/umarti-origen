#!/usr/bin/env python3
"""Trae las notas del blog cargadas en el Panel (Supabase) y las escribe en _fuente/blog/notas/*.md

Uso:  python3 _fuente/blog/importar_notas.py            (lee desde Supabase)
      python3 _fuente/blog/importar_notas.py filas.json (usa un archivo con las filas ya descargadas)

Solo se traen las notas Publicadas. Las que dejan de estar publicadas (o se borran en el Panel)
se quitan de la carpeta, y el generador del blog borra sus páginas.
Una nota con datos que no cierran (categoría que no existe, sin texto) se saltea con un aviso,
para que nunca frene la actualización del resto del sitio.
"""
import json, os, re, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = os.path.dirname(AQUI)
sys.path.insert(0, FUENTE)
sys.path.insert(0, AQUI)
from supabase_config import SUPABASE_URL, SUPABASE_KEY  # noqa: E402

NOTAS = os.path.join(AQUI, "notas")


def descargar():
    url = f"{SUPABASE_URL}/rest/v1/blog_notas?select=*&estado=eq.Publicado&order=fecha.desc"
    req = urllib.request.Request(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def limpio(v):
    """Una línea, sin saltos (el encabezado de la nota es línea por línea)."""
    return re.sub(r"\s+", " ", str(v or "")).strip()


def valida(f, categorias, temas, temas_op, autores):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", f.get("slug") or ""):
        return "dirección (slug) inválida"
    if not limpio(f.get("titulo")) or not (f.get("cuerpo") or "").strip():
        return "falta el título o el texto"
    s = f.get("seccion")
    if s == "productos":
        if f.get("categoria") not in categorias or f.get("subcategoria") not in categorias.get(f.get("categoria"), []):
            return f"categoría o subcategoría que no existe: {f.get('categoria')} / {f.get('subcategoria')}"
    elif s == "negocios":
        if f.get("tema") not in temas:
            return f"tema que no existe: {f.get('tema')}"
    elif s == "opinion":
        if f.get("tema") not in temas_op or f.get("autor") not in autores:
            return "tema o autor de opinión que no existe"
    else:
        return f"sección desconocida: {s}"
    return ""


def a_markdown(f):
    m = [("titulo", limpio(f["titulo"])), ("resumen", limpio(f.get("resumen"))), ("seccion", f["seccion"])]
    if f["seccion"] == "productos":
        m += [("categoria", f["categoria"]), ("subcategoria", f["subcategoria"])]
    else:
        m += [("tema", f["tema"])]
    if f["seccion"] == "opinion":
        m += [("autor", f["autor"])]
    m += [("tags", ", ".join(limpio(t) for t in (f.get("tags") or []) if limpio(t))), ("fecha", (f.get("fecha") or "")[:10])]
    if f.get("destacada"):
        m += [("destacada", "si")]
    if limpio(f.get("imagen")):
        m += [("imagen", limpio(f["imagen"])), ("imagen_alt", limpio(f.get("imagen_alt")) or limpio(f["titulo"]))]
        if limpio(f.get("imagen_pos")):
            m += [("imagen_pos", limpio(f["imagen_pos"]))]
    cuerpo = (f.get("cuerpo") or "").replace("\r\n", "\n").strip("\n") + "\n"
    return "---\n" + "\n".join(f"{k}: {v}" for k, v in m) + "\n---\n" + cuerpo


def main():
    from construir_blog import CATEGORIAS, TEMAS  # noqa: E402
    from autores import AUTORES, TEMAS_OPINION  # noqa: E402
    filas = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else descargar()
    filas = [f for f in filas if f.get("estado") == "Publicado"]
    if not filas:
        print("No llegó ninguna nota publicada: no toco nada (por las dudas).")
        return
    os.makedirs(NOTAS, exist_ok=True)
    escritas, cambios = set(), 0
    for f in filas:
        error = valida(f, CATEGORIAS, TEMAS, TEMAS_OPINION, AUTORES)
        if error:
            print(f"AVISO: salteo la nota '{f.get('titulo') or f.get('slug')}': {error}")
            continue
        ruta = os.path.join(NOTAS, f["slug"] + ".md")
        nuevo = a_markdown(f)
        viejo = open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else ""
        if nuevo != viejo:
            open(ruta, "w", encoding="utf-8").write(nuevo); cambios += 1
        escritas.add(f["slug"])
    for nombre in os.listdir(NOTAS):
        if nombre.endswith(".md") and nombre[:-3] not in escritas:
            os.remove(os.path.join(NOTAS, nombre)); cambios += 1
            print(f"quitada: {nombre}")
    print(f"ok {len(escritas)} notas -> {cambios} cambios")


if __name__ == "__main__":
    main()
