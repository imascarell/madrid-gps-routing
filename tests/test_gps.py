import networkx as nx

import gps


def grafo_cruce():
    G = nx.DiGraph()
    coords = {"o": (0, 0), "c": (0, 1), "izq": (-1, 1), "der": (1, 1), "rec": (0, 2)}
    for n, (x, y) in coords.items():
        G.add_node(n, x=x, y=y)
    return G


def test_tipo_giro():
    G = grafo_cruce()
    assert gps.tipo_giro(G, "o", "c", "izq") == "izquierda"
    assert gps.tipo_giro(G, "o", "c", "der") == "derecha"
    assert gps.tipo_giro(G, "o", "c", "rec") == "recto"


def test_hallar_nombre_via():
    G = nx.DiGraph()
    G.add_edge(1, 2, name="Gran Vía")
    G.add_edge(2, 3, name=["Calle Mayor", "Calle de Esparteros"])
    G.add_edge(3, 4, ref="M-30")
    G.add_edge(4, 5)
    assert gps.hallar_nombre_via(G, 1, 2) == "Gran Vía"
    assert gps.hallar_nombre_via(G, 2, 3) == "Calle Mayor y Calle de Esparteros"
    assert gps.hallar_nombre_via(G, 3, 4) == "M-30"
    assert gps.hallar_nombre_via(G, 4, 5) == "NO-NAME"
