# finanzas/domain/bo/presupuesto.py — el business object Presupuesto y su alerta (módulos 76 y 87)
from dataclasses import dataclass, fields, replace
from datetime import date

from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from finanzas.domain.exceptions.importe_no_positivo_exception import ImporteNoPositivoException

EDITABLES = frozenset({"categoria_id", "mes", "importe"})


@dataclass(eq=False)
class Presupuesto:
    """Lo que un hogar quiere gastar como mucho en una categoría (y sus subcategorías) en un mes."""

    hogar_id: int
    categoria_id: int
    mes: Mes
    importe: Dinero
    alerta_enviada: bool = False
    id: int | None = None

    def __post_init__(self):
        if isinstance(self.mes, date):  # comodidad: date(2026, 10, 15) → Mes(2026, 10)
            self.mes = Mes.de(self.mes)
        if self.importe.cantidad <= 0:
            raise ImporteNoPositivoException()

    def modificar(self, **cambios) -> set[Mes]:
        if desconocidos := cambios.keys() - EDITABLES:
            raise TypeError(f"No se pueden modificar: {sorted(desconocidos)}")
        meses = {self.mes}
        nuevo = replace(self, **cambios)
        for f in fields(self):
            setattr(self, f.name, getattr(nuevo, f.name))
        return meses | {self.mes}

    def superado(self, gastado: Dinero) -> bool:
        """`gastado` es negativo (son gastos): 110 € gastados de 100 € es superado; 100 de 100, también."""
        return abs(gastado) >= self.importe

    def nueva_alerta(self, gastado: Dinero) -> bool | None:
        """¿Cambia el estado de la alerta? True: hay que avisar. False: vuelve a estar por debajo, se rearma
        (si se supera otra vez, se volverá a avisar). None: nada que hacer, ya está como debe."""
        superado = self.superado(gastado)
        return None if superado == self.alerta_enviada else superado
