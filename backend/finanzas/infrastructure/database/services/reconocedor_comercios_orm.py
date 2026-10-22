# finanzas/infrastructure/database/services/reconocedor_comercios_orm.py — el port IReconocedorComercios
# (módulos 74, 87 y 88)
from finanzas.application.ports.i_reconocedor_comercios import IReconocedorComercios
from finanzas.infrastructure.database.services.reconocimiento_comercios import (
    reconocer_comercio,
    reconocer_o_crear_comercio,
    sugerir_categoria,
)


class ReconocedorComerciosORM(IReconocedorComercios):
    """El use case solo quiere un id; cómo se encuentra (trigram, índice GIN) es cosa de la infraestructura."""

    def reconocer(self, texto: str) -> int | None:
        comercio = reconocer_comercio(texto)
        return comercio.pk if comercio else None

    def reconocer_o_crear(self, nombre: str, nif: str = "") -> tuple[int, str] | None:
        comercio = reconocer_o_crear_comercio(nombre, nif)
        return (comercio.pk, comercio.nombre) if comercio else None

    def categoria_habitual(self, hogar_id: int, comercio_id: int | None, sugerida: str = "") -> int | None:
        return sugerir_categoria(hogar_id, comercio_id, sugerida)
