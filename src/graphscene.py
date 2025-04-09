from PyQt5.QtWidgets import QGraphicsScene
from vertex import Vertex
from edge import Edge

class GraphScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices = []
        self.edges = []
        self.new_edge_start = None

    def add_vertex(self, x, y):
        # Create and add a new vertex to the scene.
        vertex = Vertex(x, y)
        self.addItem(vertex)
        self.vertices.append(vertex)
        return vertex

    def add_edge(self, vertex1, vertex2):
        # Create and add a new edge between two vertices.
        edge = Edge(vertex1, vertex2)
        self.addItem(edge)
        self.edges.append(edge)
        return edge

    def mousePressEvent(self, event):
        # If click on empty space, add a vertex; if clicking on a vertex, record it as a start for an edge.
        clicked_items = self.items(event.scenePos())
        if not clicked_items:
            self.add_vertex(event.scenePos().x(), event.scenePos().y())
        else:
            for item in clicked_items:
                # Check if the item has a get_center method, indicating that it's a vertex.
                if hasattr(item, 'get_center'):
                    self.new_edge_start = item
                    break
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # If an edge creation was initiated and the mouse is released over a different vertex, add an edge.
        if self.new_edge_start:
            released_items = self.items(event.scenePos())
            for item in released_items:
                if hasattr(item, 'get_center') and item is not self.new_edge_start:
                    self.add_edge(self.new_edge_start, item)
                    break
        self.new_edge_start = None
        super().mouseReleaseEvent(event)

    def update_edges(self):
        # Update all edges to reflect current positions of the vertices.
        for edge in self.edges:
            edge.update_position()
