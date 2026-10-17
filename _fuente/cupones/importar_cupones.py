#!/usr/bin/env python3
"""Convierte la pestaña Cupones de la hoja 'Plan Ecommerce' en _fuente/cupones/cupones.json

Uso:  python3 _fuente/cupones/importar_cupones.py cupones_valores.json
El archivo es la respuesta de leer el rango 'Cupones'!A4:R, con la forma {"values": [[encabezados], [fila], ...]}.
"""
import json, os, re, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMPOS = {"Código": "codigo", "Título": "titulo", "Comercio": "comercio", "Categoría": "categoria", "Tipo": "tipo",
          "Código de descuento": "cupon", "Descuento": "descuento", "Descripción": "descripcion", "Condiciones": "condiciones",
          "País": "pais", "Ciudad": "ciudad", "Vence": "vence", "Link": "link", "Destacado": "destacado",
          "Exclusivo": "exclusivo", "Destino en Viajes": "destino", "Tema": "tema", "Estado": "estado"}


def slug(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def main(path):
    vals = json.load(open(path, encoding="utf-8")).get("values", [])
    head = [CAMPOS.get(h.strip()) for h in vals[0]]
    out = []
    for r in vals[1:]:
        d = {k: (r[i].strip() if i < len(r) else "") for i, k in enumerate(head) if k}
        if d.get("estado") not in ("Publicado", "Ejemplo") or not d.get("titulo"):
            continue
        d["destacado"] = d.get("destacado") == "Sí"
        d["exclusivo"] = d.get("exclusivo") == "Sí"
        d["slug"] = slug(f'{d["comercio"]}-{d["titulo"]}')
        out.append(d)
    dest = os.path.join(AQUI, "cupones.json")
    json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"ok {len(out)} cupones -> {os.path.relpath(dest)}")


if __name__ == "__main__":
    main(sys.argv[1])
