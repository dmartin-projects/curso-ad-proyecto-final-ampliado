# usuarios/application/shared/apertura_de_sesion.py — abrir la sesión, ya con todos los factores (módulo 92)
import secrets

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.ports.i_sesiones import ISesiones
from usuarios.application.ports.i_tokens import ITokens
from usuarios.domain.enums.canal import Canal
from usuarios.domain.events.inicio_desde_dispositivo_nuevo_event import InicioDesdeDispositivoNuevoEvent
from usuarios.domain.services.dispositivos import describir_dispositivo, es_dispositivo_nuevo, ip_aproximada
from usuarios.domain.vo.autenticacion import Autenticacion
from usuarios.domain.vo.contexto import Contexto
from usuarios.domain.vo.sesion_abierta import SesionAbierta


class AperturaDeSesion:
    """La sesión, ya con todos los factores que hacían falta. Solo la usan IniciarSesionUseCase y el segundo paso
    (CompletarSegundoFactorUseCase): es el final común de cualquier forma de entrar."""

    def __init__(self, *, sesiones: ISesiones, tokens: ITokens, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo):
        self.sesiones, self.tokens, self.eventos, self.uow = sesiones, tokens, eventos, uow

    def abrir(self, usuario_id: int, autenticacion: Autenticacion, canal: Canal, contexto: Contexto) -> SesionAbierta:
        dispositivo = contexto.dispositivo or secrets.token_urlsafe(32)  # la primera vez: una cookie nueva
        contexto = Contexto(contexto.user_agent, contexto.ip, dispositivo)
        with self.uow:
            nuevo = es_dispositivo_nuevo(
                conocido=self.sesiones.dispositivo_conocido(usuario_id, dispositivo),
                sesiones_anteriores=self.sesiones.cuantas(usuario_id),
            )
            sid = self.sesiones.abrir(
                usuario_id=usuario_id, canal=canal, autenticacion=autenticacion, contexto=contexto
            )
            if nuevo:  # un aviso al email de la cuenta: "¿has sido tú?"
                self.eventos.publicar(
                    InicioDesdeDispositivoNuevoEvent(
                        usuario_id, describir_dispositivo(contexto.user_agent), ip_aproximada(contexto.ip),
                        autenticacion.momento,
                    )
                )  # fmt: skip
            # La sesión del authorization server la abre su adapter (django.contrib.auth.login): aquí, sin tokens
            tokens = self.tokens.emitir(usuario_id, sid) if canal is Canal.SPA else None
            if tokens is not None:
                self.sesiones.refresh_emitido(sid, tokens.jti)  # el vigente: solo ese renueva la sesión
        return SesionAbierta(sid, autenticacion, tokens, dispositivo)
