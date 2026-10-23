# usuarios/application/registrar_passkey_use_case/registrar_passkey_use_case.py — guardar una passkey nueva (módulo 92)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.ports.i_retos import IRetos
from usuarios.application.ports.i_webauthn import IWebAuthn
from usuarios.application.registrar_passkey_use_case.dtos.registrar_passkey_input_dto import RegistrarPasskeyInputDTO
from usuarios.application.registrar_passkey_use_case.i_registrar_passkey_use_case import IRegistrarPasskeyUseCase
from usuarios.domain.bo.passkey import Passkey
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.passkey_no_valida_exception import PasskeyNoValidaException
from usuarios.domain.repositories.i_passkey_command_repository import IPasskeyCommandRepository


class RegistrarPasskeyUseCase(IRegistrarPasskeyUseCase):
    def __init__(
        self,
        *,
        passkeys: IPasskeyCommandRepository,
        webauthn: IWebAuthn,
        retos: IRetos,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.passkeys, self.webauthn, self.retos, self.eventos, self.uow = passkeys, webauthn, retos, eventos, uow

    def ejecutar(self, entrada: RegistrarPasskeyInputDTO) -> int:
        challenge = self.retos.consumir(f"registro:{entrada.usuario_id}")
        if challenge is None:
            raise PasskeyNoValidaException()
        nueva = self.webauthn.comprobar_registro(entrada.respuesta, challenge)  # PasskeyNoValidaException
        if self.passkeys.por_credencial(nueva.credencial_id) is not None:
            raise PasskeyNoValidaException()
        passkey = Passkey(
            entrada.usuario_id, nueva.credencial_id, nueva.clave_publica, nueva.contador, entrada.nombre,
            nueva.sincronizada, nueva.transportes,
        )  # fmt: skip
        with self.uow:
            self.passkeys.guardar(passkey)
            self.eventos.publicar(SeguridadCambiadaEvent(entrada.usuario_id, "passkey_registrada", passkey.nombre))
        return passkey.id
