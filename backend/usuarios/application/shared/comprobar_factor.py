# usuarios/application/shared/comprobar_factor.py — comprobar un factor y llevar la cuenta de los fallos (módulo 92)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from usuarios.application.ports.i_codigos_de_recuperacion import ICodigosDeRecuperacion
from usuarios.application.ports.i_retos import IRetos
from usuarios.application.ports.i_totp import ITotp
from usuarios.application.ports.i_webauthn import IWebAuthn
from usuarios.application.shared.comprobacion import Comprobacion
from usuarios.domain.enums.factor import Factor
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.domain.exceptions.contrasena_incorrecta_exception import ContrasenaIncorrectaException
from usuarios.domain.exceptions.passkey_no_valida_exception import PasskeyNoValidaException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from usuarios.domain.repositories.i_passkey_command_repository import IPasskeyCommandRepository
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository


class ComprobarFactor:
    """Comprueba un factor de una cuenta (un código TOTP, uno de recuperación, una passkey o la contraseña) y lleva la
    cuenta de los fallos. Lo usan el segundo paso del login y el step-up, dentro de su transacción.

    Un factor que no vale no es una excepción AQUÍ sino un resultado: el fallo tiene que quedar guardado, y una
    excepción dentro de la transacción del use case lo desharía. El use case confirma la transacción y lanza después.
    Los fallos seguidos avisan por email: quien falla el segundo factor ya tiene la contraseña.
    """

    def __init__(
        self,
        *,
        cuentas: ICuentaCommandRepository,
        segundos: ISegundoFactorCommandRepository,
        totp: ITotp,
        codigos: ICodigosDeRecuperacion,
        passkeys: IPasskeyCommandRepository,
        webauthn: IWebAuthn,
        retos: IRetos,
        eventos: IPublicadorEventos,
        reloj: IReloj,
    ):
        self.cuentas, self.segundos, self.totp, self.codigos = cuentas, segundos, totp, codigos
        self.passkeys, self.webauthn, self.retos, self.eventos, self.reloj = passkeys, webauthn, retos, eventos, reloj

    def comprobar(self, usuario_id: int, factor: Factor, *, codigo="", respuesta=None, ambito="") -> Comprobacion:
        segundo = self.segundos.de(usuario_id, bloquear=True)  # dos intentos a la vez, uno detrás de otro
        segundo.exigir_desbloqueado(self.reloj.ahora())  # SegundoFactorBloqueadoException: ni se mira el código
        try:
            sincronizada = self._comprobar(usuario_id, segundo, factor, codigo, respuesta, ambito)
        except (CodigoNoValidoException, PasskeyNoValidaException, ContrasenaIncorrectaException) as error:
            aviso = segundo.anotar_fallo(self.reloj.ahora())
            self.segundos.guardar(segundo)
            if aviso is not None:  # 5 fallos seguidos, o el techo: "alguien tiene tu contraseña"
                self.eventos.publicar(SeguridadCambiadaEvent(usuario_id, aviso.value))
            return Comprobacion(error=error)
        segundo.anotar_acierto()
        self.segundos.guardar(segundo)
        return Comprobacion(sincronizada=sincronizada)

    def _comprobar(self, usuario_id, segundo, factor, codigo, respuesta, ambito) -> bool:
        match factor:
            case Factor.TOTP:
                codigo = "".join((codigo or "").split())  # "123 456" es 123456 (la contraseña, tal cual)
                paso = self.totp.paso(segundo.secreto, codigo, self.reloj.ahora()) if segundo.activo else None
                if paso is None:
                    raise CodigoNoValidoException()
                segundo.aceptar(paso)  # CodigoNoValidoException si ese paso ya se usó: un código, una vez
            case Factor.RECUPERACION:
                if not self.codigos.usar(usuario_id, codigo):
                    raise CodigoNoValidoException()
            case Factor.CONTRASENA:
                if not self.cuentas.comprobar_contrasena(usuario_id, codigo):
                    raise ContrasenaIncorrectaException()
            case Factor.PASSKEY:
                return self._passkey(usuario_id, respuesta or {}, ambito)
            case _:
                raise CodigoNoValidoException()
        return False

    def _passkey(self, usuario_id: int, respuesta: dict, ambito: str) -> bool:
        challenge = self.retos.consumir(ambito)
        credencial_id, _ = self.webauthn.credencial(respuesta)
        passkey = self.passkeys.por_credencial(credencial_id)
        if challenge is None or passkey is None or passkey.usuario_id != usuario_id:
            raise PasskeyNoValidaException()
        firma = self.webauthn.comprobar_entrada(respuesta, challenge, passkey, exigir_verificacion=False)
        passkey.contador, passkey.sincronizada = firma.contador, firma.sincronizada
        self.passkeys.guardar(passkey)
        return firma.sincronizada
