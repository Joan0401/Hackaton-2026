"""ARMARIO: ropa y accesorios que se compran con el saldo de la pulpería.

Para el pulpero o la pulpera: sombreros, lentes, algo para el cuello,
camisas y delantales. Para Canela, la gata: pelaje, collares y gorros.
Para Bruno, el perro: pelaje, collares y trajes (¡de dinosaurio!).
Hay estilos NORMAL (baratos), LLAMATIVO y DE LUJO (caros: hay que ahorrar
varios días). De cada grupo se usa uno a la vez. Se compra una vez y
después se pone o se quita gratis.
"""
import pygame

NORMAL, LLAMATIVO, LUJO = "NORMAL", "LLAMATIVO", "DE LUJO"

# (quién, nombre en pantalla, grupo)
CATEGORIAS = [
    ("PULPERO", "SOMBREROS", "sombrero"),
    ("PULPERO", "LENTES", "lentes"),
    ("PULPERO", "CUELLO", "cuello"),
    ("PULPERO", "CAMISAS", "camisa"),
    ("PULPERO", "DELANTALES", "delantal"),
    ("GATO", "PELAJE", "pelaje"),
    ("GATO", "COLLARES", "collar"),
    ("GATO", "GORROS", "sombrero_gato"),
    ("PERRO", "TRAJES", "traje_perro"),
    ("PERRO", "PELAJE", "pelaje_perro"),
    ("PERRO", "COLLARES", "collar_perro"),
]

# (clave, grupo, nombre, precio, valor, estilo)
ARTICULOS = [
    # Sombreros
    ("gorra_roja", "sombrero", "Gorra roja", 40, ("gorra", (210, 60, 56)), NORMAL),
    ("gorra_azul", "sombrero", "Gorra azul", 40, ("gorra", (60, 100, 200)), NORMAL),
    ("lana", "sombrero", "Gorro de lana", 60, ("lana", (90, 160, 110)), NORMAL),
    ("paja", "sombrero", "Sombrero de paja", 70, ("paja", None), NORMAL),
    ("boina", "sombrero", "Boina de pintor", 90, ("boina", (150, 60, 140)), LLAMATIVO),
    ("chef", "sombrero", "Gorro de chef", 110, ("chef", None), LLAMATIVO),
    ("vaquero", "sombrero", "Sombrero vaquero", 150, ("vaquero", (150, 96, 54)), LLAMATIVO),
    ("copa", "sombrero", "Sombrero de copa", 220, ("copa", (36, 34, 40)), LUJO),
    ("corona", "sombrero", "Corona de rey", 400, ("corona", None), LUJO),
    # Lentes
    ("redondos", "lentes", "Lentes redondos", 50, "redondos", NORMAL),
    ("cuadrados", "lentes", "Lentes cuadrados", 60, "cuadrados", NORMAL),
    ("sol", "lentes", "Lentes de sol", 80, "sol", NORMAL),
    ("estrella", "lentes", "Lentes de estrella", 140, "estrella", LLAMATIVO),
    ("corazon", "lentes", "Lentes de corazón", 140, "corazon", LLAMATIVO),
    ("monoculo", "lentes", "Monóculo de oro", 260, "monoculo", LUJO),
    # Cuello
    ("corbatin", "cuello", "Corbatín rojo", 60, ("corbatin", (200, 50, 50)), NORMAL),
    ("corbata", "cuello", "Corbata azul", 60, ("corbata", (50, 80, 170)), NORMAL),
    ("bufanda", "cuello", "Bufanda verde", 80, ("bufanda", (70, 150, 90)), NORMAL),
    ("flores", "cuello", "Collar de flores", 140, ("flores", None), LLAMATIVO),
    ("medalla", "cuello", "Medalla de oro", 300, ("medalla", None), LUJO),
    # Camisas
    ("camisa_blanca", "camisa", "Camisa blanca", 40, (236, 236, 230), NORMAL),
    ("camisa_azul", "camisa", "Camisa azul", 40, (70, 110, 190), NORMAL),
    ("camisa_roja", "camisa", "Camisa roja", 40, (196, 70, 64), NORMAL),
    ("camisa_negra", "camisa", "Camisa negra", 50, (50, 50, 58), NORMAL),
    ("camisa_lima", "camisa", "Camisa verde lima", 90, (150, 220, 60), LLAMATIVO),
    ("camisa_neon", "camisa", "Camisa rosado neón", 120, (255, 80, 180), LLAMATIVO),
    ("camisa_oro", "camisa", "Camisa dorada", 250, (232, 186, 60), LUJO),
    # Delantales
    ("delantal_blanco", "delantal", "Delantal blanco", 40, (236, 236, 230), NORMAL),
    ("delantal_azul", "delantal", "Delantal azul", 40, (90, 130, 200), NORMAL),
    ("delantal_amarillo", "delantal", "Delantal amarillo", 50, (236, 200, 80), NORMAL),
    ("delantal_turquesa", "delantal", "Delantal turquesa", 90, (60, 200, 190), LLAMATIVO),
    ("delantal_naranja", "delantal", "Delantal naranja neón", 120, (255, 130, 40), LLAMATIVO),
    ("delantal_plata", "delantal", "Delantal plateado", 200, (200, 206, 214), LUJO),
    ("delantal_oro", "delantal", "Delantal dorado", 300, (232, 186, 60), LUJO),
    # Canela: pelaje
    ("pelaje_naranja", "pelaje", "Naranja (el suyo)", 0, (236, 150, 60), NORMAL),
    ("pelaje_gris", "pelaje", "Gris", 60, (130, 130, 138), NORMAL),
    ("pelaje_blanco", "pelaje", "Blanco", 60, (240, 236, 226), NORMAL),
    ("pelaje_negro", "pelaje", "Negro", 70, (60, 54, 56), NORMAL),
    ("pelaje_rosado", "pelaje", "Rosado chicle", 150, (250, 150, 200), LLAMATIVO),
    ("pelaje_azul", "pelaje", "Azul eléctrico", 180, (70, 140, 255), LLAMATIVO),
    ("pelaje_oro", "pelaje", "Dorado brillante", 350, (246, 206, 80), LUJO),
    # Canela: collares
    ("collar_rojo", "collar", "Collar rojo", 30, ((210, 50, 50), None), NORMAL),
    ("collar_azul", "collar", "Collar azul", 30, ((60, 110, 210), None), NORMAL),
    ("collar_verde", "collar", "Collar verde", 30, ((60, 160, 80), None), NORMAL),
    ("cascabel", "collar", "Collar con cascabel", 100, ((200, 50, 50), "cascabel"), LLAMATIVO),
    ("collar_flores", "collar", "Collar de flores", 120, ((250, 150, 200), "flores"), LLAMATIVO),
    ("diamantes", "collar", "Collar de diamantes", 300, ((230, 236, 250), "diamantes"), LUJO),
    # Canela: gorros
    ("moño", "sombrero_gato", "Moño rosado", 50, "moño", NORMAL),
    ("lana_gato", "sombrero_gato", "Gorrito de lana", 70, "lana", NORMAL),
    ("fiesta", "sombrero_gato", "Gorrito de fiesta", 80, "fiesta", LLAMATIVO),
    ("bruja", "sombrero_gato", "Sombrero de bruja", 120, "bruja", LLAMATIVO),
    ("corona_gato", "sombrero_gato", "Corona", 350, "corona", LUJO),
    # Bruno: trajes
    ("sueter", "traje_perro", "Suéter rojo", 60, "suéter", NORMAL),
    ("impermeable", "traje_perro", "Impermeable amarillo", 70, "impermeable", NORMAL),
    ("dino_verde", "traje_perro", "Dinosaurio verde", 150, "dino_verde", LLAMATIVO),
    ("dino_morado", "traje_perro", "Dinosaurio morado", 180, "dino_morado", LLAMATIVO),
    ("abeja", "traje_perro", "Abejita", 140, "abeja", LLAMATIVO),
    ("tiburon", "traje_perro", "Tiburón", 200, "tiburon", LUJO),
    ("superheroe", "traje_perro", "Superhéroe", 240, "superheroe", LUJO),
    ("unicornio", "traje_perro", "Unicornio", 350, "unicornio", LUJO),
    # Bruno: pelaje
    ("perro_cafe", "pelaje_perro", "Café (el suyo)", 0, (176, 120, 70), NORMAL),
    ("perro_negro", "pelaje_perro", "Negro", 60, (64, 56, 54), NORMAL),
    ("perro_blanco", "pelaje_perro", "Blanco", 60, (236, 232, 222), NORMAL),
    ("perro_gris", "pelaje_perro", "Gris", 60, (140, 140, 146), NORMAL),
    ("perro_oro", "pelaje_perro", "Dorado", 300, (240, 196, 90), LUJO),
    # Bruno: collares
    ("perro_rojo", "collar_perro", "Collar rojo", 30, ((210, 50, 50), None), NORMAL),
    ("perro_azul", "collar_perro", "Collar azul", 30, ((60, 110, 210), None), NORMAL),
    ("perro_hueso", "collar_perro", "Collar con huesito", 60, ((60, 150, 80), "hueso"), NORMAL),
    ("panoleta", "collar_perro", "Pañoleta roja", 100, ((210, 50, 50), "pañoleta"), LLAMATIVO),
    ("picos", "collar_perro", "Collar de picos", 110, ((40, 40, 46), "picos"), LLAMATIVO),
    ("perro_dorado", "collar_perro", "Collar dorado", 250, ((240, 196, 60), None), LUJO),
]

# Más colores para todo (se agregan a cada grupo; la lista se ordena por precio).
_C = {
    "roja": (210, 60, 56), "rojo": (200, 56, 52), "azul": (60, 100, 200),
    "celeste": (120, 186, 236), "verde": (70, 150, 90), "amarilla": (236, 200, 70),
    "amarillo": (236, 200, 70), "naranja": (240, 140, 50), "rosada": (240, 140, 180),
    "rosado": (240, 140, 180), "morada": (140, 80, 180), "morado": (140, 80, 180),
    "negra": (46, 44, 52), "negro": (46, 44, 52), "blanca": (236, 236, 230),
    "blanco": (236, 236, 230), "cafe": (130, 86, 52), "turquesa": (50, 190, 180),
    "gris": (130, 130, 138), "crema": (238, 218, 176), "vino": (130, 40, 60),
    "lima": (150, 220, 60), "neon": (255, 80, 180), "plata": (200, 206, 214),
    "oro": (232, 186, 60), "electrico": (70, 140, 255), "menta": (140, 220, 190),
    "coral": (250, 120, 100), "lila": (190, 150, 230),
}
_N = {"cafe": "café", "neon": "neón", "electrico": "eléctrico"}


_PLURAL = {"azul": "azules", "verde": "verdes", "naranja": "naranja", "celeste": "celestes",
           "crema": "crema", "gris": "grises", "turquesa": "turquesa"}


def _agregar(grupo, prefijo, nombre, colores, precio, estilo, valor=lambda c: c, plural=False):
    for c in colores:
        palabra = _N.get(c, c)
        if plural:                      # "Lentes redondos rojos"
            palabra = _PLURAL.get(c, palabra + "s")
        ARTICULOS.append((f"{prefijo}_{c}", grupo, f"{nombre} {palabra}", precio,
                          valor(_C[c]), estilo))


# Pulpero
_agregar("sombrero", "gorra", "Gorra", ("verde", "amarilla", "rosada", "morada", "negra",
                                        "naranja", "celeste"), 40, NORMAL, lambda c: ("gorra", c))
_agregar("sombrero", "lana", "Gorro de lana", ("rojo", "azul", "morado", "rosado", "gris"),
         60, NORMAL, lambda c: ("lana", c))
_agregar("sombrero", "boina", "Boina", ("roja", "negra", "azul", "verde"), 90, LLAMATIVO,
         lambda c: ("boina", c))
_agregar("sombrero", "vaquero", "Sombrero vaquero", ("negro", "blanco", "rosado"), 150, LLAMATIVO,
         lambda c: ("vaquero", c))
_agregar("sombrero", "copa", "Sombrero de copa", ("morado", "vino", "blanco"), 220, LUJO,
         lambda c: ("copa", c))
_agregar("lentes", "redondos", "Lentes redondos", ("rojo", "azul", "rosado", "verde"), 50, NORMAL,
         lambda c: ("redondos", c), plural=True)
_agregar("lentes", "cuadrados", "Lentes cuadrados", ("negro", "morado", "naranja"), 60, NORMAL,
         lambda c: ("cuadrados", c), plural=True)
_agregar("lentes", "sol", "Lentes de sol", ("rojo", "azul", "morado"), 80, NORMAL,
         lambda c: ("sol", c), plural=True)
_agregar("lentes", "estrella", "Lentes de estrella", ("azul", "rosado", "verde"), 140, LLAMATIVO,
         lambda c: ("estrella", c), plural=True)
_agregar("lentes", "corazon", "Lentes de corazón", ("rojo", "morado", "celeste"), 140, LLAMATIVO,
         lambda c: ("corazon", c), plural=True)
_agregar("cuello", "corbatin", "Corbatín", ("azul", "rosado", "morado", "negro", "amarillo"),
         60, NORMAL, lambda c: ("corbatin", c))
_agregar("cuello", "corbata", "Corbata", ("roja", "verde", "negra", "morada", "amarilla"),
         60, NORMAL, lambda c: ("corbata", c))
_agregar("cuello", "bufanda", "Bufanda", ("roja", "azul", "morada", "rosada", "amarilla"),
         80, NORMAL, lambda c: ("bufanda", c))
_agregar("camisa", "camisa", "Camisa", ("verde", "amarilla", "morada", "naranja", "celeste",
                                        "rosada", "cafe", "gris", "vino"), 40, NORMAL)
_agregar("camisa", "camisa", "Camisa", ("turquesa", "coral", "electrico", "menta"), 100, LLAMATIVO)
_agregar("camisa", "camisa", "Camisa", ("plata",), 220, LUJO)
_agregar("delantal", "delantal", "Delantal", ("verde", "rojo", "rosado", "morado", "cafe",
                                              "negro", "gris", "crema"), 40, NORMAL)
_agregar("delantal", "delantal", "Delantal", ("lima", "neon", "lila", "coral"), 110, LLAMATIVO)
# Canela
_agregar("pelaje", "pelaje", "Pelaje", ("cafe", "crema"), 60, NORMAL)
_agregar("pelaje", "pelaje", "Pelaje", ("menta", "lila", "morado", "coral"), 160, LLAMATIVO)
_agregar("pelaje", "pelaje", "Pelaje", ("plata",), 320, LUJO)
_agregar("collar", "collar", "Collar", ("amarillo", "morado", "rosado", "negro", "naranja",
                                        "celeste", "blanco"), 30, NORMAL, lambda c: (c, None))
_agregar("collar", "cascabel", "Cascabel", ("azul", "verde", "morado"), 100, LLAMATIVO,
         lambda c: (c, "cascabel"))
_agregar("sombrero_gato", "moño", "Moño", ("rojo", "azul", "amarillo", "morado", "celeste"),
         50, NORMAL, lambda c: ("moño", c))
_agregar("sombrero_gato", "lana_gato", "Gorrito de lana", ("rojo", "azul", "rosado"), 70, NORMAL,
         lambda c: ("lana", c))
_agregar("sombrero_gato", "fiesta", "Gorrito de fiesta", ("rosado", "verde", "morado"), 80,
         LLAMATIVO, lambda c: ("fiesta", c))
# Bruno
_agregar("traje_perro", "sueter", "Suéter", ("azul", "verde", "morado", "rosado", "amarillo"),
         60, NORMAL, lambda c: ("suéter", c))
_agregar("traje_perro", "impermeable", "Impermeable", ("rojo", "azul", "verde", "rosado"), 70,
         NORMAL, lambda c: ("impermeable", c))
_agregar("pelaje_perro", "perro", "Pelaje", ("crema", "vino"), 60, NORMAL)
_agregar("pelaje_perro", "perro", "Pelaje", ("electrico", "rosado", "menta", "lila"), 160, LLAMATIVO)
_agregar("pelaje_perro", "perro", "Pelaje", ("plata",), 300, LUJO)
_agregar("collar_perro", "perro_collar", "Collar", ("verde", "amarillo", "morado", "rosado",
                                                    "negro", "naranja"), 30, NORMAL,
         lambda c: (c, None))
_agregar("collar_perro", "perro_hueso", "Collar con huesito", ("azul", "rojo", "morado"), 60,
         NORMAL, lambda c: (c, "hueso"))
_agregar("collar_perro", "panoleta", "Pañoleta", ("azul", "verde", "amarilla", "morada"), 100,
         LLAMATIVO, lambda c: (c, "pañoleta"))

comprados = set()
puestos = {}            # grupo -> clave
# OPCIONES > EXTRAS > PERSONALIZACIÓN: apagada, nadie lleva ropa (lo comprado
# se guarda y vuelve a aparecer al encenderla).
activo = True


def reiniciar():
    comprados.clear()
    puestos.clear()


def articulo(clave):
    return next((a for a in ARTICULOS if a[0] == clave), None)


_ORDEN_ESTILO = {NORMAL: 0, LLAMATIVO: 1, LUJO: 2}


def articulos_de(grupo):
    """Del más barato al más caro (NORMAL, LLAMATIVO, DE LUJO)."""
    lista = [a for a in ARTICULOS if a[1] == grupo]
    return sorted(lista, key=lambda a: (_ORDEN_ESTILO[a[5]], a[3]))


def es_tuyo(clave):
    a = articulo(clave)
    return clave in comprados or (a is not None and a[3] == 0)


def puesto(grupo):
    """El valor del artículo puesto en ese grupo (o None)."""
    if not activo:
        return None
    clave = puestos.get(grupo)
    a = articulo(clave) if clave else None
    return a[4] if a else None


def alternar(clave):
    """Ponerse o quitarse un artículo ya comprado."""
    grupo = articulo(clave)[1]
    if puestos.get(grupo) == clave:
        del puestos[grupo]
    else:
        puestos[grupo] = clave


def _claro(c, f=0.25):
    return tuple(min(255, round(v + (255 - v) * f)) for v in c)


def _oscuro(c, f=0.3):
    return tuple(round(v * (1 - f)) for v in c)


def vestir(player, mascota=None, perro=None):
    """Aplica la ropa puesta al personaje (y a la gata) y rehace sus dibujos."""
    base = player.SKINS[player.skin]
    camisa = puesto("camisa")
    for nombre, valor in (("SHIRT", camisa), ("SHIRT_LIGHT", camisa and _claro(camisa)),
                          ("SHIRT_DARK", camisa and _oscuro(camisa))):
        if valor:
            setattr(player, nombre, valor)
        elif nombre in base:
            setattr(player, nombre, base[nombre])
        else:
            player.__dict__.pop(nombre, None)
    delantal = puesto("delantal")
    for nombre, valor in (("APRON", delantal), ("APRON_LIGHT", delantal and _claro(delantal)),
                          ("APRON_DARK", delantal and _oscuro(delantal))):
        if valor:
            setattr(player, nombre, valor)
        else:
            player.__dict__.pop(nombre, None)
    player.frames = player._build_frames()
    player.ropa = dibujar_accesorios
    if perro is not None:
        perro.color = puesto("pelaje_perro") or (176, 120, 70)
        perro.collar = puesto("collar_perro")
        perro.traje = puesto("traje_perro")
    if mascota is not None:
        mascota.color = puesto("pelaje") or (236, 150, 60)
        mascota.collar = puesto("collar")
        mascota.sombrero = puesto("sombrero_gato")


# Centro de la cabeza (x), según hacia dónde mira el personaje
# (relativo a la esquina del sprite de 28 x 40).
CABEZA_X = {"down": 14, "up": 14, "left": 15, "right": 13}


def dibujar_accesorios(surface, player, rect):
    """Cuello, lentes y sombrero encima del sprite del personaje."""
    d = player.direction
    cx = rect.x + CABEZA_X.get(d, 14)
    dibujar_cuello(surface, puesto("cuello"), cx, rect.y + 15, d)
    if d != "up":
        dibujar_lentes(surface, puesto("lentes"), rect, d)
    dibujar_sombrero(surface, puesto("sombrero"), cx, rect.y + 1, d)


# ---------------------------------------------------------
# DIBUJOS
# ---------------------------------------------------------
NEGRO = (30, 30, 36)
ORO, ORO_OSCURO = (250, 206, 70), (170, 120, 30)


def _estrella(surface, color, cx, cy, r):
    import math
    puntos = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        puntos.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(surface, color, puntos)


def _corazon(surface, color, cx, cy):
    pygame.draw.circle(surface, color, (cx - 1, cy - 1), 2)
    pygame.draw.circle(surface, color, (cx + 2, cy - 1), 2)
    pygame.draw.polygon(surface, color, [(cx - 3, cy), (cx + 4, cy), (cx, cy + 3)])


def dibujar_lentes(surface, lentes, rect, d):
    if not lentes:
        return
    color = None
    if isinstance(lentes, tuple):           # ("redondos", color del marco)
        lentes, color = lentes
    if d == "down":
        ojos = [(rect.x + 11, rect.y + 9), (rect.x + 18, rect.y + 9)]
    else:
        ojos = [(rect.x + (12 if d == "left" else 16), rect.y + 8)]
    if lentes == "monoculo":
        x, y = ojos[-1]
        pygame.draw.circle(surface, ORO, (x, y), 3, 1)
        pygame.draw.line(surface, ORO, (x + 2, y + 2), (x + 3, y + 9), 1)
        return
    for x, y in ojos:
        if lentes == "redondos":
            pygame.draw.circle(surface, color or NEGRO, (x, y), 3, 1)
        elif lentes == "cuadrados":
            pygame.draw.rect(surface, color or (110, 70, 40), (x - 3, y - 2, 6, 5), 1)
        elif lentes == "sol":
            pygame.draw.rect(surface, color or NEGRO, (x - 2, y - 1, 5, 3))
            pygame.draw.rect(surface, (120, 160, 200) if not color else (250, 250, 250), (x - 1, y - 1, 1, 1))
        elif lentes == "estrella":
            _estrella(surface, color or (255, 214, 40), x, y, 4)
        elif lentes == "corazon":
            _corazon(surface, color or (240, 70, 140), x, y)
    if d == "down" and lentes in ("redondos", "cuadrados", "sol"):
        pygame.draw.line(surface, color or NEGRO, (ojos[0][0] + 3, ojos[0][1]), (ojos[1][0] - 3, ojos[1][1]), 1)


def dibujar_cuello(surface, cuello, cx, y, d):
    if not cuello:
        return
    tipo, color = cuello
    if tipo == "bufanda":
        pygame.draw.rect(surface, _oscuro(color), (cx - 8, y, 16, 4))
        pygame.draw.rect(surface, color, (cx - 7, y, 14, 3))
        if d != "up":
            lado = cx + (3 if d != "left" else -6)
            pygame.draw.rect(surface, color, (lado, y + 3, 3, 7))
        return
    if d == "up":
        return
    if tipo == "corbatin":
        pygame.draw.polygon(surface, color, [(cx - 4, y - 1), (cx, y + 1), (cx - 4, y + 3)])
        pygame.draw.polygon(surface, color, [(cx + 4, y - 1), (cx, y + 1), (cx + 4, y + 3)])
        pygame.draw.rect(surface, _oscuro(color), (cx - 1, y, 2, 2))
    elif tipo == "corbata":
        pygame.draw.rect(surface, _oscuro(color), (cx - 1, y, 3, 2))
        pygame.draw.polygon(surface, color, [(cx - 1, y + 2), (cx + 2, y + 2), (cx + 3, y + 10),
                                             (cx + 0, y + 12), (cx - 2, y + 10)])
    elif tipo == "flores":
        for i, c in enumerate(((250, 120, 170), (255, 220, 60), (120, 200, 255), (250, 120, 170),
                               (255, 220, 60))):
            pygame.draw.circle(surface, c, (cx - 6 + i * 3, y + 1 + (2 if i in (1, 2, 3) else 0)), 2)
    elif tipo == "medalla":
        pygame.draw.line(surface, ORO, (cx - 5, y), (cx, y + 7), 1)
        pygame.draw.line(surface, ORO, (cx + 5, y), (cx, y + 7), 1)
        pygame.draw.circle(surface, ORO_OSCURO, (cx, y + 9), 3)
        pygame.draw.circle(surface, ORO, (cx, y + 9), 2)


def dibujar_sombrero(surface, sombrero, cx, top, d="down"):
    if not sombrero:
        return
    tipo, color = sombrero
    if tipo == "gorra":
        oscuro = _oscuro(color, 0.35)
        pygame.draw.rect(surface, oscuro, (cx - 9, top - 3, 18, 6))
        pygame.draw.rect(surface, color, (cx - 8, top - 2, 16, 4))
        pygame.draw.rect(surface, (250, 250, 250), (cx - 1, top - 2, 2, 2))
        if d == "down":
            pygame.draw.rect(surface, oscuro, (cx - 9, top + 2, 18, 2))
        elif d == "left":
            pygame.draw.rect(surface, oscuro, (cx - 14, top + 1, 7, 2))
        elif d == "right":
            pygame.draw.rect(surface, oscuro, (cx + 7, top + 1, 7, 2))
    elif tipo == "lana":
        pygame.draw.rect(surface, _oscuro(color), (cx - 9, top - 4, 18, 7))
        pygame.draw.rect(surface, color, (cx - 8, top - 3, 16, 5))
        pygame.draw.rect(surface, _claro(color, 0.5), (cx - 9, top + 1, 18, 2))
        pygame.draw.circle(surface, (240, 240, 236), (cx, top - 6), 3)
    elif tipo == "paja":
        paja, oscuro = (232, 200, 120), (160, 124, 64)
        pygame.draw.ellipse(surface, oscuro, (cx - 14, top - 1, 28, 7))
        pygame.draw.ellipse(surface, paja, (cx - 13, top - 1, 26, 5))
        pygame.draw.rect(surface, oscuro, (cx - 8, top - 7, 16, 8))
        pygame.draw.rect(surface, paja, (cx - 7, top - 6, 14, 6))
        pygame.draw.rect(surface, (190, 60, 50), (cx - 7, top - 2, 14, 2))
    elif tipo == "boina":
        pygame.draw.ellipse(surface, _oscuro(color), (cx - 11, top - 4, 22, 8))
        pygame.draw.ellipse(surface, color, (cx - 10, top - 4, 20, 6))
        pygame.draw.rect(surface, _oscuro(color), (cx + 1, top - 7, 2, 3))
    elif tipo == "chef":
        blanco, gris = (250, 250, 246), (190, 190, 186)
        pygame.draw.rect(surface, gris, (cx - 8, top - 3, 16, 6))
        pygame.draw.rect(surface, blanco, (cx - 7, top - 2, 14, 4))
        for ox in (-5, 0, 5):
            pygame.draw.circle(surface, gris, (cx + ox, top - 7), 5)
        for ox in (-5, 0, 5):
            pygame.draw.circle(surface, blanco, (cx + ox, top - 7), 4)
    elif tipo == "vaquero":
        oscuro = _oscuro(color)
        pygame.draw.ellipse(surface, oscuro, (cx - 16, top - 1, 32, 7))
        pygame.draw.ellipse(surface, color, (cx - 15, top - 1, 30, 5))
        pygame.draw.polygon(surface, oscuro, [(cx - 8, top + 1), (cx - 7, top - 8), (cx, top - 6),
                                              (cx + 7, top - 8), (cx + 8, top + 1)])
        pygame.draw.polygon(surface, color, [(cx - 7, top), (cx - 6, top - 7), (cx, top - 5),
                                             (cx + 6, top - 7), (cx + 7, top)])
        pygame.draw.rect(surface, (230, 200, 120), (cx - 7, top - 2, 14, 2))
    elif tipo == "copa":
        pygame.draw.rect(surface, color, (cx - 12, top, 24, 3))
        pygame.draw.rect(surface, color, (cx - 7, top - 13, 14, 14))
        pygame.draw.rect(surface, (200, 40, 50), (cx - 7, top - 4, 14, 3))
        pygame.draw.line(surface, (90, 90, 100), (cx - 5, top - 12), (cx - 5, top - 6), 1)
    elif tipo == "corona":
        puntos = [(cx - 8, top + 2), (cx - 8, top - 6), (cx - 4, top - 2), (cx, top - 8),
                  (cx + 4, top - 2), (cx + 8, top - 6), (cx + 8, top + 2)]
        pygame.draw.polygon(surface, ORO, puntos)
        pygame.draw.polygon(surface, ORO_OSCURO, puntos, 1)
        pygame.draw.circle(surface, (220, 60, 80), (cx, top - 1), 1)
        pygame.draw.circle(surface, (80, 140, 230), (cx - 5, top), 1)
        pygame.draw.circle(surface, (80, 140, 230), (cx + 5, top), 1)
