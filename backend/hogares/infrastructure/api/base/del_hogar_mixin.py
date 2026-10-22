# hogares/infrastructure/api/base/del_hogar_mixin.py — los campos relacionados, limitados al hogar de la URL (módulos 33 y 88)
class DelHogarMixin:
    """Limita los campos relacionados al hogar de la URL: no se puede apuntar a datos de otro hogar (módulo 33)."""

    campos_del_hogar: dict[str, type] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hogar = self.context.get("hogar")
        for campo, modelo in self.campos_del_hogar.items():
            if campo in self.fields and hogar is not None:
                self.fields[campo].queryset = modelo.objects.filter(hogar=hogar)
