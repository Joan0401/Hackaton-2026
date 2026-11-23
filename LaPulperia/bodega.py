"""Productos de la bodega: se toman con E y se llevan a la tienda.

Los productos tomados pasan a las manos del personaje (las mismas manos
de TableObjectManager, máximo 3) marcados con origen "bodega", para que
en la tienda se acomoden en los huecos de góndolas y refrigeradoras.
"""
import math

import pygame

from carrito import ancla
from productos import PRODUCTOS, dibujar_producto, tamano
from zonas import stock_inicial_bodega, dibujar_frente_cajas


class Bodega:
    PICKUP_DISTANCE = 42.0
    LATERAL_TOLERANCE = 30.0

    def __init__(self):
        self.items = []
        for tipo, x, y in stock_inicial_bodega():
            w, h = tamano(tipo)
            self.items.append({"kind": tipo, "x": x, "y": y, "w": w, "h": h})
        self._siguiente_id = 0

    def lugar_libre(self, kind):
        """Un lugar vacío de la bodega donde va ese producto, o None."""
        ocupados = {(i["x"], i["y"]) for i in self.items}
        for tipo, x, y in stock_inicial_bodega():
            if tipo == kind and (x, y) not in ocupados:
                return x, y
        return None

    def espacio(self, kind):
        """Cuántos lugares vacíos hay en la bodega para ese producto."""
        ocupados = {(i["x"], i["y"]) for i in self.items}
        return sum(1 for tipo, x, y in stock_inicial_bodega() if tipo == kind and (x, y) not in ocupados)

    def guardar(self, kind):
        """Guarda una unidad en su lugar de la bodega. False si está llena."""
        lugar = self.lugar_libre(kind)
        if lugar is None:
            return False
        w, h = tamano(kind)
        self.items.append({"kind": kind, "x": lugar[0], "y": lugar[1], "w": w, "h": h})
        return True

    def reabastecer(self):
        """Cada mañana llega el camión: la bodega vuelve a estar llena."""
        ocupados = {(i["x"], i["y"]) for i in self.items}
        for tipo, x, y in stock_inicial_bodega():
            if (x, y) not in ocupados:
                w, h = tamano(tipo)
                self.items.append({"kind": tipo, "x": x, "y": y, "w": w, "h": h})

    def al_alcance(self, player):
        """Productos de la bodega que el personaje alcanza desde donde está."""
        facing = {
            "up": (0, -1), "down": (0, 1),
            "left": (-1, 0), "right": (1, 0),
        }
        fx, fy = facing.get(player.direction, (0, 1))
        ax, ay = ancla(player, fx, fy)
        alcanzables = []
        for item in self.items:
            rect = pygame.Rect(item["x"], item["y"], item["w"], item["h"])
            cx = max(rect.left, min(ax, rect.right))
            cy = max(rect.top, min(ay, rect.bottom))
            vx, vy = cx - ax, cy - ay
            if (
                math.hypot(vx, vy) <= self.PICKUP_DISTANCE + 8
                and vx * fx + vy * fy >= -3
                and abs(vx * fy - vy * fx) <= self.LATERAL_TOLERANCE + 10
            ):
                alcanzables.append(item)
        return alcanzables

    def opciones_cerca(self, player):
        """[(tipo, cantidad)] de lo que hay al alcance, para el menú."""
        conteo = {}
        for item in self.al_alcance(player):
            conteo[item["kind"]] = conteo.get(item["kind"], 0) + 1
        return [(k, conteo[k]) for k in PRODUCTOS if k in conteo]

    def tomar_tipo(self, player, table_object_manager, kind):
        """Toma el producto de ese tipo más cercano, de lo que está al alcance."""
        candidatos = [i for i in self.al_alcance(player) if i["kind"] == kind]
        if not candidatos:
            return False
        item = min(candidatos, key=lambda i: abs(i["x"] + i["w"] / 2 - player.x))
        return self.tomar(player, table_object_manager, item)

    def find_target(self, player):
        """Producto de la bodega más cercano frente al personaje."""
        facing = {
            "up": (0, -1), "down": (0, 1),
            "left": (-1, 0), "right": (1, 0),
        }
        fx, fy = facing.get(player.direction, (0, 1))
        ax, ay = ancla(player, fx, fy)
        mejor = None
        for item in self.items:
            rect = pygame.Rect(item["x"], item["y"], item["w"], item["h"])
            cx = max(rect.left, min(ax, rect.right))
            cy = max(rect.top, min(ay, rect.bottom))
            vx, vy = cx - ax, cy - ay
            distancia = math.hypot(vx, vy)
            if (
                distancia <= self.PICKUP_DISTANCE
                and vx * fx + vy * fy >= -3
                and abs(vx * fy - vy * fx) <= self.LATERAL_TOLERANCE
            ):
                if mejor is None or distancia < mejor[0]:
                    mejor = (distancia, item)
        return mejor[1] if mejor else None

    def tomar(self, player, table_object_manager, item=None):
        """Pasa el producto de enfrente a las manos. True si lo tomó."""
        if item is None:
            item = self.find_target(player)
        if item is None:
            return False
        tom = table_object_manager
        if len(tom.mano) >= tom.MAX_MANOS:
            tom.avisar(*tom.mensaje_manos_llenas("a la tienda"))
            return False

        self.items.remove(item)
        self._siguiente_id += 1
        nombre, _, precio = PRODUCTOS[item["kind"]]
        nuevo = {
            "id": f"bodega_{self._siguiente_id}",
            "label": nombre,
            "kind": item["kind"],
            "table_id": "mano",
            "rel_x": 0,
            "rel_y": 0,
            "w": item["w"],
            "h": item["h"],
            "color": (224, 210, 168),
            "price": precio,
            "origen": "bodega",
            # Lugar original en la bodega, por si se devuelve (tecla Q).
            "antes_bodega": (item["x"], item["y"]),
        }
        tom.items.append(nuevo)
        tom.mano.append(nuevo)
        return True

    def devolver(self, table_object_manager):
        """Tecla Q: el último producto de la bodega vuelve a su lugar."""
        tom = table_object_manager
        item = next(
            (i for i in reversed(tom.mano) if "antes_bodega" in i), None
        )
        if item is None:
            if tom.mano:
                tom.avisar("Eso es de la tienda.",
                           "Devuélvelo en su estante de la tienda.")
            return False
        tom.mano.remove(item)
        tom.items.remove(item)
        x, y = item["antes_bodega"]
        self.items.append({
            "kind": item["kind"], "x": x, "y": y,
            "w": item["w"], "h": item["h"],
        })
        return True

    def mensaje_hud(self, player, table_object_manager):
        """Texto de ayuda de abajo mientras se está en la bodega."""
        mano = table_object_manager.mano
        maximo = table_object_manager.MAX_MANOS
        target = self.find_target(player)
        devolver = (
            "    Q: DEVOLVER"
            if any("antes_bodega" in i for i in mano) else ""
        )
        if target is not None and len(mano) < maximo:
            prefijo = f"{table_object_manager.texto_llevas()}    " if mano else ""
            accion = "ELEGIR QUÉ TOMAR"
            return f"{prefijo}E: {accion}{devolver}"
        if mano:
            llevas = table_object_manager.texto_llevas()
            if table_object_manager.en_carrito:
                return f"{llevas}    ESPACIO: SOLTAR CARRITO{devolver}"
            return f"{llevas}    LLEVALOS A LA TIENDA{devolver}"
        return "E: TOMAR PRODUCTOS PARA LA TIENDA"

    def dibujar(self, surface):
        for item in self.items:
            dibujar_producto(surface, item["kind"], item["x"], item["y"])
        # Las cajas tapan la mitad inferior de lo que tienen adentro.
        dibujar_frente_cajas(surface)
