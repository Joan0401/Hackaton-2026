"""Niveles de dificultad de La Pulpería (piso bajo - techo alto).

Cada nivel sube de HABILIDAD, no de tamaño de los números: los precios
son los mismos (1 a 9) en todos los niveles.

El equipo puede ajustar estos valores sin tocar la lógica del juego.
Los marcados "(clientes)" los usa clientes.py.
"""

NIVELES = {
    "principiante": {
        "nombre": "PRINCIPIANTE",
        "habilidad": "Conteo y número-cantidad",
        "descripcion": (
            "La factura te dice cuántos hay.",
            "Pistas desde el primer error.",
            "Calculadora: ₡5 por factura.",
        ),
        # Factura
        "factura_muestra_cantidad": True,   # "3 COLAS x 6" o solo dibujos
        "pista_desde_error": 1,             # en qué error aparece la pista
        "errores_para_calculadora": 2,
        "precio_calculadora": 5,      # ₡ para usarla en UNA factura
        # (clientes)
        "pedido_productos": (1, 1),         # mínimo y máximo por pedido
        "pedido_oculta_segundos": 5,       # se esconde a los 5 s (P lo repite)
        "pedido_con_pistas": False,
        "clientes_en_fila": 2,
        "pedido_unidades": (1, 3),         # unidades de cada producto
        "reclamo_detallado": True,       # el cliente dice qué falta o sobra
        "paciencia_segundos": 150,      # si no lo atiendes a tiempo, se va molesto
        "repeticiones_maximas": 2,      # veces que repite su pedido (P); a la 3.ª se va
        # Clientes por día: 5 frecuentes + 4 normales (lo arma clientes.py).
        # Libro de recetas: algunos clientes piden un tercio, un cuarto, la mitad
        # o el doble (nunca la receta entera: esa ya está en el libro), y el niño calcula los ingredientes (proporciones).
        # Además, cada receta tiene sus propios tamaños (ver recetas.py).
        "receta_probabilidad": 0.35,
        "fracciones_receta": ["tercio", "medio", "cuarto", "doble", "triple"],
    },
    "intermedio": {
        "nombre": "INTERMEDIO",
        "habilidad": "Memoria de trabajo",
        "descripcion": (
            "Cuenta los productos tú mismo.",
            "Pistas paso a paso.",
            "Calculadora: ₡10 por factura.",
        ),
        "factura_muestra_cantidad": False,
        "pista_desde_error": 1,
        "errores_para_calculadora": 3,
        "precio_calculadora": 10,
        "pedido_productos": (2, 3),
        "pedido_oculta_segundos": 8,
        "pedido_con_pistas": False,
        "clientes_en_fila": 4,
        "pedido_unidades": (1, 2),         # unidades de cada producto
        "reclamo_detallado": True,       # el cliente dice qué falta o sobra
        "paciencia_segundos": 120,      # si no lo atiendes a tiempo, se va molesto
        "repeticiones_maximas": 2,      # veces que repite su pedido (P); a la 3.ª se va
        # Clientes por día: 5 frecuentes + 4 normales (lo arma clientes.py).
        # Libro de recetas: algunos clientes piden un tercio, un cuarto, la mitad
        # o el doble (nunca la receta entera: esa ya está en el libro), y el niño calcula los ingredientes (proporciones).
        # Además, cada receta tiene sus propios tamaños (ver recetas.py).
        "receta_probabilidad": 0.45,
        "fracciones_receta": ["tercio", "medio", "cuarto", "doble", "triple"],
    },
    "avanzado": {
        "nombre": "AVANZADO",
        "habilidad": "Memoria + deducción",
        "descripcion": (
            "Cuenta los productos tú mismo.",
            "Pistas solo si fallas 2 veces.",
            "Calculadora: ₡15 por factura.",
        ),
        "factura_muestra_cantidad": False,
        "pista_desde_error": 2,
        "errores_para_calculadora": 4,
        "precio_calculadora": 15,
        "pedido_productos": (3, 4),
        "pedido_oculta_segundos": 5,
        "pedido_con_pistas": True,
        "clientes_en_fila": 6,
        "pedido_unidades": (1, 2),         # unidades de cada producto
        "reclamo_detallado": False,       # el cliente dice qué falta o sobra
        "paciencia_segundos": 100,      # si no lo atiendes a tiempo, se va molesto
        "repeticiones_maximas": 2,      # veces que repite su pedido (P); a la 3.ª se va
        # Clientes por día: 5 frecuentes + 4 normales (lo arma clientes.py).
        # Libro de recetas: algunos clientes piden un tercio, un cuarto, la mitad
        # o el doble (nunca la receta entera: esa ya está en el libro), y el niño calcula los ingredientes (proporciones).
        # Además, cada receta tiene sus propios tamaños (ver recetas.py).
        "receta_probabilidad": 0.5,
        "fracciones_receta": ["tercio", "medio", "cuarto", "doble", "triple"],
    },
}

ORDEN = ["principiante", "intermedio", "avanzado"]
NIVEL_INICIAL = "intermedio"
