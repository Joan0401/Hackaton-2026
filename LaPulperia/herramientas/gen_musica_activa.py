"""Genera la música ACTIVA de la tienda (más rápida y con ritmo, para
animar a los niños mientras atienden).

Tres estilos, tres canciones cada uno:
  marimba alegre, cumbia de la tienda y 8 bits saltarín.
Las melodías se repiten (A A B A) para que se puedan tararear.
Uso: python gen_musica_activa.py <carpeta_destino>
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
RUIDO = np.random.default_rng(11)


def guardar(nombre, señal, calidad=3, ganancia=1.0):
    señal = np.asarray(señal, dtype=np.float64)
    señal = señal / (np.max(np.abs(señal)) or 1.0) * 0.85 * ganancia
    wav = os.path.join(DEST, nombre + ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((señal * 32767).astype(np.int16).tobytes())
    ogg = os.path.join(DEST, nombre + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis",
                    "-q:a", str(calidad), ogg], check=True)
    os.remove(wav)


def t_(dur):
    return np.arange(int(SR * dur)) / SR


def freq(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, ataque=0.004, caida=0.3, sostener=0.0, soltar=0.03):
    t = np.arange(n) / SR
    e = np.clip(t / max(ataque, 1e-4), 0, 1) * (sostener + (1 - sostener) * np.exp(-t / max(caida, 1e-4)))
    r = int(SR * soltar)
    if r and n > r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def filtro(s, corte, tipo="low"):
    b, a = butter(2, corte / (SR / 2), btype=tipo)
    return lfilter(b, a, s)


def mezclar(pista, sonido, inicio):
    i = int(inicio * SR)
    fin = min(len(pista), i + len(sonido))
    if 0 <= i < len(pista):
        pista[i:fin] += sonido[:fin - i]


# ---------------------------------------------------------
# INSTRUMENTOS
# ---------------------------------------------------------
def marimba(m, dur, vol=1.0):
    t = t_(dur)
    f = freq(m)
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.05)
         + 0.12 * np.sin(2 * np.pi * f * 10 * t) * np.exp(-t / 0.012))
    return s * env(len(t), 0.002, 0.28, 0.0, 0.02) * vol


def acordeon(m, dur, vol=1.0):
    """Diente de sierra con vibrato y dos voces un poco desafinadas."""
    t = t_(dur)
    f = freq(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t))
    fase1 = np.cumsum(f) / SR
    fase2 = np.cumsum(f * 1.004) / SR
    s = (2 * (fase1 % 1) - 1) + 0.7 * (2 * (fase2 % 1) - 1)
    s = filtro(s, 2600)
    return s * env(len(t), 0.02, dur, 0.85, 0.04) * vol * 0.35


def cuadrada(m, dur, vol=1.0, ancho=0.25):
    t = t_(dur)
    s = np.where((freq(m) * t) % 1.0 < ancho, 1.0, -1.0)
    return s * env(len(t), 0.002, dur * 0.7, 0.55, 0.015) * vol * 0.3


def triangular(m, dur, vol=1.0):
    t = t_(dur)
    s = 4 * np.abs((freq(m) * t) % 1.0 - 0.5) - 1
    return s * env(len(t), 0.003, dur, 0.7, 0.015) * vol * 0.7


def bajo(m, dur, vol=1.0):
    t = t_(dur)
    f = freq(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)
    return s * env(len(t), 0.004, 0.25, 0.3, 0.03) * vol * 0.8


def bombo(vol=1.0):
    t = t_(0.2)
    f = 120 * np.exp(-t / 0.035) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.08) * vol


def tarola(vol=1.0):
    n = int(SR * 0.14)
    ruido = filtro(RUIDO.standard_normal(n), 1800, "high") * np.exp(-np.arange(n) / SR / 0.05)
    tono = np.sin(2 * np.pi * 190 * np.arange(n) / SR) * np.exp(-np.arange(n) / SR / 0.03)
    return (0.6 * ruido + 0.4 * tono) * vol


def charles(vol=1.0):
    n = int(SR * 0.05)
    return filtro(RUIDO.standard_normal(n), 7000, "high") * np.exp(-np.arange(n) / SR / 0.012) * 0.45 * vol


def guiro(dur=0.12, vol=1.0):
    """Raspado: ruido que tiembla rápido."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = filtro(RUIDO.standard_normal(n), 3000, "high") * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 70 * t)))
    return s * env(n, 0.005, dur * 0.6, 0.0, 0.01) * 0.4 * vol


def cencerro(vol=1.0):
    t = t_(0.12)
    s = np.where((560 * t) % 1 < 0.5, 1, -1) + np.where((845 * t) % 1 < 0.5, 1, -1)
    return filtro(s, 3000) * np.exp(-t / 0.04) * 0.25 * vol


def ruido_8bits(dur, vol=1.0, corte=5000):
    n = int(SR * dur)
    return filtro(RUIDO.choice([-1.0, 1.0], n), corte, "high" if corte > 2000 else "low") \
        * np.exp(-np.arange(n) / SR / (dur / 3)) * vol * 0.35


# ---------------------------------------------------------
# COMPOSICIÓN
# ---------------------------------------------------------
ESCALA = [0, 2, 4, 5, 7, 9, 11]
RITMOS = [  # en pulsos (negras); suman 4
    [1, 1, 1, 1], [0.5, 0.5, 1, 1, 1], [1, 0.5, 0.5, 1, 1], [0.5, 0.5, 0.5, 0.5, 1, 1],
    [1.5, 0.5, 1, 1], [0.5, 0.5, 1, 0.5, 0.5, 1], [1, 1, 0.5, 0.5, 1], [0.5] * 8,
]


def acorde(grado, tonica):
    return [tonica + ESCALA[(grado + k) % 7] + 12 * ((grado + k) // 7) for k in (0, 2, 4)]


def melodia_frase(rng, progresion, tonica):
    """Una frase (un compás por acorde), con notas del acorde y pasos cortos."""
    grados = [tonica + e + 12 * o for o in range(3) for e in ESCALA]
    nota = acorde(progresion[0], tonica)[0] + 12
    frase = []
    for grado in progresion:
        notas = [n + 12 for n in acorde(grado, tonica)]
        compas = []
        for dur in RITMOS[int(rng.integers(0, len(RITMOS)))]:
            if rng.random() < 0.55:
                nota = int(rng.choice(notas))
            else:
                i = min(range(len(grados)), key=lambda k: abs(grados[k] - nota))
                nota = grados[max(0, min(len(grados) - 1, i + int(rng.choice([-1, 1, 1, 2, -2]))))]
            nota = max(tonica + 10, min(tonica + 26, nota))
            compas.append((nota, dur))
        frase.append(compas)
    # El último compás termina en la tónica.
    ult = frase[-1]
    ult[-1] = (tonica + 12, ult[-1][1])
    return frase


def componer(estilo, semilla, tonica, tempo, prog_a, prog_b):
    rng = np.random.default_rng(semilla)
    negra = 60.0 / tempo
    compas = 4 * negra
    a = melodia_frase(rng, prog_a, tonica)
    b = melodia_frase(rng, prog_b, tonica)
    forma = [(prog_a, a), (prog_a, a), (prog_b, b), (prog_a, a)] * 2   # A A B A, dos veces
    n_compases = sum(len(p) for p, _ in forma)
    pista = np.zeros(int(SR * (n_compases * compas + 2.0)))
    c = 0
    for prog, frase in forma:
        for grado, notas_mel in zip(prog, frase):
            inicio = c * compas
            notas = acorde(grado, tonica)
            raiz = notas[0] - 12
            quinta = notas[2] - 12
            if estilo == "marimba":
                for p in range(4):
                    mezclar(pista, bombo(0.7), inicio + p * negra)
                    mezclar(pista, charles(0.8), inicio + (p + 0.5) * negra)
                    mezclar(pista, bajo(raiz if p % 2 == 0 else quinta, negra * 0.9, 0.7), inicio + p * negra)
                    for n_ in notas:      # acorde en el contratiempo
                        mezclar(pista, marimba(n_, negra * 0.5, 0.18), inicio + (p + 0.5) * negra)
                t = inicio
                for nota, dur in notas_mel:   # melodía con trémolo de marimba
                    golpes = max(1, int(dur * 4))
                    for g in range(golpes):
                        mezclar(pista, marimba(nota + 12, negra / 4, 0.5 if g == 0 else 0.3),
                                t + g * negra / 4)
                    t += dur * negra
            elif estilo == "cumbia":
                for p in range(4):
                    if p in (0, 2):
                        mezclar(pista, bombo(0.6), inicio + p * negra)
                    if p in (1, 3):
                        mezclar(pista, tarola(0.35), inicio + p * negra)
                    # güiro: largo-corto-corto
                    mezclar(pista, guiro(negra * 0.5, 0.9), inicio + p * negra)
                    mezclar(pista, guiro(negra * 0.22, 0.6), inicio + (p + 0.5) * negra)
                    mezclar(pista, guiro(negra * 0.22, 0.6), inicio + (p + 0.75) * negra)
                    mezclar(pista, cencerro(0.6), inicio + (p + 0.5) * negra)
                    for n_ in notas:      # acordeón en el contratiempo
                        mezclar(pista, acordeon(n_ + 12, negra * 0.35, 0.2), inicio + (p + 0.5) * negra)
                # bajo de cumbia: raíz, quinta, raíz (con anticipación)
                mezclar(pista, bajo(raiz, negra * 1.4, 0.9), inicio)
                mezclar(pista, bajo(quinta, negra * 0.9, 0.8), inicio + 1.5 * negra)
                mezclar(pista, bajo(raiz, negra * 0.9, 0.8), inicio + 2 * negra)
                mezclar(pista, bajo(quinta, negra * 0.9, 0.8), inicio + 3.5 * negra)
                t = inicio
                for nota, dur in notas_mel:
                    mezclar(pista, acordeon(nota + 12, dur * negra * 0.95, 0.55), t)
                    t += dur * negra
            else:                           # 8 bits
                for p in range(4):
                    mezclar(pista, ruido_8bits(0.1, 0.9, 900) if p % 2 == 0
                            else ruido_8bits(0.12, 0.8, 2500), inicio + p * negra)
                    mezclar(pista, ruido_8bits(0.04, 0.4, 7000), inicio + (p + 0.5) * negra)
                for k in range(8):          # bajo saltarín en corcheas (octavas)
                    mezclar(pista, triangular(raiz + (12 if k % 2 else 0), negra * 0.45, 0.8),
                            inicio + k * negra / 2)
                for k in range(16):         # arpegio rapidito
                    mezclar(pista, cuadrada(notas[k % 3] + 12, negra / 4, 0.18, 0.125),
                            inicio + k * negra / 4)
                t = inicio
                for nota, dur in notas_mel:
                    mezclar(pista, cuadrada(nota + 12, dur * negra * 0.9, 0.6, 0.25), t)
                    t += dur * negra
            c += 1
    cola = int(SR * 1.5)
    pista[-cola:] *= np.linspace(1, 0, cola)
    return filtro(pista, 7000)


# nombre, estilo, semilla, tónica, tempo, progresión A, progresión B
MUSICA_ACTIVA = [
    ("marimba_alegre_1", "marimba", 401, 60, 126, [0, 3, 4, 0], [5, 3, 1, 4]),
    ("marimba_alegre_2", "marimba", 402, 65, 132, [0, 4, 5, 3], [3, 4, 0, 4]),
    ("marimba_alegre_3", "marimba", 403, 62, 120, [0, 0, 3, 4], [5, 1, 3, 4]),
    ("cumbia_1", "cumbia", 501, 57, 100, [0, 4, 4, 0], [3, 0, 4, 0]),
    ("cumbia_2", "cumbia", 502, 62, 104, [0, 3, 4, 0], [5, 3, 4, 4]),
    ("cumbia_3", "cumbia", 503, 55, 98, [0, 0, 4, 4], [3, 3, 0, 4]),
    ("saltarin_1", "8bits", 601, 60, 140, [0, 5, 3, 4], [3, 4, 0, 4]),
    ("saltarin_2", "8bits", 602, 64, 132, [0, 3, 0, 4], [5, 3, 1, 4]),
    ("saltarin_3", "8bits", 603, 57, 144, [0, 4, 5, 3], [0, 3, 4, 4]),
]

if __name__ == "__main__":
    for nombre, estilo, semilla, tonica, tempo, pa, pb in MUSICA_ACTIVA:
        # El 8 bits suena más fuerte: se baja un poco para que todas parejas.
        guardar(nombre, componer(estilo, semilla, tonica, tempo, pa, pb), calidad=2,
                ganancia=0.7 if estilo == "8bits" else 1.0)
        print("música:", nombre)
