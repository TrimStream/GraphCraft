from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen

class Edge(QGraphicsLineItem):
    def __init__(self, vertex1, vertex2):
        # Store references to the connected vertices.
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        super().__init__()
        self.update_position()
        pen = QPen(Qt.black, 2)
        self.setPen(pen)

    def update_position(self):
        # Update the line coordinates to connect the centers of vertex1 and vertex2.
        center1 = self.vertex1.get_center()
        center2 = self.vertex2.get_center()
        self.setLine(center1.x(), center1.y(), center2.x(), center2.y())
