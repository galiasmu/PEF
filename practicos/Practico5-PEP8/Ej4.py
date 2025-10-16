"""Módulo para generación de reportes de usuarios."""

from dataclasses import dataclass


@dataclass
class DatosReporte:
    """Encapsula los datos del reporte."""
    usuario: str
    ventas: int
    gastos: int
    ganancias: int


class Reporte:
    """Genera reportes financieros de usuarios."""

    def generar_reporte(self, datos: DatosReporte):
        """
        Genera un reporte financiero.

        Args:
            datos (DatosReporte): Datos del reporte.
        """
        self._imprimir_datos(datos)
        self._imprimir_balance(datos)

    def _imprimir_datos(self, datos: DatosReporte):
        """Imprime los datos básicos del reporte."""
        print(f"Usuario: {datos.usuario}")
        print(f"Ventas: {datos.ventas}")
        print(f"Gastos: {datos.gastos}")
        print(f"Ganancias: {datos.ganancias}")

    def _imprimir_balance(self, datos: DatosReporte):
        """Calcula e imprime el balance."""
        balance = datos.ventas - datos.gastos
        estado = "positivo" if balance > 0 else "negativo"
        print(f"Balance {estado}")


if __name__ == "__main__":
    reporte = Reporte()
    datos = DatosReporte("Juan Pérez", 10000, 7000, 3000)
    reporte.generar_reporte(datos)