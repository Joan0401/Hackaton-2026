"""Disfraces de los clientes frecuentes (payaso, bombera, chef, astronauta, pirata).

Toma los cuadros ya hechos del personaje (28 x 44) y les agrega accesorios.
Los cuadros nuevos son más altos (EXTRA px arriba) para que quepan sombreros
y cascos; el personaje se sigue apoyando en los pies igual que antes.
"""
import pygame

EXTRA = 10            # espacio extra arriba para sombreros y cascos
ANCHO = 28
NEGRO = (35, 27, 27)
BLANCO = (246, 246, 240)


def aplicar(persona, disfraz):
    """Reemplaza los cuadros de la persona por cuadros disfrazados."""
    dibujar = DISFRACES[disfraz]
    nuevos = {}
    for direccion in ("down", "up", "left"):
        cuadros = []
        for cuadro in persona.frames[direccion]:
            alto = cuadro.get_height() + EXTRA
            s = pygame.Surface((ANCHO, alto), pygame.SRCALPHA)
            s.blit(cuadro, (0, EXTRA))
            dibujar(s, direccion)
            cuadros.append(s)
        nuevos[direccion] = tuple(cuadros)
    # La vista de la derecha es el reflejo de la izquierda (como el personaje).
    nuevos["right"] = tuple(pygame.transform.flip(c, True, False) for c in nuevos["left"])
    persona.frames = nuevos
    persona.HEIGHT = persona.HEIGHT + EXTRA   # el globo de diálogo va más arriba


# ---------------------------------------------------------
# Cada disfraz: coordenadas dentro del cuadro (cabeza arriba en y = EXTRA)
# ---------------------------------------------------------
E = EXTRA


def _payaso(s, d):
    # Lunares en la camisa
    for x, y in ((9, E + 22), (18, E + 25), (12, E + 29), (20, E + 30)):
        pygame.draw.circle(s, (255, 226, 70), (x, y), 2)
    # Pelo esponjado a los lados
    for x in ((3, 24) if d != "left" else (6, 22)):
        pygame.draw.circle(s, (230, 70, 50), (x, E + 8), 5)
        pygame.draw.circle(s, (250, 140, 60), (x - 1, E + 7), 2)
    # Gorrito de cono con pompón
    pygame.draw.polygon(s, (90, 170, 230), [(9, E + 2), (19, E + 2), (14, E - 8)])
    pygame.draw.line(s, (255, 226, 70), (11, E - 1), (17, E - 1), 2)
    pygame.draw.circle(s, BLANCO, (14, E - 8), 2)
    # Nariz roja
    if d == "down":
        pygame.draw.circle(s, (230, 40, 40), (14, E + 13), 2)
        pygame.draw.line(s, (200, 40, 40), (11, E + 16), (17, E + 16), 1)   # sonrisa
    elif d == "left":
        pygame.draw.circle(s, (230, 40, 40), (7, E + 13), 2)


def _bombera(s, d):
    # Franjas reflectivas del abrigo
    for y in (E + 26, E + 31):
        pygame.draw.line(s, (236, 238, 150), (5, y), (22, y), 2)
    # Casco rojo con ala
    pygame.draw.ellipse(s, (196, 38, 34), (3, E - 5, 22, 13))
    pygame.draw.ellipse(s, (236, 84, 70), (7, E - 4, 8, 4))
    ala = (1, E + 5, 26, 3) if d != "left" else (2, E + 5, 26, 3)
    pygame.draw.rect(s, (140, 24, 24), ala)
    if d == "down":
        pygame.draw.rect(s, (246, 200, 60), (12, E - 2, 5, 5))      # escudo
        pygame.draw.rect(s, (170, 120, 30), (12, E - 2, 5, 5), 1)


def _chef(s, d):
    # Pañuelo rojo y botones
    if d != "up":
        pygame.draw.rect(s, (214, 56, 48), (10, E + 18, 8, 3))
    if d == "down":
        for y in (E + 23, E + 27):
            for x in (11, 16):
                pygame.draw.circle(s, NEGRO, (x, y), 1)
    # Gorro alto de chef
    pygame.draw.rect(s, (200, 200, 196), (6, E, 16, 4))
    pygame.draw.rect(s, BLANCO, (7, E - 6, 14, 7))
    for x, r in ((9, 4), (14, 5), (19, 4)):
        pygame.draw.circle(s, BLANCO, (x, E - 7), r)
    pygame.draw.line(s, (214, 214, 208), (8, E + 1), (20, E + 1), 1)


def _astronauta(s, d):
    # Bandera en el pecho
    if d == "down":
        pygame.draw.rect(s, (60, 110, 200), (8, E + 21, 5, 4))
        pygame.draw.rect(s, BLANCO, (8, E + 22, 5, 1))
    # Casco de vidrio con antena
    vidrio = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(vidrio, (170, 220, 255, 70), (14, E + 8), 13)
    s.blit(vidrio, (0, 0))
    pygame.draw.circle(s, (214, 226, 236), (14, E + 8), 13, 2)
    pygame.draw.arc(s, (255, 255, 255), (5, E - 2, 14, 14), 1.6, 2.8, 2)   # brillo
    pygame.draw.line(s, (150, 160, 170), (14, E - 5), (14, E - 9), 1)
    pygame.draw.circle(s, (230, 60, 50), (14, E - 9), 2)


def _pirata(s, d):
    # Rayas de la camisa
    for y in (E + 21, E + 25, E + 29):
        pygame.draw.line(s, (196, 40, 40), (5, y), (22, y), 2)
    # Sombrero de tres picos con calavera
    pygame.draw.polygon(s, (34, 30, 36), [(0, E + 4), (28, E + 4), (22, E - 4), (14, E - 7), (6, E - 4)])
    pygame.draw.line(s, (220, 180, 70), (2, E + 3), (26, E + 3), 1)
    if d != "up":
        cx = 14 if d == "down" else 11
        pygame.draw.rect(s, BLANCO, (cx - 1, E - 3, 3, 3))
    # Parche en el ojo
    if d == "down":
        pygame.draw.line(s, NEGRO, (4, E + 8), (24, E + 12), 1)
        pygame.draw.circle(s, NEGRO, (10, E + 12), 2)
    elif d == "left":
        pygame.draw.circle(s, NEGRO, (9, E + 11), 2)


DISFRACES = {
    "payaso": _payaso,
    "bombera": _bombera,
    "chef": _chef,
    "astronauta": _astronauta,
    "pirata": _pirata,
}
