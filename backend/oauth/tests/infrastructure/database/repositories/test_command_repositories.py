"""Contract tests del port Clientes (módulo 90): el fake y el adapter de django-oauth-toolkit, los mismos tests."""

import pytest
from oauth2_provider.models import Application

from oauth.domain.bo.cliente_nuevo import ClienteNuevo
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.domain.exceptions.cliente_ya_existe_exception import ClienteYaExisteException
from oauth.infrastructure.database.repositories.cliente_command_repository_orm import ClienteCommandRepositoryORM
from oauth.models import ClienteOAuth
from oauth.tests.fakes.cliente_command_repository_fake import ClienteCommandRepositoryFake

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
