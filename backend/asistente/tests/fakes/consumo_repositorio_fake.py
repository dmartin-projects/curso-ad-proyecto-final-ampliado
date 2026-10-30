# asistente/tests/fakes/consumo_repositorio_fake.py (módulo 98)
from decimal import Decimal

from asistente.domain.read_models.coste_por_hogar import CostePorHogar
from asistente.domain.repositories.i_consumo_query_service import IConsumoQueryService
from asistente.domain.repositories.i_consumo_repository import IConsumoRepository


class ConsumoRepositorioFake(IConsumoRepository, IConsumoQueryService):
    """Los dos lados sobre la misma lista: lo que se apunta se suma al consultar."""

    def __init__(self):
        self.consumos = []

    def anotar(self, consumos):
        self.consumos.extend(consumos)

    def tokens(self, usuario_id, hogar_id, desde):
        return sum(
            c.uso.total
            for c in self.consumos
            if (c.usuario_id, c.hogar_id) == (usuario_id, hogar_id) and c.momento >= desde
        )

    def coste(self, hogar_id, desde):
        return sum(
            (c.coste or Decimal(0) for c in self.consumos if c.hogar_id == hogar_id and c.momento >= desde), Decimal(0)
        )

    def por_hogar(self, desde, hasta):
        grupos: dict = {}
        for c in self.consumos:
            if desde <= c.momento < hasta:
                grupos.setdefault((c.hogar_id, c.modelo), []).append(c)
        filas = [
            CostePorHogar(
                hogar_id=h,
                hogar=f"Hogar {h}",
                modelo=m,
                llamadas=len(cs),
                tokens_entrada=sum(c.uso.entrada for c in cs),
                tokens_cache=sum(c.uso.cache for c in cs),
                tokens_salida=sum(c.uso.salida for c in cs),
                coste=sum((c.coste or Decimal(0) for c in cs), Decimal(0)),
                sin_precio=sum(c.coste is None for c in cs),
            )
            for (h, m), cs in grupos.items()
        ]
        return tuple(sorted(filas, key=lambda f: (-f.coste, f.hogar_id, f.modelo)))
