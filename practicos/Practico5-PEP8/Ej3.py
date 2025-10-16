#Codigo original
def area_rectangulo(a, b):
    return a * b

def area_cuadrado(l):
    return l * l

"""Módulo para cálculo de áreas con código refactorizado."""


def area_rectangulo(base, altura):
    """
    Calcula el área de un rectángulo.

    Args:
        base (float): Base del rectángulo.
        altura (float): Altura del rectángulo.

    Returns:
        float: Área del rectángulo.
    """
    return base * altura


def area_cuadrado(lado):
    """
    Calcula el área de un cuadrado usando area_rectangulo.

    Args:
        lado (float): Lado del cuadrado.

    Returns:
        float: Área del cuadrado.
    """
    # Un cuadrado es un caso especial de rectángulo
    return area_rectangulo(lado, lado)


if __name__ == "__main__":
    print(f"Área rectángulo (4x6): {area_rectangulo(4, 6)}")
    print(f"Área cuadrado (5x5): {area_cuadrado(5)}")