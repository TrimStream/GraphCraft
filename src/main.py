# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QToolBar, QAction, QLabel, QMessageBox
from PyQt5.QtCore import QTimer, QEvent
from PyQt5.QtGui import QPainter, QFont
from graphscene import GraphScene
import graph_analysis as ga


class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GraphCraft")

        # Create scene and view.
        self.scene = GraphScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # Enable anti-aliasing.
        self.view.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background-color: #333333;")
        self.view.setStyleSheet("background-color: #222222; border: none;")

        # Create a toolbar.
        toolbar = QToolBar("Main Toolbar")
        toolbar.setStyleSheet("background-color: #444444; color: white;")
        self.addToolBar(toolbar)

        # Physics state label.
        self.physics_enabled = True
        self.physics_label = QLabel("Physics: ON")
        self.physics_label.setStyleSheet("color: white; font-weight: bold; margin-right: 10px;")
        self.physics_label.setFont(QFont("Arial", 12))
        toolbar.addWidget(self.physics_label)

        # Toggle physics action.
        physics_action = QAction("Toggle Physics", self)
        physics_action.triggered.connect(self.toggle_physics)
        toolbar.addAction(physics_action)

        # Graph analysis action.
        analysis_action = QAction("Analyze Graph", self)
        analysis_action.triggered.connect(self.analyze_graph)
        toolbar.addAction(analysis_action)

        # Timer for simulation updates.
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(30)  # 30 ms interval ~33 FPS
        self.scene.installEventFilter(self)

    def toggle_physics(self):
        self.physics_enabled = not self.physics_enabled
        self.physics_label.setText("Physics: ON" if self.physics_enabled else "Physics: OFF")
        print("Physics enabled:", self.physics_enabled)

    def update_simulation(self):
        dt = 0.03  # time step (s)
        if self.physics_enabled:
            self.scene.update_physics(dt)
        self.scene.update_edges()

    def analyze_graph(self):
        info = ga.get_graph_info(self.scene)
        text = ga.format_info(info)
        # Display analysis info in a message box.
        msg = QMessageBox(self)
        msg.setWindowTitle("Graph Analysis")
        msg.setText(text)
        msg.setStyleSheet("QLabel{min-width: 500px;}")
        msg.exec_()

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
