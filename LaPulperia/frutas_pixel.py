"""Frutas en pixel art detallado (32 x 32) para la vista de cerca.

Estilo: contorno oscuro, colores vivos en bandas de sombra (sin degradados)
y un brillo blanco arriba a la izquierda. Cada fruta se genera píxel a
píxel a partir de su forma, y se muestra escalada sin suavizar para que
los píxeles se vean nítidos.
"""
import math

import pygame

from frutas_referencia import FRUTAS_REFERENCIA

N = 32  # tamaño de la cuadrícula

CONTORNO = (42, 26, 46)
BLANCO = (255, 255, 255)

# Paletas: (borde oscuro, sombra, color base, luz)
PALETAS = {
    "manzana": ((142, 14, 30), (200, 28, 36), (255, 59, 48), (255, 122, 104)),
    "naranja": ((178, 74, 0), (226, 110, 0), (255, 149, 0), (255, 190, 84)),
    "banano": ((168, 114, 0), (224, 168, 0), (255, 204, 0), (255, 232, 110)),
    "uvas": ((76, 28, 112), (122, 52, 170), (175, 82, 222), (214, 150, 250)),
}
HOJA = ((24, 110, 46), (52, 199, 89), (132, 230, 140))
TALLO = ((88, 52, 30), (130, 84, 46))


# ---------------------------------------------------------
# AYUDANTES
# ---------------------------------------------------------
def _vacia():
    return [[None] * N for _ in range(N)]


def _sombreado(px, mascara, paleta, luz, radio):
    """Pinta la máscara en bandas de color según la distancia a la luz."""
    oscuro, sombra, base, claro = paleta
    lx, ly = luz
    for y in range(N):
        for x in range(N):
            if not mascara(x + 0.5, y + 0.5):
                continue
            d = math.hypot(x + 0.5 - lx, y + 0.5 - ly) / radio
            if d < 0.42:
                c = claro
            elif d < 0.95:
                c = base
            elif d < 1.30:
                c = sombra
            else:
                c = oscuro
            px[y][x] = c


def _borde_oscuro(px, mascara, color, desde_luz, grosor=1.0):
    """Oscurece los píxeles del borde que miran hacia abajo a la derecha."""
    for y in range(N):
        for x in range(N):
            if px[y][x] is None or not mascara(x + 0.5, y + 0.5):
                continue
            fuera = not mascara(x + 0.5 + grosor, y + 0.5 + grosor)
            if fuera and (x + y) > desde_luz:
                px[y][x] = color


def _contorno(px):
    """Contorno de 1 píxel alrededor de todo lo pintado."""
    salida = [fila[:] for fila in px]
    for y in range(N):
        for x in range(N):
            if px[y][x] is not None:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N and px[ny][nx] not in (None, CONTORNO):
                    salida[y][x] = CONTORNO
                    break
    return salida


def _pintar(px, puntos, color):
    for x, y in puntos:
        if 0 <= x < N and 0 <= y < N:
            px[y][x] = color


def _hoja(px, x0, y0, largo, inclinacion=-0.5):
    """Hoja diagonal hacia la derecha con vena clara."""
    oscura, media, clara = HOJA
    for i in range(largo):
        t = i / max(1, largo - 1)
        ancho = round(2.4 * math.sin(math.pi * t))
        cx = x0 + i
        cy = y0 + i * inclinacion
        for k in range(-ancho, ancho + 1):
            y = round(cy + k)
            if 0 <= cx < N and 0 <= y < N:
                px[y][cx] = oscura if k > 0 else media
        if 0 < i < largo - 1:
            y = round(cy)
            if 0 <= cx < N and 0 <= y < N:
                px[y][cx] = clara if t < 0.7 else media


def _tallo(px, puntos):
    oscuro, claro = TALLO
    for i, (x, y) in enumerate(puntos):
        if 0 <= x < N and 0 <= y < N:
            px[y][x] = claro if i % 2 == 0 else oscuro


# ---------------------------------------------------------
# FRUTAS
# ---------------------------------------------------------
def _manzana():
    px = _vacia()
    def dentro(x, y):
        izq = (x - 12.5) ** 2 + (y - 18) ** 2 <= 9.6 ** 2
        der = (x - 19.5) ** 2 + (y - 18) ** 2 <= 9.6 ** 2
        abajo = (x - 16) ** 2 + (y - 21) ** 2 <= 9.0 ** 2
        muesca = (x - 16) ** 2 + (y - 8.2) ** 2 <= 2.2 ** 2
        return (izq or der or abajo) and not muesca and y >= 8.6
    _sombreado(px, dentro, PALETAS["manzana"], (11, 13), 11.5)
    _borde_oscuro(px, dentro, PALETAS["manzana"][0], 30, 1.4)
    # Brillo
    _pintar(px, [(9, 13), (10, 12), (9, 14), (10, 13), (11, 12), (8, 15), (9, 15)], BLANCO)
    _pintar(px, [(12, 11), (8, 17)], PALETAS["manzana"][3])
    _tallo(px, [(16, 9), (16, 8), (16, 7), (17, 6), (17, 5), (17, 4)])
    _hoja(px, 18, 6, 8, -0.45)
    return _contorno(px)


def _naranja():
    px = _vacia()
    def dentro(x, y):
        return (x - 16) ** 2 + (y - 18.5) ** 2 <= 11.3 ** 2
    _sombreado(px, dentro, PALETAS["naranja"], (11.5, 13.5), 12.0)
    _borde_oscuro(px, dentro, PALETAS["naranja"][0], 31, 1.4)
    # Poros de la cáscara
    poros = [(14, 20), (19, 16), (21, 22), (17, 25), (12, 23), (23, 18), (18, 20), (15, 16)]
    for x, y in poros:
        if px[y][x] is not None:
            px[y][x] = PALETAS["naranja"][1] if px[y][x] != PALETAS["naranja"][3] else PALETAS["naranja"][2]
    _pintar(px, [(10, 13), (11, 12), (10, 14), (11, 13), (12, 12), (9, 15)], BLANCO)
    _pintar(px, [(13, 11)], PALETAS["naranja"][3])
    # Ombligo y hojita
    _pintar(px, [(16, 7), (16, 8)], TALLO[1])
    _hoja(px, 17, 6, 8, -0.4)
    return _contorno(px)


def _banano():
    px = _vacia()
    paleta = PALETAS["banano"]
    # Media luna inclinada: dentro del círculo A y fuera del círculo B.
    ax, ay, ar = 5.0, 5.0, 23.0
    bx, by, br = 1.0, 0.5, 22.0

    def dentro(x, y):
        en_a = (x - ax) ** 2 + (y - ay) ** 2 <= ar ** 2
        en_b = (x - bx) ** 2 + (y - by) ** 2 <= br ** 2
        return en_a and not en_b and 2 <= x <= 29 and 2 <= y <= 29

    # Sombra a lo ancho: borde exterior oscuro, centro amarillo vivo.
    oscuro, sombra, base, _ = paleta
    for y in range(N):
        for x in range(N):
            if dentro(x + 0.5, y + 0.5):
                prof = ar - math.hypot(x + 0.5 - ax, y + 0.5 - ay)
                px[y][x] = oscuro if prof < 1.0 else sombra if prof < 2.4 else base
    # Franja de luz siguiendo la curva interior.
    for y in range(N):
        for x in range(N):
            if px[y][x] is not None and not dentro(x - 1.0, y - 1.0) and dentro(x + 1.5, y + 1.5):
                px[y][x] = paleta[3]
    # Puntas café en los extremos de la curva.
    angulos = {}
    for y in range(N):
        for x in range(N):
            if px[y][x] is not None:
                angulos[(x, y)] = math.atan2(y + 0.5 - ay, x + 0.5 - ax)
    if angulos:
        amin, amax = min(angulos.values()), max(angulos.values())
        for (x, y), ang in angulos.items():
            if ang - amin < 0.07 or amax - ang < 0.07:
                px[y][x] = TALLO[0] if (x + y) % 2 else TALLO[1]
        # Tallito en la punta de arriba.
        punta = min(angulos, key=angulos.get)
        _tallo(px, [(punta[0], punta[1] - 1), (punta[0], punta[1] - 2), (punta[0] - 1, punta[1] - 3)])
    _pintar(px, [(15, 22), (16, 22), (17, 23)], BLANCO)
    return _contorno(px)


def _uvas():
    px = _vacia()
    granos = [(10, 13), (16, 12), (22, 13), (13, 18), (19, 18), (25, 18) if False else (7, 18),
              (16, 23), (10, 23), (22, 23), (13, 28), (19, 28), (16, 32) if False else (16, 28)]
    granos = [(10, 12), (16, 11), (22, 12), (7, 17), (13, 16.5), (19, 16.5), (25, 17),
              (10, 21.5), (16, 21.5), (22, 21.5), (13, 26), (19, 26)]
    paleta = PALETAS["uvas"]
    r = 3.6
    for gx, gy in sorted(granos, key=lambda g: g[1]):
        def dentro(x, y, gx=gx, gy=gy):
            return (x - gx) ** 2 + (y - gy) ** 2 <= r ** 2
        for y in range(N):
            for x in range(N):
                if dentro(x + 0.5, y + 0.5):
                    d = math.hypot(x + 0.5 - (gx - 1.2), y + 0.5 - (gy - 1.3)) / r
                    px[y][x] = paleta[3] if d < 0.45 else paleta[2] if d < 1.0 else paleta[1] if d < 1.45 else paleta[0]
        # Separación entre granos y brillo de cada uno
        for y in range(N):
            for x in range(N):
                if dentro(x + 0.5, y + 0.5) and not dentro(x + 1.5, y + 1.5):
                    px[y][x] = paleta[0]
        bx, by = round(gx - 1.6), round(gy - 1.8)
        _pintar(px, [(bx, by)], BLANCO)
    _tallo(px, [(16, 7), (16, 6), (17, 5), (17, 4), (18, 3)])
    _hoja(px, 18, 5, 8, -0.35)
    return _contorno(px)


GENERADORES = {
    "manzana": _manzana,
    "naranja": _naranja,
    "banano": _banano,
    "uvas": _uvas,
}

_cache = {}


def _desde_referencia(datos):
    """Construye la superficie desde la imagen de referencia del equipo."""
    filas, paleta = datos["filas"], datos["paleta"]
    letras = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    surf = pygame.Surface((len(filas[0]), len(filas)), pygame.SRCALPHA)
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            if ch != ".":
                surf.set_at((x, y), paleta[letras.index(ch)])
    return surf


def sprite_grande(kind):
    """Superficie con la fruta (fondo transparente).

    Manzana, banano y naranja vienen de la imagen de referencia del equipo
    (frutas_referencia.py); las uvas se generan en el mismo estilo.
    """
    if kind not in _cache and kind in FRUTAS_REFERENCIA:
        _cache[kind] = _desde_referencia(FRUTAS_REFERENCIA[kind])
    if kind not in _cache:
        px = GENERADORES[kind]()
        surf = pygame.Surface((N, N), pygame.SRCALPHA)
        for y in range(N):
            for x in range(N):
                if px[y][x] is not None:
                    surf.set_at((x, y), px[y][x])
        _cache[kind] = surf
    return _cache[kind]


def dibujar_fruta_pixel(surface, kind, rect):
    """Escala sin suavizar para mantener los píxeles nítidos."""
    rect = pygame.Rect(rect)
    base = sprite_grande(kind)
    w, h = base.get_size()
    # La misma altura visual para todas las frutas (como si midieran 32).
    lado = max(w, h, N)
    factor = min(rect.w, rect.h) / lado
    if factor >= 1:
        factor = int(factor)  # múltiplo entero: todos los píxeles iguales
    imagen = pygame.transform.scale(base, (max(1, round(w * factor)), max(1, round(h * factor))))
    surface.blit(imagen, imagen.get_rect(center=rect.center))
