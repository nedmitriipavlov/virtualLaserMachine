from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, \
    QGraphicsSimpleTextItem, QHBoxLayout, QRadioButton, QGraphicsProxyWidget, \
    QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QStackedLayout, \
    QMainWindow
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QGuiApplication, QFont, \
    QTransform, QBrush
import sys


class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(QColor(24, 78, 119).rgb())

        self.grid_size = 25
        self.lastPos = None

        self.distance = 4

        self.axis_points = []

        self.timer = QTimer()
        # self.timer.setSingleShot(True)
        # self.timer.timeout.connect(self.update_grid)

        self.initial_hbar_val = self.horizontalScrollBar().value() - int(self.size().width() * 1.1)
        self.initial_vbar_val = self.verticalScrollBar().value() - int(self.size().height())
        self.horizontalScrollBar().valueChanged.connect(self.update_grid)
        self.verticalScrollBar().valueChanged.connect(self.update_grid)

    def mouseReleaseEvent(self, event):
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastPos = event.pos()
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.pos() - self.lastPos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.lastPos = event.pos()
            # self.timer.start(1)

    def wheelEvent(self, event):
        self.update_grid()

    def draw_grid(self, visible_rect):
        """
        visible_rect is
        """
        self.scene().clear()

        # Distract/subtract certain number of pixels for rectangle to prevent looking at grid's borders
        extended_rect = visible_rect.adjusted(-self.grid_size, -self.grid_size, self.grid_size, self.grid_size)

        color = QColor(52, 160, 164).rgb()

        # Draw a grid
        for x in range(int(extended_rect.left()) - int(extended_rect.left()) % self.grid_size,
                       int(extended_rect.right()), self.grid_size):
            num = abs(x // self.grid_size)
            if x == 0:
                pen = QPen(color, int(8))
            elif not x // self.grid_size % 10:
                pen = QPen(color, int(1.5))
            else:
                pen = QPen(color, 0.5)

            self.scene().addLine(x, int(extended_rect.top()), x, int(extended_rect.bottom()), pen)
            pen.setColor(color)

        for y in range(int(extended_rect.top()) - int(extended_rect.top()) % self.grid_size,
                       int(extended_rect.bottom()), self.grid_size):
            num = abs(y // self.grid_size)
            if y == 0:
                pen = QPen(color, int(8))
            elif not y // self.grid_size % 10:
                pen = QPen(color, int(1.5))
            else:
                pen = QPen(color, 0.5)
            self.scene().addLine(int(extended_rect.left()), y, int(extended_rect.right()), y, pen)
            pen.setColor(color)



    def update_grid(self):
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        self.draw_grid(visible_rect)

    def get_to_back(self):
        self.horizontalScrollBar().setValue(self.initial_hbar_val)
        self.verticalScrollBar().setValue(self.initial_vbar_val)

    def resizeEvent(self, event):
        self.update_grid()
        super().resizeEvent(event)


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.center_of_screen = QApplication.primaryScreen().geometry().center()
        self.center_of_window = self.rect().center()
        self.center = self.center_of_screen - self.center_of_window

        self.setGeometry(900, 600, self.center.x(), self.center.y())
        self.grid = GraphicsView()

        self.button = QPushButton('get back')
        self.button.clicked.connect(self.grid.get_to_back)
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.grid)
        self.setLayout(layout)


app = QApplication(sys.argv)
widget = Widget()
widget.show()
app.exec()
