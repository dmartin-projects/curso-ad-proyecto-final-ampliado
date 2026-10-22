# core/infrastructure/api/serializers/regla.py — los serializers llaman a las reglas del dominio (módulo 87)
from rest_framework import serializers

from core.domain.exceptions.dominio_exception import DominioException


def regla(funcion, *args):
    """Ejecuta una regla del dominio en un `validate_<campo>` de DRF: DominioException → ValidationError.

    La regla vive en el dominio (una sola vez); el serializer solo la llama para que la API pueda devolver
    TODOS los errores del formulario a la vez. El use case la vuelve a exigir: otros adaptadores de entrada
    (Celery, un comando, las tools del agente de la Parte 7) no pasan por este serializer.
    """
    try:
        return funcion(*args)
    except DominioException as e:
        raise serializers.ValidationError(str(e.mensaje)) from e
