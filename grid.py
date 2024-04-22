from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, \
    QGraphicsSimpleTextItem, QHBoxLayout, QRadioButton, QGraphicsProxyWidget, \
    QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QStackedLayout, \
    QMainWindow
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QPoint, QRect, QSize
from PyQt6.QtGui import QPainter, QPen, QColor, QGuiApplication, QFont, \
    QTransform, QBrush

from itertools import chain


class Grid(QGraphicsView):

    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setBackgroundBrush(QColor(24, 78, 119).rgb())

        self.timer = QTimer()

        self.speed_val = 10
        self.distance = 5
        self.grid_size = 25
        self.lastPos = QPoint(0, 0)
        self.scale_factor = 1

        self.axis_points = []
        self.points = []
        self.image_points = []
        self.lines = []
        self.drawing_mode_flag = False
        self.draw_line_flag = False
        self.image_drawing_flag = False
        self.drawing_mode_times = 0
        self.last_num_of_drawn_lines = []

        self.start_hbar_val = -500
        self.start_vbar_val = -500

        self.horizontalScrollBar().valueChanged.connect(self.grid_update)
        self.verticalScrollBar().valueChanged.connect(self.grid_update)

    def grid_drawn(self, visible_rect):

        self.timer.start(50 + 800 * self.image_drawing_flag)
        if not self.image_drawing_flag:
            self.scene.clear()

        visible_rect = visible_rect.adjusted(-self.grid_size, -self.grid_size, self.grid_size, self.grid_size)

        color = QColor(52, 160, 164).rgb()

        def set_text(x_coord, y_coord, num):
            text = QGraphicsSimpleTextItem(str(num))
            text.setPen(Qt.GlobalColor.black)
            text.setBrush(Qt.GlobalColor.black)
            text.setFont(QFont('Arial', int(15 * self.scale_factor)))
            text.setPos(x_coord, y_coord)
            text.setZValue(1)
            self.axis_points.append(text)
            self.scene.addItem(text)

        order = 0

        for x in range(int(visible_rect.left()) - int(visible_rect.left()) % self.grid_size,
                       int(visible_rect.right()), self.grid_size):

            num = abs(x // self.grid_size)

            if x == 0:
                pen = QPen(color, int(5))
            elif not x // self.grid_size % 10:
                special_color = QColor(int(52 / self.scale_factor), int(160 / self.scale_factor),
                                       int(164 / self.scale_factor)).rgb()
                pen = QPen(special_color, int(1.5) ** 2)
            else:
                pen = QPen(color, int(0.5))

            if len(str(num)) > order:
                order = len(str(num))
            elif len(str(num)) < order:
                order = len(str(num))

            if not self.image_drawing_flag:
                if len(str(num)) >= order and not num % self.distance:
                    if self.scale_factor < 2:
                        set_text(x, 0, num)
                    elif not num % 2 * self.distance:
                        set_text(x, 0, num)

            self.scene.addLine(x, int(visible_rect.top()), x, int(visible_rect.bottom()), pen)

        order = 0

        for y in range(int(visible_rect.top()) - int(visible_rect.top()) % self.grid_size,
                       int(visible_rect.bottom()), self.grid_size):

            num = abs(y // self.grid_size)

            if y == 0:
                pen = QPen(color, int(5))
            elif not y // self.grid_size % 10:
                special_color = QColor(int(52 / self.scale_factor), int(160 / self.scale_factor),
                                       int(164 / self.scale_factor)).rgb()
                pen = QPen(special_color, int(1.5) ** 2)
            else:
                pen = QPen(color, int(0.5))

            if len(str(num)) > order:
                order = len(str(num))
            elif len(str(num)) < order:
                order = len(str(num))

            if not self.image_drawing_flag:
                if len(str(num)) >= order and not num % self.distance:
                    if self.scale_factor < 2:
                        set_text(0, y, num)
                    elif not num % 2 * self.distance:
                        set_text(0, y, num)

            self.scene.addLine(int(visible_rect.left()), y, int(visible_rect.right()), y, pen)

        points_color = Qt.GlobalColor.yellow
        line_pen = QPen(points_color)
        line_pen.setWidth(int(2))

        for k in range(self.drawing_mode_times):
            if self.draw_line_flag and len(self.points[k]) > 1:
                for i in range(self.last_num_of_drawn_lines[k] - 1, len(self.points[k]) - 1):
                    line = self.scene.addLine(self.points[k][i].x(), self.points[k][i].y(), self.points[k][i + 1].x(),
                                              self.points[k][i + 1].y(), line_pen)
                    line.setZValue(1)
                    if line not in list(chain(self.lines)):
                        self.lines.append(line)
                    self.last_num_of_drawn_lines[k] = len(self.lines)
                    self.draw_line_flag = False

            if len(self.points[k]):
                for point in self.points[k]:
                    self.scene.addEllipse(point.x() - 2, point.y() - 2, 6, 6, QPen(points_color), QBrush(points_color))
                for i in range(len(self.points[k]) - 1):
                    line = self.scene.addLine(self.points[k][i].x(), self.points[k][i].y(), self.points[k][i + 1].x(),
                                              self.points[k][i + 1].y(), line_pen)

        if self.image_drawing_flag:
            self.timer.stop()
            for line in self.lines:
                self.scene.addItem(line)

    def grid_update(self):
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        self.grid_drawn(visible_rect)

    def drawing_square(self, x, y):
        x = x * self.grid_size
        y = y * self.grid_size
        for i in range(y - 1, y - 1 - self.grid_size, -4):
            self.points.append([QPointF(x, i), QPointF(x - self.grid_size, i)])
            line = self.scene.addLine(x, i, x - self.grid_size, i, QPen(Qt.GlobalColor.yellow))
            self.lines.append(line)

    def image_drawing(self, matrix):
        x0, y0 = (-int(len(matrix[0]) / 2), int(len(matrix) / 2))
        for y in range(len(matrix)):
            for x in range(len(matrix[0])):
                if matrix[y][x]:
                    self.drawing_square(x0 + x, y0 - y)
        self.image_points.append(QPointF(x0, y0))
        self.image_points.append(QPointF(-x0, y0))
        self.image_points.append(QPointF(x0, -y0))
        self.image_points.append(QPointF(-x0, -y0))

    def get_to_back(self):
        self.get_to_initial = True
        self.horizontalScrollBar().setValue(self.start_hbar_val)
        self.verticalScrollBar().setValue(self.start_vbar_val)
        self.setTransform(QTransform.fromScale(1, 1))
        self.scale_factor = 1
        self.grid_update()

    def mouseReleaseEvent(self, event):
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def mousePressEvent(self, event):
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        if not self.drawing_mode_flag:
            if event.button() == Qt.MouseButton.LeftButton:
                self.lastPos = event.pos()
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        else:
            point = self.mapToScene(event.pos())
            self.points[self.drawing_mode_times-1].append(point)
            self.grid_update()

    def mouseMoveEvent(self, event):
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        if not self.drawing_mode_flag:
            if event.buttons() == Qt.MouseButton.LeftButton:
                delta = event.pos() - self.lastPos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.lastPos = event.pos()
        else:
            return

    def wheelEvent(self, event):
        factor = 1.1
        if event.angleDelta().y() > 0:
            factor = (1 / factor) ** 2
        else:
            factor *= factor
        if 0.35 <= self.scale_factor * factor < 3:
            self.scale_factor *= factor
            self.scale(self.scale_factor, self.scale_factor)
            self.setTransform(QTransform.fromScale(1 / self.scale_factor, 1 / self.scale_factor))
            self.grid_update()

    def resizeEvent(self, event):
        self.grid_update()
