# asistente/domain/vo/artefacto.py — lo que una tool produce para la interfaz, no para el modelo (módulo 97)
from asistente.domain.vo.archivo_exportado import ArchivoExportado
from asistente.domain.vo.grafico import Grafico
from asistente.domain.vo.propuesta_preparada import PropuestaPreparada

Artefacto = Grafico | ArchivoExportado | PropuestaPreparada
