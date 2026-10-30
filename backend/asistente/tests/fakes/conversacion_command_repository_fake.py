# asistente/tests/fakes/conversacion_command_repository_fake.py (módulos 97 y 99)
from asistente.domain.exceptions.conversacion_no_encontrada_exception import ConversacionNoEncontradaException
from asistente.domain.repositories.i_conversacion_command_repository import IConversacionCommandRepository
from asistente.domain.services.intercambios import emparejar as _emparejar
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia


class ConversacionCommandRepositoryFake(AlmacenEnMemoria, IConversacionCommandRepository):
    def __init__(self):
        super().__init__()
        self.mensajes: list[
            dict
        ] = []  # {"id", "conversacion_id", "mdc" (MensajeDeConversacion), "incompleto", "motivo"}
        self.guardadas = 0
        self.actualizadas: dict = {}  # módulo 107: id → cuándo se tocó por última vez (para antiguas)

    def obtener(self, usuario_id, hogar_id, conversacion_id):
        c = self._datos.get(conversacion_id)
        if c is None or (c.usuario_id, c.hogar_id) != (usuario_id, hogar_id):
            raise ConversacionNoEncontradaException()
        return copia(c)

    def guardar(self, conversacion):
        self._asignar_id(conversacion)
        self._datos[conversacion.id] = copia(conversacion)
        self.guardadas += 1

    def antiguas(self, antes_de, limite):  # módulo 107: `actualizadas` lo rellena el test
        viejas = sorted((t, i) for i, t in self.actualizadas.items() if t < antes_de and i in self._datos)
        return tuple(copia(self._datos[i]) for _, i in viejas[:limite])

    def archivos(self, conversacion_id):
        rutas = []
        for m in self.mensajes:
            if m["conversacion_id"] == conversacion_id:
                mdc = m["mdc"]
                rutas += [mdc.adjunto] if mdc.adjunto else []
                rutas += [a["ruta"] for a in mdc.datos.get("archivos", []) if a.get("ruta")]
                rutas += m.get("exportados", [])
        return tuple(dict.fromkeys(rutas))

    def ligar_archivo(self, mensaje_id, ruta):
        self.mensajes[mensaje_id - 1].setdefault("exportados", []).append(ruta)

    def eliminar(self, conversacion):
        self._datos.pop(conversacion.id, None)
        self.mensajes = [m for m in self.mensajes if m["conversacion_id"] != conversacion.id]

    def guardar_resumen(self, conversacion):
        guardada = self._datos[conversacion.id]
        guardada.resumen, guardada.resumido_hasta = conversacion.resumen, conversacion.resumido_hasta

    def historial(self, conversacion_id, despues_de=None):
        return tuple(m["mdc"].mensaje for m in self._de(conversacion_id, despues_de) if not m["incompleto"])

    def intercambios(self, conversacion_id, despues_de=None):
        visibles = [m for m in self._de(conversacion_id, despues_de) if m["mdc"].visible and not m["incompleto"]]
        return _emparejar([(m["id"], str(m["mdc"].mensaje.rol), m["mdc"].texto) for m in visibles])

    def _de(self, conversacion_id, despues_de):
        return [m for m in self.mensajes if m["conversacion_id"] == conversacion_id and m["id"] > (despues_de or 0)]

    def anadir(self, conversacion_id, mensajes):
        ids = []
        for m in mensajes:
            ids.append(len(self.mensajes) + 1)
            self.mensajes.append({"id": ids[-1], "conversacion_id": conversacion_id, "mdc": m, "incompleto": False})
        return ids

    def marcar_incompleto(self, mensaje_id, motivo):
        m = self.mensajes[mensaje_id - 1]
        m["incompleto"], m["motivo"] = True, motivo

    def visibles(self, conversacion_id) -> list:
        """Para los tests: los MensajeDeConversacion visibles, en orden."""
        return [m["mdc"] for m in self.mensajes if m["conversacion_id"] == conversacion_id and m["mdc"].visible]
