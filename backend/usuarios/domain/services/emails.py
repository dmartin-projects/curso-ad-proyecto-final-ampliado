# usuarios/domain/services/emails.py — cómo se identifica a una persona (módulos 35 y 88)
#
# La autenticación (contraseñas con hash, tokens de un solo uso, JWT) es de Django y de simplejwt: un subdominio
# genérico que no se reescribe. Lo que sí es de Gastos: cómo se identifica a alguien (su email, en minúsculas), que la
# contraseña la elige quien abre el enlace del correo (el registro no la pide), y que ni registrarse ni pedir una
# contraseña nueva revelan qué emails tienen cuenta.
from usuarios.domain.exceptions.email_no_valido_exception import EmailNoValidoException


def normalizar_email(email: str) -> str:
    """'  Ana@Example.COM ' → 'ana@example.com'. Toda la dirección en minúsculas, no solo el dominio
    (normalize_email de Django solo baja el dominio): "Ana@x.com" y "ana@x.com" son la misma persona."""
    email = (email or "").strip().lower()
    if "@" not in email.strip("@"):
        raise EmailNoValidoException()
    return email
