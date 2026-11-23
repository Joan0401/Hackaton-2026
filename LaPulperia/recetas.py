"""Libro de recetas: el cliente pide un tercio, la mitad, una receta o el
doble de una receta ("medio queque", "el doble de pan") y el niño calcula
los ingredientes. Cada receta tiene como máximo 4 ingredientes.

Solo se piden los tamaños que dan números enteros: si una fracción no
divide exacto (p. ej. la mitad de 3 bolsas de harina), el juego no la pide.
"""
from fractions import Fraction

from productos import PRODUCTOS

# clave: nombre, género (para "medio"/"media"), ingredientes [(producto, cantidad)]
# y qué tamaños puede pedir un cliente de esa receta.
RECETAS = {
    "pan": {
        "nombre": "Pan", "genero": "m",
        "ingredientes": [("huevos", 6), ("harina", 3)],
        "factores": ["tercio", "medio", "doble", "triple"],
    },
    "queque": {
        "nombre": "Queque", "genero": "m",
        "ingredientes": [("huevos", 6), ("harina", 2), ("azucar", 2), ("leche", 2)],
        "factores": ["medio", "doble", "triple"],
    },
    "arroz_leche": {
        "nombre": "Arroz con leche", "genero": "m",
        "ingredientes": [("arroz", 4), ("leche", 2), ("azucar", 2)],
        "factores": ["tercio", "medio", "doble", "triple"],
    },
    "gallo_pinto": {
        "nombre": "Gallo pinto", "genero": "m",
        "ingredientes": [("arroz", 3), ("frijoles", 3)],
        "factores": ["tercio", "doble", "triple"],
    },
    "ensalada": {
        "nombre": "Ensalada de frutas", "genero": "f",
        "ingredientes": [("manzana", 3), ("banano", 3), ("uvas", 3), ("naranja", 3)],
        "factores": ["tercio", "doble", "triple"],
    },
    # Con los helados de la heladera:
    "vaca_negra": {
        "nombre": "Vaca negra", "genero": "f",
        "ingredientes": [("cono", 4), ("cola", 4)],
        "factores": ["cuarto", "medio", "doble", "triple"],
    },
    "banana_split": {
        "nombre": "Banana split", "genero": "m",
        "ingredientes": [("banano", 4), ("cono", 4)],
        "factores": ["cuarto", "medio", "doble", "triple"],
    },
    "licuado": {
        "nombre": "Licuado de banano", "genero": "m",
        "ingredientes": [("banano", 4), ("leche", 4)],
        "factores": ["cuarto", "medio", "doble", "triple"],
    },
}
ORDEN = ["pan", "queque", "arroz_leche", "gallo_pinto", "ensalada",
         "vaca_negra", "banana_split", "licuado"]

# clave: (factor, cómo se escribe, operación)
FACTORES = {
    "tercio": (Fraction(1, 3), "un tercio", "÷ 3"),
    "medio": (Fraction(1, 2), "medio", "÷ 2"),
    "cuarto": (Fraction(1, 4), "un cuarto", "÷ 4"),
    "unidad": (Fraction(1), "una receta", "× 1"),
    "doble": (Fraction(2), "el doble", "× 2"),
    "triple": (Fraction(3), "el triple", "× 3"),
}
ORDEN_FACTORES = ["tercio", "medio", "cuarto", "doble", "triple"]


def cantidades(clave, factor):
    """{producto: cantidad} para esa fracción, o None si no da enteros."""
    f = FACTORES[factor][0]
    salida = {}
    for kind, cantidad in RECETAS[clave]["ingredientes"]:
        q = cantidad * f
        if q.denominator != 1 or q <= 0:
            return None
        salida[kind] = int(q)
    return salida


def factores_receta(clave):
    """Tamaños que se pueden pedir de esa receta y que dan números enteros
    (p. ej. la mitad de pan no: serían 1 bolsa y media de harina)."""
    return [f for f in RECETAS[clave]["factores"] if cantidades(clave, f) is not None]


def combinaciones_validas(factores_permitidos, disponibles):
    """Todas las (receta, factor) permitidas, enteras y en existencia."""
    opciones = []
    for clave in ORDEN:
        for factor in factores_receta(clave):
            if factor not in factores_permitidos:
                continue
            pedido = cantidades(clave, factor)
            if all(disponibles.get(k, 0) >= q for k, q in pedido.items()):
                opciones.append((clave, factor, pedido))
    return opciones


def frase_pedido(clave, factor):
    """'medio queque', 'media ensalada de frutas', 'el triple de pan'..."""
    receta = RECETAS[clave]
    nombre = receta["nombre"].lower()
    if factor == "medio":
        return ("media " if receta["genero"] == "f" else "medio ") + nombre
    if factor == "unidad":
        return f"una receta de {nombre}"
    return f"{FACTORES[factor][1]} de {nombre}"


def texto_ingrediente(kind, cantidad):
    nombre = PRODUCTOS[kind][0] if cantidad == 1 else PRODUCTOS[kind][1]
    return f"{cantidad} {nombre.lower()}"
