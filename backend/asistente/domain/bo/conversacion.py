# asistente/domain/bo/conversacion.py — una conversación con el asistente (módulo 97)
from dataclasses import dataclass

from core.domain.exceptions.validacion_exception import ValidacionException

MAX_TITULO = 80


def _titulo(texto: str) -> str:
    titulo = " ".join(texto.split())  # sin saltos de línea ni espacios dobles: va en una lista
    if not titulo or len(titulo) > MAX_TITULO:
        raise ValidacionException(f"El título tiene entre 1 y {MAX_TITULO} caracteres.", campo="titulo")
    return titulo


@dataclass(eq=False)
class Conversacion:
    """Una conversación es de UNA persona en UN hogar: los demás miembros no la ven y no cambia de hogar.

    El título lo pone el asistente tras la primera respuesta (`titular`), salvo que la persona lo haya cambiado: el
    suyo manda siempre (`renombrar`).
    """

    usuario_id: int
    hogar_id: int
    titulo: str = ""
    titulo_manual: bool = False
    carpeta_id: int | None = None
    id: int | None = None

    def titular(self, titulo: str) -> bool:
        """El título automático. Devuelve si ha cambiado (no cambia si ya lo eligió la persona)."""
        if self.titulo_manual:
            return False
        self.titulo = _titulo(titulo[:MAX_TITULO])
        return True

    def renombrar(self, titulo: str) -> None:
        self.titulo = _titulo(titulo)
        self.titulo_manual = True

    def mover_a(self, carpeta_id: int | None) -> None:
        """A una carpeta de la misma persona en el mismo hogar (lo comprueba el use case) o fuera de todas (None)."""
        self.carpeta_id = carpeta_id
