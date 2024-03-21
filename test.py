import sys
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen

class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setScene(QGraphicsScene())
        self.setMouseTracking(True)
        self.last_mouse_pos = None
        self.grid_size = 50
        self.draw_grid()

    def draw_grid(self):
        visible_rect = self.mapToScene(self.rect()).boundingRect()
        x_min = int(visible_rect.left()) // self.grid_size * self.grid_size
        x_max = int(visible_rect.right()) // self.grid_size * self.grid_size
        y_min = int(visible_rect.top()) // self.grid_size * self.grid_size
        y_max = int(visible_rect.bottom()) // self.grid_size * self.grid_size

        grid_pen = QPen(Qt.GlobalColor.lightGray, 0.5)
        for x in range(x_min, x_max + self.grid_size, self.grid_size):
            for y in range(y_min, y_max + self.grid_size, self.grid_size):
                self.scene().addRect(x, y, self.grid_size, self.grid_size, grid_pen)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.translate(delta.x(), delta.y())
            self.last_mouse_pos = event.pos()
            self.draw_grid()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = GraphicsView()
    view.show()
    sys.exit(app.exec())
