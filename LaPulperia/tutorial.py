"""Tutorial guiado (siempre el mismo).

Al empezar una partida nueva el juego pregunta "¿JUGAR EL TUTORIAL?" (y
también está en OPCIONES > TUTORIAL). Doña Rosa llega y pide 2 manzanas;
un letrero explica cada paso y una flecha señala adónde ir. Cada paso
termina cuando el niño lo hace (los que solo explican, con ENTER).
TAB salta el tutorial.

El juego le pasa a `actualizar` un diccionario con lo que está pasando
(ver main.estado_tutorial); este módulo no conoce el resto del juego.
"""
import math

import pygame

def _enter(e):
    """Pasos que solo explican: se pasan con ENTER."""
    return e["enter"]


# (texto, condición para pasar al siguiente, a dónde apunta la flecha)
PASOS = [
    ("¡Hola, {nombre}! Usa las FLECHAS para caminar por tu pulpería.",
     lambda e: e["caminado"] >= 40, None),
    ("Llegó Doña Rosa y quiere 2 MANZANAS. Ve a la góndola de frutas y pulsa E.",
     lambda e: e["vista"] == "gondola_1" or e["manzanas_mano"] > 0, "gondola_1"),
    ("Haz clic en una manzana para tomarla. ¡Toma 2 manzanas!",
     lambda e: e["manzanas_mano"] + e["manzanas_mostrador"] >= 2, None),
    ("¡Bien! Llévalas al MOSTRADOR y pulsa E para dejarlas ahí.",
     lambda e: e["manzanas_mostrador"] >= 2, "counter"),
    ("Ahora ponte frente a la CAJA REGISTRADORA y pulsa E para cobrar.",
     lambda e: e["factura"], "caja"),
    ("Cuenta los dibujos, escribe cada resultado con ENTER y luego COBRAR. "
     "¿Muy difícil? Con C usas la calculadora (cuesta dinero).",
     lambda e: e["ventas"] >= 1, None),
    ("¡Venta lista! Pulsa H para ver las ventas de hoy.",
     lambda e: e["historial"], None),
    ("Aquí ves cuánto vendiste. Cierra con H y pulsa R para abrir el LIBRO DE RECETAS.",
     lambda e: e["recetario"], "libro"),
    ("Si un cliente no sabe una receta, tú le dices qué lleva y él te pide la MITAD, "
     "un TERCIO o un CUARTO. Cierra con R.",
     lambda e: not e["recetario"], None),
    ("Cuando falten productos, camina a la derecha hasta la BODEGA.",
     lambda e: e["escena"] == "inventario", "bodega"),
    ("Aquí está la mercadería para rellenar la tienda. Vuelve por la puerta SALA (a la izquierda).",
     lambda e: e["escena"] == "interior", None),
    ("Con el TELÉFONO del mostrador le pides cajas al camión (hasta las 2 p. m.). "
     "ENTER: seguir.",
     _enter, "telefono"),
    ("Se atiende hasta las 6 p. m.; de 6 a 8 acomodas la tienda. En este letrero: "
     "TERMINAR EL DÍA. ENTER: seguir.",
     _enter, "letrero"),
    ("¡Terminaste el tutorial! Pulsa ENTER para abrir tu pulpería.",
     _enter, None),
]


class Tutorial:
    def __init__(self):
        self.activo = False
        self.paso = 0
        self.t = 0.0

    def empezar(self):
        self.activo = True
        self.paso = 0
        self.t = 0.0

    def terminar(self):
        self.activo = False

    @property
    def ultimo(self):
        return self.paso == len(PASOS) - 1

    @property
    def pide_enter(self):
        """¿El paso actual se pasa con ENTER?"""
        return self.activo and PASOS[self.paso][1] is _enter

    def actualizar(self, dt, estado):
        """Avanza de paso si ya se cumplió. Devuelve True al terminar."""
        if not self.activo:
            return False
        self.t += dt
        _, listo, _ = PASOS[self.paso]
        if listo(estado):
            if self.ultimo:
                self.terminar()
                return True
            self.paso += 1
            self.t = 0.0
        return False

    # -----------------------------------------------------
    def dibujar(self, surface, font, font_small, nombre, puntos, mostrar_flecha=True, abajo=False):
        """Letrero de arriba y flecha. puntos: {objetivo: (x, y)} en 640 x 360."""
        if not self.activo:
            return
        texto, _, objetivo = PASOS[self.paso]
        texto = texto.format(nombre=nombre or "pulpero")

        # Letrero con el paso actual
        lineas = _envolver(font, texto, 470)
        alto = 14 + len(lineas) * (font.get_height() + 2) + 14
        caja = pygame.Rect(0, 0, 520, alto)
        if abajo:
            # Caminando: abajo, para no tapar el globo del cliente.
            caja.midbottom = (320, 330)
        else:
            caja.midtop = (320, 6)
        pygame.draw.rect(surface, (35, 27, 27), caja.move(3, 3))
        pygame.draw.rect(surface, (250, 238, 200), caja)
        pygame.draw.rect(surface, (214, 150, 40), caja, 3)
        etiqueta = font_small.render(f"TUTORIAL  {self.paso + 1}/{len(PASOS)}", False, (176, 64, 52))
        surface.blit(etiqueta, (caja.x + 10, caja.y + 5))
        saltar = font_small.render("TAB: SALTAR", False, (120, 110, 96))
        surface.blit(saltar, saltar.get_rect(topright=(caja.right - 10, caja.y + 5)))
        y = caja.y + 18
        for linea in lineas:
            t = font.render(linea, False, (72, 46, 36))
            surface.blit(t, t.get_rect(midtop=(caja.centerx, y)))
            y += font.get_height() + 2

        # Flecha que rebota sobre el objetivo
        if mostrar_flecha and objetivo and objetivo in puntos:
            x, y = puntos[objetivo]
            y -= 6 + abs(math.sin(self.t * 4)) * 6
            punta = [(x - 7, y - 10), (x + 7, y - 10), (x, y)]
            pygame.draw.polygon(surface, (35, 27, 27), [(px + 1, py + 2) for px, py in punta])
            pygame.draw.polygon(surface, (255, 200, 60), punta)
            pygame.draw.rect(surface, (255, 200, 60), (x - 3, y - 18, 6, 9))


def _envolver(font, texto, ancho):
    palabras, lineas, actual = texto.split(), [], ""
    for palabra in palabras:
        prueba = f"{actual} {palabra}".strip()
        if font.size(prueba)[0] <= ancho or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas
