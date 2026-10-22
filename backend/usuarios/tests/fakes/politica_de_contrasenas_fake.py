# usuarios/tests/fakes/politica_de_contrasenas_fake.py — IPoliticaDeContrasenas en memoria (módulos 35 y 88)
from usuarios.application.ports.i_politica_de_contrasenas import IPoliticaDeContrasenas


class PoliticaDeContrasenasFake(IPoliticaDeContrasenas):
    def incumplimientos(self, password, *, usuario_id):
        return [] if len(password) >= 10 else ["Esta contraseña es demasiado corta."]
