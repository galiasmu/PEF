class Inventario:
    def __init__(self):
        self.productos_ordenados = []  # Lista para mantener el orden
        self.productos_por_codigo = {} # Diccionario para búsqueda rápida

    def agregar_producto(self, codigo, nombre):
        producto = {'codigo': codigo, 'nombre': nombre}
        self.productos_ordenados.append(producto)
        self.productos_por_codigo[codigo] = producto

    def buscar_por_codigo(self, codigo):
        return self.productos_por_codigo.get(codigo, "Producto no encontrado")

# Uso
inventario = Inventario()
inventario.agregar_producto("P001", "Laptop")
inventario.agregar_producto("P002", "Mouse")
inventario.agregar_producto("P003", "Teclado")

print("Productos en orden de llegada:", inventario.productos_ordenados)
print("Buscando producto P002:", inventario.buscar_por_codigo("P002"))


