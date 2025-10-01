from collections import deque
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, List, Dict

# 1)
def build_membership_index(nums: Iterable[int]) -> set[int]:
    """
    Crea un índice de pertenencia O(1) promedio.
    """
    return set(nums)

def is_in_collection(index: set[int], x: int) -> bool:
    return x in index


# 2)
@dataclass
class User:
    id: int
    name: str

class UserStoreByPosition:
    """
    Guarda 1M de usuarios en una lista para acceso O(1) por posición (0-based).
    Si "usuario n° 500,000" es 1-based, convertir a índice 499_999.
    """
    def __init__(self, users: List[User]):
        self.users = users

    def get_by_position_1_based(self, n: int) -> User:
        return self.users[n - 1]  # O(1)

    def get_by_position_0_based(self, i: int) -> User:
        return self.users[i]      # O(1)


# 3)
@dataclass(frozen=True)
class Product:
    code: str
    name: str
    price: float

class ProductStore:
    """
    - Inserción mantiene orden de llegada (dict es ordenado por inserción).
    - Búsqueda por code en O(1) promedio.
    """
    def __init__(self):
        self._by_code: Dict[str, Product] = {}

    def add(self, p: Product) -> None:
        if p.code in self._by_code:
            raise ValueError(f"Código duplicado: {p.code}")
        self._by_code[p.code] = p  # mantiene el orden de llegada

    def get(self, code: str) -> Product | None:
        return self._by_code.get(code)

    def __iter__(self) -> Iterator[Product]:
        # iterar en orden de llegada
        return iter(self._by_code.values())

    def __len__(self) -> int:
        return len(self._by_code)


# 4)
class RequestQueue:
    def __init__(self):
        self._q: deque[Any] = deque()

    def push(self, req: Any) -> None:
        self._q.append(req)    # O(1)

    def pop(self) -> Any:
        if not self._q:
            raise IndexError("Queue vacía")
        return self._q.popleft()  # O(1)

    def __len__(self) -> int:
        return len(self._q)


# 5)
def dedupe_preserving_order(seq: Iterable[Any]) -> List[Any]:
    """
    O(n) en tiempo, O(n) en memoria. Mantiene el primer encuentro de cada elemento.
    """
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def dedupe_preserving_order_one_liner(seq: Iterable[Any]) -> List[Any]:
    """
    Alternativa compacta aprovechando que dict preserva orden.
    """
    return list(dict.fromkeys(seq))



if __name__ == "__main__":
    # 1) Pertenencia
    numeros = range(1_000_000)  # ej. 0..999_999
    idx = build_membership_index(numeros)
    assert is_in_collection(idx, 123456) is True
    assert is_in_collection(idx, 1_000_001) is False

    # 2) Acceso por posición
    usuarios = [User(id=i, name=f"user_{i}") for i in range(1, 1_000_001)]
    store = UserStoreByPosition(usuarios)
    u500k = store.get_by_position_1_based(500_000)  # O(1)
    assert u500k.id == 500_000

    # 3) Productos en orden + lookup O(1)
    ps = ProductStore()
    ps.add(Product(code="A01", name="Mouse", price=10.0))
    ps.add(Product(code="B02", name="Teclado", price=20.0))
    ps.add(Product(code="C03", name="Monitor", price=150.0))
    assert ps.get("B02").name == "Teclado"
    llegada = [p.code for p in ps]  # ["A01","B02","C03"]

    # 4) Cola FIFO O(1)
    rq = RequestQueue()
    rq.push("req1")
    rq.push("req2")
    first = rq.pop()  # "req1"
    second = rq.pop() # "req2"

    # 5) Dedupe manteniendo orden
    eventos = ["login", "click", "login", "scroll", "click", "buy"]
    sin_dupes = dedupe_preserving_order(eventos)  # ["login","click","scroll","buy"]
    assert sin_dupes == ["login","click","scroll","buy"]



# -------- 1) Buscar en colección con set --------
nums = range(1_000_000)
idx = set(nums)  # índice de pertenencia
print("1) ¿123456 está en la colección?", 123456 in idx)  # True
print("1) ¿1_500_000 está en la colección?", 1_500_000 in idx)  # False


# -------- 2) Acceso directo por posición (list) --------
usuarios = [f"user_{i}" for i in range(1, 1_000_001)]
print("\n2) Usuario n° 500,000:", usuarios[499_999])  # acceso O(1)


# -------- 3) Productos en orden + búsqueda O(1) --------
productos = {}
# Insertamos en orden
productos["A01"] = {"nombre": "Mouse", "precio": 10.0}
productos["B02"] = {"nombre": "Teclado", "precio": 20.0}
productos["C03"] = {"nombre": "Monitor", "precio": 150.0}

# Búsqueda O(1)
print("\n3) Buscar producto con código 'B02':", productos["B02"])

# Iterar mantiene orden de llegada
print("3) Productos en orden de llegada:", list(productos.keys()))


# -------- 4) Cola FIFO con deque --------
from collections import deque

cola = deque()
cola.append("req1")
cola.append("req2")
cola.append("req3")

print("\n4) Primer request procesado:", cola.popleft())  # req1
print("4) Segundo request procesado:", cola.popleft())  # req2
print("4) Lo que queda en cola:", list(cola))


# -------- 5) Eliminar duplicados manteniendo orden --------
eventos = ["login", "click", "login", "scroll", "click", "buy"]
# Versión con set + lista
seen = set()
orden_sin_dupes = []
for e in eventos:
    if e not in seen:
        seen.add(e)
        orden_sin_dupes.append(e)

print("\n5) Original:", eventos)
print("5) Sin duplicados (mismo orden):", orden_sin_dupes)

# Alternativa más compacta con dict.fromkeys
print("5) One-liner:", list(dict.fromkeys(eventos)))
