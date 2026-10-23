# usuarios/application/borrar_passkey_use_case/borrar_passkey_use_case.py — quitar una passkey de MI cuenta (módulo 92)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.borrar_passkey_use_case.dtos.borrar_passkey_input_dto import BorrarPasskeyInputDTO
from usuarios.application.borrar_passkey_use_case.i_borrar_passkey_use_case import IBorrarPasskeyUseCase
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from usuarios.domain.repositories.i_identidad_command_repository import IIdentidadCommandRepository
from usuarios.domain.repositories.i_passkey_command_repository import IPasskeyCommandRepository
from usuarios.domain.vo.metodos_de_acceso import MetodosDeAcceso


class BorrarPasskeyUseCase(IBorrarPasskeyUseCase):
    """Una passkey también es una forma de entrar: no la última."""

    def __init__(
        self,
        *,
        passkeys: IPasskeyCommandRepository,
        cuentas: ICuentaCommandRepository,
        identidades: IIdentidadCommandRepository,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.passkeys, self.cuentas, self.identidades, self.eventos, self.uow = (
            passkeys, cuentas, identidades, eventos, uow
        )  # fmt: skip

    def ejecutar(self, entrada: BorrarPasskeyInputDTO) -> None:
        with self.uow:
            self.cuentas.bloquear(entrada.usuario_id)
            MetodosDeAcceso(
                contrasena=self.cuentas.tiene_contrasena(entrada.usuario_id),
                proveedores=frozenset(self.identidades.de_usuario(entrada.usuario_id)),
                passkeys=len(self.passkeys.de_usuario(entrada.usuario_id)),
            ).sin_una_passkey()  # UltimoMetodoDeAccesoException
            nombre = self.passkeys.borrar(entrada.usuario_id, entrada.passkey_id)  # PasskeyNoEncontradaException
            self.eventos.publicar(SeguridadCambiadaEvent(entrada.usuario_id, "passkey_borrada", nombre))
