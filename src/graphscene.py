# graphscene.py
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt, QPointF
from vertex import Vertex
from edge import Edge
import math

class GraphScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices = []
        self.edges = []
        self.edge_source = None  # Stores the source vertex for edge creation

    def add_vertex(self, x, y):
        vertex = Vertex(x, y)
        self.addItem(vertex)
        self.vertices.append(vertex)
        return vertex

    def add_edge(self, vertex1, vertex2, directed=False):
        edge = Edge(vertex1, vertex2, directed)
        self.addItem(edge)
        self.edges.append(edge)
        return edge

    def mousePressEvent(self, event):
        # Only respond to left mouse clicks.
        if event.button() == Qt.LeftButton:
            clicked_items = self.items(event.scenePos())
            vertex_clicked = None
            edge_clicked = None
            # Look for a vertex first.
            for item in clicked_items:
                if isinstance(item, Vertex):
                    vertex_clicked = item
                    break
                # If it's not a Vertex, check if it's an Edge.
                elif hasattr(item, 'update_position'):  # Edge objects have update_position
                    edge_clicked = item

            if vertex_clicked:
                if self.edge_source is None:
                    # First vertex becomes the source.
                    self.edge_source = vertex_clicked
                    vertex_clicked.setSelected(True)
                else:
                    # Second vertex clicked completes the edge.
                    self.add_edge(self.edge_source, vertex_clicked)
                    self.edge_source = None
            elif edge_clicked:
                # An edge was clicked. Allow default processing (i.e. selection)
                # and do not spawn a new vertex.
                pass
            else:
                # Nothing was clicked: create a new vertex.
                self.edge_source = None
                self.add_vertex(event.scenePos().x(), event.scenePos().y())
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                if hasattr(item, 'get_center'):
                    # Delete vertex and its connected edges.
                    edges_to_remove = [edge for edge in self.edges
                                       if edge.vertex1 == item or edge.vertex2 == item]
                    for edge in edges_to_remove:
                        self.removeItem(edge)
                        if edge in self.edges:
                            self.edges.remove(edge)
                    self.removeItem(item)
                    if item in self.vertices:
                        self.vertices.remove(item)
                else:
                    if item in self.edges:
                        self.removeItem(item)
                        self.edges.remove(item)
        else:
            super().keyPressEvent(event)

    def update_edges(self):
        for edge in self.edges:
            edge.update_position()

    def update_physics(self, dt):
        """
        Force-directed simulation:
         - Vertices repel each other with a 1/d force.
         - Edges act as springs with force proportional to (d - rest_length).
        """
        rest_length = 100.0
        k_repulsion = 10000.0
        k_attraction = 0.5
        damping = 0.9

        # Reset forces.
        for v in self.vertices:
            v.force = QPointF(0, 0)

        # Repulsive forces.
        n = len(self.vertices)
        for i in range(n):
            for j in range(i + 1, n):
                v1 = self.vertices[i]
                v2 = self.vertices[j]
                pos1 = v1.pos() + v1.get_center()
                pos2 = v2.pos() + v2.get_center()
                delta = pos1 - pos2
                d = math.hypot(delta.x(), delta.y())
                if d < 1:
                    d = 1
                # Force magnitude ~ 1/d.
                rep = k_repulsion / d
                # Normalize delta.
                nx_val = delta.x() / d
                ny_val = delta.y() / d
                force = QPointF(rep * nx_val, rep * ny_val)
                v1.force = v1.force + force
                v2.force = v2.force - force

        # Attractive (spring) forces along edges.
        for edge in self.edges:
            v1 = edge.vertex1
            v2 = edge.vertex2
            pos1 = v1.pos() + v1.get_center()
            pos2 = v2.pos() + v2.get_center()
            delta = pos1 - pos2
            d = math.hypot(delta.x(), delta.y())
            if d < 1:
                d = 1
            # Hooke's law: F = -k*(d - rest_length)
            attr = k_attraction * (d - rest_length)
            nx_val = delta.x() / d
            ny_val = delta.y() / d
            force = QPointF(attr * nx_val, attr * ny_val)
            # Attractive forces pull vertices together.
            v1.force = v1.force - force
            v2.force = v2.force + force

        # Update vertex velocities and positions.
        for v in self.vertices:
            acceleration = v.force  # mass = 1
            v.velocity = (v.velocity + acceleration * dt) * damping
            new_pos = v.pos() + v.velocity * dt
            v.setPos(new_pos)
