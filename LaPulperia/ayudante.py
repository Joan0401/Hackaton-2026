"""Ayudante (Tavo): rellena góndolas, refris, el estante y la huevera.

- Se llama con el botón de la pared derecha (E junto al botón).
- Dice cuántas horas puede trabajar: de 3 a 8, según el día y la hora en
  que se le llama (nunca más de las que quedan antes del cierre).
- Mientras trabaja va a la bodega y trae hasta 3 productos en las manos
  (u 8 si usa el carrito, cuando el pulpero no lo está usando) y los
  acomoda en los huecos de los muebles.
- Al terminar el turno dice: "Hoy trabajé X horas y son 3 colones la hora"
  y el niño calcula cuánto pagarle (multiplicación).
"""
import math
import random
from collections import Counter

import pygame

from carrito import CAPACIDAD as EN_CARRITO, FRENTE
from clientes import crear_persona, _burbuja
from productos import PRODUCTOS, FRUTAS, VERDURAS, BEBIDAS, ABARROTES, HUEVOS, HELADOS, tamano

NOMBRE = "Tavo"
PAGO_POR_HORA = 3
# Horas extra (se queda a guardar el pedido del camión): al mismo precio si el
# camión llegó durante su turno; a 5 si llega después de su hora de salida.
PAGO_EXTRA_TARDE = 5
VELOCIDAD = 62.0           # px por segundo
HORA_CIERRE = 20.0   # Tavo puede quedarse hasta las 8:00 p. m. (ayuda a acomodar)

# Pasillos por donde camina (coordenadas 640 x 360).
PASILLO_ARRIBA, PASILLO_MEDIO, PASILLO_ABAJO = 126, 242, 340
CORREDOR_X = 284           # pasillo vertical entre las góndolas y la huevera
PUERTA_BODEGA = (612, PASILLO_ARRIBA)
AFUERA = (668, 140)        # detrás de la puerta de la bodega
LUGAR_COBRO = (606, 262)   # junto al botón, esperando su pago
PUERTA_CALLE = (283, PASILLO_ABAJO)   # por aquí sale a buscar las cajas (alfombra CALLE)
EN_MANOS = 3               # lo que lleva en las manos en cada viaje

# Botón en la pared derecha
BOTON = pygame.Rect(618, 206, 22, 30)

DATOS = {
    "nombre": NOMBRE, "skin": "hombre",
    "HAIR": (58, 40, 30), "HAIR_LIGHT": (96, 70, 52),
    "SHIRT": (62, 140, 96), "SHIRT_LIGHT": (110, 186, 140), "SHIRT_DARK": (40, 98, 66),
    "SKIN": (186, 130, 92), "SKIN_LIGHT": (210, 156, 116), "SKIN_SHADOW": (142, 94, 64),
}


HORAS_MIN, HORAS_MAX = 3, 8


def horas_disponibles(dia, hora):
    """Cuántas horas puede trabajar si lo llaman ese día a esa hora: de 3 a 8
    al azar. Si ya no quedan ni 3 horas antes del cierre, no puede venir."""
    quedan = int(HORA_CIERRE - hora)
    if quedan < HORAS_MIN:
        return 0
    rng = random.Random(f"tavo-{dia}-{int(hora)}")
    return min(rng.randint(HORAS_MIN, HORAS_MAX), quedan)


def surtido(tom, mueble):
    """Qué productos van en ese mueble."""
    kind = mueble["kind"]
    if kind == "gondola":
        return tom.GONDOLA_STOCK.get(mueble["id"], FRUTAS)
    if kind == "fridge":
        return tom.FRIDGE_STOCK.get(mueble["id"], BEBIDAS)
    if kind == "abarrotes":
        return ABARROTES
    if kind == "huevera":
        return HUEVOS
    if kind == "heladera":
        return HELADOS
    return []


def lugar_de_trabajo(mueble):
    """Dónde se para para acomodar en ese mueble (en un pasillo)."""
    cx = mueble["x"] + mueble["w"] / 2
    if mueble["y"] + mueble["h"] <= 140 or mueble["kind"] == "abarrotes":
        y = PASILLO_ARRIBA
    elif mueble["y"] + mueble["h"] <= 245:
        y = PASILLO_MEDIO
    else:
        y = PASILLO_ABAJO
    return (cx, y)


def camino(desde, hasta):
    """Ruta por los pasillos: horizontal, por el corredor y horizontal."""
    (x0, y0), (x1, y1) = desde, hasta
    if abs(y0 - y1) < 4:
        return [hasta]
    corredor = PUERTA_BODEGA[0] if x0 > 560 and x1 > 560 else CORREDOR_X
    return [(corredor, y0), (corredor, y1), hasta]


class Ayudante:
    WIDTH = 28

    def __init__(self):
        self.persona = crear_persona(DATOS)
        self.persona.APRON = (236, 232, 220)          # delantal blanco de trabajo
        self.persona.APRON_LIGHT = (250, 248, 240)
        self.persona.APRON_DARK = (196, 190, 178)
        self.persona.frames = self.persona._build_frames()
        self.nombre = NOMBRE
        self.camion = None          # el juego le pasa el camión (cajas afuera)
        self.carrito = None         # ... y el carrito (lo usa si está libre)
        self.nuevo_dia()

    def nuevo_dia(self):
        if getattr(self, "con_carrito", False):
            self.soltar_carrito()
        self.estado = "ausente"       # ausente, trabajando, cobrando, saliendo
        self.trabajo_hoy = False
        self.horas = 0
        self.fin = 0.0
        self.ruta = []
        self.tarea = None             # None, "carrito", "surtir", "caja", "devolver"
        self.paradas = []             # [(mueble, [productos])] del viaje actual
        self.recogido = False         # ya sacó los productos (de la bodega o la caja)
        self.carga = []               # lo que lleva (en las manos o en el carrito)
        self.con_carrito = False
        self.espera = 0.0
        self.texto = None
        self.texto_t = 0.0
        self.acomodados = 0
        self.guardados = 0
        self.en_extra = False      # se quedó después de su hora por el camión
        self.extras = 0            # horas extra (se cuentan al terminar)
        self.tarifa_extra = PAGO_POR_HORA
        self.hora_actual = 0.0
        self.afuera = 0.0          # segundos que está afuera, en las cajas
        self.caja_afuera = None    # la caja de la que está sacando
        self.t = 0.0
        self.persona.x, self.persona.y = AFUERA

    # -----------------------------------------------------
    @property
    def x(self):
        return self.persona.x

    @property
    def y(self):
        return self.persona.y

    @property
    def presente(self):
        return self.estado != "ausente"

    @property
    def esperando_pago(self):
        return self.estado == "cobrando" and not self.ruta

    @property
    def pago(self):
        return self.horas * PAGO_POR_HORA + self.extras * self.tarifa_extra

    def pedido_por_guardar(self):
        """Hay un pedido del camión en camino o cajas afuera por guardar."""
        return self.camion is not None and (self.camion.pendiente or bool(self.camion.cajas))

    def _empezar_extra(self):
        """Llegó su hora de salida, pero hay un pedido: se queda."""
        self.en_extra = True
        llega_tarde = self.camion.pendiente       # el camión todavía no ha llegado
        self.tarifa_extra = PAGO_EXTRA_TARDE if llega_tarde else PAGO_POR_HORA
        if llega_tarde:
            self.decir("Ya es mi hora de salida, pero me quedo a esperar el camión. "
                       f"Las horas extra son a {self.tarifa_extra} colones.", 6.0)
        else:
            self.decir("Ya es mi hora de salida, pero me quedo a guardar el pedido. "
                       f"Las horas extra son a {self.tarifa_extra} colones.", 6.0)

    @property
    def capacidad(self):
        """Cuánto puede llevar en un viaje: 3 en las manos, 8 con el carrito."""
        return EN_CARRITO if self.con_carrito else EN_MANOS

    def decir(self, texto, segundos=None):
        self.texto = texto
        self.texto_t = segundos if segundos is not None else -1

    # -----------------------------------------------------
    def llamar(self, dia, hora):
        """Botón de la pared. Devuelve el texto para avisar, o None si vino."""
        if self.presente:
            return f"{NOMBRE} ya está aquí."
        if self.trabajo_hoy:
            return f"{NOMBRE} ya trabajó hoy. ¡Llámalo mañana!"
        horas = horas_disponibles(dia, hora)
        if horas < 1:
            return f"Ya es tarde: {NOMBRE} trabaja mínimo {HORAS_MIN} horas."
        self.horas = horas
        self.fin = hora + horas
        self.estado = "trabajando"
        self.trabajo_hoy = True
        self.acomodados = 0
        self.persona.x, self.persona.y = AFUERA
        self.ruta = [PUERTA_BODEGA]
        palabra = "hora" if horas == 1 else "horas"
        self.decir(f"¡Hola! Soy {NOMBRE}. Hoy puedo trabajar {horas} {palabra}.", 5.0)
        return None

    def terminar_turno(self, tom, bodega):
        """Se acabó el turno: guarda lo que traía, deja el carrito y va a cobrar."""
        if self.estado != "trabajando":
            return
        if self.en_extra:
            # Las horas extra se cuentan completas (la que empezó, se paga).
            self.extras = max(1, math.ceil(self.hora_actual - self.fin - 1e-6))
            self.en_extra = False
        if self.afuera > 0:
            self.persona.x, self.persona.y = PUERTA_CALLE
            self.persona.direction = "up"
            if self.con_carrito:
                self.carrito.escena = "interior"
                self.carrito.x, self.carrito.y = PUERTA_CALLE[0] - 26, PUERTA_CALLE[1] - 4
        self._guardar_carga(bodega)
        self.soltar_carrito()
        self.afuera = 0.0
        self.tarea = None
        self.paradas = []
        self.estado = "cobrando"
        self.ruta = camino((self.x, self.y), LUGAR_COBRO)
        palabra = "hora" if self.horas == 1 else "horas"
        if self.extras:
            extra = "hora extra" if self.extras == 1 else "horas extra"
            self.decir(f"Hoy trabajé {self.horas} {palabra} y son {PAGO_POR_HORA} colones "
                       f"la hora, más {self.extras} {extra} a {self.tarifa_extra} colones. "
                       "¿Cuánto me pagas?")
        else:
            self.decir(f"Hoy trabajé {self.horas} {palabra} y son {PAGO_POR_HORA} colones "
                       "la hora. ¿Cuánto me pagas?")

    def pagado(self):
        self.estado = "saliendo"
        self.decir("¡Gracias! ¡Hasta mañana!", 2.5)
        self.ruta = camino((self.x, self.y), PUERTA_BODEGA) + [AFUERA]

    # -----------------------------------------------------
    def actualizar(self, dt, hora, tom, furniture_manager, bodega):
        if self.estado == "ausente":
            return
        self.t += dt
        if self.texto_t > 0:
            self.texto_t -= dt
            if self.texto_t <= 0:
                self.texto = None

        self.hora_actual = hora
        if self.estado == "trabajando" and hora >= self.fin and not self.en_extra:
            if self.pedido_por_guardar():
                self._empezar_extra()
            else:
                self.terminar_turno(tom, bodega)

        if self.afuera > 0:
            self.afuera -= dt
            if self.afuera <= 0:
                # Vuelve de afuera con lo que sacó de la caja.
                self.persona.x, self.persona.y = PUERTA_CALLE
                self.persona.direction = "up"
                if self.con_carrito:
                    self.carrito.escena = "interior"
                    self._mover_carrito(suave=False)
                self.ruta = camino(PUERTA_CALLE, PUERTA_BODEGA)
            return
        if self.ruta:
            self._caminar(dt)
            return
        if self.espera > 0:
            self.espera -= dt
            return

        if self.estado == "saliendo":
            self.estado = "ausente"
            self.texto = None
            return
        if self.estado == "trabajando":
            if self.en_extra and self.tarea is None and not self.pedido_por_guardar():
                # Ya guardó todo el pedido: ahora sí termina.
                self.terminar_turno(tom, bodega)
                return
            self._trabajar(tom, furniture_manager, bodega)

    def _caminar(self, dt):
        p = self.persona
        tx, ty = self.ruta[0]
        dx, dy = tx - p.x, ty - p.y
        dist = math.hypot(dx, dy)
        paso = VELOCIDAD * dt
        if dist <= paso:
            p.x, p.y = tx, ty
            self.ruta.pop(0)
        else:
            p.x += dx / dist * paso
            p.y += dy / dist * paso
        if abs(dx) > abs(dy):
            p.direction = "right" if dx > 0 else "left"
        elif dist > 0.5:
            p.direction = "down" if dy > 0 else "up"
        p.frame = int(self.t / p.WALK_FRAME_TIME) % 2
        if self.con_carrito:
            self._mover_carrito()

    # -----------------------------------------------------
    # Carrito
    def carrito_libre(self):
        """El carrito se puede usar si nadie lo empuja y está vacío."""
        c = self.carrito
        return (c is not None and not c.empujando and not getattr(c, "ayudante", False)
                and not c.items and c.escena in ("interior", "inventario"))

    def _tomar_carrito(self):
        c = self.carrito
        c.ayudante = True
        c.items = self.carga           # lo que lleva se ve adentro del carrito
        c.escena = "interior"
        self.con_carrito = True
        self._mover_carrito(suave=False)

    def _mover_carrito(self, suave=True):
        c = self.carrito
        dx, dy = FRENTE.get(self.persona.direction, (0, 12))
        x, y = self.x + dx, self.y + dy
        if suave:
            c.x += (x - c.x) * 0.35
            c.y += (y - c.y) * 0.35
        else:
            c.x, c.y = x, y
        if self.persona.direction in ("left", "right"):
            c.mira_derecha = self.persona.direction == "left"

    def soltar_carrito(self, bodega=None):
        """Deja el carrito donde está. Si el pulpero se lo pide, Tavo se queda
        con 3 productos en las manos y el resto lo devuelve a la bodega."""
        if not self.con_carrito:
            return
        c = self.carrito
        c.ayudante = False
        c.items = []
        if c.escena not in ("interior", "inventario"):
            c.escena = "interior"
            c.x, c.y = PUERTA_CALLE[0] - 26, PUERTA_CALLE[1] - 4
        self.con_carrito = False
        if bodega is not None and len(self.carga) > EN_MANOS:
            sobra = self.carga[EN_MANOS:]
            del self.carga[EN_MANOS:]
            for item in sobra:
                self._guardar_uno(item, bodega)

    def prestar_carrito(self, bodega):
        """El pulpero quiere el carrito: Tavo se lo deja."""
        self.soltar_carrito(bodega)
        self.decir("¡Te lo presto! Sigo con las manos.", 2.5)

    # -----------------------------------------------------
    def _guardar_uno(self, item, bodega):
        if "x" in item:
            bodega.items.append(item)       # vino de la bodega: vuelve a su lugar
        elif bodega.guardar(item["kind"]):  # vino de una caja de afuera
            self.guardados += 1

    def _guardar_carga(self, bodega):
        for item in list(self.carga):
            self._guardar_uno(item, bodega)
        del self.carga[:]                   # (la misma lista que ve el carrito)

    def _hay_cajas(self, bodega):
        return (self.camion is not None
                and any(bodega.espacio(c.kind) > 0 for c in self.camion.cajas))

    def _trabajar(self, tom, furniture_manager, bodega):
        """Un viaje: (agarrar el carrito) -> bodega -> muebles -> volver.

        Lleva hasta 3 productos en las manos, u 8 si usa el carrito (solo si el
        pulpero no lo está usando). Si hay cajas del camión afuera, primero
        las mete a la bodega.
        """
        if self.tarea == "carrito":
            self.tarea = None
            if self.carrito_libre():
                if self.carrito.escena == "interior":
                    self.persona.direction = "left"
                self._tomar_carrito()
                self.decir("¡Uso el carrito para llevar más!", 2.5)
                self.espera = 0.5
            return
        if self.tarea == "caja":
            self._paso_caja(bodega)
            return
        if self.tarea == "surtir":
            self._paso_surtir(tom, furniture_manager, bodega)
            return
        if self.tarea == "devolver":
            self._guardar_carga(bodega)
            self.tarea = None
            self.espera = 0.6
            return

        hay_cajas = self._hay_cajas(bodega)
        paradas = [] if hay_cajas else self._planear(tom, furniture_manager, bodega)
        if not hay_cajas and not paradas:
            if self.en_extra and not self.camion.pendiente:
                # Las cajas que quedan ya no caben en ningún lado: termina.
                self.terminar_turno(tom, bodega)
                return
            # Todo está lleno: espera un rato.
            self.persona.direction = "down"
            self.espera = 2.0
            return
        if not self.con_carrito and self.carrito_libre():
            # Primero va por el carrito para llevar más en cada viaje.
            self.tarea = "carrito"
            c = self.carrito
            destino = (c.x + 20, c.y) if c.escena == "interior" else PUERTA_BODEGA
            self.ruta = camino((self.x, self.y), destino)
            return
        self.recogido = False
        if hay_cajas:
            self.tarea = "caja"
            self.ruta = camino((self.x, self.y), PUERTA_CALLE)
        else:
            self.tarea = "surtir"
            self.paradas = paradas
            self.ruta = camino((self.x, self.y), PUERTA_BODEGA)

    def _paso_surtir(self, tom, furniture_manager, bodega):
        if not self.recogido:
            # Está en la puerta: entra a la bodega por los productos.
            self.recogido = True
            paradas = []
            for mueble, kinds in self.paradas:
                tomados = []
                for kind in kinds:
                    if len(self.carga) >= self.capacidad:
                        break
                    item = next((i for i in bodega.items if i["kind"] == kind), None)
                    if item is None:
                        continue
                    bodega.items.remove(item)
                    self.carga.append(item)
                    tomados.append(kind)
                if tomados:
                    paradas.append((mueble, tomados))
            self.paradas = paradas
            if not paradas:
                self.tarea = None
                return
            self.espera = 1.0
            self.ruta = camino(PUERTA_BODEGA, lugar_de_trabajo(paradas[0][0]))
            return
        # Llegó a un mueble: acomoda lo que va ahí.
        mueble, kinds = self.paradas.pop(0)
        self.persona.direction = "up" if lugar_de_trabajo(mueble)[1] > mueble["y"] else "down"
        for kind in kinds:
            item = next((i for i in self.carga if i["kind"] == kind), None)
            if item is not None and self._acomodar(tom, mueble, item, bodega):
                self.carga.remove(item)
        self.espera = 0.4 + 0.15 * len(kinds)
        if self.paradas:
            self.ruta = camino((self.x, self.y), lugar_de_trabajo(self.paradas[0][0]))
        elif self.carga:
            # No cupo todo: lo que sobró vuelve a la bodega.
            self.tarea = "devolver"
            self.ruta = camino((self.x, self.y), PUERTA_BODEGA)
        else:
            self.tarea = None

    def _paso_caja(self, bodega):
        if not self.recogido:
            # Llegó a la puerta de la calle: sale a la acera y saca de las cajas
            # solo lo que cabe en la bodega.
            self.recogido = True
            self.caja_afuera = None
            for caja in list(self.camion.cajas):
                libre = self.capacidad - len(self.carga)
                if libre <= 0:
                    break
                ya = sum(1 for i in self.carga if i["kind"] == caja.kind)
                n = min(libre, bodega.espacio(caja.kind) - ya)
                if n <= 0:
                    continue
                if self.caja_afuera is None:
                    self.caja_afuera = caja
                n = self.camion.sacar(caja, n)
                self.carga.extend({"kind": caja.kind} for _ in range(n))
            if not self.carga:
                self.tarea = None
                return
            self.afuera = 2.5
            if self.con_carrito:
                c = self.carrito
                c.escena = "calle"
                c.x, c.y = self.caja_afuera.x + 34, self.caja_afuera.y + 6
                c.mira_derecha = True
            return
        # Llegó a la puerta de la bodega: guarda todo.
        self._guardar_carga(bodega)
        self.caja_afuera = None
        self.tarea = None
        self.espera = 1.0

    def _planear(self, tom, furniture_manager, bodega):
        """Qué llevar en el próximo viaje: [(mueble, [productos])].

        Busca el mueble más cercano con huecos, lo llena con lo que hay en la
        bodega y sigue con el siguiente más cercano, hasta llenar las manos
        (3) o el carrito (8). Los huecos se "apartan" mientras planea.
        """
        cap = EN_CARRITO if (self.con_carrito or self.carrito_libre()) else EN_MANOS
        hay = Counter(i["kind"] for i in bodega.items)
        pendientes = [m for m in furniture_manager.items if surtido(tom, m)]
        apartados, paradas, total = [], [], 0
        pos = (self.x, self.y)

        def plantilla(kind):
            w, h = tamano(kind)
            return {"kind": kind, "w": w, "h": h, "id": "plan", "label": "",
                    "table_id": None, "rel_x": 0, "rel_y": 0}

        try:
            while total < cap and pendientes:
                candidatos = []
                for m in pendientes:
                    x = lugar_de_trabajo(m)[0]
                    if any(hay[k] > 0 and tom._lugar_libre(m, plantilla(k), x) is not None
                           for k in dict.fromkeys(surtido(tom, m))):
                        candidatos.append((math.dist(pos, lugar_de_trabajo(m)), id(m), m))
                if not candidatos:
                    break
                _, _, mueble = min(candidatos, key=lambda c: c[0])
                pendientes.remove(mueble)
                x = lugar_de_trabajo(mueble)[0]
                kinds, avanza = [], True
                while total < cap and avanza:
                    avanza = False
                    for k in dict.fromkeys(surtido(tom, mueble)):   # se turnan los productos
                        if total >= cap or hay[k] <= 0:
                            continue
                        p = plantilla(k)
                        lugar = tom._lugar_libre(mueble, p, x)
                        if lugar is None:
                            continue
                        p.update(table_id=mueble["id"], rel_x=lugar[0] - round(mueble["x"]),
                                 rel_y=lugar[1] - round(mueble["y"]))
                        tom.items.append(p)
                        apartados.append(p)
                        kinds.append(k)
                        hay[k] -= 1
                        total += 1
                        avanza = True
                if kinds:
                    paradas.append((mueble, kinds))
                    pos = lugar_de_trabajo(mueble)
        finally:
            for p in apartados:
                tom.items.remove(p)
        return paradas

    def _acomodar(self, tom, mueble, item_bodega, bodega):
        kind = item_bodega["kind"]
        w, h = tamano(kind)
        nuevo = {
            "id": f"tavo_{id(item_bodega)}_{self.acomodados}",
            "label": PRODUCTOS[kind][0], "kind": kind,
            "table_id": None, "rel_x": 0, "rel_y": 0, "w": w, "h": h,
            "color": (224, 210, 168), "price": PRODUCTOS[kind][2],
        }
        lugar = tom._lugar_libre(mueble, nuevo, self.x)
        if lugar is None:
            return False
        nuevo["table_id"] = mueble["id"]
        nuevo["rel_x"] = lugar[0] - round(mueble["x"])
        nuevo["rel_y"] = lugar[1] - round(mueble["y"])
        tom.items.append(nuevo)
        self.acomodados += 1
        return True

    # -----------------------------------------------------
    def dibujar(self, surface, escena="interior"):
        if not self.presente or escena != "interior" or self.afuera > 0:
            return
        self.persona.draw(surface)
        if self.con_carrito or not self.carga:
            return
        from productos import dibujar_producto
        n = len(self.carga)
        for i, item in enumerate(self.carga[:EN_MANOS]):
            w, h = tamano(item["kind"])
            x = round(self.x) - w // 2 + (i - (n - 1) / 2) * 8
            dibujar_producto(surface, item["kind"], round(x),
                             round(self.y) - self.persona.HEIGHT - h - (i % 2) * 2)

    def dibujar_afuera(self, surface):
        """En la calle: se ve junto a la caja mientras saca los productos."""
        if self.afuera <= 0 or self.caja_afuera is None:
            return
        p = self.persona
        x, y, d = p.x, p.y, p.direction
        p.x, p.y, p.direction = self.caja_afuera.x + 14, self.caja_afuera.y + 4, "left"
        p.draw(surface)
        p.x, p.y, p.direction = x, y, d
        if self.con_carrito and self.carrito.escena == "calle":
            self.carrito.dibujar(surface, "calle")

    def dibujar_globo(self, surface, font):
        if self.presente and self.texto:
            _burbuja(surface, font, self, self.texto, (62, 120, 80), [])


def dibujar_boton(surface, encendido=False):
    """Botón en la pared derecha para llamar al ayudante."""
    r = BOTON
    pygame.draw.rect(surface, (35, 27, 27), r.move(-2, 2))
    pygame.draw.rect(surface, (120, 78, 52), r)
    pygame.draw.rect(surface, (78, 50, 34), r, 2)
    # Muñequito
    pygame.draw.circle(surface, (236, 220, 190), (r.centerx, r.y + 7), 3)
    pygame.draw.rect(surface, (62, 140, 96), (r.centerx - 3, r.y + 10, 7, 6))
    # Botón rojo (verde si el ayudante está trabajando)
    color = (90, 196, 110) if encendido else (214, 58, 48)
    pygame.draw.circle(surface, (60, 30, 28), (r.centerx, r.bottom - 7), 5)
    pygame.draw.circle(surface, color, (r.centerx, r.bottom - 8), 4)
    pygame.draw.circle(surface, (255, 220, 210), (r.centerx - 1, r.bottom - 9), 1)


def cerca_boton(player):
    return math.hypot(player.x - BOTON.left, player.y - BOTON.bottom) <= 30


def rect_boton():
    """Base sólida: el personaje no se mete en el botón."""
    return pygame.Rect(BOTON.left, BOTON.bottom - 8, BOTON.w, 10)
