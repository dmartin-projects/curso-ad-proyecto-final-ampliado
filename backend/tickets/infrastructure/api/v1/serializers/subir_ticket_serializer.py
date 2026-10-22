# tickets/infrastructure/api/v1/serializers/subir_ticket_serializer.py (módulos 74 y 88)
from django.conf import settings
from PIL import Image, UnidentifiedImageError
from rest_framework import serializers

from core.infrastructure.storage.huella_archivo import huella_archivo
from finanzas.models import Cuenta
from hogares.infrastructure.api.base.del_hogar_mixin import DelHogarMixin
from tickets.infrastructure.database.models.ticket_model import Ticket as TicketModel

# Firmas ("magic bytes"): el tipo real lo dice el contenido, no la extensión ni el Content-Type del cliente
FIRMAS = {
    b"%PDF-": "application/pdf",
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
}


def detectar_tipo(archivo) -> str | None:
    cabecera = archivo.read(16)
    archivo.seek(0)
    if cabecera[:4] == b"RIFF" and cabecera[8:12] == b"WEBP":
        return "image/webp"
    return next((tipo for firma, tipo in FIRMAS.items() if cabecera.startswith(firma)), None)


class SubirTicketSerializer(DelHogarMixin, serializers.Serializer):
    campos_del_hogar = {"cuenta": Cuenta}
    archivo = serializers.FileField()
    cuenta = serializers.PrimaryKeyRelatedField(queryset=Cuenta.objects.none())

    def validate_archivo(self, archivo):
        if archivo.size > settings.TICKETS_TAMANO_MAXIMO:
            raise serializers.ValidationError("El archivo no puede superar los 10 MB.")
        tipo = detectar_tipo(archivo)
        if tipo is None:
            raise serializers.ValidationError("Sube una foto (JPEG, PNG o WebP) o un PDF.")
        if tipo.startswith("image/"):
            try:
                with Image.open(archivo) as imagen:
                    imagen.verify()  # detecta imágenes truncadas o corruptas sin decodificarlas enteras
            except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as e:
                raise serializers.ValidationError("La imagen está dañada.") from e
            finally:
                archivo.seek(0)
        self.context["tipo"] = tipo
        return archivo

    def validate(self, datos):
        datos["tipo"] = self.context.pop("tipo")
        datos["huella_archivo"] = huella_archivo(datos["archivo"])
        repetido = TicketModel.objects.filter(
            hogar=self.context["hogar"], huella_archivo=datos["huella_archivo"]
        ).first()
        if repetido:
            raise serializers.ValidationError({"archivo": f"Este ticket ya se subió (ticket {repetido.pk})."})
        return datos
