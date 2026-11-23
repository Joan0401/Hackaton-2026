"""Ciclo de día y noche de la jornada laboral.

HORARIO: el día va de 8:00 a. m. a 8:00 p. m. y dura 7 minutos reales
(una hora del juego = 35 segundos). La tienda atiende clientes hasta las
6:00 p. m.; de 6:00 a 8:00 p. m. está cerrada para acomodar la mercadería.
A las 8:00 p. m. (o antes, con "TERMINAR EL DÍA" en el letrero) llega el
cierre de caja.

La luz se pinta encima de la escena: amanecer azulado, día normal, tarde
dorada, atardecer naranja y noche azul. Dentro de la tienda el cambio es
más suave y de noche se encienden luces cálidas.
"""
import math

import pygame

HORA_INICIO = 8.0          # 8:00 a. m.: abre la tienda
HORA_CIERRE_TIENDA = 18.0  # 6:00 p. m.: ya no se atienden clientes
HORA_FIN = 20.0            # 8:00 p. m.: termina el día (cierre de caja)
DURACION_DIA = 7 * 60.0    # segundos reales que dura el día completo
SEGUNDOS_POR_CLIENTE = 45.0   # (ya no se usa para el reloj; queda por compatibilidad)
DURACION_LETRERO = 3.0

# (hora, (r, g, b), opacidad en la calle 0-255)
CLAVES_LUZ = [
    (6.5, (40, 54, 120), 110),     # amanecer azulado
    (7.6, (255, 196, 140), 34),    # salida del sol
    (8.0, (255, 210, 160), 22),    # 8:00 a. m.: abre la tienda
    (9.0, (255, 255, 255), 0),     # día
    (15.0, (255, 255, 255), 0),
    (16.6, (255, 178, 90), 46),    # tarde dorada
    (18.0, (236, 110, 60), 86),    # atardecer
    (19.0, (24, 34, 92), 150),     # noche
    (20.0, (18, 26, 80), 160),     # 8:00 p. m.
]

# Luces de la tienda que se encienden de noche (coordenadas 640 x 360).
LAMPARAS_TIENDA = [(132, 186), (140, 290), (483, 196), (320, 230)]  # sobre los muebles
LAMPARAS_CALLE = [(320, 150), (247, 222)]   # puerta y poste de luz


# Ventanas del frente de la tienda (las mismas que se ven desde la calle),
# en coordenadas x del interior. El frente queda en el borde de abajo.
VENTANAS_FRENTE = [(44, 200), (428, 584)]
SALIDA_SOL, PUESTA_SOL = 6.2, 18.5


def _sol(hora):
    """(altura 0-1, inclinación -1..1, intensidad 0-1) del sol a esa hora."""
    t = (hora - SALIDA_SOL) / (PUESTA_SOL - SALIDA_SOL)
    if t <= 0 or t >= 1:
        return 0.0, 0.0, 0.0
    altura = math.sin(math.pi * t)
    inclinacion = math.cos(math.pi * t)          # mañana +, tarde -
    intensidad = min(1.0, t / 0.08, (1 - t) / 0.08)
    return altura, inclinacion, intensidad


def _color_sol(altura):
    """Naranja con el sol bajo, casi blanco a mediodía."""
    bajo, alto = (255, 150, 70), (255, 240, 200)
    f = min(1.0, altura / 0.75)
    return tuple(round(a + (b - a) * f) for a, b in zip(bajo, alto))


def _interpolar(hora):
    if hora <= CLAVES_LUZ[0][0]:
        return CLAVES_LUZ[0][1], CLAVES_LUZ[0][2]
    for (h0, c0, a0), (h1, c1, a1) in zip(CLAVES_LUZ, CLAVES_LUZ[1:]):
        if h0 <= hora <= h1:
            t = (hora - h0) / (h1 - h0)
            color = tuple(round(x + (y - x) * t) for x, y in zip(c0, c1))
            return color, round(a0 + (a1 - a0) * t)
    return CLAVES_LUZ[-1][1], CLAVES_LUZ[-1][2]


def progreso_de(hora):
    """Qué parte del día (0 a 1) corresponde a esa hora."""
    return max(0.0, min(1.0, (hora - HORA_INICIO) / (HORA_FIN - HORA_INICIO)))


class Reloj:
    def __init__(self):
        self.reiniciar(dia=1)

    def reiniciar(self, dia=1):
        self.progreso = 0.0
        self.t_turno = 0.0
        self._terminados = 0
        self.dia = dia
        self.letrero_t = DURACION_LETRERO if dia > 1 else 0.0

    # -----------------------------------------------------
    def actualizar(self, dt, terminados, limite, jornada_terminada):
        """El reloj avanza parejo (el día completo dura DURACION_DIA).

        Si ya se atendió a todos los clientes antes de las 6:00 p. m., avanza
        rápido hasta las 6 (la hora de acomodar); de ahí sigue normal.
        """
        self._terminados = terminados
        cierre = progreso_de(HORA_CIERRE_TIENDA)
        if jornada_terminada and self.progreso < cierre:
            self.progreso += (cierre - self.progreso) * min(1.0, dt * 1.2)
            if cierre - self.progreso < 0.002:
                self.progreso = cierre
        else:
            self.progreso = min(1.0, self.progreso + dt / DURACION_DIA)
        if self.letrero_t > 0:
            self.letrero_t -= dt

    @property
    def cerro(self):
        """Ya son las 6:00 p. m.: la tienda cierra para los clientes."""
        return self.hora >= HORA_CIERRE_TIENDA - 1e-6

    @property
    def fin_dia(self):
        """Ya son las 8:00 p. m.: termina el día (cierre de caja)."""
        return self.progreso >= 1.0

    def terminar_dia(self):
        """"TERMINAR EL DÍA": salta a las 8:00 p. m."""
        self.progreso = 1.0

    @property
    def hora(self):
        return HORA_INICIO + (HORA_FIN - HORA_INICIO) * self.progreso

    @property
    def es_noche(self):
        return self.hora >= 18.4 or self.hora < 7.0

    def texto(self):
        h = self.hora
        horas = int(h)
        minutos = int((h - horas) * 60) // 10 * 10   # de 10 en 10, más fácil de leer
        sufijo = "a. m." if horas < 12 else "p. m."
        h12 = horas % 12 or 12
        return f"{h12}:{minutos:02d} {sufijo}"

    # -----------------------------------------------------
    def dibujar_luz(self, surface, escena):
        """Tiñe la escena según la hora. escena: interior, entrada, inventario."""
        color, alfa = _interpolar(self.hora)
        if escena != "entrada":
            alfa = round(alfa * 0.45)   # dentro de la tienda, más suave
        if alfa <= 0:
            return
        capa = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        capa.fill((*color, alfa))

        # De noche se encienden luces cálidas: alrededor de cada una la capa
        # oscura se aclara poco a poco (degradado suave, sin anillos).
        noche = max(0.0, min(1.0, (self.hora - 17.6) / 1.2))
        lamparas = LAMPARAS_CALLE if escena == "entrada" else LAMPARAS_TIENDA
        radio_luz = 110 if escena == "entrada" else 95
        if noche > 0:
            for x, y in lamparas:
                luz = pygame.Surface((radio_luz * 2, radio_luz * 2), pygame.SRCALPHA)
                luz.fill((*color, alfa))
                for r in range(radio_luz, 0, -3):
                    f = r / radio_luz
                    claro = alfa * (1 - f) ** 0.8 * 0.85 * noche
                    pygame.draw.circle(luz, (*color, round(alfa - claro)), (radio_luz, radio_luz), r)
                # MIN: donde se juntan dos luces gana la más clara.
                capa.blit(luz, (x - radio_luz, y - radio_luz), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(capa, (0, 0))

        if noche > 0:
            for x, y in lamparas:
                brillo = pygame.Surface((radio_luz * 2, radio_luz * 2), pygame.SRCALPHA)
                for r in range(radio_luz, 0, -3):
                    f = r / radio_luz
                    pygame.draw.circle(brillo, (255, 196, 110, round(38 * (1 - f) ** 1.5 * noche)),
                                       (radio_luz, radio_luz), r)
                surface.blit(brillo, (x - radio_luz, y - radio_luz))

    # -----------------------------------------------------
    def dibujar_ventanas(self, surface):
        """Luz del sol que entra por las ventanas del frente y cae en el piso.

        Con el sol bajo (mañana y tarde) los rayos son largos, inclinados y
        anaranjados; a mediodía son cortos y casi blancos; de noche no hay.
        """
        hora = round(self.hora * 20) / 20     # cada 3 minutos de juego
        if getattr(self, "_ventanas_hora", None) != hora:
            self._ventanas_hora = hora
            self._ventanas_capa = self._construir_ventanas(hora, surface.get_size())
        if self._ventanas_capa is not None:
            surface.blit(self._ventanas_capa, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    @staticmethod
    def _construir_ventanas(hora, tamano):
        altura, inclinacion, intensidad = _sol(hora)
        if intensidad <= 0:
            return None
        ancho, alto = tamano
        escala = 4                           # se dibuja chico y se agranda: bordes suaves
        mascara = pygame.Surface((ancho // escala, alto // escala), pygame.SRCALPHA)
        # Distancia desde la pared del frente hasta donde cae la luz.
        largo = 1.25 + 2.4 * (1 - altura)   # sol bajo: luz larga; mediodía: corta
        cerca, lejos = 18 * largo, 62 * largo
        corte = cerca + (lejos - cerca) * 0.48     # el travesaño de la ventana
        desvio = 0.75 * inclinacion

        def paño(x0, x1, d0, d1):
            puntos = [(x0 + d0 * desvio, alto - d0), (x1 + d0 * desvio, alto - d0),
                      (x1 + d1 * desvio, alto - d1), (x0 + d1 * desvio, alto - d1)]
            pts = [(px / escala, py / escala) for px, py in puntos]
            # Más claro cerca de la ventana, más tenue lejos.
            cerca_f = 1.0 - (d0 - cerca) / max(1.0, lejos - cerca) * 0.45
            pygame.draw.polygon(mascara, (255, 255, 255, round(255 * cerca_f)), pts)

        for x0, x1 in VENTANAS_FRENTE:
            medio = (x0 + x1) / 2
            for a, b in ((x0 + 4, medio - 3), (medio + 3, x1 - 4)):   # parteluz central
                paño(a, b, cerca, corte - 3)
                paño(a, b, corte + 3, lejos)
            # Resplandor junto a la pared, donde está la ventana.
            pygame.draw.rect(mascara, (255, 255, 255, 120),
                             ((x0 - 6) / escala, (alto - 10) / escala, (x1 - x0 + 12) / escala, 3))

        mascara = pygame.transform.smoothscale(mascara, (ancho, alto))
        # Un poco de desenfoque extra para que no se vea recortado.
        mascara = pygame.transform.smoothscale(
            pygame.transform.smoothscale(mascara, (ancho // 2, alto // 2)), (ancho, alto))

        fuerza = (0.25 + 0.09 * altura) * intensidad
        color = tuple(round(c * fuerza) for c in _color_sol(altura))
        capa = pygame.Surface((ancho, alto))
        capa.fill(color)
        # Multiplicar por la máscara (su canal alfa) para recortar los rayos.
        alfa = pygame.Surface((ancho, alto))
        alfa.fill((0, 0, 0))
        alfa.blit(mascara, (0, 0))
        capa.blit(alfa, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        return capa

    def dibujar_icono(self, surface, centro, radio=6):
        """Sol de día, luna de noche."""
        cx, cy = centro
        if self.es_noche:
            pygame.draw.circle(surface, (236, 232, 196), (cx, cy), radio)
            pygame.draw.circle(surface, (35, 27, 27), (cx + radio // 2 + 1, cy - radio // 2), radio - 1)
        else:
            atardecer = self.hora >= 16.6
            color = (255, 150, 70) if atardecer else (255, 210, 70)
            for i in range(8):
                a = i * math.pi / 4
                pygame.draw.line(surface, color,
                                 (cx + math.cos(a) * (radio + 1), cy + math.sin(a) * (radio + 1)),
                                 (cx + math.cos(a) * (radio + 3), cy + math.sin(a) * (radio + 3)), 1)
            pygame.draw.circle(surface, color, (cx, cy), radio - 1)

    def dibujar_letrero(self, surface, font_title, font_small):
        """Letrero de "¡AMANECE! DÍA N" al empezar un nuevo día."""
        if self.letrero_t <= 0:
            return
        t = self.letrero_t / DURACION_LETRERO
        alfa = round(255 * min(1.0, t * 3))
        texto = font_title.render(f"¡AMANECE!  DÍA {self.dia}", False, (255, 236, 170))
        caja = texto.get_rect(center=(surface.get_width() // 2, 110)).inflate(40, 20)
        capa = pygame.Surface(caja.size, pygame.SRCALPHA)
        capa.fill((35, 27, 27, min(220, alfa)))
        capa.blit(texto, texto.get_rect(center=(caja.w // 2, caja.h // 2)))
        capa.set_alpha(alfa)
        surface.blit(capa, caja.topleft)
