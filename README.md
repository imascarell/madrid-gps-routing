# Madrid GPS Routing — Discrete Mathematics

Group project for **Discrete Mathematics** (iMAT, ICAI, Universidad Pontificia Comillas, 2025/26).
Authors (group GP11B): **Ignacio Mascarell Agúndez**, Jaime Tuesta de Simón.

Terminal GPS for the city of Madrid: type an origin and a destination, choose shortest, fastest or traffic-light-aware route, and get turn-by-turn instructions plus a map of the route. Graph algorithms are written from scratch (no NetworkX shortest-path or spanning-tree helpers); NetworkX is only used as the graph data structure.

## Modules

**`grafo_pesado.py`** — weighted graph algorithms for any weight function `peso(G, u, v)`:

- **Dijkstra** with a binary heap (shortest-path tree from an origin) and path reconstruction.
- Minimum spanning trees with **Prim** and **Kruskal** (not used by the GPS, part of the library).

**`callejero.py`** — data layer:

- Loads the official Madrid street directory (≈ 214k street numbers) and converts DMS coordinates to decimal degrees with regex.
- Address lookup in full (`Calle de Alberto Aguilera, 23`) or short form (`Alberto Aguilera, 23`), accent-insensitive, asking the user when an address is ambiguous.
- **Fuzzy search** when an address does not exist: normalised **Levenshtein distance** (own implementation, two-row dynamic programming) against every address in the directory, suggesting the closest matches. Exact lower bounds (character-histogram distance and early stopping) skip most candidates without changing the result.
- Downloads the drivable street network of Madrid from **OpenStreetMap** (OSMnx), caches it as GraphML and turns the multidigraph into a simple digraph without loops (≈ 31k intersections).

**`pesos.py`** — three edge weights:

| Mode | Weight |
|------|--------|
| `MC` shortest | edge length (m) |
| `MR` fastest | length / speed limit; missing limits inferred from the road type |
| `MRO` fastest with traffic lights | travel time + expected wait at intersections (degree > 2: 80 % chance of a 30 s light) |

**`gps.py`** — interactive program: geocodes both addresses, snaps them to the nearest graph nodes, runs Dijkstra, merges consecutive edges of the same street into instructions, classifies each turn as left / right / straight from the angle and the sign of the cross product of consecutive edges, and draws the route zoomed over the street map.

```text
-- ORIGEN --
 - Dirección: Calle de Alberto Agilera, 23
La dirección no se encuentra en la base de datos. ¿Quiere decir...?
1. CALLE DE ALBERTO AGUILERA, 23
2. CALLE DE ALBERTO AGUILERA, 13
...
-- DESTINO --
 - Dirección: Calle de Alcalá, 50
-- MÉTODO DE CÁLCULO DE RUTA --
 Opción: MR

DIRECCIONES:
...
Avance 618.13 m por Calle de Alberto Aguilera.
Siga recto hacia Glorieta de Ruiz Jiménez.
...
Gire a la derecha hacia Calle de Alcalá.
Avance 165.22 m por Calle de Alcalá hasta llegar a su destino.
```

## Data

Not included in the repo (≈ 60 MB):

- `direcciones.csv` — *Callejero vigente: relación de direcciones vigentes, con coordenadas* from the [Madrid open data portal](https://datos.madrid.es/en/dataset/213605-0-callejero-oficial-madrid) (`;`-separated, Latin-1). Download it and save it with that name next to `gps.py`. The project used the November 2025 release.
- `madrid.graphml` — downloaded automatically from OpenStreetMap on the first run (needs internet; it can take a few minutes) and reused afterwards.

## Run

```bash
pip install -r requirements.txt
python gps.py   # empty address to exit
```

## Tests

```bash
pytest
```

The tests compare Dijkstra, Prim and Kruskal with NetworkX on random graphs (directed and undirected, including unreachable nodes), check the Levenshtein implementation against a full dynamic-programming table, and cover the weight functions, address lookup (exact, ambiguous and with typos) and turn classification. They do not need the data files.

Python 3 (tested on 3.13). Code comments and docstrings are in Spanish.
