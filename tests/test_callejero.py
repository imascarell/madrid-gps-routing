import pandas as pd
import pytest

import callejero as c


def test_transform_to_degrees():
    assert c.transform_to_degrees("40°25'47.93'' N") == pytest.approx(40 + 25 / 60 + 47.93 / 3600)
    assert c.transform_to_degrees("3°42'40.53'' W") == pytest.approx(-(3 + 42 / 60 + 40.53 / 3600))


@pytest.fixture
def callejero():
    return pd.DataFrame({
        "VIA_CLASE": ["CALLE", "CALLE", "PLAZA"],
        "VIA_PAR": ["DE", "DE", "DE"],
        "VIA_NOMBRE": ["ALBERTO AGUILERA", "ALCALA", "ESPAÑA"],
        "NUMERO": [23, 50, 1],
        "LATITUD": [40.43, 40.42, 40.42],
        "LONGITUD": [-3.71, -3.69, -3.71],
    })


def test_busca_direccion(callejero):
    assert c.busca_direccion("Calle de Alberto Aguilera, 23", callejero) == (40.43, -3.71)
    assert c.busca_direccion("alberto aguilera, 23", callejero) == (40.43, -3.71)   # formato simplificado
    assert c.busca_direccion("Calle de Alcalá, 50", callejero) == (40.42, -3.69)    # con tilde
    assert c.busca_direccion("Plaza de España, 1", callejero) == (40.42, -3.71)      # la Ñ se conserva


def test_busca_direccion_errores(callejero, monkeypatch):
    with pytest.raises(c.AddressNotFoundError):   # nada parecido en el callejero
        c.busca_direccion("Calle de Inventada Totalmente, 7", callejero)
    monkeypatch.setattr("builtins.input", lambda _: "0")   # hay sugerencias, pero el usuario las rechaza
    with pytest.raises(c.AddressNotFoundError):
        c.busca_direccion("Calle de Alberto Aguilera, 999", callejero)
    with pytest.raises(c.FormatNotValidError):
        c.busca_direccion("Alberto Aguilera sin número", callejero)


def levenshtein_referencia(a, b):
    """Tabla completa de programación dinámica, para comparar."""
    d = [[i + j if i * j == 0 else 0 for j in range(len(b) + 1)] for i in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    return d[-1][-1] / max(len(a), len(b))


def test_levenshtein():
    import random
    rng = random.Random(0)
    for _ in range(2000):
        a = "".join(rng.choice("ABC ,1") for _ in range(rng.randint(1, 10)))
        b = "".join(rng.choice("ABC ,1") for _ in range(rng.randint(1, 10)))
        d = levenshtein_referencia(a, b)
        assert c.levenshtein(a, b) == pytest.approx(d)
        # con corte anticipado: mismo valor si está por debajo del máximo
        if d < 0.4:
            assert c.levenshtein(a, b, 0.4) == pytest.approx(d)
        else:
            assert c.levenshtein(a, b, 0.4) >= 0.4
    assert c.levenshtein("KITTEN", "SITTING") == pytest.approx(3 / 7)


def test_fuzzy_ordenado(callejero):
    res = c.mejores_direcciones_fuzzy(callejero, "ALBERTO AGILERA, 23", "simplificado")
    assert res[0][0] == "ALBERTO AGUILERA, 23" and res[0][2] == (40.43, -3.71)
    assert [d for _, d, _ in res] == sorted(d for _, d, _ in res)
    assert c.mejores_direcciones_fuzzy(callejero, "CALLE DE ALBERTO AGILERA, 23", "completo")[0][0] == \
        "CALLE DE ALBERTO AGUILERA, 23"
    assert c.mejores_direcciones_fuzzy(callejero, "XXXXXXXX, 1", "simplificado") == []


def test_busca_direccion_con_errata(callejero, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")   # el usuario elige la primera sugerencia
    assert c.busca_direccion("Calle de Alberto Agilera, 23", callejero) == (40.43, -3.71)
