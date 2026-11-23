"""Vida en la calle: personas, autos, perros, gatos y pájaros.

Todo se dibuja en pixel art (cuadrículas de texto, como productos.py) y se
mueve solo mientras el niño está en la calle. Detalles:
  - Personas por las aceras; algunas saludan al niño por su nombre.
  - Autos en dos carriles; frenan y pitan si el niño está enfrente.
    De noche llevan los faros encendidos.
  - Perros paseando, gatos sentados que mueven la cola, pájaros en el cielo.
"""
import math
import random

import pygame

# ---------------------------------------------------------
# GEOMETRÍA DE LA CALLE (coordenadas 640 x 360)
# ---------------------------------------------------------
ACERA_ARRIBA = 236      # pies de quienes caminan por la acera de la tienda
POSTE = (236, 243)      # base del poste de luz (en la orilla de la acera)
FAROL = (POSTE[0] + 11, POSTE[1] - 66)   # la lámpara, colgando del brazo
ACERA_ABAJO = 356       # acera de enfrente (borde inferior)
CARRIL_IZQ = 272        # base de los autos que van a la izquierda
CARRIL_DER = 318        # base de los autos que van a la derecha
CIELO = (14, 110)       # franja donde vuelan los pájaros
JARDIN = [(70, 198), (214, 200), (520, 200), (600, 198)]   # donde se sientan los gatos
PASEO_GATO = 28        # los gatos no se alejan más que esto de su lugar

# ---------------------------------------------------------
# SPRITES
# ---------------------------------------------------------
CONTORNO = (40, 30, 34)

PERRO = [
    [
        "...........oo...",
        "..........oBBo..",
        "o.........oBBBoo",
        "Bo........oBeBBn",
        "oBoooooooooBBBBo",
        ".oBBBBBBBBBBBoo.",
        ".oBBBBBBBBBBo...",
        ".oBo.oBooBo.oBo.",
        ".oo..oo..oo..oo.",
    ],
    [
        "...........oo...",
        "..........oBBo..",
        ".o........oBBBoo",
        "oBo.......oBeBBn",
        "oBoooooooooBBBBo",
        ".oBBBBBBBBBBBoo.",
        ".oBBBBBBBBBBo...",
        "..oBooBo.oBooBo.",
        "..oo.oo..oo.oo..",
    ],
]

GATO_SENTADO = [
    [
        "..o.o...",
        ".oCoCo..",
        ".oCCCo..",
        ".oeCeo..",
        "..oCo...",
        ".oCCCo..",
        "oCCCCCo.",
        "oCCCCCoo",
        "oCCCCCoC",
        ".ooooooo",
    ],
    [
        "..o.o...",
        ".oCoCo..",
        ".oCCCo..",
        ".oeCeo..",
        "..oCo...",
        ".oCCCo..",
        "oCCCCCo.",
        "oCCCCCo.",
        "oCCCCCoC",
        ".oooooCo",
    ],
]

GATO_CAMINA = [
    [
        "o..........o.o",
        "Co........oCoC",
        "oCo.......oCCC",
        ".oCooooooooeCe",
        "..oCCCCCCCCCCo",
        "..oCCCCCCCCCo.",
        "..oCo.oCoCo.o.",
        "..oo..oo.oo...",
    ],
    [
        ".o.........o.o",
        "oC........oCoC",
        "oCo.......oCCC",
        ".oCooooooooeCe",
        "..oCCCCCCCCCCo",
        "..oCCCCCCCCCo.",
        "...oCoCo.oCo..",
        "...oo.oo.oo...",
    ],
]

PAJARO = [
    [
        "o.....o",
        "Bo...oB",
        ".BoooB.",
        "..oBo..",
    ],
    [
        ".......",
        "..ooo..",
        "oBBoBBo",
        "o..o..o",
    ],
]

AUTO = [
    "...........oooooooooooo.........",
    "..........oWWWoWWWWWoWWo........",
    ".........oWWWWoWWWWWoWWWo.......",
    "...ooooooCCCCCCCCCCCCCCCCoooo...",
    "..oCCCCCCCCCCCCCCCCCCCCCCCCCCo..",
    ".oCCCCCCCCCCCCCCCCCCCCCCCCCCCLo.",
    ".oCCCCCCCCCCCCCCCCCCCCCCCCCCCCo.",
    ".oDDDDooooDDDDDDDDDDDDDooooDDDo.",
    "....oGGGGo...........oGGGGo.....",
    "....oGggGo...........oGggGo.....",
    ".....oooo.............oooo......",
]

COLORES_PERRO = [(176, 120, 70), (230, 214, 186), (70, 56, 50), (214, 170, 96)]
COLORES_GATO = [(236, 150, 60), (90, 90, 96), (240, 236, 226), (60, 50, 46)]
COLORES_AUTO = [(208, 64, 58), (64, 116, 196), (238, 196, 64), (90, 170, 104),
                (236, 236, 232), (150, 92, 176)]
SALUDOS = ["¡Hola, {n}!", "¡Buenos días, {n}!", "¡Adiós, {n}!", "¡Qué linda tu pulpería!"]

_cache = {}


def _oscurecer(c, f=0.7):
    return tuple(round(x * f) for x in c)


ESCALA = 2  # los animales y autos se dibujan al doble para que tengan proporción


def _construir(filas, colores):
    clave = (tuple(filas), tuple(sorted(colores.items())))
    if clave not in _cache:
        w = max(len(f) for f in filas)
        surf = pygame.Surface((w, len(filas)), pygame.SRCALPHA)
        for y, fila in enumerate(filas):
            for x, ch in enumerate(fila):
                if ch != "." and ch in colores:
                    surf.set_at((x, y), colores[ch])
        _cache[clave] = pygame.transform.scale_by(surf, ESCALA)
    return _cache[clave]


def sprite_perro(color, frame, derecha):
    s = _construir(PERRO[frame], {"o": CONTORNO, "B": color, "e": (20, 20, 20), "n": (30, 24, 24)})
    return s if derecha else pygame.transform.flip(s, True, False)


def sprite_gato(color, frame, caminando, derecha=True):
    filas = (GATO_CAMINA if caminando else GATO_SENTADO)[frame]
    ojos = (120, 200, 90)
    s = _construir(filas, {"o": CONTORNO, "C": color, "e": ojos})
    return s if derecha else pygame.transform.flip(s, True, False)


def sprite_pajaro(frame, color=(60, 60, 72)):
    return _construir(PAJARO[frame], {"o": CONTORNO, "B": color})


def sprite_auto(color, giro, derecha):
    cubo = (150, 150, 156) if giro == 0 else (110, 110, 116)
    s = _construir(AUTO, {"o": CONTORNO, "C": color, "D": _oscurecer(color), "W": (170, 214, 236),
                          "L": (255, 232, 140), "G": (36, 34, 40), "g": cubo})
    return s if derecha else pygame.transform.flip(s, True, False)


# ---------------------------------------------------------
# HABITANTES DE LA CALLE
# ---------------------------------------------------------
class Habitante:
    def __init__(self, tipo, x, y, vx, **datos):
        self.tipo, self.x, self.y, self.vx = tipo, float(x), float(y), vx
        self.t = random.random() * 2
        self.datos = datos
        self.burbuja = None
        self.burbuja_t = 0.0

    @property
    def derecha(self):
        return self.vx >= 0


class Calle:
    def __init__(self):
        self.lista = []
        self.esperas = {"persona": 1.0, "auto": 2.0, "perro": 4.0, "pajaros": 1.5}
        self._gatos_listos = False

    # -----------------------------------------------------
    def poblar(self, player, noche):
        """Al salir de la tienda la calle ya tiene vida (no aparece vacía)."""
        if not self.lista:
            for _ in range(int(8 / 0.1)):
                self.actualizar(0.1, player, noche, saludar=False)

    def _nuevo(self, tipo, noche):
        lado = random.choice((-1, 1))
        x0 = -30 if lado > 0 else 670
        if tipo == "persona":
            from clientes import PERSONAJES, crear_persona
            datos = random.choice(PERSONAJES)
            persona = crear_persona(datos)
            y = random.choice((ACERA_ARRIBA, ACERA_ABAJO))
            self.lista.append(Habitante("persona", x0, y, lado * random.uniform(28, 40),
                                        persona=persona, saludo=random.random() < 0.6))
        elif tipo == "auto":
            derecha = random.choice((True, False))
            y = CARRIL_DER if derecha else CARRIL_IZQ
            x = -40 if derecha else 680
            self.lista.append(Habitante("auto", x, y, (1 if derecha else -1) * random.uniform(80, 120),
                                        color=random.choice(COLORES_AUTO), pito=0.0))
        elif tipo == "perro":
            y = random.choice((ACERA_ARRIBA - 2, ACERA_ABAJO - 2))
            self.lista.append(Habitante("perro", x0, y, lado * random.uniform(34, 48),
                                        color=random.choice(COLORES_PERRO)))
        elif tipo == "pajaros" and not noche:
            y = random.uniform(*CIELO)
            for i in range(random.randint(1, 3)):
                self.lista.append(Habitante("pajaro", x0 - lado * i * 14, y + random.uniform(-8, 8),
                                            lado * random.uniform(46, 62)))

    def _poner_gatos(self):
        for x, y in random.sample(JARDIN, 2):
            self.lista.append(Habitante("gato", x, y, 0.0, color=random.choice(COLORES_GATO),
                                        casa=(x, y), paseo=random.uniform(6, 14)))
        self._gatos_listos = True

    # -----------------------------------------------------
    def actualizar(self, dt, player, noche, saludar=True, nombre=""):
        if not self._gatos_listos:
            self._poner_gatos()
        # Aparecer gente, autos, perros y pájaros de vez en cuando.
        maximos = {"persona": 1 if noche else 3, "auto": 2, "perro": 1, "pajaros": 0 if noche else 4}
        for tipo, maximo in maximos.items():
            contar = "pajaro" if tipo == "pajaros" else tipo
            self.esperas[tipo] -= dt
            if self.esperas[tipo] <= 0:
                if sum(1 for h in self.lista if h.tipo == contar) < maximo:
                    self._nuevo(tipo, noche)
                self.esperas[tipo] = random.uniform(2.5, 6.0)

        for h in self.lista:
            h.t += dt
            if h.burbuja_t > 0:
                h.burbuja_t -= dt
            if h.tipo == "auto":
                self._mover_auto(h, dt, player)
            elif h.tipo == "gato":
                self._mover_gato(h, dt)
            else:
                h.x += h.vx * dt
                if h.tipo == "pajaro":
                    h.y += math.sin(h.t * 3) * 6 * dt
            if (h.tipo == "persona" and saludar and h.datos["saludo"] and nombre
                    and abs(h.x - player.x) < 34 and abs(h.y - player.y) < 30):
                h.datos["saludo"] = False
                h.burbuja = random.choice(SALUDOS).format(n=nombre)
                h.burbuja_t = 2.2

        self.lista = [h for h in self.lista if -60 <= h.x <= 700]

    def _mover_auto(self, h, dt, player):
        sentido = 1 if h.vx > 0 else -1
        # Si el niño está enfrente, en su carril, el auto frena y pita.
        adelante = (player.x - h.x) * sentido
        en_carril = h.y - 26 <= player.y <= h.y + 8
        # Tampoco choca con el auto de adelante en su mismo carril.
        auto_adelante = any(
            o is not h and o.tipo == "auto" and o.y == h.y and 0 < (o.x - h.x) * sentido < 80
            for o in self.lista)
        if en_carril and 0 < adelante < 90:
            if h.datos["pito"] <= 0:
                h.burbuja, h.burbuja_t = "¡Pi, pi!", 1.4
                h.datos["pito"] = 3.0
        elif not auto_adelante:
            h.x += h.vx * dt
        h.datos["pito"] -= dt

    def _mover_gato(self, h, dt):
        d = h.datos
        d["paseo"] -= dt
        if h.vx == 0 and d["paseo"] <= 0:
            # A veces el gato se levanta a dar una vuelta corta.
            h.vx = random.choice((-1, 1)) * 18
            d["paseo"] = random.uniform(2.0, 3.5)
        elif h.vx != 0:
            h.x += h.vx * dt
            if abs(h.x - d["casa"][0]) > PASEO_GATO:
                h.vx = -h.vx   # da la vuelta: no se aleja de su lugar
                h.x += h.vx * dt
            if d["paseo"] <= 0:
                h.vx = 0.0
                d["paseo"] = random.uniform(8, 16)

    # -----------------------------------------------------
    def dibujar_cielo(self, surface):
        for h in self.lista:
            if h.tipo == "pajaro":
                img = sprite_pajaro(int(h.t * 6) % 2)
                if h.vx < 0:
                    img = pygame.transform.flip(img, True, False)
                surface.blit(img, (round(h.x), round(h.y)))

    def dibujar(self, surface, player, dibujar_jugador, extras=()):
        """Dibuja la calle y al jugador ordenados por profundidad (pies).

        extras: [(y, función)] para cosas del juego (camión, cajas...).
        """
        cosas = [(h.y, lambda h=h: self._dibujar(surface, h)) for h in self.lista if h.tipo != "pajaro"]
        cosas.append((player.y, dibujar_jugador))
        cosas.append((POSTE[1], lambda: dibujar_poste(surface)))
        cosas.extend(extras)
        cosas.sort(key=lambda par: par[0])
        for _, dibujar in cosas:
            dibujar()

    def dibujar_farol(self, surface, noche):
        """De noche el farol se enciende: bombillo brillante y su halo."""
        if noche <= 0.05:
            return
        x, y = FAROL
        radio = 18
        halo = pygame.Surface((radio * 2, radio * 2))
        halo.fill((0, 0, 0))
        for r in range(radio, 0, -1):
            f = (1 - r / radio) ** 1.6 * noche
            pygame.draw.circle(halo, (round(150 * f), round(120 * f), round(50 * f)), (radio, radio), r)
        surface.blit(halo, (x - radio, y + 4 - radio), special_flags=pygame.BLEND_RGB_ADD)
        pygame.draw.rect(surface, (255, 236, 150), (x - 3, y + 2, 7, 4))

    def _dibujar(self, surface, h):
        x, y = round(h.x), round(h.y)
        if h.tipo == "persona":
            p = h.datos["persona"]
            p.x, p.y = h.x, h.y
            p.direction = "right" if h.vx > 0 else "left"
            p.frame = int(h.t / p.WALK_FRAME_TIME) % 2
            p.draw(surface)
        elif h.tipo == "perro":
            img = sprite_perro(h.datos["color"], int(h.t * 8) % 2, h.vx > 0)
            pygame.draw.ellipse(surface, (55, 48, 43), (x - 15, y - 3, 30, 6))
            surface.blit(img, img.get_rect(midbottom=(x, y)))
        elif h.tipo == "gato":
            caminando = h.vx != 0
            frame = int(h.t * (8 if caminando else 1.2)) % 2
            img = sprite_gato(h.datos["color"], frame, caminando, h.vx >= 0)
            pygame.draw.ellipse(surface, (55, 48, 43), (x - 12, y - 3, 24, 6))
            surface.blit(img, img.get_rect(midbottom=(x, y)))
        elif h.tipo == "auto":
            giro = int(h.x / 6) % 2
            img = sprite_auto(h.datos["color"], giro, h.vx > 0)
            pygame.draw.ellipse(surface, (40, 40, 44), (x - 30, y - 4, 60, 8))
            surface.blit(img, img.get_rect(midbottom=(x, y)))

    def dibujar_faros(self, surface, noche):
        """De noche, luz amarilla delante de cada auto."""
        if not noche:
            return
        for h in self.lista:
            if h.tipo != "auto":
                continue
            dirx = 1 if h.vx > 0 else -1
            frente = (round(h.x + dirx * 30), round(h.y - 12))
            # Cono de luz que se suma a la escena (brilla, no oscurece).
            capa = pygame.Surface((80, 34), pygame.SRCALPHA)
            for k in range(10):
                brillo = 14 + k * 3
                pygame.draw.polygon(capa, (brillo + 10, brillo, brillo // 3), [
                    (0, 17), (80 - k * 6, 3 + k), (80 - k * 6, 31 - k)])
            pygame.draw.circle(capa, (120, 110, 60), (2, 17), 4)
            if dirx < 0:
                capa = pygame.transform.flip(capa, True, False)
                pos = (frente[0] - 80, frente[1] - 17)
            else:
                pos = (frente[0], frente[1] - 17)
            surface.blit(capa, pos, special_flags=pygame.BLEND_RGB_ADD)

    def dibujar_burbujas(self, surface, font):
        for h in self.lista:
            if h.burbuja and h.burbuja_t > 0:
                t = font.render(h.burbuja, False, (84, 50, 39))
                alto = {"persona": 48, "auto": 26}.get(h.tipo, 22)
                caja = t.get_rect(midbottom=(round(h.x), round(h.y) - alto)).inflate(10, 6)
                caja.clamp_ip(surface.get_rect().inflate(-8, -8))
                pygame.draw.rect(surface, (35, 27, 27), caja.move(2, 2))
                pygame.draw.rect(surface, (245, 226, 177), caja)
                pygame.draw.rect(surface, (84, 50, 39), caja, 2)
                surface.blit(t, t.get_rect(center=caja.center))


def rect_poste():
    """Base sólida del poste: el personaje no lo atraviesa."""
    return pygame.Rect(POSTE[0] - 4, POSTE[1] - 4, 9, 5)


def dibujar_poste(surface):
    """Poste de luz verde oscuro con su farol (apagado; se prende de noche)."""
    x, y = POSTE
    oscuro, medio, claro = (34, 48, 44), (58, 82, 74), (96, 124, 112)
    pygame.draw.ellipse(surface, (55, 48, 43), (x - 8, y - 3, 16, 5))       # sombra
    pygame.draw.rect(surface, oscuro, (x - 5, y - 8, 11, 8))                 # base
    pygame.draw.rect(surface, medio, (x - 4, y - 7, 9, 6))
    pygame.draw.rect(surface, oscuro, (x - 2, y - 70, 5, 63))                # poste
    pygame.draw.line(surface, claro, (x - 1, y - 68), (x - 1, y - 9), 1)
    pygame.draw.rect(surface, oscuro, (x - 2, y - 72, 15, 3))                # brazo
    fx, fy = FAROL
    pygame.draw.polygon(surface, oscuro, [(fx - 5, fy + 2), (fx + 6, fy + 2), (fx + 3, fy - 2), (fx - 2, fy - 2)])
    pygame.draw.rect(surface, (210, 200, 160), (fx - 3, fy + 2, 7, 4))      # vidrio
    pygame.draw.rect(surface, oscuro, (fx - 4, fy + 6, 9, 2))
