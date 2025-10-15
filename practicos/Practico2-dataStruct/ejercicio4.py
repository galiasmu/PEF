from collections import deque

# Cola de solicitudes
cola_solicitudes = deque(["Solicitud 1", "Solicitud 2", "Solicitud 3", "Solicitud 4"])

print("Cola inicial:", cola_solicitudes)

# Procesamos la primer solicitud
primera_solicitud = cola_solicitudes.popleft()
print(f"Procesando: {primera_solicitud}")

print("Cola después de procesar una solicitud:", cola_solicitudes)


