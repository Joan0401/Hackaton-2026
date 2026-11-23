
import math
import pygame

from carrito import ancla
from productos import (
    PRODUCTOS, FRUTAS, VERDURAS, BEBIDAS, ABARROTES, REFRIGERADOS, HUEVOS, HELADOS,
    dibujar_producto, dibujar_botella, tamano,
)

FLOOR_TOP = 96  # El piso comienza en y=96 (coordenadas logicas).


# =========================================================
# ESCALADO DE COORDENADAS: 480x270 -> 640x360
# Cada mueble se dibuja directamente sobre la superficie final.
# =========================================================

DRAW_SCALE = 4 / 3


def _scale_value(value):
    return int(round(value * DRAW_SCALE))


def _scale_point(point):
    return tuple(_scale_value(v) for v in point)


def _scale_rect(rect):
    return tuple(_scale_value(v) for v in rect)


class ScaledDraw:

    @staticmethod
    def rect(surface, color, rect, width=0, border_radius=0):
        return pygame.draw.rect(
            surface,
            color,
            _scale_rect(rect),
            _scale_value(width),
            border_radius=_scale_value(border_radius)
        )

    @staticmethod
    def line(surface, color, start_pos, end_pos, width=1):
        return pygame.draw.line(
            surface,
            color,
            _scale_point(start_pos),
            _scale_point(end_pos),
            max(1, _scale_value(width))
        )

    @staticmethod
    def circle(surface, color, center, radius, width=0):
        return pygame.draw.circle(
            surface,
            color,
            _scale_point(center),
            _scale_value(radius),
            _scale_value(width)
        )


draw = ScaledDraw()




# =========================================================
# PALETA DE COLORES
# =========================================================

INK = (43, 36, 43)

WALL = (132, 137, 87)
WALL_LIGHT = (157, 162, 105)
WALL_DARK = (91, 91, 59)

WOOD = (126, 75, 49)
WOOD_LIGHT = (164, 103, 66)
WOOD_DARK = (69, 42, 37)

METAL = (112, 126, 125)
METAL_LIGHT = (165, 180, 173)

GLASS = (115, 157, 165)
GLASS_LIGHT = (171, 199, 191)

TILE_A = (153, 161, 143)
TILE_B = (111, 126, 116)
TILE_LINE = (76, 91, 83)

RED = (174, 64, 57)
YELLOW = (220, 174, 76)
GREEN = (89, 145, 86)
BLUE = (77, 119, 159)
CREAM = (224, 210, 168)
WHITE = (235, 229, 199)


# =========================================================
# PARED
# =========================================================

def draw_wall(surface):

    # Fondo
    draw.rect(surface, WALL, (0, 0, 480, 70))

    # Tablillas verticales
    for x in range(0, 480, 10):

        draw.rect(
            surface, WALL_DARK,
            (x, 0, 2, 43)
        )

        draw.line(
            surface, WALL_LIGHT,
            (x + 4, 0), (x + 4, 42), 1
        )

    # Variaciones de color en la madera
    for x in range(8, 480, 23):

        draw.rect(
            surface, (117, 123, 75),
            (x, 12, 3, 8)
        )

        draw.rect(
            surface, (169, 166, 108),
            (x + 5, 29, 2, 5)
        )

    # Paneles inferiores
    draw.rect(
        surface, WOOD_DARK,
        (0, 43, 480, 26)
    )

    draw.rect(
        surface, WOOD,
        (0, 46, 480, 19)
    )

    for x in range(0, 480, 30):

        draw.rect(
            surface, WOOD_DARK,
            (x, 47, 2, 17)
        )

        draw.line(
            surface, WOOD_LIGHT,
            (x + 4, 49), (x + 26, 49), 1
        )

    # Zócalo
    draw.rect(
        surface, INK,
        (0, 66, 480, 4)
    )

    draw.rect(
        surface, WOOD_LIGHT,
        (0, 66, 480, 1)
    )

    # Puerta del personal
    draw.rect(
        surface, INK,
        (285, -2, 47, 72)
    )

    draw.rect(
        surface, WOOD_DARK,
        (290, 0, 37, 65)
    )

    draw.rect(
        surface, WOOD_LIGHT,
        (294, 3, 29, 58)
    )

    draw.rect(
        surface, WOOD_DARK,
        (298, 7, 21, 46)
    )

    draw.circle(
        surface, METAL_LIGHT,
        (320, 36), 2
    )

    # Marco superior de la puerta
    draw.rect(
        surface, WOOD_DARK,
        (284, 0, 49, 4)
    )

    # Cartel de personal
    draw.rect(
        surface, CREAM,
        (297, 9, 22, 10)
    )

    draw.rect(
        surface, WOOD_DARK,
        (297, 9, 22, 10), 1
    )

    draw.line(
        surface, WOOD_DARK,
        (301, 14), (315, 14), 1
    )


# =========================================================
# PISO
# =========================================================

def draw_floor(surface):

    tile_size = 20
    start_y = 70

    for row in range(10):

        for col in range(24):

            x = col * tile_size
            y = start_y + row * tile_size

            color = (
                TILE_A
                if (row + col) % 2 == 0
                else TILE_B
            )

            draw.rect(
                surface, color,
                (x, y, tile_size, tile_size)
            )

            draw.rect(
                surface, TILE_LINE,
                (x, y, tile_size, tile_size), 1
            )

    # Pequeñas marcas en algunas baldosas
    for x, y in [
        (45, 105), (110, 142), (270, 190),
        (320, 235), (235, 90), (430, 190)
    ]:

        draw.rect(
            surface, (133, 143, 127),
            (x, y, 3, 2)
        )


# =========================================================
# REFRIGERADORES
# =========================================================

def draw_fridge(surface, x, y, w, h, accent=RED):

    # Sombra
    draw.rect(
        surface, INK,
        (x + 3, y + 3, w, h)
    )

    # Estructura exterior
    draw.rect(
        surface, WOOD_DARK,
        (x, y, w, h)
    )

    draw.rect(
        surface, METAL,
        (x + 2, y + 2, w - 4, h - 4)
    )

    # Parte superior
    draw.rect(
        surface, WOOD_DARK,
        (x + 2, y + 2, w - 4, 12)
    )

    draw.rect(
        surface, accent,
        (x + 4, y + 4, w - 8, 8)
    )

    # Ventilación
    draw.rect(
        surface, METAL_LIGHT,
        (x + w - 15, y + 5, 8, 6)
    )

    for i in range(3):

        draw.line(
            surface, METAL,
            (x + w - 14, y + 7 + i * 2),
            (x + w - 8, y + 7 + i * 2), 1
        )

    # Cristal
    glass_y = y + 16
    glass_h = h - 20

    draw.rect(
        surface, WOOD_DARK,
        (x + 4, glass_y, w - 8, glass_h)
    )

    draw.rect(
        surface, GLASS,
        (x + 6, glass_y + 2, w - 12, glass_h - 4)
    )

    # División de puertas
    draw.line(
        surface, WOOD_DARK,
        (x + w // 2, glass_y),
        (x + w // 2, glass_y + glass_h), 2
    )

    # Estantes
    for row in range(1, 4):

        sy = glass_y + row * (glass_h // 4)

        draw.line(
            surface, METAL_LIGHT,
            (x + 6, sy),
            (x + w - 6, sy), 2
        )

    # Productos
    product_colors = [RED, GREEN, YELLOW, BLUE, CREAM]

    for row in range(3):

        for col in range(4):

            px = x + 9 + col * 10
            py = glass_y + 5 + row * 11

            color = product_colors[(row + col) % len(product_colors)]

            draw.rect(
                surface, WOOD_DARK,
                (px, py, 7, 9)
            )

            draw.rect(
                surface, color,
                (px + 1, py + 1, 5, 7)
            )

            draw.rect(
                surface, WHITE,
                (px + 2, py + 3, 3, 2)
            )

    # Reflejos del cristal
    draw.line(
        surface, GLASS_LIGHT,
        (x + 9, glass_y + 4),
        (x + 9, glass_y + 19), 2
    )


# =========================================================
# CONGELADOR LATERAL
# =========================================================

def draw_side_freezer(surface):

    x, y, w, h = 0, 87, 23, 145

    draw.rect(
        surface, INK,
        (x, y, w, h)
    )

    draw.rect(
        surface, METAL,
        (x + 2, y + 2, w - 4, h - 4)
    )

    # Compartimentos
    for i in range(3):

        sy = y + 5 + i * 45

        draw.rect(
            surface, WOOD_DARK,
            (x + 3, sy, w - 6, 40)
        )

        draw.rect(
            surface, GLASS,
            (x + 5, sy + 2, w - 10, 36)
        )

        draw.line(
            surface, GLASS_LIGHT,
            (x + 7, sy + 5),
            (x + 7, sy + 28), 1
        )


# =========================================================
# ESTANTERÍAS
# =========================================================

def draw_gondola(surface, x, y, w, h, variant=0):

    # Sombra
    draw.rect(
        surface, INK,
        (x + 4, y + 4, w, h)
    )

    # Estructura
    draw.rect(
        surface, WOOD_DARK,
        (x, y, w, h)
    )

    draw.rect(
        surface, WOOD,
        (x + 3, y + 3, w - 6, h - 6)
    )

    # Cabecera superior
    draw.rect(
        surface, WOOD_DARK,
        (x + 2, y + 2, w - 4, 14)
    )

    draw.rect(
        surface, WOOD_LIGHT,
        (x + 4, y + 4, w - 8, 9)
    )

    # Separadores
    columns = 3

    for i in range(1, columns):

        sx = x + i * (w // columns)

        draw.rect(
            surface, WOOD_DARK,
            (sx - 1, y + 17, 3, h - 21)
        )

    # Filas de productos
    product_colors = [
        RED, GREEN, YELLOW, BLUE,
        CREAM, METAL_LIGHT
    ]

    rows = 3

    for row in range(rows):

        for col in range(columns * 3):

            px = x + 7 + col * ((w - 16) // (columns * 3))
            py = y + 21 + row * ((h - 27) // rows)

            color = product_colors[
                (row + col + variant) % len(product_colors)
            ]

            if (row + col) % 2 == 0:

                draw.rect(
                    surface, WOOD_DARK,
                    (px, py, 7, 9)
                )

                draw.rect(
                    surface, color,
                    (px + 1, py + 1, 5, 7)
                )

                draw.rect(
                    surface, WHITE,
                    (px + 2, py + 3, 3, 2)
                )

            else:

                draw.rect(
                    surface, color,
                    (px, py + 2, 6, 7)
                )

                draw.rect(
                    surface, WOOD_DARK,
                    (px, py + 2, 6, 7), 1
                )

    # Bordes frontales
    draw.line(
        surface, WOOD_LIGHT,
        (x + 3, y + h - 4),
        (x + w - 3, y + h - 4), 2
    )


# =========================================================
# ESTANTERÍA CONTRA LA PARED
# =========================================================

def draw_back_shelves(surface):

    x, y, w, h = 338, 7, 138, 61

    draw.rect(
        surface, INK,
        (x + 3, y + 3, w, h)
    )

    draw.rect(
        surface, WOOD_DARK,
        (x, y, w, h)
    )

    draw.rect(
        surface, WOOD,
        (x + 3, y + 3, w - 6, h - 6)
    )

    # Tres niveles
    for row in range(3):

        sy = y + 8 + row * 17

        draw.rect(
            surface, WOOD_DARK,
            (x + 5, sy + 13, w - 10, 3)
        )

        for col in range(7):

            px = x + 9 + col * 17

            draw.rect(
                surface, WOOD_DARK,
                (px, sy, 10, 12)
            )

            color = [
                RED, BLUE, YELLOW, GREEN
            ][(row + col) % 4]

            draw.rect(
                surface, color,
                (px + 1, sy + 1, 8, 10)
            )


# =========================================================
# MOSTRADOR
# =========================================================

def draw_counter(surface):

    x, y, w, h = 337, 111, 130, 53

    # Sombra
    draw.rect(
        surface, INK,
        (x + 4, y + 5, w, h)
    )

    # Frente del mostrador
    draw.rect(
        surface, WOOD_DARK,
        (x, y + 13, w, h - 13)
    )

    draw.rect(
        surface, WOOD,
        (x + 3, y + 16, w - 6, h - 20)
    )

    # Paneles frontales
    for px in [x + 8, x + 42, x + 76, x + 110]:

        draw.rect(
            surface, WOOD_DARK,
            (px, y + 20, 26, 25)
        )

        draw.line(
            surface, WOOD_LIGHT,
            (px + 3, y + 23),
            (px + 23, y + 23), 1
        )

    # Superficie superior
    draw.rect(
        surface, WOOD_DARK,
        (x - 3, y, w + 6, 17)
    )

    draw.rect(
        surface, WOOD_LIGHT,
        (x, y + 2, w, 12)
    )

    # Bordes de la superficie
    draw.line(
        surface, CREAM,
        (x + 2, y + 3),
        (x + w - 2, y + 3), 1
    )

    # Caja registradora
    draw.rect(
        surface, WOOD_DARK,
        (x + 85, y - 9, 28, 12)
    )

    draw.rect(
        surface, METAL,
        (x + 88, y - 7, 22, 8)
    )

    draw.rect(
        surface, BLUE,
        (x + 91, y - 5, 16, 4)
    )

    # Balanza
    draw.rect(
        surface, WOOD_DARK,
        (x + 14, y - 8, 20, 12)
    )

    draw.rect(
        surface, METAL_LIGHT,
        (x + 16, y - 7, 16, 7)
    )

    draw.circle(
        surface, CREAM,
        (x + 24, y - 4), 4
    )

    draw.line(
        surface, RED,
        (x + 24, y - 4),
        (x + 27, y - 6), 1
    )


# =========================================================
# ESCENA COMPLETA
# =========================================================

def draw_interior_background(surface):

    # Piso y paredes
    draw_floor(surface)
    draw_wall(surface)

    # Refrigeradores
    draw_fridge(surface, 21, 8, 60, 64, RED)
    draw_fridge(surface, 84, 8, 60, 64, RED)
    draw_fridge(surface, 164, 12, 65, 60, METAL)

    # Congelador lateral
    draw_side_freezer(surface)

    # Estanterías de pared
    draw_back_shelves(surface)

    # Góndolas centrales
    draw_gondola(surface, 58, 96, 151, 78, 0)
    draw_gondola(surface, 73, 179, 143, 72, 2)

    # Mostrador
    draw_counter(surface)

    # Detalles del suelo y sombras
    draw.rect(
        surface, INK,
        (0, 265, 480, 5)
    )

# =========================================================
# AJUSTES DE PERSPECTIVA (640x360)
#
# Se conservan arriba todas las funciones originales del modulo.
# Estas definiciones sustituyen solo el dibujo de los elementos
# de la escena: tapas superiores, frentes sin costados, soportes
# del estante y base apoyada del mostrador.
# =========================================================

WOOD_TOP = (181, 125, 78)
METAL_DARK = (73, 88, 87)

def draw_wall(surface):
    """Pared trasera de madera. Se dibuja directamente en 640x360."""

    # Madera superior
    pygame.draw.rect(surface, WALL, (0, 0, 640, 96))

    # Tablillas verticales
    for x in range(0, 640, 16):
        pygame.draw.rect(surface, WALL_DARK, (x, 0, 2, 61))
        pygame.draw.line(surface, WALL_LIGHT, (x + 5, 0), (x + 5, 60), 1)

    # Detalles y variaciones de tono
    for x in range(9, 640, 31):
        pygame.draw.rect(surface, (117, 123, 75), (x, 13 + (x % 3), 4, 9))
        pygame.draw.rect(surface, (169, 166, 108), (x + 9, 39, 3, 6))

    # Paneles de madera inferiores
    pygame.draw.rect(surface, WOOD_DARK, (0, 61, 640, 34))
    pygame.draw.rect(surface, WOOD, (0, 65, 640, 27))

    for x in range(0, 640, 34):
        pygame.draw.line(surface, WOOD_DARK, (x, 66), (x, 91), 2)
        pygame.draw.line(surface, WOOD_LIGHT, (x + 5, 69), (x + 27, 69), 1)

    # La pared termina en y=96. No se dibuja una línea extra sobre el piso.


def draw_floor(surface):
    """Piso de baldosas cuadradas visto desde arriba."""

    tile_size = 32
    floor_top = FLOOR_TOP

    pygame.draw.rect(surface, TILE_A, (0, floor_top, 640, 360 - floor_top))

    rows = (360 - floor_top + tile_size - 1) // tile_size
    cols = (640 + tile_size - 1) // tile_size

    for row in range(rows):
        for col in range(cols):
            x = col * tile_size
            y = floor_top + row * tile_size
            color = TILE_A if (row + col) % 2 == 0 else TILE_B

            pygame.draw.rect(surface, color, (x, y, tile_size, tile_size))
            pygame.draw.rect(surface, TILE_LINE, (x, y, tile_size, tile_size), 1)

    # Marcas discretas en algunas baldosas
    for x, y in [
        (285, 132), (340, 292), (300, 235),
        (625, 160), (270, 330), (350, 110)
    ]:
        pygame.draw.rect(surface, (133, 143, 127), (x, y, 4, 2))


def fridge_bottle_slots(w, h):
    """Posiciones (rel_x, rel_y, repisa) de las botellas dentro del refri.

    Coordenadas relativas a la esquina superior del refrigerador.
    """
    glass_x, glass_y = 5, 12 + 15
    glass_w, glass_h = w - 10, h - 20
    divider_x = glass_x + glass_w // 2
    slots = []
    for row in range(3):
        shelf_y = glass_y + 2 + row * 11
        if shelf_y + 10 > glass_y + glass_h - 2:
            continue
        px = glass_x + 6
        while px + 4 < glass_x + glass_w - 3:
            # Dejar libre el marco central de las puertas.
            if not (divider_x - 5 <= px + 2 <= divider_x + 3):
                slots.append((px, shelf_y, row))
            px += 6
    return slots


def draw_fridge(surface, x, y, w, h, accent=RED, draw_products=True):
    """Refrigerador sin costado: tapa superior y frente con puertas."""

    top_h = 12
    front_y = y + top_h

    # Sombra corta, justo debajo de la base
    pygame.draw.rect(surface, (49, 35, 34), (x + 4, front_y + h, w - 8, 2))

    # Tapa superior visible
    pygame.draw.rect(surface, WOOD_DARK, (x, y, w, top_h + 2))
    pygame.draw.rect(surface, METAL_LIGHT, (x + 3, y + 2, w - 6, top_h - 1))
    pygame.draw.line(surface, WHITE, (x + 5, y + 3), (x + w - 6, y + 3), 1)

    # Frente
    pygame.draw.rect(surface, WOOD_DARK, (x, front_y, w, h))
    pygame.draw.rect(surface, METAL, (x + 3, front_y + 3, w - 6, h - 6))

    # Franja superior / marca
    pygame.draw.rect(surface, WOOD_DARK, (x + 4, front_y + 3, w - 8, 9))
    pygame.draw.rect(surface, accent, (x + 6, front_y + 5, w - 12, 5))

    # Puertas de cristal
    glass_x = x + 5
    glass_y = front_y + 15
    glass_w = w - 10
    glass_h = h - 20

    pygame.draw.rect(surface, WOOD_DARK, (glass_x, glass_y, glass_w, glass_h))
    pygame.draw.rect(surface, GLASS, (glass_x + 2, glass_y + 2, glass_w - 4, glass_h - 4))

    pygame.draw.line(
        surface, WOOD_DARK,
        (glass_x + glass_w // 2, glass_y + 1),
        (glass_x + glass_w // 2, glass_y + glass_h - 1), 2
    )

    # Repisas. Las botellas son objetos movibles (ver TableObjectManager);
    # solo se dibujan aquí cuando el refri se usa como decoración.
    for rel_y in sorted({sy for _, sy, _ in fridge_bottle_slots(w, h)}):
        pygame.draw.line(
            surface, METAL_LIGHT,
            (glass_x + 3, y + rel_y + 10),
            (glass_x + glass_w - 3, y + rel_y + 10), 1
        )

    if draw_products:
        seed = (x // 40) % 5
        for rel_x, rel_y, row in fridge_bottle_slots(w, h):
            dibujar_botella(surface, x + rel_x, y + rel_y, seed + row)

    # Reflejo y tiradores
    pygame.draw.line(
        surface, GLASS_LIGHT,
        (glass_x + 5, glass_y + 4),
        (glass_x + 5, glass_y + glass_h - 5), 2
    )
    pygame.draw.rect(surface, METAL_LIGHT, (x + w // 2 - 2, glass_y + 5, 2, 13))
    pygame.draw.rect(surface, METAL_LIGHT, (x + w // 2 + 3, glass_y + 5, 2, 13))


def draw_gondola(surface, x, y, w, h, variant=0, draw_products=True):
    """Góndola baja sin costado, con productos en la tapa superior."""

    front_h = 24
    top_depth = h - front_h
    front_y = y + top_depth

    # Sombra muy corta bajo el mueble, sin desplazarlo visualmente
    pygame.draw.rect(surface, (49, 35, 34), (x + 4, front_y + front_h, w - 8, 2))

    # Frente del mueble
    pygame.draw.rect(surface, WOOD_DARK, (x, front_y, w, front_h))
    pygame.draw.rect(surface, WOOD, (x + 3, front_y + 3, w - 6, front_h - 6))

    panel_count = max(2, w // 52)
    panel_w = (w - 16) // panel_count
    for i in range(panel_count):
        px = x + 6 + i * panel_w
        pygame.draw.rect(
            surface, WOOD_DARK,
            (px, front_y + 5, panel_w - 5, max(5, front_h - 10))
        )
        pygame.draw.line(
            surface, WOOD_LIGHT,
            (px + 3, front_y + 8),
            (px + panel_w - 9, front_y + 8), 1
        )

    # Tapa superior vista desde arriba
    pygame.draw.rect(surface, WOOD_DARK, (x, y, w, top_depth + 2))
    pygame.draw.rect(surface, WOOD_LIGHT, (x + 3, y + 3, w - 6, top_depth - 2))

    for yy in (y + 10, y + 22):
        if yy < front_y - 2:
            pygame.draw.line(surface, WOOD_TOP if 'WOOD_TOP' in globals() else CREAM,
                             (x + 5, yy), (x + w - 5, yy), 1)

    if draw_products:
        # Productos vistos desde arriba
        product_colors = [RED, GREEN, YELLOW, BLUE, CREAM, (133, 91, 139)]
        columns = max(2, (w - 18) // 19)

        for row in range(2):
            for col in range(columns):
                px = x + 8 + col * 18
                py = y + 7 + row * 15
                color = product_colors[(row + col + variant) % len(product_colors)]

                if (row + col + variant) % 3 == 0:
                    pygame.draw.circle(surface, WOOD_DARK, (px + 5, py + 5), 5)
                    pygame.draw.circle(surface, color, (px + 5, py + 5), 4)
                    pygame.draw.circle(surface, CREAM, (px + 4, py + 4), 1)
                else:
                    pygame.draw.rect(surface, WOOD_DARK, (px, py, 11, 10))
                    pygame.draw.rect(surface, color, (px + 1, py + 1, 9, 8))
                    pygame.draw.line(surface, CREAM, (px + 3, py + 3), (px + 8, py + 3), 1)


    # Borde frontal de la tapa
    pygame.draw.rect(surface, WOOD_LIGHT, (x + 2, front_y - 3, w - 4, 4))
    pygame.draw.line(surface, CREAM, (x + 5, front_y - 2), (x + w - 5, front_y - 2), 1)


def draw_back_shelves(surface):
    """Estantería trasera fijada a la pared, con soportes hasta el suelo."""

    x, y, w, h = 316, 34, 292, 42
    top_h = 10
    front_y = y + top_h

    # Tapa superior
    pygame.draw.rect(surface, WOOD_DARK, (x, y, w, top_h))
    pygame.draw.rect(surface, WOOD_LIGHT, (x + 3, y + 2, w - 6, top_h - 3))

    # Cuerpo frontal
    pygame.draw.rect(surface, WOOD_DARK, (x, front_y, w, h))
    pygame.draw.rect(surface, WOOD, (x + 3, front_y + 3, w - 6, h - 6))

    # Repisas
    for row in range(1, 3):
        sy = front_y + row * (h // 3)
        pygame.draw.rect(surface, WOOD_DARK, (x + 3, sy, w - 6, 3))
        pygame.draw.line(surface, WOOD_LIGHT, (x + 5, sy + 1), (x + w - 5, sy + 1), 1)

    # Los productos de este estante (abarrotes) son objetos que se pueden
    # tomar: los dibuja TableObjectManager, no el fondo.

    # Soportes visibles: la estantería queda anclada, no suspendida.
    for sx in (x + 18, x + w - 25):
        pygame.draw.rect(surface, WOOD_DARK, (sx, front_y + h, 5, 18))
        pygame.draw.rect(surface, WOOD_LIGHT, (sx + 1, front_y + h, 2, 16))


# ---------------------------------------------------------
# CANASTOS DE LAS GÓNDOLAS: uno por cada fruta o verdura
# ---------------------------------------------------------
CANASTO_COLUMNAS, CANASTO_FILAS = 3, 2
MIMBRE = (186, 132, 74)
MIMBRE_CLARO = (220, 172, 104)
MIMBRE_OSCURO = (112, 72, 40)
MIMBRE_FONDO = (92, 58, 34)


def gondola_canastos(w, n):
    """Rectángulos (rel_x, rel_y, ancho, alto) de los n canastos de una góndola."""
    separacion = 4
    ancho = (w - 8 - (n - 1) * separacion) // n
    return [(4 + i * (ancho + separacion), 2, ancho, 32) for i in range(n)]


def canasto_slots(w, n, indice, item_w, item_h):
    """Huecos (rel_x, rel_y) para un producto dentro de su canasto."""
    cx, cy, cw, _ = gondola_canastos(w, n)[indice]
    paso = max(12, min(13, (cw - 6) // CANASTO_COLUMNAS))
    izquierda = cx + (cw - paso * CANASTO_COLUMNAS) // 2
    return [
        (izquierda + col * paso + (paso - item_w) // 2,
         cy + 4 + fila * 13 + (12 - item_h))
        for fila in range(CANASTO_FILAS) for col in range(CANASTO_COLUMNAS)
    ]


def draw_canastos_fondo(surface, x, y, w, n):
    """Cuerpo de cada canasto (se dibuja antes que las frutas)."""
    for cx, cy, cw, ch in gondola_canastos(w, n):
        r = pygame.Rect(x + cx, y + cy, cw, ch)
        pygame.draw.rect(surface, MIMBRE_OSCURO, r)
        pygame.draw.rect(surface, MIMBRE_FONDO, r.inflate(-4, -4))
        # Tejido del fondo
        for yy in range(r.top + 4, r.bottom - 2, 4):
            pygame.draw.line(surface, (108, 70, 40), (r.left + 3, yy), (r.right - 4, yy), 1)
        # Bordes laterales con su tejido
        for lado in (r.left, r.right - 3):
            pygame.draw.rect(surface, MIMBRE, (lado, r.top, 3, ch))
            for yy in range(r.top + 1, r.bottom, 3):
                pygame.draw.line(surface, MIMBRE_CLARO, (lado, yy), (lado + 2, yy), 1)
        # Borde trasero
        pygame.draw.rect(surface, MIMBRE, (r.left, r.top, cw, 3))
        pygame.draw.line(surface, MIMBRE_CLARO, (r.left + 1, r.top), (r.right - 2, r.top), 1)


def draw_canastos_frente(surface, x, y, w, n):
    """Borde delantero de cada canasto, por encima de las frutas."""
    for cx, cy, cw, ch in gondola_canastos(w, n):
        r = pygame.Rect(x + cx, y + cy + ch - 5, cw, 6)
        pygame.draw.rect(surface, MIMBRE_OSCURO, r.inflate(0, 2).move(0, 1))
        pygame.draw.rect(surface, MIMBRE, r)
        pygame.draw.line(surface, MIMBRE_CLARO, (r.left + 1, r.top), (r.right - 2, r.top), 1)
        # Trenzado del borde
        for xx in range(r.left + 1, r.right - 2, 4):
            pygame.draw.line(surface, MIMBRE_CLARO, (xx, r.top + 2), (xx + 2, r.bottom - 2), 1)
            pygame.draw.line(surface, MIMBRE_OSCURO, (xx + 2, r.top + 2), (xx, r.bottom - 2), 1)


# Huevera: 5 columnas x 4 filas = 20 huevos.
HUEVERA_COLUMNAS, HUEVERA_FILAS = 5, 4


def huevera_slots():
    """(rel_x, rel_y) de cada hueco de la huevera, relativo al mueble."""
    return [(4 + col * 8, 4 + fila * 9)
            for fila in range(HUEVERA_FILAS) for col in range(HUEVERA_COLUMNAS)]


def draw_huevera(surface, x, y, w, h):
    """Mesita con una bandeja de cartón para 20 huevos."""
    front_h = 22
    top_depth = h - front_h
    front_y = y + top_depth
    pygame.draw.rect(surface, (49, 35, 34), (x + 3, front_y + front_h, w - 6, 2))
    # Tapa
    pygame.draw.rect(surface, WOOD_DARK, (x, y, w, top_depth + 2))
    pygame.draw.rect(surface, WOOD_LIGHT, (x + 2, y + 2, w - 4, top_depth - 2))
    # Bandeja de cartón con sus hoyitos
    pygame.draw.rect(surface, (150, 124, 90), (x + 2, y + 3, w - 4, top_depth - 4))
    pygame.draw.rect(surface, (214, 192, 150), (x + 3, y + 4, w - 6, top_depth - 6))
    for rx, ry in huevera_slots():
        pygame.draw.ellipse(surface, (176, 150, 108), (x + rx - 1, y + ry + 3, 9, 6))
    # Frente
    pygame.draw.rect(surface, WOOD_DARK, (x, front_y, w, front_h))
    pygame.draw.rect(surface, WOOD, (x + 3, front_y + 3, w - 6, front_h - 6))
    pygame.draw.rect(surface, CREAM, (x + 8, front_y + 6, w - 16, 9))
    for i in range(3):  # tres huevitos pintados en el letrero
        pygame.draw.ellipse(surface, (250, 240, 216), (x + 12 + i * 8, front_y + 7, 5, 7))
        pygame.draw.ellipse(surface, (176, 150, 108), (x + 12 + i * 8, front_y + 7, 5, 7), 1)
    base_y = front_y + front_h - 5
    pygame.draw.rect(surface, WOOD_DARK, (x + 2, base_y, w - 4, 5))


# Heladera: 4 columnas x 4 filas = 16 helados (8 de paleta y 8 de cono).
HELADERA_COLUMNAS, HELADERA_FILAS = 4, 4
HELADERA_FRENTE = 22


def heladera_slots():
    """(rel_x, rel_y, fila) de cada lugar de la heladera, relativo al mueble."""
    return [(5 + col * 10, 4 + fila * 11, fila)
            for fila in range(HELADERA_FILAS) for col in range(HELADERA_COLUMNAS)]


def heladera_surtido(fila):
    """Las dos filas de arriba son de paleta; las de abajo, de cono."""
    return HELADOS[0] if fila < HELADERA_FILAS // 2 else HELADOS[1]


def draw_heladera(surface, x, y, w, h):
    """Congelador horizontal blanco con tapa de vidrio escarchado."""
    front_h = HELADERA_FRENTE
    top_depth = h - front_h
    front_y = y + top_depth
    blanco, gris, azul_hielo, azul = (236, 240, 244), (150, 160, 170), (196, 226, 242), (70, 120, 170)
    pygame.draw.rect(surface, (49, 35, 34), (x + 3, front_y + front_h, w - 6, 2))
    # Tapa (marco blanco y vidrio)
    pygame.draw.rect(surface, gris, (x, y, w, top_depth + 2))
    pygame.draw.rect(surface, blanco, (x + 1, y + 1, w - 2, top_depth))
    pygame.draw.rect(surface, azul_hielo, (x + 3, y + 3, w - 6, top_depth - 5))
    # Separación entre paletas (arriba) y conos (abajo)
    medio = y + 3 + (top_depth - 5) // 2
    pygame.draw.line(surface, (160, 196, 220), (x + 4, medio), (x + w - 5, medio), 1)
    # Frente
    pygame.draw.rect(surface, gris, (x, front_y, w, front_h))
    pygame.draw.rect(surface, blanco, (x + 2, front_y + 2, w - 4, front_h - 5))
    pygame.draw.rect(surface, azul, (x + 6, front_y + 6, w - 12, 9))
    # Letrerito con una paleta y un cono pintados
    cx = x + w // 2
    pygame.draw.rect(surface, (246, 120, 160), (cx - 9, front_y + 7, 4, 5))
    pygame.draw.rect(surface, (230, 200, 150), (cx - 8, front_y + 12, 2, 3))
    pygame.draw.circle(surface, (250, 160, 190), (cx + 6, front_y + 9), 3)
    pygame.draw.polygon(surface, (226, 160, 90), [(cx + 3, front_y + 10), (cx + 9, front_y + 10),
                                                  (cx + 6, front_y + 15)])
    pygame.draw.rect(surface, gris, (x + 2, front_y + front_h - 4, w - 4, 3))


def draw_heladera_vidrio(surface, x, y, w, h):
    """Brillo del vidrio por encima de los helados."""
    top_depth = h - HELADERA_FRENTE
    brillo = pygame.Surface((w - 6, top_depth - 5), pygame.SRCALPHA)
    for i in range(0, w + top_depth, 14):
        pygame.draw.line(brillo, (255, 255, 255, 60), (i, 0), (i - top_depth, top_depth), 2)
    surface.blit(brillo, (x + 3, y + 3))


def draw_counter(surface, x=378, y=164, w=210, draw_props=True):
    """Mostrador sin costado, con cubierta superior y base apoyada."""

    top_depth = 40
    front_h = 24
    front_y = y + top_depth

    # Cubierta superior
    pygame.draw.rect(surface, WOOD_DARK, (x, y, w, top_depth + 3))
    pygame.draw.rect(surface, WOOD_LIGHT, (x + 4, y + 4, w - 8, top_depth - 4))

    for yy in (y + 16, y + 30):
        pygame.draw.line(surface, WOOD, (x + 8, yy), (x + w - 8, yy), 1)

    # Frente del mostrador
    pygame.draw.rect(surface, WOOD_DARK, (x, front_y, w, front_h))
    pygame.draw.rect(surface, WOOD, (x + 4, front_y + 4, w - 8, front_h - 8))

    for px in range(x + 12, x + w - 18, 28):
        pygame.draw.line(surface, WOOD_DARK,
                         (px, front_y + 5), (px, front_y + front_h - 5), 2)
        pygame.draw.line(surface, WOOD_LIGHT,
                         (px + 3, front_y + 7), (px + 3, front_y + front_h - 7), 1)

    # Zócalo/base que toca el suelo
    base_y = front_y + front_h - 6
    pygame.draw.rect(surface, WOOD_DARK, (x + 2, base_y, w - 4, 6))
    pygame.draw.line(surface, WOOD_LIGHT, (x + 5, base_y + 1), (x + w - 5, base_y + 1), 1)
    # Sombra mínima justo debajo de la base, sin hueco aparente
    pygame.draw.rect(surface, (49, 35, 34), (x + 8, front_y + front_h, w - 16, 2))

    if draw_props:
        # Balanza
        pygame.draw.rect(surface, WOOD_DARK, (x + 18, y + 11, 29, 25))
        pygame.draw.rect(surface, METAL_LIGHT, (x + 21, y + 13, 23, 19))
        pygame.draw.ellipse(surface, CREAM, (x + 25, y + 16, 15, 12))
        pygame.draw.line(surface, RED, (x + 32, y + 22), (x + 37, y + 18), 1)

        # Caja registradora
        pygame.draw.rect(surface, WOOD_DARK, (x + 166, y + 8, 29, 25))
        pygame.draw.rect(surface, METAL, (x + 169, y + 11, 23, 19))
        pygame.draw.rect(surface, BLUE, (x + 172, y + 14, 17, 8))
        for row in range(2):
            for col in range(3):
                pygame.draw.rect(surface, CREAM, (x + 173 + col * 6, y + 24 + row * 4, 4, 3))

        # Papel y lápiz
        pygame.draw.polygon(surface, CREAM,
                            [(x + 104, y + 8), (x + 132, y + 11),
                             (x + 128, y + 38), (x + 100, y + 35)])
        for yy in (y + 16, y + 22, y + 28):
            pygame.draw.line(surface, METAL_DARK, (x + 106, yy), (x + 125, yy + 2), 1)
        pygame.draw.line(surface, RED, (x + 139, y + 13), (x + 153, y + 35), 3)


def draw_interior_background(surface):
    """Escena interior 640x360. Conserva el resto de funciones del módulo."""

    # Fondo base
    draw_floor(surface)
    draw_wall(surface)

    # Refrigeradores alineados contra la pared y apoyados en el piso
    draw_fridge(surface, 24, 34, 82, 58, RED)
    draw_fridge(surface, 112, 34, 82, 58, RED)
    draw_fridge(surface, 200, 34, 82, 58, METAL)

    # Estantería derecha fijada a la pared
    draw_back_shelves(surface)

    # Góndolas centrales, con superficie superior visible
    draw_gondola(surface, 28, 157, 208, 66, 0)
    draw_gondola(surface, 45, 260, 190, 60, 2)

    # Mostrador apoyado sobre el suelo
    draw_counter(surface)




# =========================================================
# ESCENA BASE Y MUEBLES REORGANIZABLES
# =========================================================

def draw_interior_background(surface):
    """Dibuja los elementos fijos: piso, pared y estantería mural."""
    with paleta("piso"):
        draw_floor(surface)
    with paleta("paredes"):
        draw_wall(surface)
    with paleta("muebles"):
        draw_back_shelves(surface)


class FurnitureManager:
    """Permite levantar y reubicar muebles del local."""

    MOVE_SPEED = 125.0
    PICKUP_DISTANCE = 46.0
    LATERAL_TOLERANCE = 38.0
    GRID_SIZE = 4

    def __init__(self):
        self.items = [
            {
                "id": "fridge_1", "label": "REFRIGERADOR",
                "kind": "fridge", "x": 24.0, "y": 34.0,
                "w": 82, "h": 70, "body_h": 58, "accent": RED,
                "min_y": 24,
            },
            {
                "id": "fridge_2", "label": "REFRIGERADOR",
                "kind": "fridge", "x": 112.0, "y": 34.0,
                "w": 82, "h": 70, "body_h": 58, "accent": RED,
                "min_y": 24,
            },
            {
                "id": "fridge_3", "label": "REFRIGERADOR",
                "kind": "fridge", "x": 200.0, "y": 34.0,
                "w": 82, "h": 70, "body_h": 58, "accent": METAL,
                "min_y": 24,
            },
            {
                "id": "gondola_1", "label": "GONDOLA",
                "kind": "gondola", "x": 28.0, "y": 157.0,
                "w": 208, "h": 60, "variant": 0,
                "min_y": 96,
            },
            {
                "id": "gondola_2", "label": "GONDOLA",
                "kind": "gondola", "x": 28.0, "y": 260.0,
                "w": 208, "h": 60, "variant": 2,
                "min_y": 96,
            },
            {
                "id": "counter", "label": "MOSTRADOR",
                "kind": "counter", "x": 378.0, "y": 164.0,
                "w": 210, "h": 64, "min_y": 96,
            },
            {
                # Huevera para 20 huevos, a la par del mostrador.
                "id": "huevera", "label": "HUEVERA",
                "kind": "huevera", "x": 330.0, "y": 164.0,
                "w": 46, "h": 64, "min_y": 96,
            },
            {
                # Heladera en L con el mostrador: baja desde la huevera.
                "id": "heladera", "label": "HELADERA",
                "kind": "heladera", "x": 330.0, "y": 232.0,
                "w": 46, "h": 70, "min_y": 96,
            },
            {
                # Estante de la pared (pintado en el fondo). Es fijo: no se
                # mueve con SHIFT+E, pero sus productos se toman y se reponen.
                "id": "abarrotes", "label": "ABARROTES",
                "kind": "abarrotes", "x": 316.0, "y": 34.0,
                "w": 292, "h": 52, "min_y": 24, "fijo": True,
            },
        ]
        self.selected = None
        self._ya_tocaba = set()

    @property
    def carrying(self):
        return self.selected

    @staticmethod
    def _rect(item):
        return pygame.Rect(
            round(item["x"]), round(item["y"]), item["w"], item["h"]
        )

    @staticmethod
    def _front_geometry(item):
        """Devuelve el borde trasero y la profundidad del frente vertical."""
        if item["kind"] == "fridge":
            # La tapa superior del refrigerador mide 12 px.
            return item["y"] + 12, item["body_h"]

        if item["kind"] == "gondola":
            # La tapa superior es transitable; solo bloquea el frente de 24 px.
            front_h = 24
            return item["y"] + item["h"] - front_h, front_h

        if item["kind"] == "counter":
            # El mostrador tiene una cubierta de 48 px y un frente de 24 px.
            front_h = 24
            return item["y"] + 40, front_h

        if item["kind"] in ("huevera", "heladera"):
            front_h = 22
            return item["y"] + item["h"] - front_h, front_h

        return item["y"], item["h"]

    def get_collision_rects(self):
        """Construye el perímetro de colisión desde el borde trasero al frontal."""
        collision_rects = []

        for item in self.items:
            x = round(item["x"])
            y = round(item["y"])
            w = item["w"]

            if item["kind"] == "fridge":
                # Los refrigeradores conservan su colisión completa.
                collision_rects.append(
                    pygame.Rect(
                        x, round(y + 12), w, item["body_h"]
                    )
                )
                continue

            if item["kind"] not in ("gondola", "counter", "huevera", "heladera"):
                continue

            front_y, front_h = self._front_geometry(item)
            front_y = round(front_y)
            bottom_y = round(front_y + front_h)

            # Borde trasero: 20 px antes del inicio del frente.
            back_stop_y = front_y - 20

            # Perímetro: borde trasero, laterales y borde delantero.
            collision_rects.append(
                pygame.Rect(x, back_stop_y, w, 1)
            )
            collision_rects.append(
                pygame.Rect(x, bottom_y, w, 1)
            )

            # Los laterales comienzan exactamente en el borde trasero.
            side_height = bottom_y - back_stop_y
            collision_rects.append(
                pygame.Rect(x - 1, back_stop_y, 1, side_height + 1)
            )
            collision_rects.append(
                pygame.Rect(x + w, back_stop_y, 1, side_height + 1)
            )

        return collision_rects

    def find_target(self, player):
        """Busca un mueble cercano y situado delante del personaje."""
        facing = {
            "up": (0, -1), "down": (0, 1),
            "left": (-1, 0), "right": (1, 0),
        }
        fx, fy = facing.get(player.direction, (0, 1))
        anchor_x = float(player.x)
        anchor_y = float(player.y) - 18.0
        candidates = []

        for item in self.items:
            if item.get("fijo"):
                continue  # el estante de la pared no se mueve
            rect = self._rect(item)
            closest_x = max(rect.left, min(anchor_x, rect.right))
            closest_y = max(rect.top, min(anchor_y, rect.bottom))
            vx = closest_x - anchor_x
            vy = closest_y - anchor_y
            distance = math.hypot(vx, vy)
            forward = vx * fx + vy * fy
            lateral = abs(vx * fy - vy * fx)

            if (
                distance <= self.PICKUP_DISTANCE
                and forward >= -3
                and lateral <= self.LATERAL_TOLERANCE
            ):
                candidates.append((distance, item))

        return min(candidates, key=lambda entry: entry[0])[1] if candidates else None

    # Personajes que un mueble no puede tapar: el juego asigna una función
    # que devuelve [(nombre, rectángulo de los pies), ...].
    personajes = staticmethod(lambda: [])

    def _choques(self, rect):
        return {nombre for nombre, pies in self.personajes() if pies.colliderect(rect)}

    def try_pickup(self, player):
        if self.selected is not None:
            return False
        target = self.find_target(player)
        if target is None:
            return False
        self.selected = target
        # Si al levantarlo ya tocaba a alguien (p. ej. al jugador), no cuenta.
        self._ya_tocaba = self._choques(self._rect(target))
        return True

    def drop(self):
        """Coloca el mueble. False si quedaría encima de un personaje."""
        if self.selected is None:
            return False
        item = self.selected
        antes = (item["x"], item["y"])
        item["x"] = round(item["x"] / self.GRID_SIZE) * self.GRID_SIZE
        item["y"] = round(item["y"] / self.GRID_SIZE) * self.GRID_SIZE
        self._clamp_item(item)
        if self._choques(self._rect(item)) - self._ya_tocaba:
            item["x"], item["y"] = antes
            return False
        self.selected = None
        return True

    @staticmethod
    def _clamp_item(item):
        item["x"] = max(4, min(640 - item["w"] - 4, item["x"]))
        min_y = item.get("min_y", 96)
        item["y"] = max(min_y, min(360 - item["h"] - 4, item["y"]))

    def update(self, dt, keys):
        """Las flechas o WASD mueven el mueble seleccionado."""
        if self.selected is None:
            return

        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx == 0 and dy == 0:
            return

        length = math.hypot(dx, dy)
        dx /= length
        dy /= length
        item = self.selected
        # Se mueve por eje, para que se deslice junto a un personaje sin
        # pasarle por encima.
        for eje, paso in (("x", dx), ("y", dy)):
            if not paso:
                continue
            antes = item[eje]
            item[eje] += paso * self.MOVE_SPEED * dt
            self._clamp_item(item)
            choques = self._choques(self._rect(item))
            if choques - self._ya_tocaba:
                item[eje] = antes          # habría quedado encima de alguien
            else:
                self._ya_tocaba &= choques

    @staticmethod
    def _draw_item(surface, item):
        with paleta(parte_de_mueble(item["kind"])):
            FurnitureManager._draw_item_sin_paleta(surface, item)

    @staticmethod
    def _draw_item_sin_paleta(surface, item):
        x, y = round(item["x"]), round(item["y"])
        if item["kind"] == "fridge":
            draw_fridge(surface, x, y, item["w"], item["body_h"], item["accent"],
                        draw_products=False)
        elif item["kind"] == "gondola":
            draw_gondola(surface, x, y, item["w"], item["h"], item["variant"], draw_products=False)
            n = len(TableObjectManager.GONDOLA_STOCK.get(item["id"], FRUTAS))
            draw_canastos_fondo(surface, x, y, item["w"], n)
        elif item["kind"] == "counter":
            draw_counter(surface, x, y, item["w"], draw_props=False)
        elif item["kind"] == "huevera":
            draw_huevera(surface, x, y, item["w"], item["h"])
        elif item["kind"] == "heladera":
            draw_heladera(surface, x, y, item["w"], item["h"])

    @staticmethod
    def _draw_after_objects(surface, item):
        """Lo que va por encima de los productos: el borde de los canastos."""
        if item["kind"] == "gondola":
            n = len(TableObjectManager.GONDOLA_STOCK.get(item["id"], FRUTAS))
            draw_canastos_frente(surface, round(item["x"]), round(item["y"]), item["w"], n)
        elif item["kind"] == "heladera":
            draw_heladera_vidrio(surface, round(item["x"]), round(item["y"]), item["w"], item["h"])

    def _draw_front_overlay(self, surface, item):
        """Dibuja únicamente el frente del mueble por encima del personaje."""
        x = round(item["x"])
        y = round(item["y"])

        if item["kind"] == "gondola":
            front_h = 24
            top_depth = item["h"] - front_h
            front_y = y + top_depth

            # Panel frontal.
            pygame.draw.rect(
                surface, WOOD_DARK,
                (x, front_y, item["w"], front_h)
            )
            pygame.draw.rect(
                surface, WOOD,
                (x + 3, front_y + 3, item["w"] - 6, front_h - 6)
            )

            panel_count = max(2, item["w"] // 52)
            panel_w = (item["w"] - 16) // panel_count

            for i in range(panel_count):
                px = x + 6 + i * panel_w
                pygame.draw.rect(
                    surface, WOOD_DARK,
                    (px, front_y + 5, panel_w - 5, front_h - 10)
                )
                pygame.draw.line(
                    surface, WOOD_LIGHT,
                    (px + 3, front_y + 8),
                    (px + panel_w - 9, front_y + 8), 1
                )

            # Borde de la tapa, también por encima del personaje.
            pygame.draw.rect(
                surface, WOOD_LIGHT,
                (x + 2, front_y - 3, item["w"] - 4, 4)
            )
            pygame.draw.line(
                surface, CREAM,
                (x + 5, front_y - 2),
                (x + item["w"] - 5, front_y - 2), 1
            )

        elif item["kind"] == "counter":
            front_h = 24
            front_y = y + 40

            # Panel frontal del mostrador.
            pygame.draw.rect(
                surface, WOOD_DARK,
                (x, front_y, item["w"], front_h)
            )
            pygame.draw.rect(
                surface, WOOD,
                (x + 4, front_y + 4, item["w"] - 8, front_h - 8)
            )

            for px in range(x + 12, x + item["w"] - 18, 28):
                pygame.draw.line(
                    surface, WOOD_DARK,
                    (px, front_y + 5),
                    (px, front_y + front_h - 5), 2
                )
                pygame.draw.line(
                    surface, WOOD_LIGHT,
                    (px + 3, front_y + 7),
                    (px + 3, front_y + front_h - 7), 1
                )

            # Zócalo inferior.
            base_y = front_y + front_h - 6
            pygame.draw.rect(
                surface, WOOD_DARK,
                (x + 2, base_y, item["w"] - 4, 6)
            )
            pygame.draw.line(
                surface, WOOD_LIGHT,
                (x + 5, base_y + 1),
                (x + item["w"] - 5, base_y + 1), 1
            )

    def draw_world(self, surface, player, object_manager=None, extras=()):
        """Dibuja las mesas por encima del personaje cuando este está detrás."""
        ordered_items = sorted(
            self.items,
            key=lambda item: item["y"] + item["h"]
        )

        # 1. Dibujar todos los muebles y los objetos de sus superficies.
        for item in ordered_items:
            self._draw_item(surface, item)
            if object_manager is not None:
                object_manager.draw_table_objects(surface, item)
            self._draw_after_objects(surface, item)

        # 2. Dibujar el personaje (y el carrito) por orden de profundidad.
        actores = sorted([player, *extras], key=lambda a: a.y)
        for actor in actores:
            if actor is player:
                player.draw(surface)
            else:
                actor.dibujar(surface, "interior")

        # 3. Si el personaje está detrás o dentro de la profundidad de una
        #    mesa, volver a dibujar la mesa completa por encima del sprite.
        player_left = player.x - player.WIDTH / 2
        player_right = player.x + player.WIDTH / 2

        for item in ordered_items:
            if item["kind"] not in ("gondola", "counter", "huevera", "heladera"):
                continue

            item_left = item["x"]
            item_right = item["x"] + item["w"]
            item_back = item["y"]
            item_front = item["y"] + item["h"]

            overlaps_x = (
                player_right > item_left
                and player_left < item_right
            )
            detras = overlaps_x and player.y <= item_front
            for extra in extras:
                if (extra.x + extra.WIDTH / 2 > item_left and extra.x - extra.WIDTH / 2 < item_right
                        and extra.y <= item_front):
                    detras = True

            # Mientras los pies no hayan sobrepasado el borde delantero,
            # la mesa y sus productos se dibujan encima del personaje.
            if detras:
                self._draw_item(surface, item)
                if object_manager is not None:
                    object_manager.draw_table_objects(surface, item)
                self._draw_after_objects(surface, item)
                # Quien está DELANTE de esta mesa vuelve a quedar encima
                # (si no, el pulpero se vería "debajo" del mostrador cuando
                # Canela o Tavo pasan por detrás).
                for actor in actores:
                    ancho = getattr(actor, "WIDTH", 16) / 2
                    if (actor.y > item_front and actor.x + ancho > item_left
                            and actor.x - ancho < item_right):
                        if actor is player:
                            player.draw(surface)
                        else:
                            actor.dibujar(surface, "interior")

        if self.selected is not None:
            highlight = self._rect(self.selected).inflate(6, 6)
            pygame.draw.rect(surface, CREAM, highlight, 2)
            pygame.draw.rect(surface, WOOD_DARK, highlight.inflate(2, 2), 1)

        if object_manager is not None:
            object_manager.draw_carried(surface, player)



# =========================================================
# OBJETOS QUE SE PUEDEN MOVER SOBRE LAS SUPERFICIES
# =========================================================

class TableObjectManager:
    """Permite recoger y reubicar productos y utensilios de las mesas."""

    # Nombres y precios salen de productos.py.
    PRODUCT_PRICES = {tipo: datos[2] for tipo, datos in PRODUCTOS.items()}
    PRODUCT_NAMES = {tipo: datos[0] for tipo, datos in PRODUCTOS.items()}

    # Qué vende cada góndola: la de arriba frutas, la de abajo verduras.
    GONDOLA_STOCK = {
        "gondola_1": FRUTAS,
        "gondola_2": VERDURAS,
    }

    MAX_MANOS = 3
    MENSAJE_MANOS_LLENAS = (
        "¡Uy! Tus manos ya están llenas.",
        "Lleva estos 3 productos al mostrador.",
    )

    MOVE_SPEED = 105.0
    PICKUP_DISTANCE = 42.0
    LATERAL_TOLERANCE = 30.0
    GRID_SIZE = 2

    PRODUCT_COLORS = [RED, GREEN, YELLOW, BLUE, CREAM, (133, 91, 139)]

    def __init__(self, furniture_manager):
        self.items = []
        self.selected = None
        # Productos que el personaje lleva en las manos (máximo MAX_MANOS).
        # Si empuja el carrito, "mano" es lo que va en el carrito (hasta 8).
        self.mano = []
        self.en_carrito = False
        # Nombre del niño o niña, para mensajes más personales.
        self.nombre = ""
        # Globito de diálogo temporal sobre el personaje.
        self.aviso = None
        self.aviso_tiempo = 0.0
        self._create_gondola_products(furniture_manager)
        self._create_fridge_products(furniture_manager)
        self._create_abarrotes_products(furniture_manager)
        self._create_huevera_products(furniture_manager)
        self._create_heladera_products(furniture_manager)
        self._create_counter_props()

    def _create_gondola_products(self, furniture_manager):
        """Crea un objeto independiente por cada producto visible."""
        for table in furniture_manager.items:
            if table["kind"] != "gondola":
                continue

            stock = self.GONDOLA_STOCK.get(table["id"], FRUTAS)
            # Un canasto por cada fruta o verdura, con 6 piezas cada uno.
            for indice, kind in enumerate(stock):
                w, h = tamano(kind)
                slots = canasto_slots(table["w"], len(stock), indice, w, h)
                for n, (rel_x, rel_y) in enumerate(slots):
                    self.items.append({
                        "id": f'{table["id"]}_{kind}_{n}',
                        "label": self.PRODUCT_NAMES[kind],
                        "kind": kind,
                        "table_id": table["id"],
                        "rel_x": rel_x,
                        "rel_y": rel_y,
                        "w": w,
                        "h": h,
                        "color": CREAM,
                        "price": self.PRODUCT_PRICES[kind],
                    })

    def _create_fridge_products(self, furniture_manager):
        """Cada botella del refrigerador es un objeto independiente."""
        for table in furniture_manager.items:
            if table["kind"] != "fridge":
                continue

            seed = (round(table["x"]) // 40) % 5
            surtido = self.FRIDGE_STOCK.get(table["id"])
            for rel_x, rel_y, row in fridge_bottle_slots(
                table["w"], table["body_h"]
            ):
                if surtido:
                    kind = surtido[row % len(surtido)]
                else:
                    kind = BEBIDAS[(seed + row) % len(BEBIDAS)]
                w, h = tamano(kind)
                self.items.append({
                    "id": f'{table["id"]}_bottle_{rel_x}_{rel_y}',
                    "label": self.PRODUCT_NAMES[kind],
                    "kind": kind,
                    "table_id": table["id"],
                    "rel_x": rel_x,
                    "rel_y": rel_y,
                    "w": w,
                    "h": h,
                    "color": CREAM,
                    "price": self.PRODUCT_PRICES[kind],
                })

    # Refri de la derecha: solo leches y aguas (una repisa de cada una).
    FRIDGE_STOCK = {"fridge_3": ["leche", "agua", "leche"]}

    # Repisas del estante de abarrotes: 12 columnas x 2 filas.
    ABARROTES_FILAS = [
        ["harina"] * 6 + ["azucar"] * 6,
        ["arroz"] * 6 + ["frijoles"] * 6,
    ]

    def _create_huevera_products(self, furniture_manager):
        table = next((t for t in furniture_manager.items if t["kind"] == "huevera"), None)
        if table is None:
            return
        w, h = tamano("huevos")
        for n, (rx, ry) in enumerate(huevera_slots()):
            self.items.append({
                "id": f"huevera_{n}", "label": self.PRODUCT_NAMES["huevos"],
                "kind": "huevos", "table_id": table["id"],
                "rel_x": rx, "rel_y": ry, "w": w, "h": h,
                "color": CREAM, "price": self.PRODUCT_PRICES["huevos"],
            })

    def _create_heladera_products(self, furniture_manager):
        table = next((t for t in furniture_manager.items if t["kind"] == "heladera"), None)
        if table is None:
            return
        for n, (rx, ry, fila) in enumerate(heladera_slots()):
            kind = heladera_surtido(fila)
            w, h = tamano(kind)
            self.items.append({
                "id": f"heladera_{n}", "label": self.PRODUCT_NAMES[kind],
                "kind": kind, "table_id": table["id"],
                "rel_x": rx + (7 - w) // 2, "rel_y": ry + (9 - h), "w": w, "h": h,
                "color": CREAM, "price": self.PRODUCT_PRICES[kind],
            })

    @staticmethod
    def _slot_abarrotes(fila, col, w, h):
        return 9 + col * 23 + (12 - w) // 2, 15 + fila * 13 + (12 - h)

    def _create_abarrotes_products(self, furniture_manager):
        table = next((t for t in furniture_manager.items if t["kind"] == "abarrotes"), None)
        if table is None:
            return
        for fila, tipos in enumerate(self.ABARROTES_FILAS):
            for col, kind in enumerate(tipos):
                w, h = tamano(kind)
                rel_x, rel_y = self._slot_abarrotes(fila, col, w, h)
                self.items.append({
                    "id": f"abarrotes_{fila}_{col}",
                    "label": self.PRODUCT_NAMES[kind],
                    "kind": kind,
                    "table_id": table["id"],
                    "rel_x": rel_x, "rel_y": rel_y,
                    "w": w, "h": h,
                    "color": CREAM,
                    "price": self.PRODUCT_PRICES[kind],
                })

    def _create_counter_props(self):
        """La balanza, la caja, el libro de recetas y el lápiz del mostrador."""
        props = [
            {
                "id": "counter_scale", "label": "BALANZA",
                "kind": "scale", "rel_x": 4, "rel_y": 7,
                "w": 29, "h": 25,
            },
            {
                "id": "counter_register", "label": "CAJA",
                "kind": "register", "rel_x": 177, "rel_y": 6,
                "w": 29, "h": 25,
            },
            {
                # El libro de recetas: E frente a él (o clic, o R) lo abre.
                "id": "counter_recetario", "label": "LIBRO DE RECETAS",
                "kind": "recetario", "rel_x": 116, "rel_y": 6,
                "w": 34, "h": 26,
            },
            {
                # Teléfono: E frente a él (o clic) abre el pedido al camión.
                "id": "counter_telefono", "label": "TELÉFONO",
                "kind": "telefono", "rel_x": 153, "rel_y": 8,
                "w": 22, "h": 22,
            },
        ]

        for prop in props:
            self.items.append({
                **prop,
                "table_id": "counter",
                "color": CREAM,
            })

    @property
    def carrying(self):
        return self.selected

    @staticmethod
    def _table_by_id(furniture_manager, table_id):
        for table in furniture_manager.items:
            if table["id"] == table_id:
                return table
        return None

    def _position(self, item, furniture_manager):
        if item is self.selected:
            return item["x"], item["y"]

        table = TableObjectManager._table_by_id(
            furniture_manager, item["table_id"]
        )
        if table is None:
            return 0.0, 0.0

        return table["x"] + item["rel_x"], table["y"] + item["rel_y"]

    @staticmethod
    def _table_surface(table):
        """Rectángulo útil de la tapa superior de cada mesa."""
        x = round(table["x"])
        y = round(table["y"])

        if table["kind"] == "gondola":
            top_depth = table["h"] - 24
            return pygame.Rect(
                x + 3, y + 3,
                table["w"] - 6, top_depth - 5
            )

        if table["kind"] == "counter":
            top_depth = 40
            return pygame.Rect(
                x + 4, y + 4,
                table["w"] - 8, top_depth - 8
            )

        if table["kind"] in ("huevera", "heladera"):
            return pygame.Rect(x + 2, y + 2, table["w"] - 3, table["h"] - 24)

        if table["kind"] == "abarrotes":
            # Frente del estante de la pared (dos repisas).
            return pygame.Rect(x + 4, y + 12, table["w"] - 8, 30)

        if table["kind"] == "fridge":
            # Interior del vidrio: ahí se pueden volver a guardar botellas.
            return pygame.Rect(
                x + 7, y + 29,
                table["w"] - 14, table["body_h"] - 24
            )

        return None

    def find_target(self, player, furniture_manager):
        """Busca un objeto cercano y delante del personaje."""
        if self.selected is not None:
            return None

        facing = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        fx, fy = facing.get(player.direction, (0, 1))
        anchor_x, anchor_y = ancla(player, fx, fy)
        candidates = []

        for item in self.items:
            # La caja registradora y el libro de recetas son puntos de
            # interacción fijos. Lo que va en las manos tampoco se toma.
            if item["kind"] in ("register", "recetario", "telefono") or item["table_id"] in ("mano", "carrito"):
                continue

            x, y = self._position(item, furniture_manager)
            rect = pygame.Rect(round(x), round(y), item["w"], item["h"])

            closest_x = max(rect.left, min(anchor_x, rect.right))
            closest_y = max(rect.top, min(anchor_y, rect.bottom))
            vx = closest_x - anchor_x
            vy = closest_y - anchor_y
            distance = math.hypot(vx, vy)
            forward = vx * fx + vy * fy
            lateral = abs(vx * fy - vy * fx)

            if (
                distance <= self.PICKUP_DISTANCE
                and forward >= -3
                and lateral <= self.LATERAL_TOLERANCE
            ):
                candidates.append((distance, item))

        return min(candidates, key=lambda entry: entry[0])[1] if candidates else None

    def find_register_target(self, player, furniture_manager):
        """Comprueba si el jugador está frente a la caja registradora."""
        return self._punto_fijo(player, furniture_manager, "register")

    def find_recetario_target(self, player, furniture_manager):
        """Comprueba si el jugador está frente al libro de recetas."""
        return self._punto_fijo(player, furniture_manager, "recetario")

    def rect_recetario(self, furniture_manager):
        """Rectángulo del libro en el mostrador (para abrirlo con clic)."""
        for item in self.items:
            if item["kind"] == "recetario":
                x, y = self._position(item, furniture_manager)
                return pygame.Rect(round(x), round(y), item["w"], item["h"])
        return None

    def _punto_fijo(self, player, furniture_manager, kind):
        if self.selected is not None:
            return None

        facing = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        fx, fy = facing.get(player.direction, (0, 1))
        anchor_x, anchor_y = ancla(player, fx, fy)

        mejor = None
        for item in self.items:
            if item["kind"] != kind:
                continue

            x, y = self._position(item, furniture_manager)
            rect = pygame.Rect(round(x), round(y), item["w"], item["h"])

            closest_x = max(rect.left, min(anchor_x, rect.right))
            closest_y = max(rect.top, min(anchor_y, rect.bottom))
            vx = closest_x - anchor_x
            vy = closest_y - anchor_y
            distance = math.hypot(vx, vy)
            forward = vx * fx + vy * fy
            lateral = abs(vx * fy - vy * fx)

            if (
                distance <= self.PICKUP_DISTANCE + 12
                and forward >= -3
                and lateral <= self.LATERAL_TOLERANCE + 8
                and (mejor is None or distance < mejor[0])
            ):
                mejor = (distance, item)

        return mejor[1] if mejor else None

    def find_telefono_target(self, player, furniture_manager):
        return self._punto_fijo(player, furniture_manager, "telefono")

    def rect_telefono(self, furniture_manager):
        for item in self.items:
            if item["kind"] == "telefono":
                x, y = self._position(item, furniture_manager)
                return pygame.Rect(round(x), round(y), item["w"], item["h"])
        return None

    def punto_del_mostrador(self, player, furniture_manager):
        """Qué tiene enfrente en el mostrador: "recetario", "telefono",
        "register" o None (el más cercano a sus manos)."""
        ax = float(player.x)
        mejor = None
        for kind in ("recetario", "telefono", "register"):
            item = self._punto_fijo(player, furniture_manager, kind)
            if item is None:
                continue
            x, _ = self._position(item, furniture_manager)
            d = abs(x + item["w"] / 2 - ax)
            if mejor is None or d < mejor[0]:
                mejor = (d, kind, x + item["w"] / 2)
        if mejor is None:
            return None
        producto = self.find_target(player, furniture_manager)
        if producto is not None and producto["kind"] in PRODUCTOS:
            xp, _ = self._position(producto, furniture_manager)
            if abs(xp + producto["w"] / 2 - ax) < mejor[0]:
                return None
        return mejor[1]

    def mas_cerca_recetario(self, player, furniture_manager):
        """True si, frente al mostrador, el libro está más cerca que la caja."""
        libro = self.find_recetario_target(player, furniture_manager)
        if libro is None:
            return False
        ax = float(player.x)
        xl, _ = self._position(libro, furniture_manager)
        producto = self.find_target(player, furniture_manager)
        if producto is not None and producto["kind"] in PRODUCTOS:
            xp, _ = self._position(producto, furniture_manager)
            if abs(xp + producto["w"] / 2 - ax) < abs(xl + libro["w"] / 2 - ax):
                return False  # hay un producto más cerca: E lo toma
        caja = self.find_register_target(player, furniture_manager)
        if caja is None:
            return True
        xc, _ = self._position(caja, furniture_manager)
        return abs(xl + libro["w"] / 2 - ax) < abs(xc + caja["w"] / 2 - ax)

    # -----------------------------------------------------
    # LLEVAR PRODUCTOS EN LAS MANOS
    # -----------------------------------------------------
    def mensaje_manos_llenas(self, destino):
        saludo = f"¡Uy, {self.nombre}!" if self.nombre else "¡Uy!"
        if self.en_carrito:
            return (f"{saludo} El carrito ya está lleno.",
                    f"Lleva estos {self.MAX_MANOS} productos {destino}.")
        return (f"{saludo} Tus manos ya están llenas.",
                f"Lleva estos {self.MAX_MANOS} productos {destino}.")

    def texto_llevas(self):
        """'LLEVAS 2/3' en las manos o 'CARRITO 5/8' si empuja el carrito."""
        if self.en_carrito:
            return f"CARRITO {len(self.mano)}/{self.MAX_MANOS}"
        return f"LLEVAS {len(self.mano)}/{self.MAX_MANOS}"

    def avisar(self, *lineas, segundos=3.0):
        """Muestra un globito de diálogo sobre el personaje."""
        self.aviso = lineas
        self.aviso_tiempo = segundos

    def actualizar_aviso(self, dt):
        if self.aviso is not None:
            self.aviso_tiempo -= dt
            if self.aviso_tiempo <= 0:
                self.aviso = None

    @staticmethod
    def _frente(player):
        facing = {
            "up": (0, -1), "down": (0, 1),
            "left": (-1, 0), "right": (1, 0),
        }
        fx, fy = facing.get(player.direction, (0, 1))
        return (*ancla(player, fx, fy), fx, fy)

    def superficie_al_frente(self, player, furniture_manager):
        """Devuelve la mesa, góndola, refri o mostrador frente al jugador."""
        anchor_x, anchor_y, fx, fy = self._frente(player)
        mejor = None
        for table in furniture_manager.items:
            rect = self._table_surface(table)
            if rect is None:
                continue
            closest_x = max(rect.left, min(anchor_x, rect.right))
            closest_y = max(rect.top, min(anchor_y, rect.bottom))
            vx, vy = closest_x - anchor_x, closest_y - anchor_y
            distance = math.hypot(vx, vy)
            if (
                distance <= self.PICKUP_DISTANCE + 12
                and vx * fx + vy * fy >= -3
                and abs(vx * fy - vy * fx) <= self.LATERAL_TOLERANCE + 8
            ):
                if mejor is None or distance < mejor[0]:
                    mejor = (distance, table)
        return mejor[1] if mejor else None

    def tomar(self, player, furniture_manager):
        """Toma el producto de enfrente. Devuelve True si lo tomó."""
        target = self.find_target(player, furniture_manager)
        if target is None:
            return False
        if len(self.mano) >= self.MAX_MANOS:
            self.avisar(*self.mensaje_manos_llenas("al mostrador"))
            return False
        # Recordar de dónde salió, por si se devuelve (tecla Q).
        target["antes"] = (target["table_id"], target["rel_x"], target["rel_y"])
        target["table_id"] = "mano"
        self.mano.append(target)
        return True

    # -----------------------------------------------------
    # QUÉ PRODUCTO VA EN CADA MUEBLE
    # -----------------------------------------------------
    def acepta(self, table, item):
        """¿Se puede poner este producto aquí? Devuelve (bool, aviso)."""
        kind = item["kind"]
        if table["kind"] == "counter" or kind not in PRODUCTOS:
            return True, None
        if table["kind"] == "abarrotes":
            if kind in ABARROTES:
                return True, None
            return False, ("Aquí van los abarrotes:",
                           "harina, azúcar, arroz, frijoles...")
        if table["kind"] == "huevera":
            if kind in HUEVOS:
                return True, None
            return False, ("La huevera es solo",
                           "para huevos.")
        if table["kind"] == "heladera":
            if kind in HELADOS:
                return True, None
            return False, ("La heladera es solo",
                           "para helados.")
        if kind in HELADOS:
            return False, ("¡Los helados se derriten!",
                           "Van en la heladera.")
        if kind in HUEVOS:
            return False, ("Los huevos van en la huevera,",
                           "junto al mostrador.")
        if kind in ABARROTES:
            return False, ("Esto va en el estante",
                           "de abarrotes, en la pared.")
        if table["kind"] == "fridge":
            surtido = self.FRIDGE_STOCK.get(table["id"])
            if surtido is not None and kind in BEBIDAS + REFRIGERADOS:
                if kind in surtido:
                    return True, None
                return False, ("Esta refri es solo de",
                               "leches y aguas.")
            if kind in REFRIGERADOS:
                return False, ("La leche va en la refri",
                               "de leches y aguas.")
            if kind in BEBIDAS:
                return True, None
            return False, ("Las frutas y verduras no van",
                           "en la refri. ¡Busca una góndola!")
        if table["kind"] == "gondola":
            if kind in BEBIDAS + REFRIGERADOS:
                return False, ("¡Las bebidas van en la refri",
                               "para que estén bien frías!")
            stock = self.GONDOLA_STOCK.get(table["id"])
            if stock and kind not in stock:
                tipo = "frutas" if stock is FRUTAS else "verduras"
                return False, (f"Esta góndola es de {tipo}.",
                               "Busca la otra góndola.")
        return True, None

    def _huecos(self, table, item):
        """Lugares ordenados de la góndola o refri, del mismo tamaño que item."""
        x0, y0 = round(table["x"]), round(table["y"])
        if table["kind"] == "fridge":
            return [
                (x0 + rx + (4 - item["w"]) // 2, y0 + ry + (10 - item["h"]))
                for rx, ry, _ in fridge_bottle_slots(table["w"], table["body_h"])
            ]
        if table["kind"] == "huevera":
            return [(x0 + rx, y0 + ry) for rx, ry in huevera_slots()]
        if table["kind"] == "heladera":
            # Cada helado vuelve a su fila (paletas arriba, conos abajo).
            return [(x0 + rx + (7 - item["w"]) // 2, y0 + ry + (9 - item["h"]))
                    for rx, ry, fila in heladera_slots()
                    if heladera_surtido(fila) == item["kind"]]
        if table["kind"] == "abarrotes":
            return [
                (x0 + rx, y0 + ry)
                for fila in range(2) for col in range(12)
                for rx, ry in [self._slot_abarrotes(fila, col, item["w"], item["h"])]
            ]
        if table["kind"] == "gondola":
            # Cada producto vuelve a su propio canasto.
            stock = self.GONDOLA_STOCK.get(table["id"], FRUTAS)
            if item["kind"] not in stock:
                return []
            return [
                (x0 + rx, y0 + ry)
                for rx, ry in canasto_slots(table["w"], len(stock), stock.index(item["kind"]),
                                            item["w"], item["h"])
            ]
        return []

    # -----------------------------------------------------
    # MENÚ PARA ELEGIR QUÉ TOMAR
    # -----------------------------------------------------
    def opciones_mueble(self, table):
        """[(tipo, cantidad)] de productos que hay en ese mueble."""
        conteo = {}
        for o in self.items:
            if o["table_id"] == table["id"] and o["kind"] in PRODUCTOS:
                conteo[o["kind"]] = conteo.get(o["kind"], 0) + 1
        return [(k, conteo[k]) for k in PRODUCTOS if k in conteo]

    def mueble_para_elegir(self, player, furniture_manager):
        """Si E va a tomar un producto de un mueble con varios tipos,
        devuelve ese mueble para abrir el menú de elección."""
        accion, target = self._plan_e(player, furniture_manager)
        if accion != "tomar":
            return None
        table = next(
            (t for t in furniture_manager.items if t["id"] == target["table_id"]), None
        )
        if table is None or table["kind"] not in ("gondola", "fridge", "counter", "abarrotes", "huevera",
                                                   "heladera"):
            return None
        # Aunque lo más cercano sea un adorno (balanza, libreta...), si el
        # mueble tiene productos se abre la vista para elegirlos.
        if not self.opciones_mueble(table):
            return None
        return table

    def etiqueta_tomar(self, target, furniture_manager):
        table = next(
            (t for t in furniture_manager.items if t["id"] == target["table_id"]), None
        )
        if (table is not None and table["kind"] in ("gondola", "fridge", "counter", "abarrotes", "huevera",
                                                    "heladera")
                and self.opciones_mueble(table)):
            return "ELEGIR QUÉ TOMAR"
        return f"TOMAR {target['label']}"

    def tomar_item(self, item):
        """Toma exactamente ese producto (el que se eligió en la vista)."""
        if len(self.mano) >= self.MAX_MANOS:
            self.avisar(*self.mensaje_manos_llenas("al mostrador"))
            return False
        if item not in self.items or item["table_id"] == "mano":
            return False
        item["antes"] = (item["table_id"], item["rel_x"], item["rel_y"])
        item["table_id"] = "mano"
        self.mano.append(item)
        return True

    def tomar_tipo(self, player, table, kind):
        """Toma del mueble el producto de ese tipo más cercano al jugador."""
        if len(self.mano) >= self.MAX_MANOS:
            self.avisar(*self.mensaje_manos_llenas("al mostrador"))
            return False
        candidatos = [
            o for o in self.items
            if o["table_id"] == table["id"] and o["kind"] == kind
        ]
        if not candidatos:
            return False
        tx, ty = round(table["x"]), round(table["y"])
        item = min(
            candidatos,
            key=lambda o: abs(tx + o["rel_x"] + o["w"] / 2 - player.x)
        )
        item["antes"] = (item["table_id"], item["rel_x"], item["rel_y"])
        item["table_id"] = "mano"
        self.mano.append(item)
        return True

    # Cuadrícula del mostrador: entre la balanza y el libro, 3 filas de 12
    # casillas (36). Cada producto ocupa su casilla: ninguno queda escondido
    # detrás de otro. La fila del medio va corrida media casilla.
    MOSTRADOR_X = (36, 114)
    MOSTRADOR_BASES = (35, 25, 15)      # adelante, medio, atrás (dónde se apoyan)
    MOSTRADOR_COLS = 12

    def _celdas_mostrador(self):
        x0, x1 = self.MOSTRADOR_X
        paso = (x1 - x0) / self.MOSTRADOR_COLS
        celdas = []
        for fila, base in enumerate(self.MOSTRADOR_BASES):
            corrida = paso / 2 if fila == 1 else 0
            for c in range(self.MOSTRADOR_COLS):
                celdas.append((fila, c, x0 + paso * (c + 0.5) + corrida - (paso / 2 if fila == 1 and c == self.MOSTRADOR_COLS - 1 else 0), base))
        return celdas

    def _celda_de(self, o):
        """Casilla del mostrador donde está un producto."""
        cx, base = o["rel_x"] + o["w"] / 2, o["rel_y"] + o["h"]
        return min(self._celdas_mostrador(), key=lambda c: abs(c[2] - cx) + abs(c[3] - base) * 2)[:2]

    def _lugar_mostrador(self, table, item, preferido_x):
        ocupadas = {self._celda_de(o) for o in self.items
                    if o["table_id"] == table["id"] and o["kind"] in PRODUCTOS and o is not item}
        libres = [(abs(table["x"] + cx - preferido_x) + fila * 14, cx, base)
                  for fila, c, cx, base in self._celdas_mostrador() if (fila, c) not in ocupadas]
        if not libres:
            return None
        _, cx, base = min(libres)
        return round(table["x"] + cx - item["w"] / 2), round(table["y"] + base - item["h"])

    def _lugar_libre(self, table, item, preferido_x):
        """Busca dónde poner el producto, lo más cerca posible del jugador.

        En góndolas y refris primero se llenan los huecos de la cuadrícula
        original, para que el estante quede ordenado como al principio. En el
        mostrador, en su cuadrícula de 36 casillas.
        """
        if table["kind"] == "counter" and item["kind"] in PRODUCTOS:
            return self._lugar_mostrador(table, item, preferido_x)
        area = self._table_surface(table)
        # En el mostrador los productos se pueden amontonar un poco (encimarse
        # en los bordes) para que quepan pedidos grandes, como el triple de una
        # receta. Los utensilios (balanza, libro, caja) no se tapan.
        def holgura(o):
            if table["kind"] == "counter" and o["kind"] in PRODUCTOS:
                return -4
            return 2
        ocupados = [
            pygame.Rect(
                round(table["x"] + o["rel_x"]), round(table["y"] + o["rel_y"]),
                o["w"], o["h"]
            ).inflate(holgura(o), holgura(o))
            for o in self.items
            if o["table_id"] == table["id"]
        ]
        huecos = [
            (abs(x + item["w"] / 2 - preferido_x), x, y)
            for x, y in self._huecos(table, item)
            if pygame.Rect(x, y, item["w"], item["h"]).collidelist(ocupados) == -1
        ]
        if huecos:
            _, x, y = min(huecos)
            return x, y
        if table["kind"] != "counter":
            return None

        mejor = None
        for y in range(area.top, area.bottom - item["h"] + 1, 2):
            for x in range(area.left, area.right - item["w"] + 1, 2):
                rect = pygame.Rect(x, y, item["w"], item["h"])
                if rect.collidelist(ocupados) != -1:
                    continue
                costo = abs(rect.centerx - preferido_x) + abs(rect.centery - area.centery) * 0.5
                if mejor is None or costo < mejor[0]:
                    mejor = (costo, x, y)
        return None if mejor is None else (mejor[1], mejor[2])

    def _colocar(self, item, table, lugar):
        self.mano.remove(item)
        item["table_id"] = table["id"]
        item["rel_x"] = lugar[0] - round(table["x"])
        item["rel_y"] = lugar[1] - round(table["y"])
        # Ya acomodado en la tienda, es un producto más para vender.
        item.pop("origen", None)

    def dejar(self, player, furniture_manager, todos=False, solo_bodega=False):
        """Deja productos en la superficie de enfrente. Devuelve cuántos dejó."""
        table = self.superficie_al_frente(player, furniture_manager)
        if table is None or not self.mano:
            return 0
        candidatos = [
            i for i in reversed(self.mano)
            if not solo_bodega or i.get("origen") == "bodega"
        ]
        dejados = 0
        aviso = None
        for item in candidatos:
            ok, motivo = self.acepta(table, item)
            if not ok:
                aviso = aviso or motivo
                continue
            lugar = self._lugar_libre(table, item, player.x)
            if lugar is None:
                aviso = ("¡Aquí ya no cabe nada más!", "Busca otro espacio.")
                break
            self._colocar(item, table, lugar)
            dejados += 1
            if not todos:
                break
        if dejados == 0 and aviso:
            self.avisar(*aviso)
        return dejados

    def devolver(self, player, furniture_manager):
        """Tecla Q: devuelve el último producto tomado a la mesa de enfrente.

        Si es el mismo mueble de donde salió, vuelve a su lugar exacto.
        """
        if not self.mano:
            return False
        table = self.superficie_al_frente(player, furniture_manager)
        if table is None:
            self.avisar("Acércate a una mesa o estante",
                        "para devolver el producto.")
            return False
        item = self.mano[-1]
        ok, motivo = self.acepta(table, item)
        if not ok:
            self.avisar(*motivo)
            return False

        lugar = None
        antes = item.get("antes")
        if antes and antes[0] == table["id"]:
            x = round(table["x"]) + antes[1]
            y = round(table["y"]) + antes[2]
            ocupados = [
                pygame.Rect(round(table["x"] + o["rel_x"]),
                            round(table["y"] + o["rel_y"]), o["w"], o["h"])
                for o in self.items if o["table_id"] == table["id"]
            ]
            if pygame.Rect(x, y, item["w"], item["h"]).collidelist(ocupados) == -1:
                lugar = (x, y)
        if lugar is None:
            lugar = self._lugar_libre(table, item, player.x)
        if lugar is None:
            self.avisar("¡Aquí ya no cabe nada más!", "Busca otro espacio.")
            return False
        self._colocar(item, table, lugar)
        return True

    def _plan_e(self, player, furniture_manager):
        """Qué haría la tecla E ahora mismo: (accion, detalle)."""
        superficie = self.superficie_al_frente(player, furniture_manager)
        target = self.find_target(player, furniture_manager)

        # 1. Con productos en las manos, el mostrador recibe todo.
        if self.mano and superficie is not None and superficie["kind"] == "counter":
            return "mostrador", superficie
        # 2. Con las manos vacías, la caja registradora tiene prioridad.
        if not self.mano and self.find_register_target(player, furniture_manager):
            return "caja", None
        # 3. Productos traídos de la bodega: se acomodan en góndolas y refris.
        if superficie is not None and superficie["kind"] in ("gondola", "fridge", "abarrotes", "huevera",
                                                             "heladera"):
            de_bodega = [i for i in self.mano if i.get("origen") == "bodega"]
            if de_bodega:
                if any(self.acepta(superficie, i)[0] for i in de_bodega):
                    return "acomodar", superficie
                return "no_va", superficie
        # 4. Tomar el producto de enfrente.
        if target is not None:
            return ("lleno" if len(self.mano) >= self.MAX_MANOS else "tomar"), target
        # 5. Devolver un producto al estante.
        if self.mano and superficie is not None:
            return "devolver", superficie
        return None, None

    def accion_e(self, player, furniture_manager):
        """Ejecuta la tecla E. Devuelve "caja" si hay que abrir la factura."""
        accion, _ = self._plan_e(player, furniture_manager)
        if accion == "mostrador":
            self.dejar(player, furniture_manager, todos=True)
        elif accion == "caja":
            return "caja"
        elif accion in ("acomodar", "no_va"):
            self.dejar(player, furniture_manager, todos=True, solo_bodega=True)
        elif accion in ("tomar", "lleno"):
            self.tomar(player, furniture_manager)
        elif accion == "devolver":
            self.dejar(player, furniture_manager)
        return None

    def texto_e(self, player, furniture_manager):
        """Ayuda para el letrero de abajo cuando se llevan productos."""
        texto = self._texto_e(player, furniture_manager)
        if self.superficie_al_frente(player, furniture_manager) is not None:
            texto += "    Q: DEVOLVER"
        return texto

    def _texto_e(self, player, furniture_manager):
        accion, detalle = self._plan_e(player, furniture_manager)
        llevando = self.texto_llevas()
        lugar = {"gondola": "LA GONDOLA", "fridge": "LA REFRI", "abarrotes": "ABARROTES",
                 "huevera": "LA HUEVERA", "heladera": "LA HELADERA"}
        if accion == "mostrador":
            return f"{llevando}    E: DEJAR EN EL MOSTRADOR"
        if accion == "acomodar":
            return f"{llevando}    E: ACOMODAR EN {lugar[detalle['kind']]}"
        if accion == "tomar":
            return f"{llevando}    E: {self.etiqueta_tomar(detalle, furniture_manager)}"
        if self.en_carrito:
            return f"{llevando}    ESPACIO: SOLTAR CARRITO"
        if any(i.get("origen") == "bodega" for i in self.mano):
            return f"{llevando}    ACOMODALOS EN GONDOLAS Y REFRIS"
        return f"{llevando}    LLEVALOS AL MOSTRADOR"

    def draw_carried(self, surface, player=None):
        """Dibuja los productos sobre la cabeza del personaje."""
        if player is None or not self.mano or self.en_carrito:
            return  # con el carrito, van dentro del carrito
        base_y = round(player.y) - player.HEIGHT - 1
        total_w = sum(item["w"] for item in self.mano) + 2 * (len(self.mano) - 1)
        x = round(player.x) - total_w // 2
        for item in self.mano:
            self._draw_object(surface, item, x, base_y - item["h"])
            x += item["w"] + 2

    def draw_aviso(self, surface, player, font):
        """Globito de diálogo encima del personaje (y de lo que carga)."""
        if not self.aviso:
            return
        textos = [font.render(linea, False, WOOD_DARK) for linea in self.aviso]
        w = max(t.get_width() for t in textos) + 14
        h = sum(t.get_height() for t in textos) + 10
        alto_carga = 0 if self.en_carrito else max((i["h"] for i in self.mano), default=0)
        bottom = round(player.y) - player.HEIGHT - alto_carga - 8
        x = max(4, min(640 - w - 4, round(player.x) - w // 2))
        y = max(4, bottom - h)
        caja = pygame.Rect(x, y, w, h)
        cola_x = max(caja.left + 8, min(caja.right - 8, round(player.x)))
        pygame.draw.rect(surface, (35, 27, 27), caja.move(2, 2))
        pygame.draw.polygon(surface, WOOD_DARK,
                            [(cola_x - 5, caja.bottom - 1), (cola_x + 5, caja.bottom - 1),
                             (cola_x, caja.bottom + 6)])
        pygame.draw.rect(surface, CREAM, caja)
        pygame.draw.rect(surface, WOOD_DARK, caja, 2)
        pygame.draw.polygon(surface, CREAM,
                            [(cola_x - 3, caja.bottom - 2), (cola_x + 3, caja.bottom - 2),
                             (cola_x, caja.bottom + 3)])
        ty = y + 5
        for t in textos:
            surface.blit(t, (x + 7, ty))
            ty += t.get_height()

    def get_counter_sale_summary(self):
        """Resume únicamente los productos vendibles colocados en el mostrador."""
        products = [
            item for item in self.items
            if (
                item["table_id"] == "counter"
                and item["kind"] in self.PRODUCT_PRICES
            )
        ]

        groups = []
        for kind in PRODUCTOS:
            matching = [item for item in products if item["kind"] == kind]
            if not matching:
                continue

            unit_price = self.PRODUCT_PRICES[kind]
            quantity = len(matching)
            groups.append({
                "kind": kind,
                # Singular si es uno ("1 Banano"), plural si son varios.
                "label": (
                    PRODUCTOS[kind][0].capitalize()
                    if quantity == 1 else PRODUCTOS[kind][1]
                ),
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": quantity * unit_price,
            })

        return {
            "items": products,
            "groups": groups,
            "count": len(products),
            "total": sum(group["subtotal"] for group in groups),
        }

    def charge_counter(self):
        """Cobra y retira del mostrador todos los productos vendibles."""
        summary = self.get_counter_sale_summary()
        sold_ids = {item["id"] for item in summary["items"]}

        if sold_ids:
            self.items = [
                item for item in self.items
                if item["id"] not in sold_ids
            ]

        return summary

    def try_pickup(self, player, furniture_manager):
        if self.selected is not None:
            return False

        target = self.find_target(player, furniture_manager)
        if target is None:
            return False

        x, y = self._position(target, furniture_manager)
        target["x"] = float(x)
        target["y"] = float(y)
        self.selected = target
        return True

    def drop(self, furniture_manager):
        """Coloca el objeto sobre cualquier mesa; si no, vuelve a su sitio."""
        if self.selected is None:
            return False

        item = self.selected
        x = round(item["x"] / self.GRID_SIZE) * self.GRID_SIZE
        y = round(item["y"] / self.GRID_SIZE) * self.GRID_SIZE

        # Se exige que el objeto completo quede dentro de la superficie.
        for table in furniture_manager.items:
            surface = self._table_surface(table)
            if surface is None:
                continue

            object_rect = pygame.Rect(x, y, item["w"], item["h"])
            if (
                object_rect.left >= surface.left
                and object_rect.top >= surface.top
                and object_rect.right <= surface.right
                and object_rect.bottom <= surface.bottom
            ):
                item["table_id"] = table["id"]
                item["rel_x"] = x - table["x"]
                item["rel_y"] = y - table["y"]
                self.selected = None
                return True

        # Si se suelta fuera de una mesa, recupera su última posición válida.
        self.selected = None
        return False

    def update(self, dt, keys):
        """Mueve el objeto seleccionado con flechas o WASD."""
        if self.selected is None:
            return

        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx == 0 and dy == 0:
            return

        length = math.hypot(dx, dy)
        dx /= length
        dy /= length

        self.selected["x"] += dx * self.MOVE_SPEED * dt
        self.selected["y"] += dy * self.MOVE_SPEED * dt

        self.selected["x"] = max(
            0, min(640 - self.selected["w"], self.selected["x"])
        )
        self.selected["y"] = max(
            0, min(360 - self.selected["h"], self.selected["y"])
        )

    @staticmethod
    def _draw_object(surface, item, x, y):
        x, y = round(x), round(y)
        kind = item["kind"]

        if kind in PRODUCTOS:
            dibujar_producto(surface, kind, x, y)

        elif kind == "box":
            color = item["color"]
            pygame.draw.rect(surface, WOOD_DARK, (x, y, 11, 10))
            pygame.draw.rect(surface, color, (x + 1, y + 1, 9, 8))
            pygame.draw.line(
                surface, CREAM, (x + 3, y + 3), (x + 8, y + 3), 1
            )

        elif kind == "can":
            color = item["color"]
            pygame.draw.circle(surface, WOOD_DARK, (x + 5, y + 5), 5)
            pygame.draw.circle(surface, color, (x + 5, y + 5), 4)
            pygame.draw.circle(surface, CREAM, (x + 4, y + 4), 1)

        elif kind == "scale":
            pygame.draw.rect(surface, WOOD_DARK, (x, y, 29, 25))
            pygame.draw.rect(surface, METAL_LIGHT, (x + 3, y + 2, 23, 19))
            pygame.draw.ellipse(surface, CREAM, (x + 7, y + 5, 15, 12))
            pygame.draw.line(
                surface, RED, (x + 14, y + 11), (x + 19, y + 7), 1
            )

        elif kind == "register":
            pygame.draw.rect(surface, WOOD_DARK, (x, y, 29, 25))
            pygame.draw.rect(surface, METAL, (x + 3, y + 3, 23, 19))
            pygame.draw.rect(surface, BLUE, (x + 6, y + 6, 17, 8))
            for row in range(2):
                for col in range(3):
                    pygame.draw.rect(
                        surface, CREAM,
                        (x + 7 + col * 6, y + 16 + row * 4, 4, 3)
                    )

        elif kind == "recetario":
            # Libro de recetas abierto sobre el mostrador.
            x, y = round(x), round(y)
            pygame.draw.rect(surface, (58, 24, 24), (x, y + 1, 34, 25))
            pygame.draw.rect(surface, (150, 52, 44), (x + 1, y, 32, 24))
            pygame.draw.rect(surface, (246, 234, 204), (x + 3, y + 2, 13, 19))
            pygame.draw.rect(surface, (246, 234, 204), (x + 18, y + 2, 13, 19))
            pygame.draw.line(surface, (196, 176, 136), (x + 16, y + 2), (x + 16, y + 21), 2)
            # Dibujito del platillo y renglones
            pygame.draw.ellipse(surface, (196, 128, 62), (x + 5, y + 5, 9, 6))
            pygame.draw.line(surface, (226, 226, 220), (x + 5, y + 11), (x + 13, y + 11), 1)
            for yy in (y + 14, y + 17):
                pygame.draw.line(surface, METAL_DARK, (x + 5, yy), (x + 13, yy), 1)
            for yy in (y + 5, y + 8, y + 11, y + 14, y + 17):
                pygame.draw.line(surface, METAL_DARK, (x + 20, yy), (x + 29, yy), 1)
            # Cinta marcadora
            pygame.draw.rect(surface, (214, 64, 52), (x + 25, y + 21, 3, 5))

        elif kind == "telefono":
            # Teléfono de disco, rojo, sobre el mostrador.
            x, y = round(x), round(y)
            pygame.draw.rect(surface, (58, 24, 24), (x, y + 8, 22, 14))
            pygame.draw.rect(surface, (190, 52, 44), (x + 1, y + 8, 20, 12))
            pygame.draw.circle(surface, (236, 226, 200), (x + 11, y + 14), 4)
            pygame.draw.circle(surface, (58, 24, 24), (x + 11, y + 14), 4, 1)
            pygame.draw.circle(surface, (58, 24, 24), (x + 11, y + 14), 1)
            # Auricular
            pygame.draw.rect(surface, (58, 24, 24), (x - 1, y + 2, 24, 7))
            pygame.draw.rect(surface, (214, 70, 58), (x, y + 3, 22, 4))
            pygame.draw.rect(surface, (150, 40, 34), (x, y + 6, 5, 3))
            pygame.draw.rect(surface, (150, 40, 34), (x + 17, y + 6, 5, 3))

    def draw_table_objects(self, surface, table):
        """Dibuja los objetos apoyados en la mesa correspondiente."""
        objetos = [i for i in self.items if i is not self.selected and i["table_id"] == table["id"]]
        if table["kind"] == "counter":
            # Primero la fila de atrás: los de adelante tapan solo su base.
            objetos.sort(key=lambda i: i["rel_y"] + i["h"])
        for item in objetos:
            x = table["x"] + item["rel_x"]
            y = table["y"] + item["rel_y"]
            self._draw_object(surface, item, x, y)


# =========================================================
# COLORES ELEGIDOS (OPCIONES > AJUSTES VISUALES)
# =========================================================
# Cada parte tiene una lista de colores; el primero es el original.
OPCIONES_COLOR = {
    "paredes": [("ORIGINAL", None), ("AZUL CIELO", (118, 158, 190)), ("ROSADO", (198, 142, 152)),
                ("AMARILLO", (204, 178, 96)), ("MENTA", (120, 180, 158)), ("LILA", (158, 138, 190)),
                ("BLANCO", (208, 204, 188))],
    "piso": [("ORIGINAL", None), ("BLANCO Y NEGRO", (236, 236, 232)), ("MADERA", (176, 128, 84)),
             ("CREMA", (206, 196, 172)),
             ("TERRACOTA", (186, 112, 82)), ("AZULEJO AZUL", (120, 150, 182)), ("VERDE", (122, 162, 112))],
    "alfombras": [("ORIGINAL", None), ("ROJA", (160, 60, 52)), ("AZUL", (62, 92, 150)),
                  ("VERDE", (70, 122, 72)), ("MORADA", (112, 72, 132))],
    "mesa": [("ORIGINAL", None), ("MADERA CLARA", (186, 140, 96)), ("ROJA", (160, 64, 52)),
             ("AZUL", (70, 100, 150)), ("VERDE", (82, 132, 82)), ("BLANCA", (206, 200, 186))],
    "refris": [("ORIGINAL", None), ("ROJA", (190, 64, 56)), ("AZUL", (70, 110, 170)),
               ("VERDE", (80, 150, 100)), ("AMARILLA", (210, 170, 70)), ("BLANCA", (222, 222, 214))],
    "muebles": [("ORIGINAL", None), ("MADERA CLARA", (186, 140, 96)), ("ROJA", (160, 64, 52)),
                ("AZUL", (70, 100, 150)), ("VERDE", (82, 132, 82)), ("BLANCA", (206, 200, 186))],
}
# Más colores para cada parte.
OPCIONES_COLOR["paredes"] += [("DURAZNO", (214, 160, 124)), ("CELESTE", (150, 190, 214)),
                              ("VERDE LIMÓN", (170, 196, 110)), ("TURQUESA", (96, 170, 170)),
                              ("GRIS", (150, 150, 150)), ("TERRACOTA", (176, 110, 86))]
OPCIONES_COLOR["piso"] += [("ROSADO", (206, 160, 170)), ("LILA", (160, 146, 190)),
                           ("AMARILLO", (210, 190, 120)), ("GRIS", (150, 152, 156))]
OPCIONES_COLOR["alfombras"] += [("ROSADA", (190, 100, 130)), ("AMARILLA", (196, 160, 60)),
                                ("NARANJA", (196, 110, 50)), ("TURQUESA", (60, 140, 140)),
                                ("GRIS", (110, 110, 116))]
OPCIONES_COLOR["mesa"] += [("NEGRA", (60, 56, 60)), ("ROSADA", (186, 110, 130)),
                           ("MORADA", (112, 80, 140)), ("AMARILLA", (196, 160, 70))]
OPCIONES_COLOR["refris"] += [("ROSADA", (210, 120, 150)), ("MORADA", (130, 90, 170)),
                             ("NARANJA", (220, 130, 60)), ("NEGRA", (60, 60, 66)),
                             ("TURQUESA", (60, 170, 170))]
OPCIONES_COLOR["muebles"] += [("NEGRA", (60, 56, 60)), ("ROSADA", (186, 110, 130)),
                              ("MORADA", (112, 80, 140)), ("AMARILLA", (196, 160, 70)),
                              ("TURQUESA", (60, 140, 140))]
COLOR_ELEGIDO = {parte: 0 for parte in OPCIONES_COLOR}

_ORIGINALES = {nombre: globals()[nombre] for nombre in (
    "WALL", "WALL_LIGHT", "WALL_DARK", "TILE_A", "TILE_B", "TILE_LINE",
    "WOOD", "WOOD_LIGHT", "WOOD_DARK", "WOOD_TOP", "METAL", "METAL_LIGHT", "METAL_DARK")}


def _mezcla(c, hacia, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c, hacia))


def _claro(c, t):
    return _mezcla(c, (255, 255, 255), t)


def _oscuro(c, t):
    return _mezcla(c, (0, 0, 0), t)


def valor_elegido(parte):
    return OPCIONES_COLOR[parte][COLOR_ELEGIDO[parte]][0]


def color_base(parte):
    return OPCIONES_COLOR[parte][COLOR_ELEGIDO[parte]][1]


def _tonos(parte):
    """Colores que cambia cada parte (None = los originales)."""
    base = color_base(parte)
    if base is None:
        return {}
    if parte == "paredes":
        return {"WALL": base, "WALL_LIGHT": _claro(base, 0.18), "WALL_DARK": _oscuro(base, 0.32)}
    if parte == "piso":
        if valor_elegido(parte) == "BLANCO Y NEGRO":
            return {"TILE_A": (236, 236, 232), "TILE_B": (36, 36, 40), "TILE_LINE": (120, 120, 124)}
        return {"TILE_A": base, "TILE_B": _oscuro(base, 0.22), "TILE_LINE": _oscuro(base, 0.42)}
    if parte in ("mesa", "muebles"):
        return {"WOOD": base, "WOOD_LIGHT": _claro(base, 0.25), "WOOD_DARK": _oscuro(base, 0.5),
                "WOOD_TOP": _claro(base, 0.35)}
    if parte == "refris":
        return {"METAL": base, "METAL_LIGHT": _claro(base, 0.35), "METAL_DARK": _oscuro(base, 0.35)}
    return {}


class paleta:
    """with paleta("mesa"): ... dibuja con los colores elegidos y luego los
    devuelve a los originales."""

    def __init__(self, *partes):
        self.partes = partes

    def __enter__(self):
        self.antes = {}
        for parte in self.partes:
            for nombre, color in _tonos(parte).items():
                self.antes.setdefault(nombre, globals()[nombre])
                globals()[nombre] = color
        return self

    def __exit__(self, *args):
        globals().update(self.antes)
        return False


def parte_de_mueble(kind):
    return {"counter": "mesa", "fridge": "refris"}.get(kind, "muebles")


def restablecer_colores():
    for parte in COLOR_ELEGIDO:
        COLOR_ELEGIDO[parte] = 0
