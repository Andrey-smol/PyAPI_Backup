import json
import time

from tqdm import tqdm
import os.path
from collections import defaultdict
from yandex_disk_client import YandexDiskClient
from src.dog_ceo_api import DogCeoAPI
from src.exception_ import MyException
from src.logger import OperationLogger


def get_string_completion_program():
    return "\033[94mЗавершение программы\033[0m"


def get_string_interrupted_by_user():
    return "\033[94mПользователь прервал выполнение программы\033[0m"


def request_token_from_user():
    while True:
        print('*******************Ввод токена*******************')
        token = input('Введите токен для доступа на Яндекс диск: ')
        if not token or not YandexDiskClient.request_disk_data(token):
            print("ошибка доступа к Яндекс диску")
            str_ = input('Для продолжение введите Y, для выхода любой другой символ: ')
            if not 'Y' == str_.upper():
                return {'status': False, 'cod': 0}
            else:
                continue
        return {'status': True, 'cod': token}


def request_name_breed():
    while True:
        print('***************Выберите пункт меню:**************')
        print('1 - получить список пород собак')
        print('2 - введите имя породы')
        print('3 - выход из программы')
        number = input("Выберите пункт меню: ").strip()
        if number == '1':
            print("\033[94m    Список пород собак\033[0m")
            list_breeds = DogCeoAPI.get_all_breeds()
            if not list_breeds:
                print("    Не удалось получить список пород собак")
                return {'status': False, 'cod': 1}
            print_in_columns(list_breeds)
        elif number == '2':
            name = input(' Введите имя породы: ')
            if not DogCeoAPI.check_breed_into_list(name):
                print(f'    Нет данных о введенной породе - {name}')
            else:
                return {'status': True, 'cod': name}
        elif number == '3':
            return {'status': False, 'cod': 3}
        else:
            print(f"    Вы ввели недопустимые данные - {number}")


def print_in_columns(list_):
    # Словарь для группировки слов
    dict_ = defaultdict(list)

    # Группировка слов по первой букве
    for word in list_:
        dict_[word[0].lower()].append(word)
    for value in dict_.values():
        print('    ', value)


def get_images_breed(name_breed):
    list_sub_breeds = DogCeoAPI.get_list_sub_breeds(name_breed)
    print(f'\033[94m список под-пород\033[0m {list_sub_breeds}')
    images_breed = []
    if len(list_sub_breeds) > 0:
        for sub_breed in list_sub_breeds:
            url_path_file = DogCeoAPI.get_images_sub_breeds(name_breed, sub_breed)[0]
            images_breed.append(
                (url_path_file, f'{name_breed}/' + "_".join([sub_breed, os.path.basename(url_path_file)])))
    else:
        url_path_file_list = DogCeoAPI.get_images_by_breed(name_breed)
        for image in url_path_file_list:
            disk_path = f'{name_breed}/' + "_".join([name_breed, os.path.basename(image)])
            images_breed.append((image, disk_path))
    return images_breed


def writing_breed_files_to_yandex_disk(client, name_breed, list_images_breed):
    client.create_folder(name_breed)
    number_of_files = len(list_images_breed)
    with tqdm(total=number_of_files, desc="Writing files",
              colour="green", ncols=100) as pbar:
        for i, (url, path_) in enumerate(list_images_breed, start=1):
            pbar.set_description(f"Writing file {os.path.basename(path_)} {i}/{number_of_files}")
            client.upload_file_from_ethernet(url, path_)
            pbar.update(1)


def writing_info_file(client, name_breed, count_files):
    info_files = client.get_info_files(f'{name_breed}/', count_files)
    key_info = ['created', 'mime_type', 'modified', 'name', 'path', 'size']
    list_info_files = []
    for item_ in info_files['_embedded']['items']:
        list_info_files.append({k: v for k, v in item_.items() if k in key_info})

    dir_path = os.path.join(os.getcwd(), '../info_files')
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    with open(os.path.join(dir_path, f'{name_breed}.json'), 'w', encoding='utf-8') as f:
        json.dump(list_info_files, f, ensure_ascii=False, indent=2)


def main():
    logger = OperationLogger()
    try:
        logger.log('ввод и проверка токена')
        result = request_token_from_user()
        if result['status'] == False:
            print(get_string_completion_program())
            str_ = get_string_interrupted_by_user() + ' при вводе токена'
            logger.log('Пользователь прервал выполнение программы')
            raise MyException('main', str_)
        token = result['cod']

        while True:
            logger.log('ввод имени породы собаки')
            result = request_name_breed()
            if result['status'] == False:
                print(get_string_completion_program())
                logger.log('Пользователь прервал выполнение программы')
                break
            name_breed = result['cod']
            logger.log(f'Пользователь запросил файлы для породы - {name_breed}')

            images_breed = get_images_breed(name_breed)
            if not images_breed:
                print('Нет картинок для данной породы')
                logger.log(f'для породы собак {name_breed} не найдено файлов')
                continue

            count_files = len(images_breed)
            client = YandexDiskClient(token)
            writing_breed_files_to_yandex_disk(client, name_breed, images_breed)
            logger.log(f'Запись файлов на Yandex.disk завершена для породы {name_breed}')
            time.sleep(3)
            writing_info_file(client, name_breed, count_files)
            print("Запись файлов на Yandex.disk завершена")
            print('')

    except MyException as e:
        logger.log(e.message)
        print(e.message)
        print(get_string_completion_program())
    except BaseException as ex:
        logger.log(f'Исключение BaseException - {ex}')
        print('\033[91mИсключение\033[0m', ex)
    finally:
        logger.flush_log()


if __name__ == '__main__':
    main()
