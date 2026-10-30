# asistente/management/commands/coste_asistente.py — lo que ha costado el asistente, por hogar y modelo (módulo 98)
"""manage.py coste_asistente [--mes 2026-10] — del libro de cuentas (asistente_consumo), no de Prometheus: en las
métricas no hay hogares (serían miles de series). Por defecto, el mes en curso (en UTC, como factura el proveedor)."""

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from asistente.application.informe_de_costes_use_case.dtos.informe_de_costes_input_dto import InformeDeCostesInputDTO
from asistente.infrastructure import container


def _mes(texto: str) -> date:
    try:
        return date.fromisoformat(f"{texto}-01")
    except ValueError as e:
        raise CommandError(f"--mes es AAAA-MM: {texto!r}") from e


class Command(BaseCommand):
    help = "Coste del asistente en un mes, por hogar y modelo."

    def add_arguments(self, parser):
        parser.add_argument("--mes", type=_mes, help="AAAA-MM (por defecto, el mes en curso)")

    def handle(self, *args, **o):
        desde = o["mes"] or timezone.now().date().replace(day=1)
        hasta = (desde.replace(day=28) + timedelta(days=4)).replace(day=1)  # el día 1 del mes siguiente
        filas = container.informe_de_costes().ejecutar(InformeDeCostesInputDTO(desde, hasta))
        self.stdout.write(f"Coste del asistente, {desde:%Y-%m} (USD, con los precios de cada momento)\n")
        self.stdout.write(f"{'hogar':<28} {'modelo':<24} {'apuntes':>8} {'entrada':>10} {'caché':>8} "
                          f"{'salida':>8} {'coste':>10}")  # fmt: skip
        total = Decimal(0)
        for f in filas:
            hogar = f"{f.hogar[:22]} ({f.hogar_id})" if f.hogar_id else f.hogar
            coste = f"{f.coste:.4f}" + ("*" if f.sin_precio else "")
            self.stdout.write(
                f"{hogar:<28} {f.modelo:<24} {f.llamadas:>8} {f.tokens_entrada:>10} {f.tokens_cache:>8} "
                f"{f.tokens_salida:>8} {coste:>10}"
            )
            total += f.coste
        self.stdout.write(f"{'total':<28} {'':<24} {sum(f.llamadas for f in filas):>8} "
                          f"{sum(f.tokens_entrada for f in filas):>10} {sum(f.tokens_cache for f in filas):>8} "
                          f"{sum(f.tokens_salida for f in filas):>8} {total:>10.4f}")  # fmt: skip
        if any(f.sin_precio for f in filas):
            self.stdout.write("* hay apuntes de modelos sin precio en ASISTENTE_PRECIOS: no suman")
