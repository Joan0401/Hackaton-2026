"""MODO DE JUEGO: qué problemas matemáticos aparecen en la partida.

Se cambia en OPCIONES > MODO DE JUEGO. Sucesiones, multiplicar recetas,
suma del cierre de caja, adivinanzas de colores y paciencia de los
clientes vienen apagados; los demás, encendidos. En pantalla salen en orden alfabético. Multiplicar
cantidad por precio y sumar el total de la factura siempre están (son la
base del juego); lo demás se puede apagar.
"""

# clave: (nombre en pantalla, habilidad, qué pasa si está activado, ... si no)
INFO = {
    "sucesiones": ("SUCESIONES (CLIENTES FRECUENTES)", "Razonamiento inductivo",
                   "Los frecuentes dicen su regla y a veces no se acuerdan.",
                   "Los frecuentes siguen viniendo, pero dicen cuánto quieren."),
    "fracciones": ("FRACCIONES DE RECETAS", "Fracciones",
                   "Piden la mitad, un tercio o un cuarto de una receta.",
                   "Nadie pide fracciones de recetas."),
    "multiplicar": ("MULTIPLICAR RECETAS", "Multiplicación",
                    "Piden el doble o el triple de una receta.",
                    "Nadie pide el doble ni el triple."),
    "vuelto": ("VUELTO EN LA FACTURA", "Resta",
               "El cliente paga con billetes y tú das el vuelto.",
               "El cliente paga exacto."),
    "cierre": ("SUMA DEL CIERRE DE CAJA", "Suma de varias cantidades",
               "Al final del día sumas todas tus ventas.",
               "El cierre de caja te dice el total."),
    "memoria": ("RECORDAR EL PEDIDO", "Memoria de trabajo",
                "El pedido se esconde a los pocos segundos (P lo repite).",
                "El pedido siempre se ve."),
    "descarte": ("ADIVINANZAS DE COLORES", "Razonamiento deductivo",
                 "En avanzado: 'una fruta que no es roja ni morada'.",
                 "Los clientes dicen el producto directo."),
    "contar": ("CONTAR EN LA FACTURA", "Conteo",
               "En intermedio y avanzado cuentas los dibujos.",
               "La factura siempre dice la cantidad."),
    "paciencia": ("PACIENCIA DE LOS CLIENTES", "Atender a tiempo",
                  "Cada cliente tiene una barrita; si tardas, se va.",
                  "Los clientes esperan sin apurarte."),
}
# En pantalla, en orden alfabético por su nombre.
ORDEN = sorted(INFO, key=lambda clave: INFO[clave][0])

# Vienen apagados de entrada (se encienden en OPCIONES > MODO DE JUEGO).
APAGADOS = ("sucesiones", "multiplicar", "cierre", "descarte", "paciencia")
PREDETERMINADO = {clave: clave not in APAGADOS for clave in INFO}

# Estado actual (lo comparten main.py y clientes.py).
MODO = dict(PREDETERMINADO)

FRACCIONES = ("tercio", "medio", "cuarto")
MULTIPLOS = ("doble", "triple")


def factores_permitidos(factores_nivel):
    """De los tamaños de receta del nivel, los que el modo de juego deja."""
    return [f for f in factores_nivel
            if (f in FRACCIONES and MODO["fracciones"])
            or (f in MULTIPLOS and MODO["multiplicar"])]
