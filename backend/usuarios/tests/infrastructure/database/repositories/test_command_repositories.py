"""Contract tests de las cuentas (módulos 88 y 91): Django auth y los fakes, los mismos tests."""

import pytest

from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.email_ya_registrado_exception import EmailYaRegistradoException
from usuarios.domain.exceptions.identidad_de_otra_cuenta_exception import IdentidadDeOtraCuentaException
from usuarios.domain.exceptions.proveedor_ya_vinculado_exception import ProveedorYaVinculadoException
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.domain.vo.transaccion_social import TransaccionSocial
from usuarios.infrastructure.auth.enlaces_django import EnlacesDjango
from usuarios.infrastructure.auth.politica_de_contrasenas_django import PoliticaDeContrasenasDjango
from usuarios.infrastructure.cache.transacciones_en_cache import TransaccionesEnCache
from usuarios.infrastructure.database.repositories.cuenta_command_repository_orm import CuentaCommandRepositoryORM
from usuarios.infrastructure.database.repositories.identidad_command_repository_orm import (
    IdentidadCommandRepositoryORM,
)
from usuarios.tests.fakes.cuenta_command_repository_fake import CuentaCommandRepositoryFake
from usuarios.tests.fakes.enlaces_fake import EnlacesFake
from usuarios.tests.fakes.identidad_command_repository_fake import IdentidadCommandRepositoryFake
from usuarios.tests.fakes.politica_de_contrasenas_fake import PoliticaDeContrasenasFake
from usuarios.tests.fakes.transacciones_fake import TransaccionesFake


@pytest.fixture(params=["memoria", "orm"])
def piezas(request):
    if request.param == "memoria":
        return CuentaCommandRepositoryFake(), PoliticaDeContrasenasFake(), EnlacesFake()
    request.getfixturevalue("db")
    return CuentaCommandRepositoryORM(), PoliticaDeContrasenasDjango(), EnlacesDjango()


def test_registro_pendiente_completar_y_contrasenas(piezas):
    cuentas, politica, enlaces = piezas
    pk = cuentas.crear_pendiente(email="ana@example.com", nombre="Ana", apellidos="")
    assert cuentas.por_email("ANA@example.com") == pk and cuentas.por_email("luis@example.com") is None
    assert cuentas.estado(pk) is EstadoCuenta.PENDIENTE and not cuentas.comprobar_contrasena(pk, "")
    with pytest.raises(EmailYaRegistradoException):
        cuentas.crear_pendiente(email="ana@example.com", nombre="", apellidos="")
    cuentas.completar_registro(pk, "una-clave-muy-larga")
    assert cuentas.estado(pk) is EstadoCuenta.ACTIVA
    assert cuentas.comprobar_contrasena(pk, "una-clave-muy-larga") and not cuentas.comprobar_contrasena(pk, "otra")
    assert (
        politica.incumplimientos("corta", usuario_id=pk)
        and politica.incumplimientos("w9-Gz!kq-27-Lmp", usuario_id=pk) == []
    )

    enlace = enlaces.crear(pk, "nueva-password")
    uid, token = enlace.split("uid=")[1].split("&token=")
    assert enlaces.usuario_de(uid, token) == pk and enlaces.usuario_de(uid, "inventado") is None
    cuentas.cambiar_contrasena(pk, "w9-Gz!kq-27-Lmp")
    assert cuentas.comprobar_contrasena(pk, "w9-Gz!kq-27-Lmp")


# ── Módulo 91 ──


@pytest.fixture(params=["memoria", "orm"])
def social(request):
    if request.param == "memoria":
        return CuentaCommandRepositoryFake(), IdentidadCommandRepositoryFake(), TransaccionesFake()
    request.getfixturevalue("db")
    return CuentaCommandRepositoryORM(), IdentidadCommandRepositoryORM(), TransaccionesEnCache()


def test_cuentas_verificadas_sin_contrasena(social):
    cuentas, _, _ = social
    pk = cuentas.crear_verificada(email="ana@gmail.com", nombre="Ana", apellidos="García")
    assert cuentas.activa(pk) and not cuentas.tiene_contrasena(pk) and cuentas.por_email("ana@gmail.com") == pk
    with pytest.raises(EmailYaRegistradoException):
        cuentas.crear_verificada(email="ana@gmail.com", nombre="", apellidos="")
    cuentas.bloquear(pk)
    cuentas.cambiar_contrasena(pk, "una-clave-muy-larga")
    assert cuentas.tiene_contrasena(pk)


def test_identidades(social):
    cuentas, identidades, _ = social
    ana = cuentas.crear_verificada(email="ana@gmail.com", nombre="Ana", apellidos="")
    luis = cuentas.crear_verificada(email="luis@gmail.com", nombre="Luis", apellidos="")
    google = PerfilExterno(Proveedor.GOOGLE, "1081", "ana@gmail.com", True)
    identidades.vincular(ana, google)
    identidades.vincular(ana, PerfilExterno(Proveedor.GITHUB, "583231"))
    assert identidades.dueno(Proveedor.GOOGLE, "1081") == ana and identidades.dueno(Proveedor.GOOGLE, "1") is None
    assert identidades.de_usuario(ana) == {Proveedor.GOOGLE: "1081", Proveedor.GITHUB: "583231"}
    with pytest.raises(IdentidadDeOtraCuentaException):  # la constraint (proveedor, sub), aunque dos lleguen a la vez
        identidades.vincular(luis, google)
    with pytest.raises(ProveedorYaVinculadoException):  # la constraint (usuario, proveedor)
        identidades.vincular(ana, PerfilExterno(Proveedor.GOOGLE, "otra-cuenta-de-google"))
    identidades.anotar_uso(Proveedor.GOOGLE, "1081")
    identidades.desvincular(ana, Proveedor.GOOGLE)
    assert identidades.de_usuario(ana) == {Proveedor.GITHUB: "583231"} and identidades.de_usuario(luis) == {}


def test_transacciones_de_un_solo_uso(social):
    _, _, transacciones = social
    t = TransaccionSocial(Proveedor.APPLE, "s", "n", "v" * 43, Proposito.VINCULAR, "/", usuario_id=7)
    clave = transacciones.guardar(t)
    assert transacciones.consumir("otra") is None
    assert transacciones.consumir(clave) == t
    assert transacciones.consumir(clave) is None
