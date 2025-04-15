# vertex.py
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsDropShadowEffect
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QBrush, QRadialGradient, QColor


class Vertex(QGraphicsEllipseItem):
    def __init__(self, x, y, radius=20):
        # Center the vertex on (x, y)
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius)
        self.radius = radius

        # Create a radial gradient for a polished look.
        gradient = QRadialGradient(radius, radius, radius)
        gradient.setColorAt(0, QColor("lightblue"))
        gradient.setColorAt(1, QColor("blue"))
        self.setBrush(QBrush(gradient))

        # Make the vertex movable and selectable.
        self.setFlags(QGraphicsEllipseItem.ItemIsMovable | QGraphicsEllipseItem.ItemIsSelectable)

        # Apply a drop shadow for depth.
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(3, 3)
        self.setGraphicsEffect(shadow)

        self.label_item = None  # For labeling

        # Physics attributes: velocity and force for the layout simulation.
        self.velocity = QPointF(0, 0)
        self.force = QPointF(0, 0)

    def get_center(self):
        # Returns the center of the ellipse in local coordinates.
        rect = self.rect()
        return QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)

    def set_color(self, color):
        self.setBrush(QBrush(color))

    def set_label(self, text):
        if self.label_item is None:
            self.label_item = QGraphicsTextItem(text, parent=self)
            center = self.get_center()
            # Position the label just below the vertex.
            self.label_item.setPos(center.x() - self.radius, center.y() + self.radius)
        else:
            self.label_item.setPlainText(text)
