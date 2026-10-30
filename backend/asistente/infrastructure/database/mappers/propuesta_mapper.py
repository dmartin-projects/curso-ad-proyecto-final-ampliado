# asistente/infrastructure/database/mappers/propuesta_mapper.py (módulo 97)
from asistente.domain.bo.propuesta import Propuesta
from asistente.domain.enums.estado_propuesta import EstadoPropuesta
from asistente.domain.enums.tipo_propuesta import TipoPropuesta
from asistente.infrastructure.database.models.propuesta_model import Propuesta as PropuestaModel


def propuesta_a_bo(fila: PropuestaModel) -> Propuesta:
    return Propuesta(
        conversacion_id=fila.conversacion_id,
        usuario_id=fila.usuario_id,
        hogar_id=fila.hogar_id,
        tipo=TipoPropuesta(fila.tipo),
        resumen=fila.resumen,
        datos=fila.datos,
        creada=fila.creado,
        estado=EstadoPropuesta(fila.estado),
        resultado=fila.resultado,
        id=fila.pk,
    )
