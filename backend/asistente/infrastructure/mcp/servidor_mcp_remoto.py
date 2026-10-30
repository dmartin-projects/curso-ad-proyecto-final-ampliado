# asistente/infrastructure/mcp/servidor_mcp_remoto.py — IServidorMCP con el SDK oficial de MCP (módulo 104)
"""Un servidor MCP de otros, con la desconfianza que merece:

- **Solo las tools aprobadas, con su huella.** La descripción y el schema de una tool los lee el modelo en CADA
  llamada: son instrucciones. Un servidor que cambia la descripción de una tool ya aprobada ("rug pull") o que trae
  una tool nueva con instrucciones dentro ("tool poisoning") no entra: cada tool aprobada lleva la huella (SHA-256)
  de su nombre, descripción y schema, y si no coincide, fuera, con un aviso en el log. `manage.py huellas_mcp`
  enseña las huellas actuales para revisarlas y aprobarlas.
- **Sus resultados son de terceros** (ToolRemota.lee_terceros, módulo 102).
- **Su token es suyo**: cada servidor tiene su credencial (la que ESE servidor emite); nunca se le reenvía el token de
  la persona en Gastos (token passthrough, prohibido por la especificación).
- **Timeout, circuit breaker y caché** de la lista de tools, como cualquier servicio externo (módulo 95).
"""

import hashlib
import json
import logging
import re

import mcp_types as types
from django.core.cache import cache

from asistente.application.ports.i_servidor_mcp import IServidorMCP, ResultadoRemoto
from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.vo.declaracion_tool import DeclaracionTool
from asistente.infrastructure.mcp.pool import PoolMCP
from core.infrastructure.cache.circuit_breaker import CircuitBreaker
from core.infrastructure.cache.circuito_abierto_exception import CircuitoAbiertoException

logger = logging.getLogger(__name__)
MAX_DESCRIPCION = 1024  # una descripción larga son tokens en cada llamada (y espacio para esconder cosas)
# El nombre que verá el modelo ("servidor__tool") tiene que valer para TODOS los proveedores: Chat Completions y la
# Messages API aceptan letras, cifras, "_" y "-", hasta 64. Uno que no, rompería todas las preguntas del chat
NOMBRE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def huella(tool: types.Tool) -> str:
    """Lo que el modelo lee de una tool, resumido: si cambia una coma, cambia."""
    contenido = json.dumps(
        {"nombre": tool.name, "descripcion": tool.description or "", "schema": tool.input_schema}, sort_keys=True
    )
    return hashlib.sha256(contenido.encode()).hexdigest()[:16]


class ServidorMCPRemoto(IServidorMCP):
    def __init__(
        self, *, nombre: str, url: str, token: str, aprobadas: dict[str, str], pool: PoolMCP, timeout: float = 10.0
    ):
        self.nombre, self.url, self.token, self.aprobadas = nombre, url, token, aprobadas
        self.pool, self.timeout = pool, timeout
        self.circuito = CircuitBreaker(f"mcp:{nombre}", umbral=3, enfriamiento=60)

    def tools(self) -> tuple[DeclaracionTool, ...]:
        clave = f"asistente:mcp:{self.nombre}:tools"
        if (guardadas := cache.get(clave)) is not None:
            return tuple(DeclaracionTool(*t) for t in guardadas)
        todas = self._pedir(lambda c: c.list_tools()).tools
        buenas = []
        for t in todas:
            esperada = self.aprobadas.get(t.name)
            if esperada is None:
                continue  # no aprobada: el modelo ni la ve
            if huella(t) != esperada or len(t.description or "") > MAX_DESCRIPCION:
                logger.warning("MCP %s: la tool %s ha cambiado (huella %s): fuera", self.nombre, t.name, huella(t))
                continue
            if not NOMBRE.match(f"{self.nombre}__{t.name}"):
                logger.warning("MCP %s: el nombre de la tool %r no vale para el modelo: fuera", self.nombre, t.name)
                continue
            buenas.append((t.name, t.description or "", dict(t.input_schema)))
        cache.set(clave, buenas, 300)
        return tuple(DeclaracionTool(*t) for t in buenas)

    def todas_con_huella(self) -> list[tuple[str, str, str]]:
        """Para huellas_mcp: (nombre, huella, descripción) de TODAS las tools del servidor."""
        return [(t.name, huella(t), t.description or "") for t in self._pedir(lambda c: c.list_tools()).tools]

    def llamar(self, tool: str, argumentos: dict) -> ResultadoRemoto:
        r = self._pedir(lambda c: c.call_tool(tool, argumentos))
        textos = [c.text for c in r.content if isinstance(c, types.TextContent)]
        return ResultadoRemoto("\n".join(textos) or "(sin texto)", es_error=bool(r.is_error))

    def _pedir(self, operacion):
        try:
            return self.circuito.llamar(self.pool.ejecutar, self.url, self.token, operacion, self.timeout)
        except CircuitoAbiertoException as e:
            raise ServicioExternoNoDisponibleException(self.nombre) from e
        except Exception as e:  # red, timeout, protocolo: para el agente, el servidor no está
            logger.warning("MCP %s no responde: %s", self.nombre, type(e).__name__)
            raise ServicioExternoNoDisponibleException(self.nombre) from e
