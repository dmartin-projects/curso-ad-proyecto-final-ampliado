# hogares/domain/bo/hogar.py — el hogar (módulos 36, 71 y 88)
from dataclasses import dataclass, fields, replace
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from hogares.domain.exceptions.nombre_vacio_exception import NombreVacioException
from hogares.domain.exceptions.zona_horaria_no_valida_exception import ZonaHorariaNoValidaException

EDITABLES = frozenset({"nombre", "moneda", "zona_horaria"})


# ── Regla suelta: la usa el BO y, para dar todos los errores del formulario a la vez, el serializer ──
def comprobar_zona_horaria(zona: str) -> str:
    """Una zona de la base de datos IANA: el dashboard calcula "el mes de hoy" con ZoneInfo(hogar.zona_horaria)."""
    try:
        ZoneInfo(zona)
    except (ZoneInfoNotFoundError, ValueError):  # ValueError: rutas raras ("../x"), cadena vacía
        raise ZonaHorariaNoValidaException() from None
    return zona


@dataclass(eq=False)
class Hogar:
    nombre: str
    moneda: str = "EUR"
    zona_horaria: str = "Europe/Madrid"
    id: int | None = None

    def __post_init__(self):
        self.nombre = self.nombre.strip()
        if not self.nombre:
            raise NombreVacioException()
        comprobar_zona_horaria(self.zona_horaria)

    def modificar(self, **cambios) -> None:
        if desconocidos := cambios.keys() - EDITABLES:
            raise TypeError(f"No se pueden modificar: {sorted(desconocidos)}")
        nuevo = replace(self, **cambios)  # valida antes de tocar nada
        for f in fields(self):
            setattr(self, f.name, getattr(nuevo, f.name))
