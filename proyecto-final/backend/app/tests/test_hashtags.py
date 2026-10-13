from app.utils_hashtags import extract_hashtags, count_hashtags

def test_extract():
    assert extract_hashtags("hola #YouTube #IA!") == ["youtube","ia"]

def test_count():
    top = count_hashtags(["#a #a", "#b"], top_n=2)
    assert top[0] == ("a", 2)
