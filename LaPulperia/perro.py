"""Bruno, el perro de la pulpería (opcional, como Canela).

- Pasea por los pasillos de la tienda y se sienta a ratos.
- A veces sale a la calle y se echa a dormir en la acera, junto a la puerta.
- E junto a él: "¡Guau!" y un corazón.
- En el ARMARIO se le compran pelaje, collares y TRAJES (dinosaurio, abeja,
  tiburón, superhéroe, unicornio...): ver cosmeticos.py.
"""
import random

import pygame

from ambiente import sprite_perro
from ayudante import camino, PASILLO_ARRIBA, PASILLO_MEDIO, PASILLO_ABAJO, PUERTA_CALLE
from mascota import Mascota, PUERTA_AFUERA

NOMBRE = "Bruno"
COLOR = (176, 120, 70)
TAPETE = (252, 214)          # en la acera, a la izquierda de la puerta
_cache = {}


class Perro(Mascota):
    WIDTH = 28

    def reiniciar(self):
        super().reiniciar()
        self.x, self.y = 420.0, float(PASILLO_ABAJO)
        self.color = COLOR
        self.collar = None      # (color, adorno)
        self.traje = None       # "dino_verde", "abeja", ...

    def _decidir(self):
        e = self.estado
        if self.zona == "interior":
            if e == "a_la_puerta":
                self.zona = "entrada"
                self.x, self.y = PUERTA_AFUERA
                self.estado = "al_tapete"
                self.ruta = [TAPETE]
                return
            if self.paseos >= 3 and random.random() < 0.45:
                self.paseos = 0
                self.estado = "a_la_puerta"
                self.ruta = camino((self.x, self.y), PUERTA_CALLE)
                return
            if e == "paseando" or random.random() < 0.35:
                self.estado = "sentada"
                self.espera = random.uniform(3, 8)
                return
            self.paseos += 1
            self.estado = "paseando"
            destino = (random.uniform(40, 560),
                       random.choice((PASILLO_ARRIBA, PASILLO_MEDIO, PASILLO_ABAJO)))
            self.ruta = camino((self.x, self.y), destino)
            return
        # En la calle: se echa en la acera y luego vuelve a entrar.
        if e == "al_tapete":
            self.estado = "siesta"
            self.derecha = True
            self.espera = random.uniform(12, 20)
        elif e == "siesta":
            self.estado = "volviendo"
            self.ruta = [PUERTA_AFUERA]
        else:
            self.zona = "interior"
            self.x, self.y = PUERTA_CALLE
            self.estado = "paseando"
            self.ruta = camino(PUERTA_CALLE, (random.uniform(80, 520), PASILLO_ABAJO))

    def cerca(self, player, zona):
        return (self.zona == zona and abs(player.x - self.x) <= 30
                and abs(player.y - self.y) <= 22)

    def acariciar(self):
        super().acariciar()
        self.globo = random.choice(("¡Guau!", "¡Guau, guau!", "¡Arf!"))

    # -----------------------------------------------------
    def _imagen(self, frame):
        clave = (self.color, self.collar, self.traje, frame, self.derecha)
        if clave not in _cache:
            _cache[clave] = imagen_perro(self.color, self.collar, self.traje, frame, self.derecha)
        return _cache[clave]

    def dibujar(self, surface, escena="interior"):
        if escena != self.zona:
            return
        caminando = bool(self.ruta)
        frame = int(self.t * 6) % 2 if caminando else 0
        img = self._imagen(frame)
        rect = img.get_rect(midbottom=(round(self.x), round(self.y)))
        pygame.draw.ellipse(surface, (55, 48, 43), (rect.centerx - 12, rect.bottom - 3, 24, 5))
        surface.blit(img, rect)
        if self.estado == "siesta":
            z = int(self.t * 1.5) % 3
            fuente = pygame.font.Font(None, 12)
            for i in range(z + 1):
                t = fuente.render("z", True, (240, 240, 250))
                surface.blit(t, (rect.right - 2 + i * 4, rect.top - 2 - i * 5))

    def dibujar_globo(self, surface, escena):
        if self.globo and escena == self.zona:
            img = self._imagen(0)
            self._dibujar_globo(surface, img.get_rect(midbottom=(round(self.x), round(self.y))))


def _oscuro(c, f=0.3):
    return tuple(round(v * (1 - f)) for v in c)


# Color del cuerpo de cada traje (el resto se dibuja encima).
COLOR_TRAJE = {
    "dino_verde": (96, 176, 80), "dino_morado": (150, 100, 200), "abeja": (250, 206, 60),
    "tiburon": (130, 150, 170), "unicornio": (246, 242, 250),
}


def imagen_perro(color, collar, traje, frame, derecha):
    """El perro (mirando a la derecha) con su collar y su traje; luego se
    voltea si mira a la izquierda. Sprite de 32 x 18."""
    color_traje = None
    if isinstance(traje, tuple):            # ("suéter", color)
        traje, color_traje = traje
    base = sprite_perro(COLOR_TRAJE.get(traje, color), frame, True)
    s = pygame.Surface((base.get_width() + 8, base.get_height() + 10), pygame.SRCALPHA)
    ox, oy = 4, 10                      # margen para cuernos, aletas y capas
    s.blit(base, (ox, oy))

    def r(color_, x, y, w, h):
        pygame.draw.rect(s, color_, (ox + x, oy + y, w, h))

    def tri(color_, puntos):
        pygame.draw.polygon(s, color_, [(ox + x, oy + y) for x, y in puntos])

    if traje in ("suéter", "impermeable"):
        c = color_traje or ((200, 60, 60) if traje == "suéter" else (250, 210, 50))
        r(c, 6, 9, 16, 4)
        r(_oscuro(c), 6, 13, 16, 1)
        if traje == "suéter":
            for x in (9, 14, 19):
                r((250, 240, 230), x, 10, 2, 2)
        else:
            r(_oscuro(c), 20, 2, 7, 3)     # capucha
    elif traje in ("dino_verde", "dino_morado"):
        pico = (250, 150, 50) if traje == "dino_verde" else (250, 214, 70)
        for x in range(4, 22, 4):
            tri(pico, [(x, 9), (x + 2, 4), (x + 4, 9)])
        for x in (21, 25):
            tri(pico, [(x, 2), (x + 1, -2), (x + 3, 2)])
        r((250, 250, 250), 27, 6, 2, 1)    # dientitos
    elif traje == "abeja":
        for x in (8, 13, 18):
            r((40, 32, 30), x, 9, 3, 5)
        pygame.draw.ellipse(s, (220, 240, 255), (ox + 9, oy - 2, 9, 8))
        pygame.draw.ellipse(s, (180, 210, 240), (ox + 9, oy - 2, 9, 8), 1)
        for x in (23, 27):
            pygame.draw.line(s, (40, 32, 30), (ox + x, oy + 1), (ox + x - 1, oy - 4), 1)
            pygame.draw.circle(s, (40, 32, 30), (ox + x - 1, oy - 5), 1)
    elif traje == "tiburon":
        tri((110, 128, 148), [(10, 9), (15, -2), (18, 9)])
        r((236, 240, 244), 4, 13, 20, 2)
        for x in (25, 27, 29):
            tri((250, 250, 250), [(x, 7), (x + 1, 9), (x + 2, 7)])
    elif traje == "superheroe":
        tri((210, 40, 50), [(20, 7), (0, 6), (-2, 16), (14, 13)])
        r((250, 214, 70), 12, 9, 4, 3)
        r((40, 40, 60), 23, 3, 7, 2)       # antifaz
    elif traje == "unicornio":
        tri((250, 214, 70), [(26, 1), (28, -7), (29, 1)])
        for i, c in enumerate(((240, 80, 80), (250, 170, 60), (250, 230, 80), (110, 200, 110),
                               (90, 150, 240), (170, 110, 220))):
            r(c, 19 - i, 2 + i, 3, 2)
    if collar:
        color_c, adorno = collar
        if adorno == "pañoleta":
            tri(color_c, [(20, 6), (25, 6), (22, 11)])
            r((250, 250, 250), 21, 7, 1, 1)
        else:
            r(color_c, 20, 5, 3, 5)
            if adorno == "hueso":
                r((250, 246, 230), 21, 10, 3, 2)
            elif adorno == "picos":
                for y in (5, 8):
                    r((220, 220, 230), 19, y, 1, 1)
            else:
                r((250, 220, 90), 21, 10, 2, 2)
    return s if derecha else pygame.transform.flip(s, True, False)
