# usuarios/infrastructure/api/v1/serializers/proveedores_sociales_serializer.py (módulo 91)
from rest_framework import serializers

from usuarios.infrastructure.api.v1.serializers.proveedor_social_serializer import ProveedorSocialSerializer


class ProveedoresSocialesSerializer(serializers.Serializer):
    # El dominio de la app: la SPA solo ofrece los botones si está en él (una preview de Vercel tiene otro origen,
    # y su vuelta no está registrada en ningún proveedor)
    origen = serializers.URLField()
    proveedores = ProveedorSocialSerializer(many=True)
