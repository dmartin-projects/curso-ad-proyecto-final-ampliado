# finanzas/infrastructure/database/services/reconocedor_comercios_orm.py — el port IReconocedorComercios
# (módulos 74 y 87)
from finanzas.application.ports.i_reconocedor_comercios import IReconocedorComercios
from finanzas.infrastructure.database.services.reconocimiento_comercios import reconocer_comercio


class ReconocedorComerciosORM(IReconocedorComercios):
    """El use case solo quiere un id; cómo se encuentra (trigram, índice GIN) es cosa de la infraestructura."""

    def reconocer(self, texto: str) -> int | None:
        comercio = reconocer_comercio(texto)
        return comercio.pk if comercio else None
