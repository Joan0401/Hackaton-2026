"""MODO HISTORIA: la primera semana en la pulpería con Doña Rosa.

Doña Rosa, la dueña, te deja la pulpería a cargo. Cada día:
  - SALUDO al empezar (y la meta del día con un dibujito).
  - DESPEDIDA al terminar el turno, siempre con el nombre del jugador.
Los días 1 a 7 tienen saludos y metas propios. Desde el día 8 los saludos
y las metas se repiten en ronda. Al empezar el día 8 sube la dificultad
y al empezar el día 16 sube otra vez. Si no se cumple la meta no pasa
nada: se avanza igual.

Aquí solo hay textos y reglas (sin dibujos); main.py los muestra.
Cada página del diálogo es (renglón 1, renglón 2, meta o None).
"""

DIAS_HISTORIA = 7
DIAS_SUBIR_NIVEL = (8, 16)     # al empezar estos días sube la dificultad

# Tipos de meta (los dibujitos están en main.py, draw_icono_meta):
#   atender: clientes atendidos      vender: ₡ vendidos en el día
#   camion: hacer un pedido          tavo: llamar al ayudante
#   receta: entregar una receta      sin_perdidos: que no se vaya nadie
TEXTO_META = {
    "atender": "Atiende a {n} clientes.",
    "vender": "Vende ₡{n} hoy.",
    "camion": "Pide mercadería por teléfono.",
    "tavo": "Llama a Tavo para que te ayude.",
    "receta": "Entrega una receta.",
    "sin_perdidos": "Que no se vaya ningún cliente.",
}

DIAS = {
    1: {"saludo": [("¡Hola, {nombre}! Soy Doña Rosa.", "Desde hoy cuidas mi pulpería."),
                   ("{mascota}", "Yo te ayudo los primeros días.")],
        "meta": ("atender", 3),
        "manana": "Mañana: ¡a vender más!"},
    2: {"saludo": [("¡Buenos días, {nombre}!", "Hoy quiero ver esa caja llena.")],
        "meta": ("vender", 30),
        "manana": "Mañana vas a llamar al camión."},
    3: {"saludo": [("¡Buenos días, {nombre}!", "El teléfono está en el mostrador.")],
        "meta": ("camion", 1),
        "manana": "Mañana conocerás a Tavo."},
    4: {"saludo": [("¡Hola, {nombre}!", "Tavo te ayuda. Su botón está en la pared.")],
        "meta": ("tavo", 1),
        "manana": "Mañana vienen pedidos de recetas."},
    5: {"saludo": [("¡Buenos días, {nombre}!", "Hoy piden recetas. ¡Usa el libro (R)!")],
        "meta": ("receta", 1),
        "manana": "Mañana: ¡que nadie se vaya!"},
    6: {"saludo": [("¡Hola, {nombre}!", "Hoy hay que atender rápido.")],
        "meta": ("sin_perdidos", 0),
        "manana": "Mañana es el último día de la semana."},
    7: {"saludo": [("¡Último día de la semana, {nombre}!", "Muéstrame todo lo que aprendiste.")],
        "meta": ("vender", 60),
        "manana": ""},
}

# Desde el día 8: saludos y metas en ronda.
SALUDOS = [
    ("¡Buenos días, {nombre}!", "¿Lista la pulpería?"),
    ("¡Hola, {nombre}!", "Hoy va a ser un gran día."),
    ("¡Buenos días, {nombre}!", "Los clientes ya vienen."),
    ("¡Hola, {nombre}!", "¡Qué bonita está la pulpería!"),
]
METAS_RONDA = ["atender", "vender", "sin_perdidos", "camion", "receta", "tavo"]


def _sin_receta(meta, hay_recetas):
    """Si las recetas están apagadas en MODO DE JUEGO, otra meta posible."""
    if meta[0] == "receta" and not hay_recetas:
        return ("atender", 5)
    return meta


def meta(dia, hay_recetas=True):
    """(tipo, cantidad) de la meta del día."""
    if dia in DIAS:
        return _sin_receta(DIAS[dia]["meta"], hay_recetas)
    k = dia - DIAS_HISTORIA - 1
    tipo = METAS_RONDA[k % len(METAS_RONDA)]
    cantidad = {"atender": 6, "vender": min(100, 40 + 5 * (k // len(METAS_RONDA))),
                "sin_perdidos": 0}.get(tipo, 1)
    return _sin_receta((tipo, cantidad), hay_recetas)


def texto_meta(m):
    tipo, n = m
    return TEXTO_META[tipo].format(n=n)


def progreso(m, stats):
    """(lo que lleva, lo que falta llegar, ¿cumplida?). stats: atendidos,
    perdidos, ventas, camion, tavo, recetas."""
    tipo, n = m
    if tipo == "atender":
        return stats["atendidos"], n, stats["atendidos"] >= n
    if tipo == "vender":
        return stats["ventas"], n, stats["ventas"] >= n
    if tipo == "camion":
        return int(stats["camion"]), 1, bool(stats["camion"])
    if tipo == "tavo":
        return int(stats["tavo"]), 1, bool(stats["tavo"])
    if tipo == "receta":
        return stats["recetas"], 1, stats["recetas"] >= 1
    # sin_perdidos: cuenta los que se fueron; vale si atendió a alguien.
    return stats["perdidos"], 0, stats["perdidos"] == 0 and stats["atendidos"] > 0


def _texto(linea, nombre, mascota):
    return linea.format(nombre=nombre, mascota=mascota)


def paginas_saludo(dia, nombre, hay_recetas=True, mascota="", nivel_nuevo=None):
    """Páginas del saludo del día (el día 1 es la bienvenida)."""
    if mascota:
        texto_mascota = f"{mascota} te va a acompañar."
    else:
        texto_mascota = "¡Aquí vas a aprender mucho!"
    if dia in DIAS:
        lineas = DIAS[dia]["saludo"]
    else:
        lineas = [SALUDOS[(dia - DIAS_HISTORIA - 1) % len(SALUDOS)]]
    paginas = [(_texto(a, nombre, texto_mascota), _texto(b, nombre, texto_mascota), None)
               for a, b in lineas]
    if nivel_nuevo:
        paginas.append(("¡Ya sabes mucho!", f"Ahora juegas en nivel {nivel_nuevo}.", None))
    m = meta(dia, hay_recetas)
    paginas.append(("Meta de hoy:", texto_meta(m), m))
    return paginas


# Al empezar una partida, Doña Rosa pregunta quién acompaña al pulpero.
OPCIONES_MASCOTAS = [   # (texto del botón, gata, perro)
    ("LOS DOS", True, True), ("CANELA", True, False),
    ("BRUNO", False, True), ("NINGUNO", False, False),
]


def paginas_inicio(nombre):
    """Lo primero que dice Doña Rosa en una partida nueva (historia o libre)."""
    return [(f"¡Hola, {nombre}! Soy Doña Rosa.", "Desde hoy cuidas mi pulpería.", None),
            ("¿Quién quieres que te acompañe?", "", "elegir_mascotas")]


def texto_compania(gata, perro):
    if gata and perro:
        return "Canela y Bruno te van a acompañar."
    if gata:
        return "Canela te va a acompañar."
    if perro:
        return "Bruno te va a acompañar."
    return "¡Aquí vas a aprender mucho!"


def paginas_despues_de_elegir(gata, perro, con_historia, hay_recetas=True):
    """Lo que sigue después de elegir las mascotas."""
    if not con_historia:
        return [(texto_compania(gata, perro), "¡Que te vaya muy bien!", None)]
    m = meta(1, hay_recetas)
    return [(texto_compania(gata, perro), "Yo te ayudo los primeros días.", None),
            ("Meta de hoy:", texto_meta(m), m)]


def paginas_despedida(dia, nombre, cumplida):
    """La despedida al terminar el turno: siempre con el nombre."""
    if dia == DIAS_HISTORIA:
        return [
            ("¡Lo lograste!" if cumplida else "¡Qué bonita semana!",
             f"Terminaste tu primera semana, {nombre}.", "estrella" if cumplida else None),
            ("¡La pulpería es tuya!", f"¡Hasta mañana, {nombre}!", "medalla"),
        ]
    primera = "¡Cumpliste la meta!" if cumplida else "Mañana lo intentamos otra vez."
    manana = DIAS.get(dia, {}).get("manana", "")
    return [
        (primera, f"¡Hasta mañana, {nombre}!", "estrella" if cumplida else None),
    ] + ([(manana, "", None)] if manana else [])


def paginas_felicitacion(nombre):
    """Apenas se cumple la meta del día."""
    return [(f"¡Muy bien, {nombre}! Cumpliste la meta.",
             "Ahora solo falta terminar el día.", "estrella")]


# Esta meta solo se sabe al final del día (no se felicita antes).
SOLO_AL_FINAL = ("sin_perdidos",)


def nivel_siguiente(nivel, orden):
    """El nivel que sigue (o el mismo si ya es el más difícil)."""
    i = orden.index(nivel)
    return orden[min(i + 1, len(orden) - 1)]
