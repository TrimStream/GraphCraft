# graph_analysis.py
import networkx as nx
import numpy as np

def build_graph(scene):
    """
    Construct a NetworkX MultiGraph from the scene.
    Use the id() of a vertex as a node identifier.
    """
    G = nx.MultiGraph()
    for v in scene.vertices:
        G.add_node(id(v))
    for edge in scene.edges:
        # Allow parallel edges by using a MultiGraph.
        G.add_edge(id(edge.vertex1), id(edge.vertex2))
    return G

def get_graph_info(scene):
    G = build_graph(scene)
    info = {}
    info['num_vertices'] = G.number_of_nodes()
    info['num_edges'] = G.number_of_edges()
    info['degrees'] = {n: G.degree(n) for n in G.nodes()}
    components = list(nx.connected_components(G))
    info['components'] = components
    # Bridges (works on simple graphs—convert MultiGraph to simple graph)
    simpleG = nx.Graph(G)
    info['bridges'] = list(nx.bridges(simpleG))
    info['is_bipartite'] = nx.is_bipartite(G)
    # Adjacency and Laplacian matrices.
    A = nx.adjacency_matrix(G).todense()
    info['adjacency_matrix'] = A
    L = nx.laplacian_matrix(G).todense()
    info['laplacian_matrix'] = L
    eigenvalues, eigenvectors = np.linalg.eig(L)
    info['eigenvalues'] = eigenvalues
    info['eigenvectors'] = eigenvectors
    # Greedy coloring (heuristic chromatic number).
    color_map = nx.coloring.greedy_color(G, strategy='largest_first')
    info['chromatic_number'] = len(set(color_map.values()))
    return info

def format_info(info):
    s = ""
    s += f"Vertices: {info['num_vertices']}\n"
    s += f"Edges: {info['num_edges']}\n"
    s += "Degrees:\n"
    for n, d in info['degrees'].items():
        s += f"  Vertex {n}: {d}\n"
    s += f"Components: {info['components']}\n"
    s += f"Bridges: {info['bridges']}\n"
    s += f"Bipartite: {info['is_bipartite']}\n"
    s += f"Chromatic Number (heuristic): {info['chromatic_number']}\n"
    s += "Adjacency Matrix:\n" + str(info['adjacency_matrix']) + "\n"
    s += "Laplacian Matrix:\n" + str(info['laplacian_matrix']) + "\n"
    s += f"Eigenvalues:\n{info['eigenvalues']}\n"
    return s
