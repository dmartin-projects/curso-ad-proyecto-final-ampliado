# hogares/infrastructure/database/repositories/membresia_command_repository_orm.py — IMembresiaCommandRepository con el ORM (módulo 88)
from core.domain.enums.rol import Rol
from core.infrastructure.database.guardado import guardar_fila
from core.infrastructure.signals.red_de_seguridad import publicados_por_caso_de_uso
from hogares.domain.bo.membresia import Membresia
from hogares.domain.exceptions.miembro_no_encontrado_exception import MiembroNoEncontradoException
from hogares.domain.exceptions.ya_es_miembro_exception import YaEsMiembroException
from hogares.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository
from hogares.infrastructure.database.mappers.membresia_mapper import membresia_a_bo, membresia_a_modelo
from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel

CAMPOS = ["rol"]  # en un UPDATE solo cambia el rol


class MembresiaCommandRepositoryORM(IMembresiaCommandRepository):
    errores = {"membresia_unica": YaEsMiembroException}

    def obtener(self, hogar_id, membresia_id, *, bloquear=False):
        consulta = MembresiaModel.objects.filter(hogar_id=hogar_id, pk=membresia_id)
        fila = (consulta.select_for_update() if bloquear else consulta).first()
        if fila is None:
            raise MiembroNoEncontradoException()
        return membresia_a_bo(fila)

    def admins(self, hogar_id: int) -> int:
        # FOR UPDATE de los administradores (como el módulo 71): dos peticiones a la vez no pueden quitar cada una a
        # uno de los dos últimos. (list(): PostgreSQL no admite FOR UPDATE con COUNT)
        return len(
            list(MembresiaModel.objects.select_for_update().filter(hogar_id=hogar_id, rol=Rol.ADMIN).values("pk"))
        )

    def es_miembro(self, hogar_id, *, usuario_id=None, email=None):
        filtro = {"usuario_id": usuario_id} if usuario_id is not None else {"usuario__email__iexact": email}
        return MembresiaModel.objects.filter(hogar_id=hogar_id, **filtro).exists()

    def guardar(self, membresia: Membresia) -> None:
        # marcada: sus eventos los publica el use case (la alarma la deja pasar). membresia_unica: YaEsMiembro, con
        # un savepoint (guardar_fila), como los repositorios de finanzas
        fila = publicados_por_caso_de_uso(membresia_a_modelo(membresia))
        guardar_fila(fila, CAMPOS, self.errores)
        membresia.id = fila.pk

    def eliminar(self, membresia: Membresia) -> None:
        publicados_por_caso_de_uso(
            MembresiaModel(pk=membresia.id, hogar_id=membresia.hogar_id, usuario_id=membresia.usuario_id)
        ).delete()
