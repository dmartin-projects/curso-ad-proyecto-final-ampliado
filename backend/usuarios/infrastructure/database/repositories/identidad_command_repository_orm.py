# usuarios/infrastructure/database/repositories/identidad_command_repository_orm.py — IIdentidadCommandRepository con el ORM (módulo 91)
from django.db import IntegrityError, transaction
from django.utils import timezone

from core.infrastructure.database.guardado import nombre_constraint
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.identidad_de_otra_cuenta_exception import IdentidadDeOtraCuentaException
from usuarios.domain.exceptions.proveedor_ya_vinculado_exception import ProveedorYaVinculadoException
from usuarios.domain.repositories.i_identidad_command_repository import IIdentidadCommandRepository
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.infrastructure.database.models.identidad_externa_model import (
    IdentidadExterna as IdentidadExternaModel,
)


class IdentidadCommandRepositoryORM(IIdentidadCommandRepository):
    # La constraint que salta → el error del dominio (dos vueltas a la vez con la misma identidad)
    errores = {
        "identidad_externa_unica": IdentidadDeOtraCuentaException,
        "un_proveedor_por_usuario": ProveedorYaVinculadoException,
    }

    def dueno(self, proveedor, sub):
        filas = IdentidadExternaModel.objects.filter(proveedor=proveedor, sub=sub)
        return filas.values_list("usuario_id", flat=True).first()

    def de_usuario(self, usuario_id):
        filas = IdentidadExternaModel.objects.filter(usuario_id=usuario_id).values_list("proveedor", "sub")
        return {Proveedor(p): sub for p, sub in filas}

    def vincular(self, usuario_id, perfil: PerfilExterno):
        try:
            with transaction.atomic():  # savepoint: el error del dominio no rompe la transacción del use case
                IdentidadExternaModel.objects.create(
                    usuario_id=usuario_id, proveedor=perfil.proveedor, sub=perfil.sub, email=perfil.email or "",
                    ultimo_uso=timezone.now(),
                )  # fmt: skip
        except IntegrityError as e:
            if error := self.errores.get(nombre_constraint(e)):
                raise error(proveedor=perfil.proveedor.nombre) from e
            raise

    def anotar_uso(self, proveedor, sub):
        IdentidadExternaModel.objects.filter(proveedor=proveedor, sub=sub).update(ultimo_uso=timezone.now())

    def desvincular(self, usuario_id, proveedor):
        IdentidadExternaModel.objects.filter(usuario_id=usuario_id, proveedor=proveedor).delete()
