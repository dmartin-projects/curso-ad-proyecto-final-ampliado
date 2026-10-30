# asistente/tests/fakes/almacen_de_archivos_fake.py — IAlmacenDeArchivos en memoria (módulo 97)
from asistente.application.ports.i_almacen_de_archivos import IAlmacenDeArchivos


class AlmacenDeArchivosFake(IAlmacenDeArchivos):
    def __init__(self):
        self.archivos: dict[str, bytes] = {}

    def guardar(self, carpeta, contenido):
        ruta = f"{carpeta}/archivo-{len(self.archivos) + 1}"
        self.archivos[ruta] = contenido
        return ruta

    def url(self, ruta):
        return f"https://almacen.example/{ruta}?firma=fake"

    def borrar(self, ruta):
        self.archivos.pop(ruta, None)
