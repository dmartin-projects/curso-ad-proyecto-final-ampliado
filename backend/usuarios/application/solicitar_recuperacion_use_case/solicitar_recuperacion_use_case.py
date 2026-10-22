# usuarios/application/solicitar_recuperacion_use_case/solicitar_recuperacion_use_case.py (módulos 35 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.ports.i_enlaces import IEnlaces
from usuarios.application.shared.contrasenas import evento_completar_registro
from usuarios.application.solicitar_recuperacion_use_case.dtos.solicitar_recuperacion_input_dto import (
    SolicitarRecuperacionInputDTO,
)
from usuarios.application.solicitar_recuperacion_use_case.i_solicitar_recuperacion_use_case import (
    ISolicitarRecuperacionUseCase,
)
from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.events.recuperacion_pedida_event import RecuperacionPedidaEvent
from usuarios.domain.exceptions.email_no_valido_exception import EmailNoValidoException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from usuarios.domain.services.emails import normalizar_email


class SolicitarRecuperacionUseCase(ISolicitarRecuperacionUseCase):
    """Exista o no el email, quien pregunta no lo sabe: no se revela qué emails están registrados."""

    def __init__(
        self,
        *,
        cuentas: ICuentaCommandRepository,
        enlaces: IEnlaces,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.cuentas, self.enlaces, self.eventos, self.uow = cuentas, enlaces, eventos, uow

    def ejecutar(self, entrada: SolicitarRecuperacionInputDTO) -> None:
        try:
            usuario_id = self.cuentas.por_email(normalizar_email(entrada.email))
        except EmailNoValidoException:
            return
        if usuario_id is None:
            return
        estado = self.cuentas.estado(usuario_id)
        if estado is EstadoCuenta.PENDIENTE:  # aún no tiene contraseña que recuperar: le falta elegirla
            evento = evento_completar_registro(self.enlaces, usuario_id)
        elif estado is EstadoCuenta.ACTIVA:
            evento = RecuperacionPedidaEvent(usuario_id, self.enlaces.crear(usuario_id, "nueva-password"))
        else:
            return  # desactivada por soporte: ningún correo
        with self.uow:
            self.eventos.publicar(evento)
