# tests/test_extract.py
from app.stream import extract_hashtags
def test_extract_basic():
    assert extract_hashtags("Hola #AI y #Python!") == ["#ai", "#python"]
