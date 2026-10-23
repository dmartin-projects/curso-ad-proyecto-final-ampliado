"""Contract tests de las cuentas (módulos 88, 91 y 92): Django auth y los fakes, los mismos tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from usuarios.domain.bo.passkey import Passkey
from usuarios.domain.bo.segundo_factor import SegundoFactor
from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.enums.estado_renovacion import EstadoRenovacion
from usuarios.domain.enums.factor import Factor
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.email_ya_registrado_exception import EmailYaRegistradoException
from usuarios.domain.exceptions.identidad_de_otra_cuenta_exception import IdentidadDeOtraCuentaException
from usuarios.domain.exceptions.passkey_no_encontrada_exception import PasskeyNoEncontradaException
from usuarios.domain.exceptions.proveedor_ya_vinculado_exception import ProveedorYaVinculadoException
from usuarios.domain.exceptions.sesion_no_encontrada_exception import SesionNoEncontradaException
from usuarios.domain.vo.autenticacion import Autenticacion
from usuarios.domain.vo.contexto import Contexto
from usuarios.domain.vo.login_pendiente import LoginPendiente
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.domain.vo.transaccion_social import TransaccionSocial
from usuarios.infrastructure.auth.enlaces_django import EnlacesDjango
from usuarios.infrastructure.auth.politica_de_contrasenas_django import PoliticaDeContrasenasDjango
from usuarios.infrastructure.cache.transacciones_en_cache import TransaccionesEnCache
from usuarios.infrastructure.database.repositories.cuenta_command_repository_orm import CuentaCommandRepositoryORM
from usuarios.infrastructure.database.repositories.identidad_command_repository_orm import IdentidadCommandRepositoryORM
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


# ── Módulo 92 ──


@pytest.fixture(params=["memoria", "orm"])
def mfa(request):
    if request.param == "memoria":
        from usuarios.tests.fakes.codigos_de_recuperacion_fake import CodigosDeRecuperacionFake
        from usuarios.tests.fakes.passkey_command_repository_fake import PasskeyCommandRepositoryFake
        from usuarios.tests.fakes.pendientes_fake import PendientesFake
        from usuarios.tests.fakes.retos_fake import RetosFake
        from usuarios.tests.fakes.segundo_factor_command_repository_fake import SegundoFactorCommandRepositoryFake
        from usuarios.tests.fakes.sesiones_fake import SesionesFake

        return SimpleNamespace(
            cuentas=CuentaCommandRepositoryFake(), segundos=SegundoFactorCommandRepositoryFake(), codigos=CodigosDeRecuperacionFake(),
            passkeys=PasskeyCommandRepositoryFake(), sesiones=SesionesFake(), pendientes=PendientesFake(), retos=RetosFake(),
        )  # fmt: skip
    request.getfixturevalue("db")
    from usuarios.infrastructure.cache.pendientes_en_cache import PendientesEnCache
    from usuarios.infrastructure.cache.retos_en_cache import RetosEnCache
    from usuarios.infrastructure.database.repositories.passkey_command_repository_orm import PasskeyCommandRepositoryORM
    from usuarios.infrastructure.database.repositories.segundo_factor_command_repository_orm import (
        SegundoFactorCommandRepositoryORM,
    )
    from usuarios.infrastructure.database.services.codigos_de_recuperacion_orm import CodigosDeRecuperacionORM
    from usuarios.infrastructure.database.services.sesiones_orm import SesionesORM

    return SimpleNamespace(
        cuentas=CuentaCommandRepositoryORM(), segundos=SegundoFactorCommandRepositoryORM(), codigos=CodigosDeRecuperacionORM(), passkeys=PasskeyCommandRepositoryORM(),
        sesiones=SesionesORM(), pendientes=PendientesEnCache(), retos=RetosEnCache(),
    )  # fmt: skip


def test_segundos_factores(mfa):
    ana = mfa.cuentas.crear_verificada(email="ana@gmail.com", nombre="Ana", apellidos="")
    vacio = mfa.segundos.de(ana)
    assert (vacio.usuario_id, vacio.secreto, vacio.activo, vacio.fallos) == (ana, None, False, 0)
    momento = datetime(2026, 10, 23, 10, 0, tzinfo=UTC)
    mfa.segundos.guardar(SegundoFactor(ana, "JBSWY3DPEHPK3PXP", True, 7, 5, momento))
    leido = mfa.segundos.de(ana, bloquear=True)
    assert (leido.secreto, leido.activo, leido.ultimo_paso, leido.fallos, leido.bloqueado_hasta) == (
        "JBSWY3DPEHPK3PXP", True, 7, 5, momento
    )  # fmt: skip
    leido.secreto = "OTRO"  # una copia: cambiarla no cambia lo guardado
    assert mfa.segundos.de(ana).secreto == "JBSWY3DPEHPK3PXP"


def test_codigos_de_recuperacion(mfa):
    ana = mfa.cuentas.crear_verificada(email="ana@gmail.com", nombre="Ana", apellidos="")
    codigos = mfa.codigos.generar(ana)
    assert len(set(codigos)) == 10 and mfa.codigos.quedan(ana) == 10
    assert mfa.codigos.usar(ana, codigos[3]) and not mfa.codigos.usar(ana, codigos[3])
    assert not mfa.codigos.usar(ana, "inventado") and mfa.codigos.quedan(ana) == 9
    mfa.codigos.borrar(ana)
    assert mfa.codigos.quedan(ana) == 0


def test_passkeys(mfa):
    ana = mfa.cuentas.crear_verificada(email="ana@gmail.com", nombre="Ana", apellidos="")
    luis = mfa.cuentas.crear_verificada(email="luis@gmail.com", nombre="Luis", apellidos="")
    passkey = Passkey(ana, b"cred-1", b"clave", 0, "Portátil", transportes=("internal",))
    mfa.passkeys.guardar(passkey)
    assert passkey.id is not None
    assert mfa.passkeys.por_credencial(b"cred-1").nombre == "Portátil" and mfa.passkeys.por_credencial(b"x") is None
    passkey.contador, passkey.sincronizada = 4, True
    mfa.passkeys.guardar(passkey)
    (guardada,) = mfa.passkeys.de_usuario(ana)
    assert (guardada.contador, guardada.sincronizada, guardada.transportes) == (4, True, ("internal",))
    assert mfa.passkeys.manija(ana) == mfa.passkeys.manija(ana) != mfa.passkeys.manija(luis)  # fija por cuenta
    assert mfa.passkeys.usuario_de_manija(mfa.passkeys.manija(ana)) == ana
    with pytest.raises(PasskeyNoEncontradaException):
        mfa.passkeys.borrar(luis, passkey.id)  # no es suya
    assert mfa.passkeys.borrar(ana, passkey.id) == "Portátil" and mfa.passkeys.de_usuario(ana) == []


def test_sesiones(mfa):
    ana = mfa.cuentas.crear_verificada(email="ana@gmail.com", nombre="Ana", apellidos="")
    luis = mfa.cuentas.crear_verificada(email="luis@gmail.com", nombre="Luis", apellidos="")
    momento = datetime(2026, 10, 23, 10, 0, tzinfo=UTC)
    autenticacion = Autenticacion(frozenset({Factor.CONTRASENA}), momento)
    portatil = mfa.sesiones.abrir(usuario_id=ana, canal=Canal.SPA, autenticacion=autenticacion,
                                  contexto=Contexto("Chrome", "83.45.120.17", "cookie-portatil"))  # fmt: skip
    movil = mfa.sesiones.abrir(usuario_id=ana, canal=Canal.AUTORIZACION, autenticacion=autenticacion,
                               contexto=Contexto("Safari", "91.2.3.4", "cookie-movil"))  # fmt: skip
    assert mfa.sesiones.autenticacion(portatil) == autenticacion and mfa.sesiones.autenticacion("no-existe") is None
    assert mfa.sesiones.dispositivo_conocido(ana, "cookie-movil") and not mfa.sesiones.dispositivo_conocido(
        luis, "cookie-movil"
    )
    assert mfa.sesiones.cuantas(ana) == 2 and mfa.sesiones.cuantas(luis) == 0
    nueva = autenticacion.con(Factor.TOTP, momento)
    mfa.sesiones.reautenticada(portatil, nueva)
    assert mfa.sesiones.autenticacion(portatil) == nueva
    mfa.sesiones.refresh_emitido(portatil, "jti-1")
    rotar = mfa.sesiones.rotar
    assert rotar(portatil, presentado="jti-1", nuevo="jti-2", contexto=Contexto()).estado is EstadoRenovacion.ROTADA
    # el mismo, un instante después (otra pestaña): no rota; uno que nunca fue el vigente, reutilizado
    assert rotar(portatil, presentado="jti-1", nuevo="x", contexto=Contexto()).estado is EstadoRenovacion.CONCURRENTE
    robado = rotar(portatil, presentado="jti-0", nuevo="y", contexto=Contexto())
    assert (robado.estado, robado.usuario_id, robado.descripcion) == (EstadoRenovacion.REUTILIZADA, ana, "Navegador")
    assert rotar(portatil, presentado="jti-2", nuevo="jti-3", contexto=Contexto()).estado is EstadoRenovacion.ROTADA
    with pytest.raises(SesionNoEncontradaException):
        mfa.sesiones.cerrar(luis, portatil)  # no es suya
    assert mfa.sesiones.cerrar_las_demas(ana, portatil) == 1
    assert mfa.sesiones.autenticacion(movil) is None
    assert rotar(movil, presentado="", nuevo="j", contexto=Contexto()).estado is EstadoRenovacion.CERRADA
    mfa.sesiones.cerrar(ana, portatil)
    with pytest.raises(SesionNoEncontradaException):
        mfa.sesiones.cerrar(ana, portatil)  # ya cerrada
    assert mfa.sesiones.cuantas(ana) == 2  # cerradas, pero existieron: el dispositivo sigue siendo conocido


def test_logins_pendientes_y_retos(mfa):
    clave = mfa.pendientes.guardar(LoginPendiente(7, Factor.CONTRASENA, Canal.SPA, volver="/hogares"))
    assert mfa.pendientes.leer(clave) == LoginPendiente(7, Factor.CONTRASENA, Canal.SPA, volver="/hogares")
    for _ in range(5):
        assert mfa.pendientes.intento(clave)
    assert mfa.pendientes.leer(clave).intentos == 5
    assert not mfa.pendientes.intento(clave)  # el sexto: ya no quedan, y se acabó
    assert mfa.pendientes.leer(clave) is None and mfa.pendientes.consumir(clave) is None
    otra = mfa.pendientes.guardar(LoginPendiente(7, Factor.PROVEEDOR, Canal.AUTORIZACION))
    assert mfa.pendientes.consumir(otra).primero == Factor.PROVEEDOR and mfa.pendientes.consumir(otra) is None

    mfa.retos.guardar("entrar:abc", b"reto")
    assert mfa.retos.consumir("entrar:otro") is None
    assert mfa.retos.consumir("entrar:abc") == b"reto" and mfa.retos.consumir("entrar:abc") is None
