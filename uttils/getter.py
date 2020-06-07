import time
from _datetime import datetime
import requests

fmt = '%a, %d %b %Y %H:%M:%S %Z'  # формат вывода даты
last_timestamp = 0.0

while True:
    response = requests.get(
        'http://127.0.0.1:5000/get_messages/',
        params={'after': last_timestamp}
    )
    messages = response.json()['messages']

    for message in messages:
        dt = datetime.fromtimestamp(message['timestamp'])
        dt = dt.strftime(fmt)
        print(dt, message['username'])
        print(message['text'])
        print()
        last_timestamp = message['timestamp']

    time.sleep(5.0)


