"""Calculadora para niños que acompaña a la factura de La Pulpería.

Se usa con el mouse (clic en los botones) o con el teclado cuando está
activa (ESPACIO cambia entre la factura y la calculadora).
Todas las coordenadas están en píxeles lógicos 640 x 360.
"""
import pygame

# Panel a la derecha de la pantalla. La factura se corre a la izquierda
# DESPLAZAMIENTO píxeles mientras la calculadora está visible.
PANEL = pygame.Rect(494, 14, 142, 332)
DESPLAZAMIENTO = 74

# Colores (misma paleta del juego).
DARK = (84, 50, 39)
WOOD = (123, 78, 57)
CREAM = (245, 226, 177)
CREAM_DARK = (219, 196, 141)
BLUE = (76, 103, 119)
BLUE_DARK = (48, 67, 78)
YELLOW = (239, 210, 139)
YELLOW_DARK = (167, 109, 74)
RED = (184, 84, 72)
RED_DARK = (120, 52, 46)
LCD = (178, 199, 150)
LCD_DARK = (62, 82, 58)
FOCUS = (90, 160, 95)

MULT = "×"
DIV = "÷"
BORRAR = "<"


def _formato(valor):
    """1900 -> 1.900 ; 12.5 -> 12,5 (formato de Centroamérica)."""
    if valor is None:
        return ""
    if abs(valor - round(valor)) < 1e-9:
        return f"{int(round(valor)):,}".replace(",", ".")
    texto = f"{valor:,.2f}".rstrip("0").rstrip(".")
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


class Calculadora:
    MAX_DIGITOS = 9

    def __init__(self):
        self.botones = self._crear_botones()
        self.limpiar()

    # -----------------------------------------------------
    # LÓGICA
    # -----------------------------------------------------
    def limpiar(self):
        self.actual = ""          # número que se está escribiendo
        self.acumulado = None     # resultado parcial
        self.operador = None
        self.linea = ""           # operación mostrada arriba
        self.es_resultado = False
        self.presionado = None
        self.presionado_ms = 0

    @staticmethod
    def _aplicar(a, op, b):
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == MULT:
            return a * b
        if op == DIV:
            return None if b == 0 else a / b
        return b

    def digito(self, d):
        if self.es_resultado:
            self.limpiar()
        if len(self.actual) >= self.MAX_DIGITOS:
            return
        self.actual = d if self.actual == "0" else self.actual + d

    def borrar(self):
        if self.es_resultado:
            self.limpiar()
        else:
            self.actual = self.actual[:-1]

    def poner_operador(self, op):
        if self.actual == "" and self.acumulado is None:
            return
        if self.actual != "":
            valor = int(self.actual)
            if self.acumulado is None or self.operador is None:
                self.acumulado = valor
            else:
                resultado = self._aplicar(self.acumulado, self.operador, valor)
                if resultado is None:
                    self._error()
                    return
                self.acumulado = resultado
            self.actual = ""
        self.operador = op
        self.es_resultado = False
        self.linea = f"{_formato(self.acumulado)} {op}"

    def igual(self):
        if self.operador is None or self.actual == "":
            return
        a, b = self.acumulado, int(self.actual)
        resultado = self._aplicar(a, self.operador, b)
        if resultado is None:
            self._error()
            return
        self.linea = f"{_formato(a)} {self.operador} {_formato(b)} ="
        self.acumulado = resultado
        self.operador = None
        self.actual = ""
        self.es_resultado = True

    def _error(self):
        self.limpiar()
        self.linea = "¡No se divide entre 0!"

    def pantalla(self):
        if self.actual:
            return _formato(int(self.actual))
        if self.acumulado is not None:
            return _formato(self.acumulado)
        return "0"

    def presionar(self, etiqueta):
        """Ejecuta un botón por su etiqueta."""
        self.presionado = etiqueta
        self.presionado_ms = pygame.time.get_ticks()
        if etiqueta.isdigit():
            self.digito(etiqueta)
        elif etiqueta in ("+", "-", MULT, DIV):
            self.poner_operador(etiqueta)
        elif etiqueta == "=":
            self.igual()
        elif etiqueta == "C":
            self.limpiar()
        elif etiqueta == BORRAR:
            self.borrar()

    def tecla(self, event):
        """Traduce una tecla a un botón. Devuelve True si la usó."""
        u = event.unicode
        if u and u in "0123456789":
            self.presionar(u)
        elif u == "+":
            self.presionar("+")
        elif u == "-":
            self.presionar("-")
        elif u in ("*", "x", "X"):
            self.presionar(MULT)
        elif u == "/":
            self.presionar(DIV)
        elif u == "=" or event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.presionar("=")
        elif event.key == pygame.K_BACKSPACE:
            self.presionar(BORRAR)
        elif u in ("c", "C") or event.key == pygame.K_DELETE:
            self.presionar("C")
        else:
            return False
        return True

    # -----------------------------------------------------
    # BOTONES Y DIBUJO
    # -----------------------------------------------------
    def _crear_botones(self):
        x0, y0, w, h, gap = PANEL.x + 8, PANEL.y + 96, 28, 30, 4
        filas = [
            ["C", BORRAR, DIV, MULT],
            ["7", "8", "9", "-"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "="],
        ]
        botones = []
        for r, fila in enumerate(filas):
            for c, etiqueta in enumerate(fila):
                alto = h * 2 + gap if etiqueta == "=" else h
                botones.append((etiqueta, pygame.Rect(
                    x0 + c * (w + gap), y0 + r * (h + gap), w, alto)))
        # El 0 es ancho, como en las calculadoras de verdad.
        botones.append(("0", pygame.Rect(
            x0, y0 + 4 * (h + gap), w * 3 + gap * 2, h)))
        return botones

    def boton_en(self, punto):
        for etiqueta, rect in self.botones:
            if rect.collidepoint(punto):
                return etiqueta
        return None

    def dibujar(self, surface, font_small, font_medium, font_large, activa):
        panel = PANEL
        pygame.draw.rect(surface, (35, 27, 27), panel.move(4, 4))
        pygame.draw.rect(surface, CREAM_DARK, panel)
        pygame.draw.rect(surface, FOCUS if activa else DARK, panel, 4)

        # Título
        pygame.draw.rect(surface, WOOD, (panel.x + 4, panel.y + 4, panel.w - 8, 28))
        titulo = font_medium.render("CALCULADORA", False, CREAM)
        surface.blit(titulo, titulo.get_rect(center=(panel.centerx, panel.y + 18)))

        # Pantalla
        lcd = pygame.Rect(panel.x + 8, panel.y + 40, panel.w - 16, 48)
        pygame.draw.rect(surface, LCD_DARK, lcd)
        pygame.draw.rect(surface, LCD, lcd.inflate(-4, -4))
        linea = font_small.render(self.linea, False, LCD_DARK)
        if linea.get_width() > lcd.w - 10:
            linea = pygame.transform.scale(
                linea, (lcd.w - 10, linea.get_height()))
        surface.blit(linea, linea.get_rect(topright=(lcd.right - 6, lcd.y + 5)))
        numero = font_large.render(self.pantalla(), False, LCD_DARK)
        if numero.get_width() > lcd.w - 10:
            numero = font_medium.render(self.pantalla(), False, LCD_DARK)
        surface.blit(numero, numero.get_rect(bottomright=(lcd.right - 6, lcd.bottom - 4)))

        # Botones
        recien = pygame.time.get_ticks() - self.presionado_ms < 120
        for etiqueta, rect in self.botones:
            if etiqueta.isdigit():
                fill, borde, texto = CREAM, DARK, DARK
            elif etiqueta == "=":
                fill, borde, texto = YELLOW, YELLOW_DARK, DARK
            elif etiqueta == "C":
                fill, borde, texto = RED, RED_DARK, CREAM
            else:
                fill, borde, texto = BLUE, BLUE_DARK, CREAM
            hundido = recien and etiqueta == self.presionado
            r = rect.move(0, 2) if hundido else rect
            if not hundido:
                pygame.draw.rect(surface, borde, rect.move(0, 2))
            pygame.draw.rect(surface, fill, r)
            pygame.draw.rect(surface, borde, r, 2)
            if etiqueta == BORRAR:
                # Flecha de borrar dibujada a mano.
                cx, cy = r.center
                pygame.draw.polygon(surface, texto, [
                    (cx - 7, cy), (cx - 2, cy - 5), (cx + 7, cy - 5),
                    (cx + 7, cy + 5), (cx - 2, cy + 5)])
                pygame.draw.line(surface, fill, (cx, cy - 2), (cx + 4, cy + 2), 2)
                pygame.draw.line(surface, fill, (cx + 4, cy - 2), (cx, cy + 2), 2)
            else:
                t = font_large.render(etiqueta, False, texto)
                surface.blit(t, t.get_rect(center=r.center))

        # Ayuda
        ayuda_y = panel.y + 286
        lineas = (
            ("ESTAS USANDO", "LA CALCULADORA", "ESPACIO: VOLVER")
            if activa else
            ("HAZ CLIC AQUI", "O PULSA ESPACIO", "PARA USARLA")
        )
        for i, texto in enumerate(lineas):
            t = font_small.render(texto, False, FOCUS if activa and i < 2 else BLUE_DARK)
            surface.blit(t, t.get_rect(center=(panel.centerx, ayuda_y + i * 16)))
