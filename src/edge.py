# edge.py
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QPainterPath, QPen, QPolygonF
from PyQt5.QtCore import Qt, QPointF
import math

class Edge(QGraphicsPathItem):
    def __init__(self, vertex1, vertex2, directed=False):
        super().__init__()
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.directed = directed
        pen = QPen(Qt.black, 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)
        self.update_position()

    def update_position(self):
        path = QPainterPath()
        # Compute endpoints (scene positions + local center)
        center1 = self.vertex1.pos() + self.vertex1.get_center()
        center2 = self.vertex2.pos() + self.vertex2.get_center()
        if self.vertex1 == self.vertex2:
            # Loop: draw an ellipse offset from the vertex.
            offset = self.vertex1.radius
            x = center1.x() + offset
            y = center1.y() - offset
            path.addEllipse(x, y, self.vertex1.radius, self.vertex1.radius)
        else:
            path.moveTo(center1)
            path.lineTo(center2)
            if self.directed:
                self.add_arrowhead(path, center1, center2)
        self.setPath(path)

    def add_arrowhead(self, path, start, end):
        # Compute the arrowhead as a small triangle at the end.
        line_vec = end - start
        angle = math.atan2(line_vec.y(), line_vec.x())
        arrow_size = 10
        # Points for the triangle.
        p1 = end
        p2 = end - QPointF(arrow_size * math.cos(angle - math.pi/6),
                           arrow_size * math.sin(angle - math.pi/6))
        p3 = end - QPointF(arrow_size * math.cos(angle + math.pi/6),
                           arrow_size * math.sin(angle + math.pi/6))
        arrow_head = QPolygonF([p1, p2, p3])
        path.addPolygon(arrow_head)
