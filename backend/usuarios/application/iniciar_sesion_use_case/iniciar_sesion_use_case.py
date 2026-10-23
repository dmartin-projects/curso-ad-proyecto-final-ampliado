# usuarios/application/iniciar_sesion_use_case/iniciar_sesion_use_case.py — abrir una sesión, o pedir antes el segundo factor (módulos 35, 91 y 92)
from core.application.ports.i_reloj import IReloj
from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.application.iniciar_sesion_use_case.i_iniciar_sesion_use_case import IIniciarSesionUseCase
from usuarios.application.ports.i_pendientes import IPendientes
from usuarios.application.shared.apertura_de_sesion import AperturaDeSesion
from usuarios.application.shared.dtos.segundo_factor_pendiente_output_dto import SegundoFactorPendienteOutputDTO
from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO
from usuarios.application.shared.factores_de_cuenta import FactoresDeCuenta
from usuarios.domain.exceptions.cuenta_desactivada_exception import CuentaDesactivadaException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository
from usuarios.domain.services.factores import exige_segundo_factor
from usuarios.domain.vo.autenticacion import Autenticacion
from usuarios.domain.vo.login_pendiente import LoginPendiente
from usuarios.domain.vo.segundo_factor_pendiente import SegundoFactorPendiente


class IniciarSesionUseCase(IIniciarSesionUseCase):
    def __init__(
        self,
        *,
        cuentas: ICuentaCommandRepository,
        segundos: ISegundoFactorCommandRepository,
        pendientes: IPendientes,
        factores: FactoresDeCuenta,
        apertura: AperturaDeSesion,
        reloj: IReloj,
    ):
        self.cuentas, self.segundos, self.pendientes = cuentas, segundos, pendientes
        self.factores, self.apertura, self.reloj = factores, apertura, reloj

    def ejecutar(self, entrada: IniciarSesionInputDTO) -> SesionAbiertaOutputDTO | SegundoFactorPendienteOutputDTO:
        if not self.cuentas.activa(entrada.usuario_id):  # desactivada por soporte: ni con la contraseña ni con Google
            raise CuentaDesactivadaException()
        if exige_segundo_factor(entrada.factor, mfa_activo=self.segundos.de(entrada.usuario_id).activo):
            pendiente = LoginPendiente(entrada.usuario_id, entrada.factor, entrada.canal, volver=entrada.volver)
            clave = self.pendientes.guardar(pendiente)
            return SegundoFactorPendienteOutputDTO.desde_vo(
                SegundoFactorPendiente(clave, self.factores.de(entrada.usuario_id).segundos())
            )
        autenticacion = Autenticacion(frozenset({entrada.factor}), self.reloj.ahora(), entrada.passkey_sincronizada)
        sesion = self.apertura.abrir(entrada.usuario_id, autenticacion, entrada.canal, entrada.contexto)
        return SesionAbiertaOutputDTO.desde_vo(sesion)
