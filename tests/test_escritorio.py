"""Tests del arranque del ejecutable de escritorio."""

import socket

import pytest

from escritorio import puerto_libre


class TestPuertoLibre:
    def test_usa_el_puerto_preferido_si_esta_libre(self):
        # Se toma un puerto efimero libre y se suelta: al pedirlo, deberia
        # devolver ese mismo numero sin desplazarse al siguiente.
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            libre = s.getsockname()[1]

        assert puerto_libre(desde=libre) == libre

    def test_se_corre_al_siguiente_si_el_preferido_esta_ocupado(self):
        with socket.socket() as ocupado:
            ocupado.bind(("127.0.0.1", 0))
            ocupado.listen()
            puerto = ocupado.getsockname()[1]

            elegido = puerto_libre(desde=puerto)

        assert elegido > puerto

    def test_falla_con_mensaje_claro_si_no_hay_ninguno(self, monkeypatch):
        import escritorio

        monkeypatch.setattr(escritorio, "PUERTOS_A_PROBAR", 1)
        with socket.socket() as ocupado:
            ocupado.bind(("127.0.0.1", 0))
            ocupado.listen()
            puerto = ocupado.getsockname()[1]

            with pytest.raises(SystemExit, match="No encontre un puerto libre"):
                puerto_libre(desde=puerto)
