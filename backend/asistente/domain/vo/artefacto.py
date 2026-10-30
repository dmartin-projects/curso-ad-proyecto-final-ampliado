# asistente/domain/vo/artefacto.py — lo que una tool produce para la interfaz, no para el modelo (módulo 97)
from asistente.domain.vo.archivo_exportado import ArchivoExportado
from asistente.domain.vo.ayuda_consultada import AyudaConsultada
from asistente.domain.vo.consulta_sql import ConsultaSQL
from asistente.domain.vo.contenido_retirado import ContenidoRetirado
from asistente.domain.vo.grafico import Grafico
from asistente.domain.vo.propuesta_preparada import PropuestaPreparada
from asistente.domain.vo.recuerdo_guardado import RecuerdoGuardado

# el recuerdo: módulo 99; la ayuda consultada: ejercicios del 100; la consulta SQL: módulo 101; el contenido retirado: 102
Artefacto = (
    Grafico
    | ArchivoExportado
    | PropuestaPreparada
    | RecuerdoGuardado
    | AyudaConsultada
    | ConsultaSQL
    | ContenidoRetirado
)
