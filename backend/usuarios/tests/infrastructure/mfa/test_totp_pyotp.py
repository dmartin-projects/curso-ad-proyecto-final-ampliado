"""El TOTP con pyotp, el secreto cifrado en la base de datos y los códigos de recuperación con hash (módulo 92)."""

from datetime import UTC, datetime, timedelta

import pyotp
import pytest
from cryptography.fernet import Fernet
from django.core.management import call_command

from conftest import UsuarioFactory
from usuarios.domain.bo.segundo_factor import SegundoFactor
from usuarios.infrastructure.database.repositories.segundo_factor_command_repository_orm import (
    SegundoFactorCommandRepositoryORM,
)
from usuarios.infrastructure.database.services.codigos_de_recuperacion_orm import CodigosDeRecuperacionORM
from usuarios.infrastructure.mfa.codigo_qr_segno import CodigoQrSegno
from usuarios.infrastructure.mfa.totp_pyotp import TotpPyotp
from usuarios.models import CodigoRecuperacion
from usuarios.models import SegundoFactor as FilaSegundoFactor

totp = TotpPyotp()
AHORA = datetime(2026, 10, 23, 10, 0, 10, tzinfo=UTC)


def test_el_codigo_vale_en_su_paso_y_en_los_de_al_lado():
    secreto = totp.nuevo_secreto()
    assert len(secreto) == 32  # 160 bits
    app = pyotp.TOTP(secreto)  # lo que calcula la app del móvil
    paso = app.timecode(AHORA)
    for desfase, esperado in ((-30, paso - 1), (0, paso), (30, paso + 1)):
        assert totp.paso(secreto, app.at(AHORA + timedelta(seconds=desfase)), AHORA) == esperado
    for fuera in (-60, 60):  # ±1 paso, no más
        assert totp.paso(secreto, app.at(AHORA + timedelta(seconds=fuera)), AHORA) is None
    assert totp.paso(secreto, "12345", AHORA) is None and totp.paso(secreto, "abcdef", AHORA) is None


def test_la_uri_y_el_qr():
    uri = totp.uri("JBSWY3DPEHPK3PXP", "ana@example.com")
    assert uri == "otpauth://totp/Gastos:ana%40example.com?secret=JBSWY3DPEHPK3PXP&issuer=Gastos"
    assert CodigoQrSegno().svg(uri).startswith("data:image/svg+xml")


@pytest.mark.django_db
def test_el_secreto_se_guarda_cifrado_y_se_puede_rotar_la_clave(settings):
    usuario = UsuarioFactory()
    repo = SegundoFactorCommandRepositoryORM()
    repo.guardar(SegundoFactor(usuario.pk, "JBSWY3DPEHPK3PXP", activo=True, ultimo_paso=7))
    guardado = FilaSegundoFactor.objects.get(usuario=usuario).secreto
    assert "JBSWY3DPEHPK3PXP" not in guardado and guardado.startswith("gAAAAA")  # un token de Fernet
    assert repo.de(usuario.pk).secreto == "JBSWY3DPEHPK3PXP"

    vieja = settings.MFA_CLAVES[0]
    settings.MFA_CLAVES = [Fernet.generate_key().decode(), vieja]  # la nueva delante
    assert repo.de(usuario.pk).secreto == "JBSWY3DPEHPK3PXP"  # lo viejo se sigue leyendo
    call_command("rotar_clave_mfa")
    settings.MFA_CLAVES = settings.MFA_CLAVES[:1]  # y la vieja, fuera
    assert repo.de(usuario.pk).secreto == "JBSWY3DPEHPK3PXP"


@pytest.mark.django_db
def test_los_codigos_de_recuperacion_se_guardan_con_hash_y_valen_una_vez():
    usuario = UsuarioFactory()
    codigos = CodigosDeRecuperacionORM().generar(usuario.pk)
    assert len(codigos) == 10 and all(len(c) == 19 and c.count("-") == 3 for c in codigos)  # XXXX-XXXX-XXXX-XXXX
    guardados = list(CodigoRecuperacion.objects.filter(usuario=usuario).values_list("selector", "verificador"))
    for codigo, (selector, verificador) in zip(sorted(codigos), sorted(guardados), strict=True):
        sin_guiones = codigo.replace("-", "")
        assert selector == sin_guiones[:4] and sin_guiones[4:] not in verificador  # el verificador, con PBKDF2
        assert verificador.startswith("pbkdf2_sha256$100000$")
    repo = CodigosDeRecuperacionORM()
    assert repo.usar(usuario.pk, codigos[0].lower().replace("-", " "))  # como lo escriba la persona
    assert not repo.usar(usuario.pk, codigos[0])  # una vez
    assert not repo.usar(
        usuario.pk, codigos[1][:-1] + ("A" if codigos[1][-1] != "A" else "B")
    )  # selector bueno, resto no
    assert repo.quedan(usuario.pk) == 9
    nuevos = repo.generar(usuario.pk)
    assert not repo.usar(usuario.pk, codigos[2]) and repo.usar(usuario.pk, nuevos[0])  # regenerar invalida los viejos
