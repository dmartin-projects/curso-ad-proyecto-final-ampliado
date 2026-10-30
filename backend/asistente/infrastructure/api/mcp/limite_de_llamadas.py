# asistente/infrastructure/api/mcp/limite_de_llamadas.py — cuántas llamadas por minuto (ejercicio 1 del 104)
"""Un cliente MCP es un programa que llama en bucle: un agente que se equivoca, un script que alguien olvidó parar.
Cada llamada es una consulta a PostgreSQL con el permiso de una persona. El límite, por persona Y por cliente: un
cliente que abusa no agota el de los demás clientes de la misma persona.

Ventana fija de un minuto en la caché de Django (Redis en producción, compartida por todos los workers): una clave por
minuto, `incr` atómico y caducidad de dos minutos. Al pasarse, los segundos que faltan para el minuto siguiente."""

import time

from django.core.cache import cache


class LimiteDeLlamadas:
    def __init__(self, por_minuto: int, reloj=time.time):
        self.por_minuto, self.reloj = por_minuto, reloj

    def espera(self, cliente: str, usuario: str) -> int:
        """0 si puede llamar (y la cuenta); si no, los segundos hasta que pueda."""
        ahora = self.reloj()
        minuto = int(ahora // 60)
        clave = f"asistente:mcp:llamadas:{cliente}:{usuario}:{minuto}"
        cache.add(clave, 0, timeout=120)  # add no pisa: si ya existe, la cuenta sigue
        if cache.incr(clave) <= self.por_minuto:
            return 0
        return max(1, 60 - int(ahora % 60))
