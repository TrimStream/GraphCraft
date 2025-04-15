# graphscene.py
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt
from vertex import Vertex
from edge import Edge
import math
from PyQt5.QtCore import QPointF

class GraphScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices = []
        self.edges = []
        self.edge_source = None  # For storing the first vertex when creating an edge

    def add_vertex(self, x, y):
        vertex = Vertex(x, y)
        self.addItem(vertex)
        self.vertices.append(vertex)
        return vertex

    def add_edge(self, vertex1, vertex2):
        # Create an edge (parallel edges and loops are allowed).
        edge = Edge(vertex1, vertex2)
        self.addItem(edge)
        self.edges.append(edge)
        return edge

    def mousePressEvent(self, event):
        # Respond only to left mouse clicks.
        if event.button() == Qt.LeftButton:
            clicked_items = self.items(event.scenePos())
            vertex_clicked = None
            for item in clicked_items:
                if hasattr(item, 'get_center'):
                    vertex_clicked = item
                    break
            if vertex_clicked:
                if self.edge_source is None:
                    # Set this vertex as the starting vertex for an edge.
                    self.edge_source = vertex_clicked
                    vertex_clicked.setSelected(True)
                else:
                    # If a source was already set, connect it to the clicked vertex.
                    self.add_edge(self.edge_source, vertex_clicked)
                    self.edge_source = None  # Reset edge creation state.
            else:
                # If clicking on empty space, create a new vertex.
                self.edge_source = None
                self.add_vertex(event.scenePos().x(), event.scenePos().y())
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            # Delete selected vertices/edges.
            selected_items = self.selectedItems()
            for item in selected_items:
                if hasattr(item, 'get_center'):
                    # Remove connected edges first.
                    edges_to_remove = [edge for edge in self.edges if edge.vertex1 == item or edge.vertex2 == item]
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
        # Update all edge positions.
        for edge in self.edges:
            edge.update_position()

    def update_physics(self, dt):
        # Force-directed layout simulation.
        # Constants (tweak these for a visually pleasing effect)
        k_repulsion = 5000.0    # Strength of repulsive force between vertices.
        k_spring = 0.1          # Spring (attractive) constant for edges.
        rest_length = 100.0     # Desired edge length.
        damping = 0.85          # Damping factor to reduce velocity over time.

        # Reset forces on each vertex.
        for v in self.vertices:
            v.force = QPointF(0, 0)

        # Apply repulsive forces between every pair of vertices.
        n = len(self.vertices)
        for i in range(n):
            for j in range(i + 1, n):
                v1 = self.vertices[i]
                v2 = self.vertices[j]
                pos1 = v1.pos() + v1.get_center()
                pos2 = v2.pos() + v2.get_center()
                dx = pos1.x() - pos2.x()
                dy = pos1.y() - pos2.y()
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < 1:
                    distance = 1
                # Repulsive force magnitude (inverse-square law).
                force_magnitude = k_repulsion / (distance * distance)
                fx = force_magnitude * (dx / distance)
                fy = force_magnitude * (dy / distance)
                force_vector = QPointF(fx, fy)
                v1.force = v1.force + force_vector
                v2.force = v2.force - force_vector

        # Apply attractive (spring) forces along edges.
        for edge in self.edges:
            v1 = edge.vertex1
            v2 = edge.vertex2
            pos1 = v1.pos() + v1.get_center()
            pos2 = v2.pos() + v2.get_center()
            dx = pos1.x() - pos2.x()
            dy = pos1.y() - pos2.y()
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 1:
                distance = 1
            # Spring force: F = -k * (distance - rest_length)
            force_magnitude = -k_spring * (distance - rest_length)
            fx = force_magnitude * (dx / distance)
            fy = force_magnitude * (dy / distance)
            spring_force = QPointF(fx, fy)
            v1.force = v1.force + spring_force
            v2.force = v2.force - spring_force

        #
