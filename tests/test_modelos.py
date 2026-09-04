"""Tests de los modelos de datos."""

from datetime import date

import pytest
from pydantic import ValidationError

from contratos.modelos import Cliente, ContratoImpactOnline, ContratoTechTool

DATOS_CLIENTE = {
    "razon_social": "Gran Américas Santiago Chile S.A.",
    "rut": "77981536-6",
    "direccion": "Eliodoro Yáñez N° 2972, oficina 311, Providencia, Santiago",
    "contacto": "Katherine Casas",
    "representante_legal": "Claudio Castillo Castillo",
}


class TestCliente:
    def test_normaliza_el_rut_al_construirse(self):
        cliente = Cliente(**DATOS_CLIENTE)
        assert cliente.rut == "77.981.536-6"

    def test_falla_temprano_con_rut_invalido(self):
        # Ojo: 11.111.111-1 SI es valido. Un digito equivocado se ve asi:
        datos = DATOS_CLIENTE | {"rut": "77981536-9"}
        with pytest.raises(ValidationError):
            Cliente(**datos)

    def test_exige_los_campos_obligatorios(self):
        with pytest.raises(ValidationError):
            Cliente(razon_social="ACME")


class TestContratos:
    def test_impact_expone_sus_campos_propios(self):
        contrato = ContratoImpactOnline(
            cliente=Cliente(**DATOS_CLIENTE),
            fecha=date(2026, 7, 22),
            cliente_id="CL099033",
        )
        contexto = contrato.contexto()
        assert contexto["cliente_id"] == "CL099033"
        assert contexto["fecha"] == "22-07-2026"
        assert contexto["rut_sublicenciante"] == "76.284.920-8"

    def test_techtool_expone_sus_campos_propios(self):
        contrato = ContratoTechTool(
            cliente=Cliente(**DATOS_CLIENTE),
            fecha=date(2026, 7, 22),
            partner_id="CL099022",
        )
        contexto = contrato.contexto()
        assert contexto["partner_id"] == "CL099022"
        assert contexto["cantidad_licencias"] == 1

    def test_el_mismo_cliente_sirve_para_ambos_contratos(self):
        """Esta es la razon de ser del modelo: un solo registro de cliente."""
        cliente = Cliente(**DATOS_CLIENTE)
        impact = ContratoImpactOnline(
            cliente=cliente, fecha=date(2026, 7, 22), cliente_id="CL099033"
        )
        techtool = ContratoTechTool(
            cliente=cliente, fecha=date(2026, 7, 22), partner_id="CL099022"
        )
        assert impact.contexto()["rut_cliente"] == techtool.contexto()["rut_cliente"]

    def test_rechaza_cantidad_de_licencias_invalida(self):
        with pytest.raises(ValidationError):
            ContratoTechTool(
                cliente=Cliente(**DATOS_CLIENTE),
                fecha=date(2026, 7, 22),
                partner_id="CL099022",
                cantidad_licencias=0,
            )
