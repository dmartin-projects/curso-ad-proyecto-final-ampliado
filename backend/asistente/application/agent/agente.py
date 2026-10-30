# asistente/application/agent/agente.py — el agent loop, escrito a mano (módulos 94, 96, 97 y 98)
"""Preguntar al modelo, ejecutar las tools que pide, devolverle los resultados y repetir hasta que conteste con texto.

    agente = Agente(llm=llm, tools=[ResumenMesTool(finanzas=…), …])
    resultado = agente.responder((Mensaje.usuario("¿Cuánto gastamos en septiembre?"),), contexto)

Lo que lo hace apto para producción, y no un ejemplo de blog (Limites):
- MAX_ITERATIONS: un tope de vueltas; la última se hace SIN tools, para que el modelo conteste con lo que tiene.
- Un tiempo por pregunta: si se acaba, la siguiente vuelta es la última.
- Cuota por tool (Tool.max_llamadas) y nada de repetir la misma llamada con los mismos argumentos.
- Los errores se DEVUELVEN al modelo como resultado, para que se corrija; nunca revientan el bucle.
- Resultados recortados: uno enorme llenaría la context window y dispararía el coste en cada vuelta siguiente.
La reserva de modelos y el circuit breaker no están aquí: van detrás del port (LLMConReserva), y el bucle no se entera.

Módulo 97, para el chat: con `al_texto`, cada vuelta pide la respuesta en streaming (el texto sale según llega), y lo
que las tools producen para la interfaz (gráficos, archivos, propuestas: ConArtefacto) se aparta del resultado que lee
el modelo y se devuelve en ResultadoAgente.artefactos.

Módulo 98: la pregunta y cada tool, dentro de un `with` de la telemetría (spans y métricas; por defecto, ninguna).
"""

import json
import logging
import time
from collections import Counter
from collections.abc import Callable
from traceback import format_tb

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.agent.estructurar import estructurar
from asistente.application.agent.instrucciones import VERSION, instrucciones
from asistente.application.agent.limites import Limites
from asistente.application.agent.observador_mudo import ObservadorMudo
from asistente.application.agent.resultado_agente import ResultadoAgente
from asistente.application.agent.telemetria_muda import TelemetriaMuda
from asistente.application.agent.ventana import ventana
from asistente.application.ports.i_llm import ILLM
from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.application.ports.i_telemetria_del_agente import ITelemetriaDelAgente
from asistente.application.tools.con_artefacto import ConArtefacto
from asistente.application.tools.tool import Tool
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.enums.motivo_parada import MotivoParada
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.vo.artefacto import Artefacto
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.resultado_tool import ResultadoTool
from asistente.domain.vo.uso import Uso
from core.domain.exceptions.dominio_exception import DominioException

logger = logging.getLogger(__name__)

SIN_TERMINAR = "No he podido terminar de responder (demasiados pasos). Prueba a preguntarlo de forma más concreta."
BLOQUEADA = "No puedo responder a eso."


class Agente:
    def __init__(
        self,
        *,
        llm: ILLM,
        tools: list[Tool],
        limites: Limites | None = None,
        observador: IObservadorAgente | None = None,
        telemetria: ITelemetriaDelAgente | None = None,  # módulo 98: trazas y métricas (por defecto, ninguna)
        cronometro: Callable[[], float] = time.monotonic,  # segundos; en los tests, uno que avanza a mano
    ):
        self.llm = llm
        self.tools = {t.nombre: t for t in tools}
        self.declaraciones = tuple(t.declaracion() for t in tools)
        self.limites = limites or Limites()
        self.observador = observador or ObservadorMudo()
        self.telemetria = telemetria or TelemetriaMuda()
        self.cronometro = cronometro

    def responder(
        self,
        historial: tuple[Mensaje, ...],
        contexto: ContextoPregunta,
        estructurada: bool = False,
        al_texto: Callable[[str], None] | None = None,
    ) -> ResultadoAgente:
        """`historial` es la conversación ENTERA (el modelo es stateless) y acaba con la pregunta del usuario. Lo
        que hay que añadirle está en ResultadoAgente.nuevos; quien llama decide dónde guardarlo. Viaja lo que cabe
        en el presupuesto de contexto (ventana.py). Con `estructurada`, una llamada más da la respuesta en JSON.
        Con `al_texto` (módulo 97), el texto de cada vuelta va saliendo por ahí mientras el modelo lo escribe."""
        with self.telemetria.pregunta(contexto) as medir:  # módulo 98: el span de la pregunta, que envuelve los demás
            resultado = self._responder(historial, contexto, estructurada, al_texto)
            medir(resultado)
            return resultado

    def _responder(self, historial, contexto, estructurada, al_texto) -> ResultadoAgente:
        inicio = self.cronometro()
        sistema = instrucciones(contexto)  # el mismo en todas las vueltas: el prefijo que el proveedor cachea
        mensajes, nuevos, llamadas, modelos = list(ventana(historial, self.limites.max_tokens_historial)), [], [], []
        uso = Uso()
        artefactos: list[Artefacto] = []
        usos_por_tool: Counter[str] = Counter()
        ya_llamadas: set[tuple[str, str]] = set()

        def terminar(texto: str, motivo: MotivoParada, forma=None) -> ResultadoAgente:
            resultado = ResultadoAgente(
                texto=texto,
                nuevos=tuple(nuevos),
                motivo=motivo,
                uso=uso,
                iteraciones=len(modelos),
                llamadas=tuple(llamadas),
                modelos=tuple(modelos),
                duracion_ms=int((self.cronometro() - inicio) * 1000),
                estructurada=forma,
                artefactos=tuple(artefactos),
            )
            _registrar(resultado, contexto)
            return resultado

        for iteracion in range(1, self.limites.max_iteraciones + 1):
            sin_tiempo = self.cronometro() - inicio >= self.limites.segundos
            sin_tokens = self.limites.max_tokens is not None and uso.total >= self.limites.max_tokens  # ejercicio 1
            ultima = iteracion == self.limites.max_iteraciones or sin_tiempo or sin_tokens
            if sin_tiempo:
                logger.warning("Agente: %.0f s y sin terminar; última vuelta, sin tools", self.limites.segundos)
            if sin_tokens:
                logger.warning("Agente: %s tokens y sin terminar; última vuelta, sin tools", uso.total)
            peticion = PeticionLLM(
                sistema=sistema,
                mensajes=tuple(mensajes),
                tools=self.declaraciones,
                usar_tools=not ultima,  # la última: ve las tools (el historial habla de ellas), no puede pedirlas
            )
            r = self.llm.generar_en_streaming(peticion, al_texto) if al_texto else self.llm.generar(peticion)
            self.observador.respuesta(r)
            uso += r.uso
            modelos.append(r.modelo)

            if not r.llamadas:  # ha contestado (o no puede seguir): fin
                forma = None
                if estructurada and r.motivo == MotivoFin.FIN:  # módulo 96: otra llamada, sin tools y con el schema
                    forma, r2 = estructurar(self.llm, (*mensajes, r.mensaje))
                    if r2 is not None:
                        self.observador.respuesta(r2)
                        uso += r2.uso
                        modelos.append(r2.modelo)
                return self._final(r, nuevos, terminar, forma)
            llamadas.extend(r.llamadas)
            if ultima:  # pidió tools aunque no podía: no se ejecutan (quedarían llamadas sin resultado)
                logger.warning("Agente: sin respuesta tras %s iteraciones", iteracion)
                nuevos.append(Mensaje.modelo(texto=SIN_TERMINAR))
                return terminar(SIN_TERMINAR, MotivoParada.LIMITE_ITERACIONES)

            mensajes.append(r.mensaje)
            nuevos.append(r.mensaje)
            # Todas las tool calls del turno, en orden; sus resultados vuelven JUNTOS, cada uno con el id de su llamada
            resultados = []
            for llamada in r.llamadas:
                self.observador.llamada(llamada)
                antes = self.cronometro()
                with self.telemetria.tool(llamada) as medir:
                    resultado, artefacto = self._ejecutar(llamada, contexto, usos_por_tool, ya_llamadas)
                    medir(resultado)
                self.observador.resultado(resultado, int((self.cronometro() - antes) * 1000))
                if artefacto is not None:  # módulo 97: para la interfaz, no para el modelo
                    artefactos.append(artefacto)
                    self.observador.artefacto(artefacto)
                resultados.append(resultado)
            mensaje_tools = Mensaje.de_tools(tuple(resultados))
            mensajes.append(mensaje_tools)
            nuevos.append(mensaje_tools)
        raise AssertionError("inalcanzable: la última iteración siempre termina")  # pragma: no cover

    @staticmethod
    def _final(r, nuevos: list[Mensaje], terminar, forma) -> ResultadoAgente:
        if r.motivo == MotivoFin.BLOQUEADA:
            texto = r.texto or BLOQUEADA
            nuevos.append(Mensaje.modelo(texto=texto))
            return terminar(texto, MotivoParada.BLOQUEADA)
        nuevos.append(r.mensaje)
        if r.motivo == MotivoFin.LIMITE_TOKENS:  # el texto llega a medias: quien llama decide qué enseñar
            return terminar(r.texto, MotivoParada.RESPUESTA_CORTADA)
        return terminar(r.texto, MotivoParada.FIN, forma)

    def _ejecutar(
        self, llamada: LlamadaTool, contexto, usos: Counter, ya_llamadas: set
    ) -> tuple[ResultadoTool, Artefacto | None]:
        def error(texto: str) -> tuple[ResultadoTool, None]:
            contenido = json.dumps({"error": texto}, ensure_ascii=False)
            return ResultadoTool(llamada.id, llamada.nombre, contenido, es_error=True), None

        tool = self.tools.get(llamada.nombre)
        if tool is None:  # pasa: los modelos inventan nombres parecidos. Se le dice cuáles hay
            return error(f"La tool '{llamada.nombre}' no existe. Las que hay: {', '.join(self.tools)}.")
        # La misma tool con los mismos argumentos da el mismo resultado: ya lo tiene en el historial
        firma = (llamada.nombre, _normalizado(llamada.argumentos))
        if firma in ya_llamadas:
            return error(
                f"Ya has llamado a {llamada.nombre} con estos mismos argumentos y el resultado está más arriba. "
                "No repitas la llamada: usa ese resultado o cambia los argumentos."
            )
        if usos[llamada.nombre] >= tool.max_llamadas:
            return error(
                f"Ya has llamado a {llamada.nombre} {tool.max_llamadas} veces en esta pregunta, el máximo. "
                "Contesta con los datos que tienes o usa otra tool."
            )
        try:
            args = tool.validar(llamada.argumentos)
            ya_llamadas.add(firma)
            usos[llamada.nombre] += 1
            contenido = tool.ejecutar(contexto, args)
        except ToolException as e:  # error previsto: el mensaje está escrito para el modelo
            return error(str(e))
        except DominioException as e:  # una regla de la app (un permiso, un dato que no existe): su mensaje es público
            return error(e.mensaje)
        except Exception as e:  # un bug nuestro: al modelo, un mensaje sin detalles internos
            # Al log, la tool, el tipo de error y DÓNDE (las líneas del traceback); ni los argumentos ni el mensaje de
            # la excepción: llevan datos del hogar (un concepto, un importe), y el log lo lee más gente que el chat
            logger.error(
                "Error en la tool %s: %s\n%s", llamada.nombre, type(e).__name__, "".join(format_tb(e.__traceback__))
            )
            return error(f"Error interno en {llamada.nombre}. No la reintentes: explica al usuario que ha fallado.")
        artefacto = None
        if isinstance(contenido, ConArtefacto):  # módulo 97: el modelo lee solo su parte
            contenido, artefacto = contenido.para_el_modelo, contenido.artefacto
        return ResultadoTool(llamada.id, llamada.nombre, self._preparar(contenido)), artefacto

    def _preparar(self, contenido: dict) -> str:
        """A JSON compacto (sin espacios: son tokens) y recortado si se pasa: lo que lee el modelo no pasa nunca de
        max_caracteres_resultado (más el aviso). Es una red de seguridad: las tools ya devuelven poco (módulo 95)."""
        texto = json.dumps(contenido, ensure_ascii=False, separators=(",", ":"), default=str)
        maximo = self.limites.max_caracteres_resultado
        if len(texto) <= maximo:
            return texto
        logger.warning("Resultado de tool recortado: %s caracteres", len(texto))
        aviso = (
            f"Resultado demasiado largo ({len(texto)} caracteres): solo ves el principio. "
            "Si necesitas más, vuelve a llamar con filtros más concretos."
        )
        # El principio va como TEXTO dentro de otro JSON, donde cada " y cada \ se escapan (ocupan dos): se recorta
        # hasta que, ya escapado, cabe. Si no, un resultado lleno de comillas casi doblaría el tamaño
        inicio = texto[:maximo]
        while (sobra := len(json.dumps(inicio, ensure_ascii=False)) - 2 - maximo) > 0:
            inicio = inicio[:-sobra]
        return json.dumps({"recortado": True, "aviso": aviso, "inicio": inicio}, ensure_ascii=False)


def _registrar(r: ResultadoAgente, contexto: ContextoPregunta) -> None:
    """Ejercicio 3: UNA línea de log por pregunta, con todo lo que hace falta para buscarla y para sumar (coste, cuotas,
    tools más usadas). Sin la pregunta ni la respuesta: son datos del hogar (privacidad, módulo 107)."""
    logger.info(
        "Pregunta respondida: %s en %s vueltas y %s ms",
        r.motivo,
        r.iteraciones,
        r.duracion_ms,
        extra={
            "asistente": {
                "usuario_id": contexto.usuario_id,
                "hogar_id": contexto.hogar.id,
                "motivo": str(r.motivo),
                "iteraciones": r.iteraciones,
                "tools": [ll.nombre for ll in r.llamadas],
                "modelos": list(dict.fromkeys(r.modelos)),
                "tokens_entrada": r.uso.entrada,
                "tokens_salida": r.uso.salida,
                "tokens_razonamiento": r.uso.razonamiento,
                "tokens_cache": r.uso.cache,
                "duracion_ms": r.duracion_ms,
                "prompt": VERSION,  # módulo 96: qué versión del prompt contestó (para comparar versiones, módulo 98)
            }
        },
    )


def _normalizado(argumentos: str) -> str:
    """{"a":1,"b":2} y {"b": 2, "a": 1} son la misma llamada."""
    try:
        return json.dumps(json.loads(argumentos), sort_keys=True)
    except ValueError:
        return argumentos
