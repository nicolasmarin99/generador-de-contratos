"""Tests del historial de contratos generados."""

from contratos.historial import registrar, listar


def _registrar_ejemplo(dir_historial, **overrides):
    datos = {
        "tipo": "impact_interno",
        "software": "Impact Online",
        "cliente_externo": False,
        "cliente": "Gran Américas Santiago Chile S.A.",
        "rut_cliente": "77.981.536-6",
        "fecha_contrato": "22-07-2026",
        "archivo": "2026-07-22_impact-interno_gran-americas.docx",
    }
    datos.update(overrides)
    return registrar(dir_historial, **datos)


class TestRegistrar:
    def test_devuelve_el_registro_con_id_asignado(self, tmp_path):
        registro = _registrar_ejemplo(tmp_path)
        assert registro.id == 1
        assert registro.cliente == "Gran Américas Santiago Chile S.A."

    def test_crea_la_base_de_datos_dentro_de_la_carpeta(self, tmp_path):
        _registrar_ejemplo(tmp_path)
        assert (tmp_path / "historial.db").exists()

    def test_dos_registros_seguidos_no_chocan(self, tmp_path):
        primero = _registrar_ejemplo(tmp_path, cliente="Cliente Uno")
        segundo = _registrar_ejemplo(tmp_path, cliente="Cliente Dos")
        assert primero.id != segundo.id


class TestListar:
    def test_sin_registros_devuelve_lista_vacia(self, tmp_path):
        assert listar(tmp_path) == []

    def test_devuelve_lo_mas_reciente_primero(self, tmp_path):
        _registrar_ejemplo(tmp_path, cliente="Primero", archivo="a.docx")
        _registrar_ejemplo(tmp_path, cliente="Segundo", archivo="b.docx")
        resultado = listar(tmp_path)
        assert [r.cliente for r in resultado] == ["Segundo", "Primero"]

    def test_filtra_por_cliente_sin_distinguir_mayusculas(self, tmp_path):
        _registrar_ejemplo(tmp_path, cliente="Transportes Andina Ltda.")
        _registrar_ejemplo(tmp_path, cliente="Scania Chile SA", archivo="otro.docx")
        resultado = listar(tmp_path, busqueda="transportes")
        assert len(resultado) == 1
        assert resultado[0].cliente == "Transportes Andina Ltda."

    def test_filtra_por_rut(self, tmp_path):
        _registrar_ejemplo(tmp_path, rut_cliente="77.981.536-6")
        _registrar_ejemplo(tmp_path, rut_cliente="76.999.222-7", archivo="otro.docx")
        resultado = listar(tmp_path, busqueda="76.999.222")
        assert len(resultado) == 1
        assert resultado[0].rut_cliente == "76.999.222-7"

    def test_filtra_por_software(self, tmp_path):
        _registrar_ejemplo(tmp_path, software="Impact Online")
        _registrar_ejemplo(
            tmp_path,
            software="TechTool Hardware Independent",
            archivo="otro.docx",
        )
        resultado = listar(tmp_path, busqueda="techtool")
        assert len(resultado) == 1
        assert resultado[0].software == "TechTool Hardware Independent"

    def test_busqueda_sin_coincidencias_devuelve_lista_vacia(self, tmp_path):
        _registrar_ejemplo(tmp_path)
        assert listar(tmp_path, busqueda="no existe nadie con este nombre") == []

    def test_busqueda_vacia_equivale_a_listar_todo(self, tmp_path):
        _registrar_ejemplo(tmp_path, cliente="Uno", archivo="uno.docx")
        _registrar_ejemplo(tmp_path, cliente="Dos", archivo="dos.docx")
        assert len(listar(tmp_path, busqueda="   ")) == 2
