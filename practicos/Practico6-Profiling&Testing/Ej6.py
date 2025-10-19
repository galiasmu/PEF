import pytest

def es_primo(n):
    """
    Determina si un número n es primo.
    
    Args:
        n (int): Número a verificar
        
    Returns:
        bool: True si n es primo, False en caso contrario
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Verificar divisores impares hasta la raíz cuadrada de n
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

# Test cases para pytest
class TestEsPrimo:
    """Test cases para la función es_primo usando pytest"""
    
    def test_numeros_primos(self):
        """Test con números primos conocidos"""
        primos = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        for primo in primos:
            assert es_primo(primo), f"{primo} debería ser primo"
    
    def test_numeros_no_primos(self):
        """Test con números no primos conocidos"""
        no_primos = [1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25]
        for no_primo in no_primos:
            assert not es_primo(no_primo), f"{no_primo} no debería ser primo"
    
    def test_numeros_negativos(self):
        """Test con números negativos"""
        assert not es_primo(-1)
        assert not es_primo(-5)
        assert not es_primo(-10)
    
    def test_cero_y_uno(self):
        """Test con 0 y 1"""
        assert not es_primo(0)
        assert not es_primo(1)
    
    def test_numeros_grandes(self):
        """Test con números primos grandes"""
        primos_grandes = [97, 101, 103, 107, 109, 113, 127, 131, 137, 139]
        for primo in primos_grandes:
            assert es_primo(primo), f"{primo} debería ser primo"
    
    @pytest.mark.parametrize("numero,esperado", [
        (2, True),
        (3, True),
        (4, False),
        (5, True),
        (6, False),
        (7, True),
        (8, False),
        (9, False),
        (10, False),
        (11, True),
        (12, False),
        (13, True),
        (14, False),
        (15, False),
        (16, False),
        (17, True),
        (18, False),
        (19, True),
        (20, False),
    ])
    def test_parametrizado(self, numero, esperado):
        """Test parametrizado para verificar múltiples casos"""
        assert es_primo(numero) == esperado

def main():
    # Ejecutar con pytest
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    main()