# usuarios/infrastructure/mfa/webauthn_duo.py — IWebAuthn con la librería webauthn de Duo (módulo 92)
#
# Lo que comprueba la librería en cada respuesta: que el challenge es el que se dio, que el origen del navegador
# (clientDataJSON) es el de Gastos, que el hash del rp_id (authenticatorData) es el de Gastos, los flags (presencia
# y, si se exige, verificación del usuario), la firma con la clave pública guardada y que el signCount no retrocede
# (solo si se le da el que había: `credential_current_sign_count`). Lo que decide Gastos: el rp_id y el origen de cada
# entorno, qué exige en cada ceremonia y con qué contador compara.
import logging
from urllib.parse import urlsplit

from django.conf import settings
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import base64url_to_bytes
from webauthn.helpers.exceptions import WebAuthnException
from webauthn.helpers.options_to_json_dict import options_to_json_dict
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    AuthenticatorTransport,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from usuarios.application.ports.i_webauthn import IWebAuthn
from usuarios.domain.exceptions.passkey_no_valida_exception import PasskeyNoValidaException
from usuarios.domain.vo.credencial_nueva import CredencialNueva
from usuarios.domain.vo.firma_comprobada import FirmaComprobada
from usuarios.domain.vo.reto import Reto

logger = logging.getLogger(__name__)


TRANSPORTES = {t.value for t in AuthenticatorTransport}


def rp_id() -> str:
    """El dominio al que quedan atadas las passkeys: el host de la app (gastos.tudominio.com; en local, localhost).
    El navegador solo deja usar una passkey en ese dominio (o en sus subdominios): una web falsa no puede pedirla."""
    return settings.WEBAUTHN_RP_ID or urlsplit(settings.FRONTEND_URL).hostname


def origen() -> str:
    """El origen exacto desde el que se hacen las ceremonias: el de la SPA (Vercel reenvía /api a Django)."""
    partes = urlsplit(settings.FRONTEND_URL)
    return f"{partes.scheme}://{partes.netloc}"


def _descriptor(credencial_id: bytes, transportes=()) -> PublicKeyCredentialDescriptor:
    validos = [AuthenticatorTransport(t) for t in transportes if t in TRANSPORTES]
    return PublicKeyCredentialDescriptor(id=credencial_id, transports=validos or None)


class WebAuthnDuo(IWebAuthn):
    def opciones_de_registro(self, *, manija, cuenta, nombre, excluir):
        opciones = generate_registration_options(
            rp_id=rp_id(),
            rp_name="Gastos",
            user_id=manija,
            user_name=cuenta,
            user_display_name=nombre or cuenta,
            exclude_credentials=[_descriptor(c) for c in excluir],
            # Una passkey de verdad: la guarda el autenticador (discoverable: se entra sin escribir el email) y pide
            # huella, cara o PIN (sirve sola, sin contraseña). Sin attestation: Gastos no restringe marcas de
            # autenticador, y pedirla solo añade un aviso de privacidad al usuario
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.REQUIRED,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
        )
        return Reto(options_to_json_dict(opciones), opciones.challenge)

    def comprobar_registro(self, respuesta, challenge):
        try:
            hecho = verify_registration_response(
                credential=respuesta, expected_challenge=challenge, expected_rp_id=rp_id(),
                expected_origin=origen(), require_user_verification=True,
            )  # fmt: skip
        except (WebAuthnException, KeyError, TypeError, ValueError) as error:
            logger.info("Registro de passkey rechazado: %s", error)  # el motivo, al log; a la persona, uno genérico
            raise PasskeyNoValidaException() from error
        transportes = tuple(t for t in (respuesta.get("response") or {}).get("transports") or [] if t in TRANSPORTES)
        return CredencialNueva(
            hecho.credential_id, hecho.credential_public_key, hecho.sign_count, hecho.credential_backed_up, transportes
        )

    def opciones_de_entrada(self, *, permitir, exigir_verificacion):
        opciones = generate_authentication_options(
            rp_id=rp_id(),
            allow_credentials=[_descriptor(p.credencial_id, p.transportes) for p in permitir],
            user_verification=(
                UserVerificationRequirement.REQUIRED if exigir_verificacion else UserVerificationRequirement.PREFERRED
            ),
        )
        return Reto(options_to_json_dict(opciones), opciones.challenge)

    def credencial(self, respuesta):
        try:
            credencial_id = base64url_to_bytes(respuesta["rawId"])
            manija = (respuesta.get("response") or {}).get("userHandle")
            return credencial_id, base64url_to_bytes(manija) if manija else None
        except (KeyError, TypeError, ValueError, AttributeError) as error:
            raise PasskeyNoValidaException() from error

    def comprobar_entrada(self, respuesta, challenge, passkey, *, exigir_verificacion):
        try:
            hecho = verify_authentication_response(
                credential=respuesta, expected_challenge=challenge, expected_rp_id=rp_id(), expected_origin=origen(),
                credential_public_key=passkey.clave_publica,
                credential_current_sign_count=passkey.contador,  # con 0 siempre, la comprobación no haría nada
                require_user_verification=exigir_verificacion,
            )  # fmt: skip
        except (WebAuthnException, KeyError, TypeError, ValueError) as error:
            logger.info("Passkey rechazada: %s", error)
            raise PasskeyNoValidaException() from error
        return FirmaComprobada(hecho.new_sign_count, hecho.credential_backed_up)
