import random

import networkx as nx
import pytest

import grafo_pesado as g


def peso(G, u, v):
    return G[u][v]["w"]


def grafo_aleatorio(seed, dirigido):
    rng = random.Random(seed)
    G = nx.gnp_random_graph(25, 0.15, seed=seed, directed=dirigido)
    for u, v in G.edges:
        G[u][v]["w"] = rng.randint(1, 20)
    return G


def coste(G, camino):
    return sum(peso(G, u, v) for u, v in zip(camino, camino[1:]))


@pytest.mark.parametrize("seed", range(40))
def test_camino_minimo_vs_networkx(seed):
    G = grafo_aleatorio(seed, dirigido=bool(seed % 2))
    for destino in G.nodes:
        camino = g.camino_minimo(G, peso, 0, destino)
        if nx.has_path(G, 0, destino):
            assert camino[0] == 0 and camino[-1] == destino
            assert coste(G, camino) == nx.shortest_path_length(G, 0, destino, weight="w")
        else:
            assert camino is None


def test_dijkstra_solo_alcanzables():
    G = nx.DiGraph()
    G.add_edge(1, 2, w=1)
    G.add_node(3)
    assert g.dijkstra(G, peso, 1) == {1: None, 2: 1}


@pytest.mark.parametrize("seed", range(0, 40, 2))
def test_arbol_abarcador_minimo(seed):
    G = grafo_aleatorio(seed, dirigido=False)
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    optimo = nx.minimum_spanning_tree(G, weight="w").size(weight="w")

    aristas_kruskal = g.kruskal(G, peso)
    assert len(aristas_kruskal) == G.number_of_nodes() - 1
    assert sum(peso(G, u, v) for u, v in aristas_kruskal) == optimo

    padres = g.prim(G, peso)
    aristas_prim = [(u, v) for v, u in padres.items() if u is not None]
    assert len(aristas_prim) == G.number_of_nodes() - 1
    assert sum(peso(G, u, v) for u, v in aristas_prim) == optimo
