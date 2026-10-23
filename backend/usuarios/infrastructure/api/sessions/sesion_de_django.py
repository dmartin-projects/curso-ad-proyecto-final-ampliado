# usuarios/infrastructure/api/sessions/sesion_de_django.py — la sesión de Django de las páginas del authorization
# server, atada a su sesión de Gastos (módulo 92)
#
#   entrar_en_django          la sesión de Django de las páginas del authorization server, con su autenticación
#   salir_de_django           y al revés: cerrarla cierra también su sesión de Gastos
#   sesion_de_django_vigente  ¿sigue abierta su sesión de Gastos? (oauth/infrastructure/web/middleware/)
from django.contrib.auth import get_user_model, login, logout

from core.domain.exceptions.dominio_exception import DominioException
from usuarios.application.cerrar_sesion_use_case.dtos.cerrar_sesion_input_dto import CerrarSesionInputDTO
from usuarios.application.obtener_autenticacion_use_case.dtos.obtener_autenticacion_input_dto import (
    ObtenerAutenticacionInputDTO,
)
from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO
from usuarios.infrastructure import container

SESION_DJANGO = "gastos_sesion"  # en la sesión de Django del authorization server: sid, amr, acr, auth_time
PENDIENTE_DJANGO = "gastos_mfa_pendiente"  # ídem: la clave del login pendiente (falta el segundo factor)
SEGUNDO_FACTOR_AUTORIZACION = "/api/oauth/segundo-factor/"  # la página del segundo paso en el authorization server


def entrar_en_django(request, sesion: SesionAbiertaOutputDTO, usuario_id: int) -> None:
    """La sesión de las páginas del authorization server (cookie solo para /api/oauth/), con lo que el ID token tiene
    que contar de esta autenticación: cuándo (auth_time) y cómo (amr, acr)."""
    login(request, get_user_model().objects.get(pk=usuario_id), backend="django.contrib.auth.backends.ModelBackend")
    request.session.pop(PENDIENTE_DJANGO, None)
    request.session[SESION_DJANGO] = datos_de_sesion(sesion)


def salir_de_django(request) -> None:
    """Salir del authorization server («¿No eres tú?», o volver a entrar con prompt=login o max_age): su sesión de
    Gastos se cierra también. Si no, seguiría «abierta» en «Sesiones» sin que nadie pudiera usarla."""
    if request.user.is_authenticated and (datos := request.session.get(SESION_DJANGO)):
        try:
            container.cerrar_sesion().ejecutar(CerrarSesionInputDTO(request.user.pk, datos["sid"]))
        except DominioException:  # ya cerrada (desde «Sesiones») o caducada
            pass
    logout(request)


def datos_de_sesion(sesion: SesionAbiertaOutputDTO) -> dict:
    return {
        "sid": sesion.sid,
        "amr": sesion.autenticacion.amr,
        "acr": sesion.autenticacion.acr,
        "auth_time": int(sesion.autenticacion.momento.timestamp()),
    }


def sesion_de_django_vigente(request) -> bool:
    """¿La sesión de Django del authorization server es de una sesión de Gastos abierta? Sin ella (una sesión de
    antes del módulo 92) o cerrada desde «Sesiones», no."""
    datos = request.session.get(SESION_DJANGO)
    return (
        bool(datos)
        and container.obtener_autenticacion().ejecutar(ObtenerAutenticacionInputDTO(datos["sid"])) is not None
    )
