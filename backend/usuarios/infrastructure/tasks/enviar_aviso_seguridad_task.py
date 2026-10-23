# usuarios/infrastructure/tasks/enviar_aviso_seguridad_task.py — un email de la cuenta (django.tasks) (módulo 92)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.tasks import task
from django.utils import translation
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from core.infrastructure.tasks.ruta_estable import ruta_estable

AVISOS = {  # lazy: se traducen al usarse, en el idioma de cada usuario
    "mfa_activado": gettext_lazy("Has activado la verificación en dos pasos."),
    "mfa_desactivado": gettext_lazy("Has desactivado la verificación en dos pasos."),
    "passkey_registrada": gettext_lazy("Has añadido la passkey «%(detalle)s»."),
    "passkey_borrada": gettext_lazy("Has quitado la passkey «%(detalle)s»."),
    # Señales de que alguien lo está intentando, y la recuperación de la cuenta
    "fallos_segundo_factor": gettext_lazy(
        "Alguien ha fallado varias veces seguidas el segundo paso al entrar en tu cuenta: quien lo intenta ya tiene "
        "tu contraseña (o ha entrado con tu proveedor)."
    ),
    "segundo_factor_bloqueado": gettext_lazy(
        "Tras demasiados fallos seguidos, la verificación en dos pasos de tu cuenta está bloqueada. Para "
        "desbloquearla, recupera tu contraseña con «¿Has olvidado tu contraseña?» en la pantalla de entrar."
    ),
    "sesion_reutilizada": gettext_lazy(
        "Hemos cerrado la sesión «%(detalle)s»: alguien ha usado un token suyo que ya no valía, y eso suele "
        "significar que se lo han copiado."
    ),
    "contrasena_recuperada": gettext_lazy(
        "Se ha elegido una contraseña nueva con el enlace de recuperación y hemos cerrado todas las sesiones "
        "abiertas. Las aplicaciones a las que diste acceso lo conservan: si no reconoces alguna, retírasela en "
        "%(aplicaciones)s."
    ),
}


@task(queue_name="emails")
@ruta_estable("usuarios.tasks")  # la ruta que guarda la cola (ruta_estable.py)
def enviar_aviso_seguridad(usuario_id: int, cambio: str, detalle: str = "") -> None:
    """Módulo 92: un cambio en la forma de entrar (MFA, passkeys) o una señal de que alguien lo intenta, al email de
    la cuenta."""
    usuario = get_user_model().objects.get(pk=usuario_id)
    datos = {"detalle": detalle, "aplicaciones": f"{settings.FRONTEND_URL}/aplicaciones"}
    with translation.override(usuario.idioma):
        send_mail(
            _("Cambio de seguridad en tu cuenta de Gastos"),
            _("%(cambio)s\n\nSi no has sido tú, entra en %(enlace)s, cierra las demás sesiones y cambia tu contraseña.")
            % {"cambio": str(AVISOS[cambio]) % datos, "enlace": f"{settings.FRONTEND_URL}/seguridad"},
            None,
            [usuario.email],
        )
