"""Módulo para cálculos geométricos de círculos."""

import math


class Circulo:
    """Clase para realizar cálculos sobre círculos."""

    def area(self, radio):
        """
        Calcula el área de un círculo.

        Args:
            radio (float): Radio del círculo.

        Returns:
            float: Área del círculo.
        """
        # Usar constante PI de math para mayor precisión
        return math.pi * radio * radio


if __name__ == "__main__":
    circulo = Circulo()
    print(f"Área del círculo (radio=5): {circulo.area(5):.2f}")