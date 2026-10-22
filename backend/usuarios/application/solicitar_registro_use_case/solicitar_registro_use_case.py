# usuarios/application/solicitar_registro_use_case/solicitar_registro_use_case.py (módulos 35 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.ports.i_enlaces import IEnlaces
from usuarios.application.shared.contrasenas import evento_completar_registro
from usuarios.application.solicitar_registro_use_case.dtos.solicitar_registro_input_dto import SolicitarRegistroInputDTO
from usuarios.application.solicitar_registro_use_case.i_solicitar_registro_use_case import ISolicitarRegistroUseCase
from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.events.registro_con_cuenta_activa_event import RegistroConCuentaActivaEvent
from usuarios.domain.exceptions.email_ya_registrado_exception import EmailYaRegistradoException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from usuarios.domain.services.emails import normalizar_email


class SolicitarRegistroUseCase(ISolicitarRegistroUseCase):
    """El registro solo pide el email: la contraseña la elige quien abre el enlace del correo (módulo 35). Quien
    rellena el formulario no sabe si el email ya tenía cuenta: eso se le dice a su dueño, por correo."""

    def __init__(
        self,
        *,
        cuentas: ICuentaCommandRepository,
        enlaces: IEnlaces,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.cuentas, self.enlaces, self.eventos, self.uow = cuentas, enlaces, eventos, uow

    def ejecutar(self, entrada: SolicitarRegistroInputDTO) -> None:
        email = normalizar_email(entrada.email)
        with self.uow:
            usuario_id = self.cuentas.por_email(email)
            if usuario_id is None:
                try:
                    usuario_id = self.cuentas.crear_pendiente(
                        email=email, nombre=entrada.nombre, apellidos=entrada.apellidos
                    )
                except EmailYaRegistradoException:  # otro registro del mismo email a la vez: como si ya estuviera
                    usuario_id = self.cuentas.por_email(email)
            match self.cuentas.estado(usuario_id):
                case EstadoCuenta.PENDIENTE:  # nueva, o registrada antes sin completar: el mismo correo
                    self.eventos.publicar(evento_completar_registro(self.enlaces, usuario_id))
                case EstadoCuenta.ACTIVA:  # ya tiene cuenta: se le avisa a ella, con un enlace para elegir otra
                    enlace = self.enlaces.crear(usuario_id, "nueva-password")
                    self.eventos.publicar(RegistroConCuentaActivaEvent(usuario_id, enlace))
                case EstadoCuenta.DESACTIVADA:  # por soporte: ningún correo
                    pass
