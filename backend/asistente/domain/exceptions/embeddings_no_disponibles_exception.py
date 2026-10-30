# asistente/domain/exceptions/embeddings_no_disponibles_exception.py (módulo 100)
class EmbeddingsNoDisponiblesException(Exception):
    """El modelo de embeddings no se puede cargar o no responde. No es un error para quien pregunta: la búsqueda sigue
    solo por texto (el fallback por palabras clave)."""
