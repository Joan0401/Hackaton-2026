"""Vista de cerca de un mueble (refri, góndola, mostrador o estante de bodega).

Al pulsar E frente a un mueble se abre esta pantalla, dibujada a la
resolución real de la ventana (1280 x 720) para que los productos se vean
en alta calidad. Muestra el mueble tal como está, con sus huecos, y el niño
toma un producto haciendo clic sobre él (o con flechas + E).
"""
import pygame

from fuentes import FuenteTienda
from interior import (fridge_bottle_slots, huevera_slots, gondola_canastos,
                      TableObjectManager, MIMBRE, MIMBRE_CLARO, MIMBRE_OSCURO, MIMBRE_FONDO)
from productos import PRODUCTOS
from productos_hd import dibujar_hd

ANCHO, ALTO = 1280, 720
ESCALA_JUEGO = 2            # 640 x 360 -> 1280 x 720
PANEL = pygame.Rect(80, 50, 1120, 620)
CONTENIDO = pygame.Rect(130, 172, 1020, 334)
ZOOM_MAXIMO = 14.0
DURACION_APERTURA = 180     # milisegundos

MADERA = (150, 96, 62)
MADERA_CLARA = (186, 126, 82)
MADERA_OSCURA = (96, 58, 40)
CREMA = (245, 226, 177)
CREMA_OSCURA = (219, 196, 141)
CAFE = (84, 50, 39)
AZUL = (48, 67, 78)
VERDE = (66, 115, 67)
RESALTE = (239, 210, 139)

TITULOS = {
    "gondola_1": "GÓNDOLA DE FRUTAS",
    "gondola_2": "GÓNDOLA DE VERDURAS",
    "counter": "MOSTRADOR",
    "abarrotes": "ESTANTE DE ABARROTES",
    "huevera": "HUEVERA",
    "heladera": "HELADERA",
}

_fuentes = {}


def _fuente(tam):
    if tam not in _fuentes:
        _fuentes[tam] = FuenteTienda(None, tam)
    return _fuentes[tam]


class VistaMueble:
    def __init__(self, origen, mueble, table_object_manager, bodega, player):
        self.origen = origen            # "tienda" o "bodega"
        self.mueble = mueble
        self.tom = table_object_manager
        self.bodega = bodega
        self.player = player
        self.abierta_ms = pygame.time.get_ticks()
        self.sel = 0
        self.usando_teclado = False
        # El área de la bodega se fija al abrir, para que no "salte"
        # cuando se toman productos.
        self._area_bodega = None
        if origen == "bodega":
            rects = [self._rect_logico(i) for i, _ in self._productos_brutos()]
            if rects:
                self._area_bodega = rects[0].unionall(rects[1:]).inflate(14, 14)

    # -----------------------------------------------------
    # DATOS
    # -----------------------------------------------------
    @property
    def titulo(self):
        if self.origen == "bodega":
            return "BODEGA"
        if self.mueble["kind"] == "fridge":
            return "REFRIGERADORA"
        return TITULOS.get(self.mueble["id"], "ESTANTE")

    def _productos_brutos(self):
        if self.origen == "bodega":
            return [(i, None) for i in self.bodega.al_alcance(self.player)]
        return [
            (o, None) for o in self.tom.items
            if o["table_id"] == self.mueble["id"] and o["kind"] in PRODUCTOS
        ]

    def _rect_logico(self, item):
        if self.origen == "bodega":
            return pygame.Rect(item["x"], item["y"], item["w"], item["h"])
        return pygame.Rect(
            round(self.mueble["x"] + item["rel_x"]),
            round(self.mueble["y"] + item["rel_y"]),
            item["w"], item["h"])

    def area_logica(self):
        if self.origen == "bodega":
            return self._area_bodega or pygame.Rect(self.player.x - 20, self.player.y - 40, 40, 20)
        area = self.tom._table_surface(self.mueble)
        # Incluir productos que sobresalgan un poco del área.
        rects = [self._rect_logico(i) for i, _ in self._productos_brutos()]
        return area.unionall(rects) if rects else area

    def _transformacion(self):
        area = self.area_logica()
        zoom = min(CONTENIDO.w / area.w, CONTENIDO.h / area.h, ZOOM_MAXIMO)
        w, h = area.w * zoom, area.h * zoom
        origen = (CONTENIDO.centerx - w / 2, CONTENIDO.centery - h / 2)
        return area, zoom, origen

    def productos(self):
        """[(item, rect en pantalla)] ordenados por fila y columna."""
        area, zoom, (ox, oy) = self._transformacion()
        salida = []
        for item, _ in self._productos_brutos():
            r = self._rect_logico(item)
            rect = pygame.Rect(
                ox + (r.x - area.x) * zoom, oy + (r.y - area.y) * zoom,
                r.w * zoom, r.h * zoom)
            salida.append((item, rect))
        salida.sort(key=lambda par: (round(par[1].bottom / 20), par[1].x))
        return salida

    # -----------------------------------------------------
    # INTERACCIÓN
    # -----------------------------------------------------
    def item_en(self, pos):
        for item, rect in reversed(self.productos()):
            if rect.inflate(8, 8).collidepoint(pos):
                return item
        return None

    def tomar(self, item):
        if self.origen == "bodega":
            return self.bodega.tomar(self.player, self.tom, item)
        return self.tom.tomar_item(item)

    def mover(self, dx, dy):
        prods = self.productos()
        if not prods:
            return
        self.usando_teclado = True
        self.sel = min(self.sel, len(prods) - 1)
        if dx:
            self.sel = (self.sel + dx) % len(prods)
            return
        actual = prods[self.sel][1]
        candidatos = [
            (abs(r.centerx - actual.centerx) + abs(r.centery - actual.centery) * 0.3, i)
            for i, (_, r) in enumerate(prods)
            if (r.centery - actual.centery) * dy > actual.h * 0.4
        ]
        if candidatos:
            self.sel = min(candidatos)[1]

    def tomar_seleccionado(self):
        prods = self.productos()
        if prods:
            self.sel = min(self.sel, len(prods) - 1)
            return self.tomar(prods[self.sel][0])
        return False

    # -----------------------------------------------------
    # DIBUJO
    # -----------------------------------------------------
    def dibujar(self, screen):
        t = min(1.0, (pygame.time.get_ticks() - self.abierta_ms) / DURACION_APERTURA)
        suave = 1 - (1 - t) ** 3

        oscuro = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        oscuro.fill((18, 22, 24, round(180 * suave)))
        screen.blit(oscuro, (0, 0))

        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self._dibujar_panel(capa)
        if t < 1:
            # Animación al desplegarse: crece y sube un poco.
            escala = 0.92 + 0.08 * suave
            capa = pygame.transform.smoothscale_by(capa, escala)
            capa.set_alpha(round(255 * suave))
            x = (ANCHO - capa.get_width()) / 2
            y = (ALTO - capa.get_height()) / 2 + (1 - suave) * 30
            screen.blit(capa, (x, y))
        else:
            screen.blit(capa, (0, 0))

    def _dibujar_panel(self, s):
        pygame.draw.rect(s, (30, 22, 22), PANEL.move(8, 8), border_radius=18)
        pygame.draw.rect(s, CREMA, PANEL, border_radius=18)
        pygame.draw.rect(s, CAFE, PANEL, 6, border_radius=18)

        # Encabezado
        barra = pygame.Rect(PANEL.x + 6, PANEL.y + 6, PANEL.w - 12, 70)
        pygame.draw.rect(s, (154, 74, 62), barra, border_top_left_radius=13, border_top_right_radius=13)
        titulo = _fuente(54).render(self.titulo, True, CREMA)
        s.blit(titulo, titulo.get_rect(midleft=(barra.x + 30, barra.centery + 2)))
        self._dibujar_manos(s, barra)

        # Mueble de fondo
        area, zoom, (ox, oy) = self._transformacion()
        marco = pygame.Rect(ox, oy, area.w * zoom, area.h * zoom).inflate(40, 40)
        if self.origen == "tienda" and self.mueble["kind"] == "fridge":
            self._fondo_refri(s, marco, area, zoom, (ox, oy))
        elif self.origen == "tienda" and self.mueble["kind"] == "huevera":
            self._fondo_huevera(s, marco, area, zoom, (ox, oy))
        elif self.origen == "tienda" and self.mueble["kind"] == "heladera":
            self._fondo_heladera(s, marco)
        else:
            self._fondo_madera(s, marco, area, zoom, (ox, oy))
        es_gondola = self.origen == "tienda" and self.mueble["kind"] == "gondola"
        if es_gondola:
            self._canastos(s, area, zoom, (ox, oy), frente=False)

        # Productos
        prods = self.productos()
        raton = pygame.mouse.get_pos()
        hover = None
        if not self.usando_teclado:
            for item, rect in reversed(prods):
                if rect.inflate(8, 8).collidepoint(raton):
                    hover = item
                    break
        elif prods:
            self.sel = min(self.sel, len(prods) - 1)
            hover = prods[self.sel][0]

        for item, rect in prods:
            destacado = item is hover
            # En repisas anchas hay espacio: los productos se dibujan más grandes.
            crece = 0.18 if (self.origen == "tienda" and self.mueble["kind"] == "fridge") else 0.45
            dibujo = rect.inflate(rect.w * crece, rect.h * crece)
            if destacado:
                fondo = dibujo.inflate(14, 14)
                pygame.draw.rect(s, RESALTE, fondo, border_radius=12)
                pygame.draw.rect(s, (167, 109, 74), fondo, 4, border_radius=12)
                dibujo = dibujo.inflate(dibujo.w * 0.12, dibujo.h * 0.12).move(0, -4)
            dibujar_hd(s, item["kind"], dibujo)
        if es_gondola:
            self._canastos(s, area, zoom, (ox, oy), frente=True)

        # Pie: nombre del producto señalado y ayuda
        pie_y = PANEL.bottom - 84
        if hover is not None:
            nombre = PRODUCTOS[hover["kind"]][0]
            t = _fuente(42).render(nombre, True, CAFE)
            s.blit(t, t.get_rect(center=(PANEL.centerx, pie_y + 6)))
        elif not prods:
            t = _fuente(40).render("¡Aquí ya no quedan productos!", True, CAFE)
            s.blit(t, t.get_rect(center=(PANEL.centerx, pie_y + 6)))
        else:
            t = _fuente(36).render("Elige un producto", True, AZUL)
            s.blit(t, t.get_rect(center=(PANEL.centerx, pie_y + 6)))

    def _dibujar_manos(self, s, barra):
        mano = self.tom.mano
        donde = "EN EL CARRITO" if self.tom.en_carrito else "EN TUS MANOS"
        texto = _fuente(30).render(f"{donde}: {len(mano)}/{self.tom.MAX_MANOS}", True, CREMA)
        paso = 52 if self.tom.MAX_MANOS <= 3 else 40
        x = barra.right - 30 - self.tom.MAX_MANOS * paso
        s.blit(texto, texto.get_rect(midright=(x - 14, barra.centery)))
        for i in range(self.tom.MAX_MANOS):
            caja = pygame.Rect(x + i * paso, barra.centery - (paso - 6) // 2, paso - 6, paso - 6)
            pygame.draw.rect(s, (120, 56, 48), caja, border_radius=8)
            pygame.draw.rect(s, CREMA_OSCURA, caja, 2, border_radius=8)
            if i < len(mano):
                dibujar_hd(s, mano[i]["kind"], caja.inflate(-6, -6))

    def _fondo_madera(self, s, marco, area, zoom, origen):
        pygame.draw.rect(s, MADERA_OSCURA, marco.move(0, 10), border_radius=12)
        pygame.draw.rect(s, MADERA, marco, border_radius=12)
        pygame.draw.rect(s, MADERA_OSCURA, marco, 5, border_radius=12)
        for i in range(1, 6):
            y = marco.y + marco.h * i / 6
            pygame.draw.line(s, (138, 88, 56), (marco.x + 12, y), (marco.right - 12, y), 2)
        # Repisas: una línea bajo cada fila de productos.
        filas = sorted({round(r.bottom) for _, r in self.productos()})
        vistas = []
        for y in filas:
            if all(abs(y - v) > 30 for v in vistas):
                vistas.append(y)
        if self.origen == "tienda" and self.mueble["kind"] == "gondola":
            vistas = []  # Las frutas y verduras van en canastos, no en repisas.
        if self.origen == "tienda" and self.mueble["kind"] == "counter":
            vistas = []  # El mostrador es una superficie lisa, sin repisas.
        for y in vistas:
            pygame.draw.rect(s, MADERA_OSCURA, (marco.x + 8, y + 6, marco.w - 16, 12), border_radius=4)
            pygame.draw.rect(s, MADERA_CLARA, (marco.x + 10, y + 7, marco.w - 20, 4), border_radius=2)

    def _canastos(self, s, area, zoom, origen, frente):
        """Canastos de mimbre de la góndola: el cuerpo o el borde delantero."""
        stock = TableObjectManager.GONDOLA_STOCK.get(self.mueble["id"], [])
        ox, oy = origen
        for cx, cy, cw, ch in gondola_canastos(self.mueble["w"], len(stock)):
            r = pygame.Rect(ox + (self.mueble["x"] + cx - area.x) * zoom,
                            oy + (self.mueble["y"] + cy - area.y) * zoom,
                            cw * zoom, ch * zoom)
            borde = max(6, round(zoom * 2.2))
            if not frente:
                pygame.draw.rect(s, MIMBRE_OSCURO, r.move(0, 6), border_radius=16)
                pygame.draw.rect(s, MIMBRE, r, border_radius=16)
                interior = r.inflate(-borde * 2, -borde * 2)
                pygame.draw.rect(s, MIMBRE_FONDO, interior, border_radius=10)
                # Tejido del fondo y de los costados
                for y in range(interior.top + 10, interior.bottom - 4, 14):
                    pygame.draw.line(s, (112, 74, 44), (interior.left + 6, y), (interior.right - 6, y), 3)
                for y in range(r.top + 6, r.bottom - 6, 10):
                    for x0 in (r.left + 2, r.right - borde + 1):
                        pygame.draw.line(s, MIMBRE_CLARO, (x0, y), (x0 + borde - 4, y + 4), 2)
                pygame.draw.line(s, MIMBRE_CLARO, (r.left + 12, r.top + 3), (r.right - 12, r.top + 3), 3)
            else:
                lip = pygame.Rect(r.left, r.bottom - round(zoom * 2.6), r.w, round(zoom * 3.2))
                pygame.draw.rect(s, MIMBRE_OSCURO, lip.move(0, 5), border_radius=12)
                pygame.draw.rect(s, MIMBRE, lip, border_radius=12)
                pygame.draw.line(s, MIMBRE_CLARO, (lip.left + 10, lip.top + 3), (lip.right - 10, lip.top + 3), 3)
                # Trenzado
                paso = max(10, round(zoom * 3))
                for x in range(lip.left + 8, lip.right - 10, paso):
                    pygame.draw.line(s, MIMBRE_CLARO, (x, lip.top + 8), (x + paso // 2, lip.bottom - 6), 3)
                    pygame.draw.line(s, MIMBRE_OSCURO, (x + paso // 2, lip.top + 8), (x, lip.bottom - 6), 3)

    def _fondo_huevera(self, s, marco, area, zoom, origen):
        """Bandeja de cartón, con los mismos colores del sprite de la huevera."""
        borde = (150, 124, 90)
        carton = (214, 192, 150)
        hoyo = (176, 150, 108)
        hoyo_sombra = (156, 130, 92)
        pygame.draw.rect(s, MADERA_OSCURA, marco.inflate(16, 16).move(0, 10), border_radius=14)
        pygame.draw.rect(s, MADERA_CLARA, marco.inflate(16, 16), border_radius=14)
        pygame.draw.rect(s, borde, marco, border_radius=10)
        pygame.draw.rect(s, carton, marco.inflate(-12, -12), border_radius=8)
        # Hoyitos de la bandeja (también donde ya no hay huevo)
        ox, oy = origen
        w, h = 7, 8
        for rx, ry in huevera_slots():
            x = ox + (self.mueble["x"] + rx - area.x) * zoom
            y = oy + (self.mueble["y"] + ry - area.y) * zoom
            hueco = pygame.Rect(0, 0, w * zoom * 1.25, h * zoom * 0.75)
            hueco.midbottom = (x + w * zoom / 2, y + h * zoom + zoom * 0.6)
            pygame.draw.ellipse(s, hoyo_sombra, hueco)
            pygame.draw.ellipse(s, hoyo, hueco.inflate(-zoom * 0.8, -zoom * 0.8).move(0, zoom * 0.3))

    def _fondo_heladera(self, s, marco):
        """Congelador blanco con el fondo azul de hielo."""
        pygame.draw.rect(s, (110, 120, 130), marco.inflate(20, 20).move(0, 10), border_radius=14)
        pygame.draw.rect(s, (236, 240, 244), marco.inflate(20, 20), border_radius=14)
        pygame.draw.rect(s, (150, 160, 170), marco.inflate(20, 20), 4, border_radius=14)
        pygame.draw.rect(s, (196, 226, 242), marco, border_radius=8)
        medio = marco.centery
        pygame.draw.line(s, (160, 196, 220), (marco.x + 8, medio), (marco.right - 8, medio), 3)

    def _fondo_refri(self, s, marco, area, zoom, origen):
        metal = (150, 160, 166)
        pygame.draw.rect(s, (70, 76, 82), marco.inflate(28, 28).move(0, 10), border_radius=16)
        pygame.draw.rect(s, metal, marco.inflate(28, 28), border_radius=16)
        pygame.draw.rect(s, (70, 76, 82), marco.inflate(28, 28), 5, border_radius=16)
        # Vidrio con degradado
        vidrio = marco
        for i in range(vidrio.h):
            f = i / max(1, vidrio.h - 1)
            color = (round(170 + 40 * (1 - f)), round(214 + 20 * (1 - f)), round(230 + 15 * (1 - f)))
            pygame.draw.line(s, color, (vidrio.x, vidrio.y + i), (vidrio.right - 1, vidrio.y + i))
        pygame.draw.rect(s, (70, 76, 82), vidrio, 4)
        ox, oy = origen
        mx, my = self.mueble["x"], self.mueble["y"]
        # Repisas en las filas de botellas (aunque estén vacías).
        filas = sorted({ry for _, ry, _ in fridge_bottle_slots(self.mueble["w"], self.mueble["body_h"])})
        for ry in filas:
            y = oy + (my + ry + 10 - area.y) * zoom
            pygame.draw.rect(s, (226, 236, 240), (vidrio.x + 6, y, vidrio.w - 12, 8), border_radius=3)
            pygame.draw.line(s, (120, 140, 150), (vidrio.x + 6, y + 8), (vidrio.right - 6, y + 8), 2)
        # Marco central de las puertas y reflejos.
        divisor_x = ox + (mx + 5 + (self.mueble["w"] - 10) // 2 - area.x) * zoom
        pygame.draw.rect(s, metal, (divisor_x - 8, vidrio.y, 16, vidrio.h))
        pygame.draw.rect(s, (70, 76, 82), (divisor_x - 8, vidrio.y, 16, vidrio.h), 3)
        reflejo = pygame.Surface(vidrio.size, pygame.SRCALPHA)
        for k in range(3):
            x0 = vidrio.w * (0.12 + k * 0.33)
            pygame.draw.polygon(reflejo, (255, 255, 255, 40), [
                (x0, 0), (x0 + 40, 0), (x0 - vidrio.h * 0.3 + 40, vidrio.h), (x0 - vidrio.h * 0.3, vidrio.h)])
        s.blit(reflejo, vidrio.topleft)
