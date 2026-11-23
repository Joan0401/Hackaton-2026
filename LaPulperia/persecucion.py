"""Bruno persigue a Canela por la tienda (de vez en cuando, al azar).

Canela huye por los pasillos ("¡Fsss!") y Bruno la sigue por el mismo
camino, un poquito más lento ("¡Guau, guau!"). Al final ella se sienta a
descansar y él también. Solo pasa si los dos están adentro y despiertos.
"""
import math
import random

from ayudante import camino, PASILLO_ARRIBA, PASILLO_MEDIO, PASILLO_ABAJO
from mascota import VELOCIDAD

ESPERA_MIN, ESPERA_MAX = 35.0, 80.0      # segundos entre una persecución y otra
VEL_GATA = 92.0
VEL_PERRO_LEJOS, VEL_PERRO_CERCA = 125.0, 84.0   # alcanza rápido y luego la sigue de cerca
CERCA = 130.0                            # empieza cuando Bruno ve a Canela cerca
OCUPADOS = ("a_casa", "en_casa", "a_la_puerta", "siesta", "huyendo", "persiguiendo")

_espera = random.uniform(15.0, 40.0)


def reiniciar():
    global _espera
    _espera = random.uniform(15.0, 40.0)


def libres(gata, perro):
    """Los dos en la tienda, sin saltar, dormir ni ir a otro lado."""
    return (gata.zona == "interior" and perro.zona == "interior"
            and gata.salto is None and gata.estado not in OCUPADOS
            and perro.estado not in OCUPADOS)


def empezar(gata, perro):
    """Canela sale corriendo por 3 pasillos al azar; Bruno detrás."""
    puntos = [(random.uniform(40, 560), random.choice((PASILLO_ARRIBA, PASILLO_MEDIO, PASILLO_ABAJO)))
              for _ in range(5)]
    ruta, desde = [], (gata.x, gata.y)
    for p in puntos:
        ruta += camino(desde, p)
        desde = p
    gata.ruta, gata.espera = ruta, 0.0
    gata.estado, gata.velocidad = "huyendo", VEL_GATA
    gata.globo, gata.globo_t = "¡Fsss!", 1.6
    perro.ruta = camino((perro.x, perro.y), (gata.x, gata.y)) + list(ruta)
    perro.espera = 0.0
    perro.estado, perro.velocidad = "persiguiendo", VEL_PERRO_LEJOS
    perro.globo, perro.globo_t = "¡Guau, guau!", 2.0


def actualizar(gata, perro, dt, activos=True):
    """Se llama cada cuadro, después de mover a las mascotas."""
    global _espera
    if gata.estado == "huyendo" and not gata.ruta:
        gata.estado, gata.velocidad, gata.espera = "sentada", VELOCIDAD, random.uniform(4, 7)
        gata.globo, gata.globo_t = "¡Miau!", 1.5
    if perro.estado == "persiguiendo" and not perro.ruta:
        perro.estado, perro.velocidad, perro.espera = "sentada", VELOCIDAD, random.uniform(4, 7)
        perro.globo, perro.globo_t = "¡Arf!", 1.2
    if perro.estado == "persiguiendo" and gata.estado == "huyendo":
        # Corre más si se quedó atrás; cerca, va un poquito más lento que ella.
        distancia = math.hypot(gata.x - perro.x, gata.y - perro.y)
        perro.velocidad = VEL_PERRO_LEJOS if distancia > 45 else VEL_PERRO_CERCA
        if perro.globo_t <= 0 and random.random() < dt * 0.7:
            perro.globo, perro.globo_t = random.choice(("¡Guau!", "¡Guau, guau!")), 1.0
        if gata.globo_t <= 0 and random.random() < dt * 0.35:
            gata.globo, gata.globo_t = "¡Fsss!", 0.9
    if not activos:
        return
    _espera -= dt
    if (_espera <= 0 and libres(gata, perro)
            and math.hypot(gata.x - perro.x, gata.y - perro.y) <= CERCA):
        _espera = random.uniform(ESPERA_MIN, ESPERA_MAX)
        empezar(gata, perro)
