# core/infrastructure/clock/reloj_django.py — IReloj con Django (módulos 87 y 88)
from datetime import date, datetime

from django.utils import timezone

from core.application.ports.i_reloj import IReloj


class RelojDjango(IReloj):
    def hoy(self) -> date:
        return timezone.localdate()  # en la zona horaria del proyecto (TIME_ZONE)

    def ahora(self) -> datetime:
        return timezone.now()  # aware, en UTC: como auto_now y los DateTimeField
