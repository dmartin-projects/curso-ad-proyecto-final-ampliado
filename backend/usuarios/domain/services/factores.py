# usuarios/domain/services/factores.py — qué factores hay, qué cuenta como multifactor y cuándo hace falta el segundo (módulo 92)
from usuarios.domain.enums.factor import Factor

PRIMEROS_FACTORES = frozenset({Factor.CONTRASENA, Factor.PROVEEDOR})  # los que, solos, son un factor


SEGUNDOS_FACTORES = frozenset({Factor.TOTP, Factor.RECUPERACION, Factor.PASSKEY})


# Los valores de `amr` (RFC 8176) de cada factor. "fed" no está en el registro del RFC: es el que usa Microsoft Entra
# para "un proveedor federado", y el más claro para un cliente. Un código de recuperación es una contraseña de un solo
# uso de una lista: "otp".
AMR = {Factor.CONTRASENA: "pwd", Factor.PROVEEDOR: "fed", Factor.TOTP: "otp", Factor.RECUPERACION: "otp"}


ACR_UN_FACTOR, ACR_MULTIFACTOR = "urn:gastos:acr:1fa", "urn:gastos:acr:mfa"


def exige_segundo_factor(primero: Factor, *, mfa_activo: bool) -> bool:
    """Con MFA activo, la contraseña o un proveedor no bastan. Política de Gastos: el MFA del proveedor no cuenta
    (Google y Apple no dicen si lo hubo; Entra lo dice, pero lo controla el administrador de cada tenant). Una passkey
    sí basta: ya son dos factores en un gesto."""
    return mfa_activo and primero in (Factor.CONTRASENA, Factor.PROVEEDOR)
