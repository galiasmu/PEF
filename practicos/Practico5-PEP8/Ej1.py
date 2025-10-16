"""Módulo para cálculo de áreas geométricas."""


def area(r):
    """
    Calcula el área de un círculo dado su radio.

    Args:
        r (float): Radio del círculo.

    Returns:
        float: Área del círculo.

    Example:
        >>> area(5)
        78.5
    """
    # Usar pi aproximado (3.14) para calcular el área
    return 3.14 * r * r


if __name__ == "__main__":
    radio = 5
    resultado = area(radio)
    print(f"El área del círculo con radio {radio} es: {resultado}")