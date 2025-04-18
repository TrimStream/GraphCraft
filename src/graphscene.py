from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsScene, QColorDialog, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt, QPointF
from vertex import Vertex
from edge import Edge
import math
import networkx as nx
import graph_analysis as ga
import itertools

class GraphScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices = []
        self.edges = []
        self.edge_source = None
        self.directed_mode = False

    def add_vertex(self, x, y):
        v = Vertex(x, y)
        self.addItem(v)
        self.vertices.append(v)
        return v

    def add_edge(self, v1, v2):
        e = Edge(v1, v2, directed=self.directed_mode)
        self.addItem(e)
        self.edges.append(e)
        return e

    def mousePressEvent(self, event):
        items = self.items(event.scenePos())
        v_click = next((i for i in items if isinstance(i, Vertex)), None)
        e_click = next((i for i in items if isinstance(i, Edge)), None)

        if event.button() == Qt.LeftButton:
            if v_click:
                if not self.edge_source:
                    self.edge_source = v_click
                    v_click.setSelected(True)
                else:
                    self.add_edge(self.edge_source, v_click)
                    self.edge_source = None
            elif e_click:
                e_click.setSelected(True)
            else:
                self.edge_source = None
                self.add_vertex(event.scenePos().x(), event.scenePos().y())

        elif event.button() == Qt.RightButton:
            if v_click or e_click:
                color = QColorDialog.getColor()
                if color.isValid():
                    if v_click:
                        v_click.set_color(color)
                    elif e_click:
                        e_click.set_color(color)

        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in list(self.selectedItems()):
                if isinstance(item, Vertex):
                    for e in list(self.edges):
                        if e.vertex1 == item or e.vertex2 == item:
                            self.removeItem(e)
                            self.edges.remove(e)
                    self.removeItem(item)
                    self.vertices.remove(item)
                elif isinstance(item, Edge):
                    self.removeItem(item)
                    self.edges.remove(item)
            self.edge_source = None
        else:
            super().keyPressEvent(event)

    def clear_scene(self):
        for e in self.edges:
            self.removeItem(e)
        for v in self.vertices:
            self.removeItem(v)
        self.vertices.clear()
        self.edges.clear()
        self.edge_source = None

    def update_edges(self):
        for e in self.edges:
            e.update_position()

    def update_physics(self, dt):
        rest, kr, ka, damp = 100.0, 10000.0, 0.5, 0.9
        for v in self.vertices:
            v.force = QPointF(0, 0)

        for i in range(len(self.vertices)):
            for j in range(i + 1, len(self.vertices)):
                v1, v2 = self.vertices[i], self.vertices[j]
                p1 = v1.pos() + v1.get_center()
                p2 = v2.pos() + v2.get_center()
                dvec = p1 - p2
                dist = math.hypot(dvec.x(), dvec.y()) or 1
                rep = kr / dist
                f = QPointF(rep * dvec.x() / dist, rep * dvec.y() / dist)
                v1.force += f
                v2.force -= f

        for e in self.edges:
            v1, v2 = e.vertex1, e.vertex2
            p1 = v1.pos() + v1.get_center()
            p2 = v2.pos() + v2.get_center()
            dvec = p1 - p2
            dist = math.hypot(dvec.x(), dvec.y()) or 1
            attr = ka * (dist - rest)
            f = QPointF(attr * dvec.x() / dist, attr * dvec.y() / dist)
            v1.force -= f
            v2.force += f

        for v in self.vertices:
            v.velocity = (v.velocity + v.force * dt) * damp
            v.setPos(v.pos() + v.velocity * dt)

    def label_degrees(self):
        self.clear_labels()
        for v in self.vertices:
            deg = sum(1 for e in self.edges if e.vertex1 is v or e.vertex2 is v)
            v.set_label(str(deg))
            if v.label_item:
                v.label_item.setDefaultTextColor(QColor('white'))

    def clear_labels(self):
        for v in self.vertices:
            if v.label_item:
                self.removeItem(v.label_item)
                v.label_item = None

    def highlight_bridges(self):
        try:
            G = ga.build_graph(self)
            simpleG = nx.Graph(G)
            bridges = {tuple(sorted(b)) for b in nx.bridges(simpleG)}
            for e in self.edges:
                key = tuple(sorted((id(e.vertex1), id(e.vertex2))))
                if key in bridges:
                    e.set_temp_color(QColor('red'))
                else:
                    e.reset_temp_color()
        except Exception as e:
            print("Error during bridge highlighting:", e)

    def clear_edge_highlights(self):
        for e in self.edges:
            e.reset_temp_color()

    def color_by_component(self):
        adj = {v: [] for v in self.vertices}
        for e in self.edges:
            adj[e.vertex1].append(e.vertex2)
            adj[e.vertex2].append(e.vertex1)

        visited = set()
        components = []
        for v in self.vertices:
            if v not in visited:
                queue = [v]
                visited.add(v)
                comp = []
                while queue:
                    u = queue.pop(0)
                    comp.append(u)
                    for nbr in adj[u]:
                        if nbr not in visited:
                            visited.add(nbr)
                            queue.append(nbr)
                components.append(comp)

        palette = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4']
        for idx, comp in enumerate(components):
            color = QColor(palette[idx % len(palette)])
            for v in comp:
                v.set_temp_color(color)

    def reset_vertex_colors(self):
        for v in self.vertices:
            v.reset_temp_color()

    def color_by_bipartite(self):
        adj = {v: [] for v in self.vertices}
        for e in self.edges:
            adj[e.vertex1].append(e.vertex2)
            adj[e.vertex2].append(e.vertex1)

        color = {}
        for start in self.vertices:
            if start in color:
                continue
            queue = [start]
            color[start] = 0
            while queue:
                u = queue.pop(0)
                for nbr in adj[u]:
                    if nbr not in color:
                        color[nbr] = 1 - color[u]
                        queue.append(nbr)
                    elif color[nbr] == color[u]:
                        return False
        for v, side in color.items():
            v.set_temp_color(QColor('#aaffc3') if side == 0 else QColor('#ffd8b1'))
        return True

    def pretty_layout(self):
        G = ga.build_graph(self)
        pos = nx.spring_layout(G)
        id_to_vertex = {id(v): v for v in self.vertices}
        for node_id, (x, y) in pos.items():
            if node_id in id_to_vertex:
                id_to_vertex[node_id].setPos(x * 500, y * 500)

    def run_dijkstra(self):
        if len(self.vertices) < 2:
            QMessageBox.warning(None, "Error", "Need at least 2 vertices.")
            return
        ids = [str(i) for i in range(len(self.vertices))]
        i, ok1 = QInputDialog.getItem(None, "Source Vertex", "Select source vertex:", ids, 0, False)
        if not ok1:
            return
        j, ok2 = QInputDialog.getItem(None, "Target Vertex", "Select target vertex:", ids, 0, False)
        if not ok2:
            return
        source = self.vertices[int(i)]
        target = self.vertices[int(j)]

        G = ga.build_graph(self)
        try:
            length = nx.shortest_path_length(G, id(source), id(target))
            QMessageBox.information(None, "Dijkstra Result", f"Shortest path length: {length}")
        except:
            QMessageBox.warning(None, "Error", "No path exists between the selected vertices.")

    def find_mst(self):
        G = ga.build_graph(self)
        simpleG = nx.Graph(G)
        try:
            T = nx.minimum_spanning_tree(simpleG)
            total_weight = T.size(weight=None)
            QMessageBox.information(None, "MST Result", f"Total MST weight: {total_weight}")
        except:
            QMessageBox.warning(None, "Error", "Cannot compute MST for disconnected graph.")

    def find_max_flow(self):
        if len(self.vertices) < 2:
            QMessageBox.warning(None, "Error", "Need at least 2 vertices.")
            return
        ids = [str(i) for i in range(len(self.vertices))]
        i, ok1 = QInputDialog.getItem(None, "Source Vertex", "Select source vertex:", ids, 0, False)
        if not ok1:
            return
        j, ok2 = QInputDialog.getItem(None, "Sink Vertex", "Select sink vertex:", ids, 0, False)
        if not ok2:
            return
        source = self.vertices[int(i)]
        sink = self.vertices[int(j)]

        G = nx.DiGraph()
        for e in self.edges:
            u = id(e.vertex1)
            v = id(e.vertex2)
            G.add_edge(u, v, capacity=1)

        try:
            flow_value, _ = nx.maximum_flow(G, id(source), id(sink))
            QMessageBox.information(None, "Max Flow Result", f"Maximum flow value: {flow_value}")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Cannot compute max flow.\n{str(e)}")

    def chromatic_polynomial(self):
        nodes = [id(v) for v in self.vertices]
        adj = {u: set() for u in nodes}
        for e in self.edges:
            adj[id(e.vertex1)].add(id(e.vertex2))
            adj[id(e.vertex2)].add(id(e.vertex1))
        n = len(nodes)
        poly = {}
        for k in range(1, min(n, 6) + 1):
            count = 0
            for coloring in itertools.product(range(k), repeat=n):
                ok = True
                for i, u in enumerate(nodes):
                    for j, v in enumerate(nodes):
                        if v in adj[u] and coloring[i] == coloring[j]:
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    count += 1
            poly[k] = count
        return poly

    def cartesian_product(self):
        G = ga.build_graph(self)
        H = nx.complete_graph(2)
        P = nx.cartesian_product(G, H)

        id_to_pos = {id(v): v.pos() for v in self.vertices}

        for e in list(self.edges):
            self.removeItem(e)
            self.edges.remove(e)
        for v in list(self.vertices):
            self.removeItem(v)
            self.vertices.remove(v)

        self.edge_source = None
        self.vertex_map = {}

        dx = 200
        for (u, i) in P.nodes():
            pos = id_to_pos.get(u, QPointF(0, 0)) + QPointF(i * dx, 0)
            nv = self.add_vertex(pos.x(), pos.y())
            self.vertex_map[(u, i)] = nv

        for u1, u2 in P.edges():
            self.add_edge(self.vertex_map[u1], self.vertex_map[u2])
