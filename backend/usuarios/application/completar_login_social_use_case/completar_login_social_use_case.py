# usuarios/application/completar_login_social_use_case/completar_login_social_use_case.py — la vuelta del proveedor (módulo 91)
import hmac

from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.exceptions.dominio_exception import DominioException
from usuarios.application.completar_login_social_use_case.dtos.completar_login_social_input_dto import (
    CompletarLoginSocialInputDTO,
)
from usuarios.application.completar_login_social_use_case.dtos.login_social_completado_output_dto import (
    LoginSocialCompletadoOutputDTO,
)
from usuarios.application.completar_login_social_use_case.i_completar_login_social_use_case import (
    ICompletarLoginSocialUseCase,
)
from usuarios.application.ports.i_proveedores import IProveedores
from usuarios.application.ports.i_transacciones import ITransacciones
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.exceptions.acceso_cancelado_exception import AccesoCanceladoException
from usuarios.domain.exceptions.cuenta_ya_existe_exception import CuentaYaExisteException
from usuarios.domain.exceptions.email_ya_registrado_exception import EmailYaRegistradoException
from usuarios.domain.exceptions.estado_no_valido_exception import EstadoNoValidoException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from usuarios.domain.repositories.i_identidad_command_repository import IIdentidadCommandRepository
from usuarios.domain.services.social_login import decidir_entrada, decidir_vinculo
from usuarios.domain.vo.crear_cuenta import CrearCuenta
from usuarios.domain.vo.entrar import Entrar
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.domain.vo.transaccion_social import TransaccionSocial


class CompletarLoginSocialUseCase(ICompletarLoginSocialUseCase):
    def __init__(
        self,
        *,
        proveedores: IProveedores,
        transacciones: ITransacciones,
        identidades: IIdentidadCommandRepository,
        cuentas: ICuentaCommandRepository,
        uow: IUnidadDeTrabajo,
    ):
        self.proveedores, self.transacciones, self.identidades = proveedores, transacciones, identidades
        self.cuentas, self.uow = cuentas, uow

    def ejecutar(self, entrada: CompletarLoginSocialInputDTO) -> LoginSocialCompletadoOutputDTO:
        transaccion = self._transaccion(entrada)
        try:
            if "error" in entrada.parametros:  # la persona ha cancelado en el proveedor (o el proveedor no quiere)
                raise AccesoCanceladoException()
            perfil = self.proveedores.de(transaccion.proveedor).completar(transaccion, entrada.parametros)
            with self.uow:
                if transaccion.proposito is Proposito.VINCULAR:
                    return self._vincular(transaccion, perfil)
                return self._entrar(transaccion, perfil)
        except DominioException as error:
            error.contexto["proposito"] = transaccion.proposito  # el adapter de entrada decide adónde volver
            raise

    def _transaccion(self, entrada: CompletarLoginSocialInputDTO) -> TransaccionSocial:
        # Se consume ANTES de comprobar nada: una transacción, un intento (también si esta vuelta es falsa)
        transaccion = self.transacciones.consumir(entrada.clave) if entrada.clave else None
        state = entrada.parametros.get("state", "")
        if (
            transaccion is None
            or transaccion.proveedor is not entrada.proveedor
            or not hmac.compare_digest(transaccion.state.encode(), state.encode())  # en tiempo constante
        ):
            raise EstadoNoValidoException()
        return transaccion

    def _entrar(self, transaccion: TransaccionSocial, perfil: PerfilExterno) -> LoginSocialCompletadoOutputDTO:
        dueno = self.identidades.dueno(perfil.proveedor, perfil.sub)
        existe = dueno is None and perfil.email is not None and self.cuentas.por_email(perfil.email) is not None
        match decidir_entrada(perfil, dueno=dueno, existe_cuenta_con_su_email=existe):
            case Entrar(usuario_id):
                self.identidades.anotar_uso(perfil.proveedor, perfil.sub)
                return LoginSocialCompletadoOutputDTO(usuario_id, Proposito.ENTRAR, transaccion.volver)
            case CrearCuenta(email, nombre, apellidos):
                try:
                    usuario_id = self.cuentas.crear_verificada(email=email, nombre=nombre, apellidos=apellidos)
                except EmailYaRegistradoException:  # otra petición la ha creado a la vez (contraseña u otro proveedor)
                    raise CuentaYaExisteException(proveedor=perfil.proveedor.nombre) from None
                self.identidades.vincular(usuario_id, perfil)
                return LoginSocialCompletadoOutputDTO(
                    usuario_id, Proposito.ENTRAR, transaccion.volver, cuenta_nueva=True
                )

    def _vincular(self, transaccion: TransaccionSocial, perfil: PerfilExterno) -> LoginSocialCompletadoOutputDTO:
        usuario_id = transaccion.usuario_id
        dueno = self.identidades.dueno(perfil.proveedor, perfil.sub)
        actual = self.identidades.de_usuario(usuario_id).get(perfil.proveedor)
        if decidir_vinculo(perfil, usuario_id=usuario_id, dueno=dueno, sub_actual=actual):
            self.identidades.vincular(usuario_id, perfil)
        return LoginSocialCompletadoOutputDTO(usuario_id, Proposito.VINCULAR, transaccion.volver)
