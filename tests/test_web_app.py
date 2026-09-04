"""Tests de integracion de la API web (FastAPI)."""

import pytest
from fastapi.testclient import TestClient

import app as web_app

DATOS_IMPACT = {
    "tipo": "impact_interno",
    "razon_social": "Gran Américas Santiago Chile S.A.",
    "rut": "77981536-6",
    "direccion": "Eliodoro Yáñez N° 2972, oficina 311, Providencia, Santiago",
    "contacto": "Katherine Casas",
    "representante_legal": "Claudio Castillo Castillo",
    "fecha": "2026-07-22",
    "cliente_id": "CL099033",
    "digipass": "NA",
}

DATOS_TECHTOOL = {
    "tipo": "techtool_externo",
    "razon_social": "Transportes Andina Ltda.",
    "rut": "77981536-6",
    "direccion": "Camino a Melipilla 8500, Maipu, Santiago",
    "contacto": "Pedro Soto",
    "representante_legal": "María José Rivas",
    "fecha": "2026-09-04",
    "partner_id": "CL555111",
    "cantidad_licencias": "5",
}


@pytest.fixture
def cliente_http(tmp_path, monkeypatch):
    monkeypatch.setattr(web_app, "DIR_SALIDA", tmp_path / "salida")
    monkeypatch.setattr(web_app, "DIR_HISTORIAL", tmp_path / "historial")
    web_app.DIR_SALIDA.mkdir()
    return TestClient(web_app.app)


class TestPaginaInicio:
    def test_muestra_las_4_tarjetas_de_tipo(self, cliente_http):
        respuesta = cliente_http.get("/")
        assert respuesta.status_code == 200
        for tipo in ("impact_interno", "impact_externo", "techtool_interno", "techtool_externo"):
            assert f"/nuevo/{tipo}" in respuesta.text


class TestFormularioNuevo:
    def test_impact_muestra_sus_propios_campos(self, cliente_http):
        respuesta = cliente_http.get("/nuevo/impact_interno")
        assert respuesta.status_code == 200
        assert 'name="cliente_id"' in respuesta.text
        assert 'name="partner_id"' not in respuesta.text

    def test_techtool_muestra_sus_propios_campos(self, cliente_http):
        respuesta = cliente_http.get("/nuevo/techtool_externo")
        assert respuesta.status_code == 200
        assert 'name="partner_id"' in respuesta.text
        assert 'name="cantidad_licencias"' in respuesta.text
        assert 'name="cliente_id"' not in respuesta.text

    def test_tipo_desconocido_da_404(self, cliente_http):
        respuesta = cliente_http.get("/nuevo/no-existe")
        assert respuesta.status_code == 404


class TestGenerar:
    def test_genera_y_ofrece_descarga(self, cliente_http):
        respuesta = cliente_http.post("/generar", data=DATOS_IMPACT)
        assert respuesta.status_code == 200
        assert "El contrato se generó correctamente" in respuesta.text
        assert "/descargar/" in respuesta.text

    def test_rut_invalido_reprecarga_el_formulario_con_los_datos(self, cliente_http):
        datos = DATOS_IMPACT | {"rut": "11111111-9"}
        respuesta = cliente_http.post("/generar", data=datos)
        assert respuesta.status_code == 400
        assert "RUT" in respuesta.text
        assert "Gran Américas Santiago Chile S.A." in respuesta.text

    def test_fecha_invalida_reprecarga_el_formulario(self, cliente_http):
        datos = DATOS_IMPACT | {"fecha": "22/07/2026"}
        respuesta = cliente_http.post("/generar", data=datos)
        assert respuesta.status_code == 400
        assert "Fecha del contrato" in respuesta.text

    def test_cantidad_licencias_no_numerica_reprecarga_el_formulario(self, cliente_http):
        datos = DATOS_TECHTOOL | {"cantidad_licencias": "muchas"}
        respuesta = cliente_http.post("/generar", data=datos)
        assert respuesta.status_code == 400
        assert "Cantidad de licencias" in respuesta.text

    def test_tipo_desconocido_da_404(self, cliente_http):
        datos = DATOS_IMPACT | {"tipo": "no-existe"}
        respuesta = cliente_http.post("/generar", data=datos)
        assert respuesta.status_code == 404

    def test_generar_registra_en_el_historial(self, cliente_http):
        cliente_http.post("/generar", data=DATOS_IMPACT)
        respuesta = cliente_http.get("/historial")
        assert "Gran Américas Santiago Chile S.A." in respuesta.text


class TestDescargar:
    def test_archivo_inexistente_da_404(self, cliente_http):
        respuesta = cliente_http.get("/descargar/no-existe.docx")
        assert respuesta.status_code == 404

    def test_descarga_el_archivo_generado(self, cliente_http):
        generado = cliente_http.post("/generar", data=DATOS_IMPACT)
        nombre = generado.text.split("/descargar/")[1].split('"')[0]

        respuesta = cliente_http.get(f"/descargar/{nombre}")

        assert respuesta.status_code == 200
        assert respuesta.headers["content-type"].startswith(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def test_ignora_intentos_de_recorrer_directorios(self, cliente_http):
        respuesta = cliente_http.get("/descargar/..%2F..%2Fetc%2Fpasswd")
        assert respuesta.status_code == 404


class TestHistorial:
    def test_sin_contratos_generados_muestra_aviso(self, cliente_http):
        respuesta = cliente_http.get("/historial")
        assert respuesta.status_code == 200
        assert "Todavía no se generó ningún contrato" in respuesta.text

    def test_filtra_por_busqueda(self, cliente_http):
        cliente_http.post("/generar", data=DATOS_IMPACT)
        cliente_http.post("/generar", data=DATOS_TECHTOOL)

        respuesta = cliente_http.get("/historial", params={"q": "Transportes Andina"})

        assert "Transportes Andina Ltda." in respuesta.text
        assert "Gran Américas Santiago Chile S.A." not in respuesta.text

    def test_busqueda_sin_coincidencias_muestra_aviso(self, cliente_http):
        cliente_http.post("/generar", data=DATOS_IMPACT)
        respuesta = cliente_http.get(
            "/historial", params={"q": "nadie-existe-con-este-nombre"}
        )
        assert "No hay contratos que coincidan" in respuesta.text

    def test_muestra_interno_o_externo_segun_corresponda(self, cliente_http):
        cliente_http.post("/generar", data=DATOS_TECHTOOL)
        respuesta = cliente_http.get("/historial")
        assert "Externo" in respuesta.text
