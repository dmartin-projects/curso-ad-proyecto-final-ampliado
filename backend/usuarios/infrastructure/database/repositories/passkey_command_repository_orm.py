# usuarios/infrastructure/database/repositories/passkey_command_repository_orm.py — IPasskeyCommandRepository con el ORM (módulo 92)
import secrets

from django.utils import timezone

from usuarios.domain.bo.passkey import Passkey
from usuarios.domain.exceptions.passkey_no_encontrada_exception import PasskeyNoEncontradaException
from usuarios.domain.repositories.i_passkey_command_repository import IPasskeyCommandRepository
from usuarios.infrastructure.database.models.manija_webauthn_model import ManijaWebAuthn as ManijaWebAuthnModel
from usuarios.infrastructure.database.models.passkey_model import Passkey as PasskeyModel


def _a_dominio(fila: PasskeyModel) -> Passkey:
    return Passkey(
        fila.usuario_id, bytes(fila.credencial_id), bytes(fila.clave_publica), fila.contador, fila.nombre,
        fila.sincronizada, tuple(fila.transportes), fila.pk,
    )  # fmt: skip


class PasskeyCommandRepositoryORM(IPasskeyCommandRepository):
    def de_usuario(self, usuario_id):
        return [_a_dominio(f) for f in PasskeyModel.objects.filter(usuario_id=usuario_id).order_by("creada")]

    def por_credencial(self, credencial_id):
        fila = PasskeyModel.objects.filter(credencial_id=credencial_id).first()
        return _a_dominio(fila) if fila else None

    def guardar(self, passkey):
        if passkey.id is None:
            passkey.id = PasskeyModel.objects.create(
                usuario_id=passkey.usuario_id, credencial_id=passkey.credencial_id,
                clave_publica=passkey.clave_publica, contador=passkey.contador, nombre=passkey.nombre,
                sincronizada=passkey.sincronizada, transportes=list(passkey.transportes),
            ).pk  # fmt: skip
        else:
            PasskeyModel.objects.filter(pk=passkey.id).update(
                contador=passkey.contador, sincronizada=passkey.sincronizada, ultimo_uso=timezone.now()
            )

    def borrar(self, usuario_id, passkey_id):
        fila = PasskeyModel.objects.filter(usuario_id=usuario_id, pk=passkey_id).first()
        if fila is None:
            raise PasskeyNoEncontradaException()
        fila.delete()
        return fila.nombre

    def manija(self, usuario_id):
        fila, _ = ManijaWebAuthnModel.objects.get_or_create(
            usuario_id=usuario_id, defaults={"manija": secrets.token_bytes(32)}
        )
        return bytes(fila.manija)

    def usuario_de_manija(self, manija):
        return ManijaWebAuthnModel.objects.filter(manija=manija).values_list("usuario_id", flat=True).first()
