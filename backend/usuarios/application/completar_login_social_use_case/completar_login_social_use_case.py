# usuarios/application/completar_login_social_use_case/completar_login_social_use_case.py — la vuelta del proveedor (módulos 91 y 92)
import hmac

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
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
from usuarios.application.ports.i_sesiones import ISesiones
from usuarios.application.ports.i_transacciones import ITransacciones
from usuarios.domain.enums.factor import Factor
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.events.proveedor_vinculado_event import ProveedorVinculadoEvent
from usuarios.domain.exceptions.acceso_cancelado_exception import AccesoCanceladoException
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.domain.exceptions.cuenta_ya_existe_exception import CuentaYaExisteException
from usuarios.domain.exceptions.email_ya_registrado_exception import EmailYaRegistradoException
from usuarios.domain.exceptions.estado_no_valido_exception import EstadoNoValidoException
from usuarios.domain.exceptions.identidad_de_otra_cuenta_exception import IdentidadDeOtraCuentaException
from usuarios.domain.exceptions.sesion_cerrada_exception import SesionCerradaException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from usuarios.domain.repositories.i_identidad_command_repository import IIdentidadCommandRepository
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository
from usuarios.domain.services.reautenticacion_con_proveedor import exigir_reautenticacion
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
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
        sesiones: ISesiones,
        segundos: ISegundoFactorCommandRepository,
        reloj: IReloj,
    ):
        self.proveedores, self.transacciones, self.identidades = proveedores, transacciones, identidades
        self.cuentas, self.eventos, self.uow = cuentas, eventos, uow
        self.sesiones, self.segundos, self.reloj = sesiones, segundos, reloj  # módulo 92, ejercicio 3

    def ejecutar(self, entrada: CompletarLoginSocialInputDTO) -> LoginSocialCompletadoOutputDTO:
        transaccion = self._transaccion(entrada)
        try:
            if "error" in entrada.parametros:  # la persona ha cancelado en el proveedor (o el proveedor no quiere)
                raise AccesoCanceladoException()
            perfil = self.proveedores.de(transaccion.proveedor).completar(transaccion, entrada.parametros)
            with self.uow:
                if transaccion.proposito is Proposito.VINCULAR:
                    return self._vincular(transaccion, perfil)
                if transaccion.proposito is Proposito.REAUTENTICAR:
                    return self._reautenticar(transaccion, perfil)
                return self._entrar(transaccion, perfil)
        except DominioException as error:
            # el adapter de entrada decide adónde volver (ejercicio 3: al login del authorization server, con su `next`)
            error.contexto |= {"proposito": transaccion.proposito, "volver": transaccion.volver}
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
                return LoginSocialCompletadoOutputDTO(
                    usuario_id, transaccion.proposito, transaccion.volver
                )  # o AUTORIZAR
            case CrearCuenta(email, nombre, apellidos):
                try:
                    usuario_id = self.cuentas.crear_verificada(email=email, nombre=nombre, apellidos=apellidos)
                except EmailYaRegistradoException:  # otra petición la ha creado a la vez (contraseña u otro proveedor)
                    raise CuentaYaExisteException(proveedor=perfil.proveedor.nombre) from None
                self.identidades.vincular(usuario_id, perfil)
                return LoginSocialCompletadoOutputDTO(
                    usuario_id, transaccion.proposito, transaccion.volver, cuenta_nueva=True
                )

    def _vincular(self, transaccion: TransaccionSocial, perfil: PerfilExterno) -> LoginSocialCompletadoOutputDTO:
        usuario_id = transaccion.usuario_id
        dueno = self.identidades.dueno(perfil.proveedor, perfil.sub)
        actual = self.identidades.de_usuario(usuario_id).get(perfil.proveedor)
        if decidir_vinculo(perfil, usuario_id=usuario_id, dueno=dueno, sub_actual=actual):
            self.identidades.vincular(usuario_id, perfil)
            # Ejercicio 2: una forma nueva de entrar en la cuenta es un cambio de seguridad: se avisa al email de
            # Gastos (no al del proveedor), por si no ha sido su dueño (un access token robado, un ordenador prestado)
            self.eventos.publicar(ProveedorVinculadoEvent(usuario_id, perfil.proveedor.nombre, perfil.email or ""))
        return LoginSocialCompletadoOutputDTO(usuario_id, Proposito.VINCULAR, transaccion.volver)

    def _reautenticar(self, transaccion: TransaccionSocial, perfil: PerfilExterno) -> LoginSocialCompletadoOutputDTO:
        """Módulo 92, ejercicio 3: el step-up de una cuenta sin contraseña. La identidad tiene que ser de ESA cuenta, el
        proveedor tiene que haber autenticado en esta ida (auth_time) y, con el MFA activo, esto no vale: un
        proveedor es un primer factor (el step-up es con el segundo)."""
        usuario_id = transaccion.usuario_id
        if self.identidades.dueno(perfil.proveedor, perfil.sub) != usuario_id:
            raise IdentidadDeOtraCuentaException(proveedor=perfil.proveedor.nombre)
        exigir_reautenticacion(perfil, transaccion)  # ReautenticacionNoRecienteException
        if self.segundos.de(usuario_id).activo:
            raise CodigoNoValidoException(
                "Con la verificación en dos pasos activa, confirma con tu app o con una passkey."
            )
        actual = self.sesiones.autenticacion(transaccion.sid)
        if actual is None:
            raise SesionCerradaException()
        self.sesiones.reautenticada(transaccion.sid, actual.con(Factor.PROVEEDOR, self.reloj.ahora()))
        return LoginSocialCompletadoOutputDTO(usuario_id, Proposito.REAUTENTICAR, transaccion.volver)
