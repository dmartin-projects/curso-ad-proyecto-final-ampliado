# asistente/application/ver_contexto_use_case/ver_contexto_use_case.py (módulo 99, ejercicio 2)
from asistente.application.agent.limites import Limites
from asistente.application.agent.memoria import memoria
from asistente.application.agent.ventana import ventana
from asistente.application.ver_contexto_use_case.dtos.parte_del_contexto_output_dto import ParteDelContextoOutputDTO
from asistente.application.ver_contexto_use_case.dtos.ver_contexto_input_dto import VerContextoInputDTO
from asistente.application.ver_contexto_use_case.i_ver_contexto_use_case import IVerContextoUseCase
from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.repositories.i_conversacion_command_repository import IConversacionCommandRepository
from asistente.domain.repositories.i_recuerdo_query_service import IRecuerdoQueryService
from asistente.domain.services.tokens import estimar_tokens
from asistente.domain.vo.mensaje import Mensaje
from core.domain.enums.rol import Rol


class VerContextoUseCase(IVerContextoUseCase):
    """Para depurar "¿qué sabe el asistente de esta conversación?": lo mismo que monta ResponderPregunta (memoria fija
    y la ventana del historial que queda sin resumir), sin llamar al modelo."""

    rol_minimo = Rol.LECTOR

    def __init__(
        self, *, conversaciones: IConversacionCommandRepository, recuerdos: IRecuerdoQueryService, limites: Limites
    ):
        self.conversaciones, self.recuerdos, self.limites = conversaciones, recuerdos, limites

    def ejecutar(self, entrada: VerContextoInputDTO) -> list[ParteDelContextoOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        usuario_id = entrada.actor.usuario_id
        conversacion = self.conversaciones.obtener(usuario_id, entrada.hogar_id, entrada.conversacion_id)
        recuerdos = [r.texto for r in self.recuerdos.listar(usuario_id, entrada.hogar_id)]
        fijo = memoria(conversacion.resumen, recuerdos)
        presupuesto = max(0, self.limites.max_tokens_historial - sum(estimar_tokens(m.texto) for m in fijo))
        historial = self.conversaciones.historial(conversacion.id, conversacion.resumido_hasta)
        viaja = ventana((*historial, Mensaje.usuario(entrada.pregunta)), presupuesto)
        partes = [ParteDelContextoOutputDTO("memoria", m.texto, estimar_tokens(m.texto)) for m in fijo]
        for m in viaja:
            if m.rol != RolMensaje.TOOL and m.texto:
                partes.append(ParteDelContextoOutputDTO(str(m.rol), m.texto, estimar_tokens(m.texto)))
        return partes
