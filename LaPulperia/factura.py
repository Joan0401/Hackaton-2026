"""Lógica de la factura educativa de La Pulpería (sin dependencias gráficas).

Los resultados esperados se guardan internamente y no se muestran al jugador.
El cobro solo se autoriza después de validar subtotales y total.
"""


class FacturaInteractiva:
    MAX_DIGITOS = 9

    def __init__(self, resumen, pago=None):
        # Tomamos una copia de las filas para que el ejercicio sea consistente.
        self.filas = [
            {
                "label": str(grupo["label"]),
                "quantity": int(grupo["quantity"]),
                "unit_price": int(grupo["unit_price"]),
                # Tipo de producto, para dibujarlo en la factura.
                "kind": grupo.get("kind"),
            }
            for grupo in resumen["groups"]
        ]
        # Después de los subtotales va el total y, si el cliente paga con
        # billetes, un campo más para el vuelto.
        self.pago = pago
        campos = len(self.filas) + 1 + (1 if pago is not None else 0)
        self.valores = [""] * campos
        self.correctos = [False] * len(self.valores)
        self.actual = 0
        self.mensaje = (
            "Completa cada subtotal, el total y el vuelto."
            if pago is not None else
            "Completa cada subtotal y después el total."
        )
        self.error = False

    @property
    def indice_total(self):
        return len(self.filas)

    @property
    def indice_vuelto(self):
        """Campo del vuelto, o None si el cliente paga exacto."""
        return len(self.filas) + 1 if self.pago is not None else None

    @property
    def total(self):
        return sum(fila["quantity"] * fila["unit_price"] for fila in self.filas)

    @property
    def listo(self):
        return bool(self.filas) and all(self.correctos)

    @property
    def en_boton_cobrar(self):
        return self.actual == len(self.valores)

    def puede_editar(self, indice):
        return 0 <= indice < len(self.valores) and all(self.correctos[:indice])

    def seleccionar(self, indice):
        if self.puede_editar(indice):
            self.actual = indice
            self.mensaje = "Escribe el resultado y pulsa ENTER."
            self.error = False
            return True
        return False

    def ingresar(self, digito):
        if len(digito) != 1 or digito not in "0123456789":
            return False
        if not self.puede_editar(self.actual):
            return False
        indice = self.actual
        if len(self.valores[indice]) >= self.MAX_DIGITOS:
            return False
        # Al cambiar una respuesta validada, se invalidan también las posteriores.
        if self.correctos[indice]:
            self.correctos[indice:] = [False] * (len(self.correctos) - indice)
        self.valores[indice] += digito
        self.mensaje = "Pulsa ENTER para revisar tu respuesta."
        self.error = False
        return True

    def borrar(self):
        if not self.puede_editar(self.actual):
            return False
        indice = self.actual
        if self.correctos[indice]:
            self.correctos[indice:] = [False] * (len(self.correctos) - indice)
        self.valores[indice] = self.valores[indice][:-1]
        self.error = False
        self.mensaje = "Escribe el resultado y pulsa ENTER."
        return True

    def _esperado(self, indice):
        if indice == self.indice_vuelto:
            return self.pago - self.total
        if indice == self.indice_total:
            return sum(
                fila["quantity"] * fila["unit_price"]
                for fila in self.filas
            )
        fila = self.filas[indice]
        return fila["quantity"] * fila["unit_price"]

    def verificar(self):
        """Valida un campo. Devuelve True solo cuando la respuesta es correcta."""
        if not self.puede_editar(self.actual):
            return False
        indice = self.actual
        valor = self.valores[indice]
        if not valor:
            self.error = True
            self.mensaje = "Primero escribe un número."
            return False

        if int(valor) != self._esperado(indice):
            self.error = True
            if indice == self.indice_vuelto:
                self.mensaje = "Revisa: lo que pagó menos el total."
            elif indice == self.indice_total:
                self.mensaje = "Revisa la suma de tus subtotales."
            else:
                self.mensaje = "Revisa: cantidad por precio. Inténtalo otra vez."
            return False

        self.correctos[indice] = True
        self.error = False
        self.actual += 1
        if self.listo:
            self.mensaje = "¡Todo correcto! Selecciona COBRAR con ENTER."
        elif self.actual == self.indice_vuelto:
            self.mensaje = "¡Bien! Ahora calcula el vuelto."
        else:
            self.mensaje = "¡Bien! Ahora completa el siguiente resultado."
        return True
