"""Tests de la resolucion de la raiz de la app (fuente vs. empaquetada)."""

import sys
from pathlib import Path

from contratos.rutas import raiz_app


class TestRaizApp:
    def test_modo_fuente_devuelve_la_carpeta_del_proyecto(self):
        raiz = raiz_app()
        assert (raiz / "src" / "contratos").is_dir()
        assert (raiz / "web").is_dir()

    def test_modo_empaquetado_devuelve_la_carpeta_del_ejecutable(self, monkeypatch, tmp_path):
        exe_falso = tmp_path / "GeneradorContratos.exe"
        exe_falso.touch()
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "executable", str(exe_falso))

        assert raiz_app() == tmp_path

    def test_sin_frozen_ignora_sys_executable(self, monkeypatch):
        # sys.executable siempre existe (apunta al interprete de Python) pero
        # sin sys.frozen no debe usarse para calcular la raiz.
        monkeypatch.delattr(sys, "frozen", raising=False)
        raiz = raiz_app()
        assert raiz != Path(sys.executable).resolve().parent
