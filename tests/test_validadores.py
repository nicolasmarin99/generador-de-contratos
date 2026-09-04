"""Tests del validador de RUT.

Un test es codigo que ejecuta tu codigo y afirma que el resultado es el
esperado. Su valor real aparece cuando refactorizas: si rompes algo sin
darte cuenta, el test te avisa en segundos.

Ejecutar con:  pytest
"""

import pytest

from contratos.validadores import (
    RutInvalido,
    digito_verificador,
    limpiar_rut,
    validar_rut,
)


class TestDigitoVerificador:
    def test_rut_del_cliente(self):
        assert digito_verificador("77981536") == "6"

    def test_rut_de_volvo(self):
        assert digito_verificador("76284920") == "8"

    def test_verificador_puede_ser_k(self):
        # Cuando 11 - (suma % 11) da 10, el verificador se escribe como K
        assert digito_verificador("5000001") == "K"

    def test_verificador_puede_ser_cero(self):
        assert digito_verificador("12345675") == "0"


class TestLimpiarRut:
    @pytest.mark.parametrize(
        "entrada",
        ["77.981.536-6", "77981536-6", "77.981.5366", "  77981536 6  "],
    )
    def test_acepta_cualquier_formato(self, entrada):
        assert limpiar_rut(entrada) == "77981536-6"

    def test_rechaza_entradas_demasiado_cortas(self):
        with pytest.raises(RutInvalido):
            limpiar_rut("7")


class TestValidarRut:
    def test_devuelve_el_rut_formateado(self):
        assert validar_rut("77981536-6") == "77.981.536-6"

    def test_rechaza_verificador_incorrecto(self):
        with pytest.raises(RutInvalido, match="deberia ser 6"):
            validar_rut("77.981.536-9")

    def test_es_idempotente(self):
        # Validar dos veces no deberia cambiar el resultado
        una_vez = validar_rut("77981536-6")
        assert validar_rut(una_vez) == una_vez
