"""Fuente del juego con soporte para el símbolo del colón (₡) y tipos de letra.

La fuente por defecto de pygame no trae el carácter ₡ y lo muestra como
un cuadrito. FuenteTienda funciona igual que pygame.font.Font, pero cuando
el texto tiene ₡ lo dibuja a mano: una "C" con dos rayitas diagonales.

Además, el tipo de letra se puede cambiar en OPCIONES > GRÁFICOS:
todas las FuenteTienda del juego usan el tipo elegido (cambiar_tipo).
"""
import pygame

COLON = "₡"

# nombre en pantalla: fuentes del sistema a buscar, en orden (None = la de pygame)
# ESCOLAR es la que viene de entrada.
TIPOS = {
    "ESCOLAR": "verdana,tahoma,dejavusans,liberationsans",
    "SENCILLA": None,
    "REDONDA": "comicsansms,comicneue,chalkboardse,dejavusans",
    "CLÁSICA": "georgia,timesnewroman,dejavuserif,liberationserif",
    "MÁQUINA": "couriernew,dejavusansmono,liberationmono,freemono",
    "MODERNA": "trebuchetms,segoeui,opensans,dejavusans",
}
# Texto de muestra para igualar tamaños: cada letra ocupa lo mismo que la
# SENCILLA (la de pygame, con la que se diseñaron las pantallas), así nada
# se sale de su lugar.
MUESTRA = "Pulpería ABC xyz 0123 ₡"
ORDEN_TIPOS = list(TIPOS)
tipo_actual = "ESCOLAR"
_cache = {}


def cambiar_tipo(nombre):
    global tipo_actual
    if nombre in TIPOS:
        tipo_actual = nombre


def _alto_mayuscula(fuente):
    """Alto real de una H (lo que el ojo ve como tamaño de la letra)."""
    h = fuente.render("H", True, (255, 255, 255))
    cajas = pygame.mask.from_surface(h).get_bounding_rects()
    return cajas[0].unionall(cajas[1:]).h if cajas else h.get_height()


def _igualar(nombres, tam):
    """El tamaño de esa letra que se ve igual de grande que la SENCILLA:
    misma altura de mayúsculas, sin pasarse de un 10 % más de ancho."""
    base = pygame.font.Font(None, tam)
    muestra = MUESTRA.replace(COLON, "C")
    ancho_max = base.size(muestra)[0] * 1.10
    alto_obj = _alto_mayuscula(base)
    mejor = None
    for medio in range(max(4, tam // 3), tam * 2):
        f = pygame.font.SysFont(nombres, medio)
        if f.size(muestra)[0] > ancho_max or _alto_mayuscula(f) > alto_obj:
            break
        mejor = f
    return mejor or pygame.font.SysFont(nombres, max(4, tam // 3))


def _fuente_real(tam):
    clave = (tipo_actual, tam)
    if clave not in _cache:
        nombres = TIPOS[tipo_actual]
        _cache[clave] = pygame.font.Font(None, tam) if nombres is None else _igualar(nombres, tam)
    return _cache[clave]


class FuenteTienda:
    """Se usa como pygame.font.Font (render, size, get_height...)."""

    def __init__(self, archivo, tam):
        self.tam = tam

    @property
    def _f(self):
        return _fuente_real(self.tam)

    def __getattr__(self, nombre):
        # size, get_height, get_linesize... de la fuente elegida.
        return getattr(self._f, nombre)

    def _colon(self, antialias, color):
        """Dibuja el ₡ a partir de una C de la misma fuente."""
        letra = self._f.render("C", antialias, color)
        w, h = letra.get_size()
        signo = pygame.Surface((w, h), pygame.SRCALPHA)
        signo.blit(letra, (0, 0))

        # Caja real de la C (sin el espacio de arriba y abajo de la fuente).
        cajas = pygame.mask.from_surface(letra).get_bounding_rects()
        caja = cajas[0].unionall(cajas[1:]) if cajas else letra.get_rect()
        grosor = max(1, round(caja.h / 9))
        alto = caja.h + 2 * grosor
        inclinacion = max(1, round(caja.h * 0.22))
        for fraccion in (0.42, 0.68):
            x = caja.x + round(caja.w * fraccion)
            pygame.draw.line(
                signo, color,
                (x - inclinacion // 2, caja.bottom + grosor),
                (x + inclinacion // 2, caja.bottom + grosor - alto),
                grosor,
            )
        return signo

    def size(self, text):
        if COLON not in text:
            return self._f.size(text)
        return self.render(text, False, (0, 0, 0)).get_size()

    def render(self, text, antialias, color, bgcolor=None, *args, **kwargs):
        f = self._f
        if not isinstance(text, str) or COLON not in text:
            if bgcolor is None:
                return f.render(text, antialias, color, *args, **kwargs)
            return f.render(text, antialias, color, bgcolor, *args, **kwargs)

        # Renderizar por partes: texto normal + ₡ dibujado a mano.
        partes = []
        for i, trozo in enumerate(text.split(COLON)):
            if i > 0:
                partes.append(self._colon(antialias, color))
            if trozo:
                partes.append(f.render(trozo, antialias, color))
        alto = max(p.get_height() for p in partes)
        ancho = sum(p.get_width() for p in partes)
        resultado = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        if bgcolor is not None:
            resultado.fill(bgcolor)
        x = 0
        for p in partes:
            resultado.blit(p, (x, 0))
            x += p.get_width()
        return resultado
