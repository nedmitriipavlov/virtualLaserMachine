from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, \
    QGraphicsSimpleTextItem, QHBoxLayout, QRadioButton, QGraphicsProxyWidget, \
    QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QStackedLayout, \
    QMainWindow, QSlider
from PyQt6.QtCore import Qt, QPointF

from PyQt6.QtCore import QThread, pyqtSignal

from grid import Grid
from working_grid import MachineGrid
from photo_on_grid import *

import sys
import socket

command = None

server_running = True


def start_server():
    global server_running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8889))
    server_socket.listen(1)

    print("Server started")

    while server_running:
        conn, addr = server_socket.accept()
        try:
            while server_running:
                data = conn.recv(1024).decode()
                if not data:
                    break
                if data == 'exit':
                    server_running = False
                    break
                else:
                    print(data)
                    conn.send('DONE'.encode())
        except ConnectionResetError:
            print('CONNECTION RESET')
        finally:
            conn.close()
    server_socket.close()
    print("Server stopped")


class ServerThread(QThread):
    started = pyqtSignal()

    def run(self):
        # Запуск сервера
        start_server()
        self.started.emit()


class ManagerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('virtual Laser Machine')

        self.center_of_screen = QApplication.primaryScreen().geometry().center()
        self.center_of_window = self.rect().center()
        self.center = (self.center_of_screen - self.center_of_window)

        self.resize(900, 600)

        self.move(self.center)

        self.grid = Grid()
        self.machine_mode_window = None

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.grid, stretch=6)

        layout_buttons = QHBoxLayout()

        self.left_row = QVBoxLayout()
        self.stacked_layout = QStackedLayout()
        self.agree_layout = QVBoxLayout()

        self.agree = QRadioButton('Поставить точки по координатам')
        self.agree.setChecked(False)
        self.agree.toggled.connect(self.agreement)

        self.coordinates_label = QLabel('Напишите координаты точки')
        self.coordinates = QLineEdit()
        self.coordinates.setPlaceholderText('2, 5')
        self.coordinates_send = QPushButton('Установить точку')
        self.coordinates_send.clicked.connect(self.save_coordinates)

        self.agree_layout.addWidget(self.coordinates_label)
        self.agree_layout.addWidget(self.coordinates)
        self.agree_layout.addWidget(self.coordinates_send)

        container_agree_widget = QWidget()
        container_agree_widget.setLayout(self.agree_layout)

        self.stacked_layout.addWidget(container_agree_widget)
        self.stacked_layout.addWidget(QWidget())

        self.left_row.addWidget(self.agree)
        self.left_row.addLayout(self.stacked_layout)

        self.agreement(False)
        layout_buttons.addLayout(self.left_row, stretch=3)

        self.middle_row = QVBoxLayout()
        self.right_row = QVBoxLayout()

        self.button_get_to_back = QPushButton("Вернуться в начало осей координат")
        self.button_get_to_back.clicked.connect(self.grid.get_to_back)

        self.button_delete_points = QPushButton("Очистить поле")
        self.button_delete_points.clicked.connect(self.delete_points)

        self.button_delete_last_point = QPushButton("Удалить последнюю точку")
        self.button_delete_last_point.clicked.connect(self.delete_last_point)

        self.button_drawing_mode = QPushButton('Отметить точки на экране')
        self.button_drawing_mode.clicked.connect(self.start_drawing_mode)
        self.button_drawing_mode.setCheckable(True)

        self.middle_row.addWidget(self.button_get_to_back)
        self.middle_row.addWidget(self.button_drawing_mode)
        self.middle_row.addWidget(self.button_delete_last_point)
        self.middle_row.addWidget(self.button_delete_points)

        layout_buttons.addLayout(self.middle_row, stretch=2)

        self.button_machine_mode = QPushButton('Перейти к печати')
        self.button_machine_mode.clicked.connect(self.machine_mode)
        self.button_machine_mode.setCheckable(True)
        self.right_row.addWidget(self.button_machine_mode)

        self.stacked_layout_ph = QStackedLayout()
        self.agree_layout_ph = QVBoxLayout()

        self.agree_ph = QRadioButton('Установить изображение')
        self.agree_ph.setChecked(False)
        self.agree_ph.toggled.connect(self.agreement_ph)

        self.path_photo_label = QLabel('Напишите путь к изображению')
        self.path_photo = QLineEdit('')
        self.path_photo.setPlaceholderText('')
        self.path_photo_send = QPushButton('Установить')
        self.path_photo_send.clicked.connect(self.save_path_photo)

        self.agree_layout_ph.addWidget(self.path_photo_label)
        self.agree_layout_ph.addWidget(self.path_photo)
        self.agree_layout_ph.addWidget(self.path_photo_send)

        container_agree_ph_widget = QWidget()
        container_agree_ph_widget.setLayout(self.agree_layout_ph)

        self.stacked_layout_ph.addWidget(container_agree_ph_widget)
        self.stacked_layout_ph.addWidget(QWidget())

        self.right_row.addWidget(self.agree_ph)
        self.right_row.addLayout(self.stacked_layout_ph)

        self.agreement_ph(False)

        layout_buttons.addLayout(self.right_row, stretch=2)

        global server_running
        server_running = True

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_label = QLabel()

        self.server_thread = ServerThread()
        self.server_thread.started.connect(self.connect_to_server)
        self.connect_to_server()
        self.server_thread.start()

        self.layout.addLayout(layout_buttons)
        self.message_text = ''
        self.message_space = QVBoxLayout()
        self.message_space.addWidget(QLabel(self.message_text))
        self.message_space.addWidget(self.server_label)
        self.layout.addLayout(self.message_space)



        self.setLayout(self.layout)

    def connect_to_server(self):
        try:
            self.client_socket.connect(('localhost', 8889))
            self.server_label.setText("Подключено к серверу.")
        except ConnectionRefusedError:
            self.server_label.setText("Ошибка: Не удалось подключиться к серверу.")

    def send_to_server(self, command):
        if command:
            try:
                self.client_socket.sendall(command.encode())
                response = self.client_socket.recv(1024).decode()
                self.server_label.setText(f"Ответ от сервера: {response}")
            except Exception as e:
                self.server_label.setText(f"Ошибка при отправке команды: {str(e)}")
        else:
            self.server_label.setText("Команда пустая, нечего отправлять.")

    def closeEvent(self, event):
        global server_running
        server_running = False
        event.accept()

    def agreement(self, checked):
        i = 0 if checked else 1
        self.stacked_layout.setCurrentIndex(i)

    def save_coordinates(self):
        self.coordinates_value = self.coordinates.text()
        x, y = (int(i) * self.grid.grid_size for i in self.coordinates_value.split(', '))
        if not self.grid.points:
            self.grid.points.append([])
            self.grid.lines.append([])
            self.grid.last_num_of_drawn_lines.append([1])
        self.grid.points[-1].append(QPointF(x, -y))
        self.grid.grid_update()
        print(self.grid.points)
        self.set_message_text('({0}, {1}) координаты сохранены!'.format(x // 25, y // 25))
        return setattr(self.grid, 'drawing_mode_flag', True)

    def save_path_photo(self):
        try:
            img = image_processing(self.path_photo.text())
            matrix = get_img_matrix(img)
            self.grid.image_drawing(matrix)
            self.grid.image_drawing_flag = True
            self.set_message_text('Фотография отображена!')
        except:
            self.set_message_text('Проверьте путь к изображению!')

    def agreement_ph(self, checked):
        i = 0 if checked else 1
        self.stacked_layout_ph.setCurrentIndex(i)

    def set_message_text(self, text):
        self.message_text = text
        self.message_space.itemAt(0).widget().setText(self.message_text)

    def start_drawing_mode(self, checked):
        self.set_message_text('Можете отмечать точки')
        if checked:
            self.grid.points.append([])
            self.grid.lines.append([])
            self.grid.last_num_of_drawn_lines.append([1])
            self.grid.drawing_mode_times += 1
        return setattr(self.grid, 'drawing_mode_flag', checked)

    def delete_points(self):
        print(self.grid.points)
        self.grid.points.clear()
        self.grid.lines.clear()
        self.grid.last_num_of_drawn_lines.clear()
        self.grid.drawing_mode_times = 0
        self.grid.image_points.clear()
        self.grid.image_drawing_flag = False
        self.grid.grid_update()
        self.set_message_text('Поле очищено!')

    def delete_last_point(self):
        if len(self.grid.points[self.grid.drawing_mode_times - 1]) != 0:
            self.grid.points[self.grid.drawing_mode_times - 1].pop(-1)
        else:
            self.grid.points.pop(-1)
            self.grid.lines.pop(-1)
            self.grid.last_num_of_drawn_lines.pop(-1)
            self.grid.drawing_mode_times -= 1
            self.grid.points[self.grid.drawing_mode_times - 1].pop(-1)
        # if self.grid.points:
        #     self.machine_mode_window.grid.points = self.grid.points
        self.grid.grid_update()
        self.set_message_text('Последняя точка удалена!')

    def draw_lines(self):
        self.grid.draw_line_flag = True
        self.grid.grid_update()

    def machine_mode(self, checked):
        self.machine_mode_window = MachineManager()
        if checked or not self.machine_mode_window.flag_is_closed:
            self.button_machine_mode.setCheckable(False)
            self.button_drawing_mode.setCheckable(False)
            self.machine_mode_window.grid.points = self.grid.points
            if self.machine_mode_window.message_to_server:
                self.send_to_server(self.machine_mode_window.message_to_server)
            if self.machine_mode_window.grid.points:
                self.machine_mode_window.show()
            else:
                self.set_message_text('Пожалуйста, укажите точки для печати')
        else:
            self.button_drawing_mode.setCheckable(True)
            self.button_machine_mode.setCheckable(True)
            self.button_machine_mode.setDown(False)


class MachineManager(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Machine Mode')

        self.flag_is_closed = False

        self.center_of_screen = QApplication.primaryScreen().geometry().center()
        self.center_of_window = self.rect().center()
        self.center = (self.center_of_screen - self.center_of_window)

        self.message_to_server = None

        self.resize(900, 600)

        self.move(self.center)

        self.grid = MachineGrid()

        layout = QVBoxLayout()
        layout.addWidget(self.grid, stretch=6)
        layout_buttons = QHBoxLayout()

        self.button_slider_change_speed = QPushButton('Изменить скорость')
        self.button_slider_change_speed.setCheckable(True)
        self.button_slider_change_speed.clicked.connect(self.slider_change_speed_agreement)

        layout_slider = QVBoxLayout()

        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setValue(10)
        self.speed_label = QLabel(f'Установите скорость от 10 до 100: {self.slider_speed.value()}')
        self.slider_speed.setMinimum(10)
        self.slider_speed.setMaximum(100)
        self.slider_speed.setSingleStep(10)
        self.slider_speed.setPageStep(10)
        self.slider_speed.setTickInterval(10)
        self.slider_speed.setEnabled(False)
        self.slider_speed.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.slider_speed.valueChanged.connect(self.slider_change_speed)

        layout_slider.addWidget(self.speed_label)
        layout_slider.addWidget(self.slider_speed)

        work_management = QVBoxLayout()

        self.button_move_to_start = QPushButton('Переместить на старт')
        self.button_move_to_start.clicked.connect(self.move_to_start)
        work_management.addWidget(self.button_move_to_start)

        self.button_start = QPushButton('Старт работы')
        self.button_start.clicked.connect(self.start)
        work_management.addWidget(self.button_start)

        self.button_stop = QPushButton('Стоп')
        self.button_stop.setCheckable(True)
        self.button_stop.clicked.connect(self.stop)
        work_management.addWidget(self.button_stop)

        self.button_move_to_finish = QPushButton('Окончить работу')
        self.button_move_to_finish.clicked.connect(self.move_to_finish)
        work_management.addWidget(self.button_move_to_finish)

        layout_buttons.addLayout(layout_slider, stretch=2)
        layout_buttons.addWidget(self.button_slider_change_speed, stretch=2)
        layout_buttons.addLayout(work_management, stretch=2)

        layout.addLayout(layout_buttons)

        self.setLayout(layout)

    def move_to_start(self):
        self.grid.laser_off_flag = True
        self.grid.laser_in_center = False
        self.button_move_to_start.setEnabled(False)
        self.grid.start_moving()
        command = 'MOVE TO START'
        self.message_to_server = command


    def move_to_finish(self):
        self.grid.laser_off_flag = True
        self.grid.finish_moving()
        self.grid.laser_in_center = True
        self.button_move_to_finish.setEnabled(False)
        command = 'MOVE TO FINISH'
        self.message_to_server = command

    def start(self):
        if self.grid.laser_off_flag:
            self.button_start.setEnabled(False)
            self.grid.laser_on_flag = True
            self.grid.laser_off_flag = False
            self.grid.start_drawing()
            command = 'START WORK'
            self.message_to_server = command

    def stop(self, checked):
        if checked:
            self.grid.laser_stop = True
            self.grid.laser_on_flag = False
        else:
            self.grid.laser_on_flag = True
            self.grid.laser_stop = False
            self.grid.drawing_line()
            self.grid.timer1.start()
        command = 'STOP'
        self.message_to_server = command


    def start_draw_image(self):
        if self.grid.laser_off_flag:
            self.grid.laser_on_flag = True
            self.grid.laser_in_center = False
            self.grid.laser_off_flag = False
            self.grid.image_drawing()
            command = 'START DRAWING'
            self.message_to_server = command


    def slider_change_speed(self, value):
        value = (value // 10) * 10
        self.slider_speed.setValue(value)
        self.grid.speed_val = self.slider_speed.value()
        self.speed_label.setText(f'Установите скорость от 1 до 100: {self.slider_speed.value()}')
        command = F'SET SPEED {self.slider_speed.value()}'
        self.message_to_server = command

    def slider_change_speed_agreement(self, checked):
        if checked:
            self.slider_speed.setEnabled(True)
        else:
            self.slider_speed.setEnabled(False)

    def handle_slider_change(self, change):
        if change == QSlider.SliderValueChange:
            value = self.slider_speed.value()
            # Ensure value is a multiple of 10
            value = (value // 10) * 10
            self.slider_speed.setValue(value)

    def closeEvent(self, event):
        self.flag_is_closed = True
        self.message_to_server = None
        super().closeEvent(event)


app = QApplication(sys.argv)
window = ManagerApp()
window.show()
sys.exit(app.exec())
