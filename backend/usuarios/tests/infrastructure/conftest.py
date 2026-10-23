"""Los tres proveedores, de mentira (respx), para los tests del social login (módulo 91)."""

from types import SimpleNamespace

import pytest
import respx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from usuarios.tests.infrastructure.proveedor_falso import GitHubFalso, OIDCFalso

GOOGLE, APPLE = "https://accounts.google.example", "https://appleid.apple.example"
GITHUB_WEB, GITHUB_API = "https://github.example", "https://api.github.example"


@pytest.fixture
def proveedores(settings):
    clave_apple = ec.generate_private_key(ec.SECP256R1())
    pem = clave_apple.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    settings.FRONTEND_URL = "https://gastos.example"
    settings.SOCIAL_LOGIN = {
        "google": {"client_id": "gastos.apps.googleusercontent.example", "client_secret": "secreto-google", "emisor": GOOGLE},
        "github": {"client_id": "Iv23liGastos", "client_secret": "secreto-github", "web": GITHUB_WEB, "api": GITHUB_API},
        "apple": {"client_id": "com.example.gastos.web", "equipo": "EQUIPO1234", "clave_id": "CLAVE12345",
                  "clave_privada": pem.decode(), "emisor": APPLE},
    }  # fmt: skip
    with respx.mock(assert_all_called=False) as mock:  # una petición a algo no simulado: error (nada sale fuera)
        yield SimpleNamespace(
            google=OIDCFalso(mock, GOOGLE, "gastos.apps.googleusercontent.example"),
            apple=OIDCFalso(mock, APPLE, "com.example.gastos.web", pkce=False, form_post=True),  # Apple no anuncia PKCE
            github=GitHubFalso(mock, GITHUB_WEB, GITHUB_API),
            clave_apple=clave_apple.public_key(),
            http=mock,
        )
