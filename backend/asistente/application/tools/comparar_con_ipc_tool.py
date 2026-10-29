# asistente/application/tools/comparar_con_ipc_tool.py — ¿gastamos más, o es que todo está más caro? (módulo 95)
from datetime import timedelta
from decimal import Decimal

from pydantic import Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.ports.i_indice_de_precios import IIndiceDePrecios
from asistente.application.tools.categoria_por_nombre import NOMBRE_DE_CATEGORIA, categoria_por_nombre
from asistente.application.tools.formato import euros, pct
from asistente.application.tools.mes_del_contexto import MesOpcional
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.services.grupos_ecoicop import grupo_de
from asistente.domain.vo.filtro_de_movimientos import FiltroDeMovimientos
from core.domain.vo.mes import Mes


class CompararConIpcArgumentos(SinArgumentos):
    categoria: str = NOMBRE_DE_CATEGORIA
    # El tipo y la validación de MesOpcional; la descripción, propia: aquí, sin mes, el último CERRADO
    mes: MesOpcional = Field(None, description="AAAA-MM, un mes ya terminado. Si no lo envías: el último cerrado.")


class CompararConIpcTool(Tool):
    nombre = "comparar_con_ipc"
    descripcion = (
        "Compara cuánto ha cambiado el gasto del hogar en una categoría frente al mismo mes del año anterior con la "
        "inflación oficial (IPC armonizado de España, Eurostat) de ese tipo de gasto. Sin mes: el último cerrado."
    )
    Argumentos = CompararConIpcArgumentos
    max_llamadas = 3  # sale a Internet y es lento

    def __init__(self, *, finanzas: IConsultasDeFinanzas, precios: IIndiceDePrecios):
        self.finanzas, self.precios = finanzas, precios

    def ejecutar(self, contexto: ContextoPregunta, args: CompararConIpcArgumentos) -> dict:
        categoria = categoria_por_nombre(self.finanzas, contexto, args.categoria)
        mes = Mes.desde_texto(args.mes) if args.mes else Mes.de(contexto.hoy).anterior()
        if mes.contiene(contexto.hoy) or mes > Mes.de(contexto.hoy):
            raise ToolException(
                f"{mes} no ha terminado: compara un mes cerrado (hasta {Mes.de(contexto.hoy).anterior()})."
            )
        grupo = grupo_de(categoria.nombre, categoria.padre)
        resultado = {"categoria": categoria.nombre, "mes": str(mes), "grupo_ipc": grupo.nombre}
        if not grupo.exacto:
            resultado["nota_grupo"] = "Esta categoría no tiene un grupo propio en el IPC: se compara con el general."

        este, hace_un_anio = (self._gasto(contexto, categoria.id, m) for m in (mes, Mes(mes.anio - 1, mes.numero)))
        resultado["gasto_hogar"] = euros(este)
        if hace_un_anio:
            resultado["gasto_hogar_un_anio_antes"] = euros(hace_un_anio)
            resultado["variacion_hogar_pct"] = pct((este - hace_un_anio) * 100 / hace_un_anio)
        else:
            resultado["variacion_hogar_pct"] = None
            resultado["nota_hogar"] = (
                f"No hay gastos de esta categoría en {Mes(mes.anio - 1, mes.numero)}: no se puede comparar."
            )

        try:
            serie = self.precios.serie(grupo.codigo)
        except ServicioExternoNoDisponibleException as e:
            raise ToolException(
                "El servicio de Eurostat no responde ahora. No des una cifra de inflación de memoria: dile al usuario "
                "que no puedes compararlo en este momento."
            ) from e
        if mes in serie.tasas_anuales:
            resultado["ipc_variacion_anual_pct"] = pct(serie.tasas_anuales[mes])
        else:  # publicado con retraso: decirlo, no inventarlo
            ultimo = serie.ultimo_publicado
            resultado["ipc_variacion_anual_pct"] = None
            resultado["nota_ipc"] = (
                f"El IPC de {mes} todavía no está publicado (el último es {ultimo})."
                if ultimo
                else "Sin datos del IPC."
            )
        return resultado

    def _gasto(self, contexto, categoria_id: int, mes: Mes) -> Decimal:
        filtro = FiltroDeMovimientos(mes.inicio, mes.fin - timedelta(days=1), categoria_id=categoria_id)
        return self.finanzas.movimientos(contexto.actor, contexto.hogar.id, filtro, limite=0).gastos
