"""Reposición de inventario: pedido por teléfono, camión y cajas afuera.

- Con el teléfono del mostrador se piden cajas de productos.
- Unas 2 horas (del reloj del juego) después llega el camión por la calle y
  se estaciona en el costado izquierdo de la tienda.
- Descarga las cajas en la acera y se va. Cada caja trae un solo producto.
- De una caja se saca producto con un menú (E junto a ella). Si Tavo está
  trabajando, primero mete esos insumos a la bodega. Caja vacía: desaparece.
"""
import math

import pygame

from productos import PRODUCTOS, dibujar_producto, tamano

UNIDADES_POR_CAJA = 3       # todas las cajas traen 3 unidades
HORAS_ENTREGA = 2.0
HORA_LIMITE_PEDIDO = 14.0   # después de las 2:00 p. m. ya no se puede pedir

ESTACIONAMIENTO = (92, 244)       # costado izquierdo de la tienda (centro, base)
CARRIL = 272                      # carril por el que llega (va hacia la izquierda)
VELOCIDAD = 95.0
# Dónde quedan las cajas en la acera (al lado del camión)
LUGARES_CAJAS = [(150 + col * 20, 222 + fila * 16) for fila in range(2) for col in range(4)]
MAX_CAJAS = len(LUGARES_CAJAS)    # el camión trae como máximo las que caben en la acera
MAX_CAJAS_POR_PRODUCTO = MAX_CAJAS


def unidades_caja(kind=None):
    """Cuántas unidades trae una caja: siempre 3, de cualquier producto."""
    return UNIDADES_POR_CAJA


def costo(kind):
    """Lo que le cuesta a la pulpería cada unidad (un poco menos de lo que vende)."""
    return max(1, PRODUCTOS[kind][2] - 1)


class Caja:
    def __init__(self, kind, unidades, x, y):
        self.kind = kind
        self.unidades = unidades
        self.x, self.y = x, y

    @property
    def rect(self):
        return pygame.Rect(self.x - 9, self.y - 14, 18, 14)

    @property
    def pies(self):
        return pygame.Rect(self.x - 9, self.y - 5, 18, 5)


class Camion:
    def __init__(self):
        self.pedido = None          # [(kind, unidades)] pendiente
        self.llegada = None         # (día, hora) en que llega
        self.estado = None          # None, llegando, descargando, saliendo
        self.x, self.y = 700.0, float(CARRIL)
        self.por_descargar = []
        self.t = 0.0
        self.cajas = []
        self.recien_llegado = False   # para avisar al jugador una vez

    # -----------------------------------------------------
    @property
    def pendiente(self):
        return self.pedido is not None

    def texto_llegada(self):
        if not self.pendiente or self.llegada is None:
            return ""
        _, hora = self.llegada
        h = int(hora)
        m = int((hora - h) * 60) // 10 * 10
        return f"{h % 12 or 12}:{m:02d} {'a. m.' if h < 12 else 'p. m.'}"

    def pedir(self, pedido, dia, hora):
        """pedido: {kind: cajas}. Devuelve el total a pagar."""
        lista = [(k, c * unidades_caja(k)) for k, c in pedido.items() if c > 0]
        if not lista or self.pendiente:
            return 0
        self.pedido = lista
        self.llegada = (dia, hora + HORAS_ENTREGA)
        return sum(costo(k) * u for k, u in lista)

    def actualizar(self, dt, dia, hora):
        self.t += dt
        if self.pendiente and self.estado is None:
            dia_pedido, hora_llegada = self.llegada
            if dia > dia_pedido or hora >= hora_llegada:
                self.estado = "llegando"
                self.x, self.y = 700.0, float(CARRIL)
                self.por_descargar = list(self.pedido)
        if self.estado == "llegando":
            px, py = ESTACIONAMIENTO
            if self.x > px + 1:
                self.x = max(px, self.x - VELOCIDAD * dt)
            elif self.y > py + 0.5:
                self.y = max(py, self.y - 40 * dt)    # se sube a la orilla
            else:
                self.estado = "descargando"
                self.t = 0.0
                self.recien_llegado = True
        elif self.estado == "descargando":
            if self.t >= 0.5:
                self.t = 0.0
                if self.por_descargar:
                    self._bajar_caja(*self.por_descargar.pop(0))
                else:
                    self.estado = "saliendo"
                    self.pedido = None
                    self.llegada = None
        elif self.estado == "saliendo":
            if self.y < CARRIL:
                self.y = min(CARRIL, self.y + 40 * dt)
            else:
                self.x -= VELOCIDAD * dt
                if self.x < -80:
                    self.estado = None

    def _bajar_caja(self, kind, unidades):
        while unidades > 0:
            ocupados = {(c.x, c.y) for c in self.cajas}
            libre = next((p for p in LUGARES_CAJAS if p not in ocupados), None)
            if libre is None:
                # Acera llena: se suma a una caja del mismo producto.
                misma = next((c for c in self.cajas if c.kind == kind), self.cajas[-1])
                misma.unidades += unidades
                return
            n = min(unidades_caja(kind), unidades)
            self.cajas.append(Caja(kind, n, *libre))
            unidades -= n

    # -----------------------------------------------------
    def unidades_afuera(self, kind):
        """Unidades de ese producto que ya están en cajas en la acera."""
        return sum(c.unidades for c in self.cajas if c.kind == kind)

    def caja_cerca(self, player):
        mejor = None
        for c in self.cajas:
            d = math.hypot(player.x - c.x, player.y - c.y)
            if d <= 26 and (mejor is None or d < mejor[0]):
                mejor = (d, c)
        return mejor[1] if mejor else None

    def sacar(self, caja, cantidad):
        """Saca hasta 'cantidad' de la caja. Devuelve cuántas sacó."""
        n = min(cantidad, caja.unidades)
        caja.unidades -= n
        if caja.unidades <= 0 and caja in self.cajas:
            self.cajas.remove(caja)     # caja vacía: desaparece
        return n

    def obstaculos(self):
        rects = [c.pies for c in self.cajas]
        if self.estado in ("descargando",) or (self.estado == "llegando" and self.y < CARRIL):
            rects.append(pygame.Rect(round(self.x) - 36, round(self.y) - 8, 72, 8))
        return rects

    # -----------------------------------------------------
    def dibujar_camion(self, surface):
        if self.estado is None:
            return
        x, y = round(self.x), round(self.y)
        mira_izq = self.estado != "saliendo" or self.y >= CARRIL
        cuerpo = pygame.Rect(x - 36, y - 34, 50, 28)
        cabina = pygame.Rect(x + 14, y - 26, 22, 20)
        if mira_izq:
            cuerpo = pygame.Rect(x - 14, y - 34, 50, 28)
            cabina = pygame.Rect(x - 36, y - 26, 22, 20)
        pygame.draw.ellipse(surface, (40, 34, 32), (x - 38, y - 5, 76, 8))
        # Caja de carga
        pygame.draw.rect(surface, (35, 27, 27), cuerpo.inflate(2, 2))
        pygame.draw.rect(surface, (236, 230, 214), cuerpo)
        pygame.draw.rect(surface, (198, 64, 52), (cuerpo.x, cuerpo.y + 9, cuerpo.w, 6))
        etiqueta = pygame.Rect(cuerpo.x + 6, cuerpo.y + 17, cuerpo.w - 12, 7)
        pygame.draw.rect(surface, (90, 140, 200), etiqueta)
        # Cabina
        pygame.draw.rect(surface, (35, 27, 27), cabina.inflate(2, 2))
        pygame.draw.rect(surface, (198, 64, 52), cabina)
        vidrio = pygame.Rect(cabina.x + (2 if mira_izq else 10), cabina.y + 3, 10, 8)
        pygame.draw.rect(surface, (176, 214, 220), vidrio)
        # Ruedas
        for rx in (cuerpo.x + 10, cuerpo.right - 8, cabina.centerx):
            pygame.draw.circle(surface, (30, 26, 26), (rx, y - 5), 5)
            pygame.draw.circle(surface, (150, 150, 150), (rx, y - 5), 2)

    def dibujar_caja(self, surface, caja):
        r = caja.rect
        pygame.draw.rect(surface, (60, 44, 34), r.move(1, 2))
        pygame.draw.rect(surface, (196, 150, 98), r)
        pygame.draw.rect(surface, (120, 84, 52), r, 1)
        pygame.draw.line(surface, (160, 118, 74), (r.x + 1, r.y + 4), (r.right - 2, r.y + 4), 1)
        w, h = tamano(caja.kind)
        dibujar_producto(surface, caja.kind, r.centerx - w // 2, r.y - h + 6)
