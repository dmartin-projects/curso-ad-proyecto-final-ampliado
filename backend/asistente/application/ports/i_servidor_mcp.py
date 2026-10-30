# asistente/application/ports/i_servidor_mcp.py — otro servidor de tools, visto desde el agente (módulo 104)
from abc import ABC, abstractmethod
from dataclasses import dataclass

from asistente.domain.vo.declaracion_tool import DeclaracionTool


@dataclass(frozen=True, slots=True)
class ResultadoRemoto:
    texto: str
    es_error: bool = False


class IServidorMCP(ABC):
    """Un servidor MCP del que el agente usa tools. Lo implementa ServidorMCPRemoto (el SDK oficial, con un pool de
    clientes) y, en los tests, un fake. El agente no sabe que hay un protocolo: ve tools."""

    nombre: str  # corto y fijo: va delante del nombre de cada tool ("calendario__proximos_pagos")

    @abstractmethod
    def tools(self) -> tuple[DeclaracionTool, ...]:
        """Las tools que el agente puede usar (solo las aprobadas, ver ServidorMCPRemoto). Lanza
        ServicioExternoNoDisponibleException si el servidor no responde."""

    @abstractmethod
    def llamar(self, tool: str, argumentos: dict) -> ResultadoRemoto:
        """Lanza ServicioExternoNoDisponibleException si el servidor no responde."""
