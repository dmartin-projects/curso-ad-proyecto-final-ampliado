# usuarios/tests/fakes/proveedor_identidad_fake.py — IProveedorIdentidad en memoria (módulo 91)
from usuarios.application.ports.i_proveedor_identidad import IProveedorIdentidad
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.login_social_no_valido_exception import LoginSocialNoValidoException
from usuarios.domain.vo.perfil_externo import PerfilExterno


class ProveedorIdentidadFake(IProveedorIdentidad):
    """Un proveedor que, a la vuelta, dice que la persona es `perfil` (o falla, si `fallo`). Apunta lo que le piden."""

    def __init__(self, proveedor=Proveedor.GOOGLE):
        self.proveedor = proveedor
        self.perfil = PerfilExterno(proveedor, "sub-ana", "ana@gmail.com", True, "Ana", "García")
        self.fallo: Exception | None = None
        self.transacciones, self.completadas = [], []

    def url_de_autorizacion(self, transaccion):
        self.transacciones.append(transaccion)
        return f"https://{self.proveedor}.example/authorize?state={transaccion.state}"

    def completar(self, transaccion, parametros):
        if self.fallo:
            raise self.fallo
        if not parametros.get("code"):
            raise LoginSocialNoValidoException()
        self.completadas.append((transaccion, parametros))
        return self.perfil
