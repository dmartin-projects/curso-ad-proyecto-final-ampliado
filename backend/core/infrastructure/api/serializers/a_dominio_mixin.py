# core/infrastructure/api/serializers/a_dominio_mixin.py — del serializer al InputDTO del use case (módulo 87)


class ADominioMixin:
    """`a_dominio()`: los datos validados con los nombres y tipos del InputDTO (sin el hogar ni el actor, que los
    pone la view). Las relaciones viajan como ids: el dominio no conoce los modelos de Django."""

    relaciones: dict[str, str] = {}  # campo del serializer → campo del InputDTO: {"cuenta": "cuenta_id"}

    def a_dominio(self) -> dict:
        return {
            self.relaciones.get(campo, campo): getattr(valor, "pk", valor) if campo in self.relaciones else valor
            for campo, valor in self.validated_data.items()
        }
