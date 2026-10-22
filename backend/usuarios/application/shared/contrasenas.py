# usuarios/application/shared/contrasenas.py — lo que comparten los use cases de las cuentas (módulo 88)
from usuarios.application.ports.i_enlaces import IEnlaces
from usuarios.application.ports.i_politica_de_contrasenas import IPoliticaDeContrasenas
from usuarios.domain.events.registro_por_completar_event import RegistroPorCompletarEvent
from usuarios.domain.exceptions.contrasena_no_valida_exception import ContrasenaNoValidaException


def exigir_politica(politica: IPoliticaDeContrasenas, password: str, campo: str, *, usuario_id: int) -> None:
    """Todos los motivos a la vez, en el campo del formulario donde se pintan (password o nueva)."""
    if motivos := politica.incumplimientos(password, usuario_id=usuario_id):
        raise ContrasenaNoValidaException(motivos, campo=campo)


def evento_completar_registro(enlaces: IEnlaces, usuario_id: int) -> RegistroPorCompletarEvent:
    """El correo para elegir la contraseña: lo reciben un registro nuevo y uno pendiente que lo pide otra vez."""
    return RegistroPorCompletarEvent(usuario_id, enlaces.crear(usuario_id, "completar-registro"))
