"""Registrar un cliente (módulo 90), con fakes."""

import pytest

from oauth.application.registrar_cliente_use_case.dtos.registrar_cliente_input_dto import RegistrarClienteInputDTO
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.domain.exceptions.cliente_ya_existe_exception import ClienteYaExisteException
from oauth.domain.exceptions.scopes_no_validos_exception import ScopesNoValidosException
from oauth.tests.fakes.mundo import Mundo


def cmd(**cambios):
    datos = dict(nombre="CLI", tipo=TipoCliente.NATIVA, scopes=frozenset({"openid", "gastos:leer"}),
                 redirect_uris=("http://127.0.0.1/callback",), client_id="gastos-cli")  # fmt: skip
    return RegistrarClienteInputDTO(**(datos | cambios))


def test_un_cliente_nativo_no_tiene_secreto():
    m = Mundo()
    credenciales = m.registrar.ejecutar(cmd())
    assert credenciales.client_id == "gastos-cli" and credenciales.client_secret is None
    assert m.uow.confirmadas == 1


def test_un_cliente_confidencial_recibe_su_secreto_una_vez():
    m = Mundo()
    credenciales = m.registrar.ejecutar(
        cmd(tipo=TipoCliente.SERVICIO, scopes=frozenset({"operaciones:leer"}), redirect_uris=(), client_id=None)
    )
    assert len(credenciales.client_secret) > 40 and len(credenciales.client_id) > 20  # client_id aleatorio


def test_el_client_id_no_se_repite():
    m = Mundo()
    m.registrar.ejecutar(cmd())
    with pytest.raises(ClienteYaExisteException):
        m.registrar.ejecutar(cmd(nombre="Otra"))
    assert len(m.clientes.clientes) == 1


def test_las_reglas_antes_de_tocar_nada():
    m = Mundo()
    with pytest.raises(ScopesNoValidosException):
        m.registrar.ejecutar(cmd(scopes=frozenset({"openid", "operaciones:leer"})))
    assert m.clientes.clientes == {} and m.uow.confirmadas == 0
