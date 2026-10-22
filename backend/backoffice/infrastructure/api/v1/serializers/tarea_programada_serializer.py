# backoffice/infrastructure/api/v1/serializers/tarea_programada_serializer.py (módulos 79 y 88)
from django_celery_beat.models import PeriodicTask
from rest_framework import serializers


class TareaProgramadaSerializer(serializers.ModelSerializer):
    horario = serializers.CharField(source="crontab", read_only=True, default=None, allow_null=True)

    class Meta:
        model = PeriodicTask
        fields = ["id", "name", "task", "horario", "enabled", "last_run_at", "total_run_count"]
        read_only_fields = ["id", "name", "task", "horario", "last_run_at", "total_run_count"]
