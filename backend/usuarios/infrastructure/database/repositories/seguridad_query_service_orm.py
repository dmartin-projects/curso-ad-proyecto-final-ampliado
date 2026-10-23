# usuarios/infrastructure/database/repositories/seguridad_query_service_orm.py — «Seguridad» (módulo 92)
from usuarios.domain.read_models.passkey_registrada import PasskeyRegistrada
from usuarios.domain.read_models.seguridad import Seguridad
from usuarios.domain.repositories.i_seguridad_query_service import ISeguridadQueryService
from usuarios.infrastructure.database.models.codigo_recuperacion_model import (
    CodigoRecuperacion as CodigoRecuperacionModel,
)
from usuarios.infrastructure.database.models.passkey_model import Passkey as PasskeyModel
from usuarios.infrastructure.database.models.segundo_factor_model import SegundoFactor as SegundoFactorModel


class SeguridadQueryServiceORM(ISeguridadQueryService):
    def de_usuario(self, usuario_id: int) -> Seguridad:
        return Seguridad(
            mfa=SegundoFactorModel.objects.filter(usuario_id=usuario_id, activo=True).exists(),
            codigos_restantes=CodigoRecuperacionModel.objects.filter(usuario_id=usuario_id, usado__isnull=True).count(),
            passkeys=tuple(
                PasskeyRegistrada(p.pk, p.nombre, p.sincronizada, p.creada, p.ultimo_uso)
                for p in PasskeyModel.objects.filter(usuario_id=usuario_id).order_by("creada")
            ),
        )
