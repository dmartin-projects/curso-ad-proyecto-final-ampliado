# usuarios/application/iniciar_sesion_use_case/iniciar_sesion_use_case.py — abrir una sesión de la SPA (módulos 35 y 91)
#
# El ÚNICO sitio donde se emiten los tokens de la SPA, se entre como se entre: con la contraseña (LoginView) o con un
# proveedor (la vuelta del social login, tras CompletarLoginSocialUseCase). Autenticar (¿quién es?) y abrir la sesión
# (¿qué se le da?) son dos pasos: lo que haya que exigir antes de dar los tokens se pone aquí, una vez.
# Ejercicio 3: también antes de abrir la sesión de Django de las páginas del authorization server (Canal.AUTORIZACION).
from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.application.iniciar_sesion_use_case.dtos.par_de_tokens_output_dto import ParDeTokensOutputDTO
from usuarios.application.iniciar_sesion_use_case.i_iniciar_sesion_use_case import IIniciarSesionUseCase
from usuarios.application.ports.i_tokens import ITokens
from usuarios.domain.enums.canal import Canal
from usuarios.domain.exceptions.cuenta_desactivada_exception import CuentaDesactivadaException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository


class IniciarSesionUseCase(IIniciarSesionUseCase):
    def __init__(self, *, cuentas: ICuentaCommandRepository, tokens: ITokens):
        self.cuentas, self.tokens = cuentas, tokens

    def ejecutar(self, entrada: IniciarSesionInputDTO) -> ParDeTokensOutputDTO | None:
        if not self.cuentas.activa(entrada.usuario_id):  # desactivada por soporte: ni con la contraseña ni con Google
            raise CuentaDesactivadaException()
        if entrada.canal is not Canal.SPA:  # la sesión del authorization server la abre su adapter (django login)
            return None
        return ParDeTokensOutputDTO.desde_vo(self.tokens.emitir(entrada.usuario_id))
