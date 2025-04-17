from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt, QPointF
from vertex import Vertex
from edge import Edge
import math
import graph_analysis as ga
import networkx as nx

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
                pass
            else:
                self.edge_source = None
                self.add_vertex(event.scenePos().x(), event.scenePos().y())
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for itm in list(self.selectedItems()):
                if isinstance(itm, Vertex):
                    for ed in [e for e in self.edges
                               if e.vertex1 is itm or e.vertex2 is itm]:
                        self.removeItem(ed)
                        self.edges.remove(ed)
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
        # reset
        for v in self.vertices:
            v.force = QPointF(0,0)
        # repulsion
        n = len(self.vertices)
        for i in range(n):
            for j in range(i+1, n):
                v1, v2 = self.vertices[i], self.vertices[j]
                p1 = v1.pos() + v1.get_center()
                p2 = v2.pos() + v2.get_center()
                dvec = p1 - p2
                d = math.hypot(dvec.x(), dvec.y()) or 1
                rep = kr / d
                f = QPointF(rep * dvec.x()/d, rep * dvec.y()/d)
                v1.force += f
                v2.force -= f
        # springs
        for e in self.edges:
            v1, v2 = e.vertex1, e.vertex2
            p1 = v1.pos() + v1.get_center()
            p2 = v2.pos() + v2.get_center()
            dvec = p1 - p2
            d = math.hypot(dvec.x(), dvec.y()) or 1
            attr = ka * (d - rest)
            f = QPointF(attr * dvec.x()/d, attr * dvec.y()/d)
            v1.force -= f
            v2.force += f
        # integrate
        for v in self.vertices:
            v.velocity = (v.velocity + v.force * dt) * damp
            v.setPos(v.pos() + v.velocity * dt)

    # --- Recommended and bonus features ---

    def label_degrees(self):
        info = ga.get_graph_info(self)
        for v in self.vertices:
            d = info['degrees'].get(id(v), 0)
            v.set_label(str(d))

    def clear_labels(self):
        for v in self.vertices:
            if v.label_item:
                self.removeItem(v.label_item)
                v.label_item = None

    def highlight_bridges(self):
        info = ga.get_graph_info(self)
        bridges = {tuple(sorted(b)) for b in info['bridges']}
        for e in self.edges:
            pair = tuple(sorted((id(e.vertex1), id(e.vertex2))))
            col = 'red' if pair in bridges else 'black'
            pen = e.pen()
            pen.setColor(QColor(col))
            e.setPen(pen)

    def clear_edge_highlights(self):
        for e in self.edges:
            pen = e.pen()
            pen.setColor(QColor('black'))
            e.setPen(pen)

    def color_by_component(self):
        info = ga.get_graph_info(self)
        palette = ['#e6194b','#3cb44b','#ffe119','#4363d8','#f58231','#911eb4']
        for idx, comp in enumerate(info['components']):
            col = palette[idx % len(palette)]
            for v in self.vertices:
                if id(v) in comp:
                    v.set_color(QColor(col))

    def reset_vertex_colors(self):
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
        import networkx as nx
        G = ga.build_graph(self)
        H = nx.complete_graph(2)
        P = nx.cartesian_product(G, H)
        orig = {id(v): v.pos() for v in self.vertices}
        # clear scene
        for e in list(self.edges):
            self.removeItem(e); self.edges.remove(e)
        for v in list(self.vertices):
            self.removeItem(v); self.vertices.remove(v)
        self.edge_source = None
        self.vertex_map = {}
        offset = 200
        # add vertices
        for (u,i) in P.nodes():
            pos = orig.get(u, QPointF(0,0)) + QPointF(i*offset, 0)
            new_v = self.add_vertex(pos.x(), pos.y())
            self.vertex_map[(u,i)] = new_v
        # add edges
        for u1,u2 in P.edges():
            v1 = self.vertex_map[u1]; v2 = self.vertex_map[u2]
            self.add_edge(v1, v2)

    def chromatic_polynomial(self):
        import itertools
        n = len(self.vertices)
        nodes = [id(v) for v in self.vertices]
        adj = {u:set() for u in nodes}
        for e in self.edges:
            adj[id(e.vertex1)].add(id(e.vertex2))
            adj[id(e.vertex2)].add(id(e.vertex1))
        poly = {}
        # only feasible for small n
        for k in range(1, min(n,6)+1):
            count = 0
            for coloring in itertools.product(range(k), repeat=n):
                ok = True
                for i,u in enumerate(nodes):
                    for j,v in enumerate(nodes):
                        if v in adj[u] and coloring[i] == coloring[j]:
                            ok = False; break
                    if not ok: break
                if ok:
                    count += 1
            poly[k] = count
        return poly
