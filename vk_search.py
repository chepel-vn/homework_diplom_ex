import vk_common
import vk_user

COUNT_REC_BY_ONE_REQUEST = 100
MODE_DIVIDE_SEARCH_BY_MONTH = 0


# КРИТЕРИИ ПОИСКА, запрашиваемые у пользователя
# 1) пол
# 2) диапазон возраста или диапазон лет от возраста пользователя(если диапазон возраста не задан, то ищем
#    ровесников пользователя)

# КРИТЕРИИ ПОИСКА, с помощью которых сможем вытянуть больше результатов поиска
# 1) пол, если пользователем задано, что искать всех и женщин и мужчин
# 2) диапазон возраста (получаем выборку за каждый год)
# 3) семейное положение
# 4) месяц рождения

# ПРОРИТЕТ ПОИСКА
# 1) расположение (ищем людей с того же города)
# 1) пол
# 2) возраст
# 3) музыка
# 4) книги

# ПОСЛЕ ПОИСКА ДОПОЛНИТЕЛЬНО СОРТИРУЕМ ПО КРИТЕРИЯМ
# 1) кол-во общих друзей
# 2) кол-во общих групп


def search_by(search_info):
    """

    (dict) -> (integer, string, list of objects or None)

    Function executes search users by search parameters

    """

    params_here = vk_common.params.copy()
    params_here.update(search_info)
    vk_common.dprint(2, vk_common.func_name(), "Параметры поиска: ", params_here)
    value = vk_common.request_get("https://api.vk.com/method/users.search", params_here, vk_common.func_name())
    vk_common.dprint(2, vk_common.func_name(), "Результат поиска: ", value)
    return value


class Search:
    """

    Class describe search users by many field from VK

    """

    @property
    def user_id(self):
        return self.fields.get('user_id')

    @property
    def age_from(self):
        return self.fields.get('age_from')

    @property
    def age_to(self):
        return self.fields.get('age_to')

    @property
    def sex(self):
        return self.fields.get('sex')

    # Initialization class
    def __init__(self):
        """

        (None, string) -> object Search or None

        Function of initialization of class Search

        """

        # Information for search
        self.fields = dict()
        self.results = list()

    def execute_search(self, info_for_search, user_id_old, user_id_banned):
        error, msg, response = search_by(info_for_search)
        if error != 0:
            return error, msg, None

        error, msg, count, items = vk_common.get_count_items_by_response(response)
        vk_common.dprint(2, "Парсим результат запроса: ", error, msg, count, items)
        if error != 0:
            return error, msg, None

        if count == 0:
            return 0, "", None

        # Sort out all records of search
        for item in items:
            vk_common.dprint(2, item['id'], user_id_old)
            if item['id'] in user_id_old or item['id'] in user_id_banned:
                # print(f"id = {item['id']} пропустили.")
                continue

            vk_common.dprint(2, "item = ", item)
            user_add = vk_user.User()
            user_add.assign_by_user_info(item)
            vk_common.dprint(2, f"Смотрим результат работы user_add.assign_by_user_info: "
                                f"{user_add.error['error']}: {user_add.error['msg']}")
            if user_add.error["error"] != 0:
                vk_common.dprint(1, vk_common.func_name(), f"Возникла ошибка {user_add.error['error']}: "
                                                           f"{user_add.error['msg']}.")
                return -1, f"{user_add.error['error']}: {user_add.error['msg']}", None

            vk_common.dprint(2, f"user_add.uid = {user_add.uid}, user_add.age = {user_add.age}")

            if user_add.uid is None:
                vk_common.dprint(1, vk_common.func_name(), f"Параметр user_add.uid = {user_add.uid}")
                return -1, f"{vk_common.func_name()}. Параметр user_add.uid = {user_add.uid}.", None

            if user_add.age is not None:
                self.results.append(user_add)
                vk_common.dprint(2, f"id = {user_add.uid} добавили в список.")
            else:
                vk_common.dprint(2, f"id = {user_add.uid} пропустили потому как возраст не определился.")
        return 0, "", self.results

    def search_users(self, user, search_param, user_id_old, user_id_banned):
        """

        (object User, dict, list, list) -> (integer, string, list of objects User or None)

        Function executes search users by search parameters

        """

        if not isinstance(user, vk_user.User):
            vk_common.dprint(1, vk_common.func_name(), f"{type(user)} is not object User.")
            return -1, "Некорректный входной параметр.", None

        if not isinstance(user_id_banned, list):
            vk_common.dprint(1, vk_common.func_name(), f"{type(user_id_banned)} is not list.")
            return -1, "Некорректный входной параметр.", None

        if not isinstance(user_id_old, list):
            vk_common.dprint(1, vk_common.func_name(), f"{type(user_id_old)} is not list.")
            return -1, "Некорректный входной параметр.", None

        vk_common.dprint(2, "Черный список", user_id_banned)
        vk_common.dprint(2, "Список пользователей, которые были найдены ранее", user_id_old)
        vk_common.dprint(2, "Параметры поиска: ", search_param)

        age_from = search_param['age_from']
        age_to = search_param['age_to']
        sex = search_param['sex']

        if age_from <= 0 or age_to <= 0:
            return -1, f"\"Возраст\" как параметр поиска должен быть положительным числом. " \
                      f"age_from = {age_from}, age_to = {age_to}", None

        if age_to < age_from:
            return -1, f"\"Возраст ОТ\" должен быть <= \"Возраст ДО\". " \
                      f"age_from = {age_from}, age_to = {age_to}", None

        if sex not in (0, 1, 2):
            return -1, f"\"Пол\" как параметр должен быть 0, 1 или 2; sex = {sex}", None

        self.fields['user_id'] = user.uid
        self.fields['age_from'] = age_from
        self.fields['age_to'] = age_to
        self.fields['sex'] = sex
        self.fields['city'] = user.city

        # Execute the search
        info_for_search = dict()
        info_for_search['age_from'] = age_from
        info_for_search['age_to'] = age_to
        info_for_search['sex'] = sex
        info_for_search['city'] = user.city_id
        info_for_search['fields'] = vk_common.FIELDS_USER_INFO
        info_for_search['count'] = COUNT_REC_BY_ONE_REQUEST
        vk_common.dprint(2, "Формирование информации для функции поиска: ", info_for_search)

        self.results = list()
        if MODE_DIVIDE_SEARCH_BY_MONTH == 1:
            for month in range(1, 13):
                info_for_search['birth_month'] = month
                err, msg, data = self.execute_search(info_for_search, user_id_old, user_id_banned)
                if err != 0:
                    vk_common.dprint(2,  vk_common.func_name(), f"Ошибка в процедуре поиска {err}: {msg} data = {data}")
                    return -1, f"Ошибка в процедуре поиска {err}: {msg} data = {data}", None
        else:
            err, msg, data = self.execute_search(info_for_search, user_id_old, user_id_banned)
            if err != 0:
                vk_common.dprint(2, vk_common.func_name(), f"Ошибка в процедуре поиска {err}: {msg} data = {data}")
                return -1, f"Ошибка в процедуре поиска {err}: {msg} data = {data}", None

        value = (0, '', self.results)
        return value

    def print(self):
        """

        (None) -> (None)

        Function helps view results of search

        """

        if self.results is None:
            return

        if len(self.results) == 0:
            return

        for user in self.results:
            print(user.uid, user.first_name, user.last_name, user.age, user.interests, user.books, user.music, user.sex,
                  user.city_id)



