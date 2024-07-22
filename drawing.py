import sys

from PyQt6.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QGraphicsView, QGraphicsScene, QSlider, QPushButton, \
    QApplication
from PyQt6.QtGui import QPen, QPainter
from PyQt6.QtCore import Qt, QPointF, QTimer

from grid import Grid


class Drawing(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.speed_val = 1

        if not scene:
            self.scene = QGraphicsScene()
        else:
            self.scene = scene
        self.setScene(self.scene)

        self.points = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.drawing)


    def start_drawing(self):
        if len(self.points) >= 2:
            self.current_segment = 0
            self.current_progress = 0
            self.timer.start()

    def mousePressEvent(self, event):
        point = event.pos()
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.points.append(point)
        self.scene.addEllipse(point.x()-2, point.y()-2, 2, 2, QPen(Qt.GlobalColor.white))

    def mouseReleaseEvent(self, event):
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def drawing(self):
        if len(self.points) >= 2 and self.dr:
            p1 = self.points[self.current_segment]
            p2 = self.points[self.current_segment + 1]
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            total_length = ((dx ** 2) + (dy ** 2)) ** 0.5
            increment = (total_length*self.speed_val)/ (100000)

            if self.current_progress < total_length:
                new_point = QPointF(p1.x() + dx * self.current_progress / total_length,
                                    p1.y() + dy * self.current_progress / total_length)
                if self.current_progress > 0:
                    self.scene.removeItem(self.line_item)
                self.line_item = self.scene.addLine(p1.x()-1, p1.y()-1, new_point.x()-1, new_point.y()-1, QPen(Qt.GlobalColor.red))
                self.current_progress += increment
                print(self.current_progress)
            else:
                self.current_progress = 0
                self.current_segment += 1
                if self.current_segment == len(self.points) - 1:
                    last_point = self.points[-1]
                    self.points.clear()
                    self.points.append(last_point)
                    self.timer.stop()
