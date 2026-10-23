# usuarios/application/renovar_sesion_use_case/renovar_sesion_use_case.py — renovar una sesión de la SPA (POST /auth/refresh/) (módulo 92)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.ports.i_sesiones import ISesiones
from usuarios.application.renovar_sesion_use_case.dtos.renovar_sesion_input_dto import RenovarSesionInputDTO
from usuarios.application.renovar_sesion_use_case.i_renovar_sesion_use_case import IRenovarSesionUseCase
from usuarios.domain.enums.estado_renovacion import EstadoRenovacion
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.sesion_cerrada_exception import SesionCerradaException


class RenovarSesionUseCase(IRenovarSesionUseCase):
    """POST /auth/refresh/: renueva la sesión si sigue abierta (no cerrada desde otro dispositivo, ni al cambiar o
    recuperar la contraseña, ni caducada) y si el refresh es el vigente: cada uso lo rota, y uno ya rotado que vuelve
    es que lo tiene alguien más (RFC 9700 §4.14.2, detección de reutilización): la sesión se cierra para los dos y
    llega un aviso. La excepción: el anterior, segundos después de rotarlo (otra pestaña de la misma SPA que pidió su
    refresh a la vez): vale para un access, sin rotar.

    Devuelve si hay que rotar (True) o solo dar un access (False, la otra pestaña)."""

    def __init__(self, *, sesiones: ISesiones, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo):
        self.sesiones, self.eventos, self.uow = sesiones, eventos, uow

    def ejecutar(self, entrada: RenovarSesionInputDTO) -> bool:
        if not entrada.sid:
            raise SesionCerradaException()
        with self.uow:
            renovacion = self.sesiones.rotar(
                entrada.sid, presentado=entrada.presentado, nuevo=entrada.jti, contexto=entrada.contexto
            )
            if renovacion.estado is EstadoRenovacion.REUTILIZADA:
                self.sesiones.cerrar(renovacion.usuario_id, entrada.sid)
                self.eventos.publicar(
                    SeguridadCambiadaEvent(renovacion.usuario_id, "sesion_reutilizada", renovacion.descripcion)
                )
        if renovacion.estado in (EstadoRenovacion.REUTILIZADA, EstadoRenovacion.CERRADA):
            raise SesionCerradaException()
        return renovacion.estado is EstadoRenovacion.ROTADA
