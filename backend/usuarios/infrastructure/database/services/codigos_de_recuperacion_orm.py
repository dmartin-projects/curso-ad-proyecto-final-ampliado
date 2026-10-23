# usuarios/infrastructure/database/services/codigos_de_recuperacion_orm.py — ICodigosDeRecuperacion con el ORM (módulo 92)
import hashlib
import hmac
import secrets

from django.db import transaction
from django.utils import timezone

from usuarios.application.ports.i_codigos_de_recuperacion import ICodigosDeRecuperacion
from usuarios.infrastructure.database.models.codigo_recuperacion_model import (
    CodigoRecuperacion as CodigoRecuperacionModel,
)

# Los códigos de recuperación: 16 caracteres de un alfabeto sin los que se confunden (0/O, 1/I/L, U/V), en 4 grupos.
# Los 4 primeros son el selector (encuentra la fila); los 12 restantes, el verificador: 29^12 ≈ 2^58 posibilidades.
ALFABETO = "ABCDEFGHJKMNPQRSTWXYZ23456789"


ITERACIONES = 100_000  # PBKDF2: 59 bits de azar no necesitan el millón de una contraseña humana; generar 10, al momento


def _derivar(verificador: str, sal: str, iteraciones: int = ITERACIONES) -> str:
    return hashlib.pbkdf2_hmac("sha256", verificador.encode(), sal.encode(), iteraciones).hex()


def normalizar_codigo(codigo: str) -> str:
    """'abcd-efgh jkmn-pqrs' → 'ABCDEFGHJKMNPQRS': como lo escriba la persona."""
    return "".join(c for c in (codigo or "").upper() if c.isalnum())


class CodigosDeRecuperacionORM(ICodigosDeRecuperacion):
    def generar(self, usuario_id):
        codigos, filas = [], []
        while len(codigos) < 10:
            codigo = "".join(secrets.choice(ALFABETO) for _ in range(16))
            if any(c[:4] == codigo[:4] for c in codigos):
                continue  # el selector, único por cuenta
            sal = secrets.token_hex(16)
            filas.append(CodigoRecuperacionModel(
                usuario_id=usuario_id, selector=codigo[:4],
                verificador=f"pbkdf2_sha256${ITERACIONES}${sal}${_derivar(codigo[4:], sal)}",
            ))  # fmt: skip
            codigos.append(codigo)
        with transaction.atomic():
            CodigoRecuperacionModel.objects.filter(usuario_id=usuario_id).delete()  # los anteriores, fuera
            CodigoRecuperacionModel.objects.bulk_create(filas)
        return ["-".join(c[i : i + 4] for i in range(0, 16, 4)) for c in codigos]

    def usar(self, usuario_id, codigo):
        codigo = normalizar_codigo(codigo)
        if len(codigo) != 16:
            return False
        fila = CodigoRecuperacionModel.objects.filter(
            usuario_id=usuario_id, selector=codigo[:4], usado__isnull=True
        ).first()
        if fila is None:
            return False
        _, iteraciones, sal, esperado = fila.verificador.split("$")
        if not hmac.compare_digest(_derivar(codigo[4:], sal, int(iteraciones)), esperado):
            return False
        # Un solo uso, también con dos peticiones a la vez: solo una cambia la fila de "sin usar" a "usado"
        return CodigoRecuperacionModel.objects.filter(pk=fila.pk, usado__isnull=True).update(usado=timezone.now()) == 1

    def quedan(self, usuario_id):
        return CodigoRecuperacionModel.objects.filter(usuario_id=usuario_id, usado__isnull=True).count()

    def borrar(self, usuario_id):
        CodigoRecuperacionModel.objects.filter(usuario_id=usuario_id).delete()
