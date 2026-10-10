# Datos del Hub de Oportunidades (prototipo: todo son ejemplos)
# Para cambiar algo: editá este archivo y corré  python3 _fuente/construir.py

SECTORES = ["Alimentos y bebidas", "Agroindustria", "Manufacturas", "Minería y energía", "Moda y textil", "Salud", "Tecnología"]

CATEGORIAS_SERVICIO = ["Despachantes de aduana", "Transporte y logística", "Seguros de carga",
                       "Certificaciones", "Consultoría en comercio exterior", "Servicios digitales"]

# Productos de exportación (ofertas de venta)
PRODUCTOS = [
  dict(cod="UO-P-0001", nombre="Vino Malbec embotellado, 750 ml", hs="220421", sector="Alimentos y bebidas", pais="Argentina", region="Mendoza", destinos="Alemania, México, Brasil", vol="2 contenedores por mes", vence="2027-06-30", claves="vino tinto malbec bodega"),
  dict(cod="UO-P-0002", nombre="Maní tipo confitería, sin cáscara", hs="120242", sector="Agroindustria", pais="Argentina", region="Córdoba", destinos="China, Unión Europea", vol="500 toneladas", vence="2027-03-31", claves="maní cacahuate cacahuete"),
  dict(cod="UO-P-0003", nombre="Yerba mate elaborada con palo", hs="090300", sector="Alimentos y bebidas", pais="Argentina", region="Misiones", destinos="España, Estados Unidos, Siria", vol="20 toneladas por mes", vence="2027-08-15", claves="yerba mate infusión"),
  dict(cod="UO-P-0004", nombre="Miel natural a granel", hs="040900", sector="Agroindustria", pais="Argentina", region="Entre Ríos", destinos="Alemania, Estados Unidos", vol="100 toneladas", vence="2027-01-31", claves="miel apícola"),
  dict(cod="UO-P-0005", nombre="Aguacate Hass fresco", hs="080440", sector="Agroindustria", pais="México", region="Michoacán", destinos="Canadá, Japón, Emiratos Árabes Unidos", vol="40 toneladas por semana", vence="2027-05-31", claves="aguacate palta hass fruta"),
  dict(cod="UO-P-0006", nombre="Tequila 100% agave", hs="220890", sector="Alimentos y bebidas", pais="México", region="Jalisco", destinos="Estados Unidos, España, Argentina", vol="5.000 cajas", vence="2027-09-30", claves="tequila agave destilado bebida"),
  dict(cod="UO-P-0007", nombre="Limón fresco", hs="080550", sector="Agroindustria", pais="Argentina", region="Tucumán", destinos="Estados Unidos, Unión Europea", vol="300 toneladas por temporada", vence="2027-04-30", claves="limón cítrico fruta"),
  dict(cod="UO-P-0008", nombre="Filtros de aire para vehículos", hs="842131", sector="Manufacturas", pais="México", region="Querétaro", destinos="Argentina, Brasil, Chile", vol="20.000 unidades por mes", vence="2027-02-28", claves="filtros autopartes automotriz"),
]

# Servicios de comercio exterior
SERVICIOS = [
  dict(cod="UO-S-0001", nombre="Despacho de aduana para exportar e importar", categoria="Despachantes de aduana", pais="Argentina", region="Buenos Aires", cobertura="Argentina ↔ México, Argentina ↔ Brasil", detalle="Clasificación arancelaria, documentación y despacho en puerto y aeropuerto.", claves="despachante aduana despacho exportación importación"),
  dict(cod="UO-S-0002", nombre="Agente aduanal en Manzanillo y Veracruz", categoria="Despachantes de aduana", pais="México", region="Colima y Veracruz", cobertura="México ↔ Sudamérica", detalle="Importaciones de alimentos y bebidas, permisos sanitarios y padrón de importadores.", claves="agente aduanal despachante aduana importar"),
  dict(cod="UO-S-0003", nombre="Transporte marítimo consolidado y contenedor completo", categoria="Transporte y logística", pais="Argentina", region="Buenos Aires", cobertura="Buenos Aires ↔ Manzanillo y Veracruz", detalle="Carga consolidada (LCL) y contenedor completo (FCL), incluido refrigerado.", claves="transporte flete marítimo contenedor logística refrigerado"),
  dict(cod="UO-S-0004", nombre="Carga aérea para perecederos", categoria="Transporte y logística", pais="México", region="Ciudad de México", cobertura="México ↔ Estados Unidos y Europa", detalle="Frutas, flores y productos que necesitan cadena de frío.", claves="carga aérea transporte flete perecederos frío logística"),
  dict(cod="UO-S-0005", nombre="Almacenaje y preparación de pedidos en México", categoria="Transporte y logística", pais="México", region="Querétaro", cobertura="Todo México", detalle="Recepción de importaciones, almacenaje y envío a clientes finales.", claves="almacén almacenaje bodega logística distribución"),
  dict(cod="UO-S-0006", nombre="Seguro de carga internacional", categoria="Seguros de carga", pais="Argentina", region="Buenos Aires", cobertura="Todo el mundo", detalle="Cobertura por embarque o anual para carga marítima, aérea y terrestre.", claves="seguro carga póliza"),
  dict(cod="UO-S-0007", nombre="Gestión de certificados de origen y fitosanitarios", categoria="Certificaciones", pais="Argentina", region="Rosario", cobertura="Exportaciones desde Argentina", detalle="Trámites para acceder a preferencias arancelarias y requisitos sanitarios.", claves="certificado origen fitosanitario senasa certificación"),
  dict(cod="UO-S-0008", nombre="Consultoría para exportar a México", categoria="Consultoría en comercio exterior", pais="México", region="Querétaro", cobertura="Exportadores de Sudamérica", detalle="Normas oficiales mexicanas, etiquetado, registro y primeros clientes.", claves="consultoría asesoría etiquetado normas nom exportar"),
  dict(cod="UO-S-0009", nombre="Desarrollo de software a medida", categoria="Servicios digitales", pais="Argentina", region="Buenos Aires", cobertura="México, España, Estados Unidos", detalle="Equipos dedicados para tiendas en línea, sistemas de gestión y automatización.", claves="software desarrollo programación sistemas tienda digital"),
]

# Búsquedas publicadas en la Mesa de negociación
BUSQUEDAS = [
  dict(cod="UO-B-0001", tipo="producto", nombre="Vino tinto embotellado", hs="220421", sector="Alimentos y bebidas", pais="Alemania", origen="Argentina o Chile", vol="1 contenedor por trimestre", publicada="2026-10-02", vence="2027-07-13"),
  dict(cod="UO-B-0002", tipo="producto", nombre="Maní sin cáscara", hs="120242", sector="Agroindustria", pais="China", origen="Sin preferencia", vol="1.000 toneladas", publicada="2026-10-03", vence="2027-08-06"),
  dict(cod="UO-B-0003", tipo="producto", nombre="Carne bovina deshuesada, congelada", hs="020230", sector="Agroindustria", pais="China", origen="Argentina, Uruguay o Brasil", vol="500 toneladas por mes", publicada="2026-10-08", vence="2027-03-15"),
  dict(cod="UO-B-0004", tipo="servicio", nombre="Despachante de aduana para importar alimentos a México", hs="", sector="Despachantes de aduana", pais="México", origen="Con experiencia en alimentos", vol="Operaciones mensuales", publicada="2026-10-06", vence="2026-11-30"),
  dict(cod="UO-B-0005", tipo="producto", nombre="Miel orgánica certificada", hs="040900", sector="Agroindustria", pais="Alemania", origen="Sudamérica", vol="40 toneladas", publicada="2026-10-01", vence="2026-11-05"),
  dict(cod="UO-B-0006", tipo="producto", nombre="Aceite de oliva extra virgen", hs="150920", sector="Alimentos y bebidas", pais="México", origen="Argentina o España", vol="3 contenedores por año", publicada="2026-10-09", vence="2027-04-30"),
  dict(cod="UO-B-0007", tipo="producto", nombre="Yerba mate", hs="090300", sector="Alimentos y bebidas", pais="España", origen="Argentina", vol="5 toneladas por mes", publicada="2026-10-04", vence="2027-02-28"),
  dict(cod="UO-B-0008", tipo="servicio", nombre="Transporte refrigerado de Argentina a México", hs="", sector="Transporte y logística", pais="México", origen="Salida desde Buenos Aires", vol="2 contenedores por mes", publicada="2026-10-07", vence="2027-01-31"),
  dict(cod="UO-B-0009", tipo="producto", nombre="Aguacate fresco", hs="080440", sector="Agroindustria", pais="Emiratos Árabes Unidos", origen="Sin preferencia", vol="2 contenedores por mes", publicada="2026-10-05", vence="2027-01-15"),
  dict(cod="UO-B-0010", tipo="producto", nombre="Trigo duro", hs="100119", sector="Agroindustria", pais="Etiopía", origen="Sin preferencia", vol="10.000 toneladas", publicada="2026-10-09", vence="2027-10-30"),
]

PAISES = ["Alemania", "Argentina", "Bolivia", "Brasil", "Canadá", "Chile", "China", "Colombia", "Corea del Sur", "Ecuador",
          "Emiratos Árabes Unidos", "España", "Estados Unidos", "Etiopía", "Francia", "India", "Italia", "Japón", "México",
          "Países Bajos", "Paraguay", "Perú", "Portugal", "Reino Unido", "Uruguay"]

CC = {"Argentina": "AR", "México": "MX", "Alemania": "DE", "China": "CN", "España": "ES", "Emiratos Árabes Unidos": "AE",
      "Etiopía": "ET", "Estados Unidos": "US", "Brasil": "BR", "Chile": "CL", "Canadá": "CA", "Japón": "JP", "Uruguay": "UY"}
