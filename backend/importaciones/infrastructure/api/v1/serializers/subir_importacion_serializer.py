# importaciones/infrastructure/api/v1/serializers/subir_importacion_serializer.py (módulos 75 y 88)
from django.conf import settings
from rest_framework import serializers

from core.infrastructure.storage.huella_archivo import huella_archivo
from finanzas.models import Cuenta
from hogares.infrastructure.api.base.del_hogar_mixin import DelHogarMixin
from importaciones.infrastructure.database.models.importacion_model import Importacion as ImportacionModel


class SubirImportacionSerializer(DelHogarMixin, serializers.Serializer):
    campos_del_hogar = {"cuenta": Cuenta}
    archivo = serializers.FileField()
    cuenta = serializers.PrimaryKeyRelatedField(queryset=Cuenta.objects.none())

    def validate_archivo(self, archivo):
        if archivo.size > settings.IMPORTACION_TAMANO_MAXIMO:
            raise serializers.ValidationError("El archivo no puede superar los 5 MB.")
        cabecera = archivo.read(2048)
        archivo.seek(0)
        if cabecera.startswith(b"%PDF-"):
            self.context["formato"] = ImportacionModel.Formato.PDF
        elif b"\x00" in cabecera:  # un CSV es texto: un byte nulo delata un binario (xlsx, imagen…)
            raise serializers.ValidationError("Sube el extracto en CSV o PDF.")
        else:
            self.context["formato"] = ImportacionModel.Formato.CSV
        return archivo

    def validate(self, datos):
        datos["formato"] = self.context.pop("formato")
        datos["huella_archivo"] = huella_archivo(datos["archivo"])
        repetida = (
            ImportacionModel.objects.filter(hogar=self.context["hogar"], huella_archivo=datos["huella_archivo"])
            .exclude(estado__in=[ImportacionModel.Estado.DESHECHA, ImportacionModel.Estado.ERROR])
            .first()
        )
        if repetida:
            raise serializers.ValidationError({"archivo": f"Este extracto ya se importó (importación {repetida.pk})."})
        return datos
