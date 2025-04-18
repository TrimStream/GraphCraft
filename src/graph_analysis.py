import networkx as nx
import numpy as np

def build_graph(scene):
    """Build a NetworkX graph from the scene."""
    directed = any(getattr(e, 'directed', False) for e in scene.edges)
    G = nx.MultiDiGraph() if directed else nx.MultiGraph()
    for v in scene.vertices:
        G.add_node(id(v))
    for e in scene.edges:
        G.add_edge(id(e.vertex1), id(e.vertex2))
    return G

def get_graph_info(G):
    """Compute graph information given a NetworkX graph G."""
    info = {
        'is_directed': G.is_directed(),
        'num_vertices': G.number_of_nodes(),
        'num_edges': G.number_of_edges()
    }

    if info['is_directed']:
        info['degrees'] = {n: {'in': G.in_degree(n), 'out': G.out_degree(n)} for n in G.nodes()}
        info['strongly_connected_components'] = list(nx.strongly_connected_components(G))
        info['components'] = list(nx.weakly_connected_components(G))
    else:
        info['degrees'] = {n: G.degree(n) for n in G.nodes()}
        info['components'] = list(nx.connected_components(G))

    # Build a simple Graph (undirected) for matrix, bridges, and eigenvalue analysis
    simpleG = nx.Graph()
    simpleG.add_nodes_from(G.nodes())
    simpleG.add_edges_from(G.edges())

    if not info['is_directed']:
        info['bridges'] = list(nx.bridges(simpleG))

    info['is_bipartite'] = nx.is_bipartite(simpleG)

    try:
        info['adjacency_matrix'] = nx.adjacency_matrix(simpleG).todense()
    except Exception:
        info['adjacency_matrix'] = np.array([])

    try:
        info['laplacian_matrix'] = nx.laplacian_matrix(simpleG).todense()
    except Exception:
        info['laplacian_matrix'] = np.array([])

    try:
        ev, evecs = np.linalg.eig(info['laplacian_matrix'])
        info['eigenvalues'] = ev
        info['eigenvectors'] = evecs
    except Exception:
        info['eigenvalues'] = []
        info['eigenvectors'] = []

    if not info['is_directed']:
        try:
            coloring = nx.coloring.greedy_color(simpleG, strategy='largest_first')
            info['chromatic_number'] = len(set(coloring.values()))
        except Exception:
            info['chromatic_number'] = None
    else:
        info['chromatic_number'] = None

    return info

def format_info(info):
    """Format the graph info dictionary into a readable string."""
    lines = []
    lines.append(f"Graph Type: {'Directed' if info['is_directed'] else 'Undirected'}")
    lines.append(f"Vertices: {info['num_vertices']}")
    lines.append(f"Edges: {info['num_edges']}")

    lines.append("Degrees:")
    if info['is_directed']:
        for n, d in info['degrees'].items():
            lines.append(f"  Node {n}: in-degree={d['in']}, out-degree={d['out']}")
        lines.append(f"Strongly Connected Components: {len(info['strongly_connected_components'])}")
    else:
        for n, d in info['degrees'].items():
            lines.append(f"  Node {n}: degree={d}")

    lines.append(f"Connected Components: {len(info['components'])}")

    if not info['is_directed']:
        lines.append(f"Bridges: {len(info['bridges'])}")

    lines.append(f"Bipartite: {'Yes' if info['is_bipartite'] else 'No'}")

    if info['chromatic_number'] is not None:
        lines.append(f"Chromatic Number (heuristic): {info['chromatic_number']}")

    if info['adjacency_matrix'].size > 0:
        lines.append(f"Adjacency Matrix Size: {info['adjacency_matrix'].shape}")

    if info['laplacian_matrix'].size > 0:
        lines.append(f"Laplacian Matrix Size: {info['laplacian_matrix'].shape}")

    ev = info['eigenvalues']
    if len(ev) > 0:
        preview = np.round(ev[:min(10, len(ev))], 4).tolist()
        lines.append(f"First Eigenvalues: {preview}")

    return "\n".join(lines)
