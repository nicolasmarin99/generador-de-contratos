"""Modelos de datos del dominio.

Un "modelo" describe que forma tiene un dato valido. pydantic se encarga de
verificarlo automaticamente al construir el objeto: si falta un campo o el RUT
esta malo, el programa falla AQUI y no a mitad de generar el documento.

Esto se llama "fallar temprano" (fail fast) y es una de las razones por las que
vale la pena tener modelos en lugar de andar pasando diccionarios sueltos.
"""

from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

from .validadores import validar_rut


class Cliente(BaseModel):
    """La empresa que recibe la sublicencia.

    Este objeto se escribe UNA vez y se reutiliza en todos los contratos que
    firme ese cliente. Es la unica fuente de verdad de sus datos.
    """

    razon_social: str = Field(min_length=3)
    rut: str
    direccion: str = Field(min_length=10)
    contacto: str
    representante_legal: str

    @field_validator("rut")
    @classmethod
    def _rut_valido(cls, valor: str) -> str:
        # validar_rut devuelve el RUT ya formateado, asi que el modelo ademas
        # de validar, normaliza. No importa como venga escrito en el JSON.
        return validar_rut(valor)


class Sublicenciante(BaseModel):
    """La empresa del Grupo Volvo que otorga la sublicencia."""

    razon_social: str = "VOLVO CHILE SPA."
    rut: str = "76.284.920-8"
    direccion: str = (
        "Avenida Presidente Eduardo Frei Montalva 8691, Quilicura, Santiago"
    )

    @field_validator("rut")
    @classmethod
    def _rut_valido(cls, valor: str) -> str:
        return validar_rut(valor)


class ContratoBase(BaseModel):
    """Lo que comparten todos los contratos."""

    cliente: Cliente
    sublicenciante: Sublicenciante = Sublicenciante()
    fecha: date

    cliente_externo: bool = False
    """Si el cliente NO es del Grupo Volvo, la clausula de costos debe decir
    que el costo lo asume el Cliente en vez de Volvo. Cada software tiene dos
    plantillas .docx ya redactadas (interno/externo); este campo decide cual
    de las dos usa `generar_docx`. No es un marcador de la plantilla: decide
    QUE plantilla se carga, no que se imprime en ella."""

    #: Nombre del archivo .docx dentro de plantillas/. Cada subclase lo
    #: calcula solo a partir de cliente_externo (ver _elegir_plantilla).
    plantilla: str = ""

    def contexto(self) -> dict:
        """Aplana el modelo al diccionario que espera la plantilla.

        Separar el modelo del contexto importa: el modelo describe el negocio,
        el contexto describe lo que la plantilla necesita imprimir. Si manana
        cambia un marcador en el .docx, se toca solo este metodo.
        """
        return {
            "cliente": self.cliente.razon_social,
            "rut_cliente": self.cliente.rut,
            "direccion_cliente": self.cliente.direccion,
            "contacto": self.cliente.contacto,
            "representante_legal": self.cliente.representante_legal,
            "sublicenciante": self.sublicenciante.razon_social,
            "rut_sublicenciante": self.sublicenciante.rut,
            "direccion_sublicenciante": self.sublicenciante.direccion,
            "fecha": self.fecha.strftime("%d-%m-%Y"),
        }


class ContratoImpactOnline(ContratoBase):
    """Contrato de sublicencia del software Impact Online."""

    software: str = "Impact Online"
    cliente_id: str
    digipass: str = "NA"

    @model_validator(mode="after")
    def _elegir_plantilla(self) -> "ContratoImpactOnline":
        self.plantilla = f"impact/{'externo' if self.cliente_externo else 'interno'}.docx"
        return self

    def contexto(self) -> dict:
        base = super().contexto()
        base.update(
            {
                "software": self.software,
                "cliente_id": self.cliente_id,
                "digipass": self.digipass,
            }
        )
        return base


class ContratoTechTool(ContratoBase):
    """Contrato de sublicencia de TechTool Hardware Independent."""

    software: str = "TechTool Hardware Independent"
    partner_id: str
    cantidad_licencias: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def _elegir_plantilla(self) -> "ContratoTechTool":
        self.plantilla = f"techtool/{'externo' if self.cliente_externo else 'interno'}.docx"
        return self

    def contexto(self) -> dict:
        base = super().contexto()
        base.update(
            {
                "software": self.software,
                "partner_id": self.partner_id,
                "cantidad_licencias": self.cantidad_licencias,
            }
        )
        return base


#: Mapa nombre-corto -> clase. Lo usa la CLI y despues lo usara la web
#: para saber que contrato construir a partir de un string.
TIPOS_DE_CONTRATO = {
    "impact": ContratoImpactOnline,
    "techtool": ContratoTechTool,
}
