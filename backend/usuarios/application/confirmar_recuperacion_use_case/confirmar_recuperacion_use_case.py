# usuarios/application/confirmar_recuperacion_use_case/confirmar_recuperacion_use_case.py (módulos 35, 88 y 92)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.confirmar_recuperacion_use_case.dtos.confirmar_recuperacion_input_dto import (
    ConfirmarRecuperacionInputDTO,
)
from usuarios.application.confirmar_recuperacion_use_case.i_confirmar_recuperacion_use_case import (
    IConfirmarRecuperacionUseCase,
)
from usuarios.application.ports.i_enlaces import IEnlaces
from usuarios.application.ports.i_politica_de_contrasenas import IPoliticaDeContrasenas
from usuarios.application.ports.i_sesiones import ISesiones
from usuarios.application.shared.contrasenas import exigir_politica
from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.enlace_no_valido_exception import EnlaceNoValidoException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository


class ConfirmarRecuperacionUseCase(IConfirmarRecuperacionUseCase):
    """Módulo 92: quien recupera la contraseña suele hacerlo porque cree que alguien más la tiene. Así que, como al
    cambiarla, se cierran TODAS las sesiones abiertas (las de quien la tuviera), y el segundo factor bloqueado por el
    techo de fallos se desbloquea (la persona ha demostrado que el email es suyo, y la contraseña ya es otra).

    Las aplicaciones a las que dio acceso (OAuth, módulo 90) NO se desconectan: cada una es un permiso que dio a
    sabiendas, con sus scopes (nunca la cuenta, la seguridad ni el backoffice), y muchas no tienen a nadie delante
    para volver a conectarse (el CLI en un servidor, un servicio). Pero sí se le avisa, con el enlace a «Aplicaciones
    conectadas»: si no reconoce alguna, se la retira con un clic."""

    def __init__(
        self,
        *,
        cuentas: ICuentaCommandRepository,
        politica: IPoliticaDeContrasenas,
        enlaces: IEnlaces,
        sesiones: ISesiones,
        segundos: ISegundoFactorCommandRepository,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.cuentas, self.politica, self.enlaces = cuentas, politica, enlaces
        self.sesiones, self.segundos, self.eventos, self.uow = sesiones, segundos, eventos, uow

    def ejecutar(self, entrada: ConfirmarRecuperacionInputDTO) -> None:
        usuario_id = self.enlaces.usuario_de(entrada.uid, entrada.token)
        if usuario_id is None or self.cuentas.estado(usuario_id) is not EstadoCuenta.ACTIVA:
            raise EnlaceNoValidoException()  # un registro pendiente se completa con CompletarRegistroUseCase
        exigir_politica(self.politica, entrada.password, "password", usuario_id=usuario_id)
        with self.uow:
            self.cuentas.cambiar_contrasena(usuario_id, entrada.password)  # cambia el hash: el enlace deja de valer
            self.sesiones.cerrar_todas(usuario_id)
            segundo = self.segundos.de(usuario_id, bloquear=True)
            if segundo.fallos:
                segundo.desbloquear()
                self.segundos.guardar(segundo)
            self.eventos.publicar(SeguridadCambiadaEvent(usuario_id, "contrasena_recuperada"))
