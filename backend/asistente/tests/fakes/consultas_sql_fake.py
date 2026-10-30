# asistente/tests/fakes/consultas_sql_fake.py (módulo 101)
from asistente.application.ports.i_consultas_sql import IConsultasSQL
from asistente.domain.read_models.resultado_sql import ResultadoSQL


class ConsultasSQLFake(IConsultasSQL):
    """Devuelve lo que el test le prepare y apunta qué se ejecutó (y con qué hogar)."""

    def __init__(self, resultado: ResultadoSQL | Exception | None = None):
        self.resultado = resultado or ResultadoSQL(("n",), ((1,),), False, 3)
        self.ejecutadas: list[tuple[int, str]] = []

    def disponible(self):
        return True

    def ejecutar(self, hogar_id, sql):
        self.ejecutadas.append((hogar_id, sql))
        if isinstance(self.resultado, Exception):
            raise self.resultado
        return self.resultado
