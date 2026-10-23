# usuarios/tests/fakes/reloj_del_sistema_fake.py — IReloj con la hora de verdad (módulo 92)
from datetime import UTC, date, datetime

from core.application.ports.i_reloj import IReloj


class RelojDelSistemaFake(IReloj):
    """La hora de verdad, sin Django: los códigos TOTP del TotpFake y los bloqueos del segundo factor van con ella
    (un reloj fijo no deja ver que una reautenticación es posterior al login)."""

    def hoy(self) -> date:
        return datetime.now(UTC).date()

    def ahora(self) -> datetime:
        return datetime.now(UTC)
