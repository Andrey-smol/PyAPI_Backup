from src.date_time import DateTime


class MyException(Exception):

    def __init__(self, source, msg):
        self.message = f'\033[91m[Exception] {DateTime.get_date_time_now()} [{source}] ' + msg + '\033[0m'

    def __str__(self):
        return self.message
