"""Clientes con pedidos para La Pulpería (memoria de trabajo y deducción).

Un cliente entra desde la calle, camina hasta detrás del mostrador y dice
su pedido. Según el nivel (niveles.py), el pedido:
  - principiante: siempre visible, 1 producto;
  - intermedio: se oculta a los 8 s, 2-3 productos;
  - avanzado: se oculta a los 5 s, 3-4 productos, algunos con pistas
    ("una fruta que no es roja ni amarilla"), 2 clientes en fila y vuelto.

El niño junta los productos en el mostrador y abre la caja. El cliente
revisa el mostrador: si falta o sobra algo lo dice; si está bien, se hace
la factura y el cliente se va contento.
La tecla P pide que el cliente repita el pedido (se cuenta como ayuda).
"""
import random
import re

import pygame

from personaje import Player
from productos import PRODUCTOS, FRUTAS, VERDURAS, BEBIDAS, dibujar_producto, tamano
import recetas
import disfraces
from modos import MODO, factores_permitidos
import estadisticas
from horario import DURACION_DIA, HORA_INICIO, HORA_FIN, HORA_CIERRE_TIENDA

# ---------------------------------------------------------
# RECORRIDO (coordenadas lógicas 640 x 360)
# ---------------------------------------------------------
PUERTA = (283, 400)                 # afuera, por la alfombrilla CALLE (zonas.PUERTA_SALA_X)
PASILLO = (283, 158)                # pasillo entre góndolas y mostrador
# Del lado de los clientes del mostrador: el primero (el FRENTE) frente a la
# caja registradora y la fila hacia la izquierda, todos a lo largo del
# mostrador (x de 378 a 588). Cuántos caben depende del nivel.
LUGARES = [(545 - 28 * k, 158) for k in range(6)]   # pegados al mostrador (y = 164)
# Los lugares siguen al mostrador: si se mueve (SHIFT+E), la fila se corre.
FRENTE_DX, FRENTE_DY, PASO_FILA = 167, -6, 28


def lugares_del_mostrador(mostrador):
    """Lugares de la fila frente a ese mostrador (el primero frente a la caja)."""
    x0 = mostrador["x"] + FRENTE_DX
    y0 = mostrador["y"] + FRENTE_DY
    return [(round(x0 - PASO_FILA * k), round(y0)) for k in range(len(LUGARES))]
VELOCIDAD = 75.0
ESPERA_PRIMER_CLIENTE = 2.0
ESPERA_ENTRE_CLIENTES = 3.0
# Entre un cliente y el siguiente pasan de 20 a 70 minutos del reloj del
# juego (al azar). Si se atendió a alguien, el tiempo empieza a contar
# cuando ese cliente ya salió por completo de la tienda.
MINUTOS_ENTRE_CLIENTES = (20, 70)
HORA_PRIMER_CLIENTE = 8.5      # la pulpería abre a las 8:00; el primero llega a las 8:30
SEGUNDOS_RECLAMO = 4.0
SEGUNDOS_GRACIAS = 3.0
SEGUNDOS_ENOJO = 3.0
AVISO_PRISA = 0.25          # fracción de paciencia que queda al decir "¡Apúrate!"

# ---------------------------------------------------------
# PERSONAJES (mismo dibujo del jugador, otra ropa y sin delantal)
# ---------------------------------------------------------
PERSONAJES = [
    {"nombre": "Doña Rosa", "skin": "mujer",
     "HAIR": (196, 196, 204), "HAIR_LIGHT": (232, 232, 238),
     "SHIRT": (124, 92, 164), "SHIRT_LIGHT": (170, 140, 200), "SHIRT_DARK": (86, 62, 120)},
    {"nombre": "Don Chepe", "skin": "hombre",
     "HAIR": (92, 92, 98), "HAIR_LIGHT": (140, 140, 146),
     "SHIRT": (204, 164, 66), "SHIRT_LIGHT": (232, 204, 120), "SHIRT_DARK": (150, 116, 44),
     "SKIN": (198, 140, 100), "SKIN_LIGHT": (220, 168, 126), "SKIN_SHADOW": (152, 100, 70)},
    {"nombre": "Lucía", "skin": "mujer",
     "HAIR": (40, 28, 26), "HAIR_LIGHT": (82, 58, 46),
     "SHIRT": (70, 140, 192), "SHIRT_LIGHT": (130, 186, 226), "SHIRT_DARK": (46, 96, 140),
     "SKIN": (150, 100, 72), "SKIN_LIGHT": (178, 126, 94), "SKIN_SHADOW": (112, 72, 52)},
    {"nombre": "Mateo", "skin": "hombre",
     "HAIR": (150, 92, 50), "HAIR_LIGHT": (194, 134, 80),
     "SHIRT": (208, 92, 64), "SHIRT_LIGHT": (236, 146, 116), "SHIRT_DARK": (150, 60, 44)},
    {"nombre": "Sofía", "skin": "mujer",
     "HAIR": (214, 170, 92), "HAIR_LIGHT": (240, 210, 140),
     "SHIRT": (96, 168, 110), "SHIRT_LIGHT": (150, 206, 158), "SHIRT_DARK": (62, 120, 76)},
    {"nombre": "Don Beto", "skin": "hombre",
     "HAIR": (36, 30, 30), "HAIR_LIGHT": (74, 62, 60),
     "SHIRT": (64, 84, 140), "SHIRT_LIGHT": (110, 132, 186), "SHIRT_DARK": (42, 56, 100),
     "SKIN": (120, 80, 58), "SKIN_LIGHT": (148, 104, 78), "SKIN_SHADOW": (90, 58, 42)},
]


# ---------------------------------------------------------
# CLIENTES FRECUENTES: vienen una vez al día, siempre por lo mismo, y cada uno
# sigue una regla que dice en voz alta ("cada día compro el doble que el día
# anterior"). Algunos días dicen la cantidad; otros solo dicen lo que
# compraron ayer y el niño la deduce. Cada 7 días empiezan de nuevo.
# Máximo 8 productos (lo que cabe en el carrito).
# ---------------------------------------------------------
TOPE_FRECUENTE = 8
DIAS_POR_SEMANA = 7

# Reglas: dado lo que compró ayer, cuánto compra hoy.
REGLAS = {
    "mas1": lambda n: n + 1,
    "menos1": lambda n: n - 1,
    "doble": lambda n: n * 2,
    "mitad": lambda n: n // 2 if n % 2 == 0 else 0,
    "alterna": lambda n: 2 if n == 1 else 1,
}

FRECUENTES = [
    {"nombre": "Payaso Pepín", "skin": "hombre", "disfraz": "payaso",
     "HAIR": (230, 70, 50), "HAIR_LIGHT": (250, 140, 60),
     "SHIRT": (90, 170, 230), "SHIRT_LIGHT": (150, 206, 246), "SHIRT_DARK": (56, 120, 180),
     "producto": "banano", "regla": "mas1", "inicio": 1,
     "regla_texto": "cada día compro un banano más"},
    {"nombre": "Bombera Ana", "skin": "mujer", "disfraz": "bombera",
     "HAIR": (60, 36, 30), "HAIR_LIGHT": (100, 64, 50),
     "SHIRT": (186, 140, 60), "SHIRT_LIGHT": (216, 176, 96), "SHIRT_DARK": (136, 100, 40),
     "SKIN": (176, 120, 86), "SKIN_LIGHT": (204, 148, 110), "SKIN_SHADOW": (134, 88, 62),
     "producto": "agua", "regla": "doble", "inicio": 1,
     "regla_texto": "cada día compro el doble de aguas"},
    {"nombre": "Chef Tito", "skin": "hombre", "disfraz": "chef",
     "HAIR": (70, 50, 40), "HAIR_LIGHT": (110, 84, 64),
     "SHIRT": (240, 240, 234), "SHIRT_LIGHT": (255, 255, 250), "SHIRT_DARK": (196, 196, 190),
     "producto": "huevos", "regla": "mitad", "inicio": 8,
     "regla_texto": "cada día compro la mitad de huevos"},
    {"nombre": "Astronauta Leo", "skin": "hombre", "disfraz": "astronauta",
     "HAIR": (40, 30, 28), "HAIR_LIGHT": (80, 60, 50),
     "SHIRT": (232, 234, 240), "SHIRT_LIGHT": (250, 250, 255), "SHIRT_DARK": (180, 186, 200),
     "SKIN": (150, 100, 72), "SKIN_LIGHT": (178, 126, 94), "SKIN_SHADOW": (112, 72, 52),
     "producto": "leche", "regla": "alterna", "inicio": 1,
     "regla_texto": "un día compro 1 leche y al otro día 2"},
    {"nombre": "Capitana Perla", "skin": "mujer", "disfraz": "pirata",
     "HAIR": (36, 28, 26), "HAIR_LIGHT": (74, 56, 48),
     "SHIRT": (236, 232, 222), "SHIRT_LIGHT": (250, 248, 240), "SHIRT_DARK": (196, 190, 180),
     "producto": "naranja", "regla": "menos1", "inicio": 7,
     "regla_texto": "cada día compro una naranja menos"},
]

# Qué tan seguido dice la cantidad, da la regla con lo de ayer, o se le olvida.
PESOS_DIA = {"dice": 3, "regla_ayer": 4, "olvido": 3}


def sucesion(datos):
    """Las 7 cantidades de la semana. Si la regla se sale de 1..8, reinicia."""
    regla = REGLAS[datos["regla"]]
    valores = [datos["inicio"]]
    for _ in range(DIAS_POR_SEMANA - 1):
        siguiente = regla(valores[-1])
        if not 1 <= siguiente <= TOPE_FRECUENTE:
            siguiente = datos["inicio"]
        valores.append(siguiente)
    return valores


def reinicia(datos, indice):
    """True si ese día no sigue la regla (empieza otra vez)."""
    if indice == 0:
        return False
    valores = sucesion(datos)
    return valores[indice] != REGLAS[datos["regla"]](valores[indice - 1])


def cantidad_frecuente(datos, indice):
    return sucesion(datos)[indice]


def tipos_semana(datos, semana):
    """Cómo pide cada día de esa semana: presenta, dice, regla_ayer, olvido o
    reinicio. El primer día nunca se le olvida; algún otro día sí (al menos
    uno), y cambia de semana en semana."""
    rng = random.Random(f"{datos['nombre']}-{semana}")
    tipos = ["presenta"]
    for i in range(1, DIAS_POR_SEMANA):
        if reinicia(datos, i):
            tipos.append("reinicio")
        else:
            tipos.append(rng.choices(list(PESOS_DIA), weights=list(PESOS_DIA.values()))[0])
    if "olvido" not in tipos:
        posibles = [i for i, t in enumerate(tipos) if t not in ("presenta", "reinicio")]
        tipos[rng.choice(posibles)] = "olvido"
    return tipos


def _nombre_producto(kind, cantidad):
    return (PRODUCTOS[kind][0] if cantidad == 1 else PRODUCTOS[kind][1]).lower()


# ---------------------------------------------------------
# DIÁLOGOS CORTOS: saludo + "me regala" / "me das" / "quiero" + la orden.
# Los productos no se nombran: en el globo salen como "2x" + su dibujo.
# En el texto se escriben como fichas "[2:banano]".
# ---------------------------------------------------------
SALUDOS = ("¡Hola!", "¡Buenas!", "¡Hola, buenas!", "¡Buen día!")


def ficha(kind, cantidad):
    return f"[{cantidad}:{kind}]"


def saludo():
    return random.choice(SALUDOS)


def pedir(orden):
    """'¿Me regala ...?', '¿Me das ...?' o 'Quiero ...'."""
    forma = random.randrange(3)
    if forma == 0:
        return f"¿Me regala {orden}?"
    if forma == 1:
        return f"¿Me das {orden}?"
    return f"Quiero {orden}."


def _regla(datos):
    r = datos["regla_texto"]
    return r[0].upper() + r[1:]


def texto_frecuente(datos, dia):
    """Lo que dice el cliente frecuente ese día (dia empieza en 1)."""
    indice = (dia - 1) % DIAS_POR_SEMANA
    semana = (dia - 1) // DIAS_POR_SEMANA
    tipo = tipos_semana(datos, semana)[indice]
    kind = datos["producto"]
    hoy = cantidad_frecuente(datos, indice)
    if not MODO["sucesiones"]:
        # Sin sucesiones: siguen viniendo, pero dicen directo cuánto quieren.
        return f"{saludo()} {pedir(ficha(kind, hoy))}"
    if indice:
        ayer = cantidad_frecuente(datos, indice - 1)
    if tipo == "presenta":
        if semana == 0:
            return f"¡Hola! {_regla(datos)}. Hoy quiero {ficha(kind, hoy)}."
        return f"¡Semana nueva! {_regla(datos)}. Hoy quiero {ficha(kind, hoy)}."
    if tipo == "reinicio":
        if datos["regla"] == "mitad":
            motivo = f"{ayer} no se parte a la mitad."
        else:
            motivo = f"{TOPE_FRECUENTE} es lo máximo."
        return f"¡Hola! {motivo} Empiezo otra vez: quiero {ficha(kind, hoy)}."
    if tipo == "dice":
        return f"¡Hola! {_regla(datos)}. Hoy quiero {ficha(kind, hoy)}."
    if tipo == "regla_ayer":
        return f"¡Hola! {_regla(datos)}. Ayer compré {ficha(kind, ayer)}."
    # olvido: no se acuerda; el niño recuerda la regla y deduce.
    return f"¡Hola! No me acuerdo cuánto quiero hoy. Ayer compré {ficha(kind, ayer)}."


def crear_persona(datos):
    persona = Player(skin=datos["skin"])
    for clave, valor in datos.items():
        if clave.isupper():
            setattr(persona, clave, valor)
    # Los clientes no usan delantal: se pinta del color de la camisa.
    persona.APRON = persona.SHIRT
    persona.APRON_LIGHT = persona.SHIRT_LIGHT
    persona.APRON_DARK = persona.SHIRT_DARK
    persona.frames = persona._build_frames()
    if datos.get("disfraz"):
        disfraces.aplicar(persona, datos["disfraz"])
    return persona


# ---------------------------------------------------------
# PISTAS (nivel avanzado): color de cada producto en su categoría
# ---------------------------------------------------------
CATEGORIA = {}
for _k in FRUTAS:
    CATEGORIA[_k] = ("fruta", "frutas")
for _k in VERDURAS:
    CATEGORIA[_k] = ("verdura", "verduras")
for _k in BEBIDAS:
    CATEGORIA[_k] = ("bebida", "bebidas")

COLOR = {
    "manzana": "roja", "banano": "amarilla", "naranja": "anaranjada", "uvas": "morada",
    "zanahoria": "anaranjada", "tomate": "roja", "brocoli": "verde", "elote": "amarilla",
    "cola": "café", "naranjada": "anaranjada", "limonada": "amarilla",
    "agua": "celeste", "fresa": "rosada",
}


def _plural_color(color):
    return color + "s"


def _lista(partes, conector="y"):
    if len(partes) == 1:
        return partes[0]
    return ", ".join(partes[:-1]) + f" {conector} " + partes[-1]


def frase_producto(kind, cantidad, con_pista=False):
    """'2 bananos' o, con pista, '2 frutas que no son rojas, ni moradas...'."""
    if not con_pista or kind not in COLOR:
        nombre = PRODUCTOS[kind][0].lower() if cantidad == 1 else PRODUCTOS[kind][1].lower()
        return f"{cantidad} {nombre}"

    singular, plural = CATEGORIA[kind]
    sustantivo = singular if cantidad == 1 else plural
    color = COLOR[kind]
    hermanos = [k for k in COLOR if CATEGORIA.get(k) == CATEGORIA[kind] and k != kind]
    otros = [COLOR[k] for k in hermanos if COLOR[k] != color]
    if random.random() < 0.5 or not otros:
        # Pista directa: "1 bebida verde".
        c = color if cantidad == 1 else _plural_color(color)
        return f"{cantidad} {sustantivo} {c}"
    # Pista por descarte: "2 frutas que no son rojas, ni amarillas, ni moradas".
    if cantidad > 1:
        otros = [_plural_color(c) for c in otros]
    verbo = "es" if cantidad == 1 else "son"
    return f"{cantidad} {sustantivo} que no {verbo} " + ", ni ".join(otros)


def generar_pedido(nivel, disponibles):
    """Elige productos que existan en la tienda o la bodega."""
    minimo, maximo = nivel["pedido_productos"]
    u_min, u_max = nivel.get("pedido_unidades", (1, 2))
    candidatos = [k for k in PRODUCTOS if disponibles.get(k, 0) >= u_min]
    random.shuffle(candidatos)
    n = min(random.randint(minimo, maximo), len(candidatos))
    pedido = {}
    for kind in candidatos[:n]:
        pedido[kind] = random.randint(u_min, min(u_max, disponibles[kind]))
    return pedido


# Cuántas veces más probable es pedir una fracción que una receta entera o doble.
PESO_FRACCION = 4


def generar_pedido_receta(nivel, disponibles, siempre=False, solo_fracciones=False):
    """Pedido de una receta ("medio queque"). Devuelve (pedido, (clave, factor))
    o (None, None) si no toca o no hay ingredientes. siempre=True: pide
    receta aunque no le toque por probabilidad."""
    if not siempre and random.random() >= nivel.get("receta_probabilidad", 0):
        return None, None
    permitidos = factores_permitidos(nivel.get("fracciones_receta", []))
    if solo_fracciones:
        # Después de que el pulpero dice la receta: medio, tercio o cuarto.
        permitidos = [f for f in permitidos if f in ("medio", "tercio", "cuarto")]
    if not permitidos:
        return None, None   # el modo de juego apagó fracciones y multiplicación
    opciones = recetas.combinaciones_validas(permitidos, disponibles)
    if not opciones:
        return None, None
    # Las recetas fraccionadas (tercio, mitad) salen más seguido.
    pesos = [PESO_FRACCION if factor in ("tercio", "medio", "cuarto") else 1 for _, factor, _ in opciones]
    clave, factor, pedido = random.choices(opciones, weights=pesos)[0]
    return pedido, (clave, factor)


def texto_receta(clave, factor):
    return f"{saludo()} ¿Me das los ingredientes para {recetas.frase_pedido(clave, factor)}?"


# Recetas con conversación: el cliente no sabe la receta y el pulpero le
# dice qué lleva; después pide la fracción. Los que SÍ la saben, piden directo.
PROB_CONVERSACION = 0.5
SEGUNDOS_PASO = 4.0


def saludo_hora(hora):
    if hora is None or hora < 12:
        return "¡Buenos días"
    if hora < 18.5:
        return "¡Buenas tardes"
    return "¡Buenas noches"


def _ingredientes_fichas(clave):
    partes = [ficha(k, q) for k, q in recetas.RECETAS[clave]["ingredientes"]]
    return partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " y " + partes[-1]


def conversacion_receta(clave, factor, hora):
    """[(quién, texto, segundos)]: cliente, pulpero y cliente otra vez.
    "{nombre}" se cambia por el nombre del jugador al dibujar."""
    nombre_receta = recetas.RECETAS[clave]["nombre"].lower()
    n = len(recetas.RECETAS[clave]["ingredientes"])
    return [
        ("cliente", f"{saludo_hora(hora)}, {{nombre}}! Quiero hacer {nombre_receta}. "
                    "¿Me puedes ayudar?", SEGUNDOS_PASO),
        ("pulpero", f"¡Claro que sí! Una receta lleva {_ingredientes_fichas(clave)}.",
         SEGUNDOS_PASO + 1.0 * max(0, n - 2) + 1.0),
        ("cliente", f"¡Perfecto! Quiero {recetas.frase_pedido(clave, factor)}.", None),
    ]


def texto_receta_directo(clave, factor, hora):
    """El cliente que ya sabe la receta pide la fracción de una vez."""
    return (f"{saludo_hora(hora)}, {{nombre}}! Ya sé la receta: "
            f"quiero {recetas.frase_pedido(clave, factor)}.")


def texto_pedido(pedido, con_pistas=False):
    tipos = list(pedido)
    pistas = set()
    if con_pistas and tipos:
        # Al menos un producto con pista; los demás, a veces.
        pistas = {k for k in tipos if random.random() < 0.5}
        pistas.add(random.choice(tipos))
    # Con pista (adivinanza de colores) va en palabras; si no, con su dibujo.
    partes = [frase_producto(k, pedido[k], True) if k in pistas else ficha(k, pedido[k])
              for k in tipos]
    return f"{saludo()} {pedir(_lista(partes))}"


# ---------------------------------------------------------
# CLIENTE
# ---------------------------------------------------------
class Cliente:
    def __init__(self, datos, pedido, texto, lugar):
        self.nombre = datos["nombre"]
        self.persona = crear_persona(datos)
        self.persona.x, self.persona.y = PUERTA
        self.persona.direction = "up"
        self.pedido = pedido
        self.texto = texto
        self.lugar = lugar
        self.ruta = [PASILLO, LUGARES[lugar]]
        self.estado = "entrando"   # entrando, esperando, saliendo, fuera
        self.pedido_dicho = False
        self.pedido_restante = None  # segundos que se ve el pedido (None: siempre)
        self.reclamo = None
        self.reclamo_t = 0.0
        self.gracias_t = 0.0
        # Paciencia: baja mientras espera al frente del mostrador.
        self.paciencia_total = None
        self.paciencia = None
        self.aviso_prisa = False
        self.enojo_t = 0.0
        # Para estrellas e insignias más adelante.
        self.repeticiones = 0
        self.errores = 0
        # (clave, factor) si pidió una receta, p. ej. ("queque", "medio")
        self.receta = None
        self.frecuente = False
        self.sin_prisa = False   # el del tutorial: no se apura ni oculta el pedido
        # Conversación (recetas): [(quién, texto, segundos)]; None = pide directo.
        self.conversacion = None
        self.paso = -1           # paso de la conversación que se ve (-1: no empezó)
        self.paso_t = 0.0
        self._visible_final = None

    # Movimiento --------------------------------------------------------
    def ir_a(self, ruta, estado):
        self.ruta = list(ruta)
        self.estado = estado

    def _caminar(self, dt):
        p = self.persona
        if not self.ruta:
            p.frame = 0
            p.animation_time = 0.0
            return True
        tx, ty = self.ruta[0]
        dx, dy = tx - p.x, ty - p.y
        dist = (dx * dx + dy * dy) ** 0.5
        paso = VELOCIDAD * dt
        if dist <= paso:
            p.x, p.y = tx, ty
            self.ruta.pop(0)
        else:
            p.x += dx / dist * paso
            p.y += dy / dist * paso
        if abs(dx) > abs(dy):
            p.direction = "right" if dx > 0 else "left"
        else:
            p.direction = "down" if dy > 0 else "up"
        p.animation_time += dt
        p.frame = int(p.animation_time / p.WALK_FRAME_TIME) % 2
        return False

    def actualizar(self, dt, segundos_visible):
        llego = self._caminar(dt)
        if self.estado == "entrando" and llego:
            self.estado = "esperando"
            # El del frente mira al pulpero; los de la fila, hacia el mostrador.
            self.persona.direction = "down" if self.lugar == 0 else "right"
            # En la fila esperan callados; piden al llegar al frente.
            if not self.pedido_dicho and self.lugar == 0 and self.paso < 0:
                self.decir_pedido(segundos_visible)
        elif self.estado == "saliendo" and llego:
            self.estado = "fuera"

        self._avanzar_conversacion(dt)
        if self.pedido_restante is not None and self.pedido_restante > 0:
            self.pedido_restante = max(0.0, self.pedido_restante - dt)
        if self.reclamo is not None:
            self.reclamo_t -= dt
            if self.reclamo_t <= 0:
                self.reclamo = None
        if self.gracias_t > 0:
            self.gracias_t -= dt
        if self.enojo_t > 0:
            self.enojo_t -= dt

    @property
    def fraccion_paciencia(self):
        if self.paciencia_total is None:
            return 1.0
        return max(0.0, self.paciencia / self.paciencia_total)

    def decir_pedido(self, segundos_visible):
        if self.conversacion and self.paso < 0:
            # Primero conversan; el pedido se "dice" al final.
            self.paso = 0
            self.paso_t = self.conversacion[0][2] or 0.0
            self._visible_final = segundos_visible
            return
        self.pedido_dicho = True
        self.pedido_restante = segundos_visible

    @property
    def en_conversacion(self):
        return self.conversacion is not None and 0 <= self.paso < len(self.conversacion) - 1

    def linea_conversacion(self):
        """(quién, texto) del paso que se ve ahora, o None."""
        if not self.en_conversacion:
            return None
        quien, texto, _ = self.conversacion[self.paso]
        return quien, texto

    def _avanzar_conversacion(self, dt):
        if not self.en_conversacion:
            return
        self.paso_t -= dt
        if self.paso_t <= 0:
            self.paso += 1
            if self.paso >= len(self.conversacion) - 1:
                # Última línea: es el pedido (puede ocultarse, como siempre).
                self.texto = self.conversacion[-1][1]
                self.pedido_dicho = True
                self.pedido_restante = self._visible_final
            else:
                self.paso_t = self.conversacion[self.paso][2] or SEGUNDOS_PASO

    @property
    def pedido_visible(self):
        return self.pedido_dicho and (
            self.pedido_restante is None or self.pedido_restante > 0
        )


# ---------------------------------------------------------
# ADMINISTRADOR DE CLIENTES
# ---------------------------------------------------------
class Clientes:
    def __init__(self, obtener_nivel):
        self.obtener_nivel = obtener_nivel
        self.dia = 1
        self.tutorial = False    # durante el tutorial no llegan otros clientes
        # El juego dice dónde está el mostrador y si alguien lo está moviendo.
        self.obtener_mostrador = lambda: None
        self.mostrador_quieto = lambda: True
        self.jugador = None      # el pulpero (para su globo en las conversaciones)
        # Se activa en OPCIONES. Desactivada: los clientes esperan sin límite.
        self.paciencia_activa = False
        self.reiniciar()

    def reiniciar(self):
        self.lista = []
        self.espera = ESPERA_PRIMER_CLIENTE
        self.atendidos = 0
        self.perdidos = 0
        self.recetas_hoy = 0  # pedidos de receta entregados (MODO HISTORIA)
        self.generados = 0   # clientes que han llegado en esta jornada
        self.cerrada_hoy = False  # ya son las 6:00 p. m.: no llega nadie más
        self.saliendo_de = None  # cliente atendido que todavía no sale
        self.hora = None
        # Partida nueva: el pulpero empieza en la acera; hasta que no entra
        # a la tienda no llega ningún cliente.
        if not hasattr(self, "esperando_jugador"):
            self.esperando_jugador = False
        self.abierta = True  # con la tienda cerrada no entran clientes nuevos
        self._ultimo_personaje = None
        # Orden del día: los 5 frecuentes, cada uno con un cliente normal en
        # medio para que nunca lleguen dos frecuentes seguidos.
        self.frecuentes_hoy = random.sample(FRECUENTES, len(FRECUENTES))
        self.plan = []
        for i in range(len(self.frecuentes_hoy)):
            if i:
                self.plan.append("normal")
            self.plan.append("frecuente")

    @property
    def limite_jornada(self):
        """Ya no hay límite de clientes por día: llegan hasta las 6:00 p. m.
        (el plan solo ordena a los primeros: frecuentes con normales en medio)."""
        return float("inf")

    @property
    def dia_semana(self):
        """0 = primer día de la semana; cada 7 días se reinician las sucesiones."""
        return (self.dia - 1) % DIAS_POR_SEMANA

    # Consultas -----------------------------------------------------------
    @property
    def activos(self):
        return [c for c in self.lista if c.estado in ("entrando", "esperando")]

    def frente(self):
        """Cliente que está (o va) al frente del mostrador."""
        for c in self.activos:
            if c.lugar == 0:
                return c
        return None

    def cliente_esperando(self):
        c = self.frente()
        return c if c is not None and c.estado == "esperando" else None

    # Actualización ------------------------------------------------------
    def actualizar(self, dt, disponibles, pausado=False, hora=None):
        """pausado=True mientras la factura está abierta (el cliente paga).
        hora: la del reloj del juego (antes de las 7:00 no llega nadie)."""
        self.hora = hora
        nivel = self.obtener_nivel()
        for c in self.lista:
            # El cliente del tutorial nunca oculta su pedido.
            oculta = None if (c.sin_prisa or not MODO["memoria"]) else nivel["pedido_oculta_segundos"]
            c.actualizar(dt, oculta)
        self.lista = [c for c in self.lista if c.estado != "fuera"]

        # Paciencia del cliente que espera al frente.
        frente = self.cliente_esperando()
        if (frente is not None and not pausado and self.paciencia_activa and not frente.sin_prisa
                and not frente.en_conversacion):
            if frente.paciencia_total is None:
                frente.paciencia_total = float(nivel.get("paciencia_segundos", 120))
                frente.paciencia = frente.paciencia_total
            frente.paciencia -= dt
            if not frente.aviso_prisa and frente.fraccion_paciencia <= AVISO_PRISA:
                frente.aviso_prisa = True
                self._reclamar(frente, "¡Apúrate, por favor! Tengo prisa.")
            if frente.paciencia <= 0:
                self._irse_enojado(frente)

        # La fila sigue al mostrador (si lo movieron, caminan a su nuevo frente).
        self._seguir_mostrador()
        # Si alguien de adelante se fue, la fila avanza un lugar.
        self._avanzar_fila()

        # El siguiente entra cuando el atendido ya salió por completo.
        if self.saliendo_de is not None:
            if self.saliendo_de in self.lista:
                return
            self.saliendo_de = None
            self.espera = self.espera_al_azar()

        fila = nivel.get("clientes_en_fila", 1)
        temprano = (hora is not None and hora < HORA_PRIMER_CLIENTE) or self.esperando_jugador
        tarde = self.cerrada_hoy or (hora is not None and hora >= HORA_CIERRE_TIENDA)
        if (self.abierta and not self.tutorial and len(self.activos) < fila
                and not temprano and not tarde):
            self.espera -= dt
            if self.espera <= 0:
                self._nuevo_cliente(nivel, disponibles())
                self.espera = self.espera_al_azar()

    def segundos_por_minuto(self):
        """Segundos reales que dura un minuto del reloj del juego."""
        minutos_dia = (HORA_FIN - HORA_INICIO) * 60
        return DURACION_DIA / minutos_dia

    def espera_al_azar(self):
        return random.uniform(*MINUTOS_ENTRE_CLIENTES) * self.segundos_por_minuto()

    def _seguir_mostrador(self):
        mostrador = self.obtener_mostrador()
        if mostrador is None or not self.mostrador_quieto():
            return
        nuevos = lugares_del_mostrador(mostrador)
        if nuevos == LUGARES:
            return
        LUGARES[:] = nuevos
        for c in self.activos:
            if c.lugar < 0:
                continue
            destino = LUGARES[c.lugar]
            if len(c.ruta) > 1 and c.ruta[0] == PASILLO:
                c.ruta = [PASILLO, destino]       # todavía viene entrando
            else:
                c.ruta = [destino]
            if c.estado == "esperando":
                c.estado = "entrando"

    def _avanzar_fila(self):
        """Los de la fila ocupan los lugares libres de adelante."""
        en_fila = sorted((c for c in self.activos if c.lugar >= 0), key=lambda c: c.lugar)
        for i, c in enumerate(en_fila):
            if c.lugar == i:
                continue
            c.lugar = i
            # Si todavía no llega al pasillo, primero pasa por ahí.
            if len(c.ruta) > 1 and c.ruta[0] == PASILLO:
                c.ruta = [PASILLO, LUGARES[i]]
            else:
                c.ruta = [LUGARES[i]]
            if c.estado == "esperando":
                c.estado = "entrando"

    def _lugar_libre(self):
        ocupados = {c.lugar for c in self.activos}
        return next(i for i in range(len(LUGARES)) if i not in ocupados)

    def _nuevo_cliente(self, nivel, disponibles):
        tipo = self.plan[self.generados] if self.generados < len(self.plan) else "normal"
        disfrazado = None
        if tipo == "frecuente" and self.frecuentes_hoy:
            if MODO["sucesiones"]:
                self._nuevo_frecuente(self.frecuentes_hoy.pop(0))
                return
            # Sin sucesiones: los disfrazados son clientes normales que
            # piden una receta al azar (o productos, si no hay receta).
            disfrazado = self.frecuentes_hoy[0]
        # La mitad de las recetas van con conversación: el cliente no la sabe,
        # el pulpero le dice qué lleva y después pide medio, tercio o cuarto.
        conversa = random.random() < PROB_CONVERSACION
        pedido, receta = generar_pedido_receta(nivel, disponibles, siempre=disfrazado is not None,
                                               solo_fracciones=conversa)
        if conversa and receta is None and disfrazado is not None:
            conversa = False     # sin fracciones posibles: pide directo
            pedido, receta = generar_pedido_receta(nivel, disponibles, siempre=True)
        if not pedido:
            pedido = generar_pedido(nivel, disponibles)
        if not pedido:
            return
        if disfrazado is not None:
            datos = self.frecuentes_hoy.pop(0)
        else:
            opciones = [d for d in PERSONAJES if d["nombre"] != self._ultimo_personaje]
            datos = random.choice(opciones)
        self._ultimo_personaje = datos["nombre"]
        lugar = self._lugar_libre()
        conversacion = None
        if receta and conversa:
            conversacion = conversacion_receta(*receta, self.hora)
            texto = conversacion[-1][1]
        elif receta:
            texto = texto_receta_directo(*receta, self.hora)
        else:
            texto = texto_pedido(pedido, nivel.get("pedido_con_pistas", False) and MODO["descarte"])
        cliente = Cliente(datos, pedido, texto, lugar)
        cliente.receta = receta
        cliente.conversacion = conversacion
        # Adivinanza de colores: algún producto se dijo con pista, no con su dibujo.
        cliente.descarte = (not receta and nivel.get("pedido_con_pistas", False) and MODO["descarte"]
                            and any(ficha(k, q) not in texto for k, q in pedido.items()))
        self.lista.append(cliente)
        self.generados += 1

    def _nuevo_frecuente(self, datos):
        cantidad = cantidad_frecuente(datos, self.dia_semana)
        lugar = self._lugar_libre()
        cliente = Cliente(datos, {datos["producto"]: cantidad},
                          texto_frecuente(datos, self.dia), lugar)
        cliente.frecuente = True
        self.lista.append(cliente)
        self._ultimo_personaje = datos["nombre"]
        self.generados += 1

    def cliente_tutorial(self):
        """El cliente del tutorial: siempre Doña Rosa, siempre 2 manzanas."""
        datos = next(d for d in PERSONAJES if d["nombre"] == "Doña Rosa")
        cliente = Cliente(datos, {"manzana": 2}, "¡Hola! Quiero [2:manzana].", 0)
        cliente.sin_prisa = True
        self.lista.append(cliente)
        return cliente

    def cerrar_por_hora(self):
        """Son las 6:00 p. m.: la tienda cierra aunque haya clientes.

        Los que están adentro se retiran (no cuentan como perdidos) y ya no
        llegan los que faltaban del día. Devuelve cuántos había adentro.
        """
        adentro = list(self.activos)
        self.cerrada_hoy = True
        for c in adentro:
            c.reclamo = None
            c.enojo_t = 0.0
            c.pedido_restante = 0
            c.ir_a([PASILLO, PUERTA], "saliendo")
            c.lugar = -1
        return len(adentro)

    def alternar_tienda(self):
        """Abre o cierra la tienda. Devuelve True si quedó abierta."""
        self.abierta = not self.abierta
        if self.abierta:
            self.espera = min(self.espera, ESPERA_PRIMER_CLIENTE)
        return self.abierta

    def jornada_terminada(self):
        """Ya cerró la tienda (6:00 p. m.) y ningún cliente sigue adentro."""
        return self.cerrada_hoy and not self.lista

    # Acciones del jugador ------------------------------------------------
    def repetir(self):
        """Tecla P: el cliente del frente repite su pedido (solo una vez)."""
        c = self.cliente_esperando()
        if c is None or c.pedido_visible:
            return False
        if c.repeticiones >= self.obtener_nivel().get("repeticiones_maximas", 2):
            # Ya lo repitió las veces permitidas: a la siguiente se retira.
            self._irse_enojado(c)
            return False
        c.repeticiones += 1
        c.reclamo = None
        c.decir_pedido(self.obtener_nivel()["pedido_oculta_segundos"] if MODO["memoria"] else None)
        return True

    def revisar(self, resumen):
        """Compara el mostrador con el pedido. Devuelve (ok, motivo).

        ok=None si no hay cliente esperando.
        """
        c = self.cliente_esperando()
        if c is None:
            return None, None
        mostrador = {g["kind"]: g["quantity"] for g in resumen["groups"]}
        if not mostrador:
            return False, self._reclamar(c, "¡El mostrador está vacío!")
        faltan = {k: q - mostrador.get(k, 0) for k, q in c.pedido.items()
                  if mostrador.get(k, 0) < q}
        sobran = {k: q - c.pedido.get(k, 0) for k, q in mostrador.items()
                  if q > c.pedido.get(k, 0)}
        if not faltan and not sobran:
            if not getattr(c, "contado_ok", False):
                c.contado_ok = True
                self._estadistica(c, True)
            return True, None

        c.errores += 1
        self._estadistica(c, False)
        if c.receta and not self.obtener_nivel().get("reclamo_detallado", True):
            frase = recetas.frase_pedido(*c.receta)
            return False, self._reclamar(
                c, f"Mmm... con esto no me sale {frase}. ¡Revisa el recetario!")
        if not self.obtener_nivel().get("reclamo_detallado", True):
            # Avanzado: solo una pista general, el niño debe recordar.
            partes = []
            if faltan:
                partes.append("me falta algo")
            if sobran:
                partes.append("hay algo que no pedí")
            return False, self._reclamar(
                c, "Mmm... " + " y ".join(partes) + ". ¡Revisa mi pedido!")

        frases = []
        for k, q in faltan.items():
            nombre = PRODUCTOS[k][0].lower() if q == 1 else PRODUCTOS[k][1].lower()
            frases.append(f"me falta{'n' if q > 1 else ''} {q} {nombre}")
        for k, q in sobran.items():
            if k not in c.pedido:
                frases.append(f"yo no pedí {PRODUCTOS[k][1].lower()}")
            else:
                nombre = PRODUCTOS[k][0].lower() if q == 1 else PRODUCTOS[k][1].lower()
                frases.append(f"sobra{'n' if q > 1 else ''} {q} {nombre}")
        texto = _lista(frases[:2])
        return False, self._reclamar(c, "¡Ups! " + texto[0].upper() + texto[1:] + ".")

    def _reclamar(self, cliente, texto):
        cliente.reclamo = texto
        cliente.reclamo_t = SEGUNDOS_RECLAMO
        return texto

    def _estadistica(self, c, acierto):
        """Para el REPORTE: qué habilidades usó el niño con este pedido."""
        if self.tutorial or c.sin_prisa:
            return
        claves = []
        if c.receta:
            factor = c.receta[1]
            claves.append("fracciones" if factor in ("medio", "tercio", "cuarto") else "multiplicar")
        if c.frecuente and MODO["sucesiones"]:
            claves.append("sucesiones")
        if getattr(c, "descarte", False):
            claves.append("descarte")
        if MODO["memoria"] and c.pedido_dicho and not c.pedido_visible:
            claves.append("memoria")
        for clave in claves:
            estadisticas.registrar(clave, acierto)

    def _irse_enojado(self, c):
        """El cliente se retira sin comprar (y sin decir nada)."""
        if self.paciencia_activa and not self.tutorial:
            estadisticas.registrar("paciencia", False)
        c.reclamo = None
        c.enojo_t = 0.0
        c.pedido_restante = 0
        c.ir_a([PASILLO, PUERTA], "saliendo")
        c.lugar = -1
        self.perdidos += 1
        self.saliendo_de = c       # el siguiente entra cuando este ya salió

    def puede_repetir(self):
        c = self.cliente_esperando()
        return (c is not None and not c.pedido_visible and
                c.repeticiones < self.obtener_nivel().get("repeticiones_maximas", 2))

    def venta_cobrada(self):
        """El cliente del frente recibió su pedido: se va contento."""
        c = self.cliente_esperando()
        if c is None:
            return None
        c.gracias_t = SEGUNDOS_GRACIAS
        c.pedido_restante = 0
        c.ir_a([PASILLO, PUERTA], "saliendo")
        c.lugar = -1
        self.atendidos += 1
        if self.paciencia_activa and not self.tutorial and not c.sin_prisa:
            estadisticas.registrar("paciencia", True)
        if c.receta:
            self.recetas_hoy += 1
        self.saliendo_de = c       # el siguiente entra cuando este ya salió
        return c

    # Dibujo ------------------------------------------------------------
    def dibujar(self, surface):
        for c in sorted(self.lista, key=lambda c: c.persona.y):
            c.persona.draw(surface)
            if (self.paciencia_activa and c.estado == "esperando"
                    and c.paciencia_total is not None):
                _barra_paciencia(surface, c)

    def dibujar_burbujas(self, surface, font, nombre_jugador=""):
        ocupado = []
        # Primero el del frente para que su globo quede más abajo.
        for c in sorted(self.lista, key=lambda c: c.lugar if c.lugar >= 0 else 9):
            texto, color_titulo = None, (48, 67, 78)
            if c.enojo_t > 0:
                texto = "¡Me cansé de esperar! Me voy."
                color_titulo = (176, 48, 42)
            elif c.gracias_t > 0:
                texto = f"¡Gracias, {nombre_jugador}!" if nombre_jugador else "¡Gracias!"
                color_titulo = (66, 115, 67)
            elif c.estado != "esperando" or c.lugar > 0:
                continue          # en la fila esperan sin globo
            elif c.reclamo:
                texto = c.reclamo
                color_titulo = (155, 62, 52)
            elif c.linea_conversacion() is not None:
                quien, texto = c.linea_conversacion()
                texto = texto.replace("{nombre}", nombre_jugador or "")
                if quien == "pulpero" and self.jugador is not None:
                    # Habla el pulpero: el globo va sobre su cabeza.
                    habla = _Hablante(self.jugador, nombre_jugador or "Tú")
                    ocupado.append(_burbuja(surface, font, habla, texto, (48, 67, 78), ocupado))
                    continue
            elif c.pedido_visible:
                texto = c.texto
            else:
                texto = "..."
            texto = texto.replace("{nombre}", nombre_jugador or "")
            rect = _burbuja(surface, font, c, texto, color_titulo, ocupado,
                            sobre_barra=self.paciencia_activa)
            ocupado.append(rect)


class _Hablante:
    """Para dibujar el globo del pulpero con la misma función de los clientes."""
    def __init__(self, persona, nombre):
        self.persona = persona
        self.nombre = nombre


def _barra_paciencia(surface, cliente):
    """Barrita sobre la cabeza: verde, amarilla y roja según la paciencia."""
    p = cliente.persona
    f = cliente.fraccion_paciencia
    ancho, alto = 30, 4
    x = round(p.x) - ancho // 2
    y = round(p.y) - p.HEIGHT - 5
    color = (92, 176, 76) if f > 0.5 else (236, 190, 60) if f > AVISO_PRISA else (214, 64, 52)
    # Parpadea cuando queda poco.
    if f <= AVISO_PRISA and (pygame.time.get_ticks() // 250) % 2:
        color = (255, 120, 100)
    pygame.draw.rect(surface, (35, 27, 27), (x - 1, y - 1, ancho + 2, alto + 2))
    pygame.draw.rect(surface, (90, 70, 60), (x, y, ancho, alto))
    pygame.draw.rect(surface, color, (x, y, round(ancho * f), alto))


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


# "[2:banano]" (con signos pegados, p. ej. "[2:banano]?" o "[1:huevos],")
FICHA = re.compile(r"^([¿¡]?)\[(\d+):(\w+)\]([.,;:!?]*)$")


_ICONOS = {}


def _icono(kind):
    """El dibujo del producto, agrandado (sin borronear) para que se reconozca."""
    if kind not in _ICONOS:
        w, h = tamano(kind)
        base = pygame.Surface((w, h), pygame.SRCALPHA)
        dibujar_producto(base, kind, 0, 0)
        grande = pygame.transform.scale(base, (w * 2, h * 2))
        # Borde oscuro: así el huevo blanco o la leche se ven sobre el globo crema.
        silueta = pygame.mask.from_surface(grande).to_surface(
            setcolor=(*CAFE, 255), unsetcolor=(0, 0, 0, 0))
        icono = pygame.Surface((w * 2 + 2, h * 2 + 2), pygame.SRCALPHA)
        for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
            icono.blit(silueta, (dx, dy))
        icono.blit(grande, (1, 1))
        _ICONOS[kind] = icono
    return _ICONOS[kind]


def _palabra(font, palabra, color):
    """Una palabra del globo; las fichas salen como '2x' + el dibujo."""
    m = FICHA.match(palabra)
    if not m or m.group(3) not in PRODUCTOS:
        return font.render(palabra, False, color)
    antes, n, kind, despues = m.groups()
    numero = font.render(f"{antes}{n}x", False, color)
    cola = font.render(despues, False, color) if despues else None
    icono = _icono(kind)
    w, h = icono.get_size()
    alto = max(font.get_height(), h + 2)
    ancho = numero.get_width() + 1 + w + (cola.get_width() if cola else 0)
    s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    s.blit(numero, (0, alto - numero.get_height()))
    s.blit(icono, (numero.get_width() + 1, (alto - h) // 2 + 1))
    if cola:
        s.blit(cola, (ancho - cola.get_width(), alto - cola.get_height()))
    return s


def _renglones(font, texto, ancho, color):
    """Parte el texto en renglones (con fichas dibujadas) de hasta 'ancho'."""
    espacio = font.size(" ")[0]
    renglones, actual, w = [], [], 0
    for palabra in texto.split():
        s = _palabra(font, palabra, color)
        nuevo = w + (espacio if actual else 0) + s.get_width()
        if actual and nuevo > ancho:
            renglones.append(actual)
            actual, nuevo = [], s.get_width()
        actual.append(s)
        w = nuevo
    if actual:
        renglones.append(actual)
    superficies = []
    for piezas in renglones:
        alto = max(font.get_height(), max(p.get_height() for p in piezas))
        ancho_r = sum(p.get_width() for p in piezas) + espacio * (len(piezas) - 1)
        r = pygame.Surface((ancho_r, alto), pygame.SRCALPHA)
        x = 0
        for p in piezas:
            r.blit(p, (x, alto - p.get_height()))
            x += p.get_width() + espacio
        superficies.append(r)
    return superficies


CREMA = (245, 226, 177)
CAFE = (84, 50, 39)


def _burbuja(surface, font, cliente, texto, color_titulo, ocupado, sobre_barra=False):
    p = cliente.persona
    corto = texto == "..."
    titulo = font.render(cliente.nombre + (":" if not corto else ""), False, color_titulo)
    cuerpos = [] if corto else _renglones(font, texto, 210, CAFE)
    if corto:
        cuerpos = [font.render("...", False, CAFE)]
        titulo = None
    alto_linea = font.get_height()
    w = max([s.get_width() for s in cuerpos] + ([titulo.get_width()] if titulo else [])) + 14
    h = sum(s.get_height() for s in cuerpos) + (alto_linea if titulo else 0) + 10
    # Con la paciencia activada, el globo sube para dejar ver la barra.
    bottom = round(p.y) - p.HEIGHT - (14 if sobre_barra else 6)
    x = max(4, min(640 - w - 4, round(p.x) - w // 2))
    caja = pygame.Rect(x, bottom - h, w, h)
    # Si choca con otro globo, subirlo encima.
    for otro in ocupado:
        if caja.colliderect(otro.inflate(4, 4)):
            caja.bottom = otro.top - 6
    if caja.top < 2:
        # No cabe arriba: se pone a un lado del otro globo.
        caja.bottom = bottom
        for otro in ocupado:
            if caja.colliderect(otro.inflate(4, 4)):
                if otro.right + 6 + w <= 636:
                    caja.left = otro.right + 6
                elif otro.left - 6 - w >= 4:
                    caja.right = otro.left - 6
                else:
                    caja.bottom = max(h + 2, otro.top - 6)
    caja.top = max(2, caja.top)

    cola_x = max(caja.left + 8, min(caja.right - 8, round(p.x)))
    pygame.draw.rect(surface, (35, 27, 27), caja.move(2, 2))
    if caja.bottom >= bottom - 2:
        pygame.draw.polygon(surface, CAFE, [(cola_x - 5, caja.bottom - 1),
                                            (cola_x + 5, caja.bottom - 1),
                                            (cola_x, caja.bottom + 6)])
    pygame.draw.rect(surface, CREMA, caja)
    pygame.draw.rect(surface, CAFE, caja, 2)
    if caja.bottom >= bottom - 2:
        pygame.draw.polygon(surface, CREMA, [(cola_x - 3, caja.bottom - 2),
                                             (cola_x + 3, caja.bottom - 2),
                                             (cola_x, caja.bottom + 3)])
    y = caja.y + 5
    if titulo:
        surface.blit(titulo, (caja.x + 7, y))
        y += alto_linea
    for s in cuerpos:
        surface.blit(s, (caja.x + 7, y))
        y += s.get_height()
    return caja
