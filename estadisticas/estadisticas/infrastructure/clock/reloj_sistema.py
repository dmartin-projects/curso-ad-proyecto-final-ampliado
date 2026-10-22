# estadisticas/infrastructure/clock/reloj_sistema.py — IReloj con el reloj del sistema (módulo 89)
from datetime import date

from estadisticas.application.ports.i_reloj import IReloj


class RelojSistema(IReloj):
    def hoy(self) -> date:
        return date.today()
