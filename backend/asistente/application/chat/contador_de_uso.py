# asistente/application/chat/contador_de_uso.py — lo que gasta una pregunta, modelo a modelo (módulo 98)
from collections import defaultdict
from datetime import datetime

from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.application.ports.i_tarifas import ITarifas
from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.vo.ayuda_consultada import AyudaConsultada
from asistente.domain.vo.consumo import Consumo
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from asistente.domain.vo.uso import Uso


class ContadorDeUso(IObservadorAgente):
    """Un decorator del observador: deja pasar cada paso al de dentro (el del chat) y, de paso, suma el uso de cada
    turno del modelo, por modelo. Así lo gastado se sabe AUNQUE la pregunta no termine: si la persona cancela en la
    tercera vuelta, las dos primeras se pagaron, y ResultadoAgente (que no llega a existir) no lo diría.

    Por modelo, porque con la reserva una pregunta puede pasar por dos y no cuestan lo mismo."""

    def __init__(self, dentro: IObservadorAgente, con_ayuda: bool = True):
        self.dentro = dentro
        self.usos: dict[str, Uso] = defaultdict(Uso)
        # Ejercicio 1 del 100: lo que gasta buscar_ayuda con el modelo auxiliar, aparte (otro canal)
        self.ayuda = ContadorDeUso(dentro, con_ayuda=False) if con_ayuda else None

    def sumar(self, respuesta: RespuestaLLM | None) -> None:
        """También para lo que no pasa por el agente (el título)."""
        if respuesta is not None:
            self.usos[respuesta.modelo] += respuesta.uso

    def respuesta(self, respuesta):
        self.sumar(respuesta)  # antes que el de dentro: si este corta (cancelada), el turno ya se ha pagado
        self.dentro.respuesta(respuesta)

    def llamada(self, llamada):
        self.dentro.llamada(llamada)

    def resultado(self, resultado, duracion_ms):
        self.dentro.resultado(resultado, duracion_ms)

    def artefacto(self, artefacto):
        if isinstance(artefacto, AyudaConsultada) and self.ayuda is not None:
            for r in artefacto.llamadas:
                self.ayuda.sumar(r)
        self.dentro.artefacto(artefacto)

    def consumos(
        self,
        *,
        usuario_id: int,
        hogar_id: int,
        conversacion_id: int | None,
        canal: CanalDeConsumo,
        tarifas: ITarifas,
        momento: datetime,
    ) -> list[Consumo]:
        consumos = []
        for modelo, uso in self.usos.items():
            if uso.total == 0:  # un modelo que no contestó (o un proveedor que no manda el uso): nada que apuntar
                continue
            precio = tarifas.precio(modelo)
            coste = precio.coste(uso) if precio else None
            consumos.append(Consumo(usuario_id, hogar_id, canal, modelo, uso, coste, momento, conversacion_id))
        return consumos
