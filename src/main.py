import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QToolBar, QAction,
    QLabel, QDialog, QVBoxLayout, QTextEdit, QMessageBox
)
from PyQt5.QtCore import QTimer, QEvent
from PyQt5.QtGui import QPainter
from graphscene import GraphScene
from vertex import Vertex
from edge import Edge
import graph_analysis as ga

class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GraphCraft")

        self.scene = GraphScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background-color: #333333;")
        self.view.setStyleSheet("background-color: #222222; border: none;")

        self.statusBar().showMessage(self._status_text())
        self.statusBar().setStyleSheet("color: white; background-color: #333333;")

        toolbar = QToolBar("Main Toolbar")
        toolbar.setStyleSheet("background-color: #444444; color: white;")
        self.addToolBar(toolbar)

        self._setup_toolbar(toolbar)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(30)
        self.scene.installEventFilter(self)

    def _setup_toolbar(self, toolbar):
        actions = [
            ("Delete Vertex", self.delete_vertex),
            ("Delete Edge", self.delete_edge),
            ("Clear Scene", self.clear_scene),
            ("Pretty Layout", self.pretty_layout),
            ("Cartesian Product", self.cartesian_product),
            ("Chromatic Polynomial", self.show_chromatic_polynomial),
            ("Run Dijkstra", self.run_dijkstra),
            ("Find MST", self.find_mst),
            ("Find Max Flow", self.find_max_flow),
        ]

        for name, func in actions:
            act = QAction(name, self)
            act.triggered.connect(func)
            toolbar.addAction(act)

        self.directed_mode = False
        self.dir_label = QLabel("Directed: OFF")
        self.dir_label.setStyleSheet("color:white; margin-right:8px;")
        toolbar.addWidget(self.dir_label)
        act = QAction("Toggle Directed", self)
        act.triggered.connect(self.toggle_directed_mode)
        toolbar.addAction(act)

        self.physics_enabled = True
        self.phys_label = QLabel("Physics: ON")
        self.phys_label.setStyleSheet("color:white; margin-right:8px;")
        toolbar.addWidget(self.phys_label)
        act = QAction("Toggle Physics", self)
        act.triggered.connect(self.toggle_physics)
        toolbar.addAction(act)

        self.deg_act = QAction("Show Degrees", self, checkable=True)
        self.deg_act.triggered.connect(self.toggle_degrees)
        toolbar.addAction(self.deg_act)

        self.br_act = QAction("Highlight Bridges", self, checkable=True)
        self.br_act.triggered.connect(self.toggle_bridges)
        toolbar.addAction(self.br_act)

        self.comp_act = QAction("Show Components", self, checkable=True)
        self.comp_act.triggered.connect(self.toggle_components)
        toolbar.addAction(self.comp_act)

        self.bip_act = QAction("Show Bipartite", self, checkable=True)
        self.bip_act.triggered.connect(self.toggle_bipartite)
        toolbar.addAction(self.bip_act)

        act = QAction("Analyze Graph", self)
        act.triggered.connect(self.analyze_graph)
        toolbar.addAction(act)

    def _status_text(self):
        return f"Vertices: {len(self.scene.vertices)} | Edges: {len(self.scene.edges)}"

    def delete_vertex(self):
        for item in list(self.scene.selectedItems()):
            if isinstance(item, Vertex):
                for e in [e for e in self.scene.edges if e.vertex1 == item or e.vertex2 == item]:
                    self.scene.removeItem(e)
                self.scene.edges = [e for e in self.scene.edges if e.vertex1 != item and e.vertex2 != item]
                self.scene.removeItem(item)
                self.scene.vertices.remove(item)
                if self.scene.edge_source == item:
                    self.scene.edge_source = None
        self.statusBar().showMessage(self._status_text())

    def delete_edge(self):
        for item in list(self.scene.selectedItems()):
            if isinstance(item, Edge):
                self.scene.removeItem(item)
                self.scene.edges.remove(item)
        self.statusBar().showMessage(self._status_text())

    def clear_scene(self):
        self.scene.clear_scene()
        self.statusBar().showMessage(self._status_text())

    def pretty_layout(self):
        self.scene.pretty_layout()

    def cartesian_product(self):
        self.scene.cartesian_product()
        self.statusBar().showMessage(self._status_text())

    def show_chromatic_polynomial(self):
        poly = self.scene.chromatic_polynomial()
        text = "\n".join([f"{k} colors: {v} valid colorings" for k, v in poly.items()])
        QMessageBox.information(self, "Chromatic Polynomial", text)

    def run_dijkstra(self):
        self.scene.run_dijkstra()

    def find_mst(self):
        self.scene.find_mst()

    def find_max_flow(self):
        self.scene.find_max_flow()

    def toggle_directed_mode(self):
        self.directed_mode = not self.directed_mode
        self.dir_label.setText(f"Directed: {'ON' if self.directed_mode else 'OFF'}")
        self.scene.directed_mode = self.directed_mode

    def toggle_physics(self):
        self.physics_enabled = not self.physics_enabled
        self.phys_label.setText(f"Physics: {'ON' if self.physics_enabled else 'OFF'}")

    def toggle_degrees(self, checked):
        if checked:
            self.scene.label_degrees()
        else:
            self.scene.clear_labels()

    def toggle_bridges(self, checked):
        if checked:
            self.scene.highlight_bridges()
        else:
            self.scene.clear_edge_highlights()

    def toggle_components(self, checked):
        if checked:
            self.scene.color_by_component()
        else:
            self.scene.reset_vertex_colors()

    def toggle_bipartite(self, checked):
        if checked:
            ok = self.scene.color_by_bipartite()
            if not ok:
                QMessageBox.information(self, "Bipartite", "Graph is not bipartite.")
                self.bip_act.setChecked(False)
        else:
            self.scene.reset_vertex_colors()

    def update_simulation(self):
        dt = 0.03
        if self.physics_enabled:
            self.scene.update_physics(dt)
        self.scene.update_edges()
        self.statusBar().showMessage(self._status_text())

    def analyze_graph(self):
        G = ga.build_graph(self.scene)
        info = ga.get_graph_info(G)
        text = ga.format_info(info)

        dlg = QDialog(self)
        dlg.setWindowTitle("Graph Analysis")
        dlg.resize(600, 400)

        layout = QVBoxLayout(dlg)
        te = QTextEdit(dlg)
        te.setReadOnly(True)
        te.setPlainText(text)
        te.setStyleSheet("background-color: #222222; color: white; font-family: Consolas; font-size: 12pt;")
        layout.addWidget(te)

        dlg.setStyleSheet("background-color: #333333;")
        dlg.exec_()

    def eventFilter(self, source, event):
        if event.type() in (QEvent.GraphicsSceneMouseMove, QEvent.GraphicsSceneMouseRelease):
            self.scene.update_edges()
        return super().eventFilter(source, event)

def main():
    app = QApplication(sys.argv)
    w = GraphWindow()
    w.resize(1000, 800)
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
