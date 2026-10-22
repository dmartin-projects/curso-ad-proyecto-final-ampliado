# finanzas/management/commands/recategorizar.py — ejercicio 2 del módulo 87: otro adapter de entrada
#
# manage.py recategorizar --hogar 3 --usuario ana@example.com --concepto MERCADONA --categoria Supermercado
#
# El MISMO use case que POST /movimientos/recategorizar/, sin DRF: la autorización (rol en el hogar), la
# transacción, los eventos del outbox y el aviso al dashboard llegan solos, porque son del use case.
from django.core.management.base import BaseCommand, CommandError

from core.domain.enums.rol import Rol
from core.domain.exceptions.dominio_exception import DominioException
from core.domain.vo.actor import Actor
from finanzas.application.recategorizar_movimientos_use_case.dtos.recategorizar_movimientos_input_dto import (
    RecategorizarMovimientosInputDTO,
)
from finanzas.infrastructure import container
from finanzas.models import Categoria, Movimiento
from hogares.models import Membresia


class Command(BaseCommand):
    help = "Pone una categoría a los movimientos de un hogar cuyo concepto contiene un texto."

    def add_arguments(self, parser):
        parser.add_argument("--hogar", type=int, required=True)
        parser.add_argument("--usuario", required=True, help="email de quien lo hace (con su rol en el hogar)")
        parser.add_argument("--concepto", required=True)
        parser.add_argument("--categoria", required=True, help="nombre de la categoría")

    def handle(self, *args, hogar, usuario, concepto, categoria, **opciones):
        membresia = Membresia.objects.filter(hogar_id=hogar, usuario__email__iexact=usuario).first()
        if membresia is None:
            raise CommandError(f"{usuario} no es miembro del hogar {hogar}")
        destino = Categoria.objects.filter(hogar_id=hogar, nombre__iexact=categoria).first()
        if destino is None:
            raise CommandError(f"No hay ninguna categoría «{categoria}» en el hogar {hogar}")
        ids = Movimiento.objects.filter(hogar_id=hogar, concepto__icontains=concepto).values_list("pk", flat=True)
        entrada = RecategorizarMovimientosInputDTO(
            hogar_id=hogar,
            actor=Actor(usuario_id=membresia.usuario_id, rol=Rol(membresia.rol)),
            ids=tuple(ids),
            categoria_id=destino.pk,
        )
        try:
            n = container.recategorizar_movimientos().ejecutar(entrada)
        except DominioException as e:  # el adapter traduce los errores a SU idioma: aquí, un CommandError
            raise CommandError(str(e.mensaje)) from e
        self.stdout.write(self.style.SUCCESS(f"{n} movimientos pasan a «{destino.nombre}»"))
