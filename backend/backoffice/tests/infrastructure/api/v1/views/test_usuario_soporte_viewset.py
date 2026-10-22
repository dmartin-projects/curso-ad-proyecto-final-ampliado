"""Los usuarios: verlos y desactivarlos (módulos 79 y 88)."""

import pytest
from rest_framework_simplejwt.tokens import AccessToken

from backoffice.tests.infrastructure.api.v1.conftest import URL
from conftest import UsuarioFactory
from core.models import RegistroAuditoria

pytestmark = pytest.mark.django_db


def test_soporte_ve_usuarios_pero_solo_un_superusuario_los_desactiva(soporte, superusuario, api):
    usuario = UsuarioFactory()
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(usuario)}")  # un JWT de verdad
    assert api.get("/api/v1/auth/me/").status_code == 200
    assert soporte.get(URL + "usuarios/", {"search": usuario.email}).data["count"] == 1
    assert soporte.patch(URL + f"usuarios/{usuario.pk}/", {"is_active": False}).status_code == 403

    assert superusuario.patch(URL + f"usuarios/{usuario.pk}/", {"is_active": False}).data["is_active"] is False
    assert api.get("/api/v1/auth/me/").status_code == 401  # su access token deja de valer al instante
    registro = RegistroAuditoria.objects.get(object_id=str(usuario.pk))
    assert registro.cambios == {"is_active": ["True", "False"]}  # solo lo que cambió: nunca el hash de la contraseña


def test_me_dice_si_es_personal(soporte, cliente):
    assert soporte.get("/api/v1/auth/me/").data["es_personal"] is True
    assert cliente(UsuarioFactory()).get("/api/v1/auth/me/").data["es_personal"] is False
