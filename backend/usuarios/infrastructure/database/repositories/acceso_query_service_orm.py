# usuarios/infrastructure/database/repositories/acceso_query_service_orm.py — «Métodos de acceso» (módulo 91)
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.read_models.acceso import Acceso
from usuarios.domain.read_models.identidad_vinculada import IdentidadVinculada
from usuarios.domain.repositories.i_acceso_query_service import IAccesoQueryService
from usuarios.infrastructure.database.models.identidad_externa_model import (
    IdentidadExterna as IdentidadExternaModel,
)
from usuarios.infrastructure.database.models.usuario_model import Usuario as UsuarioModel


class AccesoQueryServiceORM(IAccesoQueryService):
    def de_usuario(self, usuario_id: int) -> Acceso:
        filas = IdentidadExternaModel.objects.filter(usuario_id=usuario_id).order_by("creada")
        return Acceso(
            contrasena=UsuarioModel.objects.get(pk=usuario_id).has_usable_password(),
            identidades=tuple(
                IdentidadVinculada(f.proveedor, Proveedor(f.proveedor).nombre, f.email, f.creada, f.ultimo_uso)
                for f in filas
            ),
        )
