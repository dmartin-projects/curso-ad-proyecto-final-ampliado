# finanzas/domain/bo/categoria.py — el business object Categoria y su jerarquía de dos niveles (módulo 87)
import re
from dataclasses import dataclass, fields, replace
from typing import ClassVar

from core.domain.bo.i_auditable import IAuditable
from finanzas.domain.exceptions.color_no_valido_exception import ColorNoValidoException
from finanzas.domain.exceptions.demasiados_niveles_exception import DemasiadosNivelesException
from finanzas.domain.exceptions.nombre_vacio_exception import NombreVacioException

COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")  # la misma regla que el CheckConstraint categoria_color_hex
EDITABLES = frozenset({"nombre", "color", "icono", "orden", "es_ingreso"})


@dataclass(eq=False)
class Categoria(IAuditable):
    """Una categoría de un hogar. Dos niveles como mucho: "Hogar › Luz", nunca "Hogar › Luz › Factura"."""

    tipo: ClassVar[str] = "finanzas.categoria"

    hogar_id: int
    nombre: str
    padre_id: int | None = None
    color: str = "#607d8b"
    icono: str = ""
    orden: int = 0
    es_ingreso: bool = False
    id: int | None = None

    def __post_init__(self):
        self.nombre = self.nombre.strip()
        if not self.nombre:
            raise NombreVacioException()
        if not COLOR.match(self.color):
            raise ColorNoValidoException()

    @property
    def es_raiz(self) -> bool:
        return self.padre_id is None

    def modificar(self, **cambios) -> None:
        if desconocidos := cambios.keys() - EDITABLES:
            raise TypeError(f"No se pueden modificar: {sorted(desconocidos)}")
        nuevo = replace(self, **cambios)  # valida antes de tocar nada
        for f in fields(self):
            setattr(self, f.name, getattr(nuevo, f.name))

    def colgar_de(self, padre: "Categoria | None", *, tiene_hijas: bool) -> None:
        """Mueve la categoría bajo `padre` (o a la raíz con None) sin romper los dos niveles.

        Tres casos lo romperían: ser su propia madre (un ciclo), colgar de una subcategoría y colgar una
        categoría que ya tiene hijas (tres niveles). Mirar solo si el padre tiene padre no basta.
        """
        if padre is None:
            self.padre_id = None
            return
        if self.id is not None and padre.id == self.id:
            raise DemasiadosNivelesException("Una categoría no puede ser su propia madre.")
        if not padre.es_raiz:
            raise DemasiadosNivelesException()
        if tiene_hijas:
            raise DemasiadosNivelesException("Una categoría con subcategorías no puede colgar de otra.")
        self.padre_id = padre.id

    def datos_auditables(self) -> dict:
        return {
            "nombre": self.nombre,
            "padre": self.padre_id,
            "color": self.color,
            "icono": self.icono,
            "orden": self.orden,
            "es_ingreso": self.es_ingreso,
        }

    def __str__(self) -> str:
        return self.nombre
