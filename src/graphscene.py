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
        self.edge_source = None  # For storing the source vertex when creating an edge

    def add_vertex(self, x, y):
        vertex = Vertex(x, y)
        self.addItem(vertex)
        self.vertices.append(vertex)
        return vertex

    def add_edge(self, vertex1, vertex2):
        # Create an edge (allowing loops and parallel edges).
        edge = Edge(vertex1, vertex2)
        self.addItem(edge)
        self.edges.append(edge)
        return edge

    def mousePressEvent(self, event):
        # Only respond to left mouse clicks.
        if event.button() == Qt.LeftButton:
            clicked_items = self.items(event.scenePos())
            vertex_clicked = None
            for item in clicked_items:
                if hasattr(item, 'get_center'):
                    vertex_clicked = item
                    break
            if vertex_clicked:
                if self.edge_source is None:
                    # First vertex clicked becomes the source.
                    self.edge_source = vertex_clicked
                    vertex_clicked.setSelected(True)
                else:
                    # Second vertex clicked completes the edge.
                    self.add_edge(self.edge_source, vertex_clicked)
                    self.edge_source = None
            else:
                # If no vertex was clicked, create a new vertex.
                self.edge_source = None
                self.add_vertex(event.scenePos().x(), event.scenePos().y())
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_items = self.selectedItems()
            for item in selected_items:
                if hasattr(item, 'get_center'):
                    # Remove edges connected to this vertex.
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
        # Update positions for all edges.
        for edge in self.edges:
            edge.update_position()

    def update_physics(self, dt):
        """
        Update vertex positions via a force-directed layout:
         - Each vertex repels every other vertex: force ~ constant / distance.
         - Each edge acts like a spring: force ~ constant * (d - rest_length).
        """
        rest_length = 100.0          # Desired edge length
        k_repulsion = 10000.0        # Constant for repulsive force; try adjusting if too strong/weak.
        k_attraction = 0.5           # Spring (attractive) constant for edges.
        damping = 0.9                # Damping factor to smooth motion

        # Reset forces for all vertices.
        for v in self.vertices:
            v.force = QPointF(0, 0)

        # Compute repulsive forces between each pair of vertices.
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
                    d = 1  # Avoid division by zero
                # Repulsive force magnitude decreases as 1/d.
                rep_force = (k_repulsion / d) * (delta / d)
                v1.force = v1.force + rep_force
                v2.force = v2.force - rep_force

        # Compute attractive (spring) forces along edges.
        for edge in self.edges:
            v1 = edge.vertex1
            v2 = edge.vertex2
            pos1 = v1.pos() + v1.get_center()
            pos2 = v2.pos() + v2.get_center()
            delta = pos1 - pos2
            d = math.hypot(delta.x(), delta.y())
            if d < 1:
                d = 1
            # Attractive force tries to bring d closer to rest_length.
            attr_force = k_attraction * (d - rest_length) * (delta / d)
            v1.force = v1.force - attr_force
            v2.force = v2.force + attr_force

        # Update vertices' velocities and positions.
        for v in self.vertices:
            acceleration = v.force  # Assuming mass = 1.
            v.velocity = (v.velocity + acceleration * dt) * damping
            new_pos = v.pos() + v.velocity * dt
            v.setPos(new_pos)
