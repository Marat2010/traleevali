#!/usr/bin/env python3

from datetime import datetime
import pytz
import requests
from PyQt5 import QtWidgets, QtCore
import clientui

url_server = 'http://127.0.0.1:5000'
# url_server = 'https://djherok.herokuapp.com/si/'
fmt = '%a %d %b %Y %H:%M:%S %Z'  # формат вывода даты
tz = pytz.timezone('Europe/Moscow')  # установка таймзоны


class ExampleApp(QtWidgets.QMainWindow, clientui.Ui_MainWindow):
    def __init__(self, url):
        super().__init__()
        self.setupUi(self)
        self.url = url
        # self.label_2.setText(url)
        self.label_2.setText('https://djherok.herokuapp.com')

        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)  # для точек при вводе пароля

        self.pushButton.pressed.connect(self.send_message)
        self.pushButton_2.pressed.connect(lambda: self.send_message(text_help='/help'))

        self.last_timestamp = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_messages)
        # self.timer.timeout(self.update_messages)
        self.timer.start(5000)

    def send_message(self, text_help=''):
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()

        text = self.textEdit.toPlainText() if text_help != '/help' else text_help

        # if text_help == '/help':
        #     text = '/help'
        # else:
        #     text = self.textEdit.toPlainText()

        requests.get(
            self.url + '/send_message',
            json={
                'username': username,
                'password': password,
                'text': text
            }
        )

        self.textEdit.setText('')
        self.textEdit.repaint()

    def update_messages(self):
        response = requests.get(
            self.url + '/get_messages',
            params={'after': self.last_timestamp}
        )
        messages = response.json()['messages']

        for message in messages:
            dt = datetime.fromtimestamp(message['timestamp'])
            # dt = dt.strftime('%H:%M:%S %d/%m/%Y')
            dt = dt.astimezone(tz).strftime(fmt)
            self.textBrowser.append(dt + ' -- ' + message['username'])
            self.textBrowser.append(message['text'])
            self.textBrowser.append('')
            self.last_timestamp = message['timestamp']


app = QtWidgets.QApplication([])
# window = ExampleApp('https://c91b347b7872.ngrok.io')
window = ExampleApp(url_server)
window.show()
app.exec_()

