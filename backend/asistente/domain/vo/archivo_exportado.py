# asistente/domain/vo/archivo_exportado.py — un archivo que el asistente ha preparado para descargar (módulo 97)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ArchivoExportado:
    nombre: str  # el que verá la persona al descargarlo: "movimientos-2026-09.csv"
    ruta: str  # dónde está en el almacenamiento (S3/R2, o el disco en desarrollo): la URL firmada se pide al leerlo
    filas: int
