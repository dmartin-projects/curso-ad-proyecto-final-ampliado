# asistente/infrastructure/finanzas/exportador_en_finanzas.py — IExportadorDeMovimientos con finanzas (módulo 97)
#
# El CSV es el mismo que el de la pantalla de movimientos (módulo 73): punto y coma, coma decimal, las mismas columnas
# y el texto sin fórmulas (CSV injection) con la misma función de core.
# Las filas salen del use case de CONSULTA de finanzas con el Actor de quien pregunta; el archivo va al almacén.
import csv
import io

from asistente.application.ports.i_almacen_de_archivos import IAlmacenDeArchivos
from asistente.application.ports.i_exportador_de_movimientos import IExportadorDeMovimientos
from asistente.domain.vo.archivo_exportado import ArchivoExportado
from core.infrastructure.hojas_de_calculo.celdas_de_texto import texto_csv
from finanzas.application.exportar_movimientos_use_case.dtos.exportar_movimientos_input_dto import (
    ExportarMovimientosInputDTO,
)
from finanzas.domain.repositories.queries.filtros_movimientos_query import FiltrosMovimientosQuery
from finanzas.infrastructure import container as finanzas

MAX_FILAS = 20_000  # un CSV de chat no es una copia de seguridad: para eso, la pantalla de movimientos


class ExportadorEnFinanzas(IExportadorDeMovimientos):
    def __init__(self, *, almacen: IAlmacenDeArchivos):
        self.almacen = almacen

    def exportar(self, actor, hogar_id, filtro, nombre):
        filtros = FiltrosMovimientosQuery(
            fecha_desde=filtro.desde,
            fecha_hasta=filtro.hasta,
            categorias=(filtro.categoria_id,) if filtro.categoria_id is not None else (),
            tipo=filtro.tipo,
            busqueda=tuple(filtro.texto.split()) if filtro.texto else (),
        )
        filas = finanzas.exportar_movimientos().ejecutar(ExportarMovimientosInputDTO(hogar_id, actor, filtros))
        salida = io.StringIO()
        escritor = csv.writer(salida, delimiter=";")
        escritor.writerow(["fecha", "concepto", "importe", "cuenta", "categoría", "etiquetas"])
        n = 0
        for n, f in enumerate(filas, start=1):
            if n > MAX_FILAS:
                n = MAX_FILAS
                break
            escritor.writerow(
                [
                    f.fecha,
                    texto_csv(f.concepto),
                    str(f.importe).replace(".", ","),  # el importe, tal cual: "-12,50" es un número
                    texto_csv(f.cuenta),
                    texto_csv(f.categoria or ""),
                    texto_csv(",".join(f.etiquetas)),
                ]
            )
        if not n:
            return ArchivoExportado(nombre, "", 0)
        ruta = self.almacen.guardar(f"asistente/{hogar_id}/exportaciones", salida.getvalue().encode("utf-8-sig"))
        return ArchivoExportado(nombre, ruta, n)
