from cachetools import TTLCache, cached
import requests
from requests import HTTPError

from exception_ import MyException


class DogCeoAPI:
    BASE_URL = "https://dog.ceo/api/"
    TAG = 'DogCeoAPI'
    cache = TTLCache(maxsize=128, ttl=100)

    @staticmethod
    def __get_url(url_path):
        return f'{DogCeoAPI.BASE_URL}{url_path}'

    @staticmethod
    def __check_data(data):
        return data.get('status') == 'success'

    @staticmethod
    def check_breed_into_list(breed):
        return breed in DogCeoAPI.get_all_breeds()

    @staticmethod
    @cached(cache)
    def get_all_breeds():
        '''
        list all breeds
        :param :
        :return list:
        '''

        result = []
        response = requests.get(DogCeoAPI.__get_url('breeds/list/all'))
        DogCeoAPI.__check_exception('get_all_breeds()', response)
        data = response.json()
        if DogCeoAPI.__check_data(data):
            result = [i for i in data['message']]
        return result

    @staticmethod
    def get_images_by_breed(name_breed):
        '''
        Returns an array of all the images from a breed
        :param name_breed:
        :return list images:
        '''

        result = []
        response = requests.get(DogCeoAPI.__get_url(f'breed/{name_breed}/images'))
        DogCeoAPI.__check_exception(f'get_images_by_breed({name_breed})', response)
        data = response.json()
        if DogCeoAPI.__check_data(data):
            result = data.get('message')
        return result

    @staticmethod
    def get_list_sub_breeds(name_breed):
        '''
        Returns an array of all the sub-breeds from a breed
        :param name_breed:
        :return list:
        '''

        result = []
        response = requests.get(DogCeoAPI.__get_url(f'breed/{name_breed}/list'))
        DogCeoAPI.__check_exception(f'get_list_sub_breeds({name_breed})', response)
        data = response.json()
        if DogCeoAPI.__check_data(data):
            result = data.get('message')
        return result

    @staticmethod
    def get_images_sub_breeds(name_breed, sub_name_breed):
        '''
        Returns an array of all the images from the sub-breed
        :param name_breed:
        :param sub_name_breed:
        :return:
        '''

        result = []
        response = requests.get(DogCeoAPI.__get_url(f'breed/{name_breed}/{sub_name_breed}/images'))
        DogCeoAPI.__check_exception(f'get_images_sub_breeds({name_breed}, {sub_name_breed})', response)
        data = response.json()
        if DogCeoAPI.__check_data(data):
            result = data.get('message')
        return result

    @staticmethod
    def __check_exception(msg, response):
        try:
            response.raise_for_status()
        except HTTPError:
            raise MyException(DogCeoAPI.TAG,
                              f'ошибка при запросе данных в функции - {msg} - '
                              f'код ошибки {response.status_code}, {response.json()['message']}')
