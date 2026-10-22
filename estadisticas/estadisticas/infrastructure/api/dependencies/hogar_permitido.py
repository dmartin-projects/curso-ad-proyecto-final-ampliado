# estadisticas/infrastructure/api/dependencies/hogar_permitido.py — el hogar de la URL, si quien llama es miembro
# (módulos 36, 85 y 89)
#
# Como HogarDesdeUrlMixin en el monolito: la autorización es del adapter de entrada y va ANTES que nada (también
# antes de validar los query params del endpoint).
from typing import Annotated

from fastapi import Depends, HTTPException, status

from estadisticas.domain.repositories.i_membresia_query_service import IMembresiaQueryService
from estadisticas.infrastructure import container
from estadisticas.infrastructure.api.dependencies.usuario_actual import usuario_actual


def hogar_permitido(
    hogar_id: int,
    usuario: Annotated[int, Depends(usuario_actual)],
    membresias: Annotated[IMembresiaQueryService, Depends(container.membresia_query_service)],
) -> int:
    if not membresias.es_miembro(hogar_id, usuario):  # 404 y no 403: no revelar que el hogar existe (módulo 36)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
    return hogar_id


Hogar = Annotated[int, Depends(hogar_permitido)]
