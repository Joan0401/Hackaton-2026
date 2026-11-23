"""Libro de recetas (tecla R o la hoja del mostrador).

Un libro abierto, dibujado a la resolución real de la ventana:
  - página izquierda: los ingredientes para 1 receta;
  - página derecha: una imagen de muestra del platillo.
El libro NO hace cálculos: si el cliente pide medio queque o el doble de
pan, el niño calcula mentalmente cuántos ingredientes llevar.
"""
import math

import pygame
from pygame import gfxdraw

from fuentes import FuenteTienda
from productos import PRODUCTOS
from productos_hd import dibujar_hd
from recetas import RECETAS, ORDEN

ANCHO, ALTO = 1280, 720
LIBRO = pygame.Rect(90, 52, 1100, 610)
ESCALA = 0.85        # el libro se ve un poco más pequeño que la pantalla
DURACION_APERTURA = 200

TAPA = (122, 52, 44)
TAPA_OSCURA = (78, 30, 28)
PAPEL = (250, 238, 206)
PAPEL_SOMBRA = (226, 208, 166)
TINTA = (72, 46, 36)
TINTA_SUAVE = (128, 96, 74)
ROJO = (176, 64, 52)
VERDE = (66, 115, 67)
RESALTE = (255, 220, 120)

_fuentes = {}


def _fuente(tam):
    if tam not in _fuentes:
        _fuentes[tam] = FuenteTienda(None, tam)
    return _fuentes[tam]


def _texto(s, texto, tam, color, **pos):
    img = _fuente(tam).render(texto, True, color)
    s.blit(img, img.get_rect(**pos))
    return img.get_rect(**pos)


# ---------------------------------------------------------
# DIBUJOS DE LOS PLATILLOS
# ---------------------------------------------------------
def _elipse(s, color, rect):
    r = pygame.Rect(rect)
    gfxdraw.filled_ellipse(s, r.centerx, r.centery, max(1, r.w // 2), max(1, r.h // 2), color)
    gfxdraw.aaellipse(s, r.centerx, r.centery, max(1, r.w // 2), max(1, r.h // 2), color)


def _plato(s, c, w):
    _elipse(s, (176, 160, 140), (c[0] - w // 2, c[1] - w // 8 + 4, w, w // 4 + 4))
    _elipse(s, (246, 246, 240), (c[0] - w // 2, c[1] - w // 8, w, w // 4))
    _elipse(s, (226, 226, 218), (c[0] - w // 3, c[1] - w // 14, w * 2 // 3, w // 7))


def _tazon(s, c, w, relleno):
    x, y = c
    fondo = y + round(w * 0.36)
    _elipse(s, (150, 120, 96), (x - w // 2, y - 10, w, 30))
    pygame.draw.polygon(s, (110, 70, 52), [(x - w // 2, y + 4), (x + w // 2, y + 4),
                                           (x + w // 3, fondo), (x - w // 3, fondo)])
    pygame.draw.polygon(s, (156, 96, 66), [(x - w // 2 + 8, y + 6), (x - w // 6, y + 6),
                                           (x - w // 4, fondo - 4), (x - w // 3 + 4, fondo - 4)])
    _elipse(s, relleno, (x - w // 2 + 6, y - 8, w - 12, 24))


def dibujar_platillo(s, clave, centro):
    x, y = centro
    if clave in ("arroz_leche", "ensalada"):
        y -= 20  # los tazones son más altos
    if clave == "queque":
        _plato(s, (x, y + 52), 200)
        cuerpo = pygame.Rect(x - 76, y - 20, 152, 70)
        pygame.draw.rect(s, (140, 82, 40), cuerpo, border_radius=14)
        pygame.draw.rect(s, (196, 128, 62), cuerpo.inflate(-14, -10).move(-4, -2), border_radius=12)
        _elipse(s, (140, 82, 40), (x - 76, y - 40, 152, 44))
        _elipse(s, (222, 160, 84), (x - 70, y - 38, 140, 38))
        # Glaseado que chorrea
        _elipse(s, (252, 246, 236), (x - 66, y - 38, 132, 32))
        for dx, largo in [(-52, 24), (-20, 34), (14, 22), (44, 30)]:
            pygame.draw.rect(s, (252, 246, 236), (x + dx, y - 26, 14, largo), border_radius=7)
        _elipse(s, (196, 44, 52), (x - 10, y - 50, 20, 20))
        pygame.draw.line(s, (70, 120, 50), (x, y - 48), (x + 8, y - 62), 3)
    elif clave == "pan":
        _plato(s, (x, y + 50), 210)
        for dx, dy in [(-44, 10), (40, 14), (0, -6)]:
            r = pygame.Rect(x + dx - 56, y + dy - 30, 112, 66)
            _elipse(s, (150, 88, 40), r)
            _elipse(s, (214, 150, 76), r.inflate(-12, -14).move(-3, -4))
            _elipse(s, (238, 190, 116), (r.x + 22, r.y + 10, 42, 16))
            for i in range(3):
                pygame.draw.line(s, (150, 88, 40), (r.x + 30 + i * 20, r.y + 14),
                                 (r.x + 40 + i * 20, r.y + 32), 3)
    elif clave == "arroz_leche":
        _tazon(s, (x, y + 4), 210, (250, 244, 226))
        for i in range(14):
            a = i * 2.4
            px, py = x + math.cos(a) * 70, y + 4 + math.sin(a * 1.7) * 7
            pygame.draw.ellipse(s, (236, 226, 198), (px - 5, py - 2, 10, 5))
        for dx in (-30, 6, 36):
            pygame.draw.rect(s, (150, 82, 40), (x + dx, y - 4, 22, 6), border_radius=3)
        _elipse(s, (196, 140, 80), (x - 50, y - 6, 18, 8))
    elif clave == "gallo_pinto":
        _plato(s, (x, y + 30), 230)
        _elipse(s, (90, 46, 40), (x - 92, y - 18, 184, 70))
        for i in range(60):
            a, r = i * 2.39996, 8 + (i * 37 % 80)
            px, py = x + math.cos(a) * r * 0.95, y + 17 + math.sin(a) * r * 0.36
            color = (246, 238, 220) if i % 3 else (60, 26, 26)
            pygame.draw.ellipse(s, color, (px - 5, py - 3, 10, 6))
        for dx in (-20, 4, 28):
            pygame.draw.circle(s, (70, 150, 60), (x + dx, y + 4), 5)
        # Un huevito al lado
        _elipse(s, (250, 250, 244), (x + 52, y + 8, 60, 34))
        _elipse(s, (246, 182, 44), (x + 70, y + 14, 22, 20))
    elif clave == "ensalada":
        _ensalada(s, x, y + 8)
    elif clave == "vaca_negra":
        _vaso(s, x, y + 6, (70, 34, 26), espuma=True)
    elif clave == "licuado":
        _vaso(s, x, y + 6, (246, 230, 170), espuma=False)
    elif clave == "banana_split":
        _banana_split(s, x, y + 20)


def _ensalada(s, x, y):
    """Tazón con la fruta picada ADENTRO (asoma un montoncito sobre el borde)."""
    w = 220
    fondo = y + round(w * 0.36)
    # Interior del tazón (atrás)
    _elipse(s, (110, 70, 52), (x - w // 2, y - 10, w, 30))
    _elipse(s, (196, 150, 110), (x - w // 2 + 6, y - 8, w - 12, 24))
    # Fruta picada: montoncito dentro del tazón
    piezas = []
    for i in range(64):
        a = i * 2.39996
        r = ((i * 0.37) % 1.0) ** 0.5
        px = x + math.cos(a) * (w / 2 - 26) * r
        alto = max(0.0, 1 - ((px - x) / (w / 2 - 10)) ** 2) * 62   # montoncito redondo
        py = y + 6 - alto * (0.35 + 0.65 * ((i * 0.61) % 1.0))
        piezas.append((py, px, i % 4))
    for py, px, tipo in sorted(piezas):
        if tipo == 0:      # rodaja de banano
            pygame.draw.circle(s, (200, 176, 100), (px, py), 13)
            pygame.draw.circle(s, (250, 240, 196), (px, py), 11)
            pygame.draw.circle(s, (222, 202, 140), (px, py), 4)
        elif tipo == 1:    # cubito de manzana (con cáscara roja)
            pygame.draw.rect(s, (170, 140, 110), (px - 11, py - 9, 22, 19), border_radius=3)
            pygame.draw.rect(s, (252, 238, 204), (px - 10, py - 8, 20, 17), border_radius=3)
            pygame.draw.rect(s, (200, 40, 50), (px - 10, py - 8, 20, 6), border_radius=3)
        elif tipo == 2:    # uva
            pygame.draw.circle(s, (60, 24, 84), (px, py), 11)
            pygame.draw.circle(s, (120, 56, 160), (px, py), 10)
            pygame.draw.circle(s, (190, 130, 230), (px - 3, py - 3), 3)
        else:              # gajo de naranja
            pygame.draw.ellipse(s, (200, 100, 20), (px - 14, py - 8, 28, 17))
            pygame.draw.ellipse(s, (255, 160, 50), (px - 12, py - 7, 24, 13))
            pygame.draw.line(s, (255, 210, 140), (px - 8, py), (px + 8, py), 2)
    # Frente del tazón (tapa la parte de abajo de la fruta)
    pygame.draw.polygon(s, (110, 70, 52), [(x - w // 2, y + 4), (x + w // 2, y + 4),
                                           (x + w // 3, fondo), (x - w // 3, fondo)])
    pygame.draw.polygon(s, (156, 96, 66), [(x - w // 2 + 8, y + 6), (x - w // 6, y + 6),
                                           (x - w // 4, fondo - 4), (x - w // 3 + 4, fondo - 4)])
    pygame.draw.arc(s, (150, 120, 96), (x - w // 2, y - 10, w, 30), math.pi, 2 * math.pi, 5)
    # Una hojita de menta arriba
    pygame.draw.ellipse(s, (70, 150, 70), (x - 4, y - 40, 16, 9))
    pygame.draw.ellipse(s, (90, 180, 80), (x - 14, y - 38, 14, 8))


def _vaso(s, x, y, color, espuma):
    """Vaso alto: vaca negra (cola con helado) o licuado."""
    arriba, abajo = y - 70, y + 70
    vidrio = [(x - 46, arriba), (x + 46, arriba), (x + 36, abajo), (x - 36, abajo)]
    pygame.draw.polygon(s, (220, 236, 244), vidrio)
    liquido = [(x - 42, arriba + 22), (x + 42, arriba + 22), (x + 34, abajo - 4), (x - 34, abajo - 4)]
    pygame.draw.polygon(s, color, liquido)
    if espuma:
        for dx, dy, r in ((-26, 18, 16), (0, 12, 20), (26, 18, 16), (-12, 2, 14), (14, 4, 14)):
            pygame.draw.circle(s, (246, 236, 214), (x + dx, arriba + dy), r)
        # bola de helado
        pygame.draw.circle(s, (250, 244, 228), (x + 6, arriba - 8), 26)
        pygame.draw.circle(s, (255, 255, 255), (x - 4, arriba - 16), 8)
        for i in range(6):   # burbujitas
            pygame.draw.circle(s, (120, 70, 50), (x - 20 + i * 8, abajo - 20 - (i * 13) % 50), 3)
    else:
        for i in range(5):   # pedacitos de banano
            pygame.draw.circle(s, (232, 214, 140), (x - 20 + i * 10, arriba + 40 + (i * 17) % 60), 4)
        _elipse(s, (252, 244, 206), (x - 42, arriba + 14, 84, 18))
    # pajilla
    pygame.draw.line(s, (220, 60, 70), (x + 18, arriba - 40), (x + 6, abajo - 30), 7)
    pygame.draw.line(s, (255, 255, 255), (x + 17, arriba - 30), (x + 14, arriba - 18), 7)
    pygame.draw.polygon(s, (140, 160, 170), vidrio, 3)
    pygame.draw.line(s, (255, 255, 255), (x - 34, arriba + 10), (x - 26, abajo - 20), 4)


def _banana_split(s, x, y):
    """Plato alargado con el banano partido y tres bolas de helado."""
    _elipse(s, (150, 140, 170), (x - 120, y + 8, 240, 50))
    _elipse(s, (226, 230, 246), (x - 116, y + 2, 232, 46))
    for dy in (-6, 14):   # mitades del banano
        pygame.draw.ellipse(s, (180, 150, 60), (x - 104, y + dy - 4, 208, 26))
        pygame.draw.ellipse(s, (250, 226, 120), (x - 100, y + dy - 2, 200, 20))
    for i, (color, brillo) in enumerate((((250, 160, 190), (255, 210, 225)),
                                         ((250, 244, 228), (255, 255, 255)),
                                         ((140, 84, 56), (180, 120, 90)))):
        cx = x - 60 + i * 60
        pygame.draw.circle(s, color, (cx, y - 2), 30)
        pygame.draw.circle(s, brillo, (cx - 10, y - 12), 9)
    for cx in (x - 60, x, x + 60):   # cerecitas
        pygame.draw.circle(s, (210, 30, 40), (cx, y - 34), 7)
        pygame.draw.line(s, (90, 120, 40), (cx, y - 40), (cx + 6, y - 52), 2)


# ---------------------------------------------------------
# EL LIBRO
# ---------------------------------------------------------
class Recetario:
    def __init__(self):
        self.abierto = False
        self.pagina = 0
        self.abierto_ms = 0

    def abrir(self, receta=None):
        """Abre el libro; con una receta ("queque"), en su página."""
        self.abierto = True
        if receta:
            self.pagina = ORDEN.index(receta)
        self.abierto_ms = pygame.time.get_ticks()

    def cerrar(self):
        self.abierto = False

    def pasar(self, paso):
        self.pagina = (self.pagina + paso) % len(ORDEN)

    # Controles -----------------------------------------------------------
    def manejar_tecla(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_r, pygame.K_RETURN):
            self.cerrar()
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.pasar(1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.pasar(-1)

    def manejar_clic(self, pos):
        # El libro se dibuja reducido al centro: pasar el clic a sus medidas.
        pos = ((pos[0] - ANCHO / 2) / ESCALA + ANCHO / 2,
               (pos[1] - ALTO / 2) / ESCALA + ALTO / 2)
        if self._flecha(-1).collidepoint(pos):
            self.pasar(-1)
        elif self._flecha(1).collidepoint(pos):
            self.pasar(1)
        elif not LIBRO.collidepoint(pos):
            self.cerrar()

    @staticmethod
    def _flecha(lado):
        y = LIBRO.bottom - 52
        x = LIBRO.x + 40 if lado < 0 else LIBRO.right - 100
        return pygame.Rect(x, y, 60, 40)

    # Dibujo ---------------------------------------------------------------
    def dibujar(self, screen):
        if not self.abierto:
            return
        t = min(1.0, (pygame.time.get_ticks() - self.abierto_ms) / DURACION_APERTURA)
        suave = 1 - (1 - t) ** 3
        oscuro = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        oscuro.fill((18, 22, 24, round(185 * suave)))
        screen.blit(oscuro, (0, 0))

        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self._dibujar_libro(capa)
        escala = ESCALA * (0.9 + 0.1 * suave)
        capa = pygame.transform.smoothscale_by(capa, escala)
        if t < 1:
            capa.set_alpha(round(255 * suave))
        screen.blit(capa, ((ANCHO - capa.get_width()) / 2,
                           (ALTO - capa.get_height()) / 2 + (1 - suave) * 30))

    def _dibujar_libro(self, s):
        # Tapas y hojas
        pygame.draw.rect(s, (24, 16, 16), LIBRO.move(10, 12), border_radius=22)
        pygame.draw.rect(s, TAPA_OSCURA, LIBRO, border_radius=22)
        pygame.draw.rect(s, TAPA, LIBRO.inflate(-10, -10), border_radius=18)
        hojas = LIBRO.inflate(-44, -40)
        izquierda = pygame.Rect(hojas.x, hojas.y, hojas.w // 2, hojas.h)
        derecha = pygame.Rect(hojas.centerx, hojas.y, hojas.w // 2, hojas.h)
        for i in range(3, 0, -1):  # bordes de hojas apiladas
            pygame.draw.rect(s, PAPEL_SOMBRA, hojas.move(0, i * 3), border_radius=10)
        pygame.draw.rect(s, PAPEL, hojas, border_radius=10)
        # Sombra del lomo
        lomo = pygame.Surface((80, hojas.h), pygame.SRCALPHA)
        for x in range(80):
            a = round(70 * (1 - abs(x - 40) / 40) ** 2)
            pygame.draw.line(lomo, (120, 90, 50, a), (x, 0), (x, hojas.h))
        s.blit(lomo, (hojas.centerx - 40, hojas.y))
        # Cinta marcadora
        pygame.draw.polygon(s, ROJO, [(derecha.right - 70, LIBRO.y), (derecha.right - 46, LIBRO.y),
                                      (derecha.right - 46, LIBRO.y + 70), (derecha.right - 58, LIBRO.y + 60),
                                      (derecha.right - 70, LIBRO.y + 70)])

        clave = ORDEN[self.pagina]
        self._pagina_receta(s, izquierda.inflate(-50, -30), clave)
        self._pagina_foto(s, derecha.inflate(-56, -30), clave)

        # Pie: flechas y número de página
        for lado in (-1, 1):
            r = self._flecha(lado)
            pygame.draw.rect(s, TAPA_OSCURA, r.move(0, 3), border_radius=10)
            pygame.draw.rect(s, TAPA, r, border_radius=10)
            cx, cy = r.center
            punta = [(cx - 10, cy - 12), (cx + 12, cy), (cx - 10, cy + 12)] if lado > 0 else \
                    [(cx + 10, cy - 12), (cx - 12, cy), (cx + 10, cy + 12)]
            pygame.draw.polygon(s, PAPEL, punta)
        # Puntitos de página (sin texto)
        for i in range(len(ORDEN)):
            cx = hojas.centerx + (i - (len(ORDEN) - 1) / 2) * 26
            color = ROJO if i == self.pagina else PAPEL_SOMBRA
            pygame.draw.circle(s, color, (round(cx), hojas.bottom - 26), 7)

    def _pagina_receta(self, s, area, clave):
        receta = RECETAS[clave]
        _texto(s, receta["nombre"], 54, ROJO, midtop=(area.centerx, area.y + 6))
        _texto(s, "Para 1 receta:", 28, TINTA_SUAVE, midtop=(area.centerx, area.y + 74))
        y = area.y + 116
        filas = receta["ingredientes"]
        alto = min(96, (area.bottom - 50 - y) // len(filas))
        for kind, cantidad in filas:
            fila = pygame.Rect(area.x + 10, y, area.w - 20, alto - 10)
            pygame.draw.rect(s, (243, 226, 186), fila, border_radius=12)
            lado = fila.h - 8
            dibujar_hd(s, kind, pygame.Rect(fila.x + 10, fila.y + 4, lado, lado))
            _texto(s, str(cantidad), 48, ROJO, midleft=(fila.x + lado + 28, fila.centery + 2))
            nombre = (PRODUCTOS[kind][0] if cantidad == 1 else PRODUCTOS[kind][1]).lower()
            _texto(s, nombre, 30, TINTA, midleft=(fila.x + lado + 84, fila.centery + 2))
            y += alto

    def _pagina_foto(self, s, area, clave):
        """Foto de muestra del platillo, pegada en la página."""
        foto = pygame.Surface((330, 300), pygame.SRCALPHA)
        pygame.draw.rect(foto, (40, 30, 26, 70), foto.get_rect().move(6, 8), border_radius=6)
        marco = pygame.Rect(0, 0, 322, 292)
        pygame.draw.rect(foto, (255, 253, 246), marco, border_radius=6)
        pygame.draw.rect(foto, (214, 200, 170), marco, 2, border_radius=6)
        imagen = pygame.Rect(16, 16, 290, 216)
        pygame.draw.rect(foto, (236, 222, 190), imagen)
        # Mantel a cuadros detrás del platillo
        for cy in range(imagen.top, imagen.bottom, 24):
            for cx in range(imagen.left, imagen.right, 24):
                if ((cx - imagen.left) // 24 + (cy - imagen.top) // 24) % 2 == 0:
                    pygame.draw.rect(foto, (226, 160, 150),
                                     pygame.Rect(cx, cy, 24, 24).clip(imagen))
        platillo = pygame.Surface((300, 240), pygame.SRCALPHA)
        dibujar_platillo(platillo, clave, (150, 112))
        platillo = pygame.transform.smoothscale_by(platillo, 1.15)
        foto.set_clip(imagen)
        foto.blit(platillo, platillo.get_rect(center=(imagen.centerx, imagen.centery + 6)))
        foto.set_clip(None)
        angulo = (-4, 3, -2, 4, -3)[ORDEN.index(clave) % 5]
        foto = pygame.transform.rotozoom(foto, angulo, 1.18)
        s.blit(foto, foto.get_rect(center=(area.centerx, area.centery - 10)))
        # Cinta adhesiva en las esquinas
        cinta = pygame.Surface((90, 26), pygame.SRCALPHA)
        cinta.fill((240, 226, 160, 170))
        for dx, ang in ((-150, 30), (150, -30)):
            c = pygame.transform.rotate(cinta, ang)
            s.blit(c, c.get_rect(center=(area.centerx + dx, area.centery - 175)))
