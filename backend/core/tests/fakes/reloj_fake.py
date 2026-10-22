# core/tests/fakes/reloj_fake.py — IReloj con una fecha y una hora fijas (módulos 87 y 88)
from datetime import UTC, date, datetime, time

from core.application.ports.i_reloj import IReloj


class RelojFake(IReloj):
    def __init__(self, hoy: date, ahora: datetime | None = None):
        self._hoy = hoy
        self._ahora = ahora or datetime.combine(hoy, time(12, 0), tzinfo=UTC)

    def hoy(self) -> date:
        return self._hoy

    def ahora(self) -> datetime:
        return self._ahora
