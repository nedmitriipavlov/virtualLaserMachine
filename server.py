from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
import sys
import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8888))
    server_socket.listen(1)

    while True:
        conn, addr = server_socket.accept()
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                print(data)
                conn.send('DONE'.encode())
        except ConnectionResetError:
            print('CONNECTION RESET')
        finally:
            conn.close()

class ServerThread(QThread):
    started = pyqtSignal()

    def run(self):
        # Запуск сервера
        start_server()
        self.started.emit()

class ClientThread(QThread):
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            # Подключение к серверу
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 8888))

            # Отправка данных на сервер
            client_socket.sendall(b'Hello, Server!')

            # Получение ответа от сервера
            response = client_socket.recv(1024).decode()
            self.response_received.emit(response)

            # Закрытие соединения
            client_socket.close()
        except ConnectionRefusedError:
            self.error_occurred.emit("Ошибка: Не удалось подключиться к серверу.")

class MachineManager(QWidget):
    def __init__(self):
        super().__init__()

        # Создаем и запускаем поток сервера
        self.server_thread = ServerThread()
        self.server_thread.started.connect(self.on_server_started)
        self.server_thread.start()

        # Создаем кнопку для подключения к серверу
        self.connect_button = QPushButton("Connect to Server")
        self.connect_button.clicked.connect(self.connect_to_server)

        # Создаем метку для вывода ответа сервера или ошибки
        self.label = QLabel()

        # Размещаем элементы управления на макете
        layout = QVBoxLayout()
        layout.addWidget(self.connect_button)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def on_server_started(self):
        print("Server started")

    def connect_to_server(self):
        # Создаем и запускаем поток клиента
        self.client_thread = ClientThread()
        self.client_thread.response_received.connect(self.on_response_received)
        self.client_thread.error_occurred.connect(self.on_error_occurred)
        self.client_thread.start()

    def on_response_received(self, response):
        self.label.setText(f"Ответ от сервера: {response}")

    def on_error_occurred(self, error):
        self.label.setText(error)

app = QApplication(sys.argv)
window = MachineManager()
window.show()
sys.exit(app.exec())
