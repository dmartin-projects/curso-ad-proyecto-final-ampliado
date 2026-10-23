# usuarios/application/reautenticar_use_case/reautenticar_use_case.py — el step-up: volver a demostrar quién eres (módulo 92)
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.ports.i_sesiones import ISesiones
from usuarios.application.reautenticar_use_case.dtos.reautenticar_input_dto import ReautenticarInputDTO
from usuarios.application.reautenticar_use_case.i_reautenticar_use_case import IReautenticarUseCase
from usuarios.application.shared.comprobar_factor import ComprobarFactor
from usuarios.application.shared.dtos.autenticacion_output_dto import AutenticacionOutputDTO
from usuarios.application.shared.factores_de_cuenta import FactoresDeCuenta
from usuarios.application.shared.fallo_cerrado import fallo_cerrado
from usuarios.domain.enums.factor import Factor
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.domain.exceptions.sesion_cerrada_exception import SesionCerradaException


class ReautenticarUseCase(IReautenticarUseCase):
    """Step-up: la sesión vuelve a demostrar quién es antes de una acción sensible. Con MFA, un segundo factor (la
    contraseña sola no sube el nivel de una sesión que entró con dos); sin MFA, la contraseña o una passkey."""

    def __init__(
        self,
        *,
        factores: FactoresDeCuenta,
        comprobar: ComprobarFactor,
        sesiones: ISesiones,
        uow: IUnidadDeTrabajo,
        reloj: IReloj,
    ):
        self.factores, self.comprobar, self.sesiones, self.uow, self.reloj = factores, comprobar, sesiones, uow, reloj

    def ejecutar(self, entrada: ReautenticarInputDTO) -> AutenticacionOutputDTO:
        autenticacion = self.sesiones.autenticacion(entrada.sid)
        if autenticacion is None:
            raise SesionCerradaException()
        factores = self.factores.de(entrada.usuario_id)
        admitidos = {Factor.TOTP, Factor.PASSKEY} if factores.totp else {Factor.CONTRASENA, Factor.PASSKEY}
        if entrada.factor not in admitidos:
            raise CodigoNoValidoException(
                "Con la verificación en dos pasos activa, confirma con tu app o con una passkey."
            )
        with fallo_cerrado(), self.uow:
            hecho = self.comprobar.comprobar(
                entrada.usuario_id, entrada.factor, codigo=entrada.codigo, respuesta=entrada.respuesta,
                ambito=f"reautenticar:{entrada.usuario_id}",
            )  # fmt: skip
            if not hecho.error:
                nueva = autenticacion.con(entrada.factor, self.reloj.ahora(), sincronizada=hecho.sincronizada)
                self.sesiones.reautenticada(entrada.sid, nueva)
        if hecho.error:
            raise hecho.error
        return AutenticacionOutputDTO.desde_vo(nueva)
