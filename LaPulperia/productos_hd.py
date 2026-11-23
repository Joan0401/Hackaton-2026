"""Productos dibujados en alta calidad para la vista de cerca de los muebles.

Se dibujan con figuras suavizadas (antialias) a la resolución real de la
ventana, no a la del juego pixelado. Cada función recibe un rectángulo y
dibuja el producto centrado dentro de él.
"""
import math

import pygame
from pygame import gfxdraw

from frutas_pixel import GENERADORES as FRUTAS_PIXEL, dibujar_fruta_pixel

CONTORNO = (52, 34, 32)


# ---------------------------------------------------------
# AYUDANTES
# ---------------------------------------------------------
def _circulo(s, color, centro, radio):
    x, y, r = round(centro[0]), round(centro[1]), max(1, round(radio))
    gfxdraw.filled_circle(s, x, y, r, color)
    gfxdraw.aacircle(s, x, y, r, color)


def _circulo_borde(s, color, centro, radio, borde=None):
    """Círculo con contorno oscuro, como el pixel art del juego."""
    borde = borde if borde is not None else max(2, round(radio * 0.12))
    _circulo(s, CONTORNO, centro, radio + borde)
    _circulo(s, color, centro, radio)


def _elipse(s, color, rect):
    rect = pygame.Rect(rect)
    gfxdraw.filled_ellipse(s, rect.centerx, rect.centery, max(1, rect.w // 2), max(1, rect.h // 2), color)
    gfxdraw.aaellipse(s, rect.centerx, rect.centery, max(1, rect.w // 2), max(1, rect.h // 2), color)


def _poligono(s, color, puntos):
    puntos = [(round(x), round(y)) for x, y in puntos]
    gfxdraw.filled_polygon(s, puntos, color)
    gfxdraw.aapolygon(s, puntos, color)


def _hoja(s, centro, largo, ancho, angulo, color=(86, 160, 72), vena=(56, 112, 50)):
    """Hoja ovalada rotada (en grados)."""
    a = math.radians(angulo)
    cx, cy = centro
    puntos = []
    for i in range(24):
        t = 2 * math.pi * i / 24
        x = math.cos(t) * largo / 2
        y = math.sin(t) * ancho / 2
        puntos.append((cx + x * math.cos(a) - y * math.sin(a),
                       cy + x * math.sin(a) + y * math.cos(a)))
    _poligono(s, CONTORNO, [(cx + (px - cx) * 1.15, cy + (py - cy) * 1.25) for px, py in puntos])
    _poligono(s, color, puntos)
    pygame.draw.aaline(s, vena,
                       (cx - math.cos(a) * largo * 0.4, cy - math.sin(a) * largo * 0.4),
                       (cx + math.cos(a) * largo * 0.4, cy + math.sin(a) * largo * 0.4))


def _brillo(s, centro, radio):
    _elipse(s, (255, 255, 255, 150) if s.get_flags() & pygame.SRCALPHA else (255, 246, 230),
            pygame.Rect(centro[0] - radio * 0.55, centro[1] - radio * 0.6, radio * 0.45, radio * 0.3))


def _fruta_redonda(s, rect, claro, medio, oscuro):
    cx, cy = rect.centerx, rect.centery + rect.h * 0.05
    r = min(rect.w, rect.h) * 0.40
    _circulo_borde(s, oscuro, (cx, cy), r)
    _circulo(s, medio, (cx - r * 0.08, cy - r * 0.08), r * 0.9)
    _circulo(s, claro, (cx - r * 0.25, cy - r * 0.25), r * 0.55)
    _brillo(s, (cx, cy), r)
    return cx, cy, r


# ---------------------------------------------------------
# EFECTOS PARA FRUTAS BRILLANTES Y APETITOSAS
# ---------------------------------------------------------
def _mezcla(c1, c2, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


def _degradado3(oscuro, medio, claro, t):
    return _mezcla(oscuro, medio, t * 2) if t < 0.5 else _mezcla(medio, claro, (t - 0.5) * 2)


def _sombra(s, centro, ancho, alto):
    """Sombra suave bajo la fruta, para que se vea apoyada."""
    capa = pygame.Surface((round(ancho) + 8, round(alto) + 8), pygame.SRCALPHA)
    for i in range(4):
        r = pygame.Rect(0, 0, ancho - i * ancho * 0.12, alto - i * alto * 0.15)
        r.center = (capa.get_width() / 2, capa.get_height() / 2)
        pygame.draw.ellipse(capa, (40, 20, 10, 34), r)
    s.blit(capa, capa.get_rect(center=(round(centro[0]), round(centro[1]))))


def _volumen(s, bbox, siluetas, luz, radio, oscuro, medio, claro):
    """Rellena la silueta (lista de círculos) con un degradado continuo
    desde el punto de luz: claro cerca de la luz, oscuro en el borde."""
    bbox = pygame.Rect(bbox)
    w, h = max(1, bbox.w), max(1, bbox.h)
    degradado = pygame.Surface((w, h), pygame.SRCALPHA)
    lx, ly = luz[0] - bbox.x, luz[1] - bbox.y
    lejano = max(math.hypot(lx - x, ly - y) for x, y in ((0, 0), (w, 0), (0, h), (w, h)))
    d = lejano
    while d > 0:
        t = 1 - min(1.0, d / (radio * 1.55))
        pygame.draw.circle(degradado, (*_degradado3(oscuro, medio, claro, t), 255),
                           (round(lx), round(ly)), max(1, round(d)))
        d -= max(1.0, radio / 40)
    mascara = pygame.Surface((w, h), pygame.SRCALPHA)
    for (cx, cy), r in siluetas:
        _circulo(mascara, (255, 255, 255, 255), (cx - bbox.x, cy - bbox.y), r)
    degradado.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    s.blit(degradado, bbox.topleft)


def _reflejo_inferior(s, centro, radio, medio):
    cx, cy = centro
    capa = pygame.Surface((round(radio * 2) + 4, round(radio * 2) + 4), pygame.SRCALPHA)
    c = capa.get_width() / 2
    pygame.draw.arc(capa, (*_mezcla(medio, (255, 255, 255), 0.45), 130),
                    pygame.Rect(c - radio * 0.84, c - radio * 0.84, radio * 1.68, radio * 1.68),
                    -1.35, -0.15, max(2, round(radio * 0.09)))
    s.blit(capa, (cx - c, cy - c))


def _esfera(s, centro, radio, oscuro, medio, claro, contorno=True):
    """Esfera con volumen: borde oscuro, centro iluminado arriba a la izquierda."""
    cx, cy = centro
    if contorno:
        _circulo(s, CONTORNO, (cx, cy), radio + max(2, radio * 0.10))
    bbox = pygame.Rect(cx - radio - 2, cy - radio - 2, radio * 2 + 5, radio * 2 + 5)
    _volumen(s, bbox, [((cx, cy), radio)], (cx - radio * 0.35, cy - radio * 0.38),
             radio, oscuro, medio, claro)
    if radio >= 24:  # En tamaños pequeños el reflejo del borde solo ensucia.
        _reflejo_inferior(s, centro, radio, medio)
    _brillo_fuerte(s, (cx - radio * 0.38, cy - radio * 0.42), radio)


def _brillo_fuerte(s, centro, radio):
    """Reflejo de "recién lavada": óvalo blanco y un puntito."""
    capa = pygame.Surface((round(radio * 1.2) + 4, round(radio * 0.8) + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(capa, (255, 255, 255, 120), (0, 0, radio * 0.62, radio * 0.40))
    pygame.draw.ellipse(capa, (255, 255, 255, 230), (radio * 0.08, radio * 0.06, radio * 0.34, radio * 0.20))
    s.blit(capa, (centro[0] - radio * 0.31, centro[1] - radio * 0.20))
    _circulo(s, (255, 255, 255), (centro[0] + radio * 0.42, centro[1] + radio * 0.05), max(1, radio * 0.06))


def _destello(s, centro, tam):
    """Estrellita de brillo de 4 puntas."""
    cx, cy = centro
    capa = pygame.Surface((round(tam * 2) + 2, round(tam * 2) + 2), pygame.SRCALPHA)
    c = capa.get_width() / 2
    puntos = [(c, c - tam), (c + tam * 0.22, c - tam * 0.22), (c + tam, c), (c + tam * 0.22, c + tam * 0.22),
              (c, c + tam), (c - tam * 0.22, c + tam * 0.22), (c - tam, c), (c - tam * 0.22, c - tam * 0.22)]
    pygame.draw.polygon(capa, (255, 255, 240, 235), puntos)
    s.blit(capa, (cx - c, cy - c))


def _hoja_viva(s, centro, largo, ancho, angulo):
    _hoja(s, centro, largo, ancho, angulo, color=(92, 196, 70), vena=(50, 130, 48))
    a = math.radians(angulo)
    cx, cy = centro
    pygame.draw.line(s, (170, 236, 130),
                     (cx - math.cos(a) * largo * 0.25 - math.sin(a) * ancho * 0.18,
                      cy - math.sin(a) * largo * 0.25 + math.cos(a) * ancho * -0.18),
                     (cx + math.cos(a) * largo * 0.15 - math.sin(a) * ancho * 0.18,
                      cy + math.sin(a) * largo * 0.15 + math.cos(a) * ancho * -0.18),
                     max(2, round(ancho * 0.12)))


def _tallo(s, inicio, fin, grosor):
    pygame.draw.line(s, CONTORNO, inicio, fin, grosor + 3)
    pygame.draw.line(s, (122, 78, 44), inicio, fin, grosor)


# ---------------------------------------------------------
# FRUTAS
# ---------------------------------------------------------
def manzana(s, rect):
    cx, cy = rect.centerx, rect.centery + rect.h * 0.07
    r = min(rect.w, rect.h) * 0.37
    _sombra(s, (cx, cy + r * 0.95), r * 2.0, r * 0.45)
    lobulos = [((cx - 0.40 * r, cy), r), ((cx + 0.40 * r, cy), r),
               ((cx, cy + 0.18 * r), r * 0.92)]
    borde = max(2, r * 0.10)
    for centro, rr in lobulos:
        _circulo(s, CONTORNO, centro, rr + borde)
    bbox = pygame.Rect(cx - 1.45 * r, cy - 1.05 * r, 2.9 * r, 2.15 * r)
    _volumen(s, bbox, lobulos, (cx - r * 0.55, cy - r * 0.45), r * 1.25,
             (140, 8, 32), (232, 30, 50), (255, 128, 110))
    # Hendidura del tallo.
    _elipse(s, (150, 16, 38), pygame.Rect(cx - r * 0.20, cy - r * 0.90, r * 0.40, r * 0.24))
    _reflejo_inferior(s, (cx + r * 0.40, cy), r, (232, 30, 50))
    _brillo_fuerte(s, (cx - r * 0.72, cy - r * 0.42), r)
    _tallo(s, (cx, cy - r * 0.80), (cx + r * 0.14, cy - r * 1.38), max(3, round(r * 0.13)))
    _hoja_viva(s, (cx + r * 0.50, cy - r * 1.15), r * 0.82, r * 0.40, -28)
    _destello(s, (cx + r * 0.85, cy - r * 0.55), r * 0.22)


def naranja(s, rect):
    cx, cy = rect.centerx, rect.centery + rect.h * 0.06
    r = min(rect.w, rect.h) * 0.40
    _sombra(s, (cx, cy + r * 0.92), r * 1.9, r * 0.42)
    _esfera(s, (cx, cy), r, (206, 92, 8), (255, 148, 18), (255, 206, 96))
    # Textura de cáscara: puntitos más claros y más oscuros.
    for i in range(22 if r >= 40 else 9):
        ang = i * 2.39996
        d = r * (0.18 + 0.68 * ((i * 37) % 11) / 11)
        color = (255, 186, 70) if i % 3 else (226, 112, 14)
        _circulo(s, color, (cx + math.cos(ang) * d, cy + math.sin(ang) * d), max(1, r * 0.035))
    _brillo_fuerte(s, (cx - r * 0.38, cy - r * 0.42), r)
    _tallo(s, (cx, cy - r * 0.92), (cx, cy - r * 1.14), max(3, round(r * 0.12)))
    _hoja_viva(s, (cx + r * 0.40, cy - r * 1.08), r * 0.66, r * 0.32, -22)
    _destello(s, (cx + r * 0.62, cy - r * 0.62), r * 0.20)


def banano(s, rect):
    cx, cy = rect.centerx, rect.centery
    w = min(rect.w, rect.h * 1.2) * 0.90
    _sombra(s, (cx, cy + w * 0.30), w * 0.95, w * 0.16)

    def curva(desfase, grosor):
        externa, interna = [], []
        for i in range(25):
            t = -1 + 2 * i / 24
            x = cx + t * w / 2
            y = cy + desfase - (1 - t * t) * w * 0.26 + w * 0.12
            g = grosor * (1 - 0.55 * abs(t) ** 2)
            externa.append((x, y + g / 2))
            interna.append((x, y - g / 2))
        return externa + interna[::-1]

    for desfase in (w * 0.10, -w * 0.06):
        contorno = curva(desfase, w * 0.31)
        _poligono(s, CONTORNO, [(x, y + (2 if y > cy else -2)) for x, y in contorno])
        _poligono(s, (232, 176, 18), curva(desfase, w * 0.27))            # sombra
        _poligono(s, (255, 214, 40), curva(desfase - w * 0.02, w * 0.20))  # color
        _poligono(s, (255, 240, 130), curva(desfase - w * 0.045, w * 0.08))  # luz
        # Brillo alargado.
        puntos = curva(desfase - w * 0.055, w * 0.025)
        _poligono(s, (255, 252, 220), puntos[5:20] + puntos[-20:-5])
    for lado in (-1, 1):
        x = cx + lado * w * 0.5
        y = cy - w * 0.02 + w * 0.12 + (w * 0.10 if lado < 0 else -w * 0.06)
        _circulo(s, CONTORNO, (x, y), max(3, w * 0.045))
        _circulo(s, (110, 72, 36), (x, y), max(2, w * 0.032))
    _destello(s, (cx - w * 0.18, cy - w * 0.12), w * 0.08)


def uvas(s, rect):
    cx, top = rect.centerx, rect.y + rect.h * 0.22
    r = min(rect.w, rect.h) * 0.115
    filas = [4, 3, 2, 1]
    granos = []
    for fila, n in enumerate(filas):
        for i in range(n):
            granos.append((cx + (i - (n - 1) / 2) * r * 1.75, top + r + fila * r * 1.55))
    _sombra(s, (cx, granos[-1][1] + r * 1.1), r * 5.5, r * 1.2)
    for x, y in granos:
        _circulo(s, CONTORNO, (x, y), r * 1.14)
    for x, y in granos:
        _esfera(s, (x, y), r, (62, 14, 92), (150, 52, 196), (214, 150, 246), contorno=False)
    _tallo(s, (cx, top), (cx + r * 0.3, top - r * 1.3), max(3, round(r * 0.35)))
    _hoja_viva(s, (cx + r * 1.45, top - r * 0.9), r * 2.3, r * 1.15, -15)
    _destello(s, (granos[0][0] - r * 0.2, granos[0][1] - r * 0.6), r * 0.55)


# ---------------------------------------------------------
# VERDURAS
# ---------------------------------------------------------
def tomate(s, rect):
    cx, cy = rect.centerx, rect.centery + rect.h * 0.06
    r = min(rect.w, rect.h) * 0.40
    _elipse(s, CONTORNO, pygame.Rect(cx - r * 1.08, cy - r * 0.92, r * 2.16, r * 1.86))
    _elipse(s, (176, 34, 32), pygame.Rect(cx - r, cy - r * 0.84, r * 2, r * 1.7))
    _elipse(s, (226, 62, 48), pygame.Rect(cx - r * 0.9, cy - r * 0.84, r * 1.7, r * 1.5))
    _elipse(s, (246, 112, 88), pygame.Rect(cx - r * 0.7, cy - r * 0.7, r * 0.7, r * 0.55))
    # Estrella verde (cáliz)
    puntos = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rad = r * (0.5 if i % 2 == 0 else 0.18)
        puntos.append((cx + math.cos(ang) * rad, cy - r * 0.78 - math.sin(ang) * rad * 0.55))
    _poligono(s, (60, 120, 52), puntos)
    pygame.draw.line(s, (60, 120, 52), (cx, cy - r * 0.8), (cx + r * 0.05, cy - r * 1.15), max(3, round(r * 0.13)))


def zanahoria(s, rect):
    cx = rect.centerx
    top, bottom = rect.y + rect.h * 0.30, rect.bottom - rect.h * 0.06
    w = min(rect.w, rect.h) * 0.36
    cuerpo = [(cx - w / 2, top), (cx + w / 2, top), (cx + w * 0.12, bottom), (cx - w * 0.12, bottom)]
    _poligono(s, CONTORNO, [(cx - w / 2 - 3, top - 2), (cx + w / 2 + 3, top - 2), (cx + w * 0.12 + 2, bottom + 3), (cx - w * 0.12 - 2, bottom + 3)])
    _poligono(s, (236, 128, 36), cuerpo)
    _poligono(s, (250, 164, 72), [(cx - w / 2 + 3, top + 2), (cx - w * 0.1, top + 2), (cx - w * 0.06, bottom - 6)])
    for i in range(1, 5):
        y = top + (bottom - top) * i / 5
        ancho = w / 2 * (1 - 0.76 * i / 5)
        pygame.draw.line(s, (186, 92, 28), (cx - ancho * 0.6, y), (cx + ancho * 0.1, y), 2)
    for ang in (-35, 0, 35):
        _hoja(s, (cx + math.sin(math.radians(ang)) * w * 0.5, top - w * 0.55), w * 1.0, w * 0.3, ang - 90)


def brocoli(s, rect):
    cx = rect.centerx
    r = min(rect.w, rect.h) * 0.15
    tallo_top, tallo_bottom = rect.y + rect.h * 0.52, rect.bottom - rect.h * 0.08
    _poligono(s, CONTORNO, [(cx - r * 0.75, tallo_top), (cx + r * 0.75, tallo_top), (cx + r * 0.6, tallo_bottom + 3), (cx - r * 0.6, tallo_bottom + 3)])
    _poligono(s, (176, 210, 128), [(cx - r * 0.6, tallo_top), (cx + r * 0.6, tallo_top), (cx + r * 0.45, tallo_bottom), (cx - r * 0.45, tallo_bottom)])
    copa = [(-1.2, 0.2), (1.2, 0.2), (-0.6, -0.5), (0.6, -0.5), (0, -1.0), (0, 0.1), (-1.6, -0.4), (1.6, -0.4)]
    base_y = rect.y + rect.h * 0.45
    for dx, dy in copa:
        _circulo(s, CONTORNO, (cx + dx * r, base_y + dy * r), r * 0.95)
    for dx, dy in copa:
        _circulo(s, (58, 128, 62), (cx + dx * r, base_y + dy * r), r * 0.82)
        _circulo(s, (98, 168, 84), (cx + dx * r - r * 0.2, base_y + dy * r - r * 0.2), r * 0.42)


def elote(s, rect):
    cx, cy = rect.centerx, rect.centery
    w, h = min(rect.w, rect.h) * 0.36, min(rect.w, rect.h) * 0.80
    _elipse(s, CONTORNO, pygame.Rect(cx - w / 2 - 3, cy - h / 2 - 3, w + 6, h + 6))
    _elipse(s, (240, 200, 64), pygame.Rect(cx - w / 2, cy - h / 2, w, h))
    for fila in range(9):
        y = cy - h * 0.38 + fila * h * 0.085
        for col in range(3):
            x = cx + (col - 1) * w * 0.26
            ancho = w * 0.5 * math.sqrt(max(0.0, 1 - ((y - cy) / (h / 2)) ** 2))
            if abs(x - cx) < ancho:
                _circulo(s, (252, 226, 120), (x, y), max(2, w * 0.09))
    # Hojas de la tusa
    for lado in (-1, 1):
        _poligono(s, CONTORNO, [(cx, cy + h * 0.52), (cx + lado * w * 0.95, cy + h * 0.05),
                                (cx + lado * w * 0.75, cy - h * 0.25), (cx + lado * w * 0.15, cy + h * 0.2)])
        _poligono(s, (104, 168, 82), [(cx, cy + h * 0.47), (cx + lado * w * 0.85, cy + h * 0.05),
                                      (cx + lado * w * 0.7, cy - h * 0.18), (cx + lado * w * 0.15, cy + h * 0.22)])


# ---------------------------------------------------------
# BEBIDAS
# ---------------------------------------------------------
BEBIDA_COLORES = {
    # (líquido, etiqueta, texto de la etiqueta)
    "cola": ((92, 44, 34), (206, 52, 48), "COLA"),
    "naranjada": ((240, 146, 44), (250, 238, 206), "NARANJA"),
    "limonada": ((128, 196, 84), (250, 238, 206), "LIMÓN"),
    "agua": ((176, 214, 236), (64, 116, 178), "AGUA"),
    "fresa": ((222, 72, 104), (250, 238, 206), "FRESA"),
}
_fuente_etiqueta = {}


def botella(s, rect, kind):
    liquido, etiqueta, texto = BEBIDA_COLORES[kind]
    h = rect.h * 0.94
    w = min(rect.w * 0.9, h * 0.36)
    cx, bottom = rect.centerx, rect.y + (rect.h + h) / 2
    top = bottom - h
    cuello_w = w * 0.38
    hombro = top + h * 0.34
    # Silueta
    silueta = [(cx - cuello_w / 2, top + h * 0.08), (cx + cuello_w / 2, top + h * 0.08),
               (cx + cuello_w / 2, top + h * 0.2), (cx + w / 2, hombro),
               (cx + w / 2, bottom), (cx - w / 2, bottom), (cx - w / 2, hombro),
               (cx - cuello_w / 2, top + h * 0.2)]
    _poligono(s, CONTORNO, [(x + (2 if x > cx else -2), y + (2 if y >= bottom - 1 else 0)) for x, y in silueta])
    _poligono(s, liquido, silueta)
    # Tapa
    tapa = pygame.Rect(cx - cuello_w * 0.62, top, cuello_w * 1.24, h * 0.1)
    pygame.draw.rect(s, CONTORNO, tapa.inflate(4, 4), border_radius=3)
    pygame.draw.rect(s, (214, 214, 206), tapa, border_radius=2)
    # Etiqueta
    eti = pygame.Rect(cx - w / 2, top + h * 0.5, w, h * 0.26)
    pygame.draw.rect(s, etiqueta, eti)
    pygame.draw.line(s, CONTORNO, eti.topleft, eti.topright, 2)
    pygame.draw.line(s, CONTORNO, eti.bottomleft, eti.bottomright, 2)
    tam = max(8, round(eti.h * 0.55))
    if tam not in _fuente_etiqueta:
        _fuente_etiqueta[tam] = pygame.font.Font(None, tam)
    color_txt = (250, 238, 206) if sum(etiqueta) < 400 else (120, 40, 36)
    t = _fuente_etiqueta[tam].render(texto, True, color_txt)
    if t.get_width() > eti.w - 4:
        t = pygame.transform.smoothscale(t, (eti.w - 4, t.get_height()))
    s.blit(t, t.get_rect(center=eti.center))
    # Brillo del vidrio
    pygame.draw.line(s, (255, 255, 255), (cx - w * 0.28, hombro + h * 0.04), (cx - w * 0.28, eti.top - 4), max(2, round(w * 0.08)))
    pygame.draw.line(s, (255, 255, 255), (cx - w * 0.28, eti.bottom + 4), (cx - w * 0.28, bottom - h * 0.06), max(2, round(w * 0.08)))


# ---------------------------------------------------------
# ABARROTES (bolsas, leche y huevos)
# ---------------------------------------------------------
BOLSAS = {
    #           bolsa             etiqueta          detalle
    "harina":   ((246, 244, 236), (74, 118, 200),   "trigo"),
    "azucar":   ((246, 244, 236), (226, 104, 150),  "cubos"),
    "arroz":    ((238, 224, 182), (86, 158, 84),    "granos"),
    "frijoles": ((134, 50, 46),   (238, 216, 172),  "frijol"),
}


def _bolsa_hd(s, rect, kind):
    cuerpo, etiqueta, detalle = BOLSAS[kind]
    lado = min(rect.w, rect.h * 0.85)
    w, h = lado * 0.78, lado * 1.0
    cx, base = rect.centerx, rect.centery + h / 2
    _sombra(s, (cx, base), w * 0.95, h * 0.12)
    sombra_cuerpo = _mezcla(cuerpo, (0, 0, 0), 0.22)
    # Cuello amarrado y orejas de la bolsa
    cuello_y = base - h
    _poligono(s, CONTORNO, [(cx - w * 0.22, cuello_y + h * 0.04), (cx - w * 0.30, cuello_y - h * 0.06),
                            (cx, cuello_y + h * 0.05), (cx + w * 0.30, cuello_y - h * 0.06),
                            (cx + w * 0.22, cuello_y + h * 0.04), (cx + w * 0.14, cuello_y + h * 0.16),
                            (cx - w * 0.14, cuello_y + h * 0.16)])
    _poligono(s, cuerpo, [(cx - w * 0.19, cuello_y + h * 0.05), (cx - w * 0.25, cuello_y - h * 0.02),
                          (cx, cuello_y + h * 0.07), (cx + w * 0.25, cuello_y - h * 0.02),
                          (cx + w * 0.19, cuello_y + h * 0.05), (cx + w * 0.12, cuello_y + h * 0.15),
                          (cx - w * 0.12, cuello_y + h * 0.15)])
    # Cuerpo abultado
    cuerpo_r = pygame.Rect(0, 0, w, h * 0.80)
    cuerpo_r.midbottom = (cx, base)
    pygame.draw.rect(s, CONTORNO, cuerpo_r.inflate(6, 6), border_radius=int(w * 0.22))
    pygame.draw.rect(s, sombra_cuerpo, cuerpo_r, border_radius=int(w * 0.2))
    luz = cuerpo_r.inflate(-w * 0.16, -h * 0.06).move(-w * 0.05, -h * 0.02)
    pygame.draw.rect(s, cuerpo, luz, border_radius=int(w * 0.18))
    # Amarre
    nudo = pygame.Rect(0, 0, w * 0.36, h * 0.07)
    nudo.center = (cx, cuello_y + h * 0.17)
    pygame.draw.rect(s, (214, 170, 64), nudo, border_radius=4)
    pygame.draw.rect(s, CONTORNO, nudo, 2, border_radius=4)
    # Etiqueta
    et = pygame.Rect(0, 0, w * 0.70, h * 0.36)
    et.center = (cx, cuerpo_r.centery + h * 0.03)
    pygame.draw.rect(s, _mezcla(etiqueta, (0, 0, 0), 0.25), et.move(0, 3), border_radius=6)
    pygame.draw.rect(s, etiqueta, et, border_radius=6)
    claro = _mezcla(etiqueta, (255, 255, 255), 0.75)
    r = max(2, et.h * 0.10)
    if detalle == "trigo":
        x0 = et.centerx
        pygame.draw.line(s, claro, (x0, et.bottom - et.h * 0.15), (x0, et.top + et.h * 0.18), 3)
        for i in range(3):
            y = et.top + et.h * (0.25 + i * 0.18)
            _elipse(s, claro, (x0 - r * 2.6, y, r * 2.4, r * 1.4))
            _elipse(s, claro, (x0 + r * 0.2, y, r * 2.4, r * 1.4))
    elif detalle == "cubos":
        for i, (dx, dy) in enumerate([(-1.2, 0.3), (0.2, 0.3), (-0.5, -0.9)]):
            c = pygame.Rect(0, 0, r * 2.2, r * 2.2)
            c.center = (et.centerx + dx * r * 1.3 + r * 0.5, et.centery + dy * r * 1.3)
            pygame.draw.rect(s, claro, c, border_radius=2)
    elif detalle == "granos":
        for i in range(7):
            ang = i * 0.9
            x = et.centerx + math.cos(ang) * et.w * 0.24
            y = et.centery + math.sin(ang * 1.3) * et.h * 0.22
            _elipse(s, claro, (x - r * 1.1, y - r * 0.55, r * 2.2, r * 1.1))
    else:  # frijol
        for dx, dy in [(-0.9, 0.2), (0.6, -0.3), (0.1, 0.9)]:
            x, y = et.centerx + dx * r * 2.2, et.centery + dy * r * 1.6
            _elipse(s, (104, 40, 40), (x - r * 1.3, y - r * 0.9, r * 2.6, r * 1.8))
            _elipse(s, (156, 74, 64), (x - r * 0.8, y - r * 0.6, r * 1.1, r * 0.6))
    # Brillo del plástico
    br = pygame.Rect(0, 0, w * 0.09, h * 0.34)
    br.topleft = (cuerpo_r.x + w * 0.10, cuerpo_r.y + h * 0.08)
    pygame.draw.rect(s, (255, 255, 255), br, border_radius=6)


def leche(s, rect):
    lado = min(rect.w, rect.h * 0.85)
    w, h = lado * 0.62, lado * 1.0
    cx, base = rect.centerx, rect.centery + h / 2
    _sombra(s, (cx, base), w * 1.1, h * 0.12)
    techo = base - h
    caja = pygame.Rect(0, 0, w, h * 0.78)
    caja.midbottom = (cx, base)
    # Tejado de la caja
    _poligono(s, CONTORNO, [(caja.left - 3, caja.top + 2), (cx, techo - 3), (caja.right + 3, caja.top + 2)])
    _poligono(s, (226, 226, 220), [(caja.left, caja.top + 1), (cx, techo + 1), (caja.right, caja.top + 1)])
    _poligono(s, (250, 250, 246), [(caja.left + 3, caja.top), (cx - 2, techo + 4), (cx - 2, caja.top)])
    cresta = pygame.Rect(0, 0, w * 0.5, h * 0.06)
    cresta.midbottom = (cx, techo + 4)
    pygame.draw.rect(s, CONTORNO, cresta.inflate(4, 4), border_radius=2)
    pygame.draw.rect(s, (236, 236, 230), cresta, border_radius=2)
    # Cuerpo
    pygame.draw.rect(s, CONTORNO, caja.inflate(6, 6), border_radius=5)
    pygame.draw.rect(s, (236, 236, 230), caja, border_radius=4)
    pygame.draw.rect(s, (252, 252, 248), caja.inflate(-w * 0.2, -4).move(-w * 0.08, 0), border_radius=4)
    franja = pygame.Rect(caja.x, caja.y + caja.h * 0.32, caja.w, caja.h * 0.36)
    pygame.draw.rect(s, (70, 120, 196), franja)
    pygame.draw.rect(s, (96, 148, 222), franja.inflate(-w * 0.2, -franja.h * 0.4).move(-w * 0.08, -franja.h * 0.1))
    # Gota de leche
    gr = franja.h * 0.26
    gc = (cx + w * 0.05, franja.centery + gr * 0.3)
    _poligono(s, (255, 255, 255), [(gc[0], gc[1] - gr * 2.0), (gc[0] - gr * 0.85, gc[1] - gr * 0.2),
                                   (gc[0] + gr * 0.85, gc[1] - gr * 0.2)])
    _circulo(s, (255, 255, 255), gc, gr)


def huevo(s, rect):
    lado = min(rect.w, rect.h)
    w, h = lado * 0.62, lado * 0.80
    cx, cy = rect.centerx, rect.centery + lado * 0.04
    _sombra(s, (cx, cy + h / 2), w * 1.0, h * 0.14)
    caja = pygame.Rect(0, 0, w, h)
    caja.center = (cx, cy)
    # Forma de huevo: elipse ancha abajo + elipse angosta arriba
    abajo = pygame.Rect(caja.x, caja.y + h * 0.28, w, h * 0.72)
    arriba = pygame.Rect(caja.x + w * 0.10, caja.y, w * 0.80, h * 0.80)
    for r in (abajo, arriba):
        _elipse(s, CONTORNO, r.inflate(6, 6))
    for r in (abajo, arriba):
        _elipse(s, (226, 204, 166), r)
    _elipse(s, (248, 238, 214), abajo.inflate(-w * 0.16, -h * 0.14).move(-w * 0.06, -h * 0.05))
    _elipse(s, (248, 238, 214), arriba.inflate(-w * 0.18, -h * 0.14).move(-w * 0.05, 0))
    _elipse(s, (255, 252, 242), (cx - w * 0.26, cy - h * 0.26, w * 0.18, h * 0.26))


DIBUJOS = {
    "manzana": manzana, "banano": banano, "naranja": naranja, "uvas": uvas,
    "zanahoria": zanahoria, "tomate": tomate, "brocoli": brocoli, "elote": elote,
    "leche": leche, "huevos": huevo,
}
for _k in BOLSAS:
    DIBUJOS[_k] = (lambda k: lambda s, r: _bolsa_hd(s, r, k))(_k)


# Harina: pixel art del saco naranja (imagenes/harina.png), agrandado sin
# suavizar para que los píxeles se vean nítidos.
_harina_img = {}


def harina_pixel(s, rect):
    import os
    if "base" not in _harina_img:
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes", "harina.png")
        try:
            _harina_img["base"] = pygame.image.load(ruta)
        except (pygame.error, FileNotFoundError):
            _harina_img["base"] = None
    base = _harina_img["base"]
    if base is None:
        _bolsa_hd(s, rect, "harina")
        return
    w, h = base.get_size()
    factor = min(rect.w / w, rect.h / h) * 0.95
    # Grande: múltiplo entero (píxeles parejos); chico: al tamaño justo.
    entero = int(factor) if factor >= 3 else factor
    tam = (max(1, round(w * entero)), max(1, round(h * entero)))
    if tam not in _harina_img:
        _harina_img[tam] = pygame.transform.scale(base, tam)
    img = _harina_img[tam]
    _sombra(s, (rect.centerx, rect.centery + tam[1] / 2), tam[0] * 0.95, tam[1] * 0.10)
    s.blit(img, img.get_rect(center=rect.center))


DIBUJOS["harina"] = harina_pixel


# Verduras y huevo: pixel art de imagenes/ (mismo método que la harina).
_pixel_img = {}


def _pixel_art(archivo, respaldo):
    def dibujar(s, rect):
        import os
        if archivo not in _pixel_img:
            ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes", archivo)
            try:
                _pixel_img[archivo] = pygame.image.load(ruta)
            except (pygame.error, FileNotFoundError):
                _pixel_img[archivo] = None
        base = _pixel_img[archivo]
        if base is None:
            respaldo(s, rect)
            return
        w, h = base.get_size()
        factor = min(rect.w / w, rect.h / h) * 0.95
        entero = int(factor) if factor >= 3 else factor
        tam = (max(1, round(w * entero)), max(1, round(h * entero)))
        llave = (archivo, tam)
        if llave not in _pixel_img:
            _pixel_img[llave] = pygame.transform.scale(base, tam)
        img = _pixel_img[llave]
        _sombra(s, (rect.centerx, rect.centery + tam[1] / 2), tam[0] * 0.9, tam[1] * 0.08)
        s.blit(img, img.get_rect(center=rect.center))
    return dibujar


for _k, _archivo in (("zanahoria", "zanahoria.png"), ("brocoli", "brocoli.png"),
                     ("elote", "elote.png"), ("huevos", "huevo.png")):
    DIBUJOS[_k] = _pixel_art(_archivo, DIBUJOS[_k])
# Helados: solo pixel art (si falta la imagen, se ve la versión chica agrandada).


def _respaldo_chico(kind):
    def dibujar(s, rect):
        from productos import sprite
        img = sprite(kind)
        f = max(1, int(min(rect.w / img.get_width(), rect.h / img.get_height()) * 0.9))
        img = pygame.transform.scale_by(img, f)
        s.blit(img, img.get_rect(center=rect.center))
    return dibujar


for _k in ("paleta", "cono"):
    DIBUJOS[_k] = _pixel_art(f"{_k}.png", _respaldo_chico(_k))


# Bebidas y leche en pixel art (imagenes/): van antes que las botellas dibujadas.
PIXEL_BEBIDAS = {"agua": "agua.png", "naranjada": "naranjada.png", "fresa": "fresa.png",
                 "cola": "cola.png", "limonada": "limonada.png", "leche": "leche.png"}
for _k, _archivo in PIXEL_BEBIDAS.items():
    _respaldo = DIBUJOS.get(_k) or (lambda k: lambda s, r: botella(s, r, k))(_k)
    DIBUJOS[_k] = _pixel_art(_archivo, _respaldo)


def dibujar_hd(surface, kind, rect):
    """Dibuja el producto en alta calidad dentro del rectángulo."""
    rect = pygame.Rect(rect)
    if kind in PIXEL_BEBIDAS:
        DIBUJOS[kind](surface, rect)
    elif kind in FRUTAS_PIXEL:
        # Frutas en pixel art detallado (estilo elegido por el equipo).
        dibujar_fruta_pixel(surface, kind, rect)
    elif kind in BEBIDA_COLORES:
        botella(surface, rect, kind)
    elif kind in DIBUJOS:
        DIBUJOS[kind](surface, rect)
