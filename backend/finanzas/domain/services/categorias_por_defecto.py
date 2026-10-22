# finanzas/domain/services/categorias_por_defecto.py — las categorías con las que nace cada hogar (módulos 72 y 87)
from finanzas.domain.bo.categoria import Categoria

# (nombre, color, icono, [subcategorías])
CATEGORIAS_POR_DEFECTO = [
    ("Supermercado", "#2e7d32", "shopping_cart", []),
    ("Hogar", "#6d4c41", "home", ["Alquiler / hipoteca", "Luz", "Agua", "Gas", "Internet y móvil"]),
    ("Transporte", "#1565c0", "directions_car", ["Combustible", "Transporte público", "Parking"]),
    ("Restaurantes", "#ef6c00", "restaurant", []),
    ("Salud", "#c62828", "medical_services", ["Farmacia"]),
    ("Ocio", "#8e24aa", "theaters", ["Suscripciones", "Viajes"]),
    ("Ropa", "#ad1457", "checkroom", []),
    ("Educación", "#00838f", "school", []),
    ("Otros", "#607d8b", "category", []),
]
INGRESOS_POR_DEFECTO = [("Nómina", "#1b5e20", "payments"), ("Otros ingresos", "#33691e", "savings")]


def por_defecto(hogar_id: int) -> tuple[list[Categoria], dict[str, list[Categoria]]]:
    """(raíces, {nombre de la raíz: sus hijas}). Las hijas aún no tienen padre_id: lo pone el use case
    cuando las raíces ya tienen id."""
    raices = [
        Categoria(hogar_id=hogar_id, nombre=nombre, color=color, icono=icono, orden=orden)
        for orden, (nombre, color, icono, _) in enumerate(CATEGORIAS_POR_DEFECTO)
    ]
    base = len(CATEGORIAS_POR_DEFECTO)
    raices += [
        Categoria(hogar_id=hogar_id, nombre=nombre, color=color, icono=icono, orden=base + k, es_ingreso=True)
        for k, (nombre, color, icono) in enumerate(INGRESOS_POR_DEFECTO)
    ]
    hijas = {
        nombre: [Categoria(hogar_id=hogar_id, nombre=h, color=color, icono=icono, orden=i) for i, h in enumerate(hs)]
        for nombre, color, icono, hs in CATEGORIAS_POR_DEFECTO
    }
    return raices, hijas
