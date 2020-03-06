import vk_user
import vk_common


class Users:
    """

    Class describe users VK

    """

    # Initialization class
    def __init__(self, users):
        """

        (list of object User, string) -> object User or None

        Function of initialization of class User

        """
        self.users = users

    # Get list of friends of user
    def get_id_friends(self):
        """

        (None) -> tuple(int, string, list or None)

        Function gets list of id friends of user VK: list(int, int, ..., int)

        """
        if self.users is None:
            return -1

        params_here = dict()
        params_here["count"] = 1000
        params_code = vk_common.params.copy()
        start = 0
        while True:
            if start > len(self.users):
                break

            script = ""
            user_idx = dict()
            for number, user in enumerate(self.users[start:start + vk_common.COUNT_REQUESTS_EXECUTE:1]):
                if user.friends is not None:
                    continue

                params_here["user_id"] = user.uid
                script += f"API.friends.get({params_here}),"
                user_idx[number] = user

            params_code["code"] = f"return [{script}];"
            error, msg, response = vk_common.request_get('https://api.vk.com/method/execute', params_code,
                                                         vk_common.func_name())
            if error != 0:
                value = (error, msg, None)
                return value
            response_json = response.json()
            response_json_ = response_json["response"]
            for number, response_item in enumerate(response_json_):
                user = user_idx[number]
                if response_item:
                    count = response_item["count"]
                    items = response_item["items"]

                    user.count_friends = count
                    user.friends = items
                else:
                    user.count_friends = 0
                    user.friends = None

            start = start + vk_common.COUNT_REQUESTS_EXECUTE

        return 0, "", None

    # Get list of common friends of user=self and user=other
    def get_common_friends(self, other):
        """

        (object User) -> tuple(int, string, list or None)

        Function gets common friends in list of objects of User

        """

        if not isinstance(other, vk_user.User):
            vk_common.dprint(1, f"Входные данные типа {type(other)}, а ожидается тип {type(self)}")
            raise ValueError

        if other.friends is None:
            value = (-1, "Список друзей у переданного пользователя пуст.", None)
            return value

        other_friends = set(other.friends)

        for user in self.users:
            if user.friends is None:
                vk_common.dprint(2, f"Список друзей у пользователя пуст. user_id = {user.uid}")
                user.common_friends = None
                user.cnt_common_friends = 0
                continue

            user_friends = set(user.friends)

            # Getting common friends equals intersection of sets
            common_friends_list = list(user_friends.intersection(other_friends))

            user.common_friends = common_friends_list
            user.cnt_common_friends = len(common_friends_list)

        value = (0, "", None)
        return value

    # Get list of groups of user
    def get_id_groups(self):
        """

        (None) -> list

        Function gets list of id groups of user VK: list(int, int, ..., int)

        """
        if self.users is None:
            value = (0, "get_id_groups: self.users = None", None)
            return value

        params_here = dict()
        # params_here["user_id"] = self.id
        params_here["count"] = 1000
        params_code = vk_common.params.copy()
        start = 0
        while True:
            if start > len(self.users):
                break

            script = ""
            user_idx = dict()
            for number, user in enumerate(self.users[start:start + vk_common.COUNT_REQUESTS_EXECUTE:1]):
                if user.groups is not None:
                    continue

                params_here["user_id"] = user.uid
                script += f"API.groups.get({params_here}),"
                user_idx[number] = user

            params_code["code"] = f"return [{script}];"
            error, msg, response = vk_common.request_get('https://api.vk.com/method/execute', params_code,
                                                         vk_common.func_name())
            if error != 0:
                value = (error, msg, None)
                return value
            response_json = response.json()
            vk_common.dprint(2, response_json)

            response_json_ = response_json["response"]
            for number, response_item in enumerate(response_json_):
                vk_common.dprint(2, response_item)
                user = user_idx[number]
                if response_item:
                    count = response_item["count"]
                    items = response_item["items"]

                    user.count_groups = count
                    user.groups = items
                else:
                    user.count_groups = 0
                    user.groups = None

            start = start + vk_common.COUNT_REQUESTS_EXECUTE

        value = (0, "", None)
        return value

    # Get list of common groups of user=self and user=other
    def get_common_groups(self, other):
        """

        (object User) -> tuple(int, string, list or None)

        Function gets common groups in list of id groups

        """

        if not isinstance(other, vk_user.User):
            vk_common.dprint(1, f"Входные данные типа {type(other)}, а ожидается тип {type(self)}")
            raise ValueError

        if other.groups is None:
            value = (-1, "Список групп у переданного пользователя пуст.", None)
            return value

        other_groups = set(other.groups)

        for user in self.users:
            if user.groups is None:
                vk_common.dprint(2, f"Список групп у пользователя пуст. user_id = {user.uid}")
                user.common_groups = None
                user.cnt_common_groups = 0
                continue

            user_groups = set(user.groups)

            # Getting common friends equals intersection of sets
            common_groups_list = list(user_groups.intersection(other_groups))

            user.common_groups = common_groups_list
            user.cnt_common_groups = len(common_groups_list)

        value = (0, "", None)
        return value

    def get_additional_info(self, other):

        if not isinstance(other, vk_user.User):
            vk_common.dprint(1, f"Входные данные типа {type(other)}, а ожидается тип {type(self)}")
            raise ValueError

        err, msg, data = other.get_id_friends()
        if err != 0:
            vk_common.dprint(1, f"Ошибка на стадии получения списка друзей у анализируемого пользователя: "
                                f"ошибка {err}, {msg}")
            return

        err, msg, data = self.get_id_friends()
        if err != 0:
            vk_common.dprint(1, f"Ошибка на стадии получения списка друзей у списка пользователей. ошибка {err}, {msg}")
            return

        err, msg, data = self.get_common_friends(other)
        if err != 0:
            vk_common.dprint(1, "Ошибка на стадии получения общих друзей:", msg)
            return

        err, msg, data = other.get_id_groups()
        if err != 0:
            vk_common.dprint(1, f"Ошибка на стадии получения списка групп у анализируемого пользователя: ошибка "
                                f"{err}, {msg}")
            return

        err, msg, data = self.get_id_groups()
        if err != 0:
            vk_common.dprint(1, f"Ошибка на стадии получения списка групп у списка пользователей: ошибка {err}, {msg}")
            return

        err, msg, data = self.get_common_groups(other)
        if err != 0:
            vk_common.dprint(1, f"Ошибка на стадии получения общих групп: ошибка {err}, {msg}")
            return

        # Detect common interests
        for user in self.users:
            user.cnt_common_interests = vk_common.is_common_by_text(other.interests, user.interests)
            user.cnt_common_books = vk_common.is_common_by_text(other.books, user.books)
            user.cnt_common_music = vk_common.is_common_by_text(other.music, user.music)

            # Detect age difference
            if user.age is None or other.age is None:
                user.age_difference = 100
            else:
                user.age_difference = abs(other.age - user.age)
