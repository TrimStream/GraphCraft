# edge.py
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt5.QtGui import QPainterPath, QPen, QColor, QPolygonF, QPainterPathStroker
from PyQt5.QtCore import QPointF, Qt
import math

class Edge(QGraphicsPathItem):
    def __init__(self, v1, v2, directed=False):
        super().__init__()
        self.vertex1 = v1
        self.vertex2 = v2
        self.directed = directed

        # Make the edge selectable with left‐click
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(Qt.LeftButton)

        # Thicker visible line for clarity
        pen = QPen(QColor('black'), 6)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)

        self.update_position()

    def update_position(self):
        path = QPainterPath()
        c1 = self.vertex1.pos() + self.vertex1.get_center()
        c2 = self.vertex2.pos() + self.vertex2.get_center()

        if self.vertex1 is self.vertex2:
            # Draw a loop for self‐edge
            off = self.vertex1.radius
            path.addEllipse(
                c1.x() + off,
                c1.y() - off,
                self.vertex1.radius,
                self.vertex1.radius
            )
        else:
            path.moveTo(c1)
            path.lineTo(c2)
            if self.directed:
                self._add_arrow(path, c1, c2)

        self.setPath(path)

    def shape(self):
        """
        Return a widened stroke for hit‐testing, making selection easier.
        """
        stroker = QPainterPathStroker()
        stroker.setWidth(14)  # hit area 14px wide
        return stroker.createStroke(self.path())

    def _add_arrow(self, path, start, end):
        vec = end - start
        ang = math.atan2(vec.y(), vec.x())
        sz = 10
        # build triangle arrowhead
        p1 = end
        p2 = end - QPointF(
            sz * math.cos(ang - math.pi/6),
            sz * math.sin(ang - math.pi/6)
        )
        p3 = end - QPointF(
            sz * math.cos(ang + math.pi/6),
            sz * math.sin(ang + math.pi/6)
        )
        path.addPolygon(QPolygonF([p1, p2, p3]))
