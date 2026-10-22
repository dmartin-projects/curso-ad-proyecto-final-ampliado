# core/infrastructure/clock/reloj_django.py — IReloj con Django (módulo 87)
from datetime import date

from django.utils import timezone

from core.application.ports.i_reloj import IReloj


class RelojDjango(IReloj):
    def hoy(self) -> date:
        return timezone.localdate()  # en la zona horaria del proyecto (TIME_ZONE)
