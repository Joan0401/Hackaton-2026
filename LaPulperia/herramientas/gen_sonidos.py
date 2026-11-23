"""Genera la música, los efectos y los ambientes de La Pulpería (OGG).

Todo es sintetizado: marimba, chiptune (8 bits) y piano suave; efectos de
caja registradora, campanita, etc.; y ambientes de viento, tráfico y grillos.
Uso: python gen_sonidos.py <carpeta_destino>
"""
import os
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import butter, lfilter

SR = 22050
DEST = sys.argv[1]
os.makedirs(DEST, exist_ok=True)
rng_global = np.random.default_rng(7)


def guardar(nombre, señal, calidad=3):
    señal = np.asarray(señal, dtype=np.float64)
    pico = np.max(np.abs(señal)) or 1.0
    señal = señal / pico * 0.85
    datos = (señal * 32767).astype(np.int16)
    wav = os.path.join(DEST, nombre + ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(datos.tobytes())
    ogg = os.path.join(DEST, nombre + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis",
                    "-q:a", str(calidad), ogg], check=True)
    os.remove(wav)


def t_(dur):
    return np.arange(int(SR * dur)) / SR


def freq(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def env(n, ataque=0.005, caida=0.3, sostener=0.0, soltar=0.05):
    """Envolvente simple: ataque lineal y caída exponencial."""
    t = np.arange(n) / SR
    a = np.clip(t / max(ataque, 1e-4), 0, 1)
    d = sostener + (1 - sostener) * np.exp(-t / max(caida, 1e-4))
    e = a * d
    r = int(SR * soltar)
    if r and n > r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def filtro(señal, corte, tipo="low"):
    b, a = butter(2, corte / (SR / 2), btype=tipo)
    return lfilter(b, a, señal)


# ---------------------------------------------------------
# INSTRUMENTOS
# ---------------------------------------------------------
def marimba(m, dur, vol=1.0):
    t = t_(dur)
    f = freq(m)
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.05)
         + 0.15 * np.sin(2 * np.pi * f * 10 * t) * np.exp(-t / 0.015))
    return s * env(len(t), 0.002, 0.35, 0.0, 0.02) * vol


def cuadrada(m, dur, vol=1.0, ancho=0.25):
    t = t_(dur)
    fase = (freq(m) * t) % 1.0
    s = np.where(fase < ancho, 1.0, -1.0)
    return s * env(len(t), 0.003, dur * 0.8, 0.5, 0.02) * vol * 0.35


def triangular(m, dur, vol=1.0):
    t = t_(dur)
    fase = (freq(m) * t) % 1.0
    s = 4 * np.abs(fase - 0.5) - 1
    return s * env(len(t), 0.004, dur, 0.6, 0.02) * vol * 0.6


def piano(m, dur, vol=1.0):
    t = t_(dur)
    f = freq(m)
    s = sum((0.6 ** k) * np.sin(2 * np.pi * f * (k + 1) * t) for k in range(4))
    return s * env(len(t), 0.004, 0.9, 0.0, 0.1) * vol * 0.5


def pad(m, dur, vol=1.0):
    t = t_(dur)
    f = freq(m)
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.005 * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)
    e = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return s * e * vol * 0.25


def bombo(dur=0.18):
    t = t_(dur)
    f = 110 * np.exp(-t / 0.04) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07)


def charles(dur=0.05):
    n = int(SR * dur)
    return filtro(rng_global.standard_normal(n), 6000, "high") * np.exp(-np.arange(n) / SR / 0.012) * 0.5


def caja_ritmo(dur=0.12):
    n = int(SR * dur)
    ruido = filtro(rng_global.standard_normal(n), 1500, "high") * np.exp(-np.arange(n) / SR / 0.04)
    return ruido * 0.6


def mezclar(pista, sonido, inicio):
    i = int(inicio * SR)
    fin = min(len(pista), i + len(sonido))
    if i < len(pista):
        pista[i:fin] += sonido[:fin - i]


# ---------------------------------------------------------
# COMPOSITOR: progresión + melodía generada con una semilla
# ---------------------------------------------------------
ESCALA_MAYOR = [0, 2, 4, 5, 7, 9, 11]


def acorde(grado, tonica):
    """Notas MIDI del acorde (tríada) sobre ese grado de la escala mayor."""
    return [tonica + ESCALA_MAYOR[(grado + k) % 7] + 12 * ((grado + k) // 7) for k in (0, 2, 4)]


def cancion(estilo, semilla, tonica, tempo, progresion, compases_por_acorde=1, repeticiones=2):
    rng = np.random.default_rng(semilla)
    pulsos = 3 if estilo == "marimba" else 4
    negra = 60.0 / tempo
    compas = pulsos * negra
    total = len(progresion) * compases_por_acorde * repeticiones
    pista = np.zeros(int(SR * (total * compas + 1.5)))
    # La melodía se genera una vez y se repite (para que se pueda tararear).
    melodia = []
    nota = tonica + 12 + ESCALA_MAYOR[rng.integers(0, 3) * 2]
    for i, grado in enumerate(progresion * compases_por_acorde):
        notas_acorde = acorde(grado, tonica + 12)
        ritmos = ([[1, 1, 1], [2, 1], [1, 2], [0.5, 0.5, 1, 1]] if pulsos == 3
                  else [[1, 1, 1, 1], [2, 1, 1], [1, 1, 2], [0.5, 0.5, 1, 2], [1.5, 0.5, 2]])
        ritmo = ritmos[int(rng.integers(0, len(ritmos)))]
        compas_notas = []
        for duracion in ritmo:
            if rng.random() < 0.55:
                nota = int(rng.choice(notas_acorde) + 12 * rng.integers(0, 2))
            else:
                paso = int(rng.choice([-2, -1, 1, 2]))
                grados = [tonica + 12 + e + 12 * o for o in range(3) for e in ESCALA_MAYOR]
                idx = min(range(len(grados)), key=lambda k: abs(grados[k] - nota))
                nota = grados[max(0, min(len(grados) - 1, idx + paso))]
            nota = max(tonica + 12, min(tonica + 31, nota))
            compas_notas.append((nota, duracion))
        melodia.append(compas_notas)

    for r in range(repeticiones):
        for i, grado in enumerate(progresion * compases_por_acorde):
            inicio = (r * len(progresion) * compases_por_acorde + i) * compas
            notas_acorde = acorde(grado, tonica)
            bajo = notas_acorde[0] - 12
            # Acompañamiento
            if estilo == "marimba":
                mezclar(pista, marimba(bajo, negra * 0.9, 0.7), inicio)
                for p in (1, 2):
                    for n_ in notas_acorde[1:]:
                        mezclar(pista, marimba(n_, negra * 0.6, 0.25), inicio + p * negra)
            elif estilo == "alegre":
                for p in range(pulsos):
                    mezclar(pista, triangular(bajo if p % 2 == 0 else bajo + 7, negra * 0.9, 0.8), inicio + p * negra)
                    mezclar(pista, charles(), inicio + p * negra + negra / 2)
                mezclar(pista, bombo(), inicio)
                mezclar(pista, caja_ritmo(), inicio + negra)
                mezclar(pista, bombo(), inicio + 2 * negra)
                mezclar(pista, caja_ritmo(), inicio + 3 * negra)
                for k, n_ in enumerate(notas_acorde * 2):
                    mezclar(pista, cuadrada(n_ + 12, negra / 2 * 0.9, 0.12, 0.5), inicio + k * negra / 2)
            else:  # tranquila
                mezclar(pista, pad(bajo, compas, 0.8), inicio)
                for n_ in notas_acorde:
                    mezclar(pista, pad(n_, compas, 0.35), inicio)
                for k, n_ in enumerate(notas_acorde + [notas_acorde[1]]):
                    mezclar(pista, piano(n_, negra * 1.5, 0.25), inicio + k * negra)
            # Melodía
            t_nota = inicio
            for nota, duracion in melodia[i]:
                d = duracion * negra
                if estilo == "marimba":
                    # Redoble de marimba en las notas largas.
                    if duracion >= 2:
                        golpes = int(d / 0.09)
                        for g in range(golpes):
                            mezclar(pista, marimba(nota, 0.12, 0.5), t_nota + g * 0.09)
                    else:
                        mezclar(pista, marimba(nota, d, 1.0), t_nota)
                elif estilo == "alegre":
                    mezclar(pista, cuadrada(nota + 12, d * 0.95, 0.9, 0.25), t_nota)
                else:
                    mezclar(pista, piano(nota + 12, d * 1.6, 0.8), t_nota)
                t_nota += d
    # Final suave
    cola = int(SR * 1.2)
    pista[-cola:] *= np.linspace(1, 0, cola)
    return pista


MUSICA = {
    "marimba": [
        ("marimba_1", 11, 60, 132, [0, 3, 4, 0, 0, 3, 4, 0]),     # Do mayor, vals
        ("marimba_2", 22, 67, 140, [0, 4, 5, 3, 0, 4, 3, 4]),     # Sol mayor
        ("marimba_3", 33, 62, 124, [0, 5, 3, 4, 0, 5, 1, 4]),     # Re mayor
    ],
    "alegre": [
        ("alegre_1", 44, 60, 138, [0, 4, 5, 3, 0, 4, 3, 4]),
        ("alegre_2", 55, 65, 150, [0, 3, 0, 4, 5, 3, 1, 4]),
        ("alegre_3", 66, 62, 128, [0, 5, 3, 4, 0, 5, 3, 4]),
    ],
    "tranquila": [
        ("tranquila_1", 77, 60, 76, [0, 5, 3, 4, 0, 5, 3, 4]),
        ("tranquila_2", 88, 65, 70, [0, 3, 5, 4, 0, 3, 1, 4]),
        ("tranquila_3", 99, 67, 82, [0, 4, 5, 3, 0, 4, 3, 0]),
    ],
}

for estilo, canciones in MUSICA.items():
    for nombre, semilla, tonica, tempo, prog in canciones:
        guardar(nombre, cancion(estilo, semilla, tonica, tempo, prog,
                                compases_por_acorde=1, repeticiones=3), calidad=2)
        print("música:", nombre)


# ---------------------------------------------------------
# EFECTOS
# ---------------------------------------------------------
def campana(f, dur=0.6, vol=1.0):
    t = t_(dur)
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t)
    return s * np.exp(-t / (dur / 3)) * vol


def pieza(*partes):
    largo = max(int(SR * ini) + len(s) for ini, s in partes)
    out = np.zeros(largo)
    for ini, s in partes:
        mezclar(out, s, ini)
    return out


efectos = {}
# Caja registradora: cajón que se abre (ruido + golpe) y "ding".
n = int(SR * 0.25)
cajon = filtro(rng_global.standard_normal(n), 900) * np.linspace(0.2, 1, n) * np.exp(-np.arange(n) / SR / 0.2)
golpe = bombo(0.12) * 0.6
efectos["abrir_caja"] = pieza((0, cajon * 0.5), (0.2, golpe), (0.22, campana(1760, 0.5, 0.6)))
# Cobrar: "cha-ching" con monedas.
monedas = sum(campana(f, 0.25, 0.25) for f in (2637, 3136, 3520))
efectos["cobrar"] = pieza((0, campana(1568, 0.35, 0.7)), (0.09, campana(2093, 0.8, 1.0)),
                          (0.16, monedas), (0.24, monedas * 0.7))
efectos["tomar"] = pieza((0, np.sin(2 * np.pi * np.cumsum(np.linspace(500, 1100, int(SR * 0.08))) / SR)
                          * np.exp(-np.arange(int(SR * 0.08)) / SR / 0.03)))
efectos["dejar"] = pieza((0, bombo(0.1) * 0.7), (0, filtro(rng_global.standard_normal(int(SR * 0.05)), 1200)
                                                     * np.exp(-np.arange(int(SR * 0.05)) / SR / 0.01) * 0.4))
efectos["acierto"] = pieza((0, campana(1319, 0.3, 0.8)), (0.1, campana(1760, 0.5, 0.9)))
efectos["error"] = pieza((0, cuadrada(46, 0.16, 1.6, 0.5)), (0.17, cuadrada(41, 0.25, 1.6, 0.5)))
efectos["campanita"] = pieza((0, campana(2349, 0.7, 0.8)), (0.12, campana(2794, 0.8, 0.6)))
efectos["timbre"] = pieza((0, campana(988, 0.6, 1.0)), (0.35, campana(784, 0.9, 1.0)))
fanfarria = []
for k, (m, d) in enumerate([(72, 0.15), (76, 0.15), (79, 0.15), (84, 0.5)]):
    fanfarria.append((sum(x for _, x in [(0, 0)] + [(0, 0.15)] * k), cuadrada(m, d + 0.1, 1.5, 0.5)))
efectos["logro"] = pieza(*fanfarria)
for nombre, señal in efectos.items():
    guardar("fx_" + nombre, señal, calidad=4)
    print("efecto:", nombre)


# ---------------------------------------------------------
# AMBIENTES (bucles sin cortes)
# ---------------------------------------------------------
def bucle(señal, cruce=1.0):
    """Hace que el final empate con el principio."""
    c = int(SR * cruce)
    inicio, final = señal[:c], señal[-c:]
    rampa = np.linspace(0, 1, c)
    mezcla = final * (1 - rampa) + inicio * rampa
    return np.concatenate([mezcla, señal[c:-c]])


dur = 12.0
n = int(SR * dur)
t = np.arange(n) / SR
viento = filtro(rng_global.standard_normal(n), 500) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 6.0) ** 2)
viento += filtro(rng_global.standard_normal(n), 1800, "high") * 0.04 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 4.0))
guardar("amb_viento", bucle(viento, 1.5), calidad=1)

trafico = filtro(rng_global.standard_normal(n), 220) * 0.8
for inicio, largo in ((1.0, 3.5), (6.5, 4.0)):
    k = np.arange(int(SR * largo))
    paso = np.sin(np.pi * k / len(k)) ** 2
    motor = filtro(rng_global.standard_normal(len(k)), 700) * paso * 1.6
    mezclar(trafico, motor, inicio)
guardar("amb_carros", bucle(trafico, 1.5), calidad=1)

grillos = np.zeros(n)
for _ in range(60):
    inicio = rng_global.uniform(0, dur - 0.5)
    f = rng_global.uniform(4200, 5200)
    for k in range(int(rng_global.integers(2, 5))):
        tt = t_(0.045)
        chirp = np.sin(2 * np.pi * f * tt) * np.sin(np.pi * tt / 0.045) * rng_global.uniform(0.3, 1.0)
        mezclar(grillos, chirp, inicio + k * 0.07)
grillos += filtro(rng_global.standard_normal(n), 300) * 0.05
guardar("amb_grillos", bucle(grillos, 1.0), calidad=1)
print("ambientes listos")
