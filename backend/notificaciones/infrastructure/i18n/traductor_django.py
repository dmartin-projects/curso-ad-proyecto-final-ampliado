# notificaciones/infrastructure/i18n/traductor_django.py — ITraductor con el i18n de Django (módulos 46 y 88)
from django.utils import translation

from notificaciones.application.ports.i_traductor import ITraductor


class TraductorDjango(ITraductor):
    def traducir(self, plantilla, idioma: str, contexto: dict) -> str:
        # `plantilla`: un gettext_lazy con marcadores %(nombre)s; se traduce en el idioma de cada destinatario (RNF7)
        with translation.override(idioma):
            return str(plantilla) % contexto
