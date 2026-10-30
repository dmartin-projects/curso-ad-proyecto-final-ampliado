# asistente/application/obtener_conversacion_use_case/obtener_conversacion_use_case.py (módulo 97)
from asistente.application.obtener_conversacion_use_case.dtos.obtener_conversacion_input_dto import (
    ObtenerConversacionInputDTO,
)
from asistente.application.obtener_conversacion_use_case.i_obtener_conversacion_use_case import (
    IObtenerConversacionUseCase,
)
from asistente.application.ports.i_almacen_de_archivos import IAlmacenDeArchivos
from asistente.application.shared.dtos.conversacion_detalle_output_dto import ConversacionDetalleOutputDTO
from asistente.application.shared.dtos.conversacion_output_dto import ConversacionOutputDTO
from asistente.application.shared.dtos.mensaje_output_dto import MensajeOutputDTO
from asistente.domain.read_models.mensaje_visible import MensajeVisible
from asistente.domain.repositories.i_conversacion_query_service import IConversacionQueryService
from core.domain.enums.rol import Rol


class ObtenerConversacionUseCase(IObtenerConversacionUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, consultas: IConversacionQueryService, almacen: IAlmacenDeArchivos):
        self.consultas, self.almacen = consultas, almacen

    def ejecutar(self, entrada: ObtenerConversacionInputDTO) -> ConversacionDetalleOutputDTO | None:
        entrada.actor.exigir(self.rol_minimo)
        d = self.consultas.detalle(entrada.actor.usuario_id, entrada.hogar_id, entrada.conversacion_id)
        if d is None:
            return None
        return ConversacionDetalleOutputDTO(
            ConversacionOutputDTO.desde_read_model(d.conversacion), [self._mensaje(m) for m in d.mensajes]
        )

    def _mensaje(self, m: MensajeVisible) -> MensajeOutputDTO:
        datos = dict(m.datos)
        if archivos := datos.get("archivos"):  # la URL se firma al leer: la guardada habría caducado
            datos["archivos"] = [{**a, "url": self.almacen.url(a["ruta"])} for a in archivos]
        return MensajeOutputDTO(m.id, m.rol, m.texto, datos, m.incompleto, m.nombre_adjunto, m.creado)
