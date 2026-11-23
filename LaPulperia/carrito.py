"""Carrito de compras para llenar la tienda.

Con ESPACIO junto al carrito, el personaje lo empuja: el carrito va al
frente, hacia donde mira, por la sala y la bodega. En vez de 3 productos en las manos
puede llevar hasta 8 dentro del carrito. Con ESPACIO otra vez lo suelta y
los productos se quedan guardados adentro.

Mientras se empuja, la lista de productos del carrito ES la lista "mano"
del TableObjectManager, así que tomar, acomodar, devolver (Q) y dejar en el
mostrador funcionan igual que con las manos.
"""
import math

import pygame

from productos import dibujar_producto, tamano

CAPACIDAD = 8
# Dónde va el carrito respecto a los pies del personaje, según hacia dónde mira.
FRENTE = {"up": (0, -24), "down": (0, 12), "left": (-20, 0), "right": (20, 0)}
# Con el carrito adelante el personaje queda un poco más lejos de los muebles:
# los brazos alcanzan un poco más (por encima del carrito).
ALCANCE_EXTRA = 12


def ancla(player, fx, fy):
    """Punto desde donde el personaje alcanza las cosas (frente al pecho)."""
    extra = ALCANCE_EXTRA if getattr(player, "empujando_carrito", False) else 0
    return float(player.x) + fx * extra, float(player.y) - 18.0 + fy * extra
DISTANCIA_AGARRAR = 26  # qué tan cerca hay que estar para agarrarlo
ESCENAS = ("interior", "inventario")

METAL = (176, 186, 194)
METAL_CLARO = (226, 232, 236)
METAL_OSCURO = (88, 96, 108)
ROJO = (196, 62, 52)
NEGRO = (35, 27, 27)


class Carrito:
    WIDTH = 26

    def __init__(self, escena="interior", x=600.0, y=300.0):
        self.escena = escena
        self.x, self.y = x, y
        self.empujando = False
        self.ayudante = False       # True mientras Tavo lo está usando
        self.items = []
        self.mira_derecha = False   # hacia dónde queda el manubrio

    # -----------------------------------------------------
    def cerca(self, player, escena):
        return (not self.empujando and not self.ayudante and escena == self.escena
                and math.hypot(player.x - self.x, player.y - self.y) <= DISTANCIA_AGARRAR)

    def cerca_ayudante(self, player, escena):
        """El pulpero está junto al carrito que usa Tavo (se lo puede pedir)."""
        return (self.ayudante and escena == self.escena
                and math.hypot(player.x - self.x, player.y - self.y) <= DISTANCIA_AGARRAR + 6)

    def agarrar(self, player, tom):
        """Empieza a empujar. Lo que traía en las manos entra al carrito."""
        if len(self.items) + len(tom.mano) > CAPACIDAD:
            tom.avisar("¡No cabe todo en el carrito!",
                       "Deja algo antes de agarrarlo.")
            return False
        for item in tom.mano:
            self.items.append(item)
        for item in self.items:
            item["table_id"] = "mano"
        tom.mano = self.items
        tom.MAX_MANOS = CAPACIDAD
        tom.en_carrito = True
        self.empujando = True
        self.player = player
        player.empujando_carrito = True
        return True

    def soltar(self, tom):
        """Lo deja estacionado; los productos se quedan adentro."""
        self.items = tom.mano
        for item in self.items:
            item["table_id"] = "carrito"
        tom.mano = []
        tom.MAX_MANOS = type(tom).MAX_MANOS
        tom.en_carrito = False
        self.empujando = False
        if getattr(self, "player", None) is not None:
            self.player.empujando_carrito = False

    def cambiar_escena(self, escena, player):
        """Al pasar de la sala a la bodega (o al revés) el carrito entra adelante."""
        self.escena = escena
        self.x, self.y = self._objetivo(player)

    @staticmethod
    def _objetivo(player):
        dx, dy = FRENTE.get(player.direction, (0, 12))
        return player.x + dx, player.y + dy

    @staticmethod
    def _huella(x, y):
        """Lo que ocupa el carrito en el piso (ruedas)."""
        return pygame.Rect(round(x) - 11, round(y) - 5, 22, 5)

    def bloquea(self, player, obstaculos, piso_arriba):
        """True si, en la posición actual del personaje, el carrito chocaría."""
        if not self.empujando:
            return False
        x, y = self._objetivo(player)
        huella = self._huella(x, y)
        return huella.top < piso_arriba or huella.collidelist(obstaculos) != -1

    # -----------------------------------------------------
    def seguir(self, player, obstaculos=(), piso_arriba=0):
        """El carrito va al frente del personaje (con un pequeño giro suave)."""
        if not self.empujando:
            return
        x, y = self._objetivo(player)
        huella = self._huella(x, y)
        if huella.top < piso_arriba or huella.collidelist(list(obstaculos)) != -1:
            return  # si al girar chocaría con un mueble, se queda donde está
        self.x += (x - self.x) * 0.45
        self.y += (y - self.y) * 0.45
        if abs(self.x - x) < 0.5 and abs(self.y - y) < 0.5:
            self.x, self.y = x, y
        if player.direction in ("left", "right"):
            # El manubrio queda del lado del personaje.
            self.mira_derecha = player.direction == "left"

    # -----------------------------------------------------
    def dibujar(self, surface, escena):
        if escena != self.escena:
            return
        x, y = round(self.x), round(self.y)
        izq, der = x - 12, x + 12
        canasta = pygame.Rect(izq, y - 19, 24, 11)

        # Sombra y ruedas
        pygame.draw.ellipse(surface, (40, 30, 30), (izq - 1, y - 3, 26, 5))
        for rx in (izq + 3, der - 3):
            pygame.draw.circle(surface, NEGRO, (rx, y - 2), 2)
        pygame.draw.line(surface, METAL_OSCURO, (izq + 3, y - 5), (der - 3, y - 5), 1)
        for rx in (izq + 3, der - 3):
            pygame.draw.line(surface, METAL_OSCURO, (rx, y - 8), (rx, y - 4), 1)

        # Fondo de la canasta
        pygame.draw.rect(surface, METAL_OSCURO, canasta.inflate(2, 2))
        pygame.draw.rect(surface, (120, 130, 140), canasta)

        # Productos adentro (asoman por arriba)
        items = (self.items if not self.empujando else self.items)[:CAPACIDAD]
        for n, item in enumerate(items):
            fila, col = divmod(n, 4)
            w, h = tamano(item["kind"])
            px = izq + 1 + col * 6 + (fila * 3)
            py = canasta.top + 6 - h + fila * 3
            dibujar_producto(surface, item["kind"], px, py)

        # Malla delantera de alambre
        frente = pygame.Rect(izq, y - 14, 24, 7)
        pygame.draw.rect(surface, METAL_OSCURO, frente.inflate(2, 2), 1)
        pygame.draw.rect(surface, METAL, frente, 1)
        for gx in range(frente.left + 3, frente.right - 1, 3):
            pygame.draw.line(surface, METAL, (gx, frente.top), (gx, frente.bottom - 1), 1)
        pygame.draw.line(surface, METAL_CLARO, (frente.left + 1, frente.top), (frente.right - 2, frente.top), 1)
        pygame.draw.line(surface, METAL_CLARO, (canasta.left, canasta.top), (canasta.right - 1, canasta.top), 1)

        # Manubrio rojo del lado del personaje
        mx = der + 1 if self.mira_derecha else izq - 2
        pygame.draw.line(surface, METAL_OSCURO, (mx, y - 8), (mx, y - 22), 2)
        pygame.draw.rect(surface, ROJO, (mx - 2, y - 24, 5, 3))
