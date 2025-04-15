# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QToolBar, QAction
from PyQt5.QtCore import QTimer, QEvent
from PyQt5.QtGui import QPainter
from graphscene import GraphScene


class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GraphCraft")
        self.scene = GraphScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # Enable anti-aliasing for smoother rendering.
        self.view.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background-color: #f0f0f0;")
        self.view.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc;")

        # Create a toolbar.
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Toggle physics (force-directed simulation) button.
        self.physics_enabled = True
        physics_action = QAction("Toggle Physics", self)
        physics_action.triggered.connect(self.toggle_physics)
        toolbar.addAction(physics_action)

        # Timer to update physics simulation.
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(30)  # 30 ms interval (~33 FPS)
        self.scene.installEventFilter(self)

    def toggle_physics(self):
        self.physics_enabled = not self.physics_enabled

    def update_simulation(self):
        dt = 0.03  # time step in seconds
        if self.physics_enabled:
            self.scene.update_physics(dt)
        self.scene.update_edges()

    def eventFilter(self, source, event):
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
