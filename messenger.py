from datetime import datetime
import pytz
import requests
from PyQt5 import QtWidgets, QtCore
import clientui

# url_server = 'http://127.0.0.1:5000'
url_server = 'https://traleevali.herokuapp.com'

fmt = "%a %d %b %Y %H:%M:%S %Z"  # формат вывода даты
tz = pytz.timezone('Europe/Moscow')  # установка таймзоны


class ExampleApp(QtWidgets.QMainWindow, clientui.Ui_MainWindow):
    def __init__(self, url):
        super().__init__()
        self.setupUi(self)
        self.url = url
        self.label_2.setText(url)

        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)  # для точек при вводе пароля

        self.pushButton.pressed.connect(self.send_message)
        self.pushButton_2.pressed.connect(lambda: self.send_message(text_help='/help'))

        self.last_timestamp = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_messages)
        self.timer.start(3000)

    def send_message(self, text_help=''):
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        # text = self.textEdit.toPlainText()

        text = self.textEdit.toPlainText() if text_help != '/help' else text_help

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
            dt = dt.astimezone(tz).strftime(fmt)
            self.textBrowser.append(dt + ' -- ' + message['username'])
            self.textBrowser.append(message['text'])
            self.textBrowser.append('')
            self.last_timestamp = message['timestamp']


app = QtWidgets.QApplication([])
window = ExampleApp(url_server)
window.show()
app.exec_()


# -----------------------------------------------
# Формирование Python файла из UI:
# pyuic5 messenger.ui -o clientui.py
# ------------------------
# Запуск в Python:
# python messenger.py
# ------------------------
# Создание испольняемого файла (в одном файле и без запуска консоли):
# pyinstaller --onefile --noconsole --icon=/usr/share/icons/tr_vl.ico  messenger.py
# -----------------------------------------------------------------------------------

# local_launch = bool(os.environ['local_launch'])
# local_launch = None
# print('== Local Launch: ', local_launch)
# if local_launch:
#     url_server = 'http://127.0.0.1:5000'
# else:
#     url_server = 'https://traleevali.herokuapp.com'

# dt = dt.strftime('%H:%M:%S %d/%m/%Y')
# window = ExampleApp('https://c91b347b7872.ngrok.io')

