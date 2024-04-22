from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, \
    QGraphicsSimpleTextItem, QHBoxLayout, QRadioButton, QGraphicsProxyWidget, \
    QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QStackedLayout, \
    QMainWindow
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QPoint, QRect, QSize
from PyQt6.QtGui import QPainter, QPen, QColor, QGuiApplication, QFont, \
    QTransform, QBrush

from itertools import chain


class MachineGrid(QGraphicsView):

    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self.speed_val = 10
        self.distance = 5
        self.grid_size = 25
        self.lastPos = None
        self.scale_factor = 1

        self.axis_points = []
        self.points = []
        self.lines = []
        self.line_item = None

        self.laser_off_flag = False
        self.laser_on_flag = False
        self.laser_stop_flag = False
        self.laser_is_ready = False
        self.laser_in_center = True
        self.new_point = None
        self.marked_point = self.scene.addEllipse(-2, -2, 6, 6,
                                                  QPen(Qt.GlobalColor.white), QBrush(Qt.GlobalColor.white))
        self.current_element = 0
        self.current_segment = 0
        self.current_progress = 0
        self.timer = QTimer()
        self.timer0 = QTimer()
        self.timer0.timeout.connect(self.move_to_start)
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.drawing_line)
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.move_to_finish)

        # self.timer3 = QTimer()
        # self.timer3.timeout.connect(self.draw_image)

        self.start_hbar_val = -500
        self.start_vbar_val = -500

    def grid_drawn(self, visible_rect):

        self.timer.start(50)
        visible_rect = visible_rect.adjusted(-self.grid_size, -self.grid_size, self.grid_size, self.grid_size)
        color = Qt.GlobalColor.darkYellow

        def set_text(x_coord, y_coord, num):
            text = QGraphicsSimpleTextItem(str(num))
            text.setPen(color)
            text.setBrush(color)
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

            if len(str(num)) >= order and not num % self.distance:
                if self.scale_factor < 2:
                    set_text(0, y, num)
                elif not num % 2 * self.distance:
                    set_text(0, y, num)

            self.scene.addLine(int(visible_rect.left()), y, int(visible_rect.right()), y, pen)

        points_color = Qt.GlobalColor.red
        line_pen = QPen(points_color)
        line_pen.setWidth(int(6))

        if not self.laser_off_flag and self.laser_in_center:
            self.marked_point = self.scene.addEllipse(-2, -2, 6, 6,
                                                      QPen(Qt.GlobalColor.white), QBrush(Qt.GlobalColor.white))
        if len(list(chain.from_iterable(self.points))):
            for point in chain.from_iterable(self.points):
                self.scene.addEllipse(point.x() - 2, point.y() - 2, 6, 6, QPen(points_color),
                                      QBrush(points_color))

        if len(self.lines):
            for line in self.lines:
                self.scene.addItem(line)

        if not self.laser_off_flag and not self.laser_in_center:
            self.marked_point = self.scene.addEllipse(self.points[0].x() - 2, self.points[0].y() - 2, 6, 6,
                                                      QPen(Qt.GlobalColor.white), QBrush(Qt.GlobalColor.white))

    def grid_update(self):
        if self.points[0]:
            points_with_null = list(chain.from_iterable(self.points))
            points_with_null.append(QPointF(0, 0))
            min_x = min(point.x() for point in points_with_null) - self.grid_size
            max_x = max(point.x() for point in points_with_null) + self.grid_size
            min_y = min(point.y() for point in points_with_null) - self.grid_size
            max_y = max(point.y() for point in points_with_null) + self.grid_size
            new_rect = QRectF(min_x, min_y, max_x - min_x,
                              max_y - min_y).united(
                self.mapToScene(self.viewport().rect()).boundingRect())
            self.setSceneRect(new_rect)
        self.grid_drawn(new_rect)

    def start_drawing(self):
        if self.laser_on_flag:
            self.current_element = 0
            self.current_segment = 0
            self.current_progress = 0
            self.timer1.start(10)

    def drawing_line(self):
        if self.laser_on_flag and not self.laser_stop_flag:
            if not (self.current_segment == len(self.points[self.current_element]) - 1 and self.current_element != len(
                    self.points) - 1):
                p1 = self.points[self.current_element][self.current_segment]
                p2 = self.points[self.current_element][self.current_segment + 1]
            else:
                p1 = self.points[self.current_element][self.current_segment]
                p2 = self.points[self.current_element + 1][0]

            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            total_length = (dx ** 2 + dy ** 2)
            increment = total_length * self.speed_val / 150

            if self.current_progress < total_length:
                self.scene.removeItem(self.marked_point)
                remaining_length = total_length - self.current_progress
                segment_length = min(remaining_length, increment)

                self.new_point = QPointF(p1.x() + dx * self.current_progress / total_length,
                                         p1.y() + dy * self.current_progress / total_length)

                if not (self.current_segment == len(
                        self.points[self.current_element]) - 1 and self.current_element != len(
                    self.points) - 1):

                    if self.line_item:
                        self.scene.removeItem(self.line_item)

                    self.line_item = self.scene.addLine(p1.x(), p1.y(), self.new_point.x(), self.new_point.y(),
                                                        QPen(Qt.GlobalColor.red))
                    self.marked_point = self.scene.addEllipse(self.new_point.x() - 2, self.new_point.y() - 2, 6, 6,
                                                              QPen(Qt.GlobalColor.red), QBrush(Qt.GlobalColor.red))

                else:

                    self.marked_point = self.scene.addEllipse(self.new_point.x() - 2, self.new_point.y() - 2, 6, 6,
                                                              QPen(Qt.GlobalColor.white), QBrush(Qt.GlobalColor.white))

                self.current_progress += segment_length

            else:

                if self.current_progress >= total_length and not (self.current_segment == len(
                        self.points[self.current_element]) - 1 and self.current_element == len(
                    self.points) - 1):
                    if not (self.current_segment == len(
                            self.points[self.current_element]) - 1 and self.current_element != len(
                        self.points) - 1):

                        self.scene.removeItem(self.marked_point)
                        self.line_item = self.scene.addLine(self.new_point.x(), self.new_point.y(), p2.x(), p2.y(),
                                                            QPen(Qt.GlobalColor.red))
                        self.lines.append(self.line_item)
                        self.new_point = QPointF(p2.x() - 2, p2.y() - 2)
                        self.marked_point = self.scene.addEllipse(self.new_point.x(), self.new_point.y(), 6, 6,
                                                                  QPen(Qt.GlobalColor.red), QBrush(Qt.GlobalColor.red))
                    else:
                        self.scene.removeItem(self.marked_point)
                        self.new_point = QPointF(p2.x() - 2, p2.y() - 2)
                        self.marked_point = self.scene.addEllipse(self.new_point.x(), self.new_point.y(), 6, 6,
                                                                  QPen(Qt.GlobalColor.white),
                                                                  QBrush(Qt.GlobalColor.white))
                        self.current_progress = 0
                        self.current_segment = 0
                        self.current_element += 1

                if self.current_progress >= 100:
                    self.current_segment += 1
                    self.current_progress = 0

                if self.current_segment == len(self.points[self.current_element]) - 1 and self.current_element == len(
                        self.points) - 1:
                    self.marked_point = self.scene.addEllipse(p2.x() - 2, p2.y() - 2, 6, 6,
                                                              QPen(Qt.GlobalColor.white), QBrush(Qt.GlobalColor.white))
                    self.timer1.stop()
                else:
                    self.timer1.start()

    # def start_image_drawing(self):
    #     if self.laser_on_flag:
    #         self.current_progress = 0
    #         self.current_segment = 0
    #         self.timer3.start()
    #
    # def draw_image(self):

    def start_moving(self):
        if self.laser_off_flag:
            self.timer0.start()

    def move_to_start(self):
        if self.laser_off_flag:
            p1 = QPointF(-2, -2)
            p2 = self.points[0][0]
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            total_length = ((dx ** 2) + (dy ** 2)) ** 0.5
            increment = total_length * self.speed_val / 1000

            if self.current_progress < total_length:
                self.scene.removeItem(self.marked_point)
                self.new_point = QPointF(p1.x() + dx * self.current_progress / total_length,
                                         p1.y() + dy * self.current_progress / total_length)
                if self.current_progress > 0:
                    self.marked_point = self.scene.addEllipse(self.new_point.x() - 2, self.new_point.y() - 2, 6, 6,
                                                              QPen(Qt.GlobalColor.white), QBrush(Qt.GlobalColor.white))
                self.current_progress += increment
            if self.current_progress + increment >= total_length:
                self.new_point = QPointF(p2.x(), p2.y())
                self.scene.removeItem(self.marked_point)
                self.marked_point = self.scene.addEllipse(self.new_point.x() - 2, self.new_point.y() - 2, 6, 6,
                                                          QPen(Qt.GlobalColor.white), QBrush(Qt.GlobalColor.white))
                self.timer0.stop()

    def finish_moving(self):
        self.timer2.start()

    def move_to_finish(self):
        p1 = self.points[-1][-1]
        p2 = QPointF(-2, -2)
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        total_length = ((dx ** 2) + (dy ** 2)) ** 0.5
        increment = total_length * self.speed_val / 1000

        if self.current_progress < total_length:
            self.scene.removeItem(self.marked_point)
            self.new_point = QPointF(p1.x() + dx * self.current_progress / total_length,
                                     p1.y() + dy * self.current_progress / total_length)
            if self.current_progress > 0:
                self.marked_point = self.scene.addEllipse(self.new_point.x() - 2, self.new_point.y() - 2, 6, 6,
                                                          QPen(Qt.GlobalColor.white), QBrush(Qt.GlobalColor.white))
            self.current_progress += increment
        if self.current_progress + increment > total_length:
            self.new_point = QPointF(p2.x(), p2.y())
            self.scene.removeItem(self.marked_point)
            self.marked_point = self.scene.addEllipse(self.new_point.x() - 2, self.new_point.y() - 2, 6, 6,
                                                      QPen(Qt.GlobalColor.white), QBrush(Qt.GlobalColor.white))

    def resizeEvent(self, event):
        self.grid_update()
