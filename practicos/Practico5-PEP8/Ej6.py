"""Módulo para manejo de información de personas."""

from dataclasses import dataclass


@dataclass
class Persona:
    """Representa una persona con nombre y edad."""
    nombre: str
    edad: int


class Empleado(Persona):
    """Representa un empleado."""
    pass


class Cliente(Persona):
    """Representa un cliente."""
    pass


class GestorPersonas:
    """Gestiona la visualización de información de personas."""

    @staticmethod
    def mostrar_persona(persona: Persona):
        """
        Muestra información de una persona.

        Args:
            persona (Persona): Instancia de Persona o subclase.
        """
        print(f"Nombre: {persona.nombre}")
        print(f"Edad: {persona.edad}")


if __name__ == "__main__":
    gestor = GestorPersonas()

    empleado = Empleado("Ana García", 30)
    cliente = Cliente("Carlos López", 45)

    print("--- Empleado ---")
    gestor.mostrar_persona(empleado)

    print("\n--- Cliente ---")
    gestor.mostrar_persona(cliente)