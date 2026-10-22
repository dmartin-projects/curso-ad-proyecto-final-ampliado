# notificaciones/tests/fakes/destinatarios_fake.py — IDestinatarios en memoria (módulo 88)
from notificaciones.application.ports.i_destinatarios import IDestinatarios


class DestinatariosFake(IDestinatarios):
    def __init__(self, idiomas: dict[int, str], miembros: dict[int, list[int]]):
        self._idiomas, self._miembros = idiomas, miembros  # {usuario: idioma}, {hogar: [usuarios activos]}

    def idiomas(self, usuario_ids):
        return {u: self._idiomas[u] for u in sorted(set(usuario_ids)) if u in self._idiomas}

    def miembros_activos(self, hogar_id):
        return list(self._miembros.get(hogar_id, []))

    def hogares(self, usuario_id):
        return [h for h, usuarios in self._miembros.items() if usuario_id in usuarios]
