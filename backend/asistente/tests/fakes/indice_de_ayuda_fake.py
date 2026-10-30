# asistente/tests/fakes/indice_de_ayuda_fake.py (módulo 100)
from asistente.domain.read_models.pasaje_encontrado import PasajeEncontrado
from asistente.domain.repositories.i_indice_de_ayuda import IIndiceDeAyuda
from asistente.domain.services.normalizar import sin_tildes


class IndiceDeAyudaFake(IIndiceDeAyuda):
    """En memoria. Por texto: cuántas palabras de la consulta tiene; por vector: el producto escalar."""

    def __init__(self):
        self.trozos: dict = {}  # clave: (trozo, vector, modelo)

    def huellas(self):
        return {c: (t.huella, m) for c, (t, _, m) in self.trozos.items()}

    def guardar(self, trozos, vectores, modelo):
        for n, t in enumerate(trozos):
            self.trozos[t.clave] = (t, vectores[n] if vectores else None, modelo if vectores else "")

    def borrar(self, claves):
        for c in claves:
            self.trozos.pop(c, None)

    def buscar_por_texto(self, consulta, limite):
        palabras = set(sin_tildes(consulta).split())
        puntos = [(len(palabras & set(sin_tildes(t.para_indexar).split())), t) for t, _, _ in self.trozos.values()]
        mejores = sorted([x for x in puntos if x[0]], key=lambda x: (-x[0], x[1].clave))[:limite]
        return [_pasaje(t, p) for p, t in mejores]

    def buscar_por_vector(self, vector, modelo, limite):
        puntos = [
            (sum(a * b for a, b in zip(v, vector, strict=True)), t)
            for t, v, m in self.trozos.values()
            if v is not None and m == modelo
        ]
        return [_pasaje(t, p) for p, t in sorted(puntos, key=lambda x: (-x[0], x[1].clave))[:limite]]


def _pasaje(t, puntos) -> PasajeEncontrado:
    return PasajeEncontrado(t.clave, t.fuente, t.titulo, t.texto, float(puntos))
