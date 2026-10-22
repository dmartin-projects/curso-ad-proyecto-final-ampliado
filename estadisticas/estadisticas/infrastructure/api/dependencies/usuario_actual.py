# estadisticas/infrastructure/api/dependencies/usuario_actual.py — quién llama: el JWT de Django (módulos 85 y 89)
#
# Autenticación con el MISMO JWT que emite Django: el servicio comprueba la firma con la clave compartida y saca el
# usuario del token, sin llamar a Django. La clave se pide al composition root con Depends.
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from estadisticas.infrastructure import container

bearer = HTTPBearer(auto_error=False)


def usuario_actual(
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    clave: Annotated[str, Depends(container.clave_jwt)],
) -> int:
    no_autenticado = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Credenciales no válidas", {"WWW-Authenticate": "Bearer"}
    )
    if credenciales is None:
        raise no_autenticado
    try:
        datos = jwt.decode(
            credenciales.credentials,
            clave,
            algorithms=["HS256"],  # SIEMPRE la lista explícita: nunca aceptar el algoritmo que diga el token
            options={"require": ["exp", "user_id", "token_type"]},
        )
    except jwt.InvalidTokenError as e:  # firma mala, caducado, mal formado…
        raise no_autenticado from e
    if datos["token_type"] != "access":  # un refresh token no sirve para llamar a la API
        raise no_autenticado
    return int(datos["user_id"])
