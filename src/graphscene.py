# graphscene.py
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor
from vertex import Vertex
from edge import Edge
import math
import networkx as nx
import graph_analysis as ga

class GraphScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices = []
        self.edges    = []
        self.edge_source   = None
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
        if event.button() == Qt.LeftButton:
            items = self.items(event.scenePos())
            v_click = next((i for i in items if isinstance(i, Vertex)), None)
            e_click = next((i for i in items if isinstance(i, Edge)), None)
            if v_click:
                if not self.edge_source:
                    self.edge_source = v_click
                    v_click.setSelected(True)
                else:
                    self.add_edge(self.edge_source, v_click)
                    self.edge_source = None
            elif e_click:
                pass  # let edge selection occur
            else:
                self.edge_source = None
                self.add_vertex(event.scenePos().x(), event.scenePos().y())
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for itm in list(self.selectedItems()):
                if isinstance(itm, Vertex):
                    # remove incident edges
                    for e in [e for e in self.edges if e.vertex1 is itm or e.vertex2 is itm]:
                        self.removeItem(e)
                        self.edges.remove(e)
                    self.removeItem(itm)
                    self.vertices.remove(itm)
                elif isinstance(itm, Edge):
                    self.removeItem(itm)
                    self.edges.remove(itm)
        else:
            super().keyPressEvent(event)

    def update_edges(self):
        for e in self.edges:
            e.update_position()

    def update_physics(self, dt):
        rest, kr, ka, damp = 100.0, 10000.0, 0.5, 0.9
        # reset forces
        for v in self.vertices:
            v.force = QPointF(0, 0)

        # repulsive forces
        n = len(self.vertices)
        for i in range(n):
            for j in range(i+1, n):
                v1, v2 = self.vertices[i], self.vertices[j]
                p1 = v1.pos() + v1.get_center()
                p2 = v2.pos() + v2.get_center()
                dvec = p1 - p2
                dist = math.hypot(dvec.x(), dvec.y()) or 1
                rep = kr / dist
                f = QPointF(rep * dvec.x()/dist, rep * dvec.y()/dist)
                v1.force += f
                v2.force -= f

        # attractive (spring) forces
        for e in self.edges:
            v1, v2 = e.vertex1, e.vertex2
            p1 = v1.pos() + v1.get_center()
            p2 = v2.pos() + v2.get_center()
            dvec = p1 - p2
            dist = math.hypot(dvec.x(), dvec.y()) or 1
            attr = ka * (dist - rest)
            f = QPointF(attr * dvec.x()/dist, attr * dvec.y()/dist)
            v1.force -= f
            v2.force += f

        # integrate motion
        for v in self.vertices:
            v.velocity = (v.velocity + v.force * dt) * damp
            v.setPos(v.pos() + v.velocity * dt)

    # === Recommended & Bonus Features ===

    def label_degrees(self):
        """Label each vertex with its current degree, in white text."""
        self.clear_labels()
        for v in self.vertices:
            deg = sum(1 for e in self.edges if e.vertex1 is v or e.vertex2 is v)
            v.set_label(str(deg))
            if v.label_item:
                v.label_item.setDefaultTextColor(QColor('white'))

    def clear_labels(self):
        """Remove all text labels from vertices."""
        for v in self.vertices:
            if v.label_item:
                self.removeItem(v.label_item)
                v.label_item = None

    def highlight_bridges(self):
        """
        Highlight bridges in red by computing them on a simple undirected graph.
        """
        G = ga.build_graph(self)
        simpleG = nx.Graph(G)
        bridges = {tuple(sorted(b)) for b in nx.bridges(simpleG)}
        for e in self.edges:
            key = tuple(sorted((id(e.vertex1), id(e.vertex2))))
            pen = e.pen()
            pen.setColor(QColor('red') if key in bridges else QColor('black'))
            e.setPen(pen)

    def clear_edge_highlights(self):
        """Reset all edge colors back to black."""
        for e in self.edges:
            pen = e.pen()
            pen.setColor(QColor('black'))
            e.setPen(pen)

    def color_by_component(self):
        """
        Compute connected components via BFS on the current scene graph
        and color each component from a small palette.
        """
        # Build adjacency list
        adj = {v: [] for v in self.vertices}
        for e in self.edges:
            adj[e.vertex1].append(e.vertex2)
            adj[e.vertex2].append(e.vertex1)

        visited = set()
        components = []

        # BFS to find components
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

        # Color components
        palette = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4']
        for idx, comp in enumerate(components):
            col = QColor(palette[idx % len(palette)])
            for v in comp:
                v.set_color(col)

    def reset_vertex_colors(self):
        """Reset all vertices to their original brush."""
        for v in self.vertices:
            v.reset_color()

    def color_by_bipartite(self):
        info = ga.get_graph_info(self)
        if not info['is_bipartite']:
            return False
        G = ga.build_graph(self)
        cmap = nx.bipartite.color(G)
        for v in self.vertices:
            c = QColor('#aaffc3') if cmap[id(v)] == 0 else QColor('#ffd8b1')
            v.set_color(c)
        return True

    def cartesian_product(self):
        # unchanged from your existing implementation
        ...

    def chromatic_polynomial(self):
        # unchanged from your existing implementation
        ...
