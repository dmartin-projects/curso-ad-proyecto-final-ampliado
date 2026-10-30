# asistente/application/exportar_mis_datos_use_case/exportar_mis_datos_use_case.py (ejercicio 2 del 107)
"""Derecho de acceso y portabilidad (RGPD, artículos 15 y 20): todo lo que el asistente guarda de una persona en un
hogar, en un formato que se lee y que otro programa puede importar (JSON). Lo que ve la persona, no lo interno: las
preguntas y las respuestas como se ven en el chat (sin los resultados de las tools, que son datos del hogar que ya
tiene en la app), sus recuerdos y lo que ha gastado del plan."""

from asistente.application.exportar_mis_datos_use_case.dtos.exportar_mis_datos_input_dto import (
    ExportarMisDatosInputDTO,
)
from asistente.domain.repositories.i_conversacion_query_service import IConversacionQueryService
from asistente.domain.repositories.i_recuerdo_query_service import IRecuerdoQueryService
from core.domain.enums.rol import Rol

MAX_CONVERSACIONES = 10_000


class ExportarMisDatosUseCase:
    rol_minimo = Rol.LECTOR

    def __init__(self, *, conversaciones: IConversacionQueryService, recuerdos: IRecuerdoQueryService):
        self.conversaciones, self.recuerdos = conversaciones, recuerdos

    def ejecutar(self, entrada: ExportarMisDatosInputDTO) -> dict:
        entrada.actor.exigir(self.rol_minimo)
        usuario, hogar = entrada.actor.usuario_id, entrada.hogar_id
        conversaciones = []
        for c in self.conversaciones.listar(usuario, hogar, limite=MAX_CONVERSACIONES):
            detalle = self.conversaciones.detalle(usuario, hogar, c.id)
            if detalle is None:  # borrada mientras tanto
                continue
            conversaciones.append(
                {
                    "titulo": c.titulo,
                    "actualizada": c.actualizada.isoformat(),
                    "mensajes": [
                        {"rol": m.rol, "texto": m.texto, "adjunto": m.nombre_adjunto, "creado": m.creado.isoformat()}
                        for m in detalle.mensajes
                    ],
                }
            )
        recuerdos = [{"texto": r.texto, "creado": r.creado.isoformat()} for r in self.recuerdos.listar(usuario, hogar)]
        return {"conversaciones": conversaciones, "recuerdos": recuerdos}
