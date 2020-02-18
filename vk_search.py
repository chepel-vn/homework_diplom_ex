import vk_common
import vk_user

COUNT_REC_BY_ONE_REQUEST = 15


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
# 5) кино

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
    value = vk_common.request_get("https://api.vk.com/method/users.search", params_here, vk_common.func_name())
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

    def search_users(self, user, search_param):
        """

        (object User, dict) -> (integer, string, list of objects User or None)

        Function executes search users by search parameters

        """

        self.fields['user_id'] = user.id
        self.fields['age_from'] = search_param['age_from']
        self.fields['age_to'] = search_param['age_to']
        self.fields['sex'] = search_param['sex']
        self.fields['city'] = user.city

        # Execute the search
        info_for_search = dict()
        info_for_search['age_from'] = search_param['age_from']
        info_for_search['age_to'] = search_param['age_to']
        info_for_search['sex'] = search_param['sex']
        info_for_search['city'] = user.city_id
        info_for_search['fields'] = vk_common.FIELDS_USER_INFO
        info_for_search['count'] = COUNT_REC_BY_ONE_REQUEST

        self.results = list()
        for month in range(1, 13):
            info_for_search['birth_month'] = month

            error, msg, response = search_by(info_for_search)
            if error != 0:
                value = (error, msg, None)
                return value

            error, msg, count, items = vk_common.get_count_items_by_response(response)
            if error != 0:
                value = (error, msg, None)
                return value

            if count == 0:
                continue

            # Sort out all records of search
            for item in items:
                # print(item)
                user_add = vk_user.User()
                user_add.assign_by_user_info(item)
                if user_add.age is not None:
                    self.results.append(user_add)

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
            print(user.id, user.first_name, user.last_name, user.age, user.interests, user.books, user.music, user.sex,
                  user.city_id)



