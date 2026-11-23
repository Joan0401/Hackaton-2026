"""Genera la música TRANQUILA de la tienda (la que suena mientras se juega).

Tres estilos relajantes, cada uno con tres canciones distintas (otra
tonalidad, otro tempo, otro acompañamiento):
  guitarra suave, marimba suave y cajita de música.
Uso: python gen_musica_tienda.py <carpeta_destino>
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




# ---------------------------------------------------------
# INSTRUMENTOS SUAVES
# ---------------------------------------------------------
def guitarra(m, dur, vol=1.0):
    """Cuerda pulsada (Karplus-Strong)."""
    n = int(SR * dur)
    periodo = max(2, int(SR / freq(m)))
    rng = np.random.default_rng(m)
    buf = rng.uniform(-1, 1, periodo)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % periodo]
        buf[i % periodo] = 0.996 * 0.5 * (buf[i % periodo] + buf[(i + 1) % periodo])
    out = filtro(out, 3000)
    return out * env(n, 0.003, 1.2, 0.0, 0.08) * vol * 0.8


def marimba_suave(m, dur, vol=1.0):
    t = t_(dur)
    f = freq(m)
    s = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.04)
    return filtro(s * env(len(t), 0.004, 0.5, 0.0, 0.05), 2500) * vol


def cajita(m, dur, vol=1.0):
    """Campanita de cajita de música."""
    t = t_(max(dur, 1.4))
    f = freq(m)
    s = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.3)
         + 0.15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.1))
    return s * env(len(t), 0.002, 0.8, 0.0, 0.1) * vol * 0.6


INSTRUMENTOS = {"guitarra": guitarra, "marimba_suave": marimba_suave, "cajita": cajita}


def cancion_suave(instr, semilla, tonica, tempo, progresion, patron, pulsos=4, repeticiones=3):
    tocar = INSTRUMENTOS[instr]
    rng = np.random.default_rng(semilla)
    negra = 60.0 / tempo
    compas = pulsos * negra
    total = len(progresion) * repeticiones
    pista = np.zeros(int(SR * (total * compas + 2.5)))
    octava = 24 if instr == "cajita" else 12
    # Melodía lenta: notas largas, se repite para que se pueda tararear.
    ritmos = ([[2, 1], [3], [1, 2], [1, 1, 1]] if pulsos == 3
              else [[2, 2], [4], [3, 1], [2, 1, 1], [1, 1, 2]])
    melodia = []
    nota = tonica + 12 + ESCALA_MAYOR[int(rng.integers(0, 3)) * 2]
    grados = [tonica + 12 + e + 12 * o for o in range(3) for e in ESCALA_MAYOR]
    for grado in progresion:
        notas_acorde = acorde(grado, tonica + 12)
        compas_notas = []
        for duracion in ritmos[int(rng.integers(0, len(ritmos)))]:
            if rng.random() < 0.6:
                nota = int(rng.choice(notas_acorde) + 12 * rng.integers(0, 2))
            else:
                idx = min(range(len(grados)), key=lambda k: abs(grados[k] - nota))
                nota = grados[max(0, min(len(grados) - 1, idx + int(rng.choice([-1, 1, 2, -2]))))]
            nota = max(tonica + 12, min(tonica + 28, nota))
            compas_notas.append((nota, duracion))
        melodia.append(compas_notas)

    for r in range(repeticiones):
        for i, grado in enumerate(progresion):
            inicio = (r * len(progresion) + i) * compas
            notas_acorde = acorde(grado, tonica)
            bajo = notas_acorde[0] - 12
            mezclar(pista, pad(bajo, compas, 0.5), inicio)
            mezclar(pista, pad(notas_acorde[1], compas, 0.25), inicio)
            if patron == "arpegio":           # sube y baja en corcheas
                orden = notas_acorde + [notas_acorde[0] + 12] + notas_acorde[::-1]
                for k in range(pulsos * 2):
                    mezclar(pista, tocar(orden[k % len(orden)], negra, 0.35), inicio + k * negra / 2)
            elif patron == "vals":            # bajo y dos acordes (3/4)
                mezclar(pista, tocar(bajo, negra * 1.5, 0.5), inicio)
                for p in range(1, pulsos):
                    for n_ in notas_acorde[1:]:
                        mezclar(pista, tocar(n_, negra, 0.22), inicio + p * negra)
            elif patron == "bajo_arpegio":     # bajo y arpegio que baja
                mezclar(pista, tocar(bajo, compas * 0.8, 0.5), inicio)
                for k, n_ in enumerate(([notas_acorde[0] + 12] + notas_acorde[::-1])[:pulsos]):
                    mezclar(pista, tocar(n_, negra * 1.2, 0.28), inicio + k * negra)
            else:                             # "acordes": acorde suave en el 1 y el 3
                for p in range(0, pulsos, 2):
                    for n_ in notas_acorde:
                        mezclar(pista, tocar(n_, negra * 2, 0.2), inicio + p * negra)
            t_nota = inicio
            for nota, duracion in melodia[i]:
                mezclar(pista, tocar(nota + octava, duracion * negra * 1.3, 0.75), t_nota)
                t_nota += duracion * negra
    cola = int(SR * 2.0)
    pista[-cola:] *= np.linspace(1, 0, cola)
    return filtro(pista, 5000)


MUSICA_TIENDA = [
    # nombre, instrumento, semilla, tónica, tempo, progresión, patrón, pulsos
    ("guitarra_1", "guitarra", 101, 55, 72, [0, 5, 3, 4, 0, 5, 1, 4], "arpegio", 4),
    ("guitarra_2", "guitarra", 102, 62, 84, [0, 3, 0, 4, 5, 3, 4, 0], "vals", 3),
    ("guitarra_3", "guitarra", 103, 57, 66, [0, 2, 3, 4, 0, 2, 3, 0], "bajo_arpegio", 4),
    ("marimba_suave_1", "marimba_suave", 201, 60, 76, [0, 4, 5, 3, 0, 4, 3, 4], "acordes", 4),
    ("marimba_suave_2", "marimba_suave", 202, 65, 88, [0, 3, 4, 0, 5, 1, 4, 0], "vals", 3),
    ("marimba_suave_3", "marimba_suave", 203, 58, 70, [0, 5, 1, 4, 0, 5, 3, 4], "arpegio", 4),
    ("cajita_1", "cajita", 301, 60, 68, [0, 3, 4, 0, 0, 3, 4, 0], "vals", 3),
    ("cajita_2", "cajita", 302, 67, 74, [0, 5, 3, 4, 0, 5, 3, 0], "bajo_arpegio", 4),
    ("cajita_3", "cajita", 303, 63, 64, [0, 4, 5, 3, 1, 4, 0, 0], "arpegio", 4),
]

for nombre, instr, semilla, tonica, tempo, prog, patron, pulsos in MUSICA_TIENDA:
    guardar(nombre, cancion_suave(instr, semilla, tonica, tempo, prog, patron, pulsos), calidad=2)
    print("música:", nombre)
