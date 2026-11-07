# Guías de destinos de Umarti Viajes
# Para sumar un destino: copiá un bloque, completalo y corré  python3 _fuente/construir_viajes.py
#
# paisaje: montana | ciudad | agua | cerros  (dibujo de la portada)
# tipos: Aventura, Cultura, Gastronomía, Montaña, Naturaleza, Nieve, Urbano, Vino
# origen: productos de ese lugar que se conectan con la Tienda y el Blog.
#   nota = nombre del archivo de una nota del blog (sin .md), si existe.

# Continentes en los que se agrupan los países. Para sumar un país de otro continente,
# agregalo a PAISES con continente="Europa" (o el que corresponda).
CONTINENTES = [
    ("america", "América", "De la Patagonia al Caribe, pasando por ciudades, selvas, montañas y viñedos."),
    ("europa", "Europa", "Capitales históricas, pueblos con encanto y rutas de vino y café."),
    ("asia", "Asia", "Templos, mercados, ciudades enormes y cocinas para descubrir."),
    ("africa", "África", "Desiertos, safaris y costas para viajes inolvidables."),
    ("oceania", "Oceanía", "Islas, playas y naturaleza en el otro extremo del mundo."),
]

PAISES = {
    "argentina": dict(nombre="Argentina", continente="america", tz="America/Argentina/Buenos_Aires",
                      # foto de la presentación del país (opcional)
                      fotos=[("assets/img/viajes/argentina-glaciar-perito-moreno.jpg", "El glaciar Perito Moreno, en Santa Cruz")], lead="De los glaciares de la Patagonia a la selva misionera, pasando por los viñedos de Mendoza y los cerros de colores del norte. Un país enorme para recorrer por regiones.",
                      colores=("#4a86b4", "#264d6e"), moneda="Peso argentino (ARS)", idioma="Español"),
    "mexico": dict(nombre="México", continente="america", tz="America/Mexico_City",
                   fotos=[("assets/img/viajes/mexico-atardecer-en-la-playa.jpg", "Atardecer en una playa del Pacífico mexicano", "center 18%")], lead="Ciudades coloniales, una capital inmensa, cocina reconocida en todo el mundo y regiones de vino y queso a pocas horas de la Ciudad de México.",
                   colores=("#3f8f6b", "#1f5a41"), moneda="Peso mexicano (MXN)", idioma="Español"),
}

# Los destinos se cargan desde el Panel (módulo Viajes). Ver _cargar_panel() más abajo.
DESTINOS = []

# Destinos destacados de la portada de Viajes (hasta 8, por slug, en este orden).
# Si queda vacío, se muestran los primeros 8 de DESTINOS.
DESTACADOS = []

# Link de afiliado de Despegar. Cuando tengas el tuyo, reemplazalo acá.
DESPEGAR_URL = "https://www.despegar.com/"


# ---------- Destinos cargados desde el Panel ----------
# importar_destinos.py los baja de Supabase a destinos_panel.json. Si tienen la misma dirección (slug)
# que uno de arriba, lo reemplazan; si no, se suman.
def _clave_pais(nombre):
    import unicodedata
    s = unicodedata.normalize("NFD", nombre).encode("ascii", "ignore").decode().lower()
    return "".join(c if c.isalnum() else "-" for c in s).strip("-")


def _cargar_panel():
    import json, os
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "destinos_panel.json")
    if not os.path.exists(ruta):
        return
    for f in json.load(open(ruta, encoding="utf-8")):
        pk = _clave_pais(f.get("pais") or "Argentina")
        if pk not in PAISES:
            PAISES[pk] = dict(nombre=f["pais"], continente=f.get("continente") or "", lead="", colores=("#4f6b3a", "#33472a"),
                              moneda="", idioma="")
        base = next((x for x in DESTINOS if x["slug"] == f["slug"]), None)
        x = dict(base or {})
        x.update(slug=f["slug"], nombre=f["ciudad"], pais=pk, region=f.get("region") or f["ciudad"],
                 tipos=list(f.get("tags") or []), resumen=f.get("resumen") or "", dias=f.get("dias") or "",
                 presupuesto=f.get("presupuesto") or "", mejor_epoca=f.get("mejor_epoca") or "", panel=f)
        x.setdefault("paisaje", "ciudad")
        x.setdefault("colores", PAISES[pk]["colores"])
        x.setdefault("origen", [])
        if base:
            DESTINOS[DESTINOS.index(base)] = x
        else:
            DESTINOS.append(x)


_cargar_panel()
