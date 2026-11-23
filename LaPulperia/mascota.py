"""Canela, la gata de la pulpería (la mascota de la tienda).

- Pasea por los pasillos de la tienda y a ratos se sienta a mover la cola.
- De vez en cuando sale por la puerta a la calle, camina hasta el costado de
  la pulpería, salta al techo, toma una siesta y luego vuelve a entrar.
- E junto a ella: se deja acariciar ("¡Miau!" y un corazón).
- En el ARMARIO (bodega) se le compran collares y sombreritos
  (ver cosmeticos.py); se dibujan encima de su sprite.
"""
import math
import random

import pygame

from ambiente import sprite_gato
from ayudante import camino, PASILLO_ARRIBA, PASILLO_MEDIO, PASILLO_ABAJO, PUERTA_CALLE
from casa_gato import CAMA, CAMA_Y, OREJAS_PUERTA

NOMBRE = "Canela"
COLOR = (236, 150, 60)
VELOCIDAD = 42.0

# Calle: puerta de la tienda, costado y techo (coordenadas de zonas.dibujar_entrada)
PUERTA_AFUERA = (320, 212)
COSTADO = (470, 204)
ALERO = (476, 92)            # orilla del techo donde cae al saltar
SIESTA = (420, 72)           # lugar del techo donde duerme


def _altura_techo(x):
    """Altura del techo (pendiente derecha) en esa x."""
    return 89 - (480 - x) * (54 / 160)


class Mascota:
    WIDTH = 16

    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.zona = "interior"
        self.x, self.y = 200.0, float(PASILLO_MEDIO)
        self.ruta = []
        self.estado = "sentada"
        self.espera = 3.0
        self.t = 0.0
        self.derecha = True
        self.salto = None          # (desde, hasta, duración, transcurrido)
        self.globo = None
        self.globo_t = 0.0
        self.paseos = 0            # paseos dentro antes de salir
        self.globo_arriba = 0      # sube el globo si otro está en el mismo lugar
        self.velocidad = VELOCIDAD  # más rápido cuando persigue o huye
        self.color = COLOR         # pelaje (cosméticos)
        self.nivel_casa = 0        # el juego le avisa qué casa tiene
        self.collar = None         # (color, adorno) del collar
        self.sombrero = None       # "moño", "lana", "fiesta", "bruja", "corona"

    # -----------------------------------------------------
    def actualizar(self, dt):
        self.t += dt
        if self.globo_t > 0:
            self.globo_t -= dt
            if self.globo_t <= 0:
                self.globo = None
        if self.salto is not None:
            desde, hasta, dur, pasado = self.salto
            pasado += dt
            f = min(1.0, pasado / dur)
            self.x = desde[0] + (hasta[0] - desde[0]) * f
            self.y = desde[1] + (hasta[1] - desde[1]) * f - math.sin(math.pi * f) * 26
            self.salto = (desde, hasta, dur, pasado)
            if f >= 1:
                self.salto = None
                self.x, self.y = hasta
            return
        if self.ruta:
            self._caminar(dt)
            return
        if self.espera > 0:
            self.espera -= dt
            return
        self._decidir()

    def _caminar(self, dt):
        tx, ty = self.ruta[0]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        paso = self.velocidad * dt
        if abs(dx) > 0.5:
            self.derecha = dx > 0
        if dist <= paso:
            self.x, self.y = tx, ty
            self.ruta.pop(0)
        else:
            self.x += dx / dist * paso
            self.y += dy / dist * paso

    def _decidir(self):
        """Qué hace ahora, según dónde está."""
        e = self.estado
        if self.zona == "interior":
            if e == "a_la_puerta":
                # Sale a la calle.
                self.zona = "entrada"
                self.x, self.y = PUERTA_AFUERA
                self.estado = "al_costado"
                self.ruta = [COSTADO]
                return
            if e == "a_casa":
                # Llegó a su casa: se acuesta a dormir un rato (adentro).
                self.estado = "en_casa"
                self.y = CAMA_Y.get(self.nivel_casa, CAMA[1])
                self.espera = random.uniform(10, 18)
                return
            if e != "en_casa" and self.paseos >= 2 and random.random() < 0.25:
                self.estado = "a_casa"
                self.ruta = camino((self.x, self.y), (CAMA[0], PASILLO_ABAJO)) + [CAMA]
                return
            if self.paseos >= 3 and random.random() < 0.5:
                self.paseos = 0
                self.estado = "a_la_puerta"
                self.ruta = camino((self.x, self.y), PUERTA_CALLE)
                return
            if e == "paseando" or random.random() < 0.35:
                # Se sienta un rato a mover la cola.
                self.estado = "sentada"
                self.espera = random.uniform(3, 8)
                return
            self.paseos += 1
            self.estado = "paseando"
            destino = (random.uniform(40, 560),
                       random.choice((PASILLO_ARRIBA, PASILLO_MEDIO, PASILLO_ABAJO)))
            self.ruta = camino((self.x, self.y), destino)
            return
        # En la calle
        if e == "al_costado":
            self.estado = "subiendo"
            self.salto = ((self.x, self.y), ALERO, 0.7, 0.0)
        elif e == "subiendo":
            self.estado = "al_techo"
            self.ruta = [(SIESTA[0], _altura_techo(SIESTA[0]))]
        elif e == "al_techo":
            self.estado = "siesta"
            self.espera = random.uniform(12, 22)
        elif e == "siesta":
            self.estado = "bajando_techo"
            self.ruta = [ALERO]
        elif e == "bajando_techo":
            self.estado = "bajando"
            self.salto = ((self.x, self.y), COSTADO, 0.6, 0.0)
        elif e == "bajando":
            self.estado = "volviendo"
            self.ruta = [PUERTA_AFUERA]
        else:  # volviendo: entra a la tienda
            self.zona = "interior"
            self.x, self.y = PUERTA_CALLE
            self.estado = "paseando"
            self.ruta = camino(PUERTA_CALLE, (random.uniform(80, 520), PASILLO_ABAJO))

    # -----------------------------------------------------
    def cerca(self, player, zona):
        return (self.zona == zona and self.salto is None and self.y > 150
                and math.hypot(player.x - self.x, player.y - self.y) <= 26)

    def acariciar(self):
        self.ruta = []
        self.velocidad = VELOCIDAD
        self.estado = "sentada"
        self.espera = 3.0
        self.globo = random.choice(("¡Miau!", "¡Prrr!", "¡Miau, miau!"))
        self.globo_t = 2.0

    # -----------------------------------------------------
    def dibujar(self, surface, escena="interior"):
        if escena != self.zona:
            return
        if self.estado == "en_casa" and self.nivel_casa in OREJAS_PUERTA:
            # Dormida dentro de la casita / el castillo: solo asoman las orejas.
            cx, cy = OREJAS_PUERTA[self.nivel_casa]
            for lado in (-1, 1):
                puntos = [(cx + lado * 2, cy + 3), (cx + lado * 6, cy + 3), (cx + lado * 4, cy - 2)]
                pygame.draw.polygon(surface, self.color, puntos)
                pygame.draw.polygon(surface, (40, 30, 30), puntos, 1)
            self._zzz(surface, pygame.Rect(cx - 8, cy - 4, 16, 8))
            return
        caminando = bool(self.ruta) or self.salto is not None
        frame = int(self.t * (6 if caminando else 1.5)) % 2
        img = sprite_gato(self.color, frame, caminando, self.derecha)
        rect = img.get_rect(midbottom=(round(self.x), round(self.y)))
        if self.salto is None:
            pygame.draw.ellipse(surface, (55, 48, 43), (rect.centerx - 7, rect.bottom - 3, 14, 4))
        surface.blit(img, rect)
        self._accesorios(surface, rect, caminando)
        if self.estado in ("siesta", "en_casa"):
            self._zzz(surface, rect)

    def dibujar_globo(self, surface, escena):
        """El "¡Miau!" va encima de todo (se dibuja al final)."""
        if self.globo and escena == self.zona:
            img = sprite_gato(self.color, 0, False, self.derecha)
            self._dibujar_globo(surface, img.get_rect(midbottom=(round(self.x), round(self.y))))

    def _zzz(self, surface, rect):
        z = int(self.t * 1.5) % 3
        fuente = pygame.font.Font(None, 12)
        for i in range(z + 1):
            t = fuente.render("z", True, (240, 240, 250))
            surface.blit(t, (rect.right + i * 4, rect.top - 4 - i * 5))

    def _accesorios(self, surface, rect, caminando):
        """Collar y sombrerito comprados en el armario."""
        if caminando:
            # De lado: cabeza adelante (a la derecha si mira a la derecha).
            cabeza_x = rect.x + (24 if self.derecha else 4)
            cabeza_y = rect.y + 1
            cuello = (rect.x + (19 if self.derecha else 5), rect.y + 8, 4, 3)
        else:
            cabeza_x = rect.x + (6 if self.derecha else 10)
            cabeza_y = rect.y + 1
            cuello = (rect.x + 3 if self.derecha else rect.x + 5, rect.y + 9, 8, 2)
        if self.collar:
            color, adorno = self.collar
            pygame.draw.rect(surface, color, cuello)
            medio = (cuello[0] + cuello[2] // 2, cuello[1] + cuello[3])
            if adorno == "cascabel":
                pygame.draw.circle(surface, (176, 128, 30), (medio[0], medio[1] + 1), 3)
                pygame.draw.circle(surface, (250, 214, 70), (medio[0], medio[1] + 1), 2)
            elif adorno == "flores":
                for dx, c in ((-3, (255, 220, 60)), (0, (250, 120, 170)), (3, (120, 200, 255))):
                    pygame.draw.circle(surface, c, (medio[0] + dx, cuello[1] + 1), 2)
            elif adorno == "diamantes":
                for dx in (-3, 0, 3):
                    pygame.draw.rect(surface, (255, 255, 255), (medio[0] + dx, cuello[1], 1, 1))
                pygame.draw.polygon(surface, (170, 220, 255), [(medio[0], medio[1]), (medio[0] - 2, medio[1] + 2),
                                                              (medio[0], medio[1] + 4), (medio[0] + 2, medio[1] + 2)])
            else:
                pygame.draw.rect(surface, (250, 220, 90), (medio[0] - 1, medio[1], 2, 2))
        dibujar_sombrero_gato(surface, self.sombrero, cabeza_x, cabeza_y)

    def _dibujar_globo(self, surface, rect):
        fuente = pygame.font.Font(None, 14)
        t = fuente.render(self.globo, True, (84, 50, 39))
        caja = t.get_rect(midbottom=(rect.centerx, rect.top - 6 - self.globo_arriba)).inflate(10, 6)
        pygame.draw.rect(surface, (245, 226, 177), caja)
        pygame.draw.rect(surface, (84, 50, 39), caja, 1)
        surface.blit(t, t.get_rect(center=caja.center))
        if self.estado in ("huyendo", "persiguiendo"):
            return          # en la persecución no hay corazón (¡Fsss! / ¡Guau!)
        # Corazón
        cx, cy = caja.right + 6, caja.centery
        pygame.draw.circle(surface, (220, 60, 80), (cx - 2, cy - 1), 2)
        pygame.draw.circle(surface, (220, 60, 80), (cx + 2, cy - 1), 2)
        pygame.draw.polygon(surface, (220, 60, 80), [(cx - 4, cy), (cx + 4, cy), (cx, cy + 4)])


def dibujar_sombrero_gato(surface, sombrero, cx, top):
    """cx: centro de la cabeza; top: arriba de las orejas.
    sombrero puede ser "moño" o ("moño", color) para otro color."""
    color = None
    if isinstance(sombrero, tuple):
        sombrero, color = sombrero
    oscurecer = lambda c: tuple(round(v * 0.65) for v in c)
    aclarar = lambda c: tuple(round(v + (255 - v) * 0.4) for v in c)
    if sombrero == "moño":
        rosa = color or (240, 120, 170)
        oscuro = oscurecer(rosa) if color else (170, 60, 110)
        pygame.draw.polygon(surface, rosa, [(cx - 5, top - 2), (cx, top + 1), (cx - 5, top + 4)])
        pygame.draw.polygon(surface, rosa, [(cx + 5, top - 2), (cx, top + 1), (cx + 5, top + 4)])
        pygame.draw.rect(surface, oscuro, (cx - 1, top, 3, 3))
    elif sombrero == "fiesta":
        pygame.draw.polygon(surface, color or (80, 150, 220), [(cx - 4, top + 2), (cx + 4, top + 2), (cx, top - 8)])
        pygame.draw.line(surface, (250, 220, 90), (cx - 2, top - 2), (cx + 2, top - 2), 1)
        pygame.draw.circle(surface, (240, 90, 80), (cx, top - 9), 2)
    elif sombrero == "lana":
        lana = color or (60, 120, 80)
        pygame.draw.rect(surface, lana, (cx - 5, top - 3, 10, 5))
        pygame.draw.rect(surface, aclarar(lana) if color else (110, 180, 130), (cx - 5, top + 1, 10, 1))
        pygame.draw.circle(surface, (240, 240, 236), (cx, top - 4), 2)
    elif sombrero == "bruja":
        pygame.draw.rect(surface, (40, 30, 50), (cx - 7, top + 1, 14, 2))
        pygame.draw.polygon(surface, (40, 30, 50), [(cx - 4, top + 1), (cx + 4, top + 1), (cx + 3, top - 9)])
        pygame.draw.rect(surface, (150, 80, 190), (cx - 4, top - 1, 8, 2))
    elif sombrero == "corona":
        oro, oscuro = (250, 206, 70), (170, 120, 30)
        pygame.draw.polygon(surface, oro, [(cx - 5, top + 2), (cx - 5, top - 4), (cx - 2, top - 1),
                                           (cx, top - 5), (cx + 2, top - 1), (cx + 5, top - 4),
                                           (cx + 5, top + 2)])
        pygame.draw.lines(surface, oscuro, False, [(cx - 5, top + 2), (cx + 5, top + 2)], 1)
