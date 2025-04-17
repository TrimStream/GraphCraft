# edge.py
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QPainterPath, QPen, QColor, QPolygonF
from PyQt5.QtCore import QPointF, Qt
import math

class Edge(QGraphicsPathItem):
    def __init__(self, v1, v2, directed=False):
        super().__init__()
        self.vertex1 = v1
        self.vertex2 = v2
        self.directed = directed
        pen = QPen(QColor('black'), 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)
        self.update_position()

    def update_position(self):
        path = QPainterPath()
        c1 = self.vertex1.pos() + self.vertex1.get_center()
        c2 = self.vertex2.pos() + self.vertex2.get_center()
        if self.vertex1 is self.vertex2:
            off = self.vertex1.radius
            path.addEllipse(c1.x()+off, c1.y()-off,
                            self.vertex1.radius, self.vertex1.radius)
        else:
            path.moveTo(c1)
            path.lineTo(c2)
            if self.directed:
                self._add_arrow(path, c1, c2)
        self.setPath(path)

    def _add_arrow(self, path, s, e):
        vec = e - s
        ang = math.atan2(vec.y(), vec.x())
        sz = 10
        p1 = e
        p2 = e - QPointF(sz*math.cos(ang-math.pi/6),
                        sz*math.sin(ang-math.pi/6))
        p3 = e - QPointF(sz*math.cos(ang+math.pi/6),
                        sz*math.sin(ang+math.pi/6))
        path.addPolygon(QPolygonF([p1,p2,p3]))
