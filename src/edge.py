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

        self.default_pen = QPen(QColor('black'), 2)
        self.default_pen.setCapStyle(Qt.RoundCap)
        self.default_pen.setJoinStyle(Qt.RoundJoin)

        self.user_pen = None   # User-set permanent pen
        self.temp_pen = None   # Temporary pen (e.g., for highlighting)

        self.setPen(self.default_pen)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(Qt.LeftButton)

        self.update_position()

    def update_position(self):
        path = QPainterPath()
        c1 = self.vertex1.pos() + self.vertex1.get_center()
        c2 = self.vertex2.pos() + self.vertex2.get_center()

        if self.vertex1 is self.vertex2:
            off = self.vertex1.radius
            path.addEllipse(c1.x() + off, c1.y() - off, self.vertex1.radius, self.vertex1.radius)
        else:
            path.moveTo(c1)
            path.lineTo(c2)
            if self.directed:
                self._add_arrow(path, c1, c2)

        self.setPath(path)

    def shape(self):
        stroker = QPainterPathStroker()
        stroker.setWidth(10)  # wider clickable area
        return stroker.createStroke(self.path())

    def set_color(self, color):
        """Set a permanent user color (right-click)."""
        self.user_pen = QPen(color, 2)
        self.user_pen.setCapStyle(Qt.RoundCap)
        self.user_pen.setJoinStyle(Qt.RoundJoin)
        self.update_pen()

    def set_temp_color(self, color):
        """Temporarily highlight the edge with a color (e.g., bridge)."""
        self.temp_pen = QPen(color, 2)
        self.temp_pen.setCapStyle(Qt.RoundCap)
        self.temp_pen.setJoinStyle(Qt.RoundJoin)
        self.update_pen()

    def reset_temp_color(self):
        """Remove temporary color and revert to user color or default."""
        self.temp_pen = None
        self.update_pen()

    def reset_color(self):
        """Fully reset to default black edge."""
        self.user_pen = None
        self.temp_pen = None
        self.setPen(self.default_pen)

    def update_pen(self):
        """Priority: temp_pen > user_pen > default_pen."""
        if self.temp_pen:
            self.setPen(self.temp_pen)
        elif self.user_pen:
            self.setPen(self.user_pen)
        else:
            self.setPen(self.default_pen)

    def _add_arrow(self, path, start, end):
        vec = end - start
        ang = math.atan2(vec.y(), vec.x())
        sz = 10
        p1 = end
        p2 = end - QPointF(sz * math.cos(ang - math.pi/6), sz * math.sin(ang - math.pi/6))
        p3 = end - QPointF(sz * math.cos(ang + math.pi/6), sz * math.sin(ang + math.pi/6))
        path.addPolygon(QPolygonF([p1, p2, p3]))
