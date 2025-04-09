import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView
from PyQt5.QtCore import QEvent
from graphscene import GraphScene

class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GraphCraft")
        self.scene = GraphScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.view.setMouseTracking(True)
        # Install an event filter on the scene to update edges on mouse movement.
        self.scene.installEventFilter(self)

    def eventFilter(self, source, event):
        # When the mouse moves or is released, update edge positions.
        if event.type() in (QEvent.GraphicsSceneMouseMove, QEvent.GraphicsSceneMouseRelease):
            self.scene.update_edges()
        return super().eventFilter(source, event)

def main():
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
