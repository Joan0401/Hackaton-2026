import math
import math
import random

import pygame
import sys
import os

from interior import draw_interior_background, FurnitureManager, TableObjectManager, FLOOR_TOP
from personaje import Player
from factura import FacturaInteractiva
import calculadora as calc_mod
from calculadora import Calculadora
from bodega import Bodega
from clientes import Clientes
import historia
import estadisticas
from vista_mueble import VistaMueble
from recetario import Recetario
from carrito import Carrito
from productos import tamano as tamano_producto, dibujar_producto, FRUTAS, VERDURAS, BEBIDAS, ABARROTES
from productos import HELADOS
from luciernagas import Luciernagas
from tutorial import Tutorial
import modos
from ayudante import Ayudante, dibujar_boton, cerca_boton, rect_boton, PAGO_POR_HORA
from mascota import Mascota
from perro import Perro, NOMBRE as NOMBRE_PERRO
import persecucion
from casa_gato import CasaGato, NIVELES as NIVELES_CASA, dibujar_casa
import cosmeticos
from camion import (Camion, MAX_CAJAS, MAX_CAJAS_POR_PRODUCTO, HORA_LIMITE_PEDIDO,
                    unidades_caja, costo as costo_mayoreo)
from zonas import stock_inicial_bodega
from modos import MODO
from horario import Reloj
from ambiente import Calle, rect_poste
from fuentes import FuenteTienda  # soporta el símbolo ₡
import fuentes
import sonido
import interior as interior_mod
import zonas as zonas_mod
from zonas import PUERTA_SALA_X
from niveles import NIVELES, ORDEN as ORDEN_NIVELES, NIVEL_INICIAL
from productos import PRODUCTOS, sprite as sprite_producto
from zonas import (
    dibujar_entrada,
    dibujar_inventario,
    dibujar_accesos_sala,
    dibujar_hud_zona,
    obstaculos_inventario,
    ARMARIO as ARMARIO_BODEGA,
    acceso_actual,
    destino_al_cruzar,
    EXTERIOR_FLOOR_TOP,
    INVENTARIO_FLOOR_TOP,
)

# =========================================================
# CONFIGURACION GENERAL
# =========================================================
pygame.init()

GAME_WIDTH = 640
GAME_HEIGHT = 360

# Las coordenadas originales del arte se expresan sobre este lienzo.
MENU_WIDTH = 480
MENU_HEIGHT = 270
MENU_SCALE = GAME_WIDTH / MENU_WIDTH

SCALE = 2
WINDOW_WIDTH = GAME_WIDTH * SCALE
WINDOW_HEIGHT = GAME_HEIGHT * SCALE

FPS = 60

# ---------------------------------------------------------
# PANTALLA: todo se dibuja en un lienzo de 1280 x 720 ("screen") y al final
# se agranda para llenar la ventana o la pantalla completa (sin deformar:
# si sobra, quedan franjas negras). F11 cambia entre ventana y pantalla
# completa; también en OPCIONES > GRÁFICOS > PANTALLA COMPLETA.
# ---------------------------------------------------------
def _dpi_windows():
    """En Windows con la pantalla agrandada (125 %, 150 %...), sin esto el
    juego se ve borroso o no cabe."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


_dpi_windows()
pantalla_completa = True     # viene en pantalla completa
ventana = None
screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))   # lienzo del juego


def crear_ventana():
    """Pantalla completa, o una ventana que cabe en el monitor (se puede
    agrandar o maximizar)."""
    global ventana
    if os.environ.get("SDL_VIDEODRIVER") == "dummy":
        ventana = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        return
    if pantalla_completa:
        ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return
    try:
        ancho, alto = pygame.display.get_desktop_sizes()[0]
    except Exception:
        ancho, alto = WINDOW_WIDTH, WINDOW_HEIGHT
    f = min(ancho * 0.85 / WINDOW_WIDTH, alto * 0.80 / WINDOW_HEIGHT)
    ventana = pygame.display.set_mode((round(WINDOW_WIDTH * f), round(WINDOW_HEIGHT * f)),
                                      pygame.RESIZABLE)


def cambiar_pantalla_completa():
    global pantalla_completa
    pantalla_completa = not pantalla_completa
    crear_ventana()


def _rect_lienzo():
    """Dónde va el juego dentro de la ventana (centrado, sin deformar)."""
    vw, vh = ventana.get_size()
    f = min(vw / WINDOW_WIDTH, vh / WINDOW_HEIGHT)
    w, h = max(1, round(WINDOW_WIDTH * f)), max(1, round(WINDOW_HEIGHT * f))
    return pygame.Rect((vw - w) // 2, (vh - h) // 2, w, h)


def presentar():
    """Pasa el lienzo a la ventana (agrandado) y lo muestra."""
    r = _rect_lienzo()
    if r.size == screen.get_size():
        ventana.blit(screen, r.topleft)
    else:
        ventana.fill((0, 0, 0))
        ventana.blit(pygame.transform.scale(screen, r.size), r.topleft)
    pygame.display.flip()


def ventana_a_lienzo(pos):
    """Convierte un punto de la ventana a coordenadas del lienzo (1280 x 720)."""
    r = _rect_lienzo()
    x = (pos[0] - r.x) * WINDOW_WIDTH / r.w
    y = (pos[1] - r.y) * WINDOW_HEIGHT / r.h
    return (int(max(0, min(WINDOW_WIDTH - 1, x))), int(max(0, min(WINDOW_HEIGHT - 1, y))))


_mouse_get_pos = pygame.mouse.get_pos


def _mouse_en_lienzo():
    return ventana_a_lienzo(_mouse_get_pos())


pygame.mouse.get_pos = _mouse_en_lienzo    # todo el juego ve el mouse en el lienzo


def eventos():
    """Como pygame.event.get(), pero con el mouse en coordenadas del lienzo.
    F11 (o ALT + ENTER) cambia a pantalla completa o ventana."""
    for event in pygame.event.get():
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            datos = dict(event.dict)
            datos["pos"] = ventana_a_lienzo(event.pos)
            yield pygame.event.Event(event.type, datos)
            continue
        if event.type == pygame.KEYDOWN and (
                event.key == pygame.K_F11
                or (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT)):
            cambiar_pantalla_completa()
            continue
        if event.type in (pygame.VIDEORESIZE, getattr(pygame, "WINDOWRESIZED", -1)):
            global ventana
            ventana = pygame.display.get_surface()
        yield event


crear_ventana()
pygame.display.set_caption("La Pulpería")

game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
clock = pygame.time.Clock()

# Fondo interior precalculado
interior_background = pygame.Surface(
    (GAME_WIDTH, GAME_HEIGHT)
)

draw_interior_background(interior_background)

# Otras zonas: fondo precalculado. Todo el arte es Pygame nativo.
entrada_background = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
dibujar_entrada(entrada_background)
# Nombre del cartel de la pulpería: lo escoge el niño al empezar la partida
# (en el menú siempre dice LA PULPERIA). "" = LA PULPERIA.
nombre_tienda = ""


def redibujar_entrada():
    """La fachada con el nombre que escogió el niño en el cartel."""
    dibujar_entrada(entrada_background, nombre=nombre_tienda or None)

inventario_background = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
dibujar_inventario(inventario_background)

# Gestor de muebles reorganizables.
furniture_manager = FurnitureManager()
table_object_manager = TableObjectManager(furniture_manager)
# Productos de la bodega que se pueden llevar a la tienda.
bodega = Bodega()

# Escena actual
current_scene = "menu"
ultima_zona = None   # Para que CONTINUAR recupere la zona al regresar al menú.

# Estado de la ventana de cobro.
checkout_open = False
checkout_exercise = None
checkout_receipt_total = None

# Calculadora de apoyo para la factura. calc_foco indica si el teclado
# escribe en la calculadora (True) o en la factura (False).
calculadora = Calculadora()
calc_foco = False
# La calculadora aparece solo después de varias respuestas equivocadas
# en la misma factura (depende del nivel): primero, cálculo mental.
calc_errores = 0
calc_desbloqueada = False
# Errores por fila de la factura, para dar pistas escalonadas, y la
# pista vigente de cada fila (se queda visible mientras corrige).
errores_por_fila = {}
pistas_por_fila = {}

# Dificultad elegida en OPCIONES (ver niveles.py).
nivel_actual = NIVEL_INICIAL
# Paciencia de los clientes: viene desactivada; se activa en
# OPCIONES > MODO DE JUEGO (MODO["paciencia"]).
paciencia_activa = False
# Filas de OPCIONES, en este orden:
FILA_SONIDO = 0      # abre SONIDO
FILA_VISUAL = 1      # abre GRÁFICOS (tipo de letra, luciérnagas, colores)
FILA_DIFICULTAD = 2  # principiante / intermedio / avanzado (izq./der.)
FILA_MODO = 3        # abre MODO DE JUEGO (qué problemas aparecen, paciencia)
FILA_EXTRAS = 4      # abre EXTRAS (mascotas y personalización, cada una sí/no)
FILA_TUTORIAL = 5    # empieza el tutorial guiado
FILAS_OPCIONES = 6
# OPCIONES > EXTRAS: sistemas que se pueden apagar por completo.
#   mascotas: Canela, Bruno, la casa de Canela, su comida y la persecución.
#   personalizacion: el armario de la bodega y toda la ropa puesta.
# Por defecto: mascotas encendidas con solo Canela; personalización apagada.
EXTRAS = {"mascotas": True, "personalizacion": False}
# Cuáles mascotas eligió el jugador (cuando las mascotas están encendidas).
MASCOTAS_ELEGIDAS = {"gata": True, "perro": False}
# Las que de verdad están en la tienda (las usa todo el juego).
MASCOTAS = {"gata": True, "perro": False}
OPCIONES_MASCOTAS = [  # (texto, gata, perro)
    ("CANELA Y BRUNO", True, True), ("SOLO CANELA", True, False),
    ("SOLO BRUNO", False, True),
]
FILAS_EXTRAS = ("mascotas", "cuales", "personalizacion", "reporte")
extras_seleccion = 0
sonido_seleccion = 0
efecto_prueba = 0
ambiente_prueba = 0
FILAS_SONIDO = [
    ("estilo", "MÚSICA DEL MENÚ"),
    ("estilo_tienda", "MÚSICA DE LA TIENDA"),
    ("vol_musica", "VOLUMEN DE LA MÚSICA"),
    ("efectos", "EFECTOS ESPECIALES"),
    ("vol_efectos", "VOLUMEN DE LOS EFECTOS"),
    ("probar_efecto", "PROBAR UN EFECTO"),
    ("ambiente", "RUIDO DE FONDO"),
    ("vol_ambiente", "VOLUMEN DEL RUIDO DE FONDO"),
    ("probar_ambiente", "PROBAR UN RUIDO DE FONDO"),
]
modo_seleccion = 0
visual_seleccion = 0
luciernagas_activas = True
# Aviso de abajo ("E: ACARICIAR A CANELA"...): se apaga en GRÁFICOS.
avisos_activos = True
# Burbujas de ayuda (tooltips) de las opciones: vienen activadas.
tooltips_activos = True
# Filas de AJUSTES VISUALES: (clave, nombre en pantalla)
FILAS_VISUALES = [
    ("letra", "TIPO DE LETRA"),
    ("luciernagas", "LUCIÉRNAGAS"),
    ("avisos", "AVISOS DE ABAJO"),
    ("tooltips", "BURBUJAS DE AYUDA"),
    ("pantalla", "PANTALLA COMPLETA (F11)"),
    ("paredes", "PAREDES"),
    ("piso", "PISO"),
    ("alfombras", "ALFOMBRAS"),
    ("mesa", "MOSTRADOR (MESA)"),
    ("refris", "REFRIGERADORAS"),
    ("muebles", "MUEBLES"),
    ("original", "VOLVER A LOS COLORES ORIGINALES"),
]
BILLETES_PAGO = [1, 2, 5, 10, 20]


def pago_cliente(total):
    """Con cuánto paga el cliente: billetes de 1, 2, 5, 10 y 20 (solo se dice
    la suma). Como una persona real, no da billetes de más: si quitara
    cualquiera de ellos, ya no le alcanzaría."""
    import itertools
    sumas = set()
    for cantidad in range(1, 6):
        for billetes in itertools.combinations_with_replacement(BILLETES_PAGO, cantidad):
            suma = sum(billetes)
            if suma >= total and suma - min(billetes) < total:
                sumas.add(suma)
    return random.choice(sorted(sumas)) if sumas else total


opciones_seleccion = FILA_SONIDO

def nivel():
    return NIVELES[nivel_actual]


def factura_muestra_cantidad():
    """Si la factura dice cuántos hay (si no, el niño cuenta los dibujos)."""
    return nivel()["factura_muestra_cantidad"] or not MODO["contar"]


# Clientes con pedidos (ver clientes.py). Usan la dificultad elegida.
clientes = Clientes(nivel)

# Vuelto del nivel avanzado: se pide después de cobrar la factura.
BILLETES = [5, 10, 20, 50, 100, 200]
vuelto = None


# Vista de cerca del mueble (refri, góndola, mostrador o bodega) para
# elegir qué tomar. None = cerrada. Se dibuja en alta resolución.
menu_tomar = None
# Libro de recetas (tecla R), también en alta resolución.
recetario = Recetario()
# Tutorial guiado (siempre el mismo): se activa en OPCIONES.
tutorial = Tutorial()
tutorial_inicio = (0.0, 0.0)
tutorial_enter = False


def iniciar_tutorial():
    global tutorial_inicio, tutorial_enter
    tutorial.empezar()
    clientes.tutorial = True
    clientes.lista.clear()
    clientes.cliente_tutorial()
    tutorial_inicio = (player.x, player.y)
    tutorial_enter = False


def terminar_tutorial():
    """Al terminar (o saltar) el tutorial empieza el día 1 de verdad."""
    global historial_abierto
    tutorial.terminar()
    clientes.tutorial = False
    clientes.reiniciar()
    clientes.esperando_jugador = False
    nueva_partida_jornada()
    historial_abierto = False
    recetario.cerrar()
    if historia_activa:
        abrir_bienvenida(True)          # MODO HISTORIA: ahora sí, Doña Rosa
    elif not nombre_tienda:
        abrir_cartel()                  # LIBRE: el nombre del cartel
    guardar_partida()


def estado_tutorial():
    """Lo que el tutorial necesita saber para avanzar de paso."""
    tom = table_object_manager
    return {
        "caminado": math.hypot(player.x - tutorial_inicio[0], player.y - tutorial_inicio[1]),
        "vista": (menu_tomar.mueble["id"] if menu_tomar is not None and menu_tomar.origen == "tienda"
                  else None),
        "manzanas_mano": sum(1 for i in tom.mano if i["kind"] == "manzana"),
        "manzanas_mostrador": sum(1 for i in tom.items
                                  if i["kind"] == "manzana" and i["table_id"] == "counter"),
        "factura": checkout_open,
        "ventas": len(ventas_dia),
        "historial": historial_abierto,
        "recetario": recetario.abierto,
        "escena": current_scene,
        "enter": tutorial_enter,
    }


def puntos_tutorial():
    """Dónde apunta la flecha del tutorial (coordenadas 640 x 360)."""
    puntos = {}
    for mueble in furniture_manager.items:
        if mueble["id"] in ("gondola_1", "counter"):
            puntos[mueble["id"]] = (round(mueble["x"] + mueble["w"] / 2), round(mueble["y"]) + 4)
    for item in table_object_manager.items:
        if item["kind"] == "register":
            x, y = table_object_manager._position(item, furniture_manager)
            puntos["caja"] = (round(x + item["w"] / 2), round(y))
    libro = table_object_manager.rect_recetario(furniture_manager)
    if libro is not None:
        puntos["libro"] = (libro.centerx, libro.top)
    for item in table_object_manager.items:
        if item["kind"] == "telefono":
            x, y = table_object_manager._position(item, furniture_manager)
            puntos["telefono"] = (round(x + item["w"] / 2), round(y))
    puntos["bodega"] = (607, 120)
    lx, ly = LETRERO_TIENDA["interior"]
    puntos["letrero"] = (lx, ly - 10)
    return puntos


def draw_tutorial_screen():
    """El letrero del tutorial va encima de todo (también de la factura)."""
    if not tutorial.activo or current_scene not in ("interior", "inventario", "entrada"):
        return
    capa = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    flecha = (current_scene == "interior" and menu_tomar is None and not checkout_open
              and not recetario.abierto and not historial_abierto)
    # El letrero del tutorial va abajo (no tapa los globos), salvo cuando
    # la flecha señala algo de abajo (el letrero de la puerta).
    import tutorial as tutorial_mod
    objetivo = tutorial_mod.PASOS[tutorial.paso][2] if tutorial.activo else None
    tutorial.dibujar(capa, font_medium, font_small, nombre_bonito(), puntos_tutorial(), flecha,
                     abajo=(flecha or current_scene != "interior") and objetivo != "letrero")
    screen.blit(pygame.transform.scale(capa, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))


# ---------------------------------------------------------
# SONIDO: pantalla de opciones y efectos según lo que pasa en el juego
# ---------------------------------------------------------
def cambiar_sonido(clave, paso, enter=False):
    global efecto_prueba, ambiente_prueba
    if clave == "estilo":
        sonido.cambiar_estilo(paso)
    elif clave == "estilo_tienda":
        sonido.cambiar_estilo_tienda(paso)
    elif clave == "cancion":
        if sonido.ESTILOS[sonido.estilo]:
            sonido.cancion = (sonido.cancion + paso) % len(sonido.ESTILOS[sonido.estilo])
            sonido.tocar_musica()
    elif clave == "vol_musica":
        sonido.cambiar_volumen_musica(paso)
    elif clave == "efectos":
        sonido.efectos_activos = not sonido.efectos_activos
        sonido.efecto("cobrar")
    elif clave == "vol_efectos":
        sonido.cambiar_volumen_efectos(paso)
    elif clave == "probar_efecto":
        if not enter:
            efecto_prueba = (efecto_prueba + paso) % len(sonido.ORDEN_EFECTOS)
        sonido.efecto(sonido.EFECTOS[sonido.ORDEN_EFECTOS[efecto_prueba]], forzar=True)
    elif clave == "ambiente":
        sonido.ambiente_activo = not sonido.ambiente_activo
        if sonido.ambiente_activo:
            sonido.probar_ambiente("VIENTO")
    elif clave == "vol_ambiente":
        sonido.cambiar_volumen_ambiente(paso)
        sonido.probar_ambiente(sonido.ORDEN_AMBIENTES[ambiente_prueba])
    elif clave == "probar_ambiente":
        if not enter:
            ambiente_prueba = (ambiente_prueba + paso) % len(sonido.ORDEN_AMBIENTES)
        sonido.probar_ambiente(sonido.ORDEN_AMBIENTES[ambiente_prueba])


def valor_sonido(clave):
    if clave == "estilo":
        return sonido.estilo
    if clave == "estilo_tienda":
        return sonido.estilo_tienda
    if clave == "cancion":
        canciones = sonido.ESTILOS[sonido.estilo]
        return f"{sonido.cancion % len(canciones) + 1}/{len(canciones)}" if canciones else "-"
    if clave == "efectos":
        return "SÍ" if sonido.efectos_activos else "NO"
    if clave == "ambiente":
        return "SÍ" if sonido.ambiente_activo else "NO"
    if clave == "probar_efecto":
        return sonido.ORDEN_EFECTOS[efecto_prueba]
    if clave == "probar_ambiente":
        return sonido.ORDEN_AMBIENTES[ambiente_prueba]
    return None


def draw_sonido(surface):
    """OPCIONES > SONIDO."""
    draw_background(surface)
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 120))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(40, 12, 560, 336)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, BUTTON_BLUE_DARK, (46, 18, 548, 34))
    title = font_title.render("SONIDO", False, CREAM)
    surface.blit(title, title.get_rect(center=(320, 35)))
    for i, (clave, nombre) in enumerate(FILAS_SONIDO):
        fila = pygame.Rect(66, 62 + i * 27, 508, 24)
        elegido = i == sonido_seleccion
        pygame.draw.rect(surface, CREAM if elegido else (226, 206, 158), fila)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK if elegido else WOOD_DARK, fila, 3 if elegido else 1)
        if elegido:
            pygame.draw.polygon(surface, BUTTON_HIGHLIGHT_DARK, [
                (fila.x - 12, fila.centery - 6), (fila.x - 4, fila.centery),
                (fila.x - 12, fila.centery + 6)])
        t = font_small.render(nombre, False, WOOD_DARK)
        surface.blit(t, t.get_rect(midleft=(fila.x + 10, fila.centery + 1)))
        if clave.startswith("vol_"):
            nivel_vol = {"vol_musica": sonido.volumen_musica, "vol_efectos": sonido.volumen_efectos,
                         "vol_ambiente": sonido.volumen_ambiente}[clave]
            for k in range(10):
                barra = pygame.Rect(fila.right - 150 + k * 14, fila.y + 5, 11, 14)
                pygame.draw.rect(surface, (66, 130, 70) if k < nivel_vol else (196, 180, 140), barra)
                pygame.draw.rect(surface, WOOD_DARK, barra, 1)
        else:
            valor = valor_sonido(clave)
            if clave in ("efectos", "ambiente"):
                tv = font_small.render(valor, False, (66, 130, 70) if valor == "SÍ" else (176, 48, 42))
            else:
                tv = font_small.render(f"< {valor} >", False, RED_SIGN)
            surface.blit(tv, tv.get_rect(midright=(fila.right - 10, fila.centery + 1)))
    caja = pygame.Rect(66, 307, 508, 22)
    pygame.draw.rect(surface, CREAM, caja)
    pygame.draw.rect(surface, WOOD_DARK, caja, 2)
    if not sonido.disponible():
        texto = "Esta computadora no tiene sonido disponible."
    elif sonido.canciones_actuales():
        texto = (f"Suena: \"{sonido.titulo_cancion()}\" ({sonido.estilo_actual().lower()}). "
                 "Las canciones se alternan.")
    else:
        texto = "Sin música de fondo."
    tt = font_small.render(texto, False, WOOD_DARK)
    surface.blit(tt, tt.get_rect(center=caja.center))
    # Ayuda de la fila marcada.
    clave = FILAS_SONIDO[sonido_seleccion][0]
    fila = pygame.Rect(66, 62 + sonido_seleccion * 27, 508, 24)
    dibujar_tooltip(surface, pygame.Rect(fila.centerx, fila.y, fila.w // 2, fila.h),
                    TOOLTIP_SONIDO.get(clave, ""), "abajo", 240)


MAX_ERRORES_CIERRE = 4
_antes_sonido = {}


def sonidos_por_cambios():
    """Efectos según lo que cambió desde el cuadro anterior."""
    global _antes_sonido
    exercise = checkout_exercise
    ahora = {
        "mano": len(table_object_manager.mano),
        "factura": checkout_open,
        "ventas": len(ventas_dia),
        "correctos": sum(exercise.correctos) if exercise is not None else 0,
        "clientes": clientes.generados,
        "ayudante": ayudante.estado,
        "cierre": bool(cierre and cierre["listo"] and ventas_dia
                       and cierre["errores"] < MAX_ERRORES_CIERRE),
        "pago": bool(pago_ayudante and pago_ayudante["listo"]),
    }
    a = _antes_sonido
    if a and current_scene in ("interior", "entrada", "inventario"):
        if ahora["mano"] > a["mano"]:
            sonido.efecto("tomar")
        elif ahora["mano"] < a["mano"] and ahora["ventas"] == a["ventas"]:
            sonido.efecto("dejar")
        if ahora["factura"] and not a["factura"]:
            sonido.efecto("abrir_caja")
        if ahora["ventas"] > a["ventas"]:
            sonido.efecto("cobrar")
        elif ahora["correctos"] > a["correctos"] or (ahora["pago"] and not a["pago"]):
            sonido.efecto("acierto")
        if ahora["clientes"] > a["clientes"]:
            sonido.efecto("campanita")
        if ahora["ayudante"] == "trabajando" and a["ayudante"] == "ausente":
            sonido.efecto("timbre")
        if ahora["cierre"] and not a["cierre"]:
            sonido.efecto("logro")
    _antes_sonido = ahora


def rehacer_fondo():
    """Vuelve a dibujar los fondos con los colores elegidos (sala y bodega)."""
    draw_interior_background(interior_background)
    dibujar_inventario(inventario_background)
    redibujar_entrada()


def dibujar_alfombras(surface):
    """Alfombrillas de la sala con el color elegido."""
    base = interior_mod.color_base("alfombras")
    if base is None:
        dibujar_accesos_sala(surface)
        return
    antes = (zonas_mod.WOOD, zonas_mod.WOOD_TOP, zonas_mod.DARK)
    zonas_mod.WOOD = base
    zonas_mod.WOOD_TOP = interior_mod._claro(base, 0.3)
    zonas_mod.DARK = interior_mod._oscuro(base, 0.55)
    try:
        dibujar_accesos_sala(surface)
    finally:
        zonas_mod.WOOD, zonas_mod.WOOD_TOP, zonas_mod.DARK = antes


def cambiar_visual(clave, paso):
    """Flechas / ENTER sobre una fila de AJUSTES VISUALES."""
    global luciernagas_activas, avisos_activos, tooltips_activos
    if clave == "letra":
        i = fuentes.ORDEN_TIPOS.index(fuentes.tipo_actual)
        fuentes.cambiar_tipo(fuentes.ORDEN_TIPOS[(i + paso) % len(fuentes.ORDEN_TIPOS)])
    elif clave == "luciernagas":
        luciernagas_activas = not luciernagas_activas
    elif clave == "avisos":
        avisos_activos = not avisos_activos
        zonas_mod.AVISOS_ACTIVOS = avisos_activos
    elif clave == "tooltips":
        tooltips_activos = not tooltips_activos
    elif clave == "pantalla":
        cambiar_pantalla_completa()
    elif clave == "original":
        interior_mod.restablecer_colores()
        rehacer_fondo()
    else:
        opciones = interior_mod.OPCIONES_COLOR[clave]
        interior_mod.COLOR_ELEGIDO[clave] = (interior_mod.COLOR_ELEGIDO[clave] + paso) % len(opciones)
        rehacer_fondo()


def valor_visual(clave):
    if clave == "letra":
        return fuentes.tipo_actual
    if clave == "luciernagas":
        return "SÍ" if luciernagas_activas else "NO"
    if clave == "avisos":
        return "SÍ" if avisos_activos else "NO"
    if clave == "tooltips":
        return "SÍ" if tooltips_activos else "NO"
    if clave == "pantalla":
        return "SÍ" if pantalla_completa else "NO"
    if clave == "original":
        return ""
    return interior_mod.OPCIONES_COLOR[clave][interior_mod.COLOR_ELEGIDO[clave]][0]


def draw_vista_previa(surface, rect):
    """Mini tienda para ver los colores elegidos."""
    previa = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    previa.blit(interior_background, (0, 0))
    dibujar_alfombras(previa)
    dibujar_boton(previa)
    for mueble in sorted(furniture_manager.items, key=lambda m: m["y"] + m["h"]):
        furniture_manager._draw_item(previa, mueble)
        table_object_manager.draw_table_objects(previa, mueble)
        furniture_manager._draw_after_objects(previa, mueble)
    if luciernagas_activas:
        luciernagas.dibujar(previa, 1.0)
    chico = pygame.transform.smoothscale(previa, rect.size)
    pygame.draw.rect(surface, (35, 27, 27), rect.move(3, 3))
    surface.blit(chico, rect)
    pygame.draw.rect(surface, WOOD_DARK, rect, 2)


def draw_visuales(surface):
    """OPCIONES > AJUSTES VISUALES."""
    draw_background(surface)
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 120))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(16, 12, 608, 336)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (22, 18, 596, 34))
    title = font_title.render("GRÁFICOS", False, CREAM)
    surface.blit(title, title.get_rect(center=(320, 35)))

    for i, (clave, nombre) in enumerate(FILAS_VISUALES):
        fila = pygame.Rect(40, 60 + i * 24, 340, 22)
        elegido = i == visual_seleccion
        pygame.draw.rect(surface, CREAM if elegido else (226, 206, 158), fila)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK if elegido else WOOD_DARK, fila, 3 if elegido else 1)
        if elegido:
            pygame.draw.polygon(surface, BUTTON_HIGHLIGHT_DARK, [
                (fila.x - 12, fila.centery - 6), (fila.x - 4, fila.centery),
                (fila.x - 12, fila.centery + 6)])
        t = font_small.render(nombre, False, WOOD_DARK)
        surface.blit(t, t.get_rect(midleft=(fila.x + 8, fila.centery + 1)))
        valor = valor_visual(clave)
        if clave in interior_mod.OPCIONES_COLOR:
            base = interior_mod.color_base(clave)
            muestra = pygame.Rect(fila.right - 132, fila.y + 4, 16, 16)
            if base is None:
                pygame.draw.rect(surface, (230, 222, 200), muestra)
                pygame.draw.line(surface, (176, 64, 52), muestra.bottomleft, muestra.topright, 2)
            else:
                pygame.draw.rect(surface, base, muestra)
            pygame.draw.rect(surface, WOOD_DARK, muestra, 1)
        if valor:
            tv = font_small.render(f"< {valor} >" if clave not in ("luciernagas", "avisos", "tooltips",
                                                                   "pantalla")
                                   else valor,
                                   False, RED_SIGN)
            surface.blit(tv, tv.get_rect(midright=(fila.right - 8, fila.centery + 1)))

    # Vista previa
    previa = pygame.Rect(394, 70, 212, 119)
    titulo_previa = font_small.render("ASÍ SE VE TU PULPERÍA:", False, BUTTON_BLUE_DARK)
    surface.blit(titulo_previa, (previa.x, previa.y - 14))
    draw_vista_previa(surface, previa)
    ejemplo = font_medium.render("Ejemplo: ₡12", False, WOOD_DARK)
    surface.blit(ejemplo, ejemplo.get_rect(midtop=(previa.centerx, previa.bottom + 12)))
    # Ayuda de la fila marcada.
    clave = FILAS_VISUALES[visual_seleccion][0]
    fila = pygame.Rect(40, 60 + visual_seleccion * 24, 340, 22)
    dibujar_tooltip(surface, pygame.Rect(fila.centerx, fila.y, fila.w // 2, fila.h),
                    TOOLTIP_VISUAL.get(clave, ""), "abajo", 220)


# Ayudante (Tavo): se llama con el botón de la pared derecha.
ayudante = Ayudante()
pago_ayudante = None      # ventana para pagarle (el niño calcula horas x 3)
gastos_dia = []           # (texto, monto) que se ven en el historial (H)


# ---------------------------------------------------------
# REPOSICIÓN: teléfono -> pedido -> camión -> cajas afuera
# ---------------------------------------------------------
camion = Camion()
ayudante.camion = camion
pedido_abierto = None     # menú del teléfono
menu_caja = None          # menú de una caja de afuera
def _sin_tildes(texto):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


# El pedido por teléfono va en pestañas por tipo; todo en orden alfabético.
GRUPOS_PEDIDO = sorted(
    [(nombre, sorted(kinds, key=lambda k: _sin_tildes(PRODUCTOS[k][1])))
     for nombre, kinds in (("ABARROTES", list(ABARROTES)), ("BEBIDAS", list(BEBIDAS)),
                           ("FRUTAS", list(FRUTAS)), ("HELADOS", list(HELADOS)),
                           ("HUEVOS Y LECHE", ["huevos", "leche"]),
                           ("VERDURAS", list(VERDURAS)))],
    key=lambda g: _sin_tildes(g[0]))
ORDEN_PEDIDO = tuple(k for _, kinds in GRUPOS_PEDIDO for k in kinds)


MUEBLES_DE_PRODUCTOS = ("gondola", "fridge", "abarrotes", "huevera", "heladera")


def en_muebles_tienda(items):
    """Cuántos productos de cada tipo hay acomodados en los muebles de la tienda
    (góndolas, refris, estante y huevera; el mostrador no cuenta)."""
    ids = {m["id"] for m in furniture_manager.items if m["kind"] in MUEBLES_DE_PRODUCTOS}
    cuenta = {}
    for item in items:
        if item.get("table_id") in ids and item["kind"] in PRODUCTOS:
            cuenta[item["kind"]] = cuenta.get(item["kind"], 0) + 1
    return cuenta


# Cuánto cabe en los muebles de la tienda cuando están llenos.
CAPACIDAD_TIENDA = en_muebles_tienda(TableObjectManager(furniture_manager).items)


def capacidad_total():
    """Cuánto cabe de cada producto entre los muebles de la tienda y la bodega."""
    lleno = dict(CAPACIDAD_TIENDA)
    for tipo, _, _ in stock_inicial_bodega():
        lleno[tipo] = lleno.get(tipo, 0) + 1
    return lleno


def faltan_en_bodega():
    """Cuánto espacio libre queda en la tienda y la bodega para cada producto.

    Devuelve (faltan, hay). "hay" es lo que está en la tienda y la bodega
    (también lo que va en camino en las manos, el carrito o con Tavo). Lo que
    ya está en cajas afuera también ocupa lugar, porque se va a guardar.
    """
    lleno = capacidad_total()
    hay = en_muebles_tienda(table_object_manager.items)
    en_camino = ([i for i in bodega.items] + list(ayudante.carga)
                 + [i for i in table_object_manager.mano if i.get("origen") == "bodega"])
    for item in en_camino:
        hay[item["kind"]] = hay.get(item["kind"], 0) + 1
    afuera = {k: camion.unidades_afuera(k) for k in ORDEN_PEDIDO}
    faltan = {k: max(0, lleno.get(k, 0) - hay.get(k, 0) - afuera[k]) for k in ORDEN_PEDIDO}
    return faltan, hay


def cajas_libres_acera():
    """Cuántas cajas más puede traer el camión (las que caben en la acera)."""
    return max(0, MAX_CAJAS - len(camion.cajas))


def cajas_que_caben(k, faltan=None):
    """Cuántas cajas de ese producto se pueden pedir sin que sobre nada."""
    if faltan is None:
        faltan, _ = faltan_en_bodega()
    return min(MAX_CAJAS_POR_PRODUCTO, faltan[k] // unidades_caja(k))


def pedido_sugerido():
    """Reparte las cajas entre lo que más falta, sin pasarse de lo que cabe."""
    faltan, _ = faltan_en_bodega()
    cajas = {k: 0 for k in ORDEN_PEDIDO}
    for _ in range(cajas_libres_acera()):
        candidatos = [k for k in ORDEN_PEDIDO if cajas[k] < cajas_que_caben(k, faltan)]
        if not candidatos:
            break
        k = max(candidatos, key=lambda k: faltan[k] - cajas[k] * unidades_caja(k))
        cajas[k] += 1
    return cajas


def abrir_pedido():
    global pedido_abierto
    tarde = reloj.hora >= HORA_LIMITE_PEDIDO and not camion.pendiente
    cajas = {k: 0 for k in ORDEN_PEDIDO} if (tarde or camion.pendiente) else pedido_sugerido()
    # sel: -1 = las pestañas, 0..n-1 = productos de la pestaña, n = HACER PEDIDO
    pedido_abierto = {"cajas": cajas, "grupo": 0, "sel": -1, "aviso": None, "tarde": tarde}
    sonido.efecto("timbre")


def total_pedido():
    return sum(costo_mayoreo(k) * c * unidades_caja(k) for k, c in pedido_abierto["cajas"].items())


def productos_pestana(p=None):
    p = p or pedido_abierto
    return GRUPOS_PEDIDO[p["grupo"]][1]


def manejar_tecla_pedido(event):
    global pedido_abierto
    p = pedido_abierto
    if event.key == pygame.K_ESCAPE or camion.pendiente or p.get("tarde"):
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
            pedido_abierto = None
        return
    lista = productos_pestana(p)
    n = len(lista)
    izquierda = event.key in (pygame.K_LEFT, pygame.K_a)
    derecha = event.key in (pygame.K_RIGHT, pygame.K_d)
    if event.key == pygame.K_UP:
        p["sel"] = n if p["sel"] == -1 else p["sel"] - 1
    elif event.key == pygame.K_DOWN:
        p["sel"] = -1 if p["sel"] >= n else p["sel"] + 1
    elif p["sel"] == -1 and (izquierda or derecha):
        # En las pestañas: cambiar de tipo de producto.
        p["grupo"] = (p["grupo"] + (1 if derecha else -1)) % len(GRUPOS_PEDIDO)
        p["aviso"] = None
    elif 0 <= p["sel"] < n and (izquierda or derecha):
        k = lista[p["sel"]]
        paso = 1 if derecha else -1
        nuevo = p["cajas"][k] + paso
        p["aviso"] = None
        if paso > 0 and nuevo > cajas_que_caben(k):
            # No se puede pedir una caja si en la tienda y la bodega no cabe
            # todo lo que trae.
            faltan, _ = faltan_en_bodega()
            u = unidades_caja(k)
            nombre = PRODUCTOS[k][1].lower()
            queda = faltan[k] - p["cajas"][k] * u
            lugar = "queda 1 lugar libre" if queda == 1 else f"quedan {queda} lugares libres"
            p["aviso"] = f"No cabe otra caja de {nombre}: solo {lugar}."
            sonido.efecto("error")
            return
        if paso > 0 and sum(p["cajas"].values()) >= cajas_libres_acera():
            p["aviso"] = f"El camión trae máximo {cajas_libres_acera()} cajas."
            sonido.efecto("error")
            return
        p["cajas"][k] = max(0, nuevo)
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        if p["sel"] < n:
            p["sel"] = n                       # ENTER: ir al botón de pedir
            return
        global saldo
        if total_pedido() > saldo:
            p["aviso"] = f"No te alcanza: tienes {format_colones(saldo)}."
            sonido.efecto("error")
            return
        total = camion.pedir(p["cajas"], dia, reloj.hora)
        if total <= 0:
            table_object_manager.avisar("No pediste nada.", "Elige cajas con las flechas.")
            return
        saldo -= total
        historia_hoy["camion"] = True
        gastos_dia.append(("Pedido al camión", total))
        table_object_manager.avisar("¡Pedido hecho! El camión llega",
                                    f"a las {camion.texto_llegada()} (en 2 horas).")
        sonido.efecto("acierto")
        pedido_abierto = None


def draw_pedido(surface):
    p = pedido_abierto
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 175))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(40, 10, 560, 340)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, (176, 52, 44), (46, 16, 548, 30))
    t = font_title.render("PEDIDO POR TELÉFONO", False, CREAM)
    surface.blit(t, t.get_rect(center=(320, 31)))
    mensaje = None
    if camion.pendiente:
        mensaje = ("Ya hiciste un pedido.",
                   f"El camión llega a las {camion.texto_llegada()}.",
                   "Cuando llegue, las cajas quedan afuera,",
                   "al lado izquierdo de la tienda.")
    elif p.get("tarde"):
        mensaje = ("El camión solo recibe pedidos",
                   "hasta las 2:00 p. m.",
                   "¡Llama mañana temprano!")
    if mensaje:
        for i, linea in enumerate(mensaje):
            tt = font_medium.render(linea, False, WOOD_DARK)
            surface.blit(tt, tt.get_rect(center=(320, 120 + i * 26)))
        return
    faltan, hay = faltan_en_bodega()
    lleno = capacidad_total()
    sub = font_small.render(p.get("aviso") or
                            f"Cada caja trae 3. Tienes {format_colones(saldo)}.",
                            False, (176, 48, 42) if p.get("aviso") else WOOD_DARK)
    surface.blit(sub, sub.get_rect(center=(320, 56)))
    # Pestañas por tipo de producto.
    ancho = 548 // len(GRUPOS_PEDIDO)
    for g, (nombre, kinds) in enumerate(GRUPOS_PEDIDO):
        r = pygame.Rect(46 + g * ancho + 2, 66, ancho - 4, 22)
        activa = g == p["grupo"]
        elegida = activa and p["sel"] == -1
        pedidas = sum(p["cajas"][k] for k in kinds)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT if elegida else CREAM if activa else (196, 178, 136), r)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK if elegida else WOOD_DARK, r, 2 if activa else 1)
        texto = nombre + (f" ({pedidas})" if pedidas else "")
        tt = font_small.render(texto, False, WOOD_DARK if activa else (96, 74, 60))
        surface.blit(tt, tt.get_rect(center=r.center))
    if p["sel"] == -1:
        for dx in (-1, 1):
            x = 46 + p["grupo"] * ancho + (ancho // 2) + dx * (ancho // 2 - 9)
            pygame.draw.polygon(surface, BUTTON_HIGHLIGHT_DARK,
                                [(x, 77), (x - 4 * dx, 73), (x - 4 * dx, 81)])
    for col, (texto, x) in enumerate((("PRODUCTO", 86), ("EN TIENDA", 330),
                                      ("COMPRAR", 440), ("PRECIO", 530))):
        h = font_small.render(texto, False, BUTTON_BLUE_DARK)
        surface.blit(h, h.get_rect(midleft=(x, 100)) if col == 0 else h.get_rect(center=(x, 100)))
    lista = productos_pestana(p)
    for i, k in enumerate(lista):
        r = pygame.Rect(60, 110 + i * 28, 520, 24)
        elegido = i == p["sel"]
        pygame.draw.rect(surface, CREAM if elegido else (226, 206, 158), r)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK if elegido else WOOD_DARK, r, 2 if elegido else 1)
        w, hh = tamano_producto(k)
        dibujar_producto(surface, k, r.x + 8 + (12 - w) // 2, r.y + (24 - hh) // 2)
        surface.blit(font_small.render(PRODUCTOS[k][1], False, WOOD_DARK), (r.x + 26, r.y + 6))
        te = font_small.render(f"{hay.get(k, 0)} / {lleno.get(k, 0)}", False, WOOD_DARK)
        surface.blit(te, te.get_rect(center=(330, r.centery + 1)))
        c = p["cajas"][k]
        tc = font_small.render(f"< {c} >" if elegido else str(c), False, RED_SIGN if c else WOOD_DARK)
        surface.blit(tc, tc.get_rect(center=(440, r.centery + 1)))
        tp = font_small.render(format_colones(costo_mayoreo(k) * c * unidades_caja(k)) if c else "-",
                               False, WOOD_DARK)
        surface.blit(tp, tp.get_rect(center=(530, r.centery + 1)))
    boton = pygame.Rect(130, 300, 380, 28)
    elegido = p["sel"] == len(lista)
    pygame.draw.rect(surface, BUTTON_HIGHLIGHT if elegido else BUTTON_BLUE, boton)
    pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK if elegido else BUTTON_BLUE_DARK, boton, 2)
    cajas = sum(p["cajas"].values())
    tb = font_medium.render(f"HACER PEDIDO  ·  {cajas} CAJAS  ·  {format_colones(total_pedido())}",
                            False, WOOD_DARK if elegido else CREAM)
    surface.blit(tb, tb.get_rect(center=boton.center))
    if elegido:
        dibujar_tooltip(surface, boton, "Se paga ahora y el camión llega en 2 horas. "
                        "Cada caja trae 3 productos.", "arriba", 260)


# ---------------------------------------------------------
# SALDO Y ARMARIO (ropa para el pulpero y para Canela, la gata)
# ---------------------------------------------------------
SALDO_INICIAL = 50
saldo = SALDO_INICIAL       # ventas - gastos (pedidos, Tavo) - compras del armario
mascota = Mascota()
perro = Perro()
armario = None              # menú del armario abierto: {"pestana", "sel", "aviso"}
_vista_armario = {}


def texto_mascotas():
    for texto, g, p in OPCIONES_MASCOTAS:
        if (g, p) == (MASCOTAS_ELEGIDAS["gata"], MASCOTAS_ELEGIDAS["perro"]):
            return texto
    return OPCIONES_MASCOTAS[0][0]


def aplicar_extras():
    """Pone en marcha (o apaga) las mascotas y la personalización."""
    global _fondo_menu, armario
    for k in MASCOTAS:
        MASCOTAS[k] = EXTRAS["mascotas"] and MASCOTAS_ELEGIDAS[k]
    cosmeticos.activo = EXTRAS["personalizacion"]
    zonas_mod.ARMARIO_ACTIVO = EXTRAS["personalizacion"]
    if not EXTRAS["personalizacion"]:
        armario = None
    dibujar_inventario(inventario_background)     # con o sin armario
    cosmeticos.vestir(player, mascota, perro)
    _fondo_menu = None          # el fondo del menú vuelve a dibujar a las mascotas


def cambiar_mascotas(paso):
    actual = next((i for i, (_, g, p) in enumerate(OPCIONES_MASCOTAS)
                   if (g, p) == (MASCOTAS_ELEGIDAS["gata"], MASCOTAS_ELEGIDAS["perro"])), 0)
    _, MASCOTAS_ELEGIDAS["gata"], MASCOTAS_ELEGIDAS["perro"] = \
        OPCIONES_MASCOTAS[(actual + paso) % len(OPCIONES_MASCOTAS)]
    aplicar_extras()


def cambiar_extra(clave, paso=1):
    if clave == "reporte":
        if paso > 0:
            abrir_reporte()       # ESC vuelve a EXTRAS
        return
    if clave == "cuales":
        if EXTRAS["mascotas"]:
            cambiar_mascotas(paso)
        return
    EXTRAS[clave] = not EXTRAS[clave]
    aplicar_extras()


def perro_nombre():
    return NOMBRE_PERRO.upper()


def mascota_nombre():
    from mascota import NOMBRE
    return NOMBRE.upper()


def cerca_armario():
    if not EXTRAS["personalizacion"]:
        return False            # personalización apagada: no hay armario
    r = ARMARIO_BODEGA
    cx = max(r.left, min(player.x, r.right))
    cy = max(r.top, min(player.y, r.bottom))
    return math.hypot(player.x - cx, player.y - cy) <= 22


def abrir_armario():
    global armario
    armario = {"cat": 0, "sel": 0, "aviso": None}
    sonido.efecto("abrir_caja")


def categorias_armario():
    """Las del pulpero y las de cada mascota que esté en la tienda."""
    hay = {"PULPERO": True, "GATO": MASCOTAS["gata"], "PERRO": MASCOTAS["perro"]}
    return [c for c in cosmeticos.CATEGORIAS if hay[c[0]]]


def articulos_armario():
    cats = categorias_armario()
    armario["cat"] %= len(cats)
    return cosmeticos.articulos_de(cats[armario["cat"]][2])


def manejar_tecla_armario(event):
    global armario, saldo
    a = armario
    if event.key == pygame.K_ESCAPE:
        armario = None
        return
    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
        paso = 1 if event.key in (pygame.K_RIGHT, pygame.K_d) else -1
        a["cat"] = (a["cat"] + paso) % len(categorias_armario())
        a["sel"], a["aviso"] = 0, None
        return
    lista = articulos_armario()
    if event.key == pygame.K_UP:
        a["sel"] = (a["sel"] - 1) % len(lista)
    elif event.key == pygame.K_DOWN:
        a["sel"] = (a["sel"] + 1) % len(lista)
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e, pygame.K_SPACE):
        clave, grupo, nombre, precio, _, _ = lista[a["sel"]]
        if cosmeticos.es_tuyo(clave):
            cosmeticos.alternar(clave)
            a["aviso"] = None
        elif saldo >= precio:
            saldo -= precio
            gastos_dia.append((nombre, precio))
            cosmeticos.comprados.add(clave)
            cosmeticos.puestos[grupo] = clave
            a["aviso"] = ("bien", f"¡Compraste: {nombre.lower()}!")
            sonido.efecto("cobrar")
        else:
            a["aviso"] = ("mal", "No te alcanza.")
            sonido.efecto("error")
        cosmeticos.vestir(player, mascota, perro)


def _vista_previa_armario(quien, clave):
    """Dibujo grande del pulpero o de Canela con la ropa puesta (y la elegida)."""
    llave = (quien, clave, player.skin, tuple(sorted(cosmeticos.puestos.items())))
    if llave in _vista_armario:
        return _vista_armario[llave]
    antes = dict(cosmeticos.puestos)
    if clave:
        cosmeticos.puestos[cosmeticos.articulo(clave)[1]] = clave
    s = pygame.Surface((44, 56), pygame.SRCALPHA)
    if quien == "PULPERO":
        maniqui = Player(x=0, y=0, skin=player.skin)
        cosmeticos.vestir(maniqui)
        sprite = maniqui.frames["down"][0]
        rect = sprite.get_rect(midbottom=(22, 54))
        s.blit(sprite, rect)
        cosmeticos.dibujar_accesorios(s, maniqui, rect)
    elif quien == "PERRO":
        bruno = Perro()
        cosmeticos.vestir(Player(x=0, y=0, skin=player.skin), None, bruno)
        img = bruno._imagen(0)
        s.blit(img, img.get_rect(midbottom=(22, 52)))
    else:
        gata = Mascota()
        cosmeticos.vestir(Player(x=0, y=0, skin=player.skin), gata)
        gata.x, gata.y = 22, 52
        gata.dibujar(s, "interior")
    cosmeticos.puestos.clear()
    cosmeticos.puestos.update(antes)
    _vista_armario.clear()
    _vista_armario[llave] = pygame.transform.scale_by(s, 3)
    return _vista_armario[llave]


COLOR_ESTILO = {cosmeticos.NORMAL: (84, 104, 120), cosmeticos.LLAMATIVO: (200, 60, 150),
                cosmeticos.LUJO: (176, 128, 20)}


def _color_de(valor):
    """El color de un artículo (para la muestrita de la lista), si tiene."""
    if isinstance(valor, tuple):
        if len(valor) == 3 and all(isinstance(v, int) for v in valor):
            return valor
        for v in valor:
            c = _color_de(v)
            if c:
                return c
    return None


def draw_armario(surface):
    a = armario
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 175))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(40, 10, 560, 340)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, (120, 78, 52), (46, 16, 548, 30))
    t = font_title.render("ARMARIO", False, CREAM)
    surface.blit(t, t.get_rect(midleft=(60, 31)))
    # Saldo con monedita
    moneda = font_large.render(format_colones(saldo), False, (250, 220, 110) if saldo >= 0 else (240, 120, 110))
    caja = moneda.get_rect().inflate(30, 4)
    caja.midright = (588, 31)
    pygame.draw.rect(surface, (35, 27, 27), caja)
    pygame.draw.circle(surface, (240, 196, 60), (caja.x + 11, caja.centery), 7)
    pygame.draw.circle(surface, (176, 128, 30), (caja.x + 11, caja.centery), 7, 1)
    surface.blit(moneda, moneda.get_rect(midright=(caja.right - 6, caja.centery + 1)))
    # Arriba: para quién (pulpero, Canela, Bruno); abajo, sus categorías.
    quien_txt = {"PULPERO": "PULPERA" if player.skin == "mujer" else "PULPERO",
                 "GATO": "CANELA (GATA)", "PERRO": "BRUNO (PERRO)"}
    cats = categorias_armario()
    lista = articulos_armario()
    actual = cats[a["cat"]][0]
    quienes = list(dict.fromkeys(c[0] for c in cats))
    ancho_q = 548 // len(quienes)
    for i, quien in enumerate(quienes):
        r = pygame.Rect(46 + i * ancho_q + 2, 50, ancho_q - 4, 14)
        activa = quien == actual
        pygame.draw.rect(surface, (120, 78, 52) if activa else (196, 178, 136), r)
        tq = font_small.render(quien_txt[quien], False, CREAM if activa else WOOD_DARK)
        surface.blit(tq, tq.get_rect(center=r.center))
    mias = [(i, c) for i, c in enumerate(cats) if c[0] == actual]
    ancho = min(110, 548 // len(mias))
    x_ini = 320 - ancho * len(mias) // 2
    for j, (i, (quien, nombre, _)) in enumerate(mias):
        r = pygame.Rect(x_ini + j * ancho + 2, 66, ancho - 4, 20)
        activa = i == a["cat"]
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT if activa else (196, 178, 136), r)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK if activa else WOOD_DARK, r, 2 if activa else 1)
        tt = font_small.render(nombre, False, WOOD_DARK)
        if tt.get_width() > r.w - 4:
            tt = pygame.transform.scale(tt, (r.w - 4, tt.get_height()))
        surface.blit(tt, tt.get_rect(center=r.center))
    # Lista con desplazamiento: la selección baja hasta el último visible
    # y luego la lista se corre.
    visibles = 9
    desde = min(a.get("desde", 0), max(0, len(lista) - visibles))
    if a["sel"] < desde:
        desde = a["sel"]
    elif a["sel"] >= desde + visibles:
        desde = a["sel"] - visibles + 1
    a["desde"] = desde
    # Flechitas a la izquierda de la lista: hay más arriba / más abajo.
    if desde > 0:
        pygame.draw.polygon(surface, WOOD_DARK, [(46, 98), (54, 98), (50, 92)])
    if desde + visibles < len(lista):
        pygame.draw.polygon(surface, WOOD_DARK, [(46, 296), (54, 296), (50, 302)])
    for i, (clave, grupo, nombre, precio, valor, estilo) in enumerate(lista):
        if not desde <= i < desde + visibles:
            continue
        r = pygame.Rect(56, 90 + (i - desde) * 24, 330, 22)
        elegido = i == a["sel"]
        pygame.draw.rect(surface, CREAM if elegido else (226, 206, 158), r)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK if elegido else WOOD_DARK, r, 2 if elegido else 1)
        muestra = _color_de(valor)
        if muestra:
            pygame.draw.rect(surface, muestra, (r.x + 6, r.y + 5, 12, 12))
            pygame.draw.rect(surface, WOOD_DARK, (r.x + 6, r.y + 5, 12, 12), 1)
        surface.blit(font_small.render(nombre, False, WOOD_DARK), (r.x + 24, r.y + 4))
        te = font_small.render(estilo, False, COLOR_ESTILO[estilo])
        surface.blit(te, te.get_rect(midleft=(r.x + 196, r.centery + 1)))
        if cosmeticos.puestos.get(grupo) == clave:
            estado, color = "PUESTO", (66, 130, 70)
        elif cosmeticos.es_tuyo(clave):
            estado, color = "TUYO", BUTTON_BLUE_DARK
        else:
            estado, color = format_colones(precio), RED_SIGN
        tv = font_small.render(estado, False, color)
        surface.blit(tv, tv.get_rect(midright=(r.right - 8, r.centery + 1)))
    # Probador: cómo se ve con lo elegido puesto
    marco = pygame.Rect(398, 90, 186, 214)
    pygame.draw.rect(surface, (214, 196, 160), marco)
    pygame.draw.rect(surface, WOOD_DARK, marco, 2)
    img = _vista_previa_armario(actual, lista[a["sel"]][0])
    surface.blit(img, img.get_rect(midbottom=(marco.centerx, marco.bottom - 8)))
    if a.get("aviso"):
        tipo, texto = a["aviso"]
        tv = font_medium.render(texto, False, (66, 115, 67) if tipo == "bien" else (176, 48, 42))
        surface.blit(tv, tv.get_rect(center=(320, 330)))


# Casa de Canela (caja de cartón que se mejora)
casa_gato = CasaGato()
casa_menu = None            # ventana "CASA DE CANELA" abierta


def abrir_casa_menu():
    global casa_menu
    casa_menu = {"aviso": None}


def manejar_tecla_casa(event):
    global casa_menu, saldo
    if event.key == pygame.K_ESCAPE:
        casa_menu = None
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e, pygame.K_SPACE):
        sig = casa_gato.siguiente
        if sig is None:
            casa_menu = None
            return
        nombre, precio = sig
        if saldo >= precio:
            saldo -= precio
            gastos_dia.append((f"Casa de Canela: {nombre.lower()}", precio))
            casa_gato.nivel += 1
            casa_menu["aviso"] = ("bien", f"¡Canela tiene {nombre.lower()}!")
            sonido.efecto("logro")
        else:
            casa_menu["aviso"] = ("mal", "No te alcanza.")
            sonido.efecto("error")


def draw_casa_menu(surface):
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 175))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(90, 40, 460, 270)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, (120, 78, 52), (96, 46, 448, 32))
    t = font_title.render("CASA DE CANELA", False, CREAM)
    surface.blit(t, t.get_rect(center=(320, 62)))

    def tarjeta(nivel, centro, titulo):
        marco = pygame.Rect(0, 0, 170, 150)
        marco.center = centro
        pygame.draw.rect(surface, (214, 196, 160), marco)
        pygame.draw.rect(surface, WOOD_DARK, marco, 2)
        s = pygame.Surface((72, 64), pygame.SRCALPHA)
        dibujar_casa(s, nivel, 4, 60)
        img = pygame.transform.scale_by(s, 2)
        surface.blit(img, img.get_rect(midbottom=(marco.centerx, marco.bottom - 22)))
        tn = font_small.render(NIVELES_CASA[nivel][0], False, WOOD_DARK)
        surface.blit(tn, tn.get_rect(midbottom=(marco.centerx, marco.bottom - 6)))
        tt = font_small.render(titulo, False, BUTTON_BLUE_DARK)
        surface.blit(tt, tt.get_rect(midbottom=(marco.centerx, marco.top - 3)))

    sig = casa_gato.siguiente
    if sig is None:
        tarjeta(casa_gato.nivel, (320, 172), "")
        tf = font_medium.render("¡Ya tiene la mejor casa!", False, (66, 115, 67))
        surface.blit(tf, tf.get_rect(center=(320, 268)))
    else:
        tarjeta(casa_gato.nivel, (200, 172), "AHORA")
        tarjeta(casa_gato.nivel + 1, (440, 172), "MEJORA")
        flecha = font_title.render(">", False, WOOD_DARK)
        surface.blit(flecha, flecha.get_rect(center=(320, 172)))
        boton = pygame.Rect(0, 0, 200, 28)
        boton.center = (440, 270)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK, boton.move(0, 3))
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT, boton)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK, boton, 2)
        tb = font_medium.render(f"MEJORAR  {format_colones(sig[1])}", False, WOOD_DARK)
        surface.blit(tb, tb.get_rect(center=boton.center))
        pygame.draw.circle(surface, (240, 196, 60), (130, 270), 7)
        pygame.draw.circle(surface, (176, 128, 30), (130, 270), 7, 1)
        ts = font_large.render(format_colones(saldo), False, (54, 96, 65) if saldo >= 0 else (159, 60, 47))
        surface.blit(ts, ts.get_rect(midleft=(142, 271)))
    if casa_menu.get("aviso"):
        tipo, texto = casa_menu["aviso"]
        tv = font_medium.render(texto, False, (66, 115, 67) if tipo == "bien" else (176, 48, 42))
        surface.blit(tv, tv.get_rect(center=(320, 296)))


def abrir_menu_caja(caja):
    global menu_caja
    menu_caja = {"caja": caja, "sel": 0}


def opciones_caja():
    caja = menu_caja["caja"]
    nombre = PRODUCTOS[caja.kind][0].lower()
    return [f"TOMAR 1 ({nombre})", "LLENAR LAS MANOS", "CERRAR"]


def tomar_de_caja(caja, cantidad):
    tom = table_object_manager
    tomados = 0
    while tomados < cantidad and len(tom.mano) < tom.MAX_MANOS and caja.unidades > 0:
        camion.sacar(caja, 1)
        kind = caja.kind
        w, h = tamano_producto(kind)
        nuevo = {"id": f"caja_{id(caja)}_{caja.unidades}_{len(tom.items)}", "label": PRODUCTOS[kind][0],
                 "kind": kind, "table_id": "mano", "rel_x": 0, "rel_y": 0, "w": w, "h": h,
                 "color": (224, 210, 168), "price": PRODUCTOS[kind][2], "origen": "bodega"}
        tom.items.append(nuevo)
        tom.mano.append(nuevo)
        tomados += 1
    if tomados == 0 and len(tom.mano) >= tom.MAX_MANOS:
        tom.avisar(*tom.mensaje_manos_llenas("a la tienda"))
    return tomados


def manejar_tecla_caja(event):
    global menu_caja
    opciones = opciones_caja()
    if event.key == pygame.K_ESCAPE:
        menu_caja = None
    elif event.key in (pygame.K_UP, pygame.K_w):
        menu_caja["sel"] = (menu_caja["sel"] - 1) % len(opciones)
    elif event.key in (pygame.K_DOWN, pygame.K_s):
        menu_caja["sel"] = (menu_caja["sel"] + 1) % len(opciones)
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e, pygame.K_SPACE):
        caja = menu_caja["caja"]
        if menu_caja["sel"] == 0:
            tomar_de_caja(caja, 1)
        elif menu_caja["sel"] == 1:
            tomar_de_caja(caja, table_object_manager.MAX_MANOS)
        if menu_caja["sel"] == 2 or caja not in camion.cajas or \
                len(table_object_manager.mano) >= table_object_manager.MAX_MANOS:
            menu_caja = None


def draw_menu_caja(surface):
    caja = menu_caja["caja"]
    opciones = opciones_caja()
    ancho = max(font_small.size(o)[0] for o in opciones) + 34
    alto = 26 + len(opciones) * 18
    r = pygame.Rect(0, 0, ancho, alto)
    r.midbottom = (caja.x, caja.y - 22)
    r.clamp_ip(pygame.Rect(4, 4, GAME_WIDTH - 8, GAME_HEIGHT - 8))
    pygame.draw.rect(surface, (35, 27, 27), r.move(2, 2))
    pygame.draw.rect(surface, CREAM, r)
    pygame.draw.rect(surface, WOOD_DARK, r, 2)
    titulo = font_small.render(f"CAJA: {caja.unidades} {PRODUCTOS[caja.kind][1].lower()}", False, RED_SIGN)
    surface.blit(titulo, (r.x + 8, r.y + 5))
    for i, o in enumerate(opciones):
        y = r.y + 22 + i * 18
        if i == menu_caja["sel"]:
            pygame.draw.rect(surface, BUTTON_HIGHLIGHT, (r.x + 4, y - 1, r.w - 8, 17))
        surface.blit(font_small.render(o, False, WOOD_DARK), (r.x + 14, y + 2))


def pies_de_personajes():
    """Quiénes no pueden quedar debajo de un mueble (para SHIFT+E)."""
    def pies(x, y, ancho=18):
        return pygame.Rect(round(x) - ancho // 2, round(y) - 6, ancho, 8)
    lista = [("jugador", pies(player.x, player.y))]
    for i, c in enumerate(clientes.lista):
        lista.append((f"cliente_{id(c)}", pies(c.persona.x, c.persona.y)))
    if ayudante.presente:
        lista.append(("ayudante", pies(ayudante.x, ayudante.y)))
    if carrito.escena == "interior":
        lista.append(("carrito", pies(carrito.x, carrito.y, 24)))
    return lista


furniture_manager.personajes = pies_de_personajes


def cerca_de_ayudante():
    return (ayudante.esperando_pago
            and math.hypot(player.x - ayudante.x, player.y - ayudante.y) <= 40)


def abrir_pago_ayudante():
    global pago_ayudante
    pago_ayudante = {"valor": "", "errores": 0, "listo": False,
                     "mensaje": "Escribe cuánto le pagas y pulsa ENTER."}


def revisar_pago_ayudante():
    v = pago_ayudante
    if not v["valor"]:
        v["mensaje"] = "Primero escribe un número."
        return
    esperado = ayudante.pago
    h, e, t = ayudante.horas, ayudante.extras, ayudante.tarifa_extra
    if int(v["valor"]) == esperado:
        v["listo"] = True
        cuenta = f"{h} x {PAGO_POR_HORA}" + (f" + {e} x {t}" if e else "")
        v["mensaje"] = f"¡Correcto! {cuenta} = {esperado}. ENTER: continuar."
        return
    v["errores"] += 1
    sonido.efecto("error")
    if e:
        # Con horas extra: dos multiplicaciones y una suma.
        if v["errores"] == 1:
            v["mensaje"] = "Mmm... no es eso. Calcula las horas normales y las extra, y suma."
        elif v["errores"] == 2:
            v["mensaje"] = f"Pista: horas normales: {h} x {PAGO_POR_HORA} = {h * PAGO_POR_HORA}. ¿Y las extra?"
        else:
            v["mensaje"] = (f"Pista: {h * PAGO_POR_HORA} + {e} x {t} = "
                            f"{h * PAGO_POR_HORA} + {e * t}.")
        v["valor"] = ""
        return
    if v["errores"] == 1:
        v["mensaje"] = "Mmm... no es eso. Son 3 colones por cada hora."
    elif v["errores"] == 2:
        v["mensaje"] = "Pista: suma 3 una vez por cada hora: " + " + ".join(["3"] * h) + "."
    else:
        pasos = ", ".join(str(PAGO_POR_HORA * k) for k in range(1, h + 1))
        v["mensaje"] = f"Pista: cuenta de 3 en 3, {h} veces: {pasos}."
    v["valor"] = ""


def manejar_tecla_pago(event):
    global pago_ayudante
    v = pago_ayudante
    if event.key == pygame.K_ESCAPE:
        pago_ayudante = None          # cerrar sin pagar: Tavo sigue esperando
    elif v["listo"]:
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            extra = f" + {ayudante.extras} extra" if ayudante.extras else ""
            gastos_dia.append((f"Pago a {ayudante.nombre} ({ayudante.horas} h{extra})", ayudante.pago))
            global saldo
            saldo -= ayudante.pago
            ayudante.pagado()
            pago_ayudante = None
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        revisar_pago_ayudante()
    elif event.key == pygame.K_BACKSPACE:
        v["valor"] = v["valor"][:-1]
    elif event.unicode and event.unicode.isdigit() and len(v["valor"]) < 3:
        v["valor"] += event.unicode


def draw_pago_ayudante(surface):
    v = pago_ayudante
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 170))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(110, 70, 420, 220)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, (62, 120, 80), (116, 76, 408, 34))
    t = font_title.render(f"PAGARLE A {ayudante.nombre.upper()}", False, CREAM)
    surface.blit(t, t.get_rect(center=(320, 93)))
    palabra = "hora" if ayudante.horas == 1 else "horas"
    if ayudante.extras:
        extra = "hora extra" if ayudante.extras == 1 else "horas extra"
        lineas = (f"Hoy trabajé {ayudante.horas} {palabra} a {PAGO_POR_HORA} colones",
                  f"y {ayudante.extras} {extra} a {ayudante.tarifa_extra} colones.",
                  "¿Cuánto me pagas?")
    else:
        lineas = (f"Hoy trabajé {ayudante.horas} {palabra}.",
                  f"Cobro {PAGO_POR_HORA} colones por hora.",
                  "¿Cuánto me pagas?")
    for i, linea in enumerate(lineas):
        tt = font_medium.render(linea, False, WOOD_DARK)
        surface.blit(tt, tt.get_rect(center=(320, 128 + i * 22)))
    caja = pygame.Rect(0, 0, 130, 32)
    caja.center = (320, 214)
    pygame.draw.rect(surface, (255, 247, 220), caja)
    pygame.draw.rect(surface, (66, 115, 67) if v["listo"] else BUTTON_HIGHLIGHT_DARK, caja, 3)
    valor = format_colones(int(v["valor"])) if v["valor"] else "_"
    tv = font_large.render(valor, False, WOOD_DARK)
    surface.blit(tv, tv.get_rect(center=caja.center))
    color = (66, 115, 67) if v["listo"] or v["mensaje"].startswith("Pista") else (159, 60, 47) if v["errores"] else WOOD_DARK
    tm_ = font_small.render(v["mensaje"], False, color)
    surface.blit(tm_, tm_.get_rect(center=(320, 248)))


# Unas pocas luciérnagas que vuelan dentro de la tienda...
luciernagas = Luciernagas()
# ...y afuera, entre los árboles y la acera, solo de noche.
luciernagas_calle = Luciernagas(cantidad=7, zona=pygame.Rect(20, 120, 600, 118), solo_de_noche=True)


HORA_LUCIERNAGAS = 15.0     # las luciérnagas salen después de las 3:00 p. m.


def oscuridad():
    """0 de día, 1 de noche (amanecer y atardecer en medio)."""
    h = reloj.hora
    return max(0.0, min(1.0, max((h - 17.4) / 1.2, (7.2 - h) / 0.7)))


# Carrito de compras (hasta 8 productos) para llenar la tienda desde la bodega.
carrito = Carrito("interior", 600.0, 300.0)
ayudante.carrito = carrito    # Tavo lo usa cuando el pulpero no lo empuja


def muebles_para_carrito():
    """Rectángulos completos de los muebles de la sala (el carrito no entra)."""
    return [pygame.Rect(round(m["x"]), round(m["y"]), m["w"], m["h"])
            for m in furniture_manager.items if not m.get("fijo")]


def alternar_carrito():
    """ESPACIO: agarrar el carrito si está cerca, o soltarlo si se empuja."""
    if carrito.empujando:
        carrito.soltar(table_object_manager)
        return True
    if carrito.cerca_ayudante(player, current_scene):
        # Tavo lo está usando: te lo presta (se queda con 3 en las manos).
        ayudante.prestar_carrito(bodega)
        return carrito.agarrar(player, table_object_manager)
    if carrito.cerca(player, current_scene):
        return carrito.agarrar(player, table_object_manager)
    return False


def abrir_menu_tomar(origen, mueble=None):
    global menu_tomar
    vista = VistaMueble(origen, mueble, table_object_manager, bodega, player)
    # Se abrió con E: el cursor del teclado empieza visible.
    vista.usando_teclado = True
    menu_tomar = vista if vista.productos() else None


def despues_de_tomar():
    """Cierra la vista cuando ya no caben más productos o no quedan."""
    global menu_tomar
    tom = table_object_manager
    if len(tom.mano) >= tom.MAX_MANOS:
        destino = "a la tienda" if menu_tomar.origen == "bodega" else "al mostrador"
        donde = "en el carrito" if tom.en_carrito else ""
        tom.avisar(f"¡Listo! Ya llevas {tom.MAX_MANOS} productos {donde}".strip() + ".",
                   f"Llévalos {destino}.")
        menu_tomar = None
    elif not menu_tomar.productos():
        menu_tomar = None


def manejar_tecla_menu_tomar(event):
    global menu_tomar
    vista = menu_tomar
    if event.key in (pygame.K_ESCAPE, pygame.K_q):
        menu_tomar = None
    elif event.key in (pygame.K_LEFT, pygame.K_a):
        vista.mover(-1, 0)
    elif event.key in (pygame.K_RIGHT, pygame.K_d):
        vista.mover(1, 0)
    elif event.key in (pygame.K_UP, pygame.K_w):
        vista.mover(0, -1)
    elif event.key in (pygame.K_DOWN, pygame.K_s):
        vista.mover(0, 1)
    elif event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
        if vista.usando_teclado:
            vista.tomar_seleccionado()
            despues_de_tomar()
        else:
            # Primera tecla: mostrar el cursor antes de tomar.
            vista.mover(0, 0)


def clic_menu_tomar(pos):
    global menu_tomar
    vista = menu_tomar
    item = vista.item_en(pos)
    if item is not None:
        vista.tomar(item)
        despues_de_tomar()
    elif not pygame.Rect(80, 50, 1120, 620).collidepoint(pos):
        menu_tomar = None  # Clic afuera del panel: cerrar


def draw_menu_tomar(surface):
    """La vista se dibuja directo en la ventana (ver draw)."""
    return


# Jornada laboral: montos de cada venta (sin total: lo suma el niño al
# final del día en el "CIERRE DE CAJA").
dia = 1
ventas_dia = []
venta_reciente = None     # (monto, milisegundos) para la animación "+₡21"
cierre = None             # estado del cierre de caja cuando está abierto
reloj = Reloj()           # ciclo de día y noche (ver horario.py)
calle = Calle()           # gente, autos y animales en la calle (ver ambiente.py)


def nueva_partida_completa():
    """JUGAR: partida nueva DE CERO. Tienda, bodega, muebles, carrito,
    camión, Tavo, Canela, saldo, ropa y día vuelven a como al principio.
    (Los ajustes de OPCIONES se conservan.)"""
    global venta_reciente, menu_tomar, pedido_abierto, menu_caja, casa_menu, pago_ayudante
    global historial_abierto, checkout_open, checkout_exercise, checkout_receipt_total
    global nivel_actual, historia_nivel_base, historia_activa, dialogo
    # Si una historia anterior había subido la dificultad, vuelve la de OPCIONES.
    if historia_nivel_base is not None:
        nivel_actual = historia_nivel_base
        historia_nivel_base = None
    historia_activa = False
    dialogo = None
    global nombre_tienda, cartel_edit
    nombre_tienda, cartel_edit = "", None
    redibujar_entrada()
    historia_hoy["camion"] = False
    historia_hoy["felicitado"] = False
    clientes.esperando_jugador = False
    estadisticas.reiniciar()           # el reporte empieza de cero
    furniture_manager.items = FurnitureManager().items
    furniture_manager.selected = None
    tom = table_object_manager
    tom.items = TableObjectManager(furniture_manager).items
    tom.mano = []
    tom.selected = None
    tom.en_carrito = False
    tom.MAX_MANOS = type(tom).MAX_MANOS
    tom.aviso = None
    bodega.__init__()
    carrito.__init__("interior", 600.0, 300.0)
    player.empujando_carrito = False
    clientes.dia = 1
    clientes.reiniciar()
    clientes.paciencia_activa = MODO["paciencia"]
    nueva_partida_jornada()
    menu_tomar = pedido_abierto = menu_caja = casa_menu = pago_ayudante = None
    historial_abierto = False
    checkout_open, checkout_exercise, checkout_receipt_total = False, None, None
    venta_reciente = None


# Confirmación antes de empezar de cero (si ya hay una partida guardada).
confirmar_nueva = None      # {"sel": 0 = SÍ / 1 = NO, "tutorial": bool}


def modo_elegido():
    """El modo de la partida NUEVA que se está creando."""
    return "historia" if historia_elegida else "libre"


def hay_partida(modo=None):
    """¿Ya hay una partida de ese modo (la nueva la reemplazaría)?"""
    return resumen_partida(modo or modo_elegido()) is not None


elegir_continuar = None     # CONTINUAR con dos partidas: {"sel", "modos"}


def abrir_continuar():
    """CONTINUAR: si hay partida de un solo modo, sigue con esa; si hay de
    los dos, pregunta cuál."""
    global elegir_continuar
    disp = partidas_disponibles()
    if len(disp) == 1:
        continuar_modo(disp[0])
    elif disp:
        actual = modo_partida() if partida_en_juego() else ultimo_modo
        elegir_continuar = {"sel": disp.index(actual) if actual in disp else 0, "modos": disp}


def manejar_tecla_elegir_continuar(event):
    global elegir_continuar
    c = elegir_continuar
    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d,
                     pygame.K_UP, pygame.K_DOWN):
        c["sel"] = (c["sel"] + 1) % len(c["modos"])
    elif event.key == pygame.K_ESCAPE:
        elegir_continuar = None
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
        elegir_continuar = None
        continuar_modo(c["modos"][c["sel"]])


def draw_elegir_continuar(surface):
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 185))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(110, 90, 420, 170)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (116, 96, 408, 34))
    t = font_title.render("¿CUÁL PARTIDA?", False, CREAM)
    surface.blit(t, t.get_rect(center=(320, 113)))
    for k, modo in enumerate(elegir_continuar["modos"]):
        r = pygame.Rect(0, 0, 170, 64)
        r.center = (225 if k == 0 else 415, 190)
        res = resumen_partida(modo)
        sub = f"{res[0]} - día {res[1]}" if res else ""
        _boton_pregunta(surface, r, NOMBRE_MODO[modo], elegir_continuar["sel"] == k,
                        _ajustar_texto(sub, font_small, r.w - 10))


def _ajustar_texto(texto, fuente, ancho):
    """Corta el texto con "..." si no cabe en ese ancho."""
    if fuente.size(texto)[0] <= ancho:
        return texto
    while texto and fuente.size(texto + "...")[0] > ancho:
        texto = texto[:-1]
    return texto + "..."


def pedir_partida_nueva(con_tutorial=False):
    """JUGAR: primero HISTORIA o LIBRE. TUTORIAL va directo. Si hay una
    partida guardada, después pregunta si se borra."""
    global elegir_modo, historia_elegida
    if con_tutorial:
        historia_elegida = False
        _pedir_confirmacion(True)
    else:
        elegir_modo = {"sel": 0}


def _pedir_confirmacion(con_tutorial):
    global confirmar_nueva
    if hay_partida():
        confirmar_nueva = {"sel": 1, "tutorial": con_tutorial}
    else:
        empezar_flujo_nueva(con_tutorial)


# ---------------------------------------------------------
# MODO HISTORIA (textos y metas en historia.py)
# ---------------------------------------------------------
elegir_modo = None          # pregunta de JUGAR: {"sel": 0 = HISTORIA / 1 = LIBRE}
historia_elegida = False    # lo que se eligió (se aplica al crear la partida)
historia_activa = False     # la partida actual es de MODO HISTORIA
historia_nivel_base = None  # dificultad de OPCIONES antes de que la historia la subiera
historia_hoy = {"camion": False, "felicitado": False}   # camión pedido / ya felicitó
dialogo = None              # Doña Rosa hablando: {"paginas", "i", "despues"}
_retrato = {}


def hay_recetas():
    return bool(MODO.get("fracciones") or MODO.get("multiplicar"))


def stats_hoy():
    return {"atendidos": clientes.atendidos, "perdidos": clientes.perdidos,
            "ventas": sum(ventas_dia), "camion": historia_hoy["camion"],
            "tavo": ayudante.trabajo_hoy, "recetas": getattr(clientes, "recetas_hoy", 0)}


def meta_hoy():
    return historia.meta(dia, hay_recetas())


def abrir_dialogo(paginas, despues=None):
    global dialogo
    dialogo = {"paginas": paginas, "i": 0, "despues": despues}


def abrir_saludo(nivel_nuevo=None):
    """Saludo de Doña Rosa al empezar el día (el día 1, la bienvenida)."""
    compania = (mascota_nombre().title() if MASCOTAS["gata"]
                else perro_nombre().title() if MASCOTAS["perro"] else "")
    abrir_dialogo(historia.paginas_saludo(dia, nombre_bonito(), hay_recetas(),
                                          compania, nivel_nuevo))


def revisar_meta():
    """Apenas se cumple la meta, Doña Rosa felicita (una vez por día)."""
    if (not historia_activa or tutorial.activo or historia_hoy["felicitado"]
            or dialogo is not None or cartel_edit is not None or cierre is not None or checkout_open
            or menu_tomar is not None or pedido_abierto is not None or pago_ayudante is not None
            or recetario.abierto or armario is not None or casa_menu is not None
            or menu_caja is not None or pausa is not None
            or current_scene not in ("interior", "entrada", "inventario")):
        return
    m = meta_hoy()
    if m[0] in historia.SOLO_AL_FINAL:
        return
    if historia.progreso(m, stats_hoy())[2]:
        historia_hoy["felicitado"] = True
        abrir_dialogo(historia.paginas_felicitacion(nombre_bonito()))
        sonido.efecto("logro")


def terminar_dia():
    """Botón "DÍA N >" del cierre. En la historia, primero la despedida."""
    if historia_activa and not tutorial.activo:
        cumplida = historia.progreso(meta_hoy(), stats_hoy())[2]
        abrir_dialogo(historia.paginas_despedida(dia, nombre_bonito(), cumplida),
                      despues="siguiente_dia")
        sonido.efecto("logro" if cumplida else "campanita")
    else:
        siguiente_dia()


def abrir_bienvenida(con_historia):
    """Partida nueva: Doña Rosa saluda y pregunta qué mascotas quieres."""
    actual = (MASCOTAS_ELEGIDAS["gata"], MASCOTAS_ELEGIDAS["perro"]) if EXTRAS["mascotas"] else (False, False)
    sel = next((i for i, (_, g, p) in enumerate(historia.OPCIONES_MASCOTAS) if (g, p) == actual), 1)
    abrir_dialogo(historia.paginas_inicio(nombre_bonito()))
    dialogo["mascota_sel"] = sel
    dialogo["con_historia"] = con_historia


def elegir_mascotas_dialogo():
    """Aplica la elección de mascotas y agrega lo que sigue del diálogo."""
    _, gata, perro_si = historia.OPCIONES_MASCOTAS[dialogo["mascota_sel"]]
    EXTRAS["mascotas"] = gata or perro_si
    if gata or perro_si:
        MASCOTAS_ELEGIDAS["gata"], MASCOTAS_ELEGIDAS["perro"] = gata, perro_si
    aplicar_extras()
    dialogo["paginas"] += historia.paginas_despues_de_elegir(
        gata, perro_si, dialogo.get("con_historia", False), hay_recetas())
    sonido.efecto("acierto")
    # Después de las mascotas: el nombre del cartel de la pulpería.
    abrir_cartel(rosa=True)


# ---------------------------------------------------------
# NOMBRE DEL CARTEL: el niño escribe cómo se llama su pulpería (hasta 20
# letras). Historia: después de escoger las mascotas. Libre: al empezar.
# ---------------------------------------------------------
cartel_edit = None          # {"texto": lo escrito, "rosa": Doña Rosa sigue hablando}
CARTEL_SIGNOS = " -.!'&"     # además de letras y números


def abrir_cartel(rosa=False):
    global cartel_edit
    cartel_edit = {"texto": nombre_tienda, "rosa": rosa}


def manejar_cartel(event):
    """Escribir el nombre: letras, números y espacios; BORRAR; ENTER: listo."""
    c = cartel_edit
    if event.type == pygame.TEXTINPUT:
        for letra in event.text:
            if len(c["texto"]) >= zonas_mod.CARTEL_MAX:
                break
            if not (letra.isalnum() or letra in CARTEL_SIGNOS):
                continue
            if letra == " " and (not c["texto"] or c["texto"].endswith(" ")):
                continue
            c["texto"] += letra
        return
    if event.key == pygame.K_BACKSPACE:
        c["texto"] = c["texto"][:-1]
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
        confirmar_cartel()


def confirmar_cartel():
    global cartel_edit, nombre_tienda
    c = cartel_edit
    cartel_edit = None
    nombre_tienda = " ".join(c["texto"].split())[:zonas_mod.CARTEL_MAX]
    redibujar_entrada()
    sonido.efecto("acierto")
    if c["rosa"] and dialogo is not None:
        dialogo["paginas"].insert(dialogo["i"], (
            "¡Qué bonito nombre!",
            f"Tu pulpería se llama {texto_cartel()}.", None))
    guardar_partida()


def texto_cartel():
    return " ".join((nombre_tienda or zonas_mod.NOMBRE_CARTEL).upper().split())


def draw_cartel_edit(surface):
    """¿Cómo se llama tu pulpería? El cartel se ve en grande mientras escribe."""
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 175))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(40, 26, 560, 228)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (panel.x + 6, panel.y + 6, panel.w - 12, 34))
    t = font_title.render("¿CÓMO SE LLAMA TU PULPERÍA?", False, CREAM)
    surface.blit(t, t.get_rect(center=(panel.centerx, panel.y + 23)))
    # El cartel tal como va a quedar, al doble de tamaño.
    texto = cartel_edit["texto"]
    muestra = pygame.Surface((256, 46))
    muestra.fill((132, 179, 217))
    pygame.draw.polygon(muestra, (178, 70, 58), [(0, 46), (128, 20), (256, 46)])
    zonas_mod.dibujar_cartel(muestra, texto or None, cx=128, abajo=40)
    grande = pygame.transform.scale(muestra, (512, 92))
    caja_m = grande.get_rect(midtop=(panel.centerx, panel.y + 48))
    surface.blit(grande, caja_m)
    pygame.draw.rect(surface, WOOD_DARK, caja_m, 2)
    # Casilla de texto con el cursor y cuántas letras lleva.
    casilla = pygame.Rect(0, 0, 360, 26)
    casilla.midtop = (panel.centerx, caja_m.bottom + 10)
    pygame.draw.rect(surface, CREAM, casilla)
    pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK, casilla, 2)
    tt = font_medium.render(texto.upper(), False, WOOD_DARK)
    surface.blit(tt, tt.get_rect(midleft=(casilla.x + 8, casilla.centery + 1)))
    if (pygame.time.get_ticks() // 450) % 2 == 0 and len(texto) < zonas_mod.CARTEL_MAX:
        cx = casilla.x + 10 + tt.get_width()
        pygame.draw.rect(surface, WOOD_DARK, (cx, casilla.y + 5, 2, casilla.h - 10))
    cuenta = font_small.render(f"{len(texto)}/{zonas_mod.CARTEL_MAX}", False, BUTTON_BLUE_DARK)
    surface.blit(cuenta, cuenta.get_rect(midleft=(casilla.right + 8, casilla.centery + 1)))
    pie = font_small.render("Escribe el nombre y pulsa ENTER", False, BUTTON_BLUE_DARK)
    surface.blit(pie, pie.get_rect(center=(panel.centerx, panel.bottom - 16)))


def manejar_tecla_dialogo(event):
    """ENTER / ESPACIO / E: siguiente página. ESC: termina el diálogo."""
    global dialogo
    pagina = dialogo["paginas"][dialogo["i"]]
    if pagina[2] == "elegir_mascotas":
        # Doña Rosa pregunta: flechas para elegir, ENTER para aceptar.
        n = len(historia.OPCIONES_MASCOTAS)
        if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP):
            dialogo["mascota_sel"] = (dialogo["mascota_sel"] - 1) % n
        elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN):
            dialogo["mascota_sel"] = (dialogo["mascota_sel"] + 1) % n
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_e,
                           pygame.K_ESCAPE):
            elegir_mascotas_dialogo()
            dialogo["i"] += 1
        return
    if event.key not in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE,
                         pygame.K_e, pygame.K_ESCAPE):
        return
    dialogo["i"] += 1
    if dialogo["i"] >= len(dialogo["paginas"]) or event.key == pygame.K_ESCAPE:
        despues = dialogo["despues"]
        dialogo = None
        if despues == "siguiente_dia":
            siguiente_dia()


def manejar_tecla_elegir_modo(event):
    global elegir_modo, historia_elegida
    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d,
                     pygame.K_UP, pygame.K_DOWN):
        elegir_modo["sel"] = 1 - elegir_modo["sel"]
    elif event.key == pygame.K_ESCAPE:
        elegir_modo = None
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
        historia_elegida = elegir_modo["sel"] == 0
        elegir_modo = None
        # Luego: ¿jugar el tutorial? (SÍ de entrada la primera vez)
        global pregunta_tutorial
        pregunta_tutorial = {"sel": 1 if (hay_partida("historia") or hay_partida("libre")) else 0}


pregunta_tutorial = None    # {"sel": 0 = SÍ / 1 = NO}
tutorial_desde_opciones = False


def manejar_tecla_pregunta_tutorial(event):
    global pregunta_tutorial, tutorial_desde_opciones
    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d,
                     pygame.K_UP, pygame.K_DOWN):
        pregunta_tutorial["sel"] = 1 - pregunta_tutorial["sel"]
    elif event.key == pygame.K_ESCAPE:
        pregunta_tutorial = None
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
        con_tutorial = pregunta_tutorial["sel"] == 0
        pregunta_tutorial = None
        tutorial_desde_opciones = False
        _pedir_confirmacion(con_tutorial)


def draw_pregunta_tutorial(surface):
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 185))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(110, 90, 420, 170)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (116, 96, 408, 34))
    t = font_title.render("¿JUGAR EL TUTORIAL?", False, CREAM)
    surface.blit(t, t.get_rect(center=(320, 113)))
    for k, (texto, sub) in enumerate((("SÍ", "Aprende paso a paso"), ("NO", "Empezar de una vez"))):
        r = pygame.Rect(0, 0, 170, 64)
        r.center = (225 if k == 0 else 415, 190)
        _boton_pregunta(surface, r, texto, pregunta_tutorial["sel"] == k, sub)


def _boton_pregunta(surface, rect, texto, elegido, sub=None):
    """Botón de las preguntas: el escogido es el oscuro."""
    fill = BUTTON_BLUE_DARK if elegido else (232, 216, 176)
    borde = (24, 36, 46) if elegido else (176, 150, 110)
    pygame.draw.rect(surface, borde, rect.move(0, 3))
    pygame.draw.rect(surface, fill, rect)
    pygame.draw.rect(surface, borde, rect, 2)
    color = CREAM if elegido else WOOD_DARK
    tb = font_large.render(texto, False, color)
    if sub:
        surface.blit(tb, tb.get_rect(center=(rect.centerx, rect.centery - 8)))
        ts = font_small.render(sub, False, color)
        surface.blit(ts, ts.get_rect(center=(rect.centerx, rect.centery + 14)))
    else:
        surface.blit(tb, tb.get_rect(center=rect.center))


def draw_elegir_modo(surface):
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 185))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(110, 90, 420, 170)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (116, 96, 408, 34))
    t = font_title.render("¿CÓMO QUIERES JUGAR?", False, CREAM)
    surface.blit(t, t.get_rect(center=(320, 113)))
    for k, (texto, sub) in enumerate((("HISTORIA", "Con Doña Rosa"), ("LIBRE", "A tu manera"))):
        r = pygame.Rect(0, 0, 170, 64)
        r.center = (225 if k == 0 else 415, 190)
        _boton_pregunta(surface, r, texto, elegir_modo["sel"] == k, sub)


def retrato_rosa():
    """La cara de Doña Rosa (el mismo dibujo de la clienta), en grande."""
    if "rosa" not in _retrato:
        from clientes import PERSONAJES, crear_persona
        datos = next(d for d in PERSONAJES if d["nombre"] == "Doña Rosa")
        sprite = crear_persona(datos).frames["down"][0]
        cara = sprite.subsurface((0, 0, sprite.get_width(), 26)).copy()
        _retrato["rosa"] = pygame.transform.scale(cara, (cara.get_width() * 3, 78))
    return _retrato["rosa"]


def draw_icono_meta(surface, tipo, cx, cy):
    """Dibujitos de las metas (casi sin palabras)."""
    oscuro = (35, 27, 27)
    if tipo == "atender":
        _carita(surface, cx, cy, True)
    elif tipo == "sin_perdidos":
        _carita(surface, cx, cy, False)
        pygame.draw.line(surface, (176, 48, 42), (cx - 10, cy - 10), (cx + 10, cy + 10), 3)
    elif tipo == "vender":
        pygame.draw.circle(surface, oscuro, (cx, cy + 1), 9)
        pygame.draw.circle(surface, (240, 196, 60), (cx, cy), 9)
        pygame.draw.circle(surface, (190, 140, 30), (cx, cy), 5, 1)
    elif tipo == "camion":
        pygame.draw.rect(surface, oscuro, (cx - 11, cy - 7, 23, 13))
        pygame.draw.rect(surface, (200, 70, 60), (cx - 10, cy - 6, 13, 10))
        pygame.draw.rect(surface, (90, 140, 200), (cx + 4, cy - 2, 7, 6))
        for x in (cx - 6, cx + 6):
            pygame.draw.circle(surface, oscuro, (x, cy + 6), 3)
    elif tipo == "tavo":
        pygame.draw.circle(surface, oscuro, (cx, cy - 4), 5)
        pygame.draw.circle(surface, (230, 180, 140), (cx, cy - 4), 4)
        pygame.draw.rect(surface, oscuro, (cx - 6, cy + 1, 12, 9))
        pygame.draw.rect(surface, (70, 150, 90), (cx - 5, cy + 2, 10, 7))
    elif tipo == "receta":
        pygame.draw.rect(surface, oscuro, (cx - 8, cy - 9, 16, 18))
        pygame.draw.rect(surface, (180, 60, 60), (cx - 7, cy - 8, 14, 16))
        pygame.draw.rect(surface, CREAM, (cx - 4, cy - 6, 9, 12))
        for y in (cy - 3, cy, cy + 3):
            pygame.draw.line(surface, (150, 120, 90), (cx - 3, y), (cx + 3, y), 1)
    elif tipo == "estrella":
        cosmeticos._estrella(surface, (255, 214, 40), cx, cy, 12)
    elif tipo == "medalla":
        pygame.draw.polygon(surface, (60, 110, 200), [(cx - 7, cy - 16), (cx - 1, cy - 16), (cx + 2, cy - 4)])
        pygame.draw.polygon(surface, (200, 60, 60), [(cx + 7, cy - 16), (cx + 1, cy - 16), (cx - 2, cy - 4)])
        pygame.draw.circle(surface, oscuro, (cx, cy + 4), 10)
        pygame.draw.circle(surface, (240, 196, 60), (cx, cy + 4), 9)
        cosmeticos._estrella(surface, (255, 236, 150), cx, cy + 4, 5)


def _texto_cabe(texto, fuente, color, ancho):
    t = fuente.render(texto, False, color)
    if t.get_width() > ancho:
        t = pygame.transform.scale(t, (ancho, t.get_height()))
    return t


def draw_dialogo(surface):
    """Doña Rosa habla: retrato, 2 renglones y la flechita para seguir."""
    linea1, linea2, extra = dialogo["paginas"][dialogo["i"]]
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 90))
    surface.blit(overlay, (0, 0))
    caja = pygame.Rect(56, 236, 528, 104)
    pygame.draw.rect(surface, (35, 27, 27), caja.move(4, 4))
    pygame.draw.rect(surface, CREAM, caja)
    pygame.draw.rect(surface, WOOD_DARK, caja, 3)
    marco = pygame.Rect(caja.x + 10, caja.y + 10, 86, 84)
    pygame.draw.rect(surface, (214, 196, 160), marco)
    img = retrato_rosa()
    surface.blit(img, img.get_rect(midbottom=(marco.centerx, marco.bottom - 2)))
    pygame.draw.rect(surface, WOOD_DARK, marco, 2)
    nombre = font_small.render("DOÑA ROSA", False, CREAM)
    chip = nombre.get_rect(topleft=(caja.x + 10, caja.y - 14)).inflate(12, 6)
    chip.topleft = (caja.x + 10, caja.y - 16)
    pygame.draw.rect(surface, RED_SIGN, chip)
    surface.blit(nombre, (chip.x + 6, chip.y + 3))

    x = marco.right + 14
    ancho = caja.right - 16 - x
    if extra == "elegir_mascotas":
        t1 = _texto_cabe(linea1, font_medium, WOOD_DARK, ancho)
        surface.blit(t1, (x, caja.y + 12))
        _botones_mascotas(surface, x, caja.y + 42, ancho)
        return
    icono = isinstance(extra, tuple) or extra in ("estrella", "medalla")
    if icono and not isinstance(extra, tuple):
        ancho -= 40          # la estrella o la medalla van a la derecha
    t1 = _texto_cabe(linea1, font_medium, WOOD_DARK, ancho)
    surface.blit(t1, (x, caja.y + 22))
    if isinstance(extra, tuple):
        # Página de la meta: dibujito + texto en rojo.
        draw_icono_meta(surface, extra[0], x + 12, caja.y + 64)
        t2 = _texto_cabe(linea2, font_medium, RED_SIGN, ancho - 30)
        surface.blit(t2, (x + 30, caja.y + 54))
    else:
        t2 = _texto_cabe(linea2, font_medium, WOOD_DARK, ancho)
        surface.blit(t2, (x, caja.y + 54))
    if extra in ("estrella", "medalla"):
        draw_icono_meta(surface, extra, caja.right - 34, caja.centery)
    if (pygame.time.get_ticks() // 400) % 2 == 0:
        fx, fy = caja.right - 16, caja.bottom - 12
        pygame.draw.polygon(surface, WOOD_DARK, [(fx - 6, fy - 4), (fx + 2, fy - 4), (fx - 2, fy + 2)])


_iconos_mascota = {}


def _icono_mascota(cual):
    if cual not in _iconos_mascota:
        from ambiente import sprite_gato
        from perro import imagen_perro
        _iconos_mascota[cual] = (sprite_gato((236, 150, 60), 0, False, True) if cual == "gata"
                                 else imagen_perro((176, 120, 70), None, None, 0, True))
    return _iconos_mascota[cual]


def _botones_mascotas(surface, x, y, ancho):
    """Cuatro botones con dibujitos; el escogido es el oscuro."""
    n = len(historia.OPCIONES_MASCOTAS)
    w = (ancho - (n - 1) * 6) // n
    for i, (texto, gata, perro_si) in enumerate(historia.OPCIONES_MASCOTAS):
        r = pygame.Rect(x + i * (w + 6), y, w, 46)
        elegido = dialogo["mascota_sel"] == i
        fill = BUTTON_BLUE_DARK if elegido else (232, 216, 176)
        borde = (24, 36, 46) if elegido else (176, 150, 110)
        pygame.draw.rect(surface, borde, r.move(0, 3))
        pygame.draw.rect(surface, fill, r)
        pygame.draw.rect(surface, borde, r, 2)
        dibujos = ([_icono_mascota("gata")] if gata else []) + ([_icono_mascota("perro")] if perro_si else [])
        if dibujos:
            total = sum(d.get_width() for d in dibujos) + 4 * (len(dibujos) - 1)
            dx = r.centerx - total // 2
            for d in dibujos:
                surface.blit(d, d.get_rect(bottomleft=(dx, r.y + 26)))
                dx += d.get_width() + 4
        else:
            pygame.draw.circle(surface, CREAM if elegido else WOOD_DARK, (r.centerx, r.y + 16), 8, 2)
            pygame.draw.line(surface, CREAM if elegido else WOOD_DARK,
                             (r.centerx - 5, r.y + 21), (r.centerx + 5, r.y + 11), 2)
        t = font_small.render(texto, False, CREAM if elegido else WOOD_DARK)
        surface.blit(t, t.get_rect(midbottom=(r.centerx, r.bottom - 3)))


def draw_meta_hud(surface, y):
    """Debajo del reloj: dibujito de la meta del día y cuánto lleva."""
    if not historia_activa or tutorial.activo:
        return
    m = meta_hoy()
    lleva, objetivo, lista = historia.progreso(m, stats_hoy())
    if m[0] == "vender":
        texto = f"{format_colones(lleva)} / {format_colones(objetivo)}"
    elif m[0] == "sin_perdidos":
        texto = f"= {lleva}"
    else:
        texto = f"{lleva} / {objetivo}"
    t = font_small.render(texto, False, HUD_LETRA)
    caja = pygame.Rect(4, y, t.get_width() + 46 + (16 if lista else 0), 26)
    _caja_hud(surface, caja)
    _hud_rects["meta"] = caja.copy()
    draw_icono_meta(surface, m[0], caja.x + 15, caja.centery)
    surface.blit(t, (caja.x + 32, caja.y + 8))
    if lista:
        cx, cy = caja.right - 13, caja.centery
        pygame.draw.lines(surface, (120, 230, 120), False, [(cx - 5, cy), (cx - 1, cy + 4), (cx + 6, cy - 5)], 3)


def empezar_flujo_nueva(con_tutorial):
    """Elegir personaje y nombre; al terminar se crea la partida de cero."""
    global forzar_tutorial, skin_seleccion, current_scene, nombre_jugador, confirmar_nueva
    confirmar_nueva = None
    forzar_tutorial = con_tutorial
    # La partida abierta queda guardada en el archivo de su modo (si es del
    # otro modo, sigue intacta para CONTINUAR).
    if partida_en_juego():
        guardar_partida()
    nombre_jugador = ""
    skin_seleccion = SKINS_ORDEN.index(player.skin)
    current_scene = "elegir_skin"


def manejar_tecla_confirmar(event):
    global confirmar_nueva
    c = confirmar_nueva
    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d, pygame.K_UP, pygame.K_DOWN):
        c["sel"] = 1 - c["sel"]
    elif event.key == pygame.K_ESCAPE:
        confirmar_nueva = None
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
        if c["sel"] == 0:
            empezar_flujo_nueva(c["tutorial"])
        else:
            confirmar_nueva = None


# ESC dentro del juego: menú de pausa (seguir, ayuda o salir al menú).
pausa = None                # {"sel": índice en OPCIONES_PAUSA}
OPCIONES_PAUSA = ("SEGUIR JUGANDO", "AYUDA", "SALIR AL MENÚ")
ayuda_volver = None         # zona del juego a la que vuelve AYUDA


def abrir_pausa():
    global pausa
    pausa = {"sel": 0}
    sonido.efecto("abrir_caja")


def manejar_tecla_pausa(event):
    global pausa, current_scene, ultima_zona, ayuda_volver
    if event.key in (pygame.K_UP, pygame.K_w):
        pausa["sel"] = (pausa["sel"] - 1) % len(OPCIONES_PAUSA)
    elif event.key in (pygame.K_DOWN, pygame.K_s):
        pausa["sel"] = (pausa["sel"] + 1) % len(OPCIONES_PAUSA)
    elif event.key == pygame.K_ESCAPE:
        pausa = None                                    # sigue el juego
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_e):
        eleccion = OPCIONES_PAUSA[pausa["sel"]]
        if eleccion == "SEGUIR JUGANDO":
            pausa = None
        elif eleccion == "AYUDA":
            ayuda_volver = current_scene                 # al cerrar, vuelve aquí
            current_scene = "ayuda"
        else:
            pausa = None
            ultima_zona = current_scene
            current_scene = "menu"
            guardar_partida()


def cerrar_ayuda():
    """ESC / ENTER en AYUDA: vuelve al juego (con la pausa abierta) o al menú."""
    global current_scene, ayuda_volver
    current_scene = ayuda_volver or "menu"
    ayuda_volver = None


def draw_pausa(surface):
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 170))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(200, 78, 240, 196)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (panel.x + 6, panel.y + 6, panel.w - 12, 34))
    t = font_title.render("PAUSA", False, CREAM)
    surface.blit(t, t.get_rect(center=(panel.centerx, panel.y + 23)))
    # La opción escogida es la oscura (igual que en las preguntas).
    for i, texto in enumerate(OPCIONES_PAUSA):
        r = pygame.Rect(0, 0, 190, 30)
        r.center = (panel.centerx, panel.y + 70 + i * 42)
        elegido = pausa["sel"] == i
        fill = BUTTON_BLUE_DARK if elegido else (232, 216, 176)
        borde = (24, 36, 46) if elegido else (176, 150, 110)
        pygame.draw.rect(surface, borde, r.move(0, 3))
        pygame.draw.rect(surface, fill, r)
        pygame.draw.rect(surface, borde, r, 2)
        tb = font_medium.render(texto, False, CREAM if elegido else WOOD_DARK)
        surface.blit(tb, tb.get_rect(center=r.center))
        if elegido:
            ancla = r
    dibujar_tooltip(surface, ancla, TOOLTIP_PAUSA[OPCIONES_PAUSA[pausa["sel"]]], "derecha", 150)


def draw_confirmar_nueva(surface):
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 185))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(120, 90, 400, 170)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (126, 96, 388, 34))
    t = font_title.render("¿PARTIDA NUEVA?", False, CREAM)
    surface.blit(t, t.get_rect(center=(320, 113)))
    modo = modo_elegido()
    res = resumen_partida(modo) or ("antes", 1)
    otro = "libre" if modo == "historia" else "historia"
    for i, linea in enumerate((f"Se borra la partida {NOMBRE_MODO[modo]} de {res[0]} (día {res[1]}).",
                               f"La partida {NOMBRE_MODO[otro]} no se toca.",
                               "¿Estás seguro?")):
        tt = font_medium.render(linea, False, WOOD_DARK)
        surface.blit(tt, tt.get_rect(center=(320, 150 + i * 22)))
    # La opción escogida es la OSCURA (azul con letra clara); la otra, clara.
    for k, texto in enumerate(("SÍ, EMPEZAR DE CERO", "NO")):
        tb_ancho = font_medium.size(texto)[0]
        r = pygame.Rect(0, 0, max(90, tb_ancho + 24), 28)
        r.center = (245 if k == 0 else 425, 230)
        elegido = confirmar_nueva["sel"] == k
        fill = BUTTON_BLUE_DARK if elegido else (232, 216, 176)
        borde = (24, 36, 46) if elegido else (176, 150, 110)
        pygame.draw.rect(surface, borde, r.move(0, 3))
        pygame.draw.rect(surface, fill, r)
        pygame.draw.rect(surface, borde, r, 2)
        tb = font_medium.render(texto, False, CREAM if elegido else WOOD_DARK)
        surface.blit(tb, tb.get_rect(center=r.center))


def nueva_partida_jornada():
    global dia, ventas_dia, venta_reciente, cierre, saldo, armario, hora_de_acomodar
    hora_de_acomodar = False
    saldo = SALDO_INICIAL
    armario = None
    cosmeticos.reiniciar()
    mascota.reiniciar()
    perro.reiniciar()
    persecucion.reiniciar()
    casa_gato.nivel = 0
    cosmeticos.vestir(player, mascota, perro)
    camion.__init__()
    ayudante.nuevo_dia()
    gastos_dia.clear()
    reloj.reiniciar(dia=1)
    dia = 1
    ventas_dia = []
    venta_reciente = None
    cierre = None


hora_de_acomodar = False    # ya dieron las 6:00 p. m. hoy (tienda cerrada)


def cerrar_por_hora():
    """Son las 6:00 p. m.: se cierra la factura (si estaba abierta), los
    clientes que quedaban se retiran y el letrero pasa a CERRADO. De 6 a 8
    se acomoda la tienda (o "TERMINAR EL DÍA" en el letrero)."""
    global hora_de_acomodar
    hora_de_acomodar = True
    if checkout_open:
        cerrar_factura()
    if recetario.abierto:
        recetario.cerrar()
    clientes.cerrar_por_hora()
    clientes.abierta = False
    table_object_manager.avisar("¡Son las 6:00 p. m.! Cerramos.",
                                "Acomoda la tienda hasta las 8:00 p. m.")
    sonido.efecto("campanita")
    if historia_activa and not tutorial.activo and dialogo is None:
        abrir_dialogo([(f"¡Ya son las 6, {nombre_bonito()}! Cerramos por hoy.",
                        "Acomoda la tienda para mañana.", None),
                       ("Cuando termines, ve al letrero", "de la puerta: TERMINAR EL DÍA.", None)])


def abrir_cierre():
    """Cierre de caja: poco texto; las ventas se suman como una cuenta."""
    global cierre
    cierre = {"valor": "", "errores": 0, "listo": False, "pista": False,
              "total": sum(ventas_dia), "mensaje": ""}
    if not ventas_dia:
        cierre["listo"] = True
        cierre["mensaje"] = "¡Mañana venderás más!"
    elif not MODO["cierre"]:
        # Modo de juego sin la suma del cierre: se muestra el total.
        cierre["listo"] = True
        cierre["valor"] = str(cierre["total"])
        cierre["mensaje"] = "¡Buen trabajo!"


def pista_cierre():
    """Pistas con números, casi sin palabras."""
    v = ventas_dia
    e = cierre["errores"]
    if len(v) == 1:
        return f"= {v[0]}"
    parciales = [v[0]]
    for monto in v[1:]:
        parciales.append(parciales[-1] + monto)
    if e == 1:
        return f"{v[0]} + {v[1]} = ?"
    if e == 2:
        return (f"{v[0]} + {v[1]} = {parciales[1]}   ->   {parciales[1]} + {v[2]} = ?"
                if len(v) > 2 else f"{v[0]} + {v[1]} = ?")
    return "  ->  ".join(str(x) for x in parciales[:-1]) + "  ->  ?"


def revisar_cierre():
    c = cierre
    if not c["valor"]:
        return
    if int(c["valor"]) == c["total"]:
        c["listo"] = True
        c["pista"] = False
        quien = f", {nombre_bonito()}" if nombre_jugador else ""
        c["mensaje"] = f"¡Excelente{quien}!"
        estadisticas.registrar("cierre", True)
        return
    c["errores"] += 1
    estadisticas.registrar("cierre", False)
    sonido.efecto("error")
    c["valor"] = ""
    if c["errores"] >= MAX_ERRORES_CIERRE:
        c["listo"] = True
        c["pista"] = False
        c["valor"] = str(c["total"])
        c["mensaje"] = "¡Mañana lo logras!"
    else:
        c["pista"] = True
        c["mensaje"] = pista_cierre()


def siguiente_dia():
    global dia, ventas_dia, venta_reciente, cierre, saldo, hora_de_acomodar
    hora_de_acomodar = False
    saldo -= total_cuentas()      # luz, agua, alquiler y comida de Canela
    dia += 1
    ventas_dia = []
    venta_reciente = None
    cierre = None
    clientes.dia = dia         # los clientes frecuentes siguen su sucesión
    clientes.reiniciar()
    reloj.reiniciar(dia=dia)   # amanece
    bodega.reabastecer()       # llegó el camión: la bodega se llena otra vez
    ayudante.nuevo_dia()
    gastos_dia.clear()
    historia_hoy["camion"] = False
    historia_hoy["felicitado"] = False
    table_object_manager.avisar("¡Llegó el camión!", "La bodega está llena otra vez.")
    if historia_activa and not tutorial.activo:
        # MODO HISTORIA: al empezar el día 8 y el 16 sube la dificultad.
        global nivel_actual
        nivel_nuevo = None
        if dia in historia.DIAS_SUBIR_NIVEL:
            siguiente = historia.nivel_siguiente(nivel_actual, ORDEN_NIVELES)
            if siguiente != nivel_actual:
                nivel_actual = siguiente
                nivel_nuevo = NIVELES[siguiente]["nombre"]
        abrir_saludo(nivel_nuevo)
    guardar_partida()


# Letreros de pie para abrir o cerrar la tienda (coordenadas 640 x 360).
LETRERO_TIENDA = {"interior": (404, 320), "entrada": (392, 200)}
DISTANCIA_LETRERO = 34


def rect_letrero(escena):
    """Base sólida del letrero: el personaje no lo atraviesa."""
    x, y = LETRERO_TIENDA[escena]
    return pygame.Rect(x - 16, y + 2, 32, 14)


def cerca_letrero():
    """¿El personaje está junto al letrero de la puerta en esta escena?"""
    punto = LETRERO_TIENDA.get(current_scene)
    if punto is None:
        return False
    return math.hypot(player.x - punto[0], player.y - (punto[1] + 10)) <= DISTANCIA_LETRERO + 6


def texto_letrero():
    if reloj.cerro:
        return "E: TERMINAR EL DÍA"          # de 6 a 8 p. m.: se acomoda
    return "E: CERRAR LA TIENDA" if clientes.abierta else "E: ABRIR LA TIENDA"


def alternar_tienda():
    """Darle vuelta al letrero: cerrar la tienda para reabastecer, o abrirla.
    Después de las 6:00 p. m. el letrero sirve para TERMINAR EL DÍA."""
    if reloj.cerro:
        reloj.terminar_dia()               # salta a las 8:00 p. m. (cierre de caja)
        return
    abierta = clientes.alternar_tienda()
    if abierta:
        table_object_manager.avisar("¡Tienda abierta!", "Ya pueden entrar clientes.")
    else:
        table_object_manager.avisar("¡Tienda cerrada!", "Aprovecha para llenar los estantes.")


_fuente_letrero = None


def dibujar_letrero_pie(surface, centro):
    """Letrero de pie (tipo pizarra) que el niño voltea con E."""
    x, y = centro
    pygame.draw.line(surface, (84, 50, 39), (x - 12, y + 6), (x - 16, y + 20), 2)
    pygame.draw.line(surface, (84, 50, 39), (x + 12, y + 6), (x + 16, y + 20), 2)
    dibujar_letrero_tienda(surface, centro, colgado=False)
    if cerca_letrero():
        # Destello para indicar que se puede usar.
        brillo = (pygame.time.get_ticks() // 300) % 2
        caja = pygame.Rect(0, 0, 60, 22)
        caja.center = centro
        pygame.draw.rect(surface, (255, 236, 150) if brillo else (239, 210, 139), caja, 2)


def dibujar_letrero_tienda(surface, centro, colgado=True):
    """Letrero ABIERTO (verde) o CERRADO (rojo)."""
    global _fuente_letrero
    if _fuente_letrero is None:
        _fuente_letrero = FuenteTienda(None, 13)
    abierta = clientes.abierta
    texto = _fuente_letrero.render("ABIERTO" if abierta else "CERRADO", False, CREAM)
    caja = texto.get_rect(center=centro).inflate(10, 6)
    if colgado:
        pygame.draw.line(surface, (35, 27, 27), (caja.x + 6, caja.y), (centro[0], caja.y - 7), 1)
        pygame.draw.line(surface, (35, 27, 27), (caja.right - 6, caja.y), (centro[0], caja.y - 7), 1)
    pygame.draw.rect(surface, (35, 27, 27), caja.move(1, 1))
    pygame.draw.rect(surface, (66, 130, 70) if abierta else (176, 48, 42), caja)
    pygame.draw.rect(surface, (35, 27, 27), caja, 1)
    surface.blit(texto, texto.get_rect(center=caja.center))


def manejar_tecla_cierre(event):
    c = cierre
    if c["listo"]:
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            terminar_dia()
        return
    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        revisar_cierre()
    elif event.key == pygame.K_BACKSPACE:
        c["valor"] = c["valor"][:-1]
    elif event.unicode and event.unicode.isdigit() and len(c["valor"]) < 5:
        c["valor"] += event.unicode


def _chip_monto(surface, texto, x, y, font, resaltado=False):
    t = font.render(texto, False, (54, 40, 20))
    caja = t.get_rect(topleft=(x, y)).inflate(12, 6)
    caja.topleft = (x, y)
    pygame.draw.rect(surface, (35, 27, 27), caja.move(1, 2), border_radius=4)
    pygame.draw.rect(surface, (255, 226, 120) if resaltado else (239, 210, 139), caja, border_radius=4)
    pygame.draw.rect(surface, (167, 109, 74), caja, 1, border_radius=4)
    surface.blit(t, (caja.x + 6, caja.y + 3))
    return caja


def abrir_recetario():
    """Abre el libro; si el cliente del frente pidió una receta, en esa página."""
    c = clientes.cliente_esperando()
    receta = getattr(c, "receta", None) if c is not None else None
    if receta and not c.pedido_visible:
        # Si el pedido ya se ocultó (reto de memoria), el libro no lo revela.
        receta = None
    recetario.abrir(receta[0] if receta else None)


# Historial de ventas del día: se abre y cierra con la tecla H.
historial_abierto = False


# ---------------------------------------------------------
# BURBUJAS DE AYUDA (tooltips): dicen qué hace la opción marcada
# ---------------------------------------------------------
TOOLTIP_FONDO = (35, 27, 27)
TOOLTIP_BORDE = (255, 218, 92)
TOOLTIP_LETRA = (250, 238, 200)


def _partir_texto(texto, fuente, ancho):
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = f"{actual} {p}".strip()
        if fuente.size(prueba)[0] <= ancho or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def raton_logico():
    """Dónde está el mouse, en coordenadas del juego (640 x 360)."""
    if not pygame.mouse.get_focused():
        return None
    x, y = pygame.mouse.get_pos()
    return x // SCALE, y // SCALE


def dibujar_tooltip(surface, ancla, texto, lado="derecha", ancho_max=210):
    """Burbuja oscura con letra clara junto a la opción marcada, con una
    flechita que la señala. lado: "derecha", "izquierda", "arriba" o "abajo".
    Se apagan en OPCIONES > GRÁFICOS > BURBUJAS DE AYUDA."""
    if not tooltips_activos or not texto:
        return
    ancla = pygame.Rect(ancla)
    lineas = [font_aviso.render(l, False, TOOLTIP_LETRA)
              for l in _partir_texto(texto, font_aviso, ancho_max)]
    w = max(l.get_width() for l in lineas) + 14
    h = sum(l.get_height() for l in lineas) + 10
    caja = pygame.Rect(0, 0, w, h)
    if lado == "derecha" and ancla.right + 12 + w > GAME_WIDTH - 2:
        lado = "izquierda"
    if lado == "izquierda" and ancla.left - 12 - w < 2:
        lado = "abajo"
    if lado == "arriba" and ancla.top - 10 - h < 2:
        lado = "abajo"
    if lado == "abajo" and ancla.bottom + 10 + h > GAME_HEIGHT - 2:
        lado = "arriba"
    if lado == "derecha":
        caja.midleft = (ancla.right + 10, ancla.centery)
    elif lado == "izquierda":
        caja.midright = (ancla.left - 10, ancla.centery)
    elif lado == "arriba":
        caja.midbottom = (ancla.centerx, ancla.top - 8)
    else:
        caja.midtop = (ancla.centerx, ancla.bottom + 8)
    caja.clamp_ip(pygame.Rect(2, 2, GAME_WIDTH - 4, GAME_HEIGHT - 4))
    # Flechita hacia la opción
    if lado == "derecha":
        punta = [(caja.left - 6, ancla.centery), (caja.left + 1, ancla.centery - 5),
                 (caja.left + 1, ancla.centery + 5)]
    elif lado == "izquierda":
        punta = [(caja.right + 6, ancla.centery), (caja.right - 1, ancla.centery - 5),
                 (caja.right - 1, ancla.centery + 5)]
    elif lado == "arriba":
        cx = max(caja.left + 8, min(caja.right - 8, ancla.centerx))
        punta = [(cx, caja.bottom + 6), (cx - 5, caja.bottom - 1), (cx + 5, caja.bottom - 1)]
    else:
        cx = max(caja.left + 8, min(caja.right - 8, ancla.centerx))
        punta = [(cx, caja.top - 6), (cx - 5, caja.top + 1), (cx + 5, caja.top + 1)]
    pygame.draw.rect(surface, (10, 8, 8), caja.move(2, 2), border_radius=4)
    pygame.draw.polygon(surface, TOOLTIP_BORDE, punta)
    pygame.draw.rect(surface, TOOLTIP_FONDO, caja, border_radius=4)
    pygame.draw.rect(surface, TOOLTIP_BORDE, caja, 1, border_radius=4)
    y = caja.y + 5
    for l in lineas:
        surface.blit(l, (caja.x + 7, y))
        y += l.get_height()


TOOLTIP_MENU = {
    "JUGAR": "Empieza una partida nueva.",
    "CONTINUAR": "Sigue con tu partida guardada.",
    "OPCIONES": "Sonido, gráficos, dificultad y más.",
    "REPORTE": "Para el profe o los papás: aciertos, errores y calculadora.",
    "AYUDA": "Mira cómo se juega.",
    "SALIR": "Cierra el juego. Tu partida queda guardada.",
}
TOOLTIP_PAUSA = {
    "SEGUIR JUGANDO": "Vuelve a la pulpería.",
    "AYUDA": "Mira los controles del juego.",
    "SALIR AL MENÚ": "Guarda la partida y vuelve al menú.",
}
TOOLTIP_SONIDO = {
    "estilo": "La música que suena en el menú.",
    "estilo_tienda": "La música mientras atiendes la pulpería.",
    "vol_musica": "Qué tan fuerte suena la música.",
    "efectos": "Sonidos al cobrar, tomar productos y acertar.",
    "vol_efectos": "Qué tan fuertes suenan los efectos.",
    "probar_efecto": "ENTER: escucha cómo suena cada efecto.",
    "ambiente": "Viento, carros y grillos de fondo.",
    "vol_ambiente": "Qué tan fuerte es el ruido de fondo.",
    "probar_ambiente": "ENTER: escucha cada ruido de fondo.",
}
TOOLTIP_VISUAL = {
    "letra": "Cambia el tipo de letra del juego.",
    "luciernagas": "Luciérnagas que brillan desde las 3 p. m.",
    "avisos": "El texto de abajo que dice con qué puedes interactuar.",
    "paredes": "Color de las paredes.",
    "piso": "Color del piso.",
    "alfombras": "Color de las alfombras.",
    "mesa": "Color del mostrador.",
    "refris": "Color de las refris.",
    "muebles": "Color de las góndolas y los demás muebles.",
    "original": "ENTER: vuelve a los colores de siempre.",
    "tooltips": "Estas burbujas que explican cada opción.",
    "pantalla": "El juego llena toda la pantalla. F11 también lo cambia.",
}
TOOLTIP_EXTRAS = {
    "mascotas": "Canela y Bruno viven en la pulpería. Su comida se paga cada día.",
    "cuales": "Elige qué mascotas te acompañan.",
    "personalizacion": "El armario de ropa en la bodega, para vestir a tu personaje.",
    "reporte": "Para el profe o los papás: aciertos, errores y calculadora.",
}
_hud_rects = {}             # dónde quedó cada dato de arriba (para su ayuda)


def draw_tooltips_hud(surface):
    """Mouse sobre el reloj, la meta, el saldo o el día: qué es cada cosa."""
    pos = raton_logico()
    if pos is None:
        return
    textos = {
        "reloj": "Abre 8:00 a. m. Cierra 6:00 p. m. Hasta las 8:00 p. m. se acomoda.",
        "saldo": "Tu dinero: sube con las ventas y baja con los gastos.",
        "dia": "El día de juego. Al final de cada día se pagan las cuentas.",
    }
    if historia_activa:
        textos["meta"] = "Meta de hoy: " + historia.texto_meta(meta_hoy())
    for clave, rect in _hud_rects.items():
        if clave in textos and rect.collidepoint(pos):
            dibujar_tooltip(surface, rect, textos[clave], "abajo")
            return


# Recuadros de datos del juego (reloj, día, saldo, meta): gris con letra amarilla.
HUD_FONDO = (92, 94, 102)
HUD_BORDE = (58, 60, 66)
HUD_LETRA = (255, 218, 92)


def _caja_hud(surface, caja):
    pygame.draw.rect(surface, HUD_FONDO, caja)
    pygame.draw.rect(surface, HUD_BORDE, caja, 1)


def draw_hud_ventas(surface):
    """Arriba: el día y el saldo (con una monedita); las ventas, en H."""
    titulo = font_small.render(f"DÍA {dia}", False, HUD_LETRA)
    caja = titulo.get_rect().inflate(16, 10)
    caja.topright = (GAME_WIDTH - 4, 4)
    _caja_hud(surface, caja)
    _hud_rects["dia"] = caja.copy()
    surface.blit(titulo, titulo.get_rect(center=caja.center))
    # Saldo
    monto = font_small.render(format_colones(saldo), False,
                              HUD_LETRA if saldo >= 0 else (255, 150, 140))
    caja_s = pygame.Rect(0, 0, monto.get_width() + 26, caja.h)
    caja_s.topright = (caja.left - 4, caja.top)
    _caja_hud(surface, caja_s)
    _hud_rects["saldo"] = caja_s.copy()
    pygame.draw.circle(surface, (240, 196, 60), (caja_s.x + 9, caja_s.centery), 5)
    pygame.draw.circle(surface, (176, 128, 30), (caja_s.x + 9, caja_s.centery), 5, 1)
    surface.blit(monto, monto.get_rect(midright=(caja_s.right - 6, caja_s.centery)))
    # "+₡21" que sube al cobrar (solo un momento).
    if venta_reciente is not None:
        edad = pygame.time.get_ticks() - venta_reciente[1]
        if edad < 1800:
            t = font_medium.render(f"+{format_colones(venta_reciente[0])}", False, (92, 176, 76))
            surface.blit(t, t.get_rect(midtop=(caja.centerx, caja.bottom + 4 + edad // 60)))


def draw_historial(surface):
    """Menú con el monto de cada venta del día (sin el total)."""
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 180))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(140, 40, 360, 280)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    barra = pygame.Rect(panel.x + 6, panel.y + 6, panel.w - 12, 36)
    pygame.draw.rect(surface, WOOD, barra)
    titulo = font_title.render(f"VENTAS DE HOY - DÍA {dia}", False, CREAM)
    surface.blit(titulo, titulo.get_rect(center=barra.center))

    # Clientes atendidos (carita feliz) y los que se fueron (triste).
    for i, (feliz, n) in enumerate(((True, clientes.atendidos), (False, clientes.perdidos))):
        x = panel.centerx - 40 + i * 64
        _carita(surface, x, barra.bottom + 14, feliz)
        tn = font_medium.render(str(n), False, WOOD_DARK)
        surface.blit(tn, tn.get_rect(midleft=(x + 13, barra.bottom + 15)))
    if not ventas_dia:
        t = font_medium.render("Todavía no hay ventas hoy.", False, WOOD_DARK)
        surface.blit(t, t.get_rect(center=(panel.centerx, panel.centery)))
    else:
        # Dos columnas: "Venta 1 ........ ₡12"
        filas = 5
        for i, monto in enumerate(ventas_dia):
            col, fila = divmod(i, filas)
            x = panel.x + 22 + col * 168
            y = barra.bottom + 32 + fila * 34
            etiqueta = font_small.render(f"Venta {i + 1}", False, BUTTON_BLUE_DARK)
            surface.blit(etiqueta, (x, y + 6))
            _chip_monto(surface, format_colones(monto), x + 72, y + 2, font_medium)
    for i, (texto, monto) in enumerate(gastos_dia[-4:]):
        g = font_small.render(f"{texto}: -{format_colones(monto)}", False, (159, 60, 47))
        surface.blit(g, g.get_rect(midbottom=(panel.centerx, panel.bottom - 28 - i * 16)))
    s = font_medium.render(f"SALDO: {format_colones(saldo)}", False, (54, 96, 65) if saldo >= 0 else (159, 60, 47))
    surface.blit(s, s.get_rect(midbottom=(panel.centerx, panel.bottom - 8)))


CIERRE_BOTON = pygame.Rect(245, 274, 150, 26)   # "DÍA N >" en el cierre de caja

# Cuentas que se pagan al cerrar cada día (se restan del saldo).
CUENTAS_DIA = [("luz", 8), ("agua", 5), ("alquiler", 20), ("comida", 4)]


def cuentas_dia():
    """Luz, agua y alquiler, más la comida de cada mascota que haya."""
    cuentas = [c for c in CUENTAS_DIA if c[0] != "comida"]
    if MASCOTAS["gata"]:
        cuentas.append(("comida", 4))
    if MASCOTAS["perro"]:
        cuentas.append(("comida_perro", 5))
    return cuentas


def total_cuentas():
    return sum(monto for _, monto in cuentas_dia())


def _icono_cuenta(surface, tipo, cx, cy):
    """Dibujito de cada cuenta: foco, gota, casita y pescado."""
    if tipo == "luz":
        pygame.draw.circle(surface, (250, 220, 80), (cx, cy - 2), 5)
        pygame.draw.circle(surface, (176, 140, 30), (cx, cy - 2), 5, 1)
        pygame.draw.rect(surface, (120, 120, 130), (cx - 2, cy + 3, 5, 3))
    elif tipo == "agua":
        pygame.draw.polygon(surface, (80, 160, 230), [(cx, cy - 7), (cx - 4, cy), (cx + 4, cy)])
        pygame.draw.circle(surface, (80, 160, 230), (cx, cy + 1), 4)
    elif tipo == "alquiler":
        pygame.draw.polygon(surface, (196, 70, 64), [(cx - 7, cy - 1), (cx, cy - 7), (cx + 7, cy - 1)])
        pygame.draw.rect(surface, (230, 214, 170), (cx - 5, cy - 1, 10, 7))
        pygame.draw.rect(surface, (120, 78, 52), (cx - 1, cy + 2, 3, 4))
    elif tipo == "comida_perro":  # huesito
        pygame.draw.rect(surface, (246, 240, 222), (cx - 5, cy - 1, 10, 3))
        for dx in (-5, 5):
            pygame.draw.circle(surface, (246, 240, 222), (cx + dx, cy - 2), 2)
            pygame.draw.circle(surface, (246, 240, 222), (cx + dx, cy + 2), 2)
    else:  # comida del gato: pescadito
        pygame.draw.ellipse(surface, (240, 150, 60), (cx - 6, cy - 3, 10, 7))
        pygame.draw.polygon(surface, (240, 150, 60), [(cx + 3, cy), (cx + 7, cy - 4), (cx + 7, cy + 4)])
        pygame.draw.circle(surface, (35, 27, 27), (cx - 3, cy - 1), 1)


def _carita(surface, x, y, feliz):
    """Carita para contar clientes atendidos (feliz) o que se fueron (triste)."""
    color = (96, 168, 90) if feliz else (196, 84, 70)
    pygame.draw.circle(surface, (35, 27, 27), (x, y + 1), 9)
    pygame.draw.circle(surface, color, (x, y), 9)
    pygame.draw.circle(surface, (35, 27, 27), (x - 3, y - 2), 1)
    pygame.draw.circle(surface, (35, 27, 27), (x + 3, y - 2), 1)
    if feliz:
        pygame.draw.arc(surface, (35, 27, 27), (x - 5, y - 4, 10, 9), 3.5, 5.9, 2)
    else:
        pygame.draw.arc(surface, (35, 27, 27), (x - 5, y + 2, 10, 8), 0.4, 2.7, 2)


def draw_cierre(surface):
    """CIERRE DE CAJA: casi sin texto. Las ventas del día salen como una
    suma (₡3 + ₡8 + ₡14 = ___) y el niño escribe el total."""
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 190))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(70, 40, 500, 270)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (76, 46, 488, 40))
    titulo = font_title.render(f"CIERRE - DÍA {dia}", False, CREAM)
    surface.blit(titulo, titulo.get_rect(center=(320, 66)))

    # Clientes: caritas felices (atendidos) y tristes (se fueron).
    for i, (feliz, n) in enumerate(((True, clientes.atendidos), (False, clientes.perdidos))):
        x = 270 + i * 80
        _carita(surface, x, 106, feliz)
        t = font_large.render(str(n), False, WOOD_DARK)
        surface.blit(t, t.get_rect(midleft=(x + 14, 107)))

    # Las ventas como una suma: fichas con "+" entre ellas.
    montos = ventas_dia or [0]
    fuente = font_large if len(montos) <= 6 else font_medium
    anchos = [fuente.size(format_colones(m))[0] + 12 for m in montos]
    separacion = 18 if len(montos) <= 6 else 14
    x = 320 - (sum(anchos) + separacion * (len(anchos) - 1)) // 2
    for i, monto in enumerate(montos):
        chip = _chip_monto(surface, format_colones(monto), x, 136, fuente)
        x = chip.right + separacion
        if i < len(montos) - 1:
            mas = fuente.render("+", False, WOOD_DARK)
            surface.blit(mas, mas.get_rect(center=(x - separacion // 2, chip.centery)))

    c = cierre
    igual = font_title.render("=", False, WOOD_DARK)
    caja = pygame.Rect(262, 178, 140, 34)
    surface.blit(igual, igual.get_rect(midright=(caja.x - 12, caja.centery)))
    pygame.draw.rect(surface, CREAM, caja)
    pygame.draw.rect(surface, (66, 115, 67) if c["listo"] else BUTTON_HIGHLIGHT_DARK, caja, 3)
    if c["listo"]:
        valor = format_colones(c["total"])
    else:
        valor = format_colones(int(c["valor"])) if c["valor"] else "_"
    t = font_large.render(valor, False, WOOD_DARK)
    surface.blit(t, t.get_rect(center=caja.center))

    if c["mensaje"]:
        color = (66, 115, 67) if c["listo"] or c.get("pista") else WOOD_DARK
        m = font_medium.render(c["mensaje"], False, color)
        surface.blit(m, m.get_rect(center=(320, 226)))
    if c["listo"]:
        # Cuentas del día: dibujito y monto de cada una (se pagan al seguir).
        lista = cuentas_dia()
        x = 320 - (len(lista) * 74 + 70) // 2 + 6
        for tipo, monto in lista:
            _icono_cuenta(surface, tipo, x, 252)
            t = font_medium.render(f"-{format_colones(monto)}", False, (159, 60, 47))
            surface.blit(t, t.get_rect(midleft=(x + 10, 253)))
            x += 74
        despues = saldo - total_cuentas()
        pygame.draw.circle(surface, (240, 196, 60), (x + 6, 252), 6)
        pygame.draw.circle(surface, (176, 128, 30), (x + 6, 252), 6, 1)
        ts = font_medium.render(f"{format_colones(despues)}", False,
                                (54, 96, 65) if despues >= 0 else (159, 60, 47))
        surface.blit(ts, ts.get_rect(midleft=(x + 16, 253)))
        # Flechita para seguir al día siguiente (ENTER).
        boton = CIERRE_BOTON
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK, boton.move(0, 3))
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT, boton)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK, boton, 2)
        tb = font_medium.render(f"DÍA {dia + 1}  >", False, WOOD_DARK)
        surface.blit(tb, tb.get_rect(center=boton.center))


def productos_disponibles():
    """Cuántos hay de cada producto en la tienda, las manos y la bodega."""
    conteo = {}
    for item in table_object_manager.items:
        if item["kind"] in PRODUCTOS:
            conteo[item["kind"]] = conteo.get(item["kind"], 0) + 1
    for item in bodega.items:
        conteo[item["kind"]] = conteo.get(item["kind"], 0) + 1
    return conteo


def vuelto_pendiente():
    return vuelto is not None and not vuelto["listo"]


def revisar_vuelto():
    """Valida el vuelto escrito y da pistas escalonadas."""
    v = vuelto
    if not v["valor"]:
        v["mensaje"] = "Escribe el vuelto y pulsa ENTER."
        return
    if int(v["valor"]) == v["esperado"]:
        v["listo"] = True
        v["mensaje"] = f"¡Correcto! El vuelto es {format_colones(v['esperado'])}."
        estadisticas.registrar("vuelto", True)
        return
    v["errores"] += 1
    estadisticas.registrar("vuelto", False)
    total, pago = v["total"], v["pago"]
    if v["errores"] == 1:
        v["mensaje"] = f"Pista: cuenta desde {total} hasta {pago}."
    elif v["errores"] == 2:
        v["mensaje"] = f"Pista: {total} + ? = {pago}"
    elif v["errores"] == 3:
        v["mensaje"] = f"Pista: es {pago} - {total}. ¡Tú puedes!"
    else:
        v["listo"] = True
        v["mensaje"] = f"El vuelto era {format_colones(v['esperado'])}. ¡La próxima lo logras!"
    v["valor"] = ""

# Personaje controlable. Su posicion representa el centro de los pies.
player = Player(x=320, y=248)
clientes.jugador = player     # el pulpero habla en las conversaciones de recetas
# La fila de clientes sigue al mostrador aunque se mueva (SHIFT+E).
clientes.obtener_mostrador = lambda: next(
    (m for m in furniture_manager.items if m["kind"] == "counter"), None)
clientes.mostrador_quieto = lambda: (furniture_manager.selected is None
                                     or furniture_manager.selected.get("kind") != "counter")
cosmeticos.vestir(player, mascota, perro)

# Apariencias para elegir al darle JUGAR (pulpero o pulpera).
SKINS_ORDEN = ["hombre", "mujer"]
skin_seleccion = 0
# Un personaje de muestra por apariencia, para la pantalla de elección.
skin_muestras = {clave: Player(skin=clave) for clave in SKINS_ORDEN}

# Nombre que escribe el niño o niña antes de jugar.
NOMBRE_MAX = 12
nombre_jugador = ""
nombre_aviso = False   # True si intentó empezar sin escribir su nombre


def nombre_bonito():
    """'ana maria' -> 'Ana Maria' para usarlo en los mensajes."""
    return " ".join(p.capitalize() for p in nombre_jugador.split())

# =========================================================
# PALETA DE COLORES (estilo GBA colorido)
# =========================================================
SKY = (135, 185, 230)
CLOUD = (245, 239, 220)

FAR_TREE = (79, 116, 173)
MID_TREE = (102, 148, 87)
GRASS = (86, 125, 67)
DARK_GRASS = (49, 76, 46)
PATH = (181, 155, 112)

WOOD = (123, 78, 57)
WOOD_DARK = (84, 50, 39)
WOOD_LIGHT = (170, 114, 89)

CREAM = (245, 226, 177)
CREAM_DARK = (219, 196, 141)

ROOF_RED = (179, 94, 81)
ROOF_DARK = (121, 62, 58)

WALL_TEAL = (125, 165, 159)
WALL_TEAL_DARK = (80, 115, 112)
TRIM = (228, 212, 182)

BUTTON_BLUE = (76, 103, 119)
BUTTON_BLUE_DARK = (48, 67, 78)
BUTTON_HIGHLIGHT = (239, 210, 139)
BUTTON_HIGHLIGHT_DARK = (167, 109, 74)

RED_SIGN = (156, 79, 69)
RED_SIGN_DARK = (105, 50, 46)

BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
WINDOW_GLASS = (201, 223, 229)
LAMP_YELLOW = (251, 214, 120)
FLOWER_PURPLE = (180, 110, 190)
FLOWER_RED = (205, 84, 78)
ORANGE = (225, 144, 68)

# =========================================================
# FUENTES
# =========================================================
font_small = FuenteTienda(None, round(13 * MENU_SCALE))
font_medium = FuenteTienda(None, round(17 * MENU_SCALE))
font_large = FuenteTienda(None, round(22 * MENU_SCALE))
font_title = FuenteTienda(None, round(28 * MENU_SCALE))
font_hud = FuenteTienda(None, 17)
font_aviso = FuenteTienda(None, 15)     # aviso de abajo: con qué se interactúa

# =========================================================
# ESTADO DEL MENU
# =========================================================
menu_options = ["JUGAR", "CONTINUAR", "OPCIONES", "AYUDA", "SALIR"]
forzar_tutorial = False   # se eligió OPCIONES > TUTORIAL
selected_option = 0



# =========================================================
# DIBUJO DEL MENU: coordenadas 480x270 -> 640x360
# =========================================================

def _menu_scale(value):
    return int(round(value * MENU_SCALE))


def _menu_point(point):
    return tuple(_menu_scale(v) for v in point)


def _menu_rect(rect):
    return tuple(_menu_scale(v) for v in rect)


class MenuDraw:

    @staticmethod
    def rect(surface, color, rect, width=0, border_radius=0):
        return pygame.draw.rect(
            surface,
            color,
            _menu_rect(rect),
            _menu_scale(width),
            border_radius=_menu_scale(border_radius)
        )

    @staticmethod
    def circle(surface, color, center, radius, width=0):
        return pygame.draw.circle(
            surface,
            color,
            _menu_point(center),
            _menu_scale(radius),
            _menu_scale(width)
        )

    @staticmethod
    def line(surface, color, start_pos, end_pos, width=1):
        return pygame.draw.line(
            surface,
            color,
            _menu_point(start_pos),
            _menu_point(end_pos),
            max(1, _menu_scale(width))
        )

    @staticmethod
    def polygon(surface, color, points, width=0):
        return pygame.draw.polygon(
            surface,
            color,
            [_menu_point(point) for point in points],
            _menu_scale(width)
        )

    @staticmethod
    def ellipse(surface, color, rect, width=0):
        return pygame.draw.ellipse(
            surface,
            color,
            _menu_rect(rect),
            _menu_scale(width)
        )


menu_draw = MenuDraw()


# =========================================================
# HELPERS
# =========================================================
def draw_text(
    surface,
    text,
    font,
    color,
    x,
    y,
    center=False,
    shadow=False,
    shadow_color=(50, 50, 50)
):
    # Las posiciones siguen expresadas en las coordenadas originales
    # 480x270, pero el texto se rasteriza directamente en 640x360.
    x = round(x * MENU_SCALE)
    y = round(y * MENU_SCALE)

    if shadow:
        shadow_surf = font.render(text, False, shadow_color)
        shadow_rect = shadow_surf.get_rect()

        if center:
            shadow_rect.center = (x + 1, y + 1)
        else:
            shadow_rect.topleft = (x + 1, y + 1)

        surface.blit(shadow_surf, shadow_rect)

    text_surf = font.render(text, False, color)
    rect = text_surf.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(text_surf, rect)


def draw_pixel_cloud(surface, x, y, scale=1):
    rects = [
        (0, 8, 18, 8),
        (8, 0, 18, 12),
        (20, 4, 16, 12),
        (28, 8, 14, 8),
        (10, 12, 20, 8)
    ]
    for rx, ry, rw, rh in rects:
        menu_draw.rect(surface, CLOUD, (x + rx * scale, y + ry * scale, rw * scale, rh * scale))


MENU_DESPLAZAMIENTO = 130    # la pulpería va a la derecha, el letrero a la izquierda
_fondo_menu = None


def fondo_menu():
    """La misma pulpería del juego (vista desde la calle), corrida a la
    derecha para que el letrero del menú no la tape. Canela, en el techo."""
    global _fondo_menu
    if _fondo_menu is None:
        from ambiente import sprite_gato
        base = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        dibujar_entrada(base, etiqueta=False)
        fondo = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        d = MENU_DESPLAZAMIENTO
        fondo.blit(base, (d, 0))
        fondo.blit(base, (0, 0), (GAME_WIDTH - d, 0, d, GAME_HEIGHT))
        if MASCOTAS["gata"]:
            gata = sprite_gato((236, 150, 60), 0, False, False)
            fondo.blit(gata, gata.get_rect(midbottom=(550, 70)))
        if MASCOTAS["perro"]:
            from perro import imagen_perro
            bruno = imagen_perro((176, 120, 70), None, None, 0, True)
            fondo.blit(bruno, bruno.get_rect(midbottom=(252 + d, 214)))
        _fondo_menu = fondo
    return _fondo_menu


def draw_background(surface):
    """Fondo del menú y de OPCIONES: la pulpería del juego."""
    surface.blit(fondo_menu(), (0, 0))


def _draw_background_viejo(surface):
    surface.fill(SKY)

    # Nubes
    draw_pixel_cloud(surface, 10, 20, 1)
    draw_pixel_cloud(surface, 70, 35, 1)
    draw_pixel_cloud(surface, 240, 18, 1)
    draw_pixel_cloud(surface, 370, 30, 1)
    draw_pixel_cloud(surface, 410, 15, 1)

    # Arboles lejanos / siluetas
    menu_draw.rect(surface, FAR_TREE, (0, 120, GAME_WIDTH, 55))
    menu_draw.circle(surface, FAR_TREE, (35, 118), 28)
    menu_draw.circle(surface, FAR_TREE, (90, 126), 24)
    menu_draw.circle(surface, FAR_TREE, (280, 125), 22)
    menu_draw.circle(surface, FAR_TREE, (450, 118), 35)

    # Capa media
    menu_draw.rect(surface, MID_TREE, (0, 160, GAME_WIDTH, 28))

    # Suelo
    menu_draw.rect(surface, GRASS, (0, 188, GAME_WIDTH, 82))
    menu_draw.rect(surface, DARK_GRASS, (0, 236, GAME_WIDTH, 34))

    # Caminito
    menu_draw.ellipse(surface, PATH, (20, 218, 200, 28))
    menu_draw.ellipse(surface, PATH, (150, 220, 170, 24))

    # Pasto decorativo inferior
    for x in range(0, GAME_WIDTH, 8):
        h = 4 + (x % 3)
        menu_draw.line(surface, DARK_GRASS, (x, 236), (x + 1, 236 - h), 1)

    # Flores blancas
    for pos in [(18, 228), (28, 232), (46, 224), (70, 230), (330, 228), (355, 234), (400, 226), (430, 232)]:
        menu_draw.circle(surface, WHITE, pos, 2)
        menu_draw.circle(surface, (220, 210, 90), pos, 1)


def draw_wood_post():

    menu_draw.rect(
        game_surface, WOOD_DARK,
        (12, 10, 8, 200)
    )

    menu_draw.rect(
        game_surface, WOOD,
        (14, 12, 4, 196)
    )

    menu_draw.rect(
        game_surface, WOOD_DARK,
        (12, 10, 150, 8)
    )

    menu_draw.rect(
        game_surface, WOOD,
        (14, 12, 146, 4)
    )


def draw_lantern(surface):

    menu_draw.line(
        surface, BLACK,
        (157, 16), (157, 25), 1
    )

    menu_draw.polygon(
        surface, BLACK,
        [(152, 25), (162, 25), (165, 30), (149, 30)]
    )

    menu_draw.rect(
        surface, LAMP_YELLOW,
        (152, 30, 10, 12)
    )

    menu_draw.rect(
        surface, BLACK,
        (152, 30, 10, 12), 1
    )

def draw_title_sign(surface):

    # Letrero más pequeño: deja ver la pulpería.
    sign = pygame.Rect(24, 22, 124, 46)

    menu_draw.rect(surface, WOOD_DARK, sign, border_radius=6)
    menu_draw.rect(
        surface, RED_SIGN,
        sign.inflate(-4, -4),
        border_radius=5
    )

    # Remaches
    for p in [(30, 28), (142, 28), (30, 62), (142, 62)]:
        menu_draw.circle(surface, CREAM_DARK, p, 2)

    draw_text(
        surface, "LA", font_medium,
        CREAM, 86, 33, center=True, shadow=True
    )

    draw_text(
        surface, "PULPERÍA", font_title,
        CREAM, 86, 52, center=True, shadow=True
    )


def draw_menu_button(surface, x, y, w, h, text, selected=False):

    if selected:
        outer = BUTTON_HIGHLIGHT_DARK
        inner = BUTTON_HIGHLIGHT
        text_color = WOOD_DARK
    else:
        outer = BUTTON_BLUE_DARK
        inner = BUTTON_BLUE
        text_color = CREAM

    menu_draw.rect(surface, outer, (x, y, w, h), border_radius=5)

    menu_draw.rect(
        surface, inner,
        (x + 2, y + 2, w - 4, h - 4),
        border_radius=4
    )

    # Remaches
    for px, py in [
        (x + 7, y + 7),
        (x + w - 7, y + 7),
        (x + 7, y + h - 7),
        (x + w - 7, y + h - 7)
    ]:
        menu_draw.circle(surface, CREAM_DARK, (px, py), 1)

    if selected:
        menu_draw.polygon(
            surface, BUTTON_HIGHLIGHT_DARK,
            [(x - 7, y + h // 2),
             (x - 2, y + h // 2 - 4),
             (x - 2, y + h // 2 + 4)]
        )

    draw_text(
        surface, text, font_medium, text_color,
        x + w // 2, y + h // 2,
        center=True,
        shadow=not selected
    )


def draw_shop(surface):

    # -----------------------------------------------------
    # DIMENSIONES GENERALES
    # -----------------------------------------------------

    left = 242
    right = 470
    center = 356

    # Sombra del edificio
    menu_draw.ellipse(
        surface, DARK_GRASS,
        (left, 229, 228, 12)
    )

    # -----------------------------------------------------
    # FRONTON Y TECHO SUPERIOR
    # -----------------------------------------------------

    menu_draw.polygon(
        surface, ROOF_DARK,
        [(238, 104), (center, 43), (474, 104)]
    )

    menu_draw.polygon(
        surface, ROOF_RED,
        [(244, 101), (center, 49), (468, 101)]
    )

    menu_draw.polygon(
        surface, WALL_TEAL,
        [(252, 101), (center, 55), (460, 101)]
    )

    # Tablillas verticales
    for x in range(263, 455, 10):
        menu_draw.line(
            surface, WALL_TEAL_DARK,
            (x, 94), (x, 101), 1
        )

    # Ventilación
    menu_draw.rect(
        surface, WOOD_DARK,
        (345, 69, 22, 13)
    )

    menu_draw.rect(
        surface, CREAM_DARK,
        (347, 71, 18, 9)
    )

    for y in [73, 76, 79]:
        menu_draw.line(
            surface, WOOD_DARK,
            (349, y), (363, y), 1
        )

    # -----------------------------------------------------
    # TECHO PRINCIPAL
    # -----------------------------------------------------

    menu_draw.rect(
        surface, ROOF_DARK,
        (238, 98, 236, 25)
    )

    menu_draw.rect(
        surface, ROOF_RED,
        (240, 99, 232, 22)
    )

    for x in range(246, 469, 9):
        menu_draw.line(
            surface, ROOF_DARK,
            (x, 100), (x + 5, 121), 1
        )

    # -----------------------------------------------------
    # FACHADA
    # -----------------------------------------------------

    menu_draw.rect(
        surface, WALL_TEAL_DARK,
        (250, 120, 212, 116)
    )

    menu_draw.rect(
        surface, WALL_TEAL,
        (253, 122, 206, 112)
    )

    # Tablillas horizontales
    for y in range(130, 234, 9):
        menu_draw.line(
            surface, WALL_TEAL_DARK,
            (254, y), (458, y), 1
        )

    # Columnas
    for x in [250, 310, 452, 461]:
        menu_draw.rect(
            surface, WOOD_DARK,
            (x, 120, 6, 116)
        )

        menu_draw.rect(
            surface, TRIM,
            (x + 1, 121, 4, 114)
        )

    # -----------------------------------------------------
    # PUERTA
    # -----------------------------------------------------

    menu_draw.rect(
        surface, WOOD_DARK,
        (266, 149, 43, 86)
    )

    menu_draw.rect(
        surface, WOOD,
        (269, 152, 37, 80)
    )

    menu_draw.rect(
        surface, WINDOW_GLASS,
        (274, 158, 27, 30)
    )

    menu_draw.line(
        surface, WOOD_DARK,
        (287, 158), (287, 188), 2
    )

    menu_draw.rect(
        surface, WOOD_LIGHT,
        (274, 195, 27, 31)
    )

    menu_draw.circle(
        surface, CREAM_DARK,
        (300, 208), 2
    )

    # Escalón
    menu_draw.rect(
        surface, (153, 145, 130),
        (262, 234, 51, 5)
    )

    # -----------------------------------------------------
    # VENTANA DE PRODUCTOS
    # -----------------------------------------------------

    wx = 317
    wy = 129
    ww = 132
    wh = 76

    menu_draw.rect(
        surface, WOOD_DARK,
        (wx - 3, wy - 3, ww + 6, wh + 6)
    )

    menu_draw.rect(
        surface, WINDOW_GLASS,
        (wx, wy, ww, wh)
    )

    # Estanterías
    for y in [151, 176, 194]:
        menu_draw.line(
            surface, WOOD_DARK,
            (wx, y), (wx + ww, y), 2
        )

    # Productos
    product_colors = [
        RED_SIGN,
        BUTTON_BLUE,
        BUTTON_HIGHLIGHT_DARK,
        WOOD_LIGHT
    ]

    for row, y in enumerate([135, 157, 181]):
        for col, x in enumerate(range(wx + 5, wx + 125, 15)):

            color = product_colors[(row + col) % 4]

            menu_draw.rect(
                surface, color,
                (x, y, 9, 12)
            )

            menu_draw.rect(
                surface, CREAM_DARK,
                (x + 2, y + 3, 5, 2)
            )

    # Canasta de pan
    menu_draw.rect(
        surface, WOOD_LIGHT,
        (wx + 76, 185, 34, 9)
    )

    for x in range(wx + 79, wx + 106, 7):
        menu_draw.ellipse(
            surface, CREAM_DARK,
            (x, 179, 8, 9)
        )

    # -----------------------------------------------------
    # LETREROS INFERIORES
    # -----------------------------------------------------

    menu_draw.rect(
        surface, BUTTON_BLUE_DARK,
        (317, 211, 39, 19)
    )

    menu_draw.rect(
        surface, BUTTON_BLUE,
        (319, 213, 35, 15)
    )

    draw_text(
        surface, "PULPE", font_small,
        CREAM, 336, 220, center=True
    )

    menu_draw.rect(
        surface, RED_SIGN_DARK,
        (359, 211, 42, 19)
    )

    menu_draw.rect(
        surface, RED_SIGN,
        (361, 213, 38, 15)
    )

    draw_text(
        surface, "COLA", font_small,
        WHITE, 380, 220, center=True
    )

    # -----------------------------------------------------
    # CAJONES DE BOTELLAS
    # -----------------------------------------------------

    for y in [192, 212]:

        menu_draw.rect(
            surface, RED_SIGN_DARK,
            (450, y, 18, 17)
        )

        menu_draw.rect(
            surface, RED_SIGN,
            (452, y + 2, 14, 13)
        )

        for x in [455, 461]:
            menu_draw.rect(
                surface, BLACK,
                (x, y + 5, 3, 7)
            )

    # -----------------------------------------------------
    # DECORACION EXTERIOR
    # -----------------------------------------------------

    # Maceta
    menu_draw.rect(
        surface, WOOD_DARK,
        (251, 222, 13, 12)
    )

    menu_draw.rect(
        surface, WOOD,
        (253, 222, 9, 10)
    )

    # Flores
    for p in [(254, 217), (260, 215), (266, 218)]:
        menu_draw.circle(
            surface, FLOWER_RED, p, 3
        )


def draw_main_menu(surface, selected):

    # Pulpería: ya está en el fondo (la misma del juego).

    # Estructura del cartel
    draw_wood_post()
    draw_lantern(surface)
    draw_title_sign(surface)

    # Botones
    # Botones más pequeños: el letrero no tapa media pantalla.
    button_x = 28
    button_y = 78
    button_w = 116
    button_h = 18
    gap = 5

    for i, option in enumerate(menu_options):

        draw_menu_button(
            surface,
            button_x,
            button_y + i * (button_h + gap),
            button_w,
            button_h,
            option,
            selected=(i == selected)
        )

    # Ayuda de la opción marcada (el botón está en coordenadas del menú).
    if (confirmar_nueva is None and elegir_modo is None and pregunta_tutorial is None
            and elegir_continuar is None):
        opcion = menu_options[selected]
        ancla = pygame.Rect(round(button_x * MENU_SCALE),
                            round((button_y + selected * (button_h + gap)) * MENU_SCALE),
                            round(button_w * MENU_SCALE), round(button_h * MENU_SCALE))
        texto = TOOLTIP_MENU.get(opcion, "")
        if opcion == "CONTINUAR" and not partidas_disponibles():
            texto = "Todavía no hay una partida guardada."
        dibujar_tooltip(surface, ancla, texto, "derecha")




def draw_options_menu(surface):
    """Pantalla OPCIONES: sonido, gráficos, dificultad, modo de juego y tutorial."""
    draw_background(surface)
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 120))
    surface.blit(overlay, (0, 0))

    panel = pygame.Rect(60, 18, 520, 324)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (66, 24, 508, 40))
    title = font_title.render("OPCIONES", False, CREAM)
    surface.blit(title, title.get_rect(center=(320, 44)))

    dificultad = NIVELES[nivel_actual]["nombre"]
    filas = (
        (FILA_SONIDO, "SONIDO", sonido.estilo.title() + "  >"),
        (FILA_VISUAL, "GRÁFICOS", "Letra y colores  >"),
        (FILA_DIFICULTAD, "DIFICULTAD", f"<  {dificultad}  >"),
        (FILA_MODO, "MODO DE JUEGO", f"{sum(MODO.values())} de {len(MODO)} activos  >"),
        (FILA_EXTRAS, "EXTRAS", "Mascotas y ropa  >"),
        (FILA_TUTORIAL, "TUTORIAL", "Aprende a jugar  >"),
    )
    for fila_indice, nombre, valor in filas:
        fila = pygame.Rect(92, 74 + fila_indice * 33, 456, 28)
        elegido = opciones_seleccion == fila_indice
        fill = BUTTON_HIGHLIGHT if elegido else BUTTON_BLUE
        border = BUTTON_HIGHLIGHT_DARK if elegido else BUTTON_BLUE_DARK
        pygame.draw.rect(surface, border, fila.move(0, 3))
        pygame.draw.rect(surface, fill, fila)
        pygame.draw.rect(surface, border, fila, 2)
        if elegido:
            pygame.draw.polygon(surface, BUTTON_HIGHLIGHT_DARK, [
                (fila.x - 12, fila.centery - 6), (fila.x - 4, fila.centery),
                (fila.x - 12, fila.centery + 6)])
        color = WOOD_DARK if elegido else CREAM
        t = font_large.render(nombre, False, color)
        surface.blit(t, t.get_rect(midleft=(fila.x + 14, fila.centery + 1)))
        v = font_medium.render(valor, False, RED_SIGN if elegido else CREAM)
        surface.blit(v, v.get_rect(midright=(fila.right - 14, fila.centery + 1)))

    # Descripción de lo señalado.
    caja = pygame.Rect(92, 276, 456, 46)
    pygame.draw.rect(surface, CREAM, caja)
    pygame.draw.rect(surface, WOOD_DARK, caja, 2)
    if opciones_seleccion == FILA_SONIDO:
        lineas = ("Música de fondo, efectos especiales y ruido de fondo.",)
    elif opciones_seleccion == FILA_VISUAL:
        lineas = ("Tipo de letra, luciérnagas, avisos y colores.",)
    elif opciones_seleccion == FILA_DIFICULTAD:
        datos = NIVELES[nivel_actual]
        lineas = (f"{datos['nombre']}: {datos['habilidad']}.",
                  " ".join(datos["descripcion"][:2]))
    elif opciones_seleccion == FILA_MODO:
        lineas = ("Elige qué problemas aparecen: sucesiones, fracciones,",
                  "vuelto, paciencia de los clientes y más.")
    elif opciones_seleccion == FILA_EXTRAS:
        lineas = ("Enciende o apaga las mascotas y la ropa",
                  "(armario de la bodega).")
    else:
        lineas = ("Una partida guiada, paso a paso, para aprender",
                  "a atender la pulpería. Siempre es la misma.")
    y0 = caja.centery - len(lineas) * 9
    for j, linea in enumerate(lineas):
        t = font_small.render(linea, False, WOOD_DARK)
        if t.get_width() > caja.w - 16:
            t = font_small.render(linea[:62] + "...", False, WOOD_DARK)
        surface.blit(t, t.get_rect(midtop=(caja.centerx, y0 + j * 18)))



AYUDA_CONTROLES = [
    ("MOVERSE", [
        ("FLECHAS / WASD", "Caminar"),
        ("ESC", "Pausa (ayuda / salir)"),
    ]),
    ("PRODUCTOS", [
        ("E", "Tomar, dejar o acomodar"),
        ("CLIC", "Elegir el producto"),
        ("Q", "Devolver el último"),
        ("ESPACIO", "Empujar / soltar carrito"),
    ]),
    ("CLIENTES Y CAJA", [
        ("E en la caja", "Abrir la factura"),
        ("NÚMEROS + ENTER", "Responder"),
        ("P", "Que repita el pedido"),
        ("C en la factura", "Calculadora (cuesta ₡)"),
    ]),
    ("AYUDAS", [
        ("R o el libro", "Libro de recetas"),
        ("H", "Ventas de hoy"),
        ("E en el letrero", "Abrir / cerrar tienda"),
        ("E en el armario", "Ropa (en la bodega)"),
        ("SHIFT + E", "Mover muebles"),
    ]),
]


def draw_help_menu(surface):
    """Pantalla AYUDA: todos los controles del juego."""
    draw_background(surface)
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 120))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(30, 14, 580, 332)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (36, 20, 568, 36))
    title = font_title.render("AYUDA: ¿CÓMO SE JUEGA?", False, CREAM)
    surface.blit(title, title.get_rect(center=(320, 38)))

    for n, (seccion, filas) in enumerate(AYUDA_CONTROLES):
        col, fila = n % 2, n // 2
        x = 48 + col * 284
        y = 66 + fila * 128
        t = font_medium.render(seccion, False, RED_SIGN)
        surface.blit(t, (x, y))
        for k, (tecla, accion) in enumerate(filas):
            yy = y + 22 + k * 24
            tt = font_small.render(tecla, False, CREAM)
            chip = tt.get_rect(topleft=(x, yy)).inflate(10, 6)
            chip.topleft = (x, yy)
            pygame.draw.rect(surface, BUTTON_BLUE_DARK, chip)
            surface.blit(tt, tt.get_rect(center=chip.center))
            ta = font_small.render(accion, False, WOOD_DARK)
            surface.blit(ta, (x + (136 if col == 0 else 104), yy + 3))

    # (Sin texto de pie: se encimaba con la última fila y los niños leen poco.)


# ---------------------------------------------------------
# REPORTE (OPCIONES > EXTRAS): progreso del niño para el profesor o el padre
# ---------------------------------------------------------
reporte_aviso = None        # mensaje después de guardar el CSV
CARPETA_REPORTE = os.path.dirname(os.path.abspath(__file__))


reporte_modo = None          # de qué partida se ve el reporte ("historia" / "libre")


def abrir_reporte():
    """REPORTE: empieza por la partida abierta (o la última jugada)."""
    global current_scene, reporte_modo, reporte_aviso
    reporte_aviso = None
    disp = partidas_disponibles()
    actual = modo_partida() if partida_en_juego() else ultimo_modo
    reporte_modo = actual if actual in disp else (disp[0] if disp else None)
    current_scene = "reporte"


def cambiar_reporte(paso):
    """← / →: el reporte de la otra partida (historia o libre)."""
    global reporte_modo, reporte_aviso
    disp = partidas_disponibles()
    if len(disp) < 2:
        return
    i = disp.index(reporte_modo) if reporte_modo in disp else 0
    reporte_modo = disp[(i + paso) % len(disp)]
    reporte_aviso = None


def datos_reporte():
    """(nombre, día, nombre del nivel, estadísticas) de la partida del reporte;
    estadísticas None = las de la partida abierta. None si no hay partida."""
    modo = reporte_modo
    if modo is None:
        return None
    if partida_en_juego() and modo_partida() == modo:
        return nombre_bonito(), dia, NIVELES[nivel_actual]["nombre"], None
    d = leer_partida(modo)
    if d is None:
        return None
    nivel = d.get("nivel") if modo == "historia" and d.get("nivel") in NIVELES else nivel_actual
    nombre = " ".join(p.capitalize() for p in d["jugador"]["nombre"].split())
    return nombre, d.get("dia", 1), NIVELES[nivel]["nombre"], d.get("estadisticas") or {}


def guardar_reporte_csv():
    global reporte_aviso
    info = datos_reporte()
    if info is None:
        reporte_aviso = "Primero juega una partida."
        return
    nombre_r, dia_r, nivel_r, est = info
    nombre = "".join(c for c in nombre_r if c.isalnum()) or "jugador"
    ruta = os.path.join(CARPETA_REPORTE, f"reporte_{nombre}_{reporte_modo}.csv")
    try:
        estadisticas.exportar_csv(ruta, nombre_r, dia_r, nivel_r, est, NOMBRE_MODO[reporte_modo])
        reporte_aviso = f"Guardado: {os.path.basename(ruta)} (en la carpeta del juego)"
        sonido.efecto("acierto")
    except OSError:
        reporte_aviso = "No se pudo guardar el archivo."


def draw_reporte(surface):
    """Tabla con las opciones activas del MODO DE JUEGO: aciertos, errores y
    % de aciertos, y cuántas veces se usó la calculadora."""
    draw_background(surface)
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 140))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(24, 10, 592, 340)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (30, 16, 580, 32))
    t = font_title.render("REPORTE DE PROGRESO", False, CREAM)
    surface.blit(t, t.get_rect(center=(320, 32)))
    info = datos_reporte()
    if info is None:
        m = font_medium.render("Todavía no hay una partida guardada.", False, WOOD_DARK)
        surface.blit(m, m.get_rect(center=(320, 180)))
        tv = font_small.render("ESC: volver", False, BUTTON_BLUE_DARK)
        surface.blit(tv, tv.get_rect(center=(320, 326)))
        return
    nombre_r, dia_r, nivel_r, est = info
    otra = len(partidas_disponibles()) > 1
    flechas = ("<  ", "  >") if otra else ("", "")
    sub = font_small.render(
        f"{flechas[0]}MODO {NOMBRE_MODO[reporte_modo]}{flechas[1]}     Jugador: {nombre_r}"
        f"     Día: {dia_r}     Nivel: {nivel_r}",
        False, WOOD_DARK)
    surface.blit(sub, sub.get_rect(center=(320, 60)))
    for x, titulo in zip((40, 330, 420, 500), ("OPCIÓN ACTIVA", "ACIERTOS", "ERRORES", "% ACIERTOS")):
        surface.blit(font_small.render(titulo, False, BUTTON_BLUE_DARK), (x, 74))
    pygame.draw.line(surface, WOOD_DARK, (36, 90), (604, 90), 2)
    filas = estadisticas.filas(est)
    alto = min(24, max(16, (264 - 94) // max(1, len(filas))))
    y = 94
    for i, (nombre, habilidad, a, e, pct) in enumerate(filas):
        r = pygame.Rect(36, y, 568, alto - 2)
        pygame.draw.rect(surface, (236, 220, 180) if i % 2 == 0 else (226, 206, 158), r)
        tn = _texto_cabe(nombre.capitalize(), font_small, WOOD_DARK, 282)
        surface.blit(tn, tn.get_rect(midleft=(42, r.centery + 1)))
        for x, valor, color in ((330, a, (66, 130, 70)), (420, e, (176, 48, 42))):
            tv = font_medium.render(str(valor), False, color)
            surface.blit(tv, tv.get_rect(midleft=(x + 18, r.centery + 1)))
        barra = pygame.Rect(500, r.y + 4, 70, max(6, r.h - 8))
        pygame.draw.rect(surface, (196, 180, 140), barra)
        if pct is not None:
            lleno = barra.copy()
            lleno.w = round(barra.w * pct / 100)
            pygame.draw.rect(surface, (66, 130, 70) if pct >= 70 else (220, 170, 60) if pct >= 40
                             else (196, 84, 70), lleno)
        pygame.draw.rect(surface, WOOD_DARK, barra, 1)
        tp = font_small.render(f"{pct}%" if pct is not None else "-", False, WOOD_DARK)
        surface.blit(tp, tp.get_rect(midleft=(barra.right + 4, r.centery + 1)))
        y += alto
    veces = estadisticas.calculadora_de(est)
    caja = pygame.Rect(36, 270, 568, 34)
    pygame.draw.rect(surface, CREAM, caja)
    pygame.draw.rect(surface, WOOD_DARK, caja, 2)
    tc = _texto_cabe(f"Calculadora comprada: {veces} {'vez' if veces == 1 else 'veces'}",
                     font_medium, WOOD_DARK, caja.w - 16)
    surface.blit(tc, tc.get_rect(center=caja.center))
    pie = reporte_aviso or ("ENTER: guardar (CSV, se abre con Excel)   < >: otra partida   ESC: volver"
                            if otra else
                            "ENTER: guardar la tabla (archivo CSV, se abre con Excel)      ESC: volver")
    tp = font_small.render(pie, False, (66, 115, 67) if reporte_aviso else BUTTON_BLUE_DARK)
    surface.blit(tp, tp.get_rect(center=(320, 326)))


def draw_extras(surface):
    """OPCIONES > EXTRAS: mascotas sí/no (y cuáles) y personalización sí/no."""
    draw_background(surface)
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 120))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(90, 50, 460, 214 + 40)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (panel.x + 6, panel.y + 6, panel.w - 12, 34))
    title = font_title.render("EXTRAS", False, CREAM)
    surface.blit(title, title.get_rect(center=(panel.centerx, panel.y + 23)))

    nombres = {"mascotas": "MASCOTAS", "cuales": "CUÁLES",
               "personalizacion": "PERSONALIZACIÓN", "reporte": "REPORTE DE PROGRESO"}
    for i, clave in enumerate(FILAS_EXTRAS):
        apagada = clave == "cuales" and not EXTRAS["mascotas"]
        fila = pygame.Rect(panel.x + 26, panel.y + 54 + i * 40, panel.w - 52, 30)
        if clave == "cuales":
            fila = fila.inflate(-40, -6).move(20, 0)      # depende de MASCOTAS
        elegido = i == extras_seleccion
        fondo = (210, 196, 160) if apagada else (CREAM if elegido else (226, 206, 158))
        pygame.draw.rect(surface, fondo, fila)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK if elegido else WOOD_DARK,
                         fila, 3 if elegido else 1)
        if elegido:
            pygame.draw.polygon(surface, BUTTON_HIGHLIGHT_DARK, [
                (fila.x - 12, fila.centery - 6), (fila.x - 4, fila.centery),
                (fila.x - 12, fila.centery + 6)])
        color = (150, 136, 110) if apagada else WOOD_DARK
        t = font_medium.render(nombres[clave], False, color)
        surface.blit(t, t.get_rect(midleft=(fila.x + 10, fila.centery + 1)))
        if clave == "cuales":
            v = font_small.render(f"<  {texto_mascotas()}  >", False,
                                  color if apagada else RED_SIGN)
            surface.blit(v, v.get_rect(midright=(fila.right - 10, fila.centery + 1)))
            continue
        if clave == "reporte":
            v = font_small.render("VER  >", False, RED_SIGN)
            surface.blit(v, v.get_rect(midright=(fila.right - 10, fila.centery + 1)))
            continue
        for k, (texto, valor) in enumerate((("NO", False), ("SÍ", True))):
            boton = pygame.Rect(fila.right - 92 + k * 42, 0, 36, 16)
            boton.centery = fila.centery
            activo = EXTRAS[clave] == valor
            c = ((66, 130, 70) if valor else (176, 48, 42)) if activo else (196, 180, 140)
            pygame.draw.rect(surface, c, boton)
            pygame.draw.rect(surface, WOOD_DARK, boton, 2)
            tt = font_small.render(texto, False, CREAM if activo else WOOD_DARK)
            surface.blit(tt, tt.get_rect(center=boton.center))
    # Ayuda de la fila marcada.
    clave = FILAS_EXTRAS[extras_seleccion]
    fila = pygame.Rect(panel.x + 26, panel.y + 54 + extras_seleccion * 40, panel.w - 52, 30)
    dibujar_tooltip(surface, pygame.Rect(fila.centerx - 60, fila.y, 120, fila.h),
                    TOOLTIP_EXTRAS.get(clave, ""), "abajo", 260)


def draw_modo_juego(surface):
    """OPCIONES > MODO DE JUEGO: activar o apagar cada tipo de problema."""
    draw_background(surface)
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 120))
    surface.blit(overlay, (0, 0))
    panel = pygame.Rect(40, 12, 560, 336)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (46, 18, 548, 34))
    title = font_title.render("MODO DE JUEGO", False, CREAM)
    surface.blit(title, title.get_rect(center=(320, 35)))
    sub = font_small.render("¿Qué problemas quieres practicar? (la factura siempre está)",
                            False, WOOD_DARK)
    surface.blit(sub, sub.get_rect(center=(320, 62)))

    for i, clave in enumerate(modos.ORDEN):
        nombre, habilidad, _, _ = modos.INFO[clave]
        fila = pygame.Rect(66, 72 + i * 24, 508, 22)
        elegido = i == modo_seleccion
        pygame.draw.rect(surface, CREAM if elegido else (226, 206, 158), fila)
        pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK if elegido else WOOD_DARK, fila, 3 if elegido else 1)
        if elegido:
            pygame.draw.polygon(surface, BUTTON_HIGHLIGHT_DARK, [
                (fila.x - 12, fila.centery - 6), (fila.x - 4, fila.centery),
                (fila.x - 12, fila.centery + 6)])
        t = font_small.render(nombre, False, WOOD_DARK)
        surface.blit(t, t.get_rect(midleft=(fila.x + 10, fila.centery + 1)))
        for k, (texto, valor) in enumerate((("NO", False), ("SÍ", True))):
            boton = pygame.Rect(fila.right - 92 + k * 42, 0, 36, 14)
            boton.centery = fila.centery
            activo = MODO[clave] == valor
            color = ((66, 130, 70) if valor else (176, 48, 42)) if activo else (196, 180, 140)
            pygame.draw.rect(surface, color, boton)
            pygame.draw.rect(surface, WOOD_DARK, boton, 2)
            tt = font_small.render(texto, False, CREAM if activo else WOOD_DARK)
            surface.blit(tt, tt.get_rect(center=boton.center))

    clave = modos.ORDEN[modo_seleccion]
    _, habilidad, si, no = modos.INFO[clave]
    caja = pygame.Rect(66, 294, 508, 30)
    pygame.draw.rect(surface, CREAM, caja)
    pygame.draw.rect(surface, WOOD_DARK, caja, 2)
    h = font_small.render(f"{habilidad.upper()}:", False, RED_SIGN)
    surface.blit(h, (caja.x + 8, caja.y + 8))
    d = font_small.render(si if MODO[clave] else no, False, WOOD_DARK)
    surface.blit(d, (caja.x + 16 + h.get_width(), caja.y + 8))


def draw_skin_menu(surface):
    """Pantalla para elegir el personaje antes de empezar."""
    draw_background(surface)
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 120))
    surface.blit(overlay, (0, 0))

    panel = pygame.Rect(60, 18, 520, 324)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (66, 24, 508, 40))
    title = font_title.render("¿CON QUIÉN QUIERES JUGAR?", False, CREAM)
    surface.blit(title, title.get_rect(center=(320, 44)))

    # Animación de caminar en su lugar.
    paso = (pygame.time.get_ticks() // 300) % 2
    for i, clave in enumerate(SKINS_ORDEN):
        tarjeta = pygame.Rect(118 + i * 220, 82, 184, 204)
        elegido = i == skin_seleccion
        borde = BUTTON_HIGHLIGHT_DARK if elegido else BUTTON_BLUE_DARK
        pygame.draw.rect(surface, (35, 27, 27), tarjeta.move(3, 3))
        pygame.draw.rect(surface, CREAM if elegido else (196, 180, 140), tarjeta)
        pygame.draw.rect(surface, borde, tarjeta, 4 if elegido else 2)

        muestra = skin_muestras[clave]
        imagen = muestra.frames["down"][paso if elegido else 0]
        grande = pygame.transform.scale_by(imagen, 3)
        piso = pygame.Rect(0, 0, 70, 12)
        piso.center = (tarjeta.centerx, tarjeta.y + 170)
        pygame.draw.ellipse(surface, (160, 140, 104), piso)
        surface.blit(grande, grande.get_rect(midbottom=(tarjeta.centerx, tarjeta.y + 174)))

        if elegido:
            for dx in (-1, 1):
                x = tarjeta.centerx + dx * 104
                pygame.draw.polygon(surface, BUTTON_HIGHLIGHT_DARK, [
                    (x, tarjeta.centery - 8), (x - dx * 8, tarjeta.centery),
                    (x, tarjeta.centery + 8)])



def draw_name_menu(surface):
    """Pantalla "¿CÓMO TE LLAMAS?" con el personaje elegido."""
    draw_background(surface)
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 120))
    surface.blit(overlay, (0, 0))

    panel = pygame.Rect(60, 18, 520, 324)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, RED_SIGN, (66, 24, 508, 40))
    title = font_title.render("¿CÓMO TE LLAMAS?", False, CREAM)
    surface.blit(title, title.get_rect(center=(320, 44)))

    # Personaje elegido, saludando con su animación.
    paso = (pygame.time.get_ticks() // 300) % 2
    muestra = skin_muestras[SKINS_ORDEN[skin_seleccion]]
    grande = pygame.transform.scale_by(muestra.frames["down"][paso], 3)
    piso = pygame.Rect(0, 0, 70, 12)
    piso.center = (170, 236)
    pygame.draw.ellipse(surface, (160, 140, 104), piso)
    surface.blit(grande, grande.get_rect(midbottom=(170, 240)))

    texto = font_medium.render("Escribe tu nombre:", False, WOOD_DARK)
    surface.blit(texto, (262, 118))
    caja = pygame.Rect(262, 144, 280, 44)
    pygame.draw.rect(surface, WOOD_DARK, caja.move(2, 3))
    pygame.draw.rect(surface, CREAM, caja)
    pygame.draw.rect(surface, BUTTON_HIGHLIGHT_DARK, caja, 3)
    nombre = font_title.render(nombre_jugador.upper(), False, WOOD_DARK)
    surface.blit(nombre, nombre.get_rect(midleft=(caja.x + 12, caja.centery + 1)))
    if (pygame.time.get_ticks() // 450) % 2 == 0 and len(nombre_jugador) < NOMBRE_MAX:
        cursor_x = caja.x + 14 + nombre.get_width()
        pygame.draw.rect(surface, WOOD_DARK, (cursor_x, caja.y + 10, 3, caja.h - 20))

    if nombre_aviso and not nombre_jugador.strip():
        aviso = font_small.render("¡Primero escribe tu nombre!", False, RED_SIGN)
        surface.blit(aviso, (264, 198))
    elif nombre_jugador.strip():
        saludo = font_medium.render(f"¡Hola, {nombre_bonito()}!", False, (66, 115, 67))
        surface.blit(saludo, (264, 198))



def draw_furniture_hud(surface):
    """Muestra los controles contextuales de objetos, muebles y caja."""
    if not avisos_activos or dialogo is not None:
        return                  # GRÁFICOS > AVISOS DE ABAJO: NO (o habla Doña Rosa)
    mano = table_object_manager.mano
    if cerca_letrero() and furniture_manager.carrying is None:
        message = texto_letrero()

    elif carrito.cerca(player, "interior") and furniture_manager.carrying is None:
        message = "ESPACIO: EMPUJAR CARRITO"

    elif carrito.cerca_ayudante(player, "interior") and furniture_manager.carrying is None:
        message = f"ESPACIO: PEDIRLE EL CARRITO A {ayudante.nombre.upper()}"

    elif cerca_de_ayudante():
        message = f"E: PAGARLE A {ayudante.nombre.upper()}"

    elif cerca_boton(player) and furniture_manager.carrying is None:
        message = (f"{ayudante.nombre.upper()} ESTÁ TRABAJANDO" if ayudante.presente
                   else "E: LLAMAR AL AYUDANTE")

    elif mano and acceso_actual("interior", player) is None:
        message = table_object_manager.texto_e(player, furniture_manager)

    elif furniture_manager.carrying is not None:
        label = furniture_manager.carrying["label"]
        message = f"FLECHAS / WASD: MOVER {label}    SHIFT+E: COLOCAR"

    else:
        puerta = acceso_actual("interior", player)
        register_target = table_object_manager.find_register_target(
            player, furniture_manager
        )
        object_target = table_object_manager.find_target(
            player, furniture_manager
        )
        furniture_target = furniture_manager.find_target(player)

        if puerta == "entrada":
            message = "CAMINA HACIA ABAJO: CALLE"
        elif puerta == "inventario":
            message = "CAMINA A LA DERECHA: INVENTARIO"
        elif not table_object_manager.mano and MASCOTAS["gata"] and mascota.cerca(player, "interior"):
            message = f"E: ACARICIAR A {mascota_nombre()}"
        elif not table_object_manager.mano and MASCOTAS["perro"] and perro.cerca(player, "interior"):
            message = f"E: ACARICIAR A {perro_nombre()}"
        elif not table_object_manager.mano and MASCOTAS["gata"] and casa_gato.cerca(player):
            message = f"E: CASA DE {mascota_nombre()}"
        elif table_object_manager.punto_del_mostrador(player, furniture_manager) == "recetario":
            message = "E: LIBRO DE RECETAS"
        elif table_object_manager.punto_del_mostrador(player, furniture_manager) == "telefono":
            message = ("E: TELÉFONO (PEDIDO EN CAMINO)" if camion.pendiente
                       else "E: TELÉFONO (PEDIR INSUMOS)")
        elif register_target is not None:
            message = "E: ABRIR CAJA"
        elif object_target is not None:
            message = "E: " + table_object_manager.etiqueta_tomar(
                object_target, furniture_manager
            )
        elif furniture_target is not None:
            message = f"SHIFT+E: MOVER {furniture_target['label']}"
        else:
            message = "E: OBJETOS Y CAJA  |  SHIFT+E: MUEBLES"

    # Aviso de abajo (con qué se interactúa).
    text_surface = font_aviso.render(message, False, CREAM)
    panel_w = text_surface.get_width() + 12
    panel_h = text_surface.get_height() + 6
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((43, 36, 43, 220))
    panel.blit(text_surface, (6, 3))
    surface.blit(
        panel,
        (GAME_WIDTH // 2 - panel_w // 2, GAME_HEIGHT - panel_h - 5)
    )


def format_colones(amount):
    """Formatea colones sin decimales y con separador de miles local."""
    return "₡" + f"{int(amount):,}".replace(",", ".")


# Coordenadas lógicas de la factura, antes del escalado 2x.
CHECKOUT_PAY_BUTTON = pygame.Rect(201, 300, 109, 24)
CHECKOUT_CANCEL_BUTTON = pygame.Rect(331, 300, 109, 24)
# Botón para comprar la calculadora (solo sirve para esta factura).
CHECKOUT_CALC_BUTTON = pygame.Rect(454, 300, 96, 24)
CHECKOUT_TOTAL_FIELD = pygame.Rect(412, 228, 125, 24)
CHECKOUT_VUELTO_FIELD = pygame.Rect(412, 258, 125, 22)
CHECKOUT_MAX_ROWS = 4


def checkout_visible_rows(exercise):
    """Devuelve los campos visibles, con desplazamiento para facturas largas."""
    n = len(exercise.filas)
    first = min(max(0, exercise.actual - CHECKOUT_MAX_ROWS + 1),
                max(0, n - CHECKOUT_MAX_ROWS))
    for index in range(first, min(n, first + CHECKOUT_MAX_ROWS)):
        yield index, pygame.Rect(412, 112 + (index - first) * 27, 125, 23)


def draw_invoice_input(surface, rect, exercise, index):
    """Un campo numérico con foco, valor y estado de validación."""
    active = index == exercise.actual
    correct = exercise.correctos[index]
    outline = (67, 133, 87) if correct else (174, 90, 63) if active else WOOD_DARK
    fill = (232, 239, 210) if correct else (255, 247, 220)
    pygame.draw.rect(surface, WOOD_DARK, rect.move(1, 2))
    pygame.draw.rect(surface, fill, rect)
    pygame.draw.rect(surface, outline, rect, 2)

    value = exercise.valores[index]
    if not value:
        shown = "?" if not active else "_"
    else:
        shown = format_colones(int(value))
    if correct:
        shown += "  OK"
    txt = font_medium.render(shown, False, outline if correct else WOOD_DARK)
    surface.blit(txt, txt.get_rect(midleft=(rect.x + 8, rect.centery)))


def draw_invoice_products(surface, group, x, centro_y):
    """Dibuja un producto por cada unidad comprada. Devuelve la x final."""
    kind = group.get("kind")
    if kind not in PRODUCTOS:
        return x
    imagen = sprite_producto(kind)
    q = group["quantity"]
    # Sin nombre escrito: los dibujos van grandes (si caben).
    if q <= 8:
        imagen = pygame.transform.scale_by(imagen, 2)
    for _ in range(q):
        surface.blit(imagen, imagen.get_rect(midleft=(x, centro_y)))
        x += imagen.get_width() + 2
    return x


def draw_vuelto(surface):
    """Paso extra del nivel avanzado: calcular el vuelto."""
    v = vuelto
    frente = clientes.cliente_esperando()
    quien = frente.nombre if frente else "El cliente"
    linea = font_medium.render(
        f"{quien} paga con {format_colones(v['pago'])}. ¿Cuánto vuelto le das?",
        False, WOOD_DARK)
    surface.blit(linea, linea.get_rect(center=(320, 214)))
    caja = pygame.Rect(250, 232, 140, 30)
    pygame.draw.rect(surface, CREAM, caja)
    pygame.draw.rect(surface, (66, 115, 67) if v["listo"] else BUTTON_HIGHLIGHT_DARK, caja, 3)
    valor = format_colones(v["esperado"]) if v["listo"] else (v["valor"] or "_")
    t = font_large.render(valor, False, WOOD_DARK)
    surface.blit(t, t.get_rect(center=caja.center))
    color = (66, 115, 67) if v["listo"] or v["mensaje"].startswith("Pista") else WOOD_DARK
    m = font_small.render(v["mensaje"], False, color)
    surface.blit(m, m.get_rect(center=(320, 278)))


def draw_reloj_hud(surface, y=4):
    """Reloj con sol o luna arriba a la izquierda. Devuelve dónde termina."""
    t = font_small.render(reloj.texto(), False, HUD_LETRA)
    caja = pygame.Rect(4, y, t.get_width() + 34, 22)
    _caja_hud(surface, caja)
    _hud_rects["reloj"] = caja.copy()
    reloj.dibujar_icono(surface, (caja.x + 13, caja.centery))
    surface.blit(t, (caja.x + 26, caja.y + 6))
    return caja.bottom + 4


def draw_estado_tienda_hud(surface, y):
    """ "TIENDA ABIERTA · C: CERRAR" en verde, o cerrada en rojo."""
    if clientes.abierta:
        texto, color = "TIENDA ABIERTA", (140, 220, 130)
    else:
        texto, color = "TIENDA CERRADA", (255, 130, 110)
    t = font_small.render(texto, False, color)
    caja = t.get_rect(topleft=(8, y)).inflate(12, 6)
    caja.topleft = (4, y)
    pygame.draw.rect(surface, (35, 27, 27), caja)
    surface.blit(t, (caja.x + 6, caja.y + 3))
    return caja.bottom + 4


def draw_clientes_hud(surface):
    """Arriba solo el reloj. Atendidos / se fueron están en el historial (H);
    si la tienda está abierta o cerrada lo dice el letrero de la puerta."""
    draw_meta_hud(surface, draw_reloj_hud(surface))


def draw_checkout_menu(surface):
    """Factura educativa: el niño escribe cada subtotal y luego el total."""
    summary = table_object_manager.get_counter_sale_summary()

    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((22, 27, 29, 178))
    surface.blit(overlay, (0, 0))

    panel = pygame.Rect(78, 14, 484, 332)
    pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
    pygame.draw.rect(surface, CREAM_DARK, panel)
    pygame.draw.rect(surface, WOOD_DARK, panel, 4)
    pygame.draw.rect(surface, WOOD, (84, 20, 472, 44))
    pygame.draw.rect(surface, WOOD_DARK, (84, 20, 472, 4))
    pygame.draw.line(surface, WOOD_LIGHT, (88, 65), (552, 65), 2)

    title = font_title.render("FACTURA DE LA PULPERIA", False, CREAM)
    surface.blit(title, title.get_rect(center=(320, 43)))

    if checkout_receipt_total is not None:
        success = font_title.render("¡VENTA COBRADA!", False, (66, 115, 67))
        surface.blit(success, success.get_rect(center=(320, 121)))
        money = font_title.render(format_colones(checkout_receipt_total), False, WOOD_DARK)
        surface.blit(money, money.get_rect(center=(320, 179)))
        if checkout_exercise is not None and checkout_exercise.pago is not None:
            linea = font_medium.render(
                f"Pagó con {format_colones(checkout_exercise.pago)}   ·   "
                f"Vuelto: {format_colones(checkout_exercise.pago - checkout_receipt_total)}",
                False, (54, 96, 65))
            surface.blit(linea, linea.get_rect(center=(320, 200)))
        if vuelto is not None:
            draw_vuelto(surface)
            return
        note = font_small.render(
            f"¡Muy bien, {nombre_bonito()}! Los productos ya se vendieron."
            if nombre_jugador else "Los productos ya no están en el mostrador.",
            False, WOOD_DARK
        )
        surface.blit(note, note.get_rect(center=(320, 226)))
        return

    if summary["count"] == 0:
        note = font_medium.render("No hay productos para facturar.", False, WOOD_DARK)
        surface.blit(note, note.get_rect(center=(320, 160)))
        return

    exercise = checkout_exercise
    if exercise is None:
        return

    instruction = font_small.render(
        "Multiplica cantidad x precio y escribe el resultado."
        if factura_muestra_cantidad() else
        "Cuenta los dibujos, multiplica por el precio y escribe el resultado.",
        False, WOOD_DARK
    )
    surface.blit(instruction, instruction.get_rect(center=(320, 80)))

    header = font_small.render("PRODUCTO Y PRECIO", False, BUTTON_BLUE_DARK)
    surface.blit(header, (108, 97))
    answer_header = font_small.render("TU SUBTOTAL", False, BUTTON_BLUE_DARK)
    surface.blit(answer_header, answer_header.get_rect(topright=(536, 97)))

    for index, rect in checkout_visible_rows(exercise):
        group = exercise.filas[index]
        # Muestra solo factores, nunca el subtotal esperado.
        x = draw_invoice_products(surface, group, 108, rect.centery)
        if factura_muestra_cantidad():
            # Sin el nombre del producto: para eso están los dibujos.
            description = f'{group["quantity"]}  x  {format_colones(group["unit_price"])}  ='
        else:
            # El niño cuenta los dibujos: no se escribe la cantidad.
            description = f'x  {format_colones(group["unit_price"])}  ='
        caption = font_medium.render(description, False, WOOD_DARK)
        surface.blit(caption, caption.get_rect(midleft=(x + 6, rect.centery + 1)))
        draw_invoice_input(surface, rect, exercise, index)

    if len(exercise.filas) > CHECKOUT_MAX_ROWS:
        first_visible = next(iter(checkout_visible_rows(exercise)))[0] + 1
        pager = font_small.render(
            f'PRODUCTOS {first_visible}-{min(first_visible + 3, len(exercise.filas))}'
            f' / {len(exercise.filas)}', False, BUTTON_BLUE_DARK
        )
        surface.blit(pager, (107, 213))

    pygame.draw.line(surface, WOOD_LIGHT, (105, 224), (536, 224), 2)
    # Mismo tamaño que "TU VUELTO" y justo encima de él.
    total_label = font_medium.render("TOTAL", False, WOOD_DARK)
    surface.blit(total_label, total_label.get_rect(midright=(CHECKOUT_TOTAL_FIELD.x - 10,
                                                             CHECKOUT_TOTAL_FIELD.centery)))
    draw_invoice_input(surface, CHECKOUT_TOTAL_FIELD, exercise, exercise.indice_total)

    if exercise.pago is not None:
        # El cliente paga con billetes (solo se dice cuánto) y el niño da el vuelto.
        fila_y = CHECKOUT_VUELTO_FIELD.centery
        paga = font_medium.render("PAGA CON", False, WOOD_DARK)
        surface.blit(paga, paga.get_rect(midleft=(108, fila_y)))
        billete = pygame.Rect(0, 0, 58, 20)
        billete.midleft = (108 + paga.get_width() + 8, fila_y)
        pygame.draw.rect(surface, (64, 120, 72), billete.move(1, 2))
        pygame.draw.rect(surface, (150, 206, 140), billete)
        pygame.draw.rect(surface, (64, 120, 72), billete, 2)
        monto = font_medium.render(format_colones(exercise.pago), False, (34, 70, 40))
        surface.blit(monto, monto.get_rect(center=billete.center))
        etiqueta = font_medium.render("TU VUELTO", False, WOOD_DARK)
        surface.blit(etiqueta, etiqueta.get_rect(midright=(CHECKOUT_VUELTO_FIELD.x - 10, fila_y)))
        draw_invoice_input(surface, CHECKOUT_VUELTO_FIELD, exercise, exercise.indice_vuelto)

    # Retroalimentación discreta: nunca se revela el número correcto.
    message_color = (159, 60, 47) if exercise.error else (54, 96, 65)
    texto_estado = exercise.mensaje
    if not exercise.listo and exercise.actual in pistas_por_fila:
        # La pista se queda mientras el niño corrige esa fila.
        texto_estado = pistas_por_fila[exercise.actual]
        message_color = (54, 96, 65)
    status = font_small.render(texto_estado, False, message_color)
    surface.blit(status, status.get_rect(center=(320, 289)))

    # Mouse encima de un botón: se marca y sale su ayuda.
    pos = raton_logico()
    if pos is not None and calculadora_visible():
        pos = (pos[0] + calc_mod.DESPLAZAMIENTO, pos[1])
    marcado = None
    for text, rect, enabled in (
        ("COBRAR", CHECKOUT_PAY_BUTTON, exercise.listo),
        ("CANCELAR", CHECKOUT_CANCEL_BUTTON, True),
    ):
        if pos is not None and rect.collidepoint(pos):
            marcado = text
        elif text == "COBRAR" and exercise.en_boton_cobrar and marcado is None:
            marcado = text
        border = WOOD_DARK if enabled else (123, 119, 108)
        if marcado == text:
            border = BUTTON_HIGHLIGHT_DARK
        fill = BUTTON_HIGHLIGHT if enabled and text == "COBRAR" else BUTTON_BLUE
        if not enabled:
            fill = (137, 141, 130)
        pygame.draw.rect(surface, border, rect.move(0, 2))
        pygame.draw.rect(surface, fill, rect)
        pygame.draw.rect(surface, border, rect, 2)
        label = font_medium.render(text, False, WOOD_DARK if enabled and text == "COBRAR" else CREAM)
        surface.blit(label, label.get_rect(center=rect.center))
    boton_calc = (not calc_desbloqueada and checkout_receipt_total is None
                  and table_object_manager.get_counter_sale_summary()["count"] > 0)
    if boton_calc:
        if pos is not None and CHECKOUT_CALC_BUTTON.collidepoint(pos):
            marcado = "CALCULADORA"
        _dibujar_boton_calculadora(surface, marcado == "CALCULADORA")
    if marcado == "COBRAR":
        dibujar_tooltip(surface, CHECKOUT_PAY_BUTTON,
                        "Cobra la venta. Primero escribe bien todas las cuentas."
                        if not exercise.listo else "¡Todo bien! Cobra la venta.", "arriba")
    elif marcado == "CANCELAR":
        dibujar_tooltip(surface, CHECKOUT_CANCEL_BUTTON, "Cierra la factura sin cobrar.", "arriba")
    elif marcado == "CALCULADORA":
        precio = format_colones(precio_calculadora())
        dibujar_tooltip(surface, CHECKOUT_CALC_BUTTON,
                        f"Para usar la calculadora cuesta {precio}. Solo sirve para esta factura."
                        if saldo >= precio_calculadora() else
                        f"La calculadora cuesta {precio} y no te alcanza.", "arriba")



def calculadora_visible():
    """La calculadora acompaña a la factura mientras se está resolviendo."""
    return (
        checkout_open
        and calc_desbloqueada
        and checkout_exercise is not None
        and checkout_receipt_total is None
        and table_object_manager.get_counter_sale_summary()["count"] > 0
    )


def draw_checkout_con_calculadora(surface):
    """Dibuja la factura y, si corresponde, la calculadora a su derecha."""
    if not calculadora_visible():
        draw_checkout_menu(surface)
        return

    capa = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    draw_checkout_menu(capa)
    surface.blit(capa, (-calc_mod.DESPLAZAMIENTO, 0))
    # Completar el oscurecido en la franja derecha que quedó libre.
    franja = pygame.Surface((calc_mod.DESPLAZAMIENTO, GAME_HEIGHT), pygame.SRCALPHA)
    franja.fill((22, 27, 29, 178))
    surface.blit(franja, (GAME_WIDTH - calc_mod.DESPLAZAMIENTO, 0))
    calculadora.dibujar(surface, font_small, font_medium, font_large, calc_foco)


def pista_factura(exercise, indice, intento):
    """Pista para niños según la fila y cuántas veces se ha equivocado."""
    if indice == exercise.indice_vuelto:
        total, pago = exercise.total, exercise.pago
        if intento == 0:
            return f"Pista: cuenta desde {total} hasta llegar a {pago}."
        return f"Pista: {total} + ? = {pago}. ¿Cuánto le falta a {total}?"
    if indice == exercise.indice_total:
        return "Pista: suma todos tus subtotales, uno por uno."
    fila = exercise.filas[indice]
    p, q = fila["unit_price"], fila["quantity"]
    if factura_muestra_cantidad():
        if intento == 0 and q <= 6:
            return f"Pista: {q} x {p} es " + " + ".join([str(p)] * q) + "."
        pasos = ", ".join(str(p * k) for k in range(1, min(q, 3) + 1))
        return f"Pista: cuenta de {p} en {p}: {pasos}... ({q} veces)."
    if intento == 0:
        return f"Pista: cuenta los dibujos. Cada uno vale {p}."
    pasos = ", ".join(str(p * k) for k in range(1, 4))
    return f"Pista: di {pasos}... un número por cada dibujo."


def precio_calculadora():
    return nivel().get("precio_calculadora", 5)


def comprar_calculadora():
    """Pagar para usar la calculadora en ESTA factura (al cerrarla se
    bloquea otra vez). El gasto queda en el historial (H)."""
    global calc_desbloqueada, calc_foco, saldo
    if calc_desbloqueada or checkout_exercise is None or checkout_receipt_total is not None:
        return
    precio = precio_calculadora()
    if saldo < precio:
        checkout_exercise.mensaje = f"No te alcanza: la calculadora cuesta {format_colones(precio)}."
        checkout_exercise.error = True
        sonido.efecto("error")
        return
    saldo -= precio
    gastos_dia.append(("Calculadora", precio))
    if not tutorial.activo:
        estadisticas.usar_calculadora(pagada=True)
    calc_desbloqueada = True
    calc_foco = True
    checkout_exercise.mensaje = f"Calculadora: -{format_colones(precio)}. Solo para esta factura."
    checkout_exercise.error = False
    sonido.efecto("cobrar")


def _dibujar_boton_calculadora(surface, marcado=False):
    """Botón con una calculadita y su precio (gris si no alcanza el saldo)."""
    r = CHECKOUT_CALC_BUTTON
    precio = precio_calculadora()
    alcanza = saldo >= precio
    fill = (232, 216, 176) if alcanza else (176, 170, 156)
    borde = WOOD_DARK if alcanza else (123, 119, 108)
    if marcado:
        borde = BUTTON_HIGHLIGHT_DARK
    pygame.draw.rect(surface, borde, r.move(0, 2))
    pygame.draw.rect(surface, fill, r)
    pygame.draw.rect(surface, borde, r, 2)
    # Calculadita
    cx, cy = r.x + 14, r.centery
    pygame.draw.rect(surface, (60, 70, 80), (cx - 6, cy - 8, 12, 16))
    pygame.draw.rect(surface, (170, 220, 170), (cx - 4, cy - 6, 8, 4))
    for fila in range(2):
        for col in range(3):
            pygame.draw.rect(surface, (230, 230, 230), (cx - 4 + col * 3, cy + fila * 3, 2, 2))
    t = font_medium.render(f"{format_colones(precio)}  (C)", False, WOOD_DARK if alcanza else (90, 86, 80))
    surface.blit(t, t.get_rect(midleft=(r.x + 26, r.centery + 1)))


def registrar_error_factura(indice=None):
    """Cuenta una respuesta equivocada: da pistas y, después de varios
    errores, recuerda que se puede comprar la calculadora (nunca es gratis)."""
    global calc_errores
    calc_errores += 1
    sonido.efecto("error")
    if indice is not None:
        errores_por_fila[indice] = errores_por_fila.get(indice, 0) + 1
        intento = errores_por_fila[indice] - nivel()["pista_desde_error"]
        if intento >= 0:
            pistas_por_fila[indice] = pista_factura(checkout_exercise, indice, intento)
    if not calc_desbloqueada and calc_errores == nivel()["errores_para_calculadora"]:
        quien = f", {nombre_bonito()}" if nombre_jugador else ""
        checkout_exercise.mensaje = (f"¡Tranquilo{quien}! Si quieres, compra la calculadora "
                                     f"({format_colones(precio_calculadora())}, tecla C).")
        checkout_exercise.error = False


def cerrar_factura():
    """Cierra la caja sin modificar los artículos del mostrador."""
    global checkout_open, checkout_exercise, checkout_receipt_total, vuelto
    if checkout_receipt_total is not None:
        # La venta se completó: el cliente se va contento.
        clientes.venta_cobrada()
    vuelto = None
    checkout_open = False
    checkout_exercise = None
    checkout_receipt_total = None


def cobrar_factura():
    """Elimina productos solo si todos los cálculos fueron validados."""
    global checkout_receipt_total
    if checkout_exercise is None or not checkout_exercise.listo:
        if checkout_exercise is not None:
            checkout_exercise.mensaje = "Completa correctamente subtotales y total primero."
            checkout_exercise.error = True
        return False
    global vuelto
    global venta_reciente
    venta = table_object_manager.charge_counter()
    checkout_receipt_total = venta["total"]
    global saldo
    saldo += venta["total"]
    if venta["total"] > 0:
        ventas_dia.append(venta["total"])
        venta_reciente = (venta["total"], pygame.time.get_ticks())
    # El vuelto ahora se calcula dentro de la factura (opción VUELTO).
    vuelto = None
    # Sin pantalla final de "venta cobrada": la factura se cierra de una vez
    # y el cliente se va contento.
    cerrar_factura()
    return True


def viajar_a_zona(destino, origen):
    """Cambia de habitación sin recrear los productos ni los muebles."""
    global current_scene, ultima_zona, checkout_open, checkout_receipt_total, checkout_exercise
    if destino == "entrada":
        calle.poblar(player, reloj.es_noche)

    puntos = {
        # En la calle aparece sobre el sendero, mirando hacia afuera.
        ("interior", "entrada"): (320, 216, "down"),
        # En la sala aparece antes de la alfombrilla de salida.
        ("entrada", "interior"): (PUERTA_SALA_X, 301, "up"),
        # En la bodega aparece a la derecha de su puerta de regreso.
        ("interior", "inventario"): (91, 311, "right"),
        # En la sala aparece a la izquierda de la puerta de bodega.
        ("inventario", "interior"): (569, 140, "left"),
    }
    destino_posicion = puntos.get((origen, destino))
    if destino_posicion is None:
        return

    if carrito.empujando:
        if destino in ("interior", "inventario"):
            llevar_carrito = True
        else:
            # A la calle no: el carrito se queda estacionado en la tienda.
            carrito.soltar(table_object_manager)
            table_object_manager.avisar("El carrito se queda adentro.",
                                        "¡Lo esperas en la tienda!")
            llevar_carrito = False
    else:
        llevar_carrito = False

    player.x, player.y, player.direction = destino_posicion
    if llevar_carrito:
        carrito.cambiar_escena(destino, player)
    player.frame = 0
    player.animation_time = 0.0
    current_scene = destino
    ultima_zona = destino
    checkout_open = False
    checkout_receipt_total = None
    checkout_exercise = None


def draw():

    if current_scene == "menu":

        draw_background(game_surface)
        draw_main_menu(game_surface, selected_option)
        if confirmar_nueva is not None:
            draw_confirmar_nueva(game_surface)
        if elegir_modo is not None:
            draw_elegir_modo(game_surface)
        if elegir_continuar is not None:
            draw_elegir_continuar(game_surface)
        if pregunta_tutorial is not None:
            draw_pregunta_tutorial(game_surface)

    elif current_scene == "opciones":

        draw_options_menu(game_surface)
        if confirmar_nueva is not None:
            draw_confirmar_nueva(game_surface)

    elif current_scene == "elegir_skin":

        draw_skin_menu(game_surface)

    elif current_scene == "escribir_nombre":

        draw_name_menu(game_surface)

    elif current_scene == "reporte":

        draw_reporte(game_surface)

    elif current_scene == "ayuda":

        draw_help_menu(game_surface)

    elif current_scene == "modo_juego":

        draw_modo_juego(game_surface)

    elif current_scene == "visuales":

        draw_visuales(game_surface)

    elif current_scene == "extras":

        draw_extras(game_surface)

    elif current_scene == "sonido":

        draw_sonido(game_surface)

    elif current_scene == "interior":

        game_surface.blit(
            interior_background,
            (0, 0)
        )

        # Puertas sobre la pared y alfombrilla de salida (con su color).
        dibujar_alfombras(game_surface)
        # Botón para llamar al ayudante (pared derecha).
        dibujar_boton(game_surface, encendido=ayudante.presente)

        # Letrero ABIERTO/CERRADO junto a la salida a la calle.
        dibujar_letrero_pie(game_surface, LETRERO_TIENDA["interior"])

        # Clientes (detrás del mostrador o caminando por el pasillo).
        clientes.dibujar(game_surface)

        # Muebles y personaje se ordenan por profundidad (eje Y).
        furniture_manager.draw_world(
            game_surface, player, table_object_manager,
            extras=([carrito] if carrito.escena == "interior" else [])
                   + ([ayudante] if ayudante.presente else [])
                   + ([mascota] if MASCOTAS["gata"] and mascota.zona == "interior" else [])
                   + ([perro] if MASCOTAS["perro"] and perro.zona == "interior" else [])
                   + ([casa_gato, casa_gato.frente] if MASCOTAS["gata"] else []))
        # Si los dos hablan a la vez y están cerca, el globo de Bruno sube
        # para no tapar el "¡Fsss!" de Canela.
        perro.globo_arriba = (16 if MASCOTAS["gata"] and mascota.globo and perro.globo
                              and abs(mascota.x - perro.x) < 70 and abs(mascota.y - perro.y) < 30 else 0)
        if MASCOTAS["perro"]:
            perro.dibujar_globo(game_surface, "interior")
        if MASCOTAS["gata"]:
            mascota.dibujar_globo(game_surface, "interior")

        if player.y < rect_letrero("interior").bottom:
            dibujar_letrero_pie(game_surface, LETRERO_TIENDA["interior"])

        # Luz según la hora del día (los letreros se dibujan después).
        reloj.dibujar_luz(game_surface, "interior")
        # Sol que entra por las ventanas del frente (cambia con la hora).
        reloj.dibujar_ventanas(game_surface)
        # Luciérnagas (después de la luz, para que brillen de noche).
        if luciernagas_activas and reloj.hora >= HORA_LUCIERNAGAS:
            luciernagas.dibujar(game_surface, oscuridad())

        if checkout_open:
            draw_checkout_con_calculadora(game_surface)
        else:
            clientes.dibujar_burbujas(game_surface, font_hud, nombre_bonito())
            ayudante.dibujar_globo(game_surface, font_hud)
            table_object_manager.draw_aviso(game_surface, player, font_hud)
            draw_clientes_hud(game_surface)
            draw_hud_ventas(game_surface)
            draw_furniture_hud(game_surface)
            draw_menu_tomar(game_surface)

    elif current_scene == "entrada":
        game_surface.blit(entrada_background, (0, 0))
        calle.dibujar_cielo(game_surface)                   # pájaros
        dibujar_letrero_tienda(game_surface, (320, 128))   # colgado en la puerta
        dibujar_letrero_pie(game_surface, LETRERO_TIENDA["entrada"])

        def jugador():
            player.draw(game_surface)
            if player.y < rect_letrero("entrada").bottom:
                dibujar_letrero_pie(game_surface, LETRERO_TIENDA["entrada"])
            table_object_manager.draw_carried(game_surface, player)

        # Gente, autos y animales ordenados por profundidad con el jugador.
        extras = [(c.y, lambda c=c: camion.dibujar_caja(game_surface, c)) for c in camion.cajas]
        if camion.estado is not None:
            extras.append((camion.y, lambda: camion.dibujar_camion(game_surface)))
        if ayudante.afuera > 0 and ayudante.caja_afuera is not None:
            extras.append((ayudante.caja_afuera.y + 4, lambda: ayudante.dibujar_afuera(game_surface)))
        if MASCOTAS["gata"] and mascota.zona == "entrada":
            extras.append((mascota.y, lambda: mascota.dibujar(game_surface, "entrada")))
        if MASCOTAS["perro"] and perro.zona == "entrada":
            extras.append((perro.y, lambda: perro.dibujar(game_surface, "entrada")))
        calle.dibujar(game_surface, player, jugador, extras)
        if MASCOTAS["gata"]:
            mascota.dibujar_globo(game_surface, "entrada")
        if MASCOTAS["perro"]:
            perro.dibujar_globo(game_surface, "entrada")
        reloj.dibujar_luz(game_surface, "entrada")
        calle.dibujar_farol(game_surface, oscuridad())          # poste de luz
        if luciernagas_activas and reloj.hora >= HORA_LUCIERNAGAS:
            # Desde las 3 p. m. (más brillantes cuando oscurece).
            luciernagas_calle.dibujar(game_surface, max(0.5, oscuridad()))
        calle.dibujar_faros(game_surface, reloj.es_noche)
        calle.dibujar_burbujas(game_surface, font_hud)
        table_object_manager.draw_aviso(game_surface, player, font_hud)
        if dialogo is None:
            dibujar_hud_zona(
                game_surface, "entrada", acceso_actual("entrada", player),
                texto_letrero() if cerca_letrero() else
            "SUBE POR EL CAMINO PARA ENTRAR A LA TIENDA" if clientes.esperando_jugador else
                f"E: ACARICIAR A {mascota_nombre()}" if MASCOTAS["gata"] and mascota.cerca(player, "entrada") else
                f"E: ACARICIAR A {perro_nombre()}" if MASCOTAS["perro"] and perro.cerca(player, "entrada") else
                (f"E: CAJA DE {PRODUCTOS[camion.caja_cerca(player).kind][1].upper()}"
                 f" ({camion.caja_cerca(player).unidades})" if camion.caja_cerca(player) else None)
            )

    elif current_scene == "inventario":
        game_surface.blit(inventario_background, (0, 0))
        bodega.dibujar(game_surface)
        # Personaje y carrito por orden de profundidad.
        if carrito.escena == "inventario" and carrito.y <= player.y:
            carrito.dibujar(game_surface, "inventario")
        player.draw(game_surface)
        if carrito.escena == "inventario" and carrito.y > player.y:
            carrito.dibujar(game_surface, "inventario")
        table_object_manager.draw_carried(game_surface, player)
        reloj.dibujar_luz(game_surface, "inventario")
        table_object_manager.draw_aviso(game_surface, player, font_hud)
        puerta = acceso_actual("inventario", player)
        mensaje = None if puerta else bodega.mensaje_hud(player, table_object_manager)
        if not puerta and carrito.cerca(player, "inventario"):
            mensaje = "ESPACIO: EMPUJAR CARRITO"
        if not puerta and cerca_armario():
            mensaje = "E: ARMARIO (ROPA)"
        if dialogo is None:
            dibujar_hud_zona(game_surface, "inventario", puerta, mensaje)
        draw_menu_tomar(game_surface)

    if current_scene in ("entrada", "inventario"):
        draw_hud_ventas(game_surface)
        # Debajo del letrero de la zona (ENTRADA / INVENTARIO): solo el reloj.
        draw_meta_hud(game_surface, draw_reloj_hud(game_surface, y=48))
    if current_scene in ("interior", "entrada", "inventario"):
        reloj.dibujar_letrero(game_surface, font_title, font_small)
    if historial_abierto and current_scene in ("interior", "entrada", "inventario"):
        draw_historial(game_surface)
    if pausa is not None and current_scene in ("interior", "entrada", "inventario"):
        draw_pausa(game_surface)
    if armario is not None and current_scene == "inventario":
        draw_armario(game_surface)
    if casa_menu is not None and current_scene == "interior":
        draw_casa_menu(game_surface)
    if pago_ayudante is not None and current_scene == "interior":
        draw_pago_ayudante(game_surface)
    if pedido_abierto is not None and current_scene == "interior":
        draw_pedido(game_surface)
    if menu_caja is not None and current_scene == "entrada":
        draw_menu_caja(game_surface)
    if cierre is not None and current_scene in ("interior", "entrada", "inventario"):
        draw_cierre(game_surface)
    if (dialogo is not None and cartel_edit is None
            and current_scene in ("interior", "entrada", "inventario")):
        draw_dialogo(game_surface)
    if cartel_edit is not None and current_scene in ("interior", "entrada", "inventario"):
        draw_cartel_edit(game_surface)
    # Mouse sobre el reloj, la meta, el saldo o el día: burbuja de ayuda.
    if (current_scene in ("interior", "entrada", "inventario") and pausa is None
            and dialogo is None and cartel_edit is None
            and not checkout_open and cierre is None and menu_tomar is None
            and pedido_abierto is None and not recetario.abierto and not historial_abierto
            and armario is None and casa_menu is None and pago_ayudante is None
            and menu_caja is None):
        draw_tooltips_hud(game_surface)

    # Único escalado: 640x360 -> 1280x720 (factor entero 2x).
    pygame.transform.scale(
        game_surface,
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        screen
    )

    # La vista de cerca del mueble va encima, en alta resolución.
    if menu_tomar is not None and current_scene in ("interior", "inventario"):
        menu_tomar.dibujar(screen)

    # El libro de recetas también va en alta resolución.
    if recetario.abierto and current_scene in ("interior", "inventario"):
        recetario.dibujar(screen)

    # Letrero del tutorial, encima de todo.
    draw_tutorial_screen()



# =========================================================
# BUCLE PRINCIPAL
# =========================================================
# ---------------------------------------------------------
# GUARDAR PARTIDA: al cerrar el juego, al volver al menú, al empezar un
# día y cada 20 segundos mientras se juega. Al abrir, CONTINUAR sigue
# donde se quedó.
# MODO HISTORIA y MODO LIBRE tienen cada uno su partida, independientes:
#   partida_historia.json y partida_libre.json (junto al juego).
# Los ajustes de OPCIONES son de las dos: ajustes.json.
# (Si hay un partida_guardada.json de una versión anterior, se pasa solo
# al archivo de su modo la primera vez que se abre el juego.)
# ---------------------------------------------------------
import json
import os

_CARPETA_JUEGO = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_PARTIDA = os.path.join(_CARPETA_JUEGO, "partida_guardada.json")   # versión anterior
ARCHIVO_AJUSTES = os.path.join(_CARPETA_JUEGO, "ajustes.json")
ARCHIVOS_PARTIDA = {"historia": os.path.join(_CARPETA_JUEGO, "partida_historia.json"),
                    "libre": os.path.join(_CARPETA_JUEGO, "partida_libre.json")}
MODOS_PARTIDA = ("historia", "libre")
NOMBRE_MODO = {"historia": "HISTORIA", "libre": "LIBRE"}
GUARDADO_ACTIVO = os.environ.get("PULPERIA_SIN_GUARDAR") != "1"
# Sin archivos (pruebas): las partidas se guardan en memoria.
_en_memoria = {}
_cache_leido = {}
ultimo_modo = None           # modo de la última partida jugada
AUTOGUARDADO_SEGUNDOS = 20.0
_autoguardado_t = 0.0


def modo_partida():
    """De qué modo es la partida abierta: "historia" o "libre"."""
    return "historia" if historia_activa else "libre"


def partida_en_juego():
    return ultima_zona is not None and bool(nombre_jugador) and not tutorial.activo


def _escribir_json(ruta, datos):
    if not GUARDADO_ACTIVO:
        _en_memoria[ruta] = json.loads(json.dumps(datos))
        return
    temporal = ruta + ".tmp"
    with open(temporal, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False)
    os.replace(temporal, ruta)


def _leer_json(ruta):
    if not GUARDADO_ACTIVO:
        d = _en_memoria.get(ruta)
        return json.loads(json.dumps(d)) if d is not None else None
    # Se lee de nuevo solo si el archivo cambió (el menú pregunta seguido).
    try:
        st = os.stat(ruta)
        marca = (st.st_mtime_ns, st.st_size)
        if _cache_leido.get(ruta, (None,))[0] != marca:
            with open(ruta, encoding="utf-8") as f:
                _cache_leido[ruta] = (marca, json.load(f))
        return json.loads(json.dumps(_cache_leido[ruta][1]))
    except (OSError, ValueError):
        return None


def leer_partida(modo):
    """La partida guardada de ese modo (o None)."""
    d = _leer_json(ARCHIVOS_PARTIDA[modo])
    return d if isinstance(d, dict) and "jugador" in d else None


def _ajustes():
    # La dificultad de OPCIONES (si la historia la subió, la de antes).
    base = historia_nivel_base if (historia_activa and historia_nivel_base in NIVELES) else nivel_actual
    return {
        "nivel": base, "ultimo_modo": ultimo_modo, "modo": dict(MODO), "letra": fuentes.tipo_actual,
        "colores": dict(interior_mod.COLOR_ELEGIDO), "luciernagas": luciernagas_activas,
        "avisos": avisos_activos, "tooltips": tooltips_activos,
        "pantalla_completa": pantalla_completa,
        "mascotas": dict(MASCOTAS_ELEGIDAS), "extras": dict(EXTRAS),
        "sonido": {"estilo": sonido.estilo, "estilo_tienda": sonido.estilo_tienda,
                   "vol_musica": sonido.volumen_musica, "vol_efectos": sonido.volumen_efectos,
                   "vol_ambiente": sonido.volumen_ambiente, "efectos": sonido.efectos_activos,
                   "ambiente": sonido.ambiente_activo},
    }


def estado_partida():
    """Todo lo necesario para seguir jugando otro día, en un diccionario."""
    tom = table_object_manager
    if carrito.empujando:
        en_carrito, en_manos = [i["id"] for i in tom.mano if "id" in i], []
    elif getattr(ayudante, "con_carrito", False) or carrito.items is ayudante.carga:
        # Tavo usa el carrito: lo que lleva es su carga (de la bodega o de las
        # cajas), no productos del jugador. Lo de la bodega vuelve a su lugar.
        en_carrito, en_manos = [], [i["id"] for i in tom.mano if "id" in i]
    else:
        en_carrito = [i["id"] for i in carrito.items if "id" in i]
        en_manos = [i["id"] for i in tom.mano if "id" in i]
    productos = [dict(i) for i in tom.items if i["kind"] in PRODUCTOS]
    for item in productos:
        if item["id"] in en_carrito:
            item["table_id"] = "carrito"
    bodega_items = [dict(i) for i in bodega.items]
    # Lo que Tavo llevaba de la bodega vuelve a su lugar.
    bodega_items += [dict(i) for i in ayudante.carga if "x" in i]
    zona = ultima_zona if current_scene not in ("interior", "entrada", "inventario") else current_scene
    return {
        "version": 2,
        "modo_partida": modo_partida(),
        "nivel": nivel_actual,
        "jugador": {"nombre": nombre_jugador, "skin": player.skin, "zona": zona or "interior",
                    "x": player.x, "y": player.y, "direccion": player.direction},
        "dia": dia, "saldo": saldo, "ventas": list(ventas_dia), "gastos": [list(g) for g in gastos_dia],
        "estadisticas": estadisticas.a_dict(),
        "historia": {"activa": historia_activa, "nivel_base": historia_nivel_base,
                     "camion_hoy": historia_hoy["camion"], "recetas_hoy": clientes.recetas_hoy,
                     "felicitado": historia_hoy["felicitado"]},
        "reloj": reloj.progreso,
        "clientes": {"atendidos": clientes.atendidos, "perdidos": clientes.perdidos,
                     "esperando_jugador": clientes.esperando_jugador,
                     "generados": clientes.generados, "abierta": clientes.abierta,
                     "frecuentes_hoy": [d["nombre"] for d in clientes.frecuentes_hoy]},
        "muebles": {m["id"]: [m["x"], m["y"]] for m in furniture_manager.items},
        "productos": productos, "en_manos": en_manos, "en_carrito": en_carrito,
        "carrito": {"escena": carrito.escena, "x": carrito.x, "y": carrito.y},
        "bodega": bodega_items,
        "camion": {"pedido": camion.pedido if camion.estado != "descargando" else camion.por_descargar,
                   "llegada": camion.llegada if camion.estado != "saliendo" else None,
                   "cajas": [[c.kind, c.unidades, c.x, c.y] for c in camion.cajas]},
        "tavo_trabajo_hoy": ayudante.trabajo_hoy,
        "ropa": {"comprados": sorted(cosmeticos.comprados), "puestos": dict(cosmeticos.puestos)},
        "cierre": cierre is not None,
        "casa_gato": casa_gato.nivel,
        "nombre_tienda": nombre_tienda,
    }


def guardar_partida():
    """Guarda los ajustes y la partida abierta, en el archivo de SU modo
    (la del otro modo no se toca)."""
    global ultimo_modo
    try:
        if partida_en_juego():
            ultimo_modo = modo_partida()
            _escribir_json(ARCHIVOS_PARTIDA[ultimo_modo], estado_partida())
        _escribir_json(ARCHIVO_AJUSTES, _ajustes())
    except (OSError, ValueError, TypeError):
        pass   # si no se puede guardar, el juego sigue igual


def partidas_disponibles():
    """Los modos que tienen partida para CONTINUAR (la abierta o guardada)."""
    return [m for m in MODOS_PARTIDA
            if (partida_en_juego() and modo_partida() == m) or leer_partida(m) is not None]


def resumen_partida(modo):
    """(nombre, día) de la partida de ese modo, o None."""
    if partida_en_juego() and modo_partida() == modo:
        return nombre_bonito(), dia
    d = leer_partida(modo)
    if d is None:
        return None
    return " ".join(p.capitalize() for p in d["jugador"]["nombre"].split()), d.get("dia", 1)


def continuar_modo(modo):
    """CONTINUAR la partida de ese modo. Si estaba abierta la del otro modo,
    esa se guarda primero (las dos quedan independientes)."""
    global current_scene
    if partida_en_juego() and modo_partida() == modo:
        current_scene = ultima_zona
        return True
    d = leer_partida(modo)
    if d is None:
        return False
    if partida_en_juego():
        guardar_partida()
    nueva_partida_completa()
    d.pop("ajustes", None)            # los ajustes son de las dos partidas
    if not aplicar_partida(d):
        return False
    rehacer_fondo()
    current_scene = ultima_zona
    return True


def _migrar_partida_vieja():
    """Versión anterior: una sola partida en partida_guardada.json. Se pasa
    al archivo de su modo (y sus ajustes a ajustes.json)."""
    if not GUARDADO_ACTIVO or not os.path.exists(ARCHIVO_PARTIDA):
        return
    try:
        with open(ARCHIVO_PARTIDA, encoding="utf-8") as f:
            viejo = json.load(f)
        ajustes = dict(viejo.pop("ajustes", {}) or {})
        if "jugador" in viejo:
            h = viejo.get("historia", {})
            modo = "historia" if h.get("activa") else "libre"
            viejo["nivel"] = ajustes.get("nivel")
            viejo["modo_partida"] = modo
            if modo == "historia" and h.get("nivel_base") in NIVELES:
                ajustes["nivel"] = h["nivel_base"]
            if not os.path.exists(ARCHIVOS_PARTIDA[modo]):
                _escribir_json(ARCHIVOS_PARTIDA[modo], viejo)
            ajustes["ultimo_modo"] = modo
        if not os.path.exists(ARCHIVO_AJUSTES):
            _escribir_json(ARCHIVO_AJUSTES, ajustes)
        os.replace(ARCHIVO_PARTIDA, ARCHIVO_PARTIDA + ".anterior")
    except (OSError, ValueError, TypeError, AttributeError):
        pass


def _aplicar_ajustes(a):
    global nivel_actual, luciernagas_activas, paciencia_activa, avisos_activos, tooltips_activos
    if a.get("nivel") in NIVELES:
        nivel_actual = a["nivel"]
    for k, v in a.get("modo", {}).items():
        if k in MODO:
            MODO[k] = bool(v)
    paciencia_activa = MODO["paciencia"]
    clientes.paciencia_activa = paciencia_activa
    fuentes.cambiar_tipo(a.get("letra", fuentes.tipo_actual))
    for k, v in a.get("colores", {}).items():
        if k in interior_mod.COLOR_ELEGIDO:
            interior_mod.COLOR_ELEGIDO[k] = v
    luciernagas_activas = a.get("luciernagas", luciernagas_activas)
    avisos_activos = a.get("avisos", avisos_activos)
    tooltips_activos = a.get("tooltips", tooltips_activos)
    if a.get("pantalla_completa", pantalla_completa) != pantalla_completa:
        cambiar_pantalla_completa()
    zonas_mod.AVISOS_ACTIVOS = avisos_activos
    elegidas = {k: bool(v) for k, v in a.get("mascotas", {}).items() if k in MASCOTAS}
    if elegidas and not any(elegidas.values()):
        # Partida vieja con "NINGUNA": ahora es MASCOTAS = NO.
        EXTRAS["mascotas"] = False
        elegidas = {"gata": True, "perro": True}
    MASCOTAS_ELEGIDAS.update(elegidas)
    for k, v in a.get("extras", {}).items():
        if k in EXTRAS:
            EXTRAS[k] = bool(v)
    aplicar_extras()
    so = a.get("sonido", {})
    if so.get("estilo") in sonido.ESTILOS:
        sonido.estilo = so["estilo"]
    if so.get("estilo_tienda") in sonido.ESTILOS_TIENDA:
        sonido.estilo_tienda = so["estilo_tienda"]
    sonido.volumen_musica = so.get("vol_musica", sonido.volumen_musica)
    sonido.volumen_efectos = so.get("vol_efectos", sonido.volumen_efectos)
    sonido.volumen_ambiente = so.get("vol_ambiente", sonido.volumen_ambiente)
    sonido.efectos_activos = so.get("efectos", sonido.efectos_activos)
    sonido.ambiente_activo = so.get("ambiente", sonido.ambiente_activo)


def aplicar_partida(d):
    """Pone el juego tal como estaba al guardar."""
    global dia, saldo, ventas_dia, gastos_dia, nombre_jugador, ultima_zona, cierre
    global checkout_open, checkout_exercise, checkout_receipt_total, venta_reciente
    _aplicar_ajustes(d.get("ajustes", {}))
    if "jugador" not in d:
        return False
    from clientes import FRECUENTES
    j = d["jugador"]
    nombre_jugador = j["nombre"]
    table_object_manager.nombre = nombre_bonito()
    player.set_skin(j.get("skin", "hombre"))
    dia = d["dia"]
    saldo = d["saldo"]
    global historia_activa, historia_nivel_base, dialogo
    estadisticas.desde_dict(d.get("estadisticas"))
    h = d.get("historia", {})
    historia_activa = bool(h.get("activa", False))
    historia_nivel_base = h.get("nivel_base") if h.get("nivel_base") in NIVELES else None
    global nivel_actual
    if historia_activa and d.get("nivel") in NIVELES:
        # La historia sube la dificultad con los días: es de esa partida.
        if historia_nivel_base is None:
            historia_nivel_base = nivel_actual
        nivel_actual = d["nivel"]
    historia_hoy["camion"] = bool(h.get("camion_hoy", False))
    historia_hoy["felicitado"] = bool(h.get("felicitado", False))
    dialogo = None
    ventas_dia = list(d.get("ventas", []))
    gastos_dia[:] = [tuple(g) for g in d.get("gastos", [])]
    venta_reciente = None
    checkout_open, checkout_exercise, checkout_receipt_total = False, None, None
    reloj.reiniciar(dia=dia)
    reloj.progreso = d.get("reloj", 0.0)
    global hora_de_acomodar
    hora_de_acomodar = reloj.cerro      # si se guardó después de las 6 p. m.
    reloj.letrero_t = 0.0
    # Clientes del día
    clientes.dia = dia
    clientes.reiniciar()
    c = d.get("clientes", {})
    clientes.atendidos = c.get("atendidos", 0)
    clientes.perdidos = c.get("perdidos", 0)
    clientes.recetas_hoy = d.get("historia", {}).get("recetas_hoy", 0)
    clientes.generados = c.get("generados", 0)
    clientes.abierta = c.get("abierta", True)
    clientes.esperando_jugador = c.get("esperando_jugador", False)
    nombres = c.get("frecuentes_hoy")
    if nombres is not None:
        clientes.frecuentes_hoy = [f for n in nombres for f in FRECUENTES if f["nombre"] == n]
    clientes.tutorial = False
    tutorial.terminar()
    # Muebles y productos
    for m in furniture_manager.items:
        if m["id"] in d.get("muebles", {}):
            m["x"], m["y"] = d["muebles"][m["id"]]
    tom = table_object_manager
    tom.items = [i for i in tom.items if i["kind"] not in PRODUCTOS]
    for item in d.get("productos", []):
        if "antes_bodega" in item:
            item["antes_bodega"] = tuple(item["antes_bodega"])
        if "color" in item:
            item["color"] = tuple(item["color"])
        tom.items.append(item)
    por_id = {i["id"]: i for i in tom.items}
    tom.mano = [por_id[i] for i in d.get("en_manos", []) if i in por_id]
    tom.en_carrito = False
    tom.MAX_MANOS = type(tom).MAX_MANOS
    if carrito.empujando:
        carrito.empujando = False
        player.empujando_carrito = False
    carrito.items = [por_id[i] for i in d.get("en_carrito", []) if i in por_id]
    ca = d.get("carrito", {})
    carrito.escena = ca.get("escena", carrito.escena)
    carrito.x, carrito.y = ca.get("x", carrito.x), ca.get("y", carrito.y)
    # Bodega, camión, Tavo
    bodega.items = [dict(i) for i in d.get("bodega", bodega.items)]
    camion.__init__()
    cm = d.get("camion", {})
    if cm.get("pedido") and cm.get("llegada"):
        camion.pedido = [tuple(p) for p in cm["pedido"]]
        camion.llegada = tuple(cm["llegada"])
    from camion import Caja
    camion.cajas = [Caja(k, u, x, y) for k, u, x, y in cm.get("cajas", [])]
    ayudante.nuevo_dia()
    ayudante.trabajo_hoy = d.get("tavo_trabajo_hoy", False)
    # Ropa
    cosmeticos.reiniciar()
    ropa = d.get("ropa", {})
    cosmeticos.comprados.update(ropa.get("comprados", []))
    cosmeticos.puestos.update(ropa.get("puestos", {}))
    mascota.reiniciar()
    perro.reiniciar()
    casa_gato.nivel = d.get("casa_gato", 0)
    global nombre_tienda, cartel_edit
    nombre_tienda, cartel_edit = d.get("nombre_tienda", ""), None
    redibujar_entrada()
    cosmeticos.vestir(player, mascota, perro)
    # Dónde estaba el personaje
    player.x, player.y = j.get("x", player.x), j.get("y", player.y)
    player.direction = j.get("direccion", "down")
    ultima_zona = j.get("zona", "interior")
    cierre = None
    if d.get("cierre"):
        abrir_cierre()
    return True


def cargar_partida():
    """Al abrir el juego: los ajustes y la última partida jugada (si hay).
    La del otro modo queda guardada para CONTINUAR."""
    global ultimo_modo
    if not GUARDADO_ACTIVO:
        return False
    _migrar_partida_vieja()
    try:
        ajustes = _leer_json(ARCHIVO_AJUSTES) or {}
        _aplicar_ajustes(ajustes)
        ultimo_modo = ajustes.get("ultimo_modo")
        orden = ([ultimo_modo] if ultimo_modo in MODOS_PARTIDA else []) + list(MODOS_PARTIDA)
        for modo in orden:
            datos = leer_partida(modo)
            if datos is not None:
                datos.pop("ajustes", None)
                ok = aplicar_partida(datos)
                ultimo_modo = modo
                rehacer_fondo()
                return ok
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return False


def autoguardar(dt):
    global _autoguardado_t
    if current_scene in ("interior", "entrada", "inventario"):
        _autoguardado_t += dt
        if _autoguardado_t >= AUTOGUARDADO_SEGUNDOS:
            _autoguardado_t = 0.0
            guardar_partida()


aplicar_extras()            # valores por defecto (los cambia la partida guardada)
cargar_partida()


def main():

    global selected_option, current_scene, ultima_zona, reporte_aviso
    global checkout_open, checkout_exercise, checkout_receipt_total
    global calc_foco, calc_errores, calc_desbloqueada
    global nivel_actual, opciones_seleccion, skin_seleccion, paciencia_activa, modo_seleccion
    global extras_seleccion, historia_activa, historia_nivel_base, tutorial_desde_opciones
    global visual_seleccion, sonido_seleccion
    global nombre_jugador, nombre_aviso, vuelto, menu_tomar, historial_abierto
    global tutorial_enter, forzar_tutorial, pago_ayudante, pedido_abierto, menu_caja

    running = True
    if not pygame.mixer.get_init() or not pygame.mixer.music.get_busy():
        sonido.tocar_musica()

    while running:

        # Delta time para que la velocidad no dependa de los FPS.
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        # Mientras se juega suena la música tranquila de la tienda; en los
        # menús, la del menú. (En SONIDO, la de la tienda suena de prueba.)
        en_tienda = current_scene in ("interior", "entrada", "inventario") or (
            current_scene == "sonido" and FILAS_SONIDO[sonido_seleccion][0] == "estilo_tienda")
        sonido.poner_zona("tienda" if en_tienda else "menu")

        for event in eventos():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == sonido.FIN_CANCION:
                sonido.siguiente_cancion()   # las canciones se van alternando

            elif (cartel_edit is not None and event.type in (pygame.KEYDOWN, pygame.TEXTINPUT)
                  and current_scene in ("interior", "entrada", "inventario")):
                manejar_cartel(event)            # escribe el nombre del cartel

            elif (event.type == pygame.KEYDOWN and dialogo is not None
                  and current_scene in ("interior", "entrada", "inventario")):
                manejar_tecla_dialogo(event)     # Doña Rosa habla (MODO HISTORIA)

            elif (event.type == pygame.KEYDOWN and cierre is not None
                  and current_scene in ("interior", "entrada", "inventario")):
                manejar_tecla_cierre(event)

            elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                  and cierre is not None and cierre["listo"]
                  and current_scene in ("interior", "entrada", "inventario")):
                # Clic en el botón "DÍA N >" del cierre de caja.
                if (dialogo is None
                        and CIERRE_BOTON.collidepoint(event.pos[0] // SCALE, event.pos[1] // SCALE)):
                    terminar_dia()

            elif (tutorial.activo and event.type == pygame.KEYDOWN and event.key == pygame.K_TAB
                  and current_scene in ("interior", "entrada", "inventario")):
                terminar_tutorial()   # TAB: saltar el tutorial

            elif (tutorial.activo and tutorial.pide_enter and event.type == pygame.KEYDOWN
                  and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                  and current_scene == "interior" and not checkout_open):
                tutorial_enter = True

            elif (pago_ayudante is not None and event.type == pygame.KEYDOWN
                  and current_scene == "interior"):
                manejar_tecla_pago(event)

            elif (pausa is not None and event.type == pygame.KEYDOWN
                  and current_scene in ("interior", "entrada", "inventario")):
                manejar_tecla_pausa(event)

            elif pedido_abierto is not None and event.type == pygame.KEYDOWN:
                manejar_tecla_pedido(event)

            elif armario is not None and event.type == pygame.KEYDOWN:
                manejar_tecla_armario(event)

            elif casa_menu is not None and event.type == pygame.KEYDOWN:
                manejar_tecla_casa(event)

            elif menu_caja is not None and event.type == pygame.KEYDOWN:
                manejar_tecla_caja(event)

            elif (historial_abierto and event.type == pygame.KEYDOWN
                  and current_scene in ("interior", "entrada", "inventario")):
                if event.key in (pygame.K_h, pygame.K_ESCAPE):
                    historial_abierto = False

            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_h
                  and current_scene in ("interior", "entrada", "inventario")
                  and not checkout_open and cierre is None and menu_tomar is None
                  and not recetario.abierto and furniture_manager.carrying is None):
                historial_abierto = True

            elif (recetario.abierto and current_scene in ("interior", "inventario")
                  and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)):
                if event.type == pygame.KEYDOWN:
                    recetario.manejar_tecla(event.key)
                elif event.button == 1:
                    recetario.manejar_clic(event.pos)

            elif event.type == pygame.KEYDOWN and menu_tomar is not None:
                manejar_tecla_menu_tomar(event)

            elif event.type == pygame.MOUSEMOTION and menu_tomar is not None:
                menu_tomar.usando_teclado = False

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and menu_tomar is not None
            ):
                # La vista usa coordenadas reales de la ventana.
                clic_menu_tomar(event.pos)

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and current_scene == "interior"
                and not checkout_open and cierre is None
                and furniture_manager.carrying is None
                and (rect_libro := table_object_manager.rect_recetario(furniture_manager))
                and rect_libro.inflate(8, 8).collidepoint(
                    event.pos[0] // SCALE, event.pos[1] // SCALE)
            ):
                # Clic en el libro del mostrador.
                abrir_recetario()

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and current_scene == "interior"
                and not checkout_open and cierre is None and pedido_abierto is None
                and furniture_manager.carrying is None
                and (rect_tel := table_object_manager.rect_telefono(furniture_manager))
                and rect_tel.inflate(8, 8).collidepoint(
                    event.pos[0] // SCALE, event.pos[1] // SCALE)
            ):
                abrir_pedido()

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and current_scene == "interior"
                and checkout_open
            ):
                point = (event.pos[0] // SCALE, event.pos[1] // SCALE)
                if calculadora_visible():
                    if calc_mod.PANEL.collidepoint(point):
                        # Clic en la calculadora: el teclado pasa a ella.
                        calc_foco = True
                        boton = calculadora.boton_en(point)
                        if boton is not None:
                            calculadora.presionar(boton)
                        continue
                    # La factura está corrida a la izquierda.
                    point = (point[0] + calc_mod.DESPLAZAMIENTO, point[1])
                    calc_foco = False
                if vuelto_pendiente():
                    pass
                elif (not calc_desbloqueada and checkout_receipt_total is None
                      and CHECKOUT_CALC_BUTTON.collidepoint(point)):
                    comprar_calculadora()
                elif checkout_receipt_total is not None:
                    cerrar_factura()
                elif CHECKOUT_CANCEL_BUTTON.collidepoint(point):
                    cerrar_factura()
                elif CHECKOUT_PAY_BUTTON.collidepoint(point):
                    cobrar_factura()
                elif checkout_exercise is not None:
                    if (checkout_exercise.indice_vuelto is not None
                            and CHECKOUT_VUELTO_FIELD.collidepoint(point)):
                        checkout_exercise.seleccionar(checkout_exercise.indice_vuelto)
                        continue
                    if CHECKOUT_TOTAL_FIELD.collidepoint(point):
                        checkout_exercise.seleccionar(checkout_exercise.indice_total)
                    else:
                        for index, rect in checkout_visible_rows(checkout_exercise):
                            if rect.collidepoint(point):
                                checkout_exercise.seleccionar(index)
                                break

            elif event.type == pygame.TEXTINPUT and current_scene == "escribir_nombre":
                # Solo letras (con tildes y ñ) y espacios.
                for letra in event.text:
                    if (letra.isalpha() or letra == " ") and len(nombre_jugador) < NOMBRE_MAX:
                        if letra == " " and (not nombre_jugador or nombre_jugador.endswith(" ")):
                            continue
                        nombre_jugador += letra

            elif event.type == pygame.KEYDOWN and elegir_modo is not None:
                manejar_tecla_elegir_modo(event)

            elif event.type == pygame.KEYDOWN and elegir_continuar is not None:
                manejar_tecla_elegir_continuar(event)

            elif event.type == pygame.KEYDOWN and pregunta_tutorial is not None:
                manejar_tecla_pregunta_tutorial(event)

            elif event.type == pygame.KEYDOWN and confirmar_nueva is not None:
                manejar_tecla_confirmar(event)

            elif event.type == pygame.KEYDOWN:

                if current_scene == "menu":

                    if event.key == pygame.K_UP:
                        selected_option = (
                            selected_option - 1
                        ) % len(menu_options)

                    elif event.key == pygame.K_DOWN:
                        selected_option = (
                            selected_option + 1
                        ) % len(menu_options)

                    elif event.key == pygame.K_RETURN:

                        option = menu_options[selected_option]

                        if option == "JUGAR":
                            # Partida nueva de cero (si hay una guardada, pregunta antes).
                            pedir_partida_nueva(con_tutorial=False)

                        elif option == "CONTINUAR":
                            # Historia y libre son partidas aparte: si hay
                            # de las dos, pregunta cuál.
                            abrir_continuar()

                        elif option == "AYUDA":
                            current_scene = "ayuda"

                        elif option == "OPCIONES":
                            opciones_seleccion = FILA_SONIDO
                            current_scene = "opciones"

                        elif option == "SALIR":
                            running = False

                elif current_scene == "elegir_skin":

                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                        skin_seleccion = 1 - skin_seleccion
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        nombre_aviso = False
                        current_scene = "escribir_nombre"
                    elif event.key == pygame.K_ESCAPE:
                        current_scene = "opciones" if tutorial_desde_opciones else "menu"

                elif current_scene == "escribir_nombre":

                    if event.key == pygame.K_BACKSPACE:
                        nombre_jugador = nombre_jugador[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if not nombre_jugador.strip():
                            nombre_aviso = True
                        else:
                            nombre_jugador = " ".join(nombre_jugador.split())
                            # Todo de cero: tienda, bodega, muebles, saldo, ropa...
                            nueva_partida_completa()
                            table_object_manager.nombre = nombre_bonito()
                            player.set_skin(SKINS_ORDEN[skin_seleccion])
                            cosmeticos.vestir(player, mascota, perro)
                            player.reset()
                            checkout_open = False
                            checkout_exercise = None
                            checkout_receipt_total = None
                            current_scene = "interior"
                            ultima_zona = "interior"
                            # El tutorial solo se juega desde el botón TUTORIAL.
                            if forzar_tutorial:
                                if historia_elegida and not tutorial_desde_opciones:
                                    # Historia: Doña Rosa aparece al terminar el tutorial.
                                    historia_activa = True
                                    historia_nivel_base = nivel_actual
                                iniciar_tutorial()
                                guardar_partida()
                            else:
                                tutorial.terminar()
                                clientes.tutorial = False
                                if historia_elegida:
                                    # MODO HISTORIA: Doña Rosa guía la semana; saluda
                                    # y pregunta qué mascotas quieres. (En el modo
                                    # LIBRE no aparece nunca.)
                                    historia_activa = True
                                    historia_nivel_base = nivel_actual
                                    abrir_bienvenida(True)
                                else:
                                    abrir_cartel()      # LIBRE: el nombre del cartel
                                # Se empieza en la acera, frente a la tienda; los
                                # clientes llegan cuando el pulpero entra.
                                current_scene = "entrada"
                                ultima_zona = "entrada"
                                player.x, player.y, player.direction = 320, 240, "up"
                                calle.poblar(player, reloj.es_noche)
                                clientes.esperando_jugador = True
                                guardar_partida()   # la nueva reemplaza a la vieja
                    elif event.key == pygame.K_ESCAPE:
                        current_scene = "elegir_skin"

                elif current_scene == "sonido":
                    clave = FILAS_SONIDO[sonido_seleccion][0]
                    if event.key == pygame.K_UP:
                        sonido_seleccion = (sonido_seleccion - 1) % len(FILAS_SONIDO)
                    elif event.key == pygame.K_DOWN:
                        sonido_seleccion = (sonido_seleccion + 1) % len(FILAS_SONIDO)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        cambiar_sonido(clave, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        cambiar_sonido(clave, -1)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        cambiar_sonido(clave, 1, enter=clave.startswith("probar"))
                    elif event.key == pygame.K_ESCAPE:
                        current_scene = "opciones"

                elif current_scene == "extras":
                    if event.key == pygame.K_UP:
                        extras_seleccion = (extras_seleccion - 1) % len(FILAS_EXTRAS)
                        if FILAS_EXTRAS[extras_seleccion] == "cuales" and not EXTRAS["mascotas"]:
                            extras_seleccion = (extras_seleccion - 1) % len(FILAS_EXTRAS)
                    elif event.key == pygame.K_DOWN:
                        extras_seleccion = (extras_seleccion + 1) % len(FILAS_EXTRAS)
                        if FILAS_EXTRAS[extras_seleccion] == "cuales" and not EXTRAS["mascotas"]:
                            extras_seleccion = (extras_seleccion + 1) % len(FILAS_EXTRAS)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN,
                                       pygame.K_KP_ENTER, pygame.K_SPACE):
                        cambiar_extra(FILAS_EXTRAS[extras_seleccion], 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        cambiar_extra(FILAS_EXTRAS[extras_seleccion], -1)
                    elif event.key == pygame.K_ESCAPE:
                        current_scene = "opciones"

                elif current_scene == "visuales":
                    clave = FILAS_VISUALES[visual_seleccion][0]
                    if event.key == pygame.K_UP:
                        visual_seleccion = (visual_seleccion - 1) % len(FILAS_VISUALES)
                    elif event.key == pygame.K_DOWN:
                        visual_seleccion = (visual_seleccion + 1) % len(FILAS_VISUALES)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN,
                                       pygame.K_KP_ENTER, pygame.K_SPACE):
                        cambiar_visual(clave, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        cambiar_visual(clave, -1)
                    elif event.key == pygame.K_ESCAPE:
                        current_scene = "opciones"

                elif current_scene == "modo_juego":
                    total_filas = len(modos.ORDEN)
                    if event.key == pygame.K_UP:
                        modo_seleccion = (modo_seleccion - 1) % total_filas
                    elif event.key == pygame.K_DOWN:
                        modo_seleccion = (modo_seleccion + 1) % total_filas
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE,
                                       pygame.K_LEFT, pygame.K_RIGHT):
                        clave = modos.ORDEN[modo_seleccion]
                        MODO[clave] = not MODO[clave]
                        paciencia_activa = MODO["paciencia"]
                        clientes.paciencia_activa = paciencia_activa
                    elif event.key == pygame.K_ESCAPE:
                        current_scene = "opciones"

                elif current_scene == "reporte":
                    if event.key == pygame.K_ESCAPE:
                        current_scene = "extras"
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                        cambiar_reporte(1 if event.key in (pygame.K_RIGHT, pygame.K_d) else -1)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_g):
                        guardar_reporte_csv()

                elif current_scene == "ayuda":
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                        cerrar_ayuda()

                elif current_scene == "opciones":

                    if event.key == pygame.K_UP:
                        opciones_seleccion = (opciones_seleccion - 1) % FILAS_OPCIONES
                    elif event.key == pygame.K_DOWN:
                        opciones_seleccion = (opciones_seleccion + 1) % FILAS_OPCIONES
                    elif opciones_seleccion == FILA_EXTRAS and event.key in (
                            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_RIGHT):
                        extras_seleccion = 0
                        current_scene = "extras"
                    elif opciones_seleccion == FILA_DIFICULTAD and event.key in (
                            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE,
                            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                        paso = -1 if event.key in (pygame.K_LEFT, pygame.K_a) else 1
                        i = ORDEN_NIVELES.index(nivel_actual)
                        nivel_actual = ORDEN_NIVELES[(i + paso) % len(ORDEN_NIVELES)]
                    elif opciones_seleccion == FILA_TUTORIAL and event.key in (
                            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        # La partida empieza con el tutorial guiado (también de cero).
                        tutorial_desde_opciones = True
                        pedir_partida_nueva(con_tutorial=True)
                    elif opciones_seleccion == FILA_SONIDO and event.key in (
                            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        sonido_seleccion = 0
                        current_scene = "sonido"
                    elif opciones_seleccion == FILA_VISUAL and event.key in (
                            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_RIGHT):
                        visual_seleccion = 0
                        current_scene = "visuales"
                    elif opciones_seleccion == FILA_MODO and event.key in (
                            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_RIGHT):
                        modo_seleccion = 0
                        current_scene = "modo_juego"
                    elif event.key == pygame.K_ESCAPE:
                        current_scene = "menu"

                elif current_scene == "interior":

                    if checkout_open:
                        # El teclado controla solo la factura, no al personaje.
                        if vuelto_pendiente():
                            # Avanzado: hay que dar el vuelto antes de seguir.
                            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                revisar_vuelto()
                            elif event.key == pygame.K_BACKSPACE:
                                vuelto["valor"] = vuelto["valor"][:-1]
                            elif event.unicode.isdigit() and len(vuelto["valor"]) < 4:
                                vuelto["valor"] += event.unicode

                        elif event.key == pygame.K_ESCAPE:
                            cerrar_factura()

                        elif checkout_receipt_total is not None:
                            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                cerrar_factura()

                        elif table_object_manager.get_counter_sale_summary()["count"] == 0:
                            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                cerrar_factura()

                        elif event.key == pygame.K_c and not calc_desbloqueada:
                            comprar_calculadora()      # C: pagar la calculadora

                        elif calculadora_visible() and event.key == pygame.K_SPACE:
                            calc_foco = not calc_foco

                        elif calculadora_visible() and calc_foco:
                            calculadora.tecla(event)

                        elif checkout_exercise is not None:
                            exercise = checkout_exercise
                            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                if exercise.en_boton_cobrar:
                                    cobrar_factura()
                                else:
                                    indice = exercise.actual
                                    escrito = exercise.valores[indice]
                                    # Solo cuenta como error si escribió algo.
                                    acierto = exercise.verificar()
                                    if escrito and not tutorial.activo:
                                        # REPORTE: cada respuesta de la factura.
                                        if indice == getattr(exercise, "indice_vuelto", None):
                                            clave = "vuelto"
                                        elif (indice != exercise.indice_total and MODO["contar"]
                                              and not factura_muestra_cantidad()):
                                            clave = "contar"
                                        else:
                                            clave = "factura"
                                        estadisticas.registrar(clave, acierto)
                                    if not acierto and escrito:
                                        registrar_error_factura(indice)

                            elif event.key == pygame.K_BACKSPACE:
                                exercise.borrar()

                            elif event.key in (pygame.K_UP,):
                                exercise.seleccionar(max(0, exercise.actual - 1))

                            elif event.key in (pygame.K_DOWN, pygame.K_TAB):
                                exercise.seleccionar(min(exercise.indice_total, exercise.actual + 1))

                            elif event.unicode and event.unicode in "0123456789":
                                exercise.ingresar(event.unicode)

                    elif event.key == pygame.K_ESCAPE:
                        abrir_pausa()

                    elif event.key == pygame.K_p:
                        # P: el cliente repite su pedido (ayuda de memoria).
                        clientes.repetir()

                    elif event.key == pygame.K_r:
                        # R: libro de recetas.
                        abrir_recetario()

                    elif event.key == pygame.K_SPACE and furniture_manager.carrying is None:
                        # ESPACIO: empujar o soltar el carrito.
                        alternar_carrito()


                    elif event.key == pygame.K_q:
                        # Q devuelve el último producto tomado a la mesa de enfrente.
                        if furniture_manager.carrying is None:
                            table_object_manager.devolver(player, furniture_manager)

                    elif event.key == pygame.K_e:
                        if event.mod & pygame.KMOD_SHIFT:
                            # Shift+E queda reservado para muebles completos.
                            if furniture_manager.carrying is not None:
                                if not furniture_manager.drop():
                                    table_object_manager.avisar(
                                        "¡Ahí hay alguien!",
                                        "Pon el mueble en otro lugar.",
                                    )
                            elif table_object_manager.mano:
                                table_object_manager.avisar(
                                    "Primero deja lo que llevas",
                                    "en las manos.",
                                )
                            else:
                                furniture_manager.try_pickup(player)
                        else:
                            # E toma productos (hasta 3), los deja en el
                            # mostrador o abre la caja si las manos están vacías.
                            mueble = None
                            letrero = furniture_manager.carrying is None and cerca_letrero()
                            punto = (table_object_manager.punto_del_mostrador(player, furniture_manager)
                                     if furniture_manager.carrying is None
                                     and not table_object_manager.mano else None)
                            libro = punto == "recetario"
                            if letrero:
                                # Junto a la puerta: darle vuelta al letrero.
                                alternar_tienda()
                            elif furniture_manager.carrying is None and cerca_de_ayudante():
                                abrir_pago_ayudante()
                                letrero = True
                            elif furniture_manager.carrying is None and cerca_boton(player):
                                aviso = ayudante.llamar(dia, reloj.hora)
                                if aviso:
                                    table_object_manager.avisar(aviso, "")
                                letrero = True
                            elif punto == "telefono":
                                # Teléfono: pedir insumos al camión.
                                abrir_pedido()
                                letrero = True
                            elif libro:
                                # La hoja del mostrador es el libro de recetas.
                                abrir_recetario()
                                letrero = True  # ya se usó la E
                            elif (furniture_manager.carrying is None and not table_object_manager.mano
                                  and MASCOTAS["gata"] and mascota.cerca(player, "interior")):
                                # Junto a Canela: acariciarla.
                                mascota.acariciar()
                                letrero = True
                            elif (furniture_manager.carrying is None and not table_object_manager.mano
                                  and MASCOTAS["perro"] and perro.cerca(player, "interior")):
                                perro.acariciar()
                                letrero = True
                            elif (furniture_manager.carrying is None and not table_object_manager.mano
                                  and MASCOTAS["gata"] and casa_gato.cerca(player)):
                                # Junto a su casa: ver la mejora.
                                abrir_casa_menu()
                                letrero = True
                            elif furniture_manager.carrying is None:
                                mueble = table_object_manager.mueble_para_elegir(
                                    player, furniture_manager
                                )
                            if letrero:
                                pass
                            elif mueble is not None:
                                abrir_menu_tomar("tienda", mueble)
                            elif furniture_manager.carrying is None:
                                accion = table_object_manager.accion_e(
                                    player, furniture_manager
                                )
                                ok_pedido = None
                                if accion == "caja":
                                    ok_pedido, _ = clientes.revisar(
                                        table_object_manager.get_counter_sale_summary()
                                    )
                                    if ok_pedido is None:
                                        table_object_manager.avisar(
                                            "Todavía no hay ningún cliente.",
                                            "¡Espera a que llegue uno!",
                                        )
                                if accion == "caja" and ok_pedido:
                                    checkout_open = True
                                    resumen = table_object_manager.get_counter_sale_summary()
                                    total_venta = sum(g["quantity"] * g["unit_price"]
                                                      for g in resumen["groups"])
                                    checkout_exercise = FacturaInteractiva(
                                        resumen,
                                        pago=((10 if tutorial.activo else pago_cliente(total_venta))
                                              if MODO["vuelto"] else None),
                                    )
                                    checkout_receipt_total = None
                                    calculadora.limpiar()
                                    calc_foco = False
                                    calc_errores = 0
                                    calc_desbloqueada = False
                                    errores_por_fila.clear()
                                    pistas_por_fila.clear()

                elif current_scene in ("entrada", "inventario"):
                    if event.key == pygame.K_e and current_scene == "entrada" and cerca_letrero():
                        alternar_tienda()
                    elif (event.key == pygame.K_e and current_scene == "entrada"
                          and MASCOTAS["gata"] and mascota.cerca(player, "entrada")):
                        mascota.acariciar()
                    elif (event.key == pygame.K_e and current_scene == "entrada"
                          and MASCOTAS["perro"] and perro.cerca(player, "entrada")):
                        perro.acariciar()
                    elif (event.key == pygame.K_e and current_scene == "entrada"
                          and camion.caja_cerca(player) is not None):
                        abrir_menu_caja(camion.caja_cerca(player))
                    elif event.key == pygame.K_e and current_scene == "inventario" and cerca_armario():
                        abrir_armario()
                    elif event.key == pygame.K_e and current_scene == "inventario":
                        lleno = len(table_object_manager.mano) >= table_object_manager.MAX_MANOS
                        if not lleno and bodega.opciones_cerca(player):
                            abrir_menu_tomar("bodega")
                        else:
                            bodega.tomar(player, table_object_manager)
                    elif event.key == pygame.K_q and current_scene == "inventario":
                        bodega.devolver(table_object_manager)
                    elif event.key == pygame.K_r and current_scene == "inventario":
                        abrir_recetario()
                    elif event.key == pygame.K_SPACE and current_scene == "inventario":
                        alternar_carrito()
                    elif event.key == pygame.K_ESCAPE:
                        abrir_pausa()

        table_object_manager.actualizar_aviso(dt)
        jugando = (current_scene in ("interior", "entrada", "inventario")
                   and pausa is None and dialogo is None and cartel_edit is None)
        if jugando:
            clientes.actualizar(dt, productos_disponibles,
                                pausado=checkout_open or recetario.abierto or historial_abierto,
                                hora=reloj.hora)
            # Con la tienda cerrada y sin clientes adentro, el reloj se detiene.
            if current_scene == "interior":
                clientes.esperando_jugador = False      # ya entró a la tienda
            # Después de las 6:00 p. m. el reloj sigue hasta las 8 (acomodar).
            if (cierre is None and (clientes.abierta or clientes.lista or reloj.cerro)
                    and not clientes.esperando_jugador):
                reloj.actualizar(
                    dt, clientes.atendidos + clientes.perdidos,
                    clientes.limite_jornada,
                    clientes.jornada_terminada(),
                )
            # A las 6:00 p. m. la tienda cierra, haya clientes o no.
            if reloj.cerro and not hora_de_acomodar and cierre is None:
                cerrar_por_hora()

        if jugando:       # con el menú de pausa abierto, todo se detiene
            camion.actualizar(dt, dia, reloj.hora)
            if MASCOTAS["gata"]:
                mascota.nivel_casa = casa_gato.nivel
                mascota.actualizar(dt)
            if MASCOTAS["perro"]:
                perro.actualizar(dt)
            # De vez en cuando Bruno persigue a Canela por la tienda.
            persecucion.actualizar(mascota, perro, dt,
                                   activos=MASCOTAS["gata"] and MASCOTAS["perro"])
            if camion.recien_llegado:
                camion.recien_llegado = False
                table_object_manager.avisar("¡Llegó el camión con tu pedido!",
                                            "Las cajas están afuera, a la izquierda.")
                sonido.efecto("timbre")
            ayudante.actualizar(dt, reloj.hora, table_object_manager, furniture_manager, bodega)
            if reloj.fin_dia and ayudante.estado == "trabajando":
                # Se acabó el día: Tavo termina su turno y viene a cobrar.
                ayudante.terminar_turno(table_object_manager, bodega)

        if (cierre is None and not checkout_open and menu_tomar is None
                and current_scene in ("interior", "entrada", "inventario")
                and reloj.fin_dia and not clientes.lista and not ayudante.presente):
            abrir_cierre()          # 8:00 p. m. (o TERMINAR EL DÍA): cierre de caja
        revisar_meta()          # MODO HISTORIA: felicitar al cumplir la meta

        if (menu_tomar is not None or cierre is not None or recetario.abierto
                or historial_abierto or pago_ayudante is not None or pausa is not None
                or dialogo is not None or cartel_edit is not None
                or pedido_abierto is not None or menu_caja is not None
                or armario is not None or casa_menu is not None):
            pass  # Menú, cierre o recetario abiertos: el personaje espera quieto.

        elif current_scene == "interior" and not checkout_open:
            keys = pygame.key.get_pressed()

            if table_object_manager.carrying is not None:
                table_object_manager.update(dt, keys)
            elif furniture_manager.carrying is not None:
                furniture_manager.update(dt, keys)
            else:
                antes = (player.x, player.y)
                obstaculos = (furniture_manager.get_collision_rects()
                              + [rect_letrero("interior"), rect_boton()]
                              + ([casa_gato.rect_choque()] if MASCOTAS["gata"] else []))
                player.update(dt, keys, GAME_WIDTH, GAME_HEIGHT, obstaculos, FLOOR_TOP)
                # El carrito va adelante y no se mete en ningún mueble (ni en su tapa).
                obstaculos_carrito = obstaculos + muebles_para_carrito()
                if carrito.bloquea(player, obstaculos_carrito, FLOOR_TOP):
                    player.x, player.y = antes
                carrito.seguir(player, obstaculos_carrito, FLOOR_TOP)
                destino = destino_al_cruzar("interior", antes, (player.x, player.y))
                if destino is not None:
                    viajar_a_zona(destino, "interior")

        elif current_scene == "entrada":
            calle.actualizar(dt, player, reloj.es_noche, nombre=nombre_bonito())
            antes = (player.x, player.y)
            player.update(
                dt, pygame.key.get_pressed(), GAME_WIDTH, GAME_HEIGHT,
                [rect_letrero("entrada"), rect_poste()] + camion.obstaculos(), EXTERIOR_FLOOR_TOP
            )
            destino = destino_al_cruzar("entrada", antes, (player.x, player.y))
            if destino is not None:
                viajar_a_zona(destino, "entrada")

        elif current_scene == "inventario":
            antes = (player.x, player.y)
            player.update(
                dt, pygame.key.get_pressed(), GAME_WIDTH, GAME_HEIGHT,
                obstaculos_inventario(), INVENTARIO_FLOOR_TOP
            )
            if carrito.bloquea(player, obstaculos_inventario(), INVENTARIO_FLOOR_TOP):
                player.x, player.y = antes
            carrito.seguir(player, obstaculos_inventario(), INVENTARIO_FLOOR_TOP)
            destino = destino_al_cruzar("inventario", antes, (player.x, player.y))
            if destino is not None:
                viajar_a_zona(destino, "inventario")

        sonidos_por_cambios()
        sonido.actualizar_ambiente(
            dt, current_scene if current_scene in ("interior", "entrada", "inventario") else None,
            oscuridad())

        if current_scene == "interior":
            luciernagas.actualizar(dt)
        elif current_scene == "entrada":
            luciernagas_calle.actualizar(dt)
        if tutorial.activo and current_scene in ("interior", "entrada", "inventario"):
            if tutorial.actualizar(dt, estado_tutorial()):
                terminar_tutorial()
            tutorial_enter = False

        autoguardar(dt)
        draw()

        presentar()

    guardar_partida()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
