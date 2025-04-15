# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QToolBar, QAction, QLabel
from PyQt5.QtCore import QTimer, QEvent
from PyQt5.QtGui import QPainter, QFont
from graphscene import GraphScene


class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GraphCraft")

        # Create the scene and view.
        self.scene = GraphScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # Enable anti-aliasing for smoother rendering.
        self.view.setRenderHint(QPainter.Antialiasing)

        # Set styles for a modern, colorful look.
        self.setStyleSheet("background-color: #333333;")
        self.view.setStyleSheet("background-color: #222222; border: none;")

        # Create a toolbar with a dark style.
        toolbar = QToolBar("Main Toolbar")
        toolbar.setStyleSheet("background-color: #444444; color: white;")
        self.addToolBar(toolbar)

        # Label indicating physics state.
        self.physics_enabled = True
        self.physics_label = QLabel("Physics: ON")
        self.physics_label.setStyleSheet("color: white; font-weight: bold; margin-right: 10px;")
        self.physics_label.setFont(QFont("Arial", 12))
        toolbar.addWidget(self.physics_label)

        # Action to toggle physics.
        physics_action = QAction("Toggle Physics", self)
        physics_action.triggered.connect(self.toggle_physics)
        toolbar.addAction(physics_action)

        # Timer for updating the simulation.
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(30)  # Approximately 33 FPS (30ms interval)
        self.scene.installEventFilter(self)

    def toggle_physics(self):
        self.physics_enabled = not self.physics_enabled
        self.physics_label.setText("Physics: ON" if self.physics_enabled else "Physics: OFF")
        print("Physics enabled:", self.physics_enabled)

    def update_simulation(self):
        dt = 0.03  # Time step in seconds.
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
    window.resize(1000, 800)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
