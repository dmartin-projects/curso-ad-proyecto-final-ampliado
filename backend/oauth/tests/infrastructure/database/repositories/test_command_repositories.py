"""Contract tests del port Clientes (módulo 90): el fake y el adapter de django-oauth-toolkit, los mismos tests."""

import pytest
from oauth2_provider.models import AccessToken, Application

from conftest import UsuarioFactory
from oauth.domain.bo.cliente_nuevo import ClienteNuevo
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.domain.exceptions.cliente_ya_existe_exception import ClienteYaExisteException
from oauth.infrastructure.database.repositories.cliente_command_repository_orm import ClienteCommandRepositoryORM
from oauth.infrastructure.database.repositories.concesion_command_repository_orm import ConcesionCommandRepositoryORM
from oauth.models import ClienteOAuth
from oauth.tests.fakes.cliente_command_repository_fake import ClienteCommandRepositoryFake
from oauth.tests.fakes.concesion_command_repository_fake import ConcesionCommandRepositoryFake
from oauth.tests.infrastructure.flujo import refrescar, registrar, tokens

pytestmark = pytest.mark.django_db

NATIVA = ClienteNuevo("CLI", TipoCliente.NATIVA, frozenset({"openid"}), ("http://127.0.0.1/callback",), "gastos-cli")
SERVICIO = ClienteNuevo("Monitor", TipoCliente.SERVICIO, frozenset({"operaciones:leer"}))


@pytest.fixture(params=["fake", "dot"])
def clientes(request):
    return ClienteCommandRepositoryFake() if request.param == "fake" else ClienteCommandRepositoryORM()


def test_crear_y_existe(clientes):
    assert not clientes.existe("gastos-cli")
    credenciales = clientes.crear(NATIVA)
    assert credenciales.client_id == "gastos-cli" and credenciales.client_secret is None
    assert clientes.existe("gastos-cli")


def test_un_confidencial_recibe_secreto_y_client_id_aleatorio(clientes):
    credenciales = clientes.crear(SERVICIO)
    assert credenciales.client_secret and len(credenciales.client_id) >= 20


def test_el_client_id_repetido(clientes):
    clientes.crear(NATIVA)
    with pytest.raises(ClienteYaExisteException):
        clientes.crear(NATIVA)


def test_lo_que_guarda_django_oauth_toolkit():
    ClienteCommandRepositoryORM().crear(NATIVA)
    ClienteCommandRepositoryORM().crear(SERVICIO)
    cli = Application.objects.get(client_id="gastos-cli")
    assert (cli.client_type, cli.authorization_grant_type, cli.algorithm) == ("public", "authorization-code", "RS256")
    assert cli.redirect_uris == "http://127.0.0.1/callback" and not cli.skip_authorization
    monitor = Application.objects.exclude(client_id="gastos-cli").get()
    assert (monitor.client_type, monitor.authorization_grant_type) == ("confidential", "client-credentials")
    assert ClienteOAuth.objects.get(aplicacion=monitor).scopes == ["operaciones:leer"]


# ── Ejercicio 1: el port Concesiones ──
@pytest.fixture(params=["fake", "dot"])
def concesiones(request):
    """(adapter, dar(usuario, client_id)): en el fake se apunta; con DOT, el flujo de verdad (tokens())."""
    if request.param == "fake":
        fake = ConcesionCommandRepositoryFake()
        return fake, lambda usuario, client_id: fake.dar(usuario.pk, client_id)
    return ConcesionCommandRepositoryORM(), lambda usuario, client_id: tokens(usuario, client_id=client_id)


def test_concesiones_tiene_y_revocar(concesiones):
    adapter, dar = concesiones
    registrar()
    registrar("otra-app")
    ana, luis = UsuarioFactory(), UsuarioFactory()
    dar(ana, "gastos-cli")
    dar(ana, "gastos-cli")  # dos sesiones (dos equipos)
    dar(ana, "otra-app")
    dar(luis, "gastos-cli")
    assert adapter.tiene(ana.pk, "gastos-cli") and not adapter.tiene(ana.pk, "no-existe")
    assert adapter.revocar(ana.pk, "gastos-cli") == 2
    assert not adapter.tiene(ana.pk, "gastos-cli")
    assert adapter.tiene(ana.pk, "otra-app") and adapter.tiene(luis.pk, "gastos-cli")  # nada más


def test_revocar_con_dot_invalida_refresh_y_access():
    registrar()
    ana = UsuarioFactory()
    t = tokens(ana)
    ConcesionCommandRepositoryORM().revocar(ana.pk, "gastos-cli")
    assert refrescar(t["refresh_token"]).json()["error"] == "invalid_grant"
    assert not AccessToken.objects.exists()
