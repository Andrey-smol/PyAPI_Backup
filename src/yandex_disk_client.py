import requests
from src.exception_ import MyException


class YandexDiskClient:
    BASE_URL = "https://cloud-api.yandex.net"
    TAG = 'YandexDiskClient'

    def __init__(self, token):
        self.__token = token

    @property
    def token(self):
        return self.__token

    def __get_base_headers(self):
        return {
            "Authorization": f'OAuth {self.__token}'
        }

    @classmethod
    def request_disk_data(cls, token):
        '''
        возвращает статус подключения к диску пользователя по переданному token
        :param token:
        :return:
        '''
        response = requests.get(f'{cls.BASE_URL}/v1/disk/',
                                headers={"Authorization": f'OAuth {token}'})
        return response.status_code == 200

    def create_folder(self, path):
        '''
        создание папки на диске
        :param path: Путь к создаваемой папке
        :return:
        '''
        response = requests.put(f'{self.BASE_URL}/v1/disk/resources',
                                headers=self.__get_base_headers(),
                                params={'path': path}
                                )
        status = response.status_code
        if status not in (201, 409):
            raise MyException(self.TAG,
                              f"не удалось создать папку {path} - "
                              f"{self.__generate_error_string(response)}")

    def upload_file(self, local_path, disk_path, content):
        '''
        local_path - путь к конкретному файлу, который нужно загрузить
        disk_path - место куда загрузить на яндекс диск
        :return:
        '''
        response = requests.get(f'{self.BASE_URL}/v1/disk/resources/upload',
                                params={'path': disk_path},
                                headers=self.__get_base_headers())

        upload_link = response.json()['href']
        response = requests.put(upload_link, files={'file': content})
        status_code = response.status_code
        if status_code == 201:
            print(f'файл {local_path} успешно записан')
        else:
            raise MyException(self.TAG,
                              f"файл {local_path} не удалось записать - "
                              f"{self.__generate_error_string(response)}")

    def upload_file_from_ethernet(self, url_path_file, disk_path):
        '''
        Сохранение файла из интернета на Диск
        :param url_path_file: ссылка на скачиваемый файл
        :param disk_path: путь к папке, в которую нужно скачать файл
        :return:
        '''

        response = requests.post(f'{self.BASE_URL}/v1/disk/resources/upload',
                                 params={'url': url_path_file, 'path': disk_path},
                                 headers=self.__get_base_headers())
        try:
            response.raise_for_status()
        except Exception as e:
            raise MyException(self.TAG, f"файл {disk_path} не удалось записать - "
                                        f"{self.__generate_error_string(response)}")

    def get_info_files(self, path):
        '''

        :param path:
        :return:
        '''
        response = requests.get(f'{self.BASE_URL}/v1/disk/resources',
                                params={'path': path, 'fields': '_embedded.items'},
                                headers=self.__get_base_headers())
        try:
            response.raise_for_status()
        except:
            raise MyException(self.TAG, f"не удалось получить метаданные о папке {path} - "
                                        f"{self.__generate_error_string(response)}")
        return response.json()

    @staticmethod
    def __generate_error_string(response):
        return f"код ошибки {response.status_code}, {response.json()['message']}"
