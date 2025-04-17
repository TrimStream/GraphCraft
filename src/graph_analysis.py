# graph_analysis.py
import networkx as nx
import numpy as np

def build_graph(scene):
    directed = any(getattr(e, 'directed', False) for e in scene.edges)
    G = nx.MultiDiGraph() if directed else nx.MultiGraph()
    for v in scene.vertices:
        G.add_node(id(v))
    for e in scene.edges:
        G.add_edge(id(e.vertex1), id(e.vertex2))
    return G

def get_graph_info(scene):
    G = build_graph(scene)
    info = {
        'is_directed': G.is_directed(),
        'num_vertices': G.number_of_nodes(),
        'num_edges': G.number_of_edges()
    }
    if info['is_directed']:
        info['num_arcs'] = G.number_of_edges()
        info['directed_edges'] = list(G.edges())

    if info['is_directed']:
        info['degrees'] = {
            n:{'in':G.in_degree(n),'out':G.out_degree(n)}
            for n in G.nodes()
        }
    else:
        info['degrees'] = {n:G.degree(n) for n in G.nodes()}

    if info['is_directed']:
        info['strongly_connected_components'] = list(nx.strongly_connected_components(G))
        info['components'] = list(nx.weakly_connected_components(G))
    else:
        info['components'] = list(nx.connected_components(G))

    simple = nx.Graph(G)
    info['bridges'] = list(nx.bridges(simple))

    info['is_bipartite'] = nx.is_bipartite(G)

    info['adjacency_matrix'] = nx.adjacency_matrix(G).todense()
    info['laplacian_matrix'] = nx.laplacian_matrix(G).todense()

    ev, evecs = np.linalg.eig(info['laplacian_matrix'])
    info['eigenvalues']  = ev
    info['eigenvectors'] = evecs

    if not info['is_directed']:
        cm = nx.coloring.greedy_color(G, strategy='largest_first')
        info['chromatic_number'] = len(set(cm.values()))
    else:
        info['chromatic_number'] = None

    return info

def format_info(info):
    L=[]
    L.append(f"Graph Type: {'Directed' if info['is_directed'] else 'Undirected'}")
    L.append(f"Vertices: {info['num_vertices']}")
    L.append(f"Edges: {info['num_edges']}")
    if info.get('num_arcs') is not None:
        L.append(f"Arcs: {info['num_arcs']}")
        L.append(f"Directed Edges: {info['directed_edges']}")
    L.append("Degrees:")
    if info['is_directed']:
        for n,d in info['degrees'].items():
            L.append(f"  Vertex {n}: in={d['in']}, out={d['out']}")
    else:
        for n,d in info['degrees'].items():
            L.append(f"  Vertex {n}: {d}")
    if info['is_directed']:
        L.append(f"Strongly Connected: {info['strongly_connected_components']}")
    L.append(f"Connected Components: {info['components']}")
    L.append(f"Bridges: {info['bridges']}")
    L.append(f"Bipartite: {info['is_bipartite']}")
    if info.get('chromatic_number') is not None:
        L.append(f"Chromatic Number (heuristic): {info['chromatic_number']}")
    A = info['adjacency_matrix']
    L.append(f"Adjacency shape: {A.shape}")
    M = info['laplacian_matrix']
    L.append(f"Laplacian shape: {M.shape}")
    ev = info['eigenvalues']
    pr = ev[:min(10,len(ev))]
    L.append(f"Eigenvalues (first {len(pr)} of {len(ev)}): {np.round(pr,4).tolist()}")
    return "\n".join(L)
