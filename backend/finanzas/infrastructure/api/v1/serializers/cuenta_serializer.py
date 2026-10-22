# finanzas/infrastructure/api/v1/serializers/cuenta_serializer.py (módulos 33 y 87)
from rest_framework import serializers

from finanzas.infrastructure.database.models.cuenta_model import Cuenta as CuentaModel


# Cuentas: CRUD sin reglas de negocio, sin use cases (módulo 87, "cuándo NO merece la pena")
class CuentaSerializer(serializers.ModelSerializer):
    saldo = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = CuentaModel
        fields = ["id", "nombre", "tipo", "iban", "activa", "saldo"]

    def validate_nombre(self, nombre: str) -> str:
        # La UniqueConstraint (hogar, nombre) no la ve DRF (el hogar no es un campo del serializer): sin esto, un
        # nombre repetido llegaría a la base de datos y sería un IntegrityError (500), no un error del campo
        otras = CuentaModel.objects.filter(hogar=self.context.get("hogar"), nombre=nombre)
        if self.instance is not None:
            otras = otras.exclude(pk=self.instance.pk)
        if otras.exists():
            raise serializers.ValidationError("Ya hay una cuenta con ese nombre.")
        return nombre
