# usuarios/infrastructure/database/repositories/segundo_factor_command_repository_orm.py — ISegundoFactorCommandRepository con el ORM (módulo 92)
from usuarios.domain.bo.segundo_factor import SegundoFactor
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository
from usuarios.infrastructure.database.cifrado import cifrar, descifrar
from usuarios.infrastructure.database.models.segundo_factor_model import SegundoFactor as SegundoFactorModel


class SegundoFactorCommandRepositoryORM(ISegundoFactorCommandRepository):
    def de(self, usuario_id, *, bloquear=False):
        filas = SegundoFactorModel.objects.filter(usuario_id=usuario_id)
        fila = (filas.select_for_update() if bloquear else filas).first()
        if fila is None:
            return SegundoFactor(usuario_id)
        return SegundoFactor(
            usuario_id, descifrar(fila.secreto) if fila.secreto else None, fila.activo, fila.ultimo_paso,
            fila.fallos, fila.bloqueado_hasta,
        )  # fmt: skip

    def guardar(self, segundo):
        SegundoFactorModel.objects.update_or_create(
            usuario_id=segundo.usuario_id,
            defaults={
                "secreto": cifrar(segundo.secreto) if segundo.secreto else "",  # nunca en claro en la BD
                "activo": segundo.activo,
                "ultimo_paso": segundo.ultimo_paso,
                "fallos": segundo.fallos,
                "bloqueado_hasta": segundo.bloqueado_hasta,
            },
        )
