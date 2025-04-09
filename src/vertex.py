from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtCore import QPointF, Qt   # Import Qt from QtCore
from PyQt5.QtGui import QBrush

class Vertex(QGraphicsEllipseItem):
    def __init__(self, x, y, radius=20):
        # Create the circle so that (x, y) is the center of the vertex.
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius)
        self.setBrush(QBrush(Qt.blue))
        self.setFlags(QGraphicsEllipseItem.ItemIsMovable | QGraphicsEllipseItem.ItemIsSelectable)
        self.radius = radius

    def get_center(self):
        # Returns the center point of the vertex.
        rect = self.rect()
        return QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)
