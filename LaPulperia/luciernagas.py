"""Luciérnagas que vuelan dentro de la tienda.

Son pocas y pequeñitas: un puntito amarillo verdoso con un brillo suave que
se prende y se apaga. Vuelan despacio, cambiando de rumbo poco a poco. De
noche brillan más (se dibujan después de oscurecer la escena).
"""
import math
import random

import pygame

CANTIDAD = 5
ZONA = pygame.Rect(16, 96, 608, 244)   # dónde pueden volar (coordenadas 640 x 360)
VELOCIDAD = 14.0                       # px por segundo
COLOR = (214, 255, 120)
RADIO_BRILLO = 6


NIVELES = 10   # halos pre-dibujados con distinta intensidad


def _halos():
    """Halos que SUMAN luz (se dibujan con BLEND_RGB_ADD), de tenue a fuerte."""
    tam = RADIO_BRILLO * 2 + 1
    lista = []
    for n in range(1, NIVELES + 1):
        s = pygame.Surface((tam, tam))
        s.fill((0, 0, 0))
        for r in range(RADIO_BRILLO, 0, -1):
            f = (1 - r / RADIO_BRILLO) ** 1.4 * (n / NIVELES)
            pygame.draw.circle(s, tuple(round(c * 0.55 * f) for c in COLOR), (RADIO_BRILLO, RADIO_BRILLO), r)
        lista.append(s)
    return lista


class Luciernaga:
    def __init__(self, rng, zona=ZONA):
        self.rng = rng
        self.zona = zona
        self.x = rng.uniform(zona.left, zona.right)
        self.y = rng.uniform(zona.top, zona.bottom)
        self.rumbo = rng.uniform(0, math.tau)
        self.fase = rng.uniform(0, math.tau)
        self.ritmo = rng.uniform(1.2, 2.2)       # qué tan rápido parpadea
        self.t = 0.0

    def actualizar(self, dt):
        self.t += dt
        # Gira un poquito al azar, y hacia el centro si se acerca a un borde.
        self.rumbo += self.rng.uniform(-2.2, 2.2) * dt
        zona = self.zona
        if not zona.inflate(-30, -30).collidepoint(self.x, self.y):
            hacia_centro = math.atan2(zona.centery - self.y, zona.centerx - self.x)
            diferencia = (hacia_centro - self.rumbo + math.pi) % math.tau - math.pi
            self.rumbo += diferencia * min(1.0, dt * 1.5)
        # Pequeño vaivén vertical para que parezca que revolotea.
        vaiven = math.sin(self.t * 5 + self.fase) * 4
        self.x += math.cos(self.rumbo) * VELOCIDAD * dt
        self.y += (math.sin(self.rumbo) * VELOCIDAD + vaiven) * dt
        self.x = max(zona.left, min(zona.right, self.x))
        self.y = max(zona.top, min(zona.bottom, self.y))

    @property
    def intensidad(self):
        """0..1: se prende y se apaga suavemente (a ratos queda apagada)."""
        onda = math.sin(self.t * self.ritmo + self.fase)
        return max(0.0, onda) ** 1.5


class Luciernagas:
    def __init__(self, cantidad=CANTIDAD, semilla=None, zona=ZONA, solo_de_noche=False):
        rng = random.Random(semilla)
        self.lista = [Luciernaga(rng, zona) for _ in range(cantidad)]
        self.solo_de_noche = solo_de_noche
        self._halo = None

    def actualizar(self, dt):
        for l in self.lista:
            l.actualizar(dt)

    def dibujar(self, surface, noche=0.0):
        """noche: 0 de día, 1 de noche (de noche se ven más)."""
        if self._halo is None:
            self._halo = _halos()
        if self.solo_de_noche:
            if noche <= 0.05:
                return          # de día no hay (afuera solo salen de noche)
            fuerza = noche
        else:
            fuerza = 0.65 + 0.35 * noche
        for l in self.lista:
            x, y = round(l.x), round(l.y)
            i = l.intensidad * fuerza
            if i <= 0.03:
                surface.set_at((x, y), (70, 64, 40))   # apagada: solo el cuerpito
                continue
            nivel = max(1, min(NIVELES, round(i * NIVELES)))
            surface.blit(self._halo[nivel - 1], (x - RADIO_BRILLO, y - RADIO_BRILLO),
                         special_flags=pygame.BLEND_RGB_ADD)
            nucleo = tuple(round(90 + (c - 90) * min(1.0, i * 1.3)) for c in (255, 255, 170))
            pygame.draw.rect(surface, nucleo, (x, y, 2, 2) if i > 0.45 else (x, y, 1, 1))
