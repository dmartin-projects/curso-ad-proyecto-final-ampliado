# finanzas/tests/fakes/reloj_fake.py — IReloj con una fecha fija (módulo 87)
from datetime import date

from core.application.ports.i_reloj import IReloj


class RelojFake(IReloj):
    def __init__(self, hoy: date):
        self._hoy = hoy

    def hoy(self) -> date:
        return self._hoy
