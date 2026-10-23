# usuarios/domain/services/social_login.py — qué pasa a la vuelta del proveedor (módulo 91)
from usuarios.domain.exceptions.cuenta_ya_existe_exception import CuentaYaExisteException
from usuarios.domain.exceptions.email_no_verificado_exception import EmailNoVerificadoException
from usuarios.domain.exceptions.identidad_de_otra_cuenta_exception import IdentidadDeOtraCuentaException
from usuarios.domain.exceptions.proveedor_ya_vinculado_exception import ProveedorYaVinculadoException
from usuarios.domain.vo.crear_cuenta import CrearCuenta
from usuarios.domain.vo.entrar import Entrar
from usuarios.domain.vo.perfil_externo import PerfilExterno


def decidir_entrada(
    perfil: PerfilExterno, *, dueno: int | None, existe_cuenta_con_su_email: bool
) -> Entrar | CrearCuenta:
    """Entrar con un proveedor desde la pantalla de login.

    1. La identidad ya es de una cuenta → esa cuenta (sin mirar el email: puede haber cambiado en el proveedor).
    2. Si no, hace falta un email VERIFICADO por el proveedor: sin él, cualquiera podría crear una cuenta de GitHub con
       tu email (sin verificarlo) y que Gastos le diera algo tuyo.
    3. Ya hay una cuenta de Gastos con ese email → NO se vincula sola (CuentaYaExisteException): que lo haga su dueño,
       desde dentro (entrando como siempre), en «Métodos de acceso». Vincular por email confía la cuenta entera a la
       verificación de email del proveedor (y a un dominio caducado que alguien vuelve a registrar).
    4. Si no hay ninguna → una cuenta nueva, ya activa (el proveedor ha verificado el email) y sin contraseña.
    """
    if dueno is not None:
        return Entrar(dueno)
    if not perfil.email or not perfil.email_verificado:
        raise EmailNoVerificadoException(proveedor=perfil.proveedor.nombre)
    if existe_cuenta_con_su_email:
        raise CuentaYaExisteException(proveedor=perfil.proveedor.nombre)
    return CrearCuenta(perfil.email, perfil.nombre, perfil.apellidos)


def decidir_vinculo(perfil: PerfilExterno, *, usuario_id: int, dueno: int | None, sub_actual: str | None) -> bool:
    """Vincular un proveedor a MI cuenta (ya he entrado). El email da igual: lo que prueba que la cuenta del proveedor
    es mía es que acabo de entrar en ella. Devuelve si hay que guardar algo (False: ya estaba vinculada)."""
    if dueno is not None and dueno != usuario_id:
        raise IdentidadDeOtraCuentaException(proveedor=perfil.proveedor.nombre)
    if dueno == usuario_id:
        return False
    if sub_actual is not None:  # ya tengo OTRA cuenta de este proveedor
        raise ProveedorYaVinculadoException(proveedor=perfil.proveedor.nombre)
    return True
