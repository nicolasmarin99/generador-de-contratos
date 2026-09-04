"""Validaciones de dominio.

Aqui vive la logica que decide si un dato es valido o no.
Se mantiene separada de los modelos para poder testearla sola.
"""

import re


class RutInvalido(ValueError):
    """Se lanza cuando un RUT no supera la validacion de modulo 11."""


def limpiar_rut(rut: str) -> str:
    """Deja el RUT en formato canonico: solo digitos + guion + verificador.

    '77.981.536-6' -> '77981536-6'
    """
    sin_formato = re.sub(r"[^0-9kK]", "", rut).upper()
    if len(sin_formato) < 2:
        raise RutInvalido(f"RUT demasiado corto: {rut!r}")
    return f"{sin_formato[:-1]}-{sin_formato[-1]}"


def digito_verificador(cuerpo: str) -> str:
    """Calcula el digito verificador con el algoritmo modulo 11.

    Se recorre el numero de derecha a izquierda multiplicando cada digito
    por la serie 2,3,4,5,6,7 (que se reinicia al llegar a 7).
    El resto de dividir la suma por 11 se resta de 11 para obtener el digito.
    """
    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = 11 - (suma % 11)
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


def validar_rut(rut: str) -> str:
    """Valida un RUT y lo devuelve formateado con puntos y guion.

    Devuelve el RUT normalizado ('77.981.536-6') o lanza RutInvalido.
    """
    canonico = limpiar_rut(rut)
    cuerpo, _, verificador = canonico.partition("-")

    if not cuerpo.isdigit():
        raise RutInvalido(f"El cuerpo del RUT debe ser numerico: {rut!r}")

    esperado = digito_verificador(cuerpo)
    if verificador != esperado:
        raise RutInvalido(
            f"RUT invalido: {rut!r}. El digito verificador deberia ser {esperado}."
        )

    return f"{formatear_miles(cuerpo)}-{verificador}"


def formatear_miles(numero: str) -> str:
    """'77981536' -> '77.981.536'"""
    return f"{int(numero):,}".replace(",", ".")
