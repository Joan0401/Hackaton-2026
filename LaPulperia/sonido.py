"""Música, efectos y ruido de fondo (OPCIONES > SONIDO).

- Música del MENÚ: marimba, alegre (8 bits) o tranquila.
- Música de la TIENDA (mientras se juega): siempre tranquila y relajante;
  se elige entre piano tranquilo, guitarra suave, marimba suave o cajita
  de música. Cada estilo tiene tres canciones distintas que se alternan
  (en desorden, sin repetir la misma dos veces seguidas).
- Efectos: abrir caja, cobrar, tomar, dejar, acierto, error, campanita...
- Ruido de fondo: viento y carros afuera; grillos de noche.
Los archivos están en la carpeta "sonidos". Si la computadora no tiene
sonido, el juego sigue funcionando sin él.
"""
import os
import random

import pygame

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sonidos")
FIN_CANCION = pygame.USEREVENT + 7

ESTILOS = {
    "MARIMBA": [("marimba_1", "El Pulpero"), ("marimba_2", "Mercado de Antigua"),
                ("marimba_3", "Domingo en el Parque")],
    "ALEGRE (8 BITS)": [("alegre_1", "Caja Registradora"), ("alegre_2", "Corre Carrito"),
                        ("alegre_3", "Ofertas del Día")],
    "TRANQUILA": [("tranquila_1", "Amanecer"), ("tranquila_2", "Tarde de Lluvia"),
                  ("tranquila_3", "Noche de Luciérnagas")],
    "SIN MÚSICA": [],
}
ORDEN_ESTILOS = list(ESTILOS)
# Música de la tienda. Las ACTIVAS (rápidas, con ritmo, para animar) se
# generan con herramientas/gen_musica_activa.py; las tranquilas, con
# herramientas/gen_musica_tienda.py.
ESTILOS_TIENDA = {
    "MARIMBA ALEGRE": [("marimba_alegre_1", "Pulpería en Fiesta"), ("marimba_alegre_2", "Feria del Pueblo"),
                       ("marimba_alegre_3", "Corre que Corre")],
    "CUMBIA": [("cumbia_1", "Cumbia del Mostrador"), ("cumbia_2", "Bailando con Canela"),
               ("cumbia_3", "La Cumbia del Vuelto")],
    "8 BITS SALTARÍN": [("saltarin_1", "Salta Salta"), ("saltarin_2", "Carrito Turbo"),
                        ("saltarin_3", "Súper Pulpero")],
    "ALEGRE (8 BITS)": ESTILOS["ALEGRE (8 BITS)"],
    "PIANO TRANQUILO": ESTILOS["TRANQUILA"],
    "GUITARRA SUAVE": [("guitarra_1", "Hamaca"), ("guitarra_2", "Café de la Tarde"),
                       ("guitarra_3", "Camino al Volcán")],
    "MARIMBA SUAVE": [("marimba_suave_1", "Brisa del Lago"), ("marimba_suave_2", "Siesta"),
                      ("marimba_suave_3", "Patio con Flores")],
    "CAJITA DE MÚSICA": [("cajita_1", "Estrellitas"), ("cajita_2", "Lluvia Suave"),
                         ("cajita_3", "Buenas Noches")],
    "SIN MÚSICA": [],
}
ORDEN_ESTILOS_TIENDA = list(ESTILOS_TIENDA)
EFECTOS = {
    "COBRAR": "cobrar", "ABRIR CAJA": "abrir_caja", "TOMAR PRODUCTO": "tomar",
    "DEJAR PRODUCTO": "dejar", "RESPUESTA CORRECTA": "acierto", "ERROR": "error",
    "LLEGA UN CLIENTE": "campanita", "TIMBRE DEL AYUDANTE": "timbre", "¡LOGRO!": "logro",
}
ORDEN_EFECTOS = list(EFECTOS)
AMBIENTES = {"VIENTO": "viento", "CARROS": "carros", "GRILLOS": "grillos"}
ORDEN_AMBIENTES = list(AMBIENTES)

# Ajustes (se cambian en OPCIONES > SONIDO)
estilo = "ALEGRE (8 BITS)"            # música del menú
estilo_tienda = "MARIMBA ALEGRE"      # música mientras se juega (activa)
zona = "menu"                         # "menu" o "tienda": qué música suena
cancion = 0
volumen_musica = 3          # 0 a 10
efectos_activos = True
volumen_efectos = 3
ambiente_activo = True
volumen_ambiente = 3

_listo = None
_sonidos = {}
_canales = {}
_vol_ambiente = {nombre: 0.0 for nombre in AMBIENTES.values()}
_prueba_ambiente = None     # (nombre, segundos) mientras se escucha una prueba


def disponible():
    """Inicia el mezclador la primera vez. False si no hay sonido."""
    global _listo
    if _listo is None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(22050, -16, 2, 512)
            pygame.mixer.set_num_channels(16)
            pygame.mixer.music.set_endevent(FIN_CANCION)
            _listo = True
        except pygame.error:
            _listo = False
    return _listo


def _sonido(nombre):
    if nombre not in _sonidos:
        ruta = os.path.join(CARPETA, nombre + ".ogg")
        try:
            _sonidos[nombre] = pygame.mixer.Sound(ruta)
        except (pygame.error, FileNotFoundError):
            _sonidos[nombre] = None
    return _sonidos[nombre]


# ---------------------------------------------------------
# MÚSICA
# ---------------------------------------------------------
def estilo_actual():
    return estilo_tienda if zona == "tienda" else estilo


def canciones_actuales():
    return ESTILOS_TIENDA[estilo_tienda] if zona == "tienda" else ESTILOS[estilo]


def titulo_cancion():
    canciones = canciones_actuales()
    if not canciones:
        return ""
    return canciones[cancion % len(canciones)][1]


def poner_zona(nueva):
    """'menu' o 'tienda'. Al cambiar, empieza una canción al azar de esa música."""
    global zona, cancion
    if nueva == zona:
        return
    zona = nueva
    canciones = canciones_actuales()
    cancion = random.randrange(len(canciones)) if canciones else 0
    tocar_musica()


def tocar_musica():
    """Empieza (o cambia) la canción actual del estilo elegido."""
    if not disponible():
        return
    canciones = canciones_actuales()
    if not canciones:
        pygame.mixer.music.stop()
        return
    archivo = os.path.join(CARPETA, canciones[cancion % len(canciones)][0] + ".ogg")
    try:
        pygame.mixer.music.load(archivo)
        pygame.mixer.music.set_volume(volumen_musica / 10 * 0.6)
        pygame.mixer.music.play(fade_ms=600)
    except pygame.error:
        pass


def siguiente_cancion():
    """Al terminar una canción suena la siguiente del mismo estilo."""
    global cancion
    canciones = canciones_actuales()
    if canciones:
        # Otra canción del mismo estilo, nunca la misma dos veces seguidas.
        otras = [i for i in range(len(canciones)) if i != cancion % len(canciones)] or [0]
        cancion = random.choice(otras)
        tocar_musica()


def cambiar_estilo(paso):
    global estilo, cancion
    estilo = ORDEN_ESTILOS[(ORDEN_ESTILOS.index(estilo) + paso) % len(ORDEN_ESTILOS)]
    cancion = 0
    if zona == "menu":
        tocar_musica()


def cambiar_estilo_tienda(paso):
    global estilo_tienda, cancion
    estilo_tienda = ORDEN_ESTILOS_TIENDA[(ORDEN_ESTILOS_TIENDA.index(estilo_tienda) + paso)
                                         % len(ORDEN_ESTILOS_TIENDA)]
    cancion = 0
    if zona == "tienda":
        tocar_musica()


def cambiar_volumen_musica(paso):
    global volumen_musica
    volumen_musica = max(0, min(10, volumen_musica + paso))
    if disponible():
        pygame.mixer.music.set_volume(volumen_musica / 10 * 0.6)


# ---------------------------------------------------------
# EFECTOS
# ---------------------------------------------------------
def efecto(nombre, forzar=False):
    """Suena un efecto (si los efectos están activados)."""
    if not (efectos_activos or forzar) or not disponible():
        return
    s = _sonido("fx_" + nombre)
    if s is not None:
        s.set_volume(volumen_efectos / 10)
        s.play()


def cambiar_volumen_efectos(paso):
    global volumen_efectos
    volumen_efectos = max(0, min(10, volumen_efectos + paso))
    efecto("acierto")


# ---------------------------------------------------------
# RUIDO DE FONDO
# ---------------------------------------------------------
def _objetivos(escena, noche):
    """Qué tan fuerte suena cada ambiente según dónde estás y la hora."""
    if escena == "entrada":
        return {"viento": 0.55, "carros": 0.6 * (1 - 0.5 * noche), "grillos": 0.8 * noche}
    if escena == "interior":
        return {"viento": 0.12, "carros": 0.15 * (1 - 0.5 * noche), "grillos": 0.3 * noche}
    if escena == "inventario":
        return {"viento": 0.08, "carros": 0.06, "grillos": 0.2 * noche}
    return {"viento": 0.0, "carros": 0.0, "grillos": 0.0}


def actualizar_ambiente(dt, escena, noche):
    """Sube o baja poco a poco cada ambiente (se llama en cada cuadro)."""
    global _prueba_ambiente
    if not disponible():
        return
    objetivos = _objetivos(escena, noche) if ambiente_activo else dict.fromkeys(_vol_ambiente, 0.0)
    if _prueba_ambiente is not None:
        nombre, quedan = _prueba_ambiente
        objetivos = dict.fromkeys(_vol_ambiente, 0.0)
        objetivos[nombre] = 0.9
        quedan -= dt
        _prueba_ambiente = (nombre, quedan) if quedan > 0 else None
    for nombre, objetivo in objetivos.items():
        objetivo *= volumen_ambiente / 10
        actual = _vol_ambiente[nombre]
        actual += (objetivo - actual) * min(1.0, dt * 1.5)
        _vol_ambiente[nombre] = actual
        canal = _canales.get(nombre)
        if actual > 0.01 and canal is None:
            s = _sonido("amb_" + nombre)
            if s is not None:
                canal = s.play(loops=-1)
                _canales[nombre] = canal
        if canal is not None:
            canal.set_volume(actual)
            if actual <= 0.01:
                canal.stop()
                _canales.pop(nombre, None)


def probar_ambiente(nombre_pantalla):
    """Deja sonar solo ese ambiente unos segundos (para escucharlo)."""
    global _prueba_ambiente
    _prueba_ambiente = (AMBIENTES[nombre_pantalla], 3.5)


def cambiar_volumen_ambiente(paso):
    global volumen_ambiente
    volumen_ambiente = max(0, min(10, volumen_ambiente + paso))
