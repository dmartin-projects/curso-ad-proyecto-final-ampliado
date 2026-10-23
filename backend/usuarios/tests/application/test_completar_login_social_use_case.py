"""Los use cases del social login y de la sesión (módulo 91), con fakes: sin proveedores, HTTP ni base de datos."""

import pytest

from usuarios.application.completar_login_social_use_case.dtos.completar_login_social_input_dto import (
    CompletarLoginSocialInputDTO,
)
from usuarios.application.completar_login_social_use_case.dtos.login_social_completado_output_dto import (
    LoginSocialCompletadoOutputDTO,
)
from usuarios.application.desvincular_use_case.dtos.desvincular_input_dto import DesvincularInputDTO
from usuarios.application.empezar_login_social_use_case.dtos.empezar_login_social_input_dto import (
    EmpezarLoginSocialInputDTO,
)
from usuarios.application.establecer_contrasena_use_case.dtos.establecer_contrasena_input_dto import (
    EstablecerContrasenaInputDTO,
)
from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.acceso_cancelado_exception import AccesoCanceladoException
from usuarios.domain.exceptions.contrasena_no_valida_exception import ContrasenaNoValidaException
from usuarios.domain.exceptions.cuenta_desactivada_exception import CuentaDesactivadaException
from usuarios.domain.exceptions.cuenta_ya_existe_exception import CuentaYaExisteException
from usuarios.domain.exceptions.estado_no_valido_exception import EstadoNoValidoException
from usuarios.domain.exceptions.identidad_de_otra_cuenta_exception import IdentidadDeOtraCuentaException
from usuarios.domain.exceptions.login_social_no_valido_exception import LoginSocialNoValidoException
from usuarios.domain.exceptions.proveedor_no_disponible_exception import ProveedorNoDisponibleException
from usuarios.domain.exceptions.ultimo_metodo_de_acceso_exception import UltimoMetodoDeAccesoException
from usuarios.domain.exceptions.ya_tiene_contrasena_exception import YaTieneContrasenaException
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.tests.fakes.mundo import Mundo

G = Proveedor.GOOGLE


def ida(mundo, proveedor=G, **kwargs):
    """Empezar: lo que el navegador se lleva (la URL del proveedor) y lo que guarda (la clave, en su cookie)."""
    return mundo.empezar.ejecutar(EmpezarLoginSocialInputDTO(proveedor, **kwargs))


def vuelta(mundo, ida_, proveedor=G, **parametros):
    """Volver del proveedor con el state de la ida (o el que se diga) y un code."""
    state = mundo.proveedores.de(proveedor).transacciones[-1].state
    datos = {"state": state, "code": "code-1"} | parametros
    return mundo.completar.ejecutar(CompletarLoginSocialInputDTO(proveedor, ida_.clave, datos))


def test_la_ida_genera_valores_aleatorios_y_guarda_la_transaccion():
    mundo = Mundo()
    a, b = ida(mundo, volver="/hogares/3"), ida(mundo, volver="//otra.example")
    t1, t2 = mundo.google.transacciones
    assert len({t1.state, t2.state, t1.nonce, t2.nonce}) == 4 and len(t1.code_verifier) >= 43
    assert (t1.volver, t2.volver) == ("/hogares/3", "/")  # el open redirect se corta al empezar
    assert mundo.transacciones.guardadas == {a.clave: t1, b.clave: t2}
    with pytest.raises(ProveedorNoDisponibleException):
        ida(mundo, Proveedor.APPLE)


def test_entrar_por_primera_vez_crea_una_cuenta_activa_sin_contrasena():
    mundo = Mundo()
    hecho = vuelta(mundo, ida(mundo, volver="/hogares"))
    assert hecho == LoginSocialCompletadoOutputDTO(1, Proposito.ENTRAR, "/hogares", cuenta_nueva=True)
    assert (
        mundo.cuentas.usuarios[1] | {"email": "ana@gmail.com", "activo": True, "password": None}
        == (mundo.cuentas.usuarios[1])
    )
    assert mundo.identidades.filas == {(G, "sub-ana"): 1}
    # La segunda vez, a la misma cuenta (y se anota el uso)
    assert vuelta(mundo, ida(mundo)) == LoginSocialCompletadoOutputDTO(1, Proposito.ENTRAR, "/")
    assert mundo.identidades.usos == [(G, "sub-ana")]


def test_sin_cookie_con_otro_state_o_dos_veces_no_se_canjea_nada():
    mundo = Mundo()
    a = ida(mundo)
    state = mundo.google.transacciones[-1].state
    for clave, parametros in [
        (None, {"state": state, "code": "c"}),  # sin la cookie (la vuelta no viene del navegador que empezó)
        ("inventada", {"state": state, "code": "c"}),
    ]:
        with pytest.raises(EstadoNoValidoException):
            mundo.completar.ejecutar(CompletarLoginSocialInputDTO(G, clave, parametros))
    with pytest.raises(EstadoNoValidoException):  # otro state: y la transacción ya se ha gastado
        mundo.completar.ejecutar(CompletarLoginSocialInputDTO(G, a.clave, {"state": "otro", "code": "c"}))
    with pytest.raises(EstadoNoValidoException):
        mundo.completar.ejecutar(CompletarLoginSocialInputDTO(G, a.clave, {"state": state, "code": "c"}))
    b = ida(mundo)
    vuelta(mundo, b)
    with pytest.raises(EstadoNoValidoException):  # la misma vuelta otra vez (reutilizar el callback)
        vuelta(mundo, b)
    assert len(mundo.google.completadas) == 1  # el proveedor solo vio un canje


def test_la_vuelta_de_un_proveedor_no_vale_para_otro():
    mundo = Mundo()
    a = ida(mundo, G)
    state = mundo.google.transacciones[-1].state
    with pytest.raises(EstadoNoValidoException):  # (mix-up: la respuesta de Google llega a la vuelta de GitHub)
        mundo.completar.ejecutar(CompletarLoginSocialInputDTO(Proveedor.GITHUB, a.clave, {"state": state, "code": "c"}))


def test_si_cancela_o_el_proveedor_falla_no_hay_cuenta_y_se_sabe_para_que_era():
    mundo = Mundo()
    with pytest.raises(AccesoCanceladoException) as e:
        vuelta(mundo, ida(mundo), error="access_denied", code=None)
    assert e.value.contexto == {"proposito": Proposito.ENTRAR}
    mundo.google.fallo = LoginSocialNoValidoException()
    with pytest.raises(LoginSocialNoValidoException):
        vuelta(mundo, ida(mundo))
    assert mundo.cuentas.usuarios == {} and mundo.identidades.filas == {}


def con_contrasena(mundo: Mundo, email: str) -> int:
    """Una cuenta con contraseña: registrada y completada."""
    pk = mundo.cuentas.crear_pendiente(email=email, nombre="", apellidos="")
    mundo.cuentas.completar_registro(pk, "una-clave-muy-larga")
    return pk


def test_no_se_vincula_sola_una_cuenta_que_ya_existe():
    mundo = Mundo()
    con_contrasena(mundo, "ana@gmail.com")
    with pytest.raises(CuentaYaExisteException):
        vuelta(mundo, ida(mundo))
    assert mundo.identidades.filas == {}  # ni identidad nueva ni sesión
    assert mundo.uow_social.deshechas == 1


def test_vincular_desde_dentro_aunque_el_email_sea_otro():
    mundo = Mundo()
    pk = con_contrasena(mundo, "ana@trabajo.example")
    hecho = vuelta(mundo, ida(mundo, proposito=Proposito.VINCULAR, usuario_id=pk))
    assert (hecho.usuario_id, hecho.proposito) == (pk, Proposito.VINCULAR)
    assert mundo.identidades.filas == {(G, "sub-ana"): pk}
    # Y desde ahora entra con Google
    assert vuelta(mundo, ida(mundo)).usuario_id == pk


def test_no_se_puede_vincular_la_identidad_de_otro():
    mundo = Mundo()
    vuelta(mundo, ida(mundo))  # la cuenta 1 entra con Google (sub-ana)
    otro = con_contrasena(mundo, "luis@example.com")
    with pytest.raises(IdentidadDeOtraCuentaException) as e:
        vuelta(mundo, ida(mundo, proposito=Proposito.VINCULAR, usuario_id=otro))
    assert e.value.contexto["proposito"] is Proposito.VINCULAR  # → la SPA vuelve a «Métodos de acceso»
    with pytest.raises(ValueError):
        ida(mundo, proposito=Proposito.VINCULAR)  # vincular sin saber para quién: un fallo de programación


def test_quitar_un_proveedor_solo_si_queda_otra_forma_de_entrar():
    mundo = Mundo()
    vuelta(mundo, ida(mundo))  # cuenta 1: solo Google
    with pytest.raises(UltimoMetodoDeAccesoException):
        mundo.desvincular.ejecutar(DesvincularInputDTO(1, G))
    mundo.github.perfil = PerfilExterno(Proveedor.GITHUB, "583231", "ana@gmail.com", True)
    vuelta(mundo, ida(mundo, Proveedor.GITHUB, proposito=Proposito.VINCULAR, usuario_id=1), Proveedor.GITHUB)
    mundo.desvincular.ejecutar(DesvincularInputDTO(1, G))
    assert mundo.identidades.de_usuario(1) == {Proveedor.GITHUB: "583231"}
    assert mundo.cuentas.bloqueadas == [1]  # con la cuenta bloqueada mientras se decide


def test_establecer_una_contrasena_a_una_cuenta_sin_ella():
    mundo = Mundo()
    vuelta(mundo, ida(mundo))
    with pytest.raises(ContrasenaNoValidaException) as e:
        mundo.establecer.ejecutar(EstablecerContrasenaInputDTO(1, "corta"))
    assert e.value.campo == "nueva"
    mundo.establecer.ejecutar(EstablecerContrasenaInputDTO(1, "una-clave-muy-larga"))
    assert mundo.cuentas.comprobar_contrasena(1, "una-clave-muy-larga")
    with pytest.raises(YaTieneContrasenaException):  # cambiarla pide la actual: CambiarContrasena
        mundo.establecer.ejecutar(EstablecerContrasenaInputDTO(1, "otra-clave-muy-larga"))
    mundo.desvincular.ejecutar(DesvincularInputDTO(1, G))  # ahora sí: le queda la contraseña


def test_iniciar_sesion_es_el_mismo_para_todos_y_no_abre_cuentas_desactivadas():
    mundo = Mundo()
    vuelta(mundo, ida(mundo))
    assert mundo.iniciar_sesion.ejecutar(IniciarSesionInputDTO(1)).refresh == "refresh-1"
    mundo.cuentas.usuarios[1]["activo"] = False  # desactivada por soporte
    with pytest.raises(CuentaDesactivadaException):
        mundo.iniciar_sesion.ejecutar(IniciarSesionInputDTO(1))
