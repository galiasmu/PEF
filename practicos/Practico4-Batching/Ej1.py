import random
import time
from datetime import datetime

def generar_archivo_grande(nombre_archivo, num_lineas=10000):
    """
    Genera un archivo de texto grande con datos de ejemplo.
    
    Args:
        nombre_archivo (str): Nombre del archivo a crear
        num_lineas (int): Número de líneas a generar
    """
    print(f"Generando archivo '{nombre_archivo}' con {num_lineas:,} líneas...")
    
    # Datos de ejemplo para generar registros realistas
    nombres = ["Juan", "María", "Carlos", "Ana", "Luis", "Carmen", "Pedro", "Laura"]
    apellidos = ["García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez", "Ramírez"]
    ciudades = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza", "Málaga", "Murcia", "Palma"]
    productos = ["Laptop", "Smartphone", "Tablet", "Monitor", "Teclado", "Mouse", "Auriculares", "Cámara"]
    
    start_time = time.time()
    
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        for i in range(1, num_lineas + 1):
            # Generar registro de ejemplo
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            ciudad = random.choice(ciudades)
            producto = random.choice(productos)
            precio = round(random.uniform(10.0, 1000.0), 2)
            fecha = f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            
            # Formato del registro
            registro = f"ID:{i:06d}|{nombre} {apellido}|{ciudad}|{producto}|${precio}|{fecha}"
            archivo.write(registro + '\n')
            
            # Mostrar progreso cada 1000 líneas
            if i % 1000 == 0:
                elapsed = time.time() - start_time
                print(f"  Progreso: {i:,} líneas generadas ({elapsed:.1f}s)")
    
    elapsed_total = time.time() - start_time
    print(f"✅ Archivo '{nombre_archivo}' generado exitosamente!")
    print(f"   - Líneas: {num_lineas:,}")
    print(f"   - Tiempo: {elapsed_total:.2f} segundos")
    print(f"   - Tamaño: {num_lineas * 50 / 1024:.1f} KB (estimado)")

def leer_por_lotes(archivo_path, batch_size=100):
    """
    Lee un archivo de texto en lotes de tamaño especificado
    y procesa cada lote imprimiendo cuántas líneas contiene.
    """
    try:
        print(f"Leyendo archivo '{archivo_path}' en lotes de {batch_size} líneas...")
        print("-" * 50)
        
        start_time = time.time()
        total_lineas = 0
        
        with open(archivo_path, 'r', encoding='utf-8') as archivo:
            lote_numero = 1
            lote_actual = []
            
            for linea in archivo:
                lote_actual.append(linea.strip())
                total_lineas += 1
                
                # Cuando el lote alcanza el tamaño deseado, lo procesamos
                if len(lote_actual) == batch_size:
                    print(f"Lote {lote_numero}: {len(lote_actual)} líneas")
                    lote_actual = []  # Reiniciamos el lote
                    lote_numero += 1
            
            # Procesamos el último lote si no está vacío
            if lote_actual:
                print(f"Lote {lote_numero}: {len(lote_actual)} líneas")
        
        elapsed = time.time() - start_time
        print("-" * 50)
        print(f"✅ Lectura completada!")
        print(f"   - Total de líneas: {total_lineas:,}")
        print(f"   - Total de lotes: {lote_numero}")
        print(f"   - Tiempo de lectura: {elapsed:.2f} segundos")
        print(f"   - Velocidad: {total_lineas/elapsed:.0f} líneas/segundo")
                
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo '{archivo_path}'")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")

def main():
    """Función principal que demuestra el ejercicio 1 completo."""
    print("=" * 60)
    print("EJERCICIO 1: Lectura eficiente de archivos en lotes")
    print("=" * 60)
    
    # Configuración
    nombre_archivo = "archivo_grande.txt"
    num_lineas = 50000  # 50,000 líneas para un archivo considerable
    batch_size = 1000
    
    # Paso 1: Generar archivo grande
    print("\nPASO 1: Generando archivo de prueba...")
    generar_archivo_grande(nombre_archivo, num_lineas)
    
    # Paso 2: Leer archivo en lotes
    print(f"\nPASO 2: Leyendo archivo en lotes de {batch_size}...")
    leer_por_lotes(nombre_archivo, batch_size)

if __name__ == "__main__":
    main()