# finanzas/infrastructure/database/repositories/cuenta_command_repository_orm.py (módulo 87)
from finanzas.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from finanzas.infrastructure.database.models.cuenta_model import Cuenta as CuentaModel


class CuentaCommandRepositoryORM(ICuentaCommandRepository):
    def existe(self, hogar_id: int, cuenta_id: int) -> bool:
        return CuentaModel.objects.filter(hogar_id=hogar_id, pk=cuenta_id).exists()
