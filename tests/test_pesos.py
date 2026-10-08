import networkx as nx
import pytest

import pesos


def test_parse_maxspeed():
    assert pesos.parse_maxspeed("50") == 50
    assert pesos.parse_maxspeed("30 mph") == 30
    assert pesos.parse_maxspeed(["30", "50"]) == 50   # se toma la menos restrictiva


def test_time_weight():
    G = nx.DiGraph()
    G.add_edge(1, 2, length=100, maxspeed="36")                  # 36 km/h = 10 m/s
    G.add_edge(2, 3, length=100, highway="residential")           # sin maxspeed -> 30 km/h
    G.add_edge(3, 4, length=100, highway="tipo_desconocido")      # sin maxspeed ni tipo conocido -> 50 km/h
    G.add_edge(4, 5, length=100, highway=["residential", "primary"])
    assert pesos.time_weight(G, 1, 2) == pytest.approx(10)
    assert pesos.time_weight(G, 2, 3) == pytest.approx(12)
    assert pesos.time_weight(G, 3, 4) == pytest.approx(7.2)
    assert pesos.time_weight(G, 4, 5) == pytest.approx(7.2)


def test_stoplights_weight():
    G = nx.DiGraph()
    G.add_edge(1, 2, length=100, maxspeed="36")
    G.add_edges_from([(2, 3), (3, 2)], length=100, maxspeed="36")
    assert pesos.stoplights_weight(G, 1, 2) == pytest.approx(10 + 0.8 * 30)   # 2 es intersección (grado 3)
    assert pesos.stoplights_weight(G, 2, 3) == pytest.approx(10)              # 3 no lo es (grado 2)
