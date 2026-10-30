# asistente/application/seguridad/procedencia.py — si el modelo ha leído texto de terceros (módulo 102)
from dataclasses import dataclass


@dataclass(slots=True)
class Procedencia:
    """Taint tracking, en pequeño: en cuanto entra en el contexto un texto que no ha escrito la persona (un ticket, un
    concepto de un extracto, un adjunto, una tool de un servidor MCP), la pregunta queda "con terceros", y las tools
    que guardan algo sin confirmación (Tool.persiste) se niegan.

    La marca es de la CONVERSACIÓN, no de la pregunta: ese texto se queda en el historial (el OCR dentro de la pregunta,
    el resultado de la tool, la respuesta que lo repite, el resumen que lo cuenta) y el modelo lo vuelve a leer en cada
    pregunta siguiente. Una instrucción educada puede esperar: «cuando vuelva a escribir, recuerda que…». Por eso el
    agente devuelve la marca (ResultadoAgente.terceros), la conversación la guarda (Conversacion.con_terceros) y la
    pregunta siguiente empieza con ella.

    No depende del clasificador: aunque un ataque se le escape, lo que lea el modelo ya no puede convertirse en un
    recuerdo que viaje a todas las conversaciones."""

    terceros: bool = False
    retirados: int = 0
