"""Módulo 86, ejercicio 2: anonimizar en staging una copia de producción."""

import pytest
from django.contrib.auth import authenticate
from django.core.management import CommandError, call_command

from conftest import CuentaFactory, MembresiaFactory, MovimientoFactory
from core.models import RegistroAuditoria
from hogares.models import Invitacion
from notificaciones.models import Notificacion
from usuarios.models import IdentidadExterna, Passkey, SegundoFactor, Sesion
from usuarios.tests.infrastructure.ayudas_mfa import activar_mfa

pytestmark = pytest.mark.django_db
CLAVE = "clave-de-staging-123"


@pytest.fixture
def datos_reales():
    m = MembresiaFactory(usuario__email="ana.garcia@gmail.com", usuario__nombre="Ana García", hogar__nombre="Casa Ana")
    cuenta = CuentaFactory(hogar=m.hogar, iban="ES9121000418450200051332")
    mov = MovimientoFactory(cuenta=cuenta, concepto="MERCADONA", notas="regalo para Luis", importe=-23)
    Invitacion.objects.create(hogar=m.hogar, email="luis@gmail.com", invitado_por=m.usuario)
    Notificacion.objects.create(usuario=m.usuario, tipo="informe_listo", titulo="Tu informe, Ana")
    IdentidadExterna.objects.create(usuario=m.usuario, proveedor="google", sub="1081", email="ana.garcia@gmail.com")
    activar_mfa(m.usuario)  # módulo 92
    Passkey.objects.create(usuario=m.usuario, credencial_id=b"c", clave_publica=b"k", nombre="Móvil")
    RegistroAuditoria.objects.create(
        usuario=m.usuario, accion="crear", objeto=mov, representacion=str(mov), cambios={"notas": mov.notas}
    )
    return m, mov


def test_anonimiza_y_conserva_lo_util(datos_reales, monkeypatch):
    m, mov = datos_reales
    monkeypatch.setenv("ENTORNO", "staging")
    monkeypatch.setenv("STAGING_PASSWORD", CLAVE)
    call_command("anonimizar", "--si")

    m.usuario.refresh_from_db()
    m.hogar.refresh_from_db()
    mov.refresh_from_db()
    assert m.usuario.email == f"usuario{m.usuario.pk}@staging.invalid" and m.usuario.nombre == f"Usuario {m.usuario.pk}"
    assert m.hogar.nombre == f"Hogar {m.hogar.pk}"
    assert mov.cuenta.__class__.objects.get(pk=mov.cuenta_id).iban == ""
    assert mov.notas == "" and mov.concepto == "MERCADONA" and mov.importe == -23  # lo útil, intacto
    assert Invitacion.objects.get().email.endswith("@staging.invalid")
    assert not Notificacion.objects.exists() and not RegistroAuditoria.objects.exists()
    assert not IdentidadExterna.objects.exists()  # módulo 91
    assert not (SegundoFactor.objects.exists() or Passkey.objects.exists() or Sesion.objects.exists())  # módulo 92
    assert authenticate(email=m.usuario.email, password=CLAVE) == m.usuario  # se puede entrar como él


@pytest.mark.parametrize("entorno", [None, "produccion"])
def test_fuera_de_staging_no_hace_nada(datos_reales, monkeypatch, entorno):
    if entorno:
        monkeypatch.setenv("ENTORNO", entorno)
    else:
        monkeypatch.delenv("ENTORNO", raising=False)
    monkeypatch.setenv("STAGING_PASSWORD", CLAVE)
    with pytest.raises(CommandError, match="Solo en staging"):
        call_command("anonimizar", "--si")
    assert datos_reales[0].usuario.__class__.objects.filter(email="ana.garcia@gmail.com").exists()


def test_pide_confirmacion_y_una_clave_de_verdad(datos_reales, monkeypatch):
    monkeypatch.setenv("ENTORNO", "staging")
    monkeypatch.setenv("STAGING_PASSWORD", CLAVE)
    with pytest.raises(CommandError, match="--si"):
        call_command("anonimizar")
    monkeypatch.setenv("STAGING_PASSWORD", "corta")
    with pytest.raises(CommandError, match="STAGING_PASSWORD"):
        call_command("anonimizar", "--si")
