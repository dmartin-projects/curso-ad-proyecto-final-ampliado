# asistente/infrastructure/storage/almacen_django.py — IAlmacenDeArchivos con el almacenamiento de Django (módulo 97)
#
# El de toda la app (módulos 20 y 67): S3/R2 en producción, con URLs firmadas que caducan; el disco en desarrollo y E2E.
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from asistente.application.ports.i_almacen_de_archivos import IAlmacenDeArchivos


class AlmacenDjango(IAlmacenDeArchivos):
    def guardar(self, carpeta, contenido):
        # Un nombre nuevo, nunca el del cliente (módulo 20): ni rutas con "../" ni nombres que pisen otros
        return default_storage.save(f"{carpeta}/{uuid.uuid4().hex}", ContentFile(contenido))

    def url(self, ruta):
        return default_storage.url(ruta)

    def borrar(self, ruta):
        default_storage.delete(ruta)  # en S3 y en disco, sin error si ya no está
