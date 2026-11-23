"""La casa de Canela: empieza como una caja de cartón y se va mejorando.

Está en la tienda, abajo a la derecha. E junto a ella abre "CASA DE
CANELA", donde se compra la siguiente mejora (cuestan mucho: hay que
ahorrar). Canela a veces se va a dormir ahí.
"""
import pygame

# (nombre, precio)
NIVELES = [
    ("Caja de cartón", 0),
    ("Cama acolchada", 250),
    ("Casita de madera", 600),
    ("Castillo de gato", 1200),
]
X, BASE = 468, 350              # esquina izquierda y piso de la casa
W = 60
CAMA = (498, 351)               # donde se acuesta Canela
# Altura de Canela dormida en cada casa: en la caja solo sobresalen las orejas.
CAMA_Y = {0: 346, 1: 346, 2: 349, 3: 349}
# En la casita y el castillo solo se le ven las orejas en la puerta.
OREJAS_PUERTA = {2: (X + 30, BASE - 15), 3: (X + 30, BASE - 13)}


class CasaGato:
    WIDTH = W

    def __init__(self):
        self.nivel = 0
        self.x = X + W / 2
        self.y = BASE - 30       # la parte de atrás va detrás de Canela dormida
        self.frente = FrenteCasa(self)

    @property
    def nombre(self):
        return NIVELES[self.nivel][0]

    @property
    def siguiente(self):
        """(nombre, precio) de la próxima mejora, o None si ya es la mejor."""
        return NIVELES[self.nivel + 1] if self.nivel + 1 < len(NIVELES) else None

    def rect_choque(self):
        """Parte de abajo: el personaje no la atraviesa."""
        return pygame.Rect(X, BASE - 14, W, 14)

    def cerca(self, player):
        r = pygame.Rect(X, BASE - 30, W, 30)
        cx = max(r.left, min(player.x, r.right))
        cy = max(r.top, min(player.y, r.bottom))
        return ((player.x - cx) ** 2 + (player.y - cy) ** 2) ** 0.5 <= 22

    def dibujar(self, surface, escena="interior"):
        if escena == "interior":
            dibujar_casa(surface, self.nivel, X, BASE)


class FrenteCasa:
    """El frente de la caja (o el borde de la cama): se dibuja DELANTE de
    Canela cuando duerme adentro, para que solo se le vean las orejas."""
    WIDTH = W

    def __init__(self, casa):
        self.casa = casa
        self.x = X + W / 2
        self.y = BASE + 1

    def dibujar(self, surface, escena="interior"):
        if escena == "interior":
            dibujar_frente(surface, self.casa.nivel, X, BASE)


def dibujar_frente(surface, nivel, x, base):
    if nivel == 0:
        carton, carton_o = (196, 150, 96), (140, 100, 60)
        pygame.draw.rect(surface, carton_o, (x + 6, base - 20, 48, 20))
        pygame.draw.rect(surface, carton, (x + 8, base - 18, 44, 16))
        pygame.draw.line(surface, carton_o, (x + 30, base - 18), (x + 30, base - 3), 1)
    elif nivel == 1:
        anterior = surface.get_clip()
        surface.set_clip(pygame.Rect(x, base - 9, W, 12).clip(anterior) if anterior else
                         pygame.Rect(x, base - 9, W, 12))
        pygame.draw.ellipse(surface, (150, 50, 70), (x + 2, base - 18, 56, 18))
        pygame.draw.ellipse(surface, (220, 90, 110), (x + 4, base - 17, 52, 15))
        for px in range(x + 8, x + 54, 8):
            pygame.draw.circle(surface, (250, 200, 210), (px, base - 4), 1)
        surface.set_clip(anterior)


def dibujar_casa(surface, nivel, x, base):
    """Dibuja la casa de ese nivel con la esquina izquierda en x y el piso en base."""
    oscuro = (49, 35, 34)
    pygame.draw.ellipse(surface, (55, 48, 43), (x + 2, base - 4, W - 4, 7))
    if nivel == 0:
        # Caja de cartón abierta con las solapas hacia afuera.
        carton, carton_o = (196, 150, 96), (140, 100, 60)
        pygame.draw.rect(surface, carton_o, (x + 6, base - 20, 48, 20))
        pygame.draw.rect(surface, carton, (x + 8, base - 18, 44, 16))
        pygame.draw.polygon(surface, carton, [(x + 6, base - 20), (x - 2, base - 27), (x + 4, base - 28), (x + 12, base - 20)])
        pygame.draw.polygon(surface, carton, [(x + 54, base - 20), (x + 62, base - 27), (x + 56, base - 28), (x + 48, base - 20)])
        pygame.draw.line(surface, carton_o, (x + 30, base - 18), (x + 30, base - 3), 1)
        pygame.draw.rect(surface, (90, 60, 40), (x + 12, base - 20, 36, 3))
    elif nivel == 1:
        # Cama redonda acolchada con almohadita.
        pygame.draw.ellipse(surface, (150, 50, 70), (x + 2, base - 18, 56, 18))
        pygame.draw.ellipse(surface, (220, 90, 110), (x + 4, base - 17, 52, 15))
        pygame.draw.ellipse(surface, (250, 236, 220), (x + 10, base - 14, 40, 9))
        pygame.draw.ellipse(surface, (170, 210, 240), (x + 38, base - 16, 14, 7))
        for px in range(x + 8, x + 54, 8):
            pygame.draw.circle(surface, (250, 200, 210), (px, base - 4), 1)
    elif nivel == 2:
        # Casita de madera con techo rojo y puerta redonda.
        pygame.draw.rect(surface, oscuro, (x + 6, base - 30, 48, 30))
        pygame.draw.rect(surface, (176, 116, 72), (x + 8, base - 28, 44, 27))
        for py in range(base - 24, base - 2, 6):
            pygame.draw.line(surface, (140, 90, 56), (x + 8, py), (x + 51, py), 1)
        pygame.draw.polygon(surface, (150, 40, 40), [(x + 2, base - 28), (x + 30, base - 46), (x + 58, base - 28)])
        pygame.draw.polygon(surface, (200, 66, 60), [(x + 6, base - 29), (x + 30, base - 43), (x + 54, base - 29)])
        pygame.draw.ellipse(surface, (40, 28, 30), (x + 20, base - 20, 20, 24))
        pygame.draw.rect(surface, (250, 236, 200), (x + 22, base - 40, 16, 6))
        pygame.draw.circle(surface, (240, 150, 60), (x + 30, base - 37), 2)
    else:
        # Castillo de gato: dos torres con banderas y un poste para rascar.
        piedra, piedra_o = (196, 188, 214), (120, 110, 150)
        for tx in (x + 2, x + 40):
            pygame.draw.rect(surface, piedra_o, (tx, base - 42, 18, 42))
            pygame.draw.rect(surface, piedra, (tx + 2, base - 40, 14, 39))
            for k in range(3):
                pygame.draw.rect(surface, piedra_o, (tx + k * 6, base - 46, 4, 5))
            pygame.draw.line(surface, (90, 70, 60), (tx + 9, base - 46), (tx + 9, base - 58), 1)
            pygame.draw.polygon(surface, (240, 90, 160), [(tx + 10, base - 58), (tx + 18, base - 55), (tx + 10, base - 52)])
            pygame.draw.rect(surface, (60, 50, 80), (tx + 7, base - 34, 5, 7))
        pygame.draw.rect(surface, piedra_o, (x + 18, base - 30, 24, 30))
        pygame.draw.rect(surface, piedra, (x + 20, base - 28, 20, 27))
        pygame.draw.ellipse(surface, (40, 28, 30), (x + 23, base - 18, 14, 20))
        pygame.draw.rect(surface, (250, 206, 70), (x + 26, base - 27, 8, 4))
        # Poste para rascar con cuerda
        pygame.draw.rect(surface, (210, 180, 130), (x + 60, base - 28, 6, 28))
        for py in range(base - 26, base - 2, 3):
            pygame.draw.line(surface, (160, 120, 70), (x + 60, py), (x + 65, py + 1), 1)
        pygame.draw.circle(surface, (240, 90, 160), (x + 63, base - 30), 3)
