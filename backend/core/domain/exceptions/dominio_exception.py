# core/domain/exceptions/dominio_exception.py — la base de los errores de negocio (módulos 38 y 87)
#
# Sin Django: los lanza el dominio y los traduce a HTTP un único exception handler
# (core/infrastructure/api/exceptions/manejador_errores.py), nunca un try/except por view.
class DominioException(Exception):
    """Base de los errores de negocio. Cada subclase dice cómo se ve en la API.

    `campo`: si el error es de un dato concreto ("nombre", "padre"), la API lo devuelve con el formato de los
    errores de validación (400 y `errors: {campo: [mensaje]}`), igual que si lo hubiera detectado un serializer.
    """

    codigo = "error_de_dominio"
    status = 409
    mensaje = "La operación no es posible en el estado actual."
    campo: str | None = None

    def __init__(self, mensaje: str | None = None, *, campo: str | None = None, **contexto):
        super().__init__(mensaje or self.mensaje)
        self.mensaje = mensaje or self.mensaje
        if campo is not None:
            self.campo = campo
        self.contexto = contexto
