# oauth/infrastructure/crypto/claves.py — la clave con la que el servidor firma los ID tokens (módulo 90)
#
# Sin Django: la usan los ajustes de tests y E2E (una clave nueva en cada arranque) y el comando generar_clave_oidc.
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def nueva_clave_pem() -> str:
    """Una clave RSA de 2048 bits en PEM (PKCS#8), la que espera OIDC_RSA_PRIVATE_KEY. RS256 con 2048 bits es lo
    que exige como mínimo el RFC 7518 §3.3 y lo que usan Google o Microsoft."""
    clave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return clave.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    ).decode()
