# hogares/domain/services/administradores.py — LA regla de los miembros: un hogar necesita un administrador (módulo 88)
from hogares.domain.bo.membresia import Membresia
from hogares.domain.exceptions.ultimo_administrador_exception import UltimoAdministradorException


def exigir_otro_admin(membresia: Membresia, admins: int) -> None:
    """Un hogar necesita al menos un administrador: el último no puede dejar de serlo… ni irse (módulos 71 y 88).

    `admins`: cuántos tiene el hogar AHORA (contados con las filas bloqueadas: dos peticiones a la vez no pueden
    quitar cada una a uno de los dos últimos).
    """
    if membresia.es_admin and admins <= 1:
        raise UltimoAdministradorException()
