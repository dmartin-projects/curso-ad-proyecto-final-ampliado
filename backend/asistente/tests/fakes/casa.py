# asistente/tests/fakes/casa.py — los datos del hogar de los tests, en un solo sitio (módulos 94 y 95)
#
# La fixture `casa` (tests/conftest.py) los escribe en PostgreSQL; ConsultasDeFinanzasFake.de_casa() los tiene en
# memoria. Los contract tests comprueban que el adapter y el fake dicen lo mismo de los MISMOS datos.
NOMBRE = "Casa de Ana y Luis"

# (nombre, categoría principal, es_ingreso)
CATEGORIAS = [
    ("Supermercado", None, False),
    ("Restaurantes", None, False),
    ("Ocio", None, False),
    ("Casa", None, False),
    ("Luz", "Casa", False),
    ("Transporte", None, False),
    ("Nómina", None, True),
]
COMERCIOS = ["Mercadona", "Lidl", "Bar Manolo", "Netflix", "Renfe"]

# (fecha, importe, concepto, categoría, comercio)
MOVIMIENTOS = [
    *[(f"2026-{mes}-01", "2100.00", "Nómina", "Nómina", None) for mes in ("08", "09", "10")],
    *[(f"2026-{mes}-02", "-37.50", "Abono transporte", "Transporte", "Renfe") for mes in ("08", "09", "10")],
    ("2026-08-03", "-312.40", "Compra semanal", "Supermercado", "Mercadona"),
    ("2026-08-17", "-98.15", "Compra", "Supermercado", "Mercadona"),
    ("2026-08-10", "-64.20", "Compra", "Supermercado", "Lidl"),
    ("2026-08-14", "-46.80", "Cena", "Restaurantes", "Bar Manolo"),
    ("2026-08-22", "-24.00", "Cine", "Ocio", None),
    ("2026-08-28", "-88.30", "Factura de la luz", "Luz", None),
    ("2026-09-05", "-287.90", "Compra semanal", "Supermercado", "Mercadona"),
    ("2026-09-19", "-121.35", "Compra", "Supermercado", "Mercadona"),
    ("2026-09-12", "-52.10", "Compra", "Supermercado", "Lidl"),
    ("2026-09-13", "-23.40", "Cena (a medias)", "Restaurantes", "Bar Manolo"),
    ("2026-09-20", "-78.60", "Cumpleaños de Luis", "Restaurantes", None),
    ("2026-09-15", "-17.99", "Suscripción", "Ocio", "Netflix"),
    ("2026-09-26", "-65.00", "Concierto", "Ocio", None),
    ("2026-09-28", "-92.75", "Factura de la luz", "Luz", None),
    ("2026-10-03", "-301.25", "Compra semanal", "Supermercado", "Mercadona"),
    ("2026-10-11", "-45.80", "Compra", "Supermercado", "Lidl"),
    ("2026-10-18", "-31.20", "Cena", "Restaurantes", "Bar Manolo"),
    ("2026-10-15", "-17.99", "Suscripción", "Ocio", "Netflix"),
    ("2026-10-27", "-71.40", "Factura de la luz", "Luz", None),
    # Módulo 95: un año antes, para comparar con el IPC
    ("2025-09-06", "-352.60", "Compra semanal", "Supermercado", "Mercadona"),
    ("2025-09-20", "-61.40", "Compra", "Supermercado", "Lidl"),
    ("2025-09-27", "-79.80", "Factura de la luz", "Luz", None),
]
