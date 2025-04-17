# graphscene.py
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen
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
        self.edge_source  = None
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
                # Let selection of edges work normally
                pass
            else:
                self.edge_source = None
                self.add_vertex(event.scenePos().x(), event.scenePos().y())

        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for itm in list(self.selectedItems()):
                if isinstance(itm, Vertex):
                    # remove connected edges
                    for ed in [e for e in self.edges if e.vertex1==itm or e.vertex2==itm]:
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
        rest=100.0; kr=10000.0; ka=0.5; damp=0.9
        # reset
        for v in self.vertices: v.force = QPointF(0,0)
        # repulsion
        n=len(self.vertices)
        for i in range(n):
            for j in range(i+1,n):
                v1=self.vertices[i]; v2=self.vertices[j]
                p1=v1.pos()+v1.get_center(); p2=v2.pos()+v2.get_center()
                d_vec = p1-p2
                d = math.hypot(d_vec.x(),d_vec.y()) or 1
                rep = kr/d
                f = QPointF(rep*(d_vec.x()/d), rep*(d_vec.y()/d))
                v1.force += f; v2.force -= f
        # attraction
        for e in self.edges:
            v1,e_v2 = e.vertex1, e.vertex2
            p1=v1.pos()+v1.get_center(); p2=e_v2.pos()+e_v2.get_center()
            d_vec = p1-p2
            d = math.hypot(d_vec.x(),d_vec.y()) or 1
            attr = ka*(d-rest)
            f = QPointF(attr*(d_vec.x()/d), attr*(d_vec.y()/d))
            v1.force -= f; e_v2.force += f
        # integrate
        for v in self.vertices:
            v.velocity = (v.velocity + v.force*dt)*damp
            v.setPos(v.pos()+v.velocity*dt)

    # --- Recommended features below ---

    def label_degrees(self):
        info = ga.get_graph_info(self)
        deg  = info['degrees']
        for v in self.vertices:
            d = deg.get(id(v), 0)
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
            pen = e.pen()
            pen.setColor(QColor('red') if pair in bridges else QColor('black'))
            e.setPen(pen)

    def clear_edge_highlights(self):
        for e in self.edges:
            pen=e.pen(); pen.setColor(QColor('black')); e.setPen(pen)

    def color_by_component(self):
        info = ga.get_graph_info(self)
        comps = info['components']
        palette = [QColor(c) for c in ('#e6194b','#3cb44b','#ffe119','#4363d8','#f58231','#911eb4')]
        for idx, comp in enumerate(comps):
            col = palette[idx%len(palette)]
            for v in self.vertices:
                if id(v) in comp:
                    v.set_color(col)

    def reset_vertex_colors(self):
        for v in self.vertices:
            v.reset_color()

    def color_by_bipartite(self):
        info = ga.get_graph_info(self)
        if not info['is_bipartite']:
            return False
        import networkx as nx
        G = ga.build_graph(self)
        color_map = nx.bipartite.color(G)
        for v in self.vertices:
            c = QColor('#aaffc3') if color_map[id(v)]==0 else QColor('#ffd8b1')
            v.set_color(c)
        return True
