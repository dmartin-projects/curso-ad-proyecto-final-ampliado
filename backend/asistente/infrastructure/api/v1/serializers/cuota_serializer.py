# asistente/infrastructure/api/v1/serializers/cuota_serializer.py (módulo 98)
from rest_framework import serializers


class CuotaSerializer(serializers.Serializer):
    plan = serializers.CharField()
    tokens_hoy = serializers.IntegerField(help_text="Los de quien pide, hoy (en el día del hogar)")
    tokens_dia = serializers.IntegerField(help_text="Los que permite su plan al día, por persona")
    coste_mes = serializers.DecimalField(max_digits=12, decimal_places=6, help_text="USD del hogar este mes")
    coste_mes_maximo = serializers.DecimalField(max_digits=12, decimal_places=6)
    agotada = serializers.BooleanField()
    agotada_por = serializers.ChoiceField(choices=["", "persona", "hogar"], help_text="Qué cuota se ha agotado")
    renueva = serializers.DateTimeField(help_text="Cuándo vuelve a haber cuota (si está agotada) o empieza mañana")
