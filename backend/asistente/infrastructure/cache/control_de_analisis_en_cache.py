# asistente/infrastructure/cache/control_de_analisis_en_cache.py — IControlDeAnalisis con la caché (ejercicios del 105)
"""En la caché de Django: Redis en producción, compartida por la API y los workers de Celery.

- El cerrojo, con `add` (atómico: si la clave existe, no la pisa y devuelve False) y caducidad igual al `time_limit`
  de la tarea: si el worker muere a mitad, el cerrojo se va solo.
- La cancelación, una marca con la persona en la clave: nadie puede cancelar el análisis de otro aunque sepa su id."""

from django.core.cache import cache

from asistente.application.ports.i_control_de_analisis import IControlDeAnalisis

DURA = 300  # el time_limit de la tarea analizar_mes


class ControlDeAnalisisEnCache(IControlDeAnalisis):
    def empezar(self, usuario_id, hogar_id, tarea):
        return cache.add(f"asistente:analisis:en_curso:{usuario_id}:{hogar_id}", tarea, timeout=DURA)

    def terminar(self, usuario_id, hogar_id):
        cache.delete(f"asistente:analisis:en_curso:{usuario_id}:{hogar_id}")

    def cancelar(self, usuario_id, tarea):
        cache.set(f"asistente:analisis:cancelado:{usuario_id}:{tarea}", True, timeout=DURA)

    def cancelado(self, usuario_id, tarea):
        return bool(cache.get(f"asistente:analisis:cancelado:{usuario_id}:{tarea}"))
