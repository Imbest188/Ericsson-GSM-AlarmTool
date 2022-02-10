from .AlarmCollector import AlarmCollector
from threading import Thread
Thread(target=AlarmCollector().start).start()
