from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, \
    QGraphicsSimpleTextItem, QHBoxLayout, QRadioButton, QGraphicsProxyWidget, \
    QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QStackedLayout, \
    QMainWindow
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QGuiApplication, QFont, \
    QTransform, QBrush
import sys


class Widget(QWidget):
    def __init__(self, view):
        super().__init__()
        self.setWindowTitle('Virtual Laser Machine')
        self.layout = QVBoxLayout(self)
        self.view = view
        self.layout.addWidget(self.view, stretch=6)
        self.resize(1400, 1000)

        self.new_window_flag = False
        self.ready_to_draw = False
        self.speed_value = 1
        self.current_pos = 0

        self.space_manager()
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.move_to_start_def)
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.return_to_null_def)
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.drawing_lines_def)

        self.center()

    def center(self):
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        center_point = screen_geometry.center()

        self.move(center_point - self.rect().center())

    def space_manager(self):
        self.space = QVBoxLayout()
        self.rows = QHBoxLayout()

        self.agreement_row = QVBoxLayout()
        agreement = QRadioButton('Setting points')
        agreement.setChecked(False)
        agreement.toggled.connect(self.agreement)

        self.stacked_layout = QStackedLayout()
        self.agree_layout = QVBoxLayout()

        coordinates_label = QLabel('Set the coordinates')
        self.coordinates = QLineEdit()
        self.coordinates.setPlaceholderText('2, 5')
        self.coordinates_send = QPushButton('Set the coordinates')
        self.coordinates_send.clicked.connect(self.save_coordinates)

        label_speed = QLabel('Set speed')
        self.speed = QLineEdit()
        self.speed.setPlaceholderText('1')
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

        self.connect_points = QPushButton('Connect the points')
        self.connect_points.setChecked(False)
        self.connect_points.clicked.connect(self.connect_points_def)
        self.middle_row.addWidget(self.connect_points)

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
        machine_mode.clicked.connect(self.machine_mode_def)
        self.modes_row.addWidget(machine_mode)

        self.rows.addLayout(self.modes_row, stretch=1)

        self.space.addLayout(self.rows, stretch=6)

        self.message_text = 'GTA VI alpha'
        self.message_space = QVBoxLayout()
        self.message_space.addWidget(QLabel(self.message_text))

        self.space.addLayout(self.message_space, stretch=1)

        self.layout.addLayout(self.space, stretch=1)

    def drawing(self, checked):
        self.set_message_text(
            'If you want to see all the points in machine mode, please, set a convenient zoom and position')
        return setattr(self.view, 'point_drawing_enabled', checked)

    def set_message_text(self, text):
        self.message_text = text
        self.message_space.itemAt(0).widget().setText(self.message_text)

    def machine_mode_def(self):
        self.machine_view = self.view.working_view
        if not self.new_window_flag:
            self.new_window = QMainWindow()
            self.new_window.central_widget = QWidget()
            self.new_window.setCentralWidget(self.new_window.central_widget)
            self.new_window.layout = QVBoxLayout()

            self.new_window.layout.addWidget(self.machine_view)

            self.new_window.new_rows = QHBoxLayout()

            self.move_to_start = QPushButton('Move laser to first point')
            self.move_to_start.setChecked(False)
            self.move_to_start.clicked.connect(self.start_move_to_start_def)
            self.new_window.new_rows.addWidget(self.move_to_start)

            self.return_to_null = QPushButton('Return laser to (0, 0)')
            self.return_to_null.setChecked(False)
            self.return_to_null.clicked.connect(self.start_return_to_null_def)
            self.new_window.new_rows.addWidget(self.return_to_null)

            self.drawing_lines = QPushButton('Draw lines')
            self.drawing_lines.setChecked(False)
            self.drawing_lines.clicked.connect(self.start_drawing_lines_def)
            self.new_window.new_rows.addWidget(self.drawing_lines)

            self.new_window.layout.addLayout(self.new_window.new_rows)
            self.new_window.central_widget.setLayout(self.new_window.layout)

            self.new_window.setWindowTitle('Working Machine')

            self.new_window_flag = True
        self.view.machine_mode_flag = True

        if len(self.view.points):
            self.machine_view.centerOn(0, 0)

        self.view.update_grid()

        if self.new_window.isVisible():
            self.set_message_text('Machine mode window is shown!')
        else:
            self.view.machine_mode_flag = False
            self.set_message_text(
                'Такую игру будут делать около 50-ти лет, нужны будут миллиарды долларов, что бы воссоздать это!')

        self.new_window.show()

    def laser_off_moving(self, p1, p2, timer):
        self.view.working_space.removeItem(self.view.laser_pos)
        dx = (p2.x() - p1.x())
        dy = (p2.y() - p1.y())
        total_length = ((dx ** 2) + (dy ** 2)) ** 0.5
        increment = total_length / 100
        if self.current_progress < total_length:
            new_point = QPointF(p1.x() + dx * self.current_progress / total_length,
                                p1.y() + dy * self.current_progress / total_length)
            if self.current_progress > 0:
                self.view.working_space.removeItem(self.view.laser_pos)
            self.view.laser_pos = self.view.working_space.addEllipse(
                new_point.x(), new_point.y(),
                6 / self.view.scale_factor, 6 / self.view.scale_factor,
                QPen(self.view.laser_off_color), QBrush(self.view.laser_off_color))
            self.current_progress += increment
        else:
            timer.stop()
        self.view.update_grid()

    def laser_on_moving(self, points, timer):
        if self.current_pos != len(points) - 1:
            p1 = points[self.current_pos]
            p2 = points[self.current_pos + 1]
            dx = (p2.x() - p1.x())
            dy = (p2.y() - p1.y())
            total_length = ((dx ** 2) + (dy ** 2)) ** 0.5
            increment = total_length / 100
            if self.current_progress < total_length:
                self.new_point = QPointF(p1.x() + dx * self.current_progress / total_length,
                                         p1.y() + dy * self.current_progress / total_length)
                if self.current_progress > 0:
                    self.view.working_space.removeItem(self.view.laser_pos)
                    self.view.working_space.removeItem(self.view.line_item)
                self.view.laser_pos = self.view.working_space.addEllipse(
                    self.new_point.x(), self.new_point.y(),
                    6 / self.view.scale_factor, 6 / self.view.scale_factor,
                    QPen(self.view.laser_on_color), QBrush(self.view.laser_on_color))
                self.view.line_item = self.view.working_space.addLine(p1.x(), p1.y(),
                                                                      self.new_point.x(), self.new_point.y(),
                                                                      QPen(self.view.laser_color))
                self.current_progress += increment
            else:
                if self.current_pos == len(points) - 1:
                    print(1)
                    self.view.working_space.removeItem(self.view.laser_pos)
                    self.view.laser_pos = self.view.working_space.addEllipse(
                        self.new_point.x(), self.new_point.y(),
                        6 / self.view.scale_factor, 6 / self.view.scale_factor,
                        QPen(self.view.laser_off_color), QBrush(self.view.laser_off_color))
                    self.timer.stop()
                self.current_progress = 0
                self.current_pos += 1
            self.view.update_grid()

    def start_move_to_start_def(self):
        self.current_progress = 0
        self.timer.start(int(1000 / self.view.speed_value))

    def move_to_start_def(self):
        if not len(self.view.points):
            self.set_message_text('Please, set the first point for processing')
        else:
            self.view.flag_move_to_start = True
            if self.view.flag_move_to_start:
                self.laser_off_moving(QPoint(0, 0), self.view.points[0], self.timer)
                self.ready_to_draw = True

    def start_return_to_null_def(self):
        self.current_progress = 0
        self.timer1.start(int(1000 / self.view.speed_value))

    def return_to_null_def(self):
        if not len(self.view.points):
            self.set_message_text('Please, set the first point for processing')
        else:
            if self.ready_to_draw:
                self.laser_off_moving(self.view.points[0], QPoint(0, 0), self.timer1)
            else:
                self.laser_off_moving(self.view.points[-1], QPoint(0, 0), self.timer1)

    def start_drawing_lines_def(self):
        self.current_progress = 0
        self.timer2.start(int(1000 / self.view.speed_value))

    def drawing_lines_def(self):
        if not len(self.view.points):
            self.set_message_text('Please, set the first point for processing')
        else:
            self.laser_on_moving(self.view.points, self.timer2)
            self.ready_to_draw = False

    def connect_points_def(self):
        self.view.connect_points_flag = True
        self.view.update_grid()
        self.set_message_text('The points on display are connected!')

    def clear_drawings_def(self):
        self.view.points.clear()
        for p in self.view.working_points:
            self.view.working_space.removeItem(p)
        self.view.working_points.clear()
        self.view.update_grid()
        self.set_message_text('All drawings are deleted!')

    def return_to_start(self):
        self.view.resetTransform()
        self.view.lastPos = None
        self.view.scale_factor = 1
        self.view.order = 1
        self.view.last_s = 1
        self.view.centerOn(0, 0)
        self.view.flag_tocenter = True
        self.view.update_grid()
        self.set_message_text('Returned to start position!')

    def agreement(self, checked):
        i = 0 if checked else 1
        self.stacked_layout.setCurrentIndex(i)

    def save_speed(self):
        self.speed_value = int(self.speed.text())
        self.view.speed_value = self.speed_value * self.view.grid_size
        self.set_message_text('Value for speed is saved!')

    def save_coordinates(self):
        self.coordinates_value = self.coordinates.text()
        x, y = (int(i) * self.view.grid_size for i in self.coordinates_value.split(', '))
        self.view.points.append(QPointF(x, -y))
        self.view.update_grid()
        self.set_message_text('Value for coordinates is saved!')


class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(QColor(24, 78, 119).rgb())

        self.grid_size = 25
        self.speed_value = self.grid_size
        self.lastPos = None
        self.scale_factor = 1
        self.order = 1
        self.last_s = 1
        self.flag_tocenter = False
        self.connect_points_flag = False

        self.working_space = QGraphicsScene()
        self.working_view = QGraphicsView()

        self.working_grid_color = Qt.GlobalColor.darkYellow
        self.working_space_color = Qt.GlobalColor.black
        self.laser_color = Qt.GlobalColor.red
        self.laser_on_color = Qt.GlobalColor.green
        self.laser_off_color = Qt.GlobalColor.gray

        self.begin_point = QPoint(0, 0)
        self.laser_pos = None

        self.working_view.setBackgroundBrush(self.working_space_color)

        self.working_view.setScene(self.working_space)
        self.machine_mode_flag = False
        self.flag_move_to_start = False

        # Distance between marked squares
        self.distance = 4

        self.axis_points = []
        self.points = []
        self.working_points = []
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
            pen.setColor(self.working_grid_color)
            self.working_space.addLine(x, int(extended_rect.top()), x, int(extended_rect.bottom()), pen)
            pen.setColor(color)

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
            pen.setColor(self.working_grid_color)
            self.working_space.addLine(int(extended_rect.left()), y, int(extended_rect.right()), y, pen)
            pen.setColor(color)

            # Draw points
        points_color = Qt.GlobalColor.red
        line_pen = QPen(points_color)
        line_pen.setWidth(int(6 / s))
        if len(self.points):
            for point in self.points:
                self.scene().addEllipse(point.x(), point.y(), 6 / s, 6 / s, QPen(points_color),
                                        QBrush(points_color))
                p = self.working_space.addEllipse(point.x(), point.y(), 6 / s, 6 / s, QPen(points_color),
                                                  QBrush(points_color))
                self.working_points.append(p)

        if not self.laser_pos:
            self.laser_pos = self.working_space.addEllipse(self.begin_point.x(), self.begin_point.y(), 6 / s, 6 / s,
                                                           QPen(self.laser_off_color), QBrush(self.laser_off_color))

        if self.connect_points_flag:
            for i in range(len(self.points) - 1):
                line = self.scene().addLine(self.points[i].x(), self.points[i].y(),
                                            self.points[i + 1].x(), self.points[i + 1].y())
                line.setPen(line_pen)
            self.connect_points_flag = False

        self.last_s = s

    def wheelEvent(self, event):
        if not self.machine_mode_flag:
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
        if event.button() == Qt.MouseButton.LeftButton and not self.machine_mode_flag:
            self.lastPos = event.pos()
            if self.point_drawing_enabled:
                point = self.mapToScene(event.pos())
                self.points.append(point)
                self.update_grid()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.machine_mode_flag:
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
