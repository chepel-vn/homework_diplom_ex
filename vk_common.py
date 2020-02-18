from urllib.parse import urlencode
import requests
import time
# from decorator_logger import logger_path_decorator, get_name_module
from datetime import date
import re

FIELDS_USER_INFO = "id,first_name,last_name,bdate,interests,books,movies,music,sex,city"

# Variables which need to work with API VK
params = {"access_token": "", "v": 5.103, "timeout": 10}

COUNT_REQUESTS_EXECUTE = 25


def write_to_json(file_path, users):
    """

    (string, list of objects of User) -> bool

    Function writes info about users to json file (info = {'link': ***, 'photo1'=***, 'photo2'=***, 'photo3'=***})

    """

    data_list = []
    for user in users:
        data = dict()
        data['link'] = user.link
        if user.photos is not None:
            for number, photo_path in enumerate(user.photos, 1):
                data[f"photo{number}"] = photo_path
        data_list.append(data)

    if len(data_list) == 0:
        return False

    try:
        import json
        with open(file_path, "w", encoding="utf-8") as outfile:
            json.dump(data_list, outfile, ensure_ascii=False)
        return True
    except FileNotFoundError:
        print(f"Файл \"{file_path}\" не найден.")
    except PermissionError:
        print(f"Не хватает прав для создания файла \"{file_path}\".")
    except Exception as e:
        print(f"Ошибка записи в файл \"{file_path}\".")
        print(e)


def download_photo(img_url):
    """

    (string) -> object Image

    Function download file by url and save it to file by file_path

    """

    image = requests.get(img_url)
    if image is not None:
        return image


def download_photo_to_file(img_url, file_path):
    """

    (string, string) -> bool

    Function download file by url and save it to file by file_path

    """

    img = requests.get(img_url)
    try:
        with open(file_path, 'wb') as img_file:
            img_file.write(img.content)
        return True
    except PermissionError:
        return False


def func_name():
    """

    (None) -> string

    Function gets name of function in which called this function

    """

    import traceback
    return traceback.extract_stack(None, 2)[0][2]


def sex_to_char(sex_id):
    """

    (integer) -> string

    Function gets symbol of sex from integer VK code

    """

    if sex_id == 1:
        return 'Ж'
    elif sex_id == 2:
        return 'М'
    else:
        return ' '


def is_common_by_text(text_src, text):
    """

    (string, string) -> integer

    Function gets count of similar parts of text with using divider = ','

    """

    if text_src is None or text is None:
        return 0

    if len(text_src) == 0 or len(text) == 0:
        return 0

    # Replace special symbols to nothing in each string
    pattern = r'([ ~!@"#$;%^&?*()-+=.]+)'
    replacer = r' '
    text_src = re.sub(pattern, replacer, text_src)
    text = re.sub(pattern, replacer, text)

    # Divide source string by commas
    text_src_list = text_src.split(',')
    count_coincidences = 0
    for text_element in text_src_list:
        text_element = text_element.strip()
        # Replace ' ' to all special symbols = make new pattern
        pattern_words = '([ ]+)'
        replacer_words = '[ ~!@"#$;%^&?*()-+=.]*'
        text_element = re.sub(pattern_words, replacer_words, text_element)
        text_element = f"{replacer_words}{text_element}{replacer_words}"
        pattern_res = text_element

        found = re.search(pattern_res, text, re.IGNORECASE)
        if found is not None:
            # print(found)
            count_coincidences += 1

    return count_coincidences


def get_age(birthday):
    """

    (string, string) -> integer

    Function gets count of similar parts of text with using divider = ','

    """

    if birthday is None:
        return

    try:
        day, month, year = [int(i) for i in birthday.split('.')]
    except ValueError:
        # If date of birthday don't has a year so that we can't detect age
        return

    today = date.today()
    age = today.year - year
    if today.month < month:
        age -= 1
    elif today.month == month and today.day < day:
        age -= 1

    return age


# @logger_path_decorator(get_name_module(__file__)+'.log')
def get_token(filename):
    """

    (string) -> string

    Get token - read from file filename

    """

    token = ""
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            token = file.readline().strip()
            if len(token) > 0:
                params["access_token"] = token
            else:
                print(f"Не удалось прочитать токен. Расместите токен в файле \"{filename}\" в папке с программой.")
    except FileNotFoundError:
        print(f"Файл \"{filename}\" не найден.")
    return token


# @logger_path_decorator(get_name_module(__file__)+'.log')
def get_field_of_response(response_json, field_name):
    """

    (dict, string) -> tuple(int, string, object or None)

    Get value by key=field_name from dictionary

    """

    try:
        value = (0, "", response_json[field_name])
        return value
    except KeyError:
        try:
            error_info = response_json['error']
            value = (error_info['error_code'], error_info['error_msg'], None)
            return value
        except KeyError:
            # print(f"Не найден ключ \"{field_name}\" в ответе {response_json}")
            value = (-2, 'Не найден ключ', None)
            return value
    except TypeError:
        print(f"Входные данные типа {type(response_json)}, а ожидается тип {type(dict())}")
        value = (-1, "Ошибка входных данных", None)
        return value


def get_fields_of_response(response_json, fields_string):
    """

    (dict, string) -> tuple(int, string, object or None)

    Get value by key in fields from dictionary

    """

    fields_list = fields_string.split(',')
    fields = dict()
    for field in fields_list:
        # fields[field] = get_field_of_response(response_json, field)
        error, msg, field_value = get_field_of_response(response_json, field)
        if error == 0:
            fields[field] = field_value
        elif error == -2:
            fields[field] = None
        else:
            value = (error, f"{msg}, поле \"{field}\"", None)
            return value
    value = (0, '', fields)
    return value


# @logger_path_decorator(get_name_module(__file__)+'.log')
def get_count_items_by_response(response):
    """

    (object response) -> tuple(int, string, int, list or None)

    Get fields count and items from response

    """

    response_json = response.json()

    error, msg, info_json = get_field_of_response(response_json, 'response')
    if error != 0:
        value = (error, msg, 0, None)
        return value

    error, msg, count = get_field_of_response(info_json, 'count')
    if error != 0:
        value = (error, msg, 0, None)
        return value

    error, msg, items = get_field_of_response(info_json, 'items')
    if error != 0:
        value = (error, msg, 0, None)
        return value
    value = (0, "", count, items)
    return value


# @logger_path_decorator(get_name_module(__file__)+'.log')
def request_get(method, params_, function_name):
    """

    (string, dict) -> tuple(int, string, object response or None)

    Function execute request to API VK by method api vk and param and get response

    """
    response = None
    try:
        while True:
            response = requests.get(method, params_)
            response_json = response.json()
            error_info = response_json.get('error')
            if error_info is not None:
                if error_info['error_code'] != 6:
                    value = (error_info['error_code'], error_info['error_msg'], None)
                    return value
                else:
                    continue
            else:
                print('.', end='')
                # print(f".{function_name}")
                # because error appeared: many requests per second
                time.sleep(1/3)
                break
    except requests.exceptions.ReadTimeout:
        time.sleep(1)
        request_get(method, params_, function_name)
    except Exception as e:
        value = (-1, e, None)
        return value

    value = (0, "", response)
    return value


# @logger_path_decorator(get_name_module(__file__)+'.log')
def auth():
    """

    (None) -> None

    Function helps getting token for work with api VK

    """

    oauth_url = "https://oauth.vk.com/authorize"
    oauth_params = {
        "client_id": 7238600,
        "display": "page",
        "response_type": "token",
        "scope": "status, friends"
    }

    print("?".join(
      (oauth_url, urlencode(oauth_params)))
    )


# @logger_path_decorator(get_name_module(__file__)+'.log')
def test_id(sid):
    """

    (string) -> boolean

    Function test string = id or not

    """

    sid = sid.strip()
    if len(sid) == 0:
        return False

    if 'a' <= sid[0].lower() <= 'z' or sid[0] == '_':
        for i in range(1, len(sid)):
            if not ('a' <= sid[i].lower() <= 'z' or '0' <= sid[i].lower() <= '9' or sid[i].lower() == '_'):
                return False
        return True
    else:
        return False
