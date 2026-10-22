# estadisticas/domain/bo/movimiento.py — lo que el servicio sabe de un movimiento de Gastos (módulos 85 y 89)
#
# No es un business object que cambie poco a poco, como los de finanzas (módulo 87): es una FOTO. Cada evento trae
# la foto completa y una versión (el id del evento en el outbox de Django, que crece con cada cambio); una foto más
# nueva sustituye a la vieja entera. Por eso es inmutable (`frozen`): nadie modifica una foto, se cambia por otra.
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Movimiento:
    id: int  # el id de Django
    hogar_id: int
    cuenta_id: int
    fecha: date
    importe: Decimal  # negativo: gasto; positivo: ingreso
    categoria_id: int | None
    comercio_id: int | None
    origen: str
    revisado: bool
    version: int

    @classmethod
    def desde_evento(cls, pk: int, datos: dict, version: int) -> "Movimiento":
        """Lector tolerante (tolerant reader): coge los campos que usa e ignora el resto. Si falta uno o no tiene
        la forma esperada, KeyError, ValueError… (interpretacion.py los convierte en EventoInvalidoException)."""
        return cls(
            id=pk,
            hogar_id=datos["hogar_id"],
            cuenta_id=datos["cuenta_id"],
            fecha=date.fromisoformat(datos["fecha"]),
            importe=Decimal(datos["importe"]),
            categoria_id=datos["categoria_id"],
            comercio_id=datos["comercio_id"],
            origen=datos["origen"],
            revisado=datos.get("revisado", True),  # .get: los mensajes antiguos sin el campo siguen valiendo
            version=version,
        )
