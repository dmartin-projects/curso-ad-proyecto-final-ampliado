# finanzas/domain/bo/movimiento.py — el business object Movimiento y sus reglas (módulos 87 y 88)
from dataclasses import dataclass, field, fields, replace
from datetime import date
from typing import ClassVar

from core.domain.bo.i_auditable import IAuditable
from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from finanzas.domain.enums.origen import Origen
from finanzas.domain.exceptions.concepto_vacio_exception import ConceptoVacioException
from finanzas.domain.exceptions.fecha_futura_exception import FechaFuturaException
from finanzas.domain.exceptions.importe_cero_exception import ImporteCeroException
from finanzas.domain.exceptions.movimiento_ya_conciliado_exception import MovimientoYaConciliadoException


# ── Reglas sueltas: las usa el BO y, para dar todos los errores a la vez, el serializer ──
def comprobar_importe(importe: Dinero) -> Dinero:
    if importe.es_cero:
        raise ImporteCeroException()
    return importe


def comprobar_fecha(fecha: date, hoy: date) -> date:
    """Una persona no puede apuntar un gasto de mañana (un extracto o un ticket sí traen la fecha que traen)."""
    if fecha > hoy:
        raise FechaFuturaException()
    return fecha


def normalizar_etiquetas(etiquetas) -> list[str]:
    """[' Casa', 'casa', 'Mes'] → ['casa', 'mes']: sin espacios, en minúsculas, sin repetir y ordenadas."""
    return sorted({e.strip().lower() for e in etiquetas if e.strip()})


EDITABLES = frozenset({"cuenta_id", "fecha", "importe", "concepto", "categoria_id", "etiquetas", "notas", "revisado"})


@dataclass(eq=False)
class Movimiento(IAuditable):
    """Un gasto (importe negativo) o un ingreso (positivo) de un hogar.

    Las invariantes se comprueban al construirlo y al modificarlo: no existe un Movimiento con importe cero
    o sin concepto, venga de la API, de un ticket o de un test. eq=False: dos BOs son el mismo por su
    identidad, no por tener los mismos datos.
    """

    tipo: ClassVar[str] = "finanzas.movimiento"  # para la auditoría (app.modelo)

    hogar_id: int
    cuenta_id: int
    fecha: date
    importe: Dinero
    concepto: str
    categoria_id: int | None = None
    comercio_id: int | None = None
    etiquetas: list[str] = field(default_factory=list)
    notas: str = ""
    origen: Origen = Origen.MANUAL
    revisado: bool = True
    creado_por_id: int | None = None
    # La fila del extracto del banco con la que se ha conciliado (módulos 75 y 88): sha256 de cuenta, fecha, importe,
    # concepto y nº de ocurrencia. Importaciones no escribe en esta tabla: se lo pide a finanzas, y la regla "una
    # fila del banco por movimiento" vive aquí.
    huella: str = ""
    id: int | None = None

    def __post_init__(self):
        comprobar_importe(self.importe)
        if not self.concepto.strip():
            raise ConceptoVacioException()
        self.etiquetas = normalizar_etiquetas(self.etiquetas)
        self.origen = Origen(self.origen)

    @classmethod
    def registrar(cls, *, hoy: date, **datos) -> "Movimiento":
        """Un movimiento que apunta una persona: además de las invariantes, la fecha no puede ser futura."""
        movimiento = cls(**datos)
        comprobar_fecha(movimiento.fecha, hoy)
        return movimiento

    def modificar(self, *, hoy: date, **cambios) -> set[Mes]:
        """Aplica los cambios (todos o ninguno) y devuelve los meses afectados: el de antes y el de después."""
        if desconocidos := cambios.keys() - EDITABLES:
            raise TypeError(f"No se pueden modificar: {sorted(desconocidos)}")
        if "fecha" in cambios:
            comprobar_fecha(cambios["fecha"], hoy)
        meses = {self.mes}
        nuevo = replace(self, **cambios)  # construye otro BO: si algo no es válido, este no cambia
        for f in fields(self):
            setattr(self, f.name, getattr(nuevo, f.name))
        return meses | {self.mes}

    @staticmethod
    def cambios_al_recategorizar(categoria_id: int) -> dict:
        """Elegir la categoría a mano es revisarlo. Una regla, para uno (modificar) o para mil (en bloque)."""
        return {"categoria_id": categoria_id, "revisado": True}

    @property
    def es_propuesta(self) -> bool:
        """Lo creó un proceso (un ticket, un extracto) y nadie lo ha revisado: aún no es un dato de nadie."""
        return not self.revisado and self.origen != Origen.MANUAL

    @property
    def conciliado(self) -> bool:
        return bool(self.huella)

    def conciliar(self, huella: str) -> None:
        """El gasto apuntado a mano "absorbe" la fila del banco: no se importará otra vez (módulo 75)."""
        if self.conciliado and self.huella != huella:
            raise MovimientoYaConciliadoException()
        self.huella = huella

    def desconciliar(self) -> None:
        self.huella = ""

    @property
    def mes(self) -> Mes:
        return Mes.de(self.fecha)

    @property
    def es_gasto(self) -> bool:
        return self.importe.es_gasto

    def instantanea(self) -> "Movimiento":
        """Una copia, para el "antes" de la auditoría y para los eventos (que no deben cambiar después)."""
        return replace(self)

    def datos_auditables(self) -> dict:
        """Los campos que compara la auditoría, con los nombres de siempre (los de model_to_dict)."""
        return {
            "hogar": self.hogar_id,
            "cuenta": self.cuenta_id,
            "fecha": self.fecha,
            "importe": self.importe,
            "concepto": self.concepto,
            "comercio": self.comercio_id,
            "categoria": self.categoria_id,
            "etiquetas": list(self.etiquetas),
            "notas": self.notas,
            "origen": str(self.origen),
            "revisado": self.revisado,
            "creado_por": self.creado_por_id,
        }

    def __str__(self) -> str:
        return f"{self.fecha} {self.concepto} {self.importe}"
