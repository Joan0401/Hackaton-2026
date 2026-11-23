"""Productos de La Pulpería dibujados como pixel art.

Cada sprite es una cuadrícula de texto: cada carácter es un píxel lógico
y el punto (.) es transparente. Para crear un producto nuevo basta con
agregar su dibujo en SPRITES y sus datos en PRODUCTOS.
"""
import pygame

# ---------------------------------------------------------
# PALETA (carácter -> color)
# ---------------------------------------------------------
PALETA = {
    "o": (48, 32, 36),      # contorno oscuro
    "w": (250, 240, 214),   # brillo
    # Rojos (manzana, tomate)
    "R": (200, 58, 52),
    "r": (142, 36, 40),
    # Amarillos (banano, elote)
    "Y": (240, 204, 76),
    "y": (196, 150, 46),
    "K": (246, 214, 96),
    "k": (214, 162, 52),
    # Naranja y zanahoria
    "O": (234, 140, 50),
    "n": (180, 92, 36),
    # Morado (uvas)
    "P": (124, 72, 150),
    "p": (84, 46, 106),
    # Verdes (hojas, brócoli, tallos)
    "G": (96, 170, 74),
    "g": (52, 112, 58),
    "B": (70, 140, 66),
    "b": (124, 190, 92),
    "S": (176, 206, 128),
    "h": (120, 160, 80),
    # Café (tallos, puntas)
    "s": (110, 72, 44),
    # Botellas
    "c": (214, 214, 206),   # tapa
    # Abarrotes (bolsas, leche y huevos)
    "Q": (242, 240, 232),   # bolsa blanca
    "A": (74, 118, 200),    # etiqueta azul (harina)
    "Z": (226, 104, 150),   # etiqueta rosada (azúcar)
    "V": (236, 220, 176),   # bolsa crema (arroz)
    "X": (86, 158, 84),     # etiqueta verde (arroz)
    "F": (128, 46, 44),     # bolsa roja oscura (frijoles)
    "f": (236, 214, 170),   # etiqueta clara (frijoles)
    "M": (70, 120, 196),    # franja azul de la leche
    "E": (250, 240, 216),   # huevo
    "e": (216, 196, 158),   # sombra del huevo
}

# ---------------------------------------------------------
# SPRITES
# ---------------------------------------------------------
SPRITES = {
    # ------------------- FRUTAS -------------------
    "manzana": [
        ".....s.....",
        "....sgG....",
        "..ooosooo..",
        ".oRRRoRRRo.",
        "oRwRRRRRRRo",
        "oRwRRRRRRRo",
        "oRRRRRRRRro",
        "oRRRRRRRRro",
        ".oRRRRRRro.",
        "..oRrorRo..",
        "...oo.oo...",
    ],
    "banano": [
        "s..........s",
        "oo........oo",
        "oYo......oYo",
        "oYYo....oYYo",
        "oyYYooooYYYo",
        ".oyYYYYYYYo.",
        ".oyyYYYYYyo.",
        "..ooyyyyyo..",
        "....ooooo...",
    ],
    "naranja": [
        ".....sG....",
        "...ooooo...",
        "..oOOOOOo..",
        ".oOwOOOOOo.",
        ".oOwOOOOOo.",
        ".oOOOOOOOo.",
        ".oOOOOOOno.",
        ".oOOOOOnno.",
        "..oOOOnno..",
        "...ooooo...",
    ],
    "uvas": [
        ".....s....",
        "....sgG...",
        ".oo.oo.oo.",
        "oPwooPwoPo",
        "oPPpoPPoPo",
        ".ooPwooPo.",
        ".oPPPoPPo.",
        "..ooPwoo..",
        "..oPPPPo..",
        "...ooPo...",
        "....oo....",
    ],
    # ------------------ VERDURAS ------------------
    # Zanahoria, brócoli y elote: versión chica del pixel art de imagenes/
    # (colores propios en COLORES_PROPIOS, más abajo).
    "zanahoria": [
        "..o.oo.o.",
        ".oloGlGo.",
        ".olGlGGo.",
        "..oGGGo..",
        ".oOOOOOo.",
        ".oOhOOOo.",
        ".oOOOOro.",
        "..oOOOo..",
        "..oOOro..",
        "...oOo...",
        "...oro...",
        "....o....",
    ],
    "tomate": [
        "...g.G.g...",
        "....gGg....",
        "..oooGooo..",
        ".oRRRgRRRo.",
        "oRwRRRRRRRo",
        "oRwRRRRRRRo",
        "oRRRRRRRRro",
        ".oRRRRRRro.",
        "..oorrroo..",
        "....ooo....",
    ],
    "brocoli": [
        "...ooo.oo..",
        "..oLlLoGLo.",
        ".oLlLLolGLo",
        "oLLlLGoGLGo",
        "oGLLGGGLGGo",
        ".oGGoGGGGo.",
        "..oo.oSSo..",
        "....oSSso..",
        "...oSsSo...",
        "...oSSo....",
        "....oo.....",
    ],
    "elote": [
        "...oo...",
        "..oYyo..",
        ".oYyYOo.",
        ".oyYyOo.",
        "ooYyYOoo",
        "oloyYOdo",
        "ollooddo",
        ".olgddo.",
        ".ollgdo.",
        "..olgo..",
        "...oo...",
    ],
}

# ------------------ ABARROTES ------------------
def _bolsa(cuerpo, etiqueta):
    """Bolsa de abarrotes amarrada arriba, con etiqueta de color."""
    plantilla = [
        "...o.o...",
        "..oCoCo..",
        ".oCCCCCo.",
        "oCCCCCCCo",
        "oCLLLLLCo",
        "oCLLLLLCo",
        "oCLLLLLCo",
        "oCCCCCCCo",
        "oCCCCCCCo",
        ".ooooooo.",
    ]
    return [f.replace("C", cuerpo).replace("L", etiqueta) for f in plantilla]


# Harina: saco naranja con harina blanca asomando arriba y una espiga
# (versión chica del pixel art de imagenes/harina.png).
COLORES_HARINA = {
    "2": (253, 253, 255), "3": (204, 204, 204), "4": (246, 179, 136),
    "5": (182, 98, 45), "6": (227, 125, 58), "o": (39, 32, 40),
}
SPRITES.update({
    "harina": [
        "...oooo...",
        "..o2222o..",
        ".o322223o.",
        "o44444444o",
        "o56666665o",
        ".o666666o.",
        "o66262266o",
        "o64266666o",
        "o66266666o",
        "oooooooooo",
    ],
    "azucar": _bolsa("Q", "Z"),
    "arroz": _bolsa("V", "X"),
    "frijoles": _bolsa("F", "f"),
    # Cajita de leche delgada: cabe en los huecos de la refri (como una botella).
    # Caja de leche (versión chica del pixel art de imagenes/leche.png)
    "leche": [
        ".ooo.",
        "oWWwo",
        "oWWwo",
        "oBBbo",
        "oWBbo",
        "oBBbo",
        "oBcbo",
        "oBBbo",
        "oBBbo",
        "ooooo",
    ],
    # Helados (versión chica del pixel art de imagenes/paleta.png y cono.png)
    "paleta": [
        ".ooo.",
        "oCCCo",
        "oRwRo",
        "oRRRo",
        "oRRRo",
        "orrro",
        ".oSo.",
        ".oSo.",
        "..o..",
    ],
    "cono": [
        "..oxo..",
        ".oFFFo.",
        "oFwFFfo",
        "oVVVVvo",
        ".oMmMo.",
        ".oMnMo.",
        "..oMo..",
        "..omo..",
        "...o...",
    ],
    "huevos": [
        "..ooo..",
        ".oWEEo.",
        "oWEEEEo",
        "oEEEEeo",
        "oEEEEeo",
        "oeEEeso",
        ".oesso.",
        "..ooo..",
    ],
})

# Botellas para refrigeradores (4 x 10). "L" = etiqueta, "X" = líquido.
BOTELLA = [
    ".cc.",
    ".oo.",
    ".XX.",
    "oXXo",
    "oXwo",
    "oLLo",
    "oLLo",
    "oXXo",
    "oXXo",
    "oooo",
]

# Colores (líquido, etiqueta) de cada bebida.
COLORES_BEBIDA = {
    "cola": ((92, 46, 36), (206, 54, 50)),
    "naranjada": ((236, 148, 48), (250, 236, 200)),
    "limonada": ((112, 186, 84), (250, 236, 200)),
    "agua": ((150, 196, 222), (70, 120, 180)),
    "fresa": ((214, 70, 92), (250, 236, 200)),
}
BEBIDAS = list(COLORES_BEBIDA)

# Botellas chicas de cada bebida (refris y globos), como el pixel art de
# imagenes/ (agua, naranjada, fresa, cola y limonada en vaso).
SPRITES_BEBIDA = {
    "agua": [".bb.", ".oo.", "oWco", "oWco", "oLLo", "osso", "oWco", "oWco", "oWco", "oooo"],
    "naranjada": [".NN.", ".oo.", "oNno", "oNno", "oAAo", "oAgo", "oNno", "oNno", "oNno", "oooo"],
    "fresa": [".PP.", ".oo.", "oRro", "oRro", "oKko", "oSko", "oKSo", "oKko", "oRro", "oooo"],
    "cola": [".CC.", ".oo.", ".DD.", "oDdo", "oDho", "oQQo", "oZZo", "oQQo", "oDdo", "oooo"],
    "limonada": ["...L", "o..o", "oFFo", "oYIo", "oYYo", "oIYo", "oYYo", "oYYo", "oYYo", "oooo"],
}
COLORES_BEBIDA_CHICA = {
    "o": (24, 22, 34),
    "b": (70, 110, 210), "W": (226, 242, 255), "c": (90, 196, 230), "L": (84, 112, 226),
    "s": (250, 252, 255),
    "N": (246, 122, 0), "n": (200, 96, 0), "A": (252, 176, 66), "g": (0, 130, 100),
    "P": (240, 90, 140), "R": (250, 130, 175), "r": (212, 84, 132), "K": (252, 176, 204),
    "k": (222, 126, 164), "S": (226, 46, 68),
    "C": (214, 40, 40), "D": (84, 30, 22), "d": (124, 50, 32), "h": (196, 150, 140),
    "Q": (222, 40, 40), "Z": (250, 246, 240),
    "F": (255, 242, 206), "Y": (250, 214, 120), "I": (255, 252, 240),
}
COLORES_BEBIDA_CHICA["L_limon"] = (240, 226, 90)

# ---------------------------------------------------------
# DATOS DE VENTA
# ---------------------------------------------------------
PRODUCTOS = {
    # tipo: (nombre, plural, precio en colones)
    # Precios de UNA sola cifra (1 a 9) para que el niño calcule mentalmente.
    "manzana": ("MANZANA", "Manzanas", 3),
    "banano": ("BANANO", "Bananos", 1),
    "naranja": ("NARANJA", "Naranjas", 2),
    "uvas": ("RACIMO DE UVAS", "Racimos de uvas", 7),
    "zanahoria": ("ZANAHORIA", "Zanahorias", 2),
    "tomate": ("TOMATE", "Tomates", 3),
    "brocoli": ("BRÓCOLI", "Brócolis", 5),
    "elote": ("ELOTE", "Elotes", 4),
    # Bebidas de las refrigeradoras
    "cola": ("COLA", "Colas", 6),
    "naranjada": ("NARANJADA", "Naranjadas", 5),
    "limonada": ("LIMONADA", "Limonadas", 5),
    "agua": ("AGUA", "Aguas", 3),
    "fresa": ("GASEOSA DE FRESA", "Gaseosas de fresa", 5),
    # Abarrotes (estante de la pared): ingredientes de las recetas
    "harina": ("BOLSA DE HARINA", "Bolsas de harina", 4),
    "azucar": ("BOLSA DE AZÚCAR", "Bolsas de azúcar", 3),
    "arroz": ("BOLSA DE ARROZ", "Bolsas de arroz", 3),
    "frijoles": ("BOLSA DE FRIJOLES", "Bolsas de frijoles", 4),
    "leche": ("CAJA DE LECHE", "Cajas de leche", 3),
    "huevos": ("HUEVO", "Huevos", 1),
    # Helados (heladera junto al mostrador)
    "paleta": ("HELADO DE PALETA", "Helados de paleta", 3),
    "cono": ("HELADO DE CONO", "Helados de cono", 4),
}

# Si alguien pone un precio de dos cifras, el juego avisa al arrancar.
for _tipo, (_nombre, _plural, _precio) in PRODUCTOS.items():
    assert 1 <= _precio <= 9, f"El precio de {_tipo} debe ser de una cifra (1 a 9)"

FRUTAS = ["manzana", "banano", "naranja", "uvas"]
ABARROTES = ["harina", "azucar", "arroz", "frijoles"]
# Los huevos van en la huevera, junto al mostrador.
HUEVOS = ["huevos"]
# La leche va en la refri de leches y aguas (la de la derecha).
REFRIGERADOS = ["leche"]
VERDURAS = ["zanahoria", "tomate", "brocoli", "elote"]
# Los helados van en la heladera (en L con el mostrador).
HELADOS = ["paleta", "cono"]


# ---------------------------------------------------------
# RENDER
# ---------------------------------------------------------
_cache = {}


def _construir(filas, extra=None):
    colores = dict(PALETA)
    if extra:
        colores.update(extra)
    w = max(len(f) for f in filas)
    surf = pygame.Surface((w, len(filas)), pygame.SRCALPHA)
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            if ch != "." and ch in colores:
                surf.set_at((x, y), colores[ch])
    return surf


# Colores propios de los sprites chicos hechos a partir del pixel art.
COLORES_PROPIOS = {
    "harina": COLORES_HARINA,
    "zanahoria": {"o": (24, 18, 16), "l": (150, 214, 70), "G": (70, 150, 50),
                  "O": (244, 140, 40), "h": (255, 204, 150), "r": (200, 92, 30)},
    "brocoli": {"o": (40, 10, 10), "L": (80, 190, 20), "l": (150, 250, 30), "G": (10, 112, 10),
                "S": (40, 150, 20), "s": (130, 240, 30)},
    "elote": {"o": (34, 26, 22), "Y": (255, 232, 100), "y": (250, 190, 50), "O": (232, 124, 34),
              "l": (176, 232, 96), "g": (110, 196, 70), "d": (40, 136, 52)},
    "leche": {"o": (30, 40, 80), "W": (240, 248, 250), "w": (200, 226, 230),
              "B": (84, 132, 222), "b": (52, 82, 190), "c": (232, 192, 140)},
    "huevos": {"o": (110, 100, 80), "W": (252, 246, 228), "E": (238, 226, 196),
               "e": (214, 198, 160), "s": (180, 162, 124)},
    "paleta": {"o": (40, 26, 30), "C": (120, 70, 44), "R": (246, 120, 160), "r": (214, 80, 124),
               "w": (255, 200, 220), "S": (230, 200, 150)},
    "cono": {"o": (40, 26, 30), "x": (230, 60, 70), "F": (250, 160, 190), "f": (220, 110, 150),
             "w": (255, 220, 235), "V": (255, 246, 222), "v": (236, 214, 180),
             "M": (226, 160, 90), "m": (186, 116, 56), "n": (150, 90, 40)},
}


def sprite(tipo):
    if tipo not in _cache:
        if tipo in SPRITES_BEBIDA:
            colores = dict(COLORES_BEBIDA_CHICA)
            if tipo == "limonada":
                colores["L"] = COLORES_BEBIDA_CHICA["L_limon"]
            _cache[tipo] = _construir(SPRITES_BEBIDA[tipo], colores)
        elif tipo in COLORES_BEBIDA:
            liquido, etiqueta = COLORES_BEBIDA[tipo]
            _cache[tipo] = _construir(BOTELLA, {"X": liquido, "L": etiqueta})
        else:
            _cache[tipo] = _construir(SPRITES[tipo], COLORES_PROPIOS.get(tipo))
    return _cache[tipo]


def tamano(tipo):
    return sprite(tipo).get_size()


def dibujar_producto(surface, tipo, x, y):
    """Dibuja el producto con su esquina superior izquierda en (x, y)."""
    surface.blit(sprite(tipo), (round(x), round(y)))


def dibujar_botella(surface, x, y, variante):
    dibujar_producto(surface, BEBIDAS[variante % len(BEBIDAS)], x, y)
