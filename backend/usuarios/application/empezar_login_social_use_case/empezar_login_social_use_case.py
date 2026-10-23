# usuarios/application/empezar_login_social_use_case/empezar_login_social_use_case.py — la ida al proveedor (módulos 91 y 92)
#
# Gastos es aquí el CLIENTE (Relying Party): manda el navegador al proveedor y, a la vuelta, canjea el code desde el
# servidor (patrón BFF: los tokens del proveedor nunca llegan al navegador). Los use cases no saben de OIDC ni de HTTP:
# eso lo hacen los adapters (infrastructure/providers); aquí, el orden de las comprobaciones y las reglas del dominio.
import secrets

from core.application.ports.i_reloj import IReloj
from usuarios.application.empezar_login_social_use_case.dtos.empezar_login_social_input_dto import (
    EmpezarLoginSocialInputDTO,
)
from usuarios.application.empezar_login_social_use_case.dtos.ida_al_proveedor_output_dto import (
    IdaAlProveedorOutputDTO,
)
from usuarios.application.empezar_login_social_use_case.i_empezar_login_social_use_case import (
    IEmpezarLoginSocialUseCase,
)
from usuarios.application.ports.i_proveedores import IProveedores
from usuarios.application.ports.i_transacciones import ITransacciones
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.exceptions.proveedor_no_disponible_exception import ProveedorNoDisponibleException
from usuarios.domain.services.destino_seguro import destino_seguro
from usuarios.domain.vo.transaccion_social import TransaccionSocial


class EmpezarLoginSocialUseCase(IEmpezarLoginSocialUseCase):
    def __init__(self, *, proveedores: IProveedores, transacciones: ITransacciones, reloj: IReloj):
        self.proveedores, self.transacciones, self.reloj = proveedores, transacciones, reloj

    def ejecutar(self, entrada: EmpezarLoginSocialInputDTO) -> IdaAlProveedorOutputDTO:
        if (entrada.proposito in (Proposito.VINCULAR, Proposito.REAUTENTICAR)) != (entrada.usuario_id is not None):
            raise ValueError("Vincular y reautenticar son para un usuario concreto, y solo eso")
        proveedor = self.proveedores.de(entrada.proveedor)
        reautenticar = entrada.proposito is Proposito.REAUTENTICAR
        if reautenticar and not proveedor.reautentica:  # GitHub: OAuth 2.0 sin ID token, no dice cuándo
            raise ProveedorNoDisponibleException("Con ese proveedor no se puede confirmar quién eres.")
        transaccion = TransaccionSocial(
            proveedor=entrada.proveedor,
            state=secrets.token_urlsafe(32),  # 256 bits: imposibles de adivinar
            nonce=secrets.token_urlsafe(32),
            code_verifier=secrets.token_urlsafe(64),  # 86 caracteres (RFC 7636: entre 43 y 128)
            proposito=entrada.proposito,
            volver=destino_seguro(entrada.volver),
            usuario_id=entrada.usuario_id,
            sid=entrada.sid,
            desde=int(self.reloj.ahora().timestamp()) if reautenticar else None,
        )
        return IdaAlProveedorOutputDTO(
            proveedor.url_de_autorizacion(transaccion),
            self.transacciones.guardar(transaccion),
            form_post=proveedor.modo_respuesta == "form_post",
        )
