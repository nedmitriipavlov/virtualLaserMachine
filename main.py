from PyQt6.QtCore import Qt, QRectF, QEvent, QLineF, QObject, \
    QPointF
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout,\
QLabel, QHBoxLayout, QSlider, QPushButton, QWidget, QGraphicsScene,\
    QGraphicsView, QGraphicsLineItem, QLayout, QGraphicsSceneMouseEvent,\
    QScrollArea, QScrollBar
from PyQt6.QtGui import QImage, QPainter, QColor, QPixmap, QPalette,\
    QPen, QCursor, QGuiApplication
import sys


class MouseFilter(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def eventFilter(self, obj, e):
        if e.type() == QEvent.Type.GraphicsSceneMousePress:
            if e.button() == Qt.MouseButton.LeftButton:
                self.main_window.changeCursor(Qt.CursorShape.OpenHandCursor)  # Change cursor shape to crosshair
                print("Mouse pressed at:", e.scenePos())
                self.lastPos = e.scenePos()


        elif e.type() == QEvent.Type.GraphicsSceneMouseRelease:
            if e.button() == Qt.MouseButton.LeftButton:
                self.main_window.changeCursor(Qt.CursorShape.ArrowCursor)  # Reset cursor shape to default
                print("Mouse released at:", e.scenePos())
        elif e.type() == QEvent.Type.GraphicsSceneMouseMove:
            delta = e.scenePos() - self.lastPos

            print("Mouse moved at:", e.scenePos())
        return super().eventFilter(obj, e)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.lastPos = None

        self.setWindowTitle('VirtualLaserMachine')
        self.rows = 50
        self.columns = 50
        self.setGeometry(200, 400, 800, 600)
        self.squareSize = self.sqSz()


        self.scene = QGraphicsScene(0, 0, self.size().width(), self.size().width())
        self.graphics_view = QGraphicsView(self.scene)



        self.graphics_view.setSceneRect(0, 0, 150, 150)
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setBackgroundBrush(QColor(51, 124, 160).rgb())



        self.setMouseTracking(True)


        self.center()

        self.mouse_filter = MouseFilter(self)

        self.scene.installEventFilter(self.mouse_filter)

        self.setCentralWidget(self.graphics_view)

        self.drawGrid()

    def changeCursor(self, cursor_shape):
        self.graphics_view.setCursor(QCursor(cursor_shape))

    def center(self):
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        center_point = screen_geometry.center()
        print(self.rect().center())
        print(center_point)
        self.move(center_point - self.rect().center())


    def sqSz(self):
        ref = (self.width() / self.rows) * self.columns
        if ref > self.height():
            return self.height() / self.columns
        return self.width() / self.rows


    def drawGrid(self):

        #center the grid
        color = QColor(195, 235, 120).rgb()
        pen = QPen(color, 10, Qt.PenStyle.SolidLine)
        strong_pen = QPen(color, 5, Qt.PenStyle.SolidLine)
        middle_pen = QPen(color, 3, Qt.PenStyle.SolidLine)
        ox = abs(self.size().width()) / 2
        oy = abs(self.size().height()) / 2

        line = QGraphicsLineItem(int(ox), int(oy), int(ox + self.width()), int(oy))
        line.setPen(pen)
        self.scene.addItem(line)





app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()



    # def resizeEvent(self, e):
    #     self.setSceneRect()
    #
    # def eventFilter(self, e):

    # def drawGrid(self):
    #
    #     #center the grid
    #     color = QColor(195, 235, 120).rgb()
    #     pen = QPen(color, 10, Qt.PenStyle.SolidLine)
    #     strong_pen = QPen(color, 5, Qt.PenStyle.SolidLine)
    #     middle_pen = QPen(color, 3, Qt.PenStyle.SolidLine)
    #     ox = abs(self.scene.width()) / 2
    #     oy = abs(self.scene.height()) / 2
    #
    #     # print(ox, oy)
    #     #
    #     line = QGraphicsLineItem()
    #     line.setPen(pen)
    #     self.scene.addItem(line)
        #
        # line = QGraphicsLineItem(0, 0, 100, 100)
        # line.setPen(pen)
        # self.scene.addItem(line)
        #
        # x = ox
        #
        # line = QGraphicsLineItem(int(x), int(-oy), int(x), int(oy+height))
        # line.setPen(pen)
        # self.scene.addItem(line)

        # for row in range(self.rows):
        #     line = QGraphicsLineItem(int(left), int(y), int(left + width), int(y))
        #     line.setPen(pen)
        #     self.scene.addItem(line)
        #     y += self.squareSize
        #
        # line = QGraphicsLineItem(int(left), int(y), int(left + width), int(y))
        # line.setPen(strong_pen)
        # self.scene.addItem(line)
        #
        # y = top
        #
        # for row in range(self.rows):
        #     line = QGraphicsLineItem(int(left), int(y), int(left + width), int(y))
        #     line.setPen(pen)
        #     self.scene.addItem(line)
        #     y -= self.squareSize

        # x = left

        # for col in range(self.columns + 1):
        #     line = QGraphicsLineItem(QLineF(int(x), int(top), int(x), int(top + height)))
        #     line.setPen(pen)
        #     self.scene.addItem(line)
        #     x += self.squareSize







app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

