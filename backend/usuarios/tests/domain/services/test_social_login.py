"""Las reglas del social login (módulo 91), sin base de datos ni proveedores."""

import pytest

from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.cuenta_ya_existe_exception import CuentaYaExisteException
from usuarios.domain.exceptions.email_no_verificado_exception import EmailNoVerificadoException
from usuarios.domain.exceptions.identidad_de_otra_cuenta_exception import IdentidadDeOtraCuentaException
from usuarios.domain.exceptions.identidad_no_vinculada_exception import IdentidadNoVinculadaException
from usuarios.domain.exceptions.login_social_no_valido_exception import LoginSocialNoValidoException
from usuarios.domain.exceptions.proveedor_no_disponible_exception import ProveedorNoDisponibleException
from usuarios.domain.exceptions.proveedor_ya_vinculado_exception import ProveedorYaVinculadoException
from usuarios.domain.exceptions.ultimo_metodo_de_acceso_exception import UltimoMetodoDeAccesoException
from usuarios.domain.services.destino_seguro import destino_seguro
from usuarios.domain.services.social_login import decidir_entrada, decidir_vinculo
from usuarios.domain.vo.crear_cuenta import CrearCuenta
from usuarios.domain.vo.entrar import Entrar
from usuarios.domain.vo.metodos_de_acceso import MetodosDeAcceso
from usuarios.domain.vo.perfil_externo import PerfilExterno

ANA = PerfilExterno(Proveedor.GOOGLE, "1081", " Ana@Gmail.com", True, "Ana", "García")


def test_el_perfil_normaliza_el_email_y_exige_sub():
    assert ANA.email == "ana@gmail.com"
    assert PerfilExterno(Proveedor.GITHUB, "7", "esto no es un email", True).email_verificado is False
    with pytest.raises(LoginSocialNoValidoException):
        PerfilExterno(Proveedor.APPLE, "")
    with pytest.raises(ProveedorNoDisponibleException):
        Proveedor.de("facebook")


@pytest.mark.parametrize(
    "volver, destino",
    [
        ("/hogares/3/movimientos?mes=2026-10", "/hogares/3/movimientos?mes=2026-10"),
        (None, "/"),
        ("", "/"),
        ("hogares", "/"),  # relativa sin barra: el navegador la resolvería contra la página actual
        ("//otra.example/robar", "/"),  # protocol-relative: el navegador la entiende como https://otra.example
        ("/\\otra.example", "/"),  # algunos navegadores tratan "\" como "/"
        ("https://otra.example/", "/"),
        ("javascript:alert(1)", "/"),
        ("/ruta\r\nSet-Cookie: x=1", "/"),  # caracteres de control
        ("/" + "a" * 600, "/"),
    ],
)
def test_solo_se_vuelve_a_rutas_de_gastos(volver, destino):
    assert destino_seguro(volver) == destino


def test_entrar_con_una_identidad_ya_vinculada_no_mira_el_email():
    sin_email = PerfilExterno(Proveedor.GOOGLE, "1081")
    assert decidir_entrada(sin_email, dueno=7, existe_cuenta_con_su_email=False) == Entrar(7)


def test_una_cuenta_nueva_solo_con_email_verificado():
    assert decidir_entrada(ANA, dueno=None, existe_cuenta_con_su_email=False) == CrearCuenta(
        "ana@gmail.com", "Ana", "García"
    )
    for perfil in (PerfilExterno(Proveedor.GITHUB, "9", "ana@gmail.com", False), PerfilExterno(Proveedor.APPLE, "9")):
        with pytest.raises(EmailNoVerificadoException):
            decidir_entrada(perfil, dueno=None, existe_cuenta_con_su_email=False)


def test_el_email_de_una_cuenta_que_ya_existe_no_la_vincula():
    # Aunque el proveedor lo haya verificado: el dueño de la cuenta la vincula desde dentro
    with pytest.raises(CuentaYaExisteException) as e:
        decidir_entrada(ANA, dueno=None, existe_cuenta_con_su_email=True)
    assert e.value.contexto == {"proveedor": "Google"}


def test_vincular_a_mi_cuenta():
    assert decidir_vinculo(ANA, usuario_id=7, dueno=None, sub_actual=None) is True
    assert decidir_vinculo(ANA, usuario_id=7, dueno=7, sub_actual="1081") is False  # ya estaba: nada que hacer
    with pytest.raises(IdentidadDeOtraCuentaException):
        decidir_vinculo(ANA, usuario_id=7, dueno=8, sub_actual=None)
    with pytest.raises(ProveedorYaVinculadoException):  # ya tengo OTRA cuenta de Google
        decidir_vinculo(ANA, usuario_id=7, dueno=None, sub_actual="2222")


def test_nadie_se_queda_sin_forma_de_entrar():
    solo_google = MetodosDeAcceso(contrasena=False, proveedores=frozenset({Proveedor.GOOGLE}))
    with pytest.raises(UltimoMetodoDeAccesoException):
        solo_google.sin(Proveedor.GOOGLE)
    with pytest.raises(IdentidadNoVinculadaException):
        solo_google.sin(Proveedor.APPLE)
    dos = MetodosDeAcceso(contrasena=False, proveedores=frozenset({Proveedor.GOOGLE, Proveedor.APPLE}))
    assert dos.sin(Proveedor.GOOGLE).proveedores == {Proveedor.APPLE}
    con_contrasena = MetodosDeAcceso(contrasena=True, proveedores=frozenset({Proveedor.GOOGLE}))
    assert con_contrasena.sin(Proveedor.GOOGLE) == MetodosDeAcceso(True, frozenset())
