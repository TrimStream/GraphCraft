# edge.py
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QPainterPath, QPen
from PyQt5.QtCore import Qt

class Edge(QGraphicsPathItem):
    def __init__(self, vertex1, vertex2):
        super().__init__()
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        pen = QPen(Qt.black, 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)
        self.update_position()

    def update_position(self):
        path = QPainterPath()
        center1 = self.vertex1.pos() + self.vertex1.get_center()
        center2 = self.vertex2.pos() + self.vertex2.get_center()
        if self.vertex1 is self.vertex2:
            # Draw a loop: an ellipse offset from the vertex.
            offset = self.vertex1.radius
            x = center1.x() + offset
            y = center1.y() - offset
            path.addEllipse(x, y, self.vertex1.radius, self.vertex1.radius)
        else:
            path.moveTo(center1)
            path.lineTo(center2)
        self.setPath(path)
