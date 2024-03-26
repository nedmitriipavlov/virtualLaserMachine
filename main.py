from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, \
    QGraphicsSimpleTextItem, QHBoxLayout, QRadioButton, QGraphicsProxyWidget, \
    QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QStackedLayout
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QGuiApplication, QFont, \
    QTransform, QBrush
import sys
import math


class Widget(QWidget):
    def __init__(self, view):
        super().__init__()
        self.setWindowTitle('Virtual Laser Machine')
        self.layout = QVBoxLayout(self)
        self.view = view
        self.layout.addWidget(self.view, stretch=6)
        self.resize(1400, 1000)

        self.space_manager()
        self.setLayout(self.layout)

        self.center()

    def center(self):
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        center_point = screen_geometry.center()

        self.move(center_point - self.rect().center())

    def space_manager(self):
        self.rows = QHBoxLayout()

        self.agreement_row = QVBoxLayout()
        agreement = QRadioButton('Setting points')
        agreement.setChecked(False)
        agreement.toggled.connect(self.agreement)

        self.stacked_layout = QStackedLayout()
        self.agree_layout = QVBoxLayout()

        coordinates_label = QLabel('Set the coordinates')
        self.coordinates = QLineEdit()
        self.coordinates.setPlaceholderText('1.2, 3.5')
        self.coordinates_send = QPushButton('Set the coordinates')
        self.coordinates_send.clicked.connect(self.save_coordinates)

        label_speed = QLabel('Set speed')
        self.speed = QLineEdit()
        self.speed.setPlaceholderText('1.5')
        self.speed_send = QPushButton('Set a speed')
        self.speed_send.clicked.connect(self.save_speed)

        self.agree_layout.addWidget(coordinates_label)
        self.agree_layout.addWidget(self.coordinates)
        self.agree_layout.addWidget(self.coordinates_send)

        self.agree_layout.addWidget(label_speed)
        self.agree_layout.addWidget(self.speed)
        self.agree_layout.addWidget(self.speed_send)

        container_agree_widget = QWidget()
        container_agree_widget.setLayout(self.agree_layout)

        self.stacked_layout.addWidget(container_agree_widget)
        self.stacked_layout.addWidget(QWidget())

        self.agreement_row.addWidget(agreement)
        self.agreement_row.addLayout(self.stacked_layout)

        # Make stacked_layout not visible
        self.agreement(False)

        self.rows.addLayout(self.agreement_row, stretch=1)

        self.middle_row = QVBoxLayout()

        self.to_start = QPushButton('Return to start position')
        self.to_start.setChecked(False)
        self.to_start.clicked.connect(self.return_to_start)
        self.middle_row.addWidget(self.to_start)

        self.clear_drawings = QPushButton('Clear all the drawings')
        self.clear_drawings.setChecked(False)
        self.clear_drawings.clicked.connect(self.clear_drawings_def)
        self.middle_row.addWidget(self.clear_drawings)

        self.rows.addLayout(self.middle_row, stretch=1)

        self.modes_row = QVBoxLayout()

        self.drawing_mode = QPushButton('Drawing mode')
        self.drawing_mode.setCheckable(True)
        self.drawing_mode.clicked.connect(self.drawing)
        self.modes_row.addWidget(self.drawing_mode)



        machine_mode = QPushButton('Machine mode')

        machine_mode.setChecked(False)
        machine_mode.clicked.connect(self.machine_mode)
        self.modes_row.addWidget(machine_mode)

        self.rows.addLayout(self.modes_row, stretch=1)

        self.layout.addLayout(self.rows, stretch=1)

    def drawing(self, checked):
        return setattr(self.view, 'point_drawing_enabled', checked)

    def clear_drawings_def(self):
        self.view.points.clear()
        self.view.update_grid()
        print(self.view.points)

    def return_to_start(self):
        self.view.resetTransform()
        self.view.lastPos = None
        self.view.scale_factor = 1
        self.view.order = 1
        self.view.last_s = 1
        self.view.centerOn(0, 0)
        self.view.flag_tocenter = True
        self.view.update_grid()

    def agreement(self, checked):
        i = 0 if checked else 1
        self.stacked_layout.setCurrentIndex(i)

    def save_speed(self):
        self.speed_value = self.speed.text()

    def save_coordinates(self):
        self.coordinates_value = self.coordinates.text()
        x, y = (int(i) * self.view.grid_size for i in self.coordinates_value.split(', '))
        self.view.points.append(QPointF(x, -y))

    def machine_mode(self):
        pass


class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(QColor(24, 78, 119).rgb())

        self.grid_size = 25
        self.lastPos = None
        self.scale_factor = 1
        self.order = 1
        self.last_s = 1
        self.flag_tocenter = False

        # Distance between marked squares
        self.distance = 4

        self.axis_points = []
        self.points = []
        self.point_drawing_enabled = False

        # Set timer for updating a grid

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.update_grid)

        # Determine anchor for zooming in point where we are
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Set drag mode for scrolling like in CAD programs
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def draw_grid(self, visible_rect):
        self.scene().clear()

        # Distract/subtract certain number of pixels for rectangle to prevent looking at grid's borders
        extended_rect = visible_rect.adjusted(-self.grid_size, -self.grid_size, self.grid_size, self.grid_size)

        s = self.scale_factor

        color = QColor(52, 160, 164).rgb()

        # Draw a grid
        for x in range(int(extended_rect.left()) - int(extended_rect.left()) % self.grid_size,
                       int(extended_rect.right()), self.grid_size):
            num = abs(x // self.grid_size)
            if x == 0:
                pen = QPen(color, int(8 / s))
            elif not x // self.grid_size % 10:
                pen = QPen(color, int(1.5 / s))
            else:
                pen = QPen(color, 0.5)
            if len(str(num)) > self.order and s < 1:
                self.order = len(str(num))
            if len(str(num)) > self.order and s <= self.last_s <= 1:
                self.order = len(str(num))
            elif len(str(num)) < self.order and self.last_s != s:
                self.order = len(str(num))
            if len(str(num)) >= self.order and not num % (self.distance ** len(str(num))):
                text = QGraphicsSimpleTextItem(str(num))
                text.setFont(QFont('Arial', int(15 / s)))
                text.setPos(x, 0)
                self.axis_points.append(text)
                self.scene().addItem(text)
            self.scene().addLine(x, int(extended_rect.top()), x, int(extended_rect.bottom()), pen)

        for y in range(int(extended_rect.top()) - int(extended_rect.top()) % self.grid_size,
                       int(extended_rect.bottom()), self.grid_size):
            num = abs(y // self.grid_size)
            if y == 0:
                pen = QPen(color, int(8 / s))
            elif not y // self.grid_size % 10:
                pen = QPen(color, int(1.5 / s))
            else:
                pen = QPen(color, 0.5)
            if len(str(num)) > self.order and s <= self.last_s <= 1:
                self.order = len(str(num))
            elif len(str(num)) < self.order and self.last_s != s:
                self.order = len(str(num))

            if len(str(num)) >= self.order and not num % (self.distance ** len(str(num))):
                text = QGraphicsSimpleTextItem(str(num))
                text.setFont(QFont('Arial', int(15 / s)))
                text.setPos(0, y)
                self.axis_points.append(text)
                self.scene().addItem(text)
            self.scene().addLine(int(extended_rect.left()), y, int(extended_rect.right()), y, pen)

            # Draw points
        points_color = Qt.GlobalColor.red
        if len(self.points):
            for point in self.points:
                self.scene().addEllipse(point.x(), point.y(), 4 / s, 4 / s, QPen(points_color),
                                        QBrush(points_color))
        self.last_s = s

    def wheelEvent(self, event):
        factor = 1.5  # zoom factor
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        if self.flag_tocenter:
            self.flag_tocenter = False
            self.scale_factor = 1
        else:
            self.scale_factor *= factor
        self.scale(factor, factor)
        self.update_grid()


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastPos = event.pos()
            if self.point_drawing_enabled:
                point = self.mapToScene(event.pos())
                self.points.append(point)
                self.update_grid()


    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if not self.flag_tocenter:
                delta = event.pos() - self.lastPos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.lastPos = event.pos()
                self.timer.start(1)
            else:
                self.lastPos = QPoint(0, 0)
                self.update_grid()
                self.timer.start(1)
                self.flag_tocenter = False

    def update_grid(self):
        if self.flag_tocenter:

            self.centerOn(0, 0)
            self.mapToScene(0, 0)
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        self.draw_grid(visible_rect)


    def resizeEvent(self, event):
        self.update_grid()
        super().resizeEvent(event)


app = QApplication(sys.argv)
widget = Widget(GraphicsView())
widget.show()
app.exec()
