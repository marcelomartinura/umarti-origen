"""Autores y columnas de opinión del blog.

Cada autor tiene una página en blog/autor/<clave>/ y sus columnas en blog/opinion/.
Para sumar otro columnista, agregá una entrada con la misma forma.
"""

AUTORES = {
    "marcelo-uranga": {
        "nombre": "Marcelo Uranga Martínez",
        "iniciales": "MU",
        "rol": "Fundador de Umarti",
        "columna": "Ida y vuelta",
        "columna_bajada": "Negocios, origen y experiencias entre Argentina y México.",
        "foto": "",  # ruta a la foto (por ejemplo assets/img/marcelo.jpg); vacío muestra las iniciales
        "bio": [
            "Fundador de Umarti, un ecosistema que conecta productos con historia, comercio entre países y viajes.",
            "Tiene más de 20 años de experiencia en liderazgo comercial, transformación digital, innovación y automatización de procesos en la industria automotriz y de tecnología.",
            "Vive en Querétaro, México. En esta columna escribe sobre negocios, emprender entre países y las experiencias que lo llevaron hasta acá.",
        ],
        "redes": [
            # ("LinkedIn", "https://www.linkedin.com/in/..."),
        ],
    },
}

# Temas de las columnas de opinión
TEMAS_OPINION = ["Negocios", "Experiencias"]
