from flask import Flask, request
from datetime import datetime
import locale
import json
import pytz
import time
import os
import requests

file_users = './users.json'
file_messages = './messages.json'
fmt = '%a %d %b %Y %H:%M:%S %Z'  # формат вывода даты
tz = pytz.timezone('Europe/Moscow')  # установка таймзоны
locale.setlocale(locale.LC_ALL, ('RU', 'UTF8'))
token_trans_ya = os.environ['token_trans_ya']
url_trans = 'https://translate.yandex.net/api/v1.5/tr.json/translate'

server_start = datetime.now(tz).strftime(fmt)


def write_json(data, filename=file_messages, wa='w'):
    with open(filename, wa) as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


def read_json(filename=file_messages):
    with open(filename, 'r') as f:
        r = json.load(f)
    return r


def transl_msg(msg, language_code):
    data = {'key': token_trans_ya, 'lang': language_code, 'text': msg}  # Параметры запроса
    try:
        r = requests.post(url_trans, data=data).json()
        answer_tr = r['text'][0] if r['code'] == 200 else '---*** Could not translate ***---'
    except Exception:
        answer_tr = '---*** Could not translate ***---'
    return answer_tr


try:    # Чтение пользователей и сообщений из файла
    messages = read_json()
    users = read_json(file_users)
except Exception  as e:
    print('Файлов данных нет, или попорчены! {}'.format(e))
    messages = []
    users = {}

app = Flask(__name__)  # создаем экземпляр приложения Flask


@app.route('/')
def index():
    return 'Hello World! Это наш мессенджер\n Его <a href="/status">статус</a>'


@app.route('/status/')
def status():
    current_time = datetime.now(tz).strftime(fmt)  # тек. время
    count_messages = len(messages)
    count_users = len(users)
    data = {'Status': 'Ok',
            'name': 'Трали Вали ',
            'Время старта сервера': server_start,
            'Тек. время сервера': current_time,
            'Кол-во сообщений: ': count_messages,
            'Кол-во пользователей: ': count_users}

    # вывод через json, для русских букв "ensure_ascii=False"
    state = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
    return state


@app.route('/send_message/')
def send_message():
    username = request.json['username']
    password = request.json['password']
    text = request.json['text']

    if username in users:
        if users[username]['password'] != password:
            return {'ok': False}
    else:
        users[username] = {'password': password, 'lang_code': ''}
        write_json(users, file_users)

    # Чат-Бот с переводчиком для общения с иностранцем.
    # Чтобы ваши сообщения дублировалсиь на другом языке наберите "/L **" , где вместо ** подставить
    # код языка: ru, en, de, fr, zh, ja, ar, ... .
    # Коды языков здесь:
    # https://yandex.ru/dev/translate/doc/dg/concepts/api-overview-docpage/#api-overview__languages
    # После все сообщения будут с переводом на выбранном языке:
    #          22:56:16 03/06/2020 marat
    #          Как ты?
    #          🗺 en : How are you?
    #  Чтобы убрать перевод введите просто "/L" без кода.

    if text == '/help':
        text = '  Чат-Бот с переводчиком для общения с иностранцем.\n' \
               'Чтобы ваши сообщения дублировалиcь на другом языке наберите "/L **" , ' \
               'где вместо ** подставить код языка: ru, en, de, fr, zh, ja, ar, ... .\n   Коды языков здесь:\n' \
               '"https://yandex.ru/dev/translate/doc/dg/concepts/api-overview-docpage/#api-overview__languages" .\n' \
               '  После все сообщения будут с переводом на выбранном языке.\n' \
               'Чтобы убрать перевод введите просто "/L" без кода\n'

    if '/L' in text and len(text.split()) < 3:
        ll = text.split()
        users[username]['lang_code'] = ll[1] if len(ll) > 1 else ''
        write_json(users, file_users)
    elif users[username]['lang_code']:
        lang_code = users[username]['lang_code']
        tr_msg = transl_msg(text, lang_code)
        text += '\n\U0001F5FA {} : {}\n'.format(lang_code, tr_msg)

    messages.append({'username': username, 'text': text, 'timestamp': time.time()})

    if len(messages) > 100:
        mes_100 = messages[-100:]  # Оставляем 100 последних сообщений
        messages.clear()
        messages.extend(mes_100)

    write_json(messages)

    return {'ok': True}


@app.route('/get_messages/')
def get_messages():
    after = float(request.args['after'])

    result = []

    for message in messages:
        if message['timestamp'] > after:
            result.append(message)

    return {'messages': result}


if __name__ == '__main__':
    app.run()  # запуск приложения


# print('---=== Запись в файл: ', filename)
# answer_tr = r['text'][0] if r['code'] == 200 else '---*** Could not translate ***---'

# if len(ll) > 1:
#     users[username]['lang_code'] = ll[1]
# else:
#     users[username]['lang_code'] = ''

# answer_tr = msg
# if not language_code == 'ru':
# if language_code != 'ru':

# if '/L' in text:
#     ll = text.split()
#     if len(ll) > 2:
#         lang_code = ll[1]
#         msg = ' '.join(ll[2:])
#         tr_msg = transl_msg(msg, lang_code)
#         text += '\n {}: {}\n'.format(lang_code, tr_msg)

# msg = ' '.join(ll[2:])
# except FileNotFoundError (json.JSONDecodeError):
# messages = [
#     {'username': 'jack', 'text': 'Hello Jack', 'timestamp': time.time()},
#     {'username': 'jack2', 'text': 'Hello Jack2', 'timestamp': time.time()}
# ]
# users = {
#     'jack': '12345',
#     'jack2': '1234'}

# locale.setlocale(locale.LC_ALL, ('RU', 'UTF8'))
# locale.setlocale(locale.LC_ALL, 'RU')  # локализация (для даты на русском)


