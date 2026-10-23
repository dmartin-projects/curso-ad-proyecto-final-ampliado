# usuarios/application/completar_segundo_factor_use_case/completar_segundo_factor_use_case.py — el segundo paso del login (módulo 92)
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.completar_segundo_factor_use_case.dtos.completar_segundo_factor_input_dto import (
    CompletarSegundoFactorInputDTO,
)
from usuarios.application.completar_segundo_factor_use_case.i_completar_segundo_factor_use_case import (
    ICompletarSegundoFactorUseCase,
)
from usuarios.application.ports.i_pendientes import IPendientes
from usuarios.application.shared.apertura_de_sesion import AperturaDeSesion
from usuarios.application.shared.comprobar_factor import ComprobarFactor
from usuarios.application.shared.dtos.login_pendiente_output_dto import LoginPendienteOutputDTO
from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO
from usuarios.application.shared.fallo_cerrado import fallo_cerrado
from usuarios.application.shared.login_pendiente import leer_pendiente
from usuarios.domain.enums.factor import Factor
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.domain.exceptions.login_pendiente_no_valido_exception import LoginPendienteNoValidoException
from usuarios.domain.vo.autenticacion import Autenticacion


class CompletarSegundoFactorUseCase(ICompletarSegundoFactorUseCase):
    def __init__(
        self,
        *,
        apertura: AperturaDeSesion,
        comprobar: ComprobarFactor,
        pendientes: IPendientes,
        uow: IUnidadDeTrabajo,
        reloj: IReloj,
    ):
        self.apertura, self.comprobar, self.pendientes, self.uow, self.reloj = (
            apertura,
            comprobar,
            pendientes,
            uow,
            reloj,
        )

    def ejecutar(
        self, entrada: CompletarSegundoFactorInputDTO
    ) -> tuple[SesionAbiertaOutputDTO, LoginPendienteOutputDTO]:
        pendiente = leer_pendiente(self.pendientes, entrada.clave, entrada.canal)
        if entrada.factor not in (Factor.TOTP, Factor.RECUPERACION, Factor.PASSKEY):
            raise CodigoNoValidoException()
        # El intento se cuenta ANTES de mirar el código: si algo falla a medias, ya está gastado (fail closed).
        # 5 y se acabó: vuelta a la contraseña
        if not self.pendientes.intento(entrada.clave):
            raise LoginPendienteNoValidoException()
        with fallo_cerrado(), self.uow:
            hecho = self.comprobar.comprobar(
                pendiente.usuario_id, entrada.factor, codigo=entrada.codigo, respuesta=entrada.respuesta,
                ambito=f"segundo:{entrada.clave}",
            )  # fmt: skip
        if hecho.error:
            raise hecho.error
        if self.pendientes.consumir(entrada.clave) is None:  # otra petición lo ha completado a la vez
            raise LoginPendienteNoValidoException()
        primero = Autenticacion(frozenset({pendiente.primero}), self.reloj.ahora())
        autenticacion = primero.con(entrada.factor, self.reloj.ahora(), sincronizada=hecho.sincronizada)
        sesion = self.apertura.abrir(pendiente.usuario_id, autenticacion, entrada.canal, entrada.contexto)
        return SesionAbiertaOutputDTO.desde_vo(sesion), LoginPendienteOutputDTO.desde_vo(pendiente)
