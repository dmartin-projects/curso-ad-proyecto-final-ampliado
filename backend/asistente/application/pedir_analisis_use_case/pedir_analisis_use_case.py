# asistente/application/pedir_analisis_use_case/pedir_analisis_use_case.py — encargar el análisis (módulo 105)
"""Lo rápido, en la petición: quién, qué hogar, qué mes y si le queda cuota (un análisis gasta como varias preguntas,
módulo 98). Lo lento, en Celery (AnalizarMesUseCase): la respuesta HTTP sale en milisegundos."""

import re

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.cuotas.calcular_cuota import calcular_cuota
from asistente.application.pedir_analisis_use_case.dtos.pedir_analisis_input_dto import PedirAnalisisInputDTO
from asistente.application.pedir_analisis_use_case.i_pedir_analisis_use_case import IPedirAnalisisUseCase
from asistente.application.ports.i_control_de_analisis import IControlDeAnalisis
from asistente.application.ports.i_membresias import IMembresias
from asistente.application.ports.i_programador_de_analisis import IProgramadorDeAnalisis
from asistente.application.ports.i_tarifas import ITarifas
from asistente.domain.exceptions.analisis_en_curso_exception import AnalisisEnCursoException
from asistente.domain.repositories.i_consumo_query_service import IConsumoQueryService
from asistente.domain.repositories.i_plan_del_hogar_repository import IPlanDelHogarRepository
from core.application.ports.i_reloj import IReloj
from core.domain.enums.rol import Rol
from core.domain.exceptions.validacion_exception import ValidacionException
from core.domain.vo.mes import Mes

TAREA = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class PedirAnalisisUseCase(IPedirAnalisisUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(
        self,
        *,
        membresias: IMembresias,
        programador: IProgramadorDeAnalisis,
        planes: IPlanDelHogarRepository,
        tarifas: ITarifas,
        consumos: IConsumoQueryService,
        reloj: IReloj,
        control: IControlDeAnalisis | None = None,  # ejercicio 3: uno a la vez
    ):
        self.membresias, self.programador = membresias, programador
        self.planes, self.tarifas, self.consumos, self.reloj = planes, tarifas, consumos, reloj
        self.control = control

    def ejecutar(self, entrada: PedirAnalisisInputDTO) -> str:
        entrada.actor.exigir(self.rol_minimo)
        if not TAREA.match(entrada.tarea):
            raise ValidacionException("La tarea es un UUID en minúsculas.", campo="tarea")
        contexto = ContextoPregunta.abrir(
            usuario_id=entrada.actor.usuario_id, hogar_id=entrada.hogar_id, membresias=self.membresias, reloj=self.reloj
        )
        mes = Mes.de(contexto.hoy) if entrada.mes is None else _mes(entrada.mes, contexto.hoy)
        cuota = calcular_cuota(
            contexto, self.reloj.ahora(), planes=self.planes, tarifas=self.tarifas, consumos=self.consumos
        )
        cuota.exigir(self.reloj.ahora())
        if self.control is not None and not self.control.empezar(
            entrada.actor.usuario_id, entrada.hogar_id, entrada.tarea
        ):
            raise AnalisisEnCursoException()
        self.programador.programar(entrada.actor.usuario_id, entrada.hogar_id, str(mes), entrada.tarea)
        return str(mes)


def _mes(texto: str, hoy) -> Mes:
    try:
        mes = Mes.desde_texto(texto)
    except ValueError:
        raise ValidacionException("El mes va como AAAA-MM.", campo="mes") from None
    if mes > Mes.de(hoy):
        raise ValidacionException("No se puede analizar un mes que no ha empezado.", campo="mes")
    return mes
