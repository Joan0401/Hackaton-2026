"""REPORTE para el profesor o el padre: aciertos, errores y calculadora.

Se cuentan las respuestas del niño en cada habilidad (las del MODO DE JUEGO
y la factura, que siempre está) y cuántas veces usó la calculadora. Se
guarda con la partida y se ve en el menú principal > REPORTE, donde también
se puede guardar como archivo CSV (se abre con Excel).

Qué cuenta como acierto / error en cada habilidad:
  factura:     cada subtotal y el total de la factura (ENTER).
  contar:      los subtotales cuando la factura solo tiene dibujos.
  vuelto:      el vuelto que se escribe.
  cierre:      la suma del cierre de caja.
  fracciones:  entregar bien (o mal) un pedido de medio, tercio o cuarto.
  multiplicar: entregar bien (o mal) un pedido del doble o el triple.
  sucesiones:  entregar bien (o mal) el pedido de un cliente frecuente.
  memoria:     entregar bien (o mal) un pedido que ya estaba escondido.
  descarte:    entregar bien (o mal) un pedido con adivinanza de colores.
  paciencia:   cliente atendido a tiempo (acierto) o que se fue (error).
"""
import csv

from modos import INFO, ORDEN, MODO

FACTURA = ("FACTURA (CANTIDAD X PRECIO Y TOTAL)", "Multiplicación y suma")

datos = {}
calculadora = {"pagada": 0, "gratis": 0}


def reiniciar():
    datos.clear()
    for clave in ["factura"] + list(INFO):
        datos[clave] = {"aciertos": 0, "errores": 0}
    calculadora["pagada"] = calculadora["gratis"] = 0


reiniciar()


def registrar(clave, acierto):
    if clave not in datos:
        datos[clave] = {"aciertos": 0, "errores": 0}
    datos[clave]["aciertos" if acierto else "errores"] += 1


def usar_calculadora(pagada):
    calculadora["pagada" if pagada else "gratis"] += 1


def a_dict():
    return {"datos": {k: dict(v) for k, v in datos.items()}, "calculadora": dict(calculadora)}


def desde_dict(d):
    reiniciar()
    for k, v in (d or {}).get("datos", {}).items():
        datos[k] = {"aciertos": int(v.get("aciertos", 0)), "errores": int(v.get("errores", 0))}
    for k, v in (d or {}).get("calculadora", {}).items():
        if k in calculadora:
            calculadora[k] = int(v)


def filas(d=None):
    """[(nombre, habilidad, aciertos, errores, % aciertos o None)]: la factura
    y las opciones del MODO DE JUEGO que están activadas.
    d: los datos de otra partida (como los da a_dict); None = la abierta."""
    datos_ = datos if d is None else (d or {}).get("datos", {})
    claves = ["factura"] + [k for k in ORDEN if MODO.get(k)]
    salida = []
    for k in claves:
        nombre, habilidad = FACTURA if k == "factura" else INFO[k][:2]
        a, e = datos_.get(k, {}).get("aciertos", 0), datos_.get(k, {}).get("errores", 0)
        pct = round(100 * a / (a + e)) if a + e else None
        salida.append((nombre, habilidad, a, e, pct))
    return salida


def calculadora_de(d=None):
    """Cuántas veces se compró la calculadora (en la partida abierta o en d)."""
    if d is None:
        return calculadora["pagada"]
    return int((d or {}).get("calculadora", {}).get("pagada", 0))


def exportar_csv(ruta, nombre, dia, nivel, d=None, modo=None):
    """Guarda la tabla en un archivo CSV (separado por ; para Excel en español)."""
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Reporte de La Pulpería"])
        w.writerow(["Jugador", nombre])
        if modo:
            w.writerow(["Modo", modo])
        w.writerow(["Día", dia])
        w.writerow(["Nivel", nivel])
        w.writerow([])
        w.writerow(["Opción del juego", "Habilidad", "Aciertos", "Errores", "% de aciertos"])
        for n, h, a, e, pct in filas(d):
            w.writerow([n, h, a, e, "" if pct is None else pct])
        w.writerow([])
        w.writerow(["Calculadora comprada (veces)", calculadora_de(d)])
    return ruta
