# asistente/infrastructure/database/repositories/consumo_repository_orm.py (módulo 98)
from asistente.domain.repositories.i_consumo_repository import IConsumoRepository
from asistente.infrastructure.database.models.consumo_model import Consumo as ConsumoModel


class ConsumoRepositoryORM(IConsumoRepository):
    def anotar(self, consumos):
        ConsumoModel.objects.bulk_create(
            [
                ConsumoModel(
                    usuario_id=c.usuario_id,
                    hogar_id=c.hogar_id,
                    conversacion_id=c.conversacion_id,
                    canal=str(c.canal),
                    modelo=c.modelo,
                    tokens_entrada=c.uso.entrada,
                    tokens_cache=c.uso.cache,
                    tokens_salida=c.uso.salida,
                    tokens_razonamiento=c.uso.razonamiento,
                    coste=c.coste,
                    momento=c.momento,
                )
                for c in consumos
            ]
        )
