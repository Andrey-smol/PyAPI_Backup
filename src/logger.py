import os
from zipfile import ZipFile, ZIP_DEFLATED

from src.date_time import DateTime
from src.exception_ import MyException


class OperationLogger:
    __LOG_DIR = '../log'
    __LOG_FILE = "logOperation.log"
    __LOG_ZIP = 'log_zip.zip'
    __MAX_BUFFER_ENTRIES = 30
    __MAX_SIZE_FILE = 10_000_000
    __buf = []
    _instance = None
    __initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OperationLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not OperationLogger.__initialized:
            if not os.path.exists(self.__LOG_DIR) or not os.path.isdir(self.__LOG_DIR):
                os.makedirs(os.path.join(os.getcwd(), self.__LOG_DIR))
            self.__pathFile = os.path.join(os.getcwd(), self.__LOG_DIR, self.__LOG_FILE)
            self.__pathZipFile = os.path.join(os.getcwd(), self.__LOG_DIR, self.__LOG_ZIP)
            OperationLogger.__initialized = True

    @property
    def path_file(self):
        return self.__pathFile

    def __log_write(self):
        try:
            with open(self.path_file, "a", encoding='utf-8') as file:
                for item in self.__buf:
                    file.write(item)
                    file.write('\n')
            self.__buf.clear()
            self.__write_file_into_zip(self.path_file)
        except OSError:
            raise MyException('Logger', f'Ошибка записи {self.path_file}')

    def log(self, msg):
        if not msg:
            return
        if 'error' in msg.lower():
            msg = f'ERROR {DateTime.get_date_time_now()} {msg}'
        else:
            msg = f'INFO {DateTime.get_date_time_now()} {msg}'
        self.__buf.append(msg)
        if len(self.__buf) > self.__MAX_BUFFER_ENTRIES:
            self.__log_write()

    def flush_log(self):
        if len(self.__buf) > 0:
            self.__log_write()

    def __write_file_into_zip(self, file_path):
        if os.path.getsize(self.path_file) > self.__MAX_SIZE_FILE:
            with ZipFile(self.__pathZipFile, 'a', compression=ZIP_DEFLATED, compresslevel=3) as fz:
                new_path = ".".join([DateTime.get_date_time_now(),'log'])
                fz.write(file_path, new_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                pass
