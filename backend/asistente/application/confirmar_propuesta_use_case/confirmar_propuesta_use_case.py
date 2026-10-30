# asistente/application/confirmar_propuesta_use_case/confirmar_propuesta_use_case.py (módulo 97)
from asistente.application.confirmar_propuesta_use_case.dtos.confirmar_propuesta_input_dto import (
    ConfirmarPropuestaInputDTO,
)
from asistente.application.confirmar_propuesta_use_case.i_confirmar_propuesta_use_case import (
    IConfirmarPropuestaUseCase,
)
from asistente.application.ports.i_ejecutor_de_propuestas import IEjecutorDePropuestas
from asistente.application.shared.dtos.propuesta_output_dto import PropuestaOutputDTO
from asistente.domain.repositories.i_propuesta_command_repository import IPropuestaCommandRepository
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol


class ConfirmarPropuestaUseCase(IConfirmarPropuestaUseCase):
    """Human-in-the-loop: lo único del asistente que cambia los datos del hogar, y no lo pide el modelo sino una persona.

    - Solo la confirma quien hizo la pregunta (la propuesta es de su conversación).
    - Se ejecuta con SU Actor, no con el de lector del agente: el rol lo comprueba el use case de la app dueña, como
      si viniera del formulario (un lector no puede apuntar un gasto, tampoco a través del asistente).
    - En una transacción, con la propuesta bloqueada: dos "Confirmar" a la vez no apuntan el gasto dos veces, y si el
      use case falla, la propuesta sigue pendiente.
    """

    rol_minimo = Rol.LECTOR  # el de la app dueña lo exige ella

    def __init__(
        self,
        *,
        propuestas: IPropuestaCommandRepository,
        ejecutor: IEjecutorDePropuestas,
        reloj: IReloj,
        uow: IUnidadDeTrabajo,
    ):
        self.propuestas, self.ejecutor, self.reloj, self.uow = propuestas, ejecutor, reloj, uow

    def ejecutar(self, entrada: ConfirmarPropuestaInputDTO) -> PropuestaOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            propuesta = self.propuestas.obtener(
                entrada.actor.usuario_id, entrada.hogar_id, entrada.propuesta_id, bloquear=True
            )
            propuesta.comprobar_pendiente(self.reloj.ahora())  # antes de ejecutar nada
            resultado = self.ejecutor.ejecutar(propuesta, entrada.actor)
            propuesta.confirmar(resultado, self.reloj.ahora())
            self.propuestas.guardar(propuesta)
        return PropuestaOutputDTO.desde_bo(propuesta)
