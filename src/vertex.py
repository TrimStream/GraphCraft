# vertex.py
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsDropShadowEffect
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QBrush, QRadialGradient, QColor


class Vertex(QGraphicsEllipseItem):
    def __init__(self, x, y, radius=20):
        # Center the vertex at (x,y)
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius)
        self.radius = radius

        # Use a fixed blue gradient for all vertices.
        gradient = QRadialGradient(radius, radius, radius)
        gradient.setColorAt(0, QColor("#add8e6"))  # light blue
        gradient.setColorAt(1, QColor("#0000ff"))  # blue
        self.setBrush(QBrush(gradient))

        self.setFlags(QGraphicsEllipseItem.ItemIsMovable | QGraphicsEllipseItem.ItemIsSelectable)

        # Drop shadow for depth.
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(4, 4)
        self.setGraphicsEffect(shadow)

        self.label_item = None  # Label can be set via set_label() later.

        # Physics attributes for simulation.
        self.velocity = QPointF(0, 0)
        self.force = QPointF(0, 0)

    def get_center(self):
        rect = self.rect()
        return QPointF(rect.x() + rect.width() / 2,
                       rect.y() + rect.height() / 2)

    def set_color(self, color):
        self.setBrush(QBrush(color))

    def set_label(self, text):
        if self.label_item is None:
            self.label_item = QGraphicsTextItem(text, parent=self)
            center = self.get_center()
            # Position the label below the vertex.
            self.label_item.setPos(center.x() - self.radius, center.y() + self.radius)
        else:
            self.label_item.setPlainText(text)
