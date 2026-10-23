# usuarios/application/shared/login_pendiente.py — leer el login a medias de un canal (módulo 92)
from usuarios.application.ports.i_pendientes import IPendientes
from usuarios.domain.enums.canal import Canal
from usuarios.domain.exceptions.login_pendiente_no_valido_exception import LoginPendienteNoValidoException
from usuarios.domain.vo.login_pendiente import LoginPendiente


def leer_pendiente(pendientes: IPendientes, clave: str | None, canal: Canal) -> LoginPendiente:
    pendiente = pendientes.leer(clave) if clave else None
    if pendiente is None or pendiente.canal != canal:  # la de la SPA no vale en el authorization server
        raise LoginPendienteNoValidoException()
    return pendiente
