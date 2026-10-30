# asistente/infrastructure/finanzas/ejecutor_de_propuestas_en_finanzas.py — las propuestas, con finanzas (módulo 97)
#
# Cada tipo de propuesta es un use case de COMANDO de finanzas, el mismo que usa su API: las mismas reglas (importe,
# fecha, cuenta y categoría del hogar), la misma auditoría y los mismos eventos (outbox de Kafka, avisos, presupuestos).
from datetime import date
from decimal import Decimal

from asistente.application.ports.i_ejecutor_de_propuestas import IEjecutorDePropuestas
from asistente.domain.enums.tipo_propuesta import TipoPropuesta
from finanzas.application.registrar_movimiento_use_case.dtos.registrar_movimiento_input_dto import (
    RegistrarMovimientoInputDTO,
)
from finanzas.infrastructure import container as finanzas


class EjecutorDePropuestasEnFinanzas(IEjecutorDePropuestas):
    def ejecutar(self, propuesta, actor):
        if propuesta.tipo == TipoPropuesta.MOVIMIENTO:
            d = propuesta.datos
            movimiento = finanzas.registrar_movimiento().ejecutar(
                RegistrarMovimientoInputDTO(
                    hogar_id=propuesta.hogar_id,
                    actor=actor,  # el de quien confirma, con SU rol
                    cuenta_id=d["cuenta_id"],
                    fecha=date.fromisoformat(d["fecha"]),
                    importe=Decimal(d["importe"]),
                    concepto=d["concepto"],
                    categoria_id=d["categoria_id"],
                    notas="Apuntado desde el asistente",
                )
            )
            return {"movimiento_id": movimiento.id}
        raise ValueError(f"Tipo de propuesta sin ejecutor: {propuesta.tipo}")
