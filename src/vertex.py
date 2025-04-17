# vertex.py
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QBrush, QRadialGradient, QColor

class Vertex(QGraphicsEllipseItem):
    def __init__(self, x, y, radius=20):
        super().__init__(x-radius, y-radius, 2*radius, 2*radius)
        self.radius = radius

        grad = QRadialGradient(radius, radius, radius)
        grad.setColorAt(0, QColor("#add8e6"))
        grad.setColorAt(1, QColor("#0000ff"))
        self.original_brush = QBrush(grad)
        self.setBrush(self.original_brush)

        self.setFlags(
            QGraphicsEllipseItem.ItemIsMovable |
            QGraphicsEllipseItem.ItemIsSelectable
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(4, 4)
        self.setGraphicsEffect(shadow)

        self.label_item = None
        self.velocity = QPointF(0,0)
        self.force    = QPointF(0,0)

    def get_center(self):
        r = self.rect()
        return QPointF(r.x()+r.width()/2, r.y()+r.height()/2)

    def set_color(self, color):
        self.setBrush(QBrush(color))

    def reset_color(self):
        self.setBrush(self.original_brush)

    def set_label(self, text):
        if not self.label_item:
            self.label_item = QGraphicsTextItem(text, parent=self)
            c = self.get_center()
            self.label_item.setPos(c.x()-self.radius, c.y()+self.radius)
        else:
            self.label_item.setPlainText(text)
