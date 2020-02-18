import vk_common


def get_info_dict(user_id, first_name, last_name, age, sex, interests, books, music, cnt_common_interests,
                  cnt_common_books, cnt_common_music, cnt_common_friend, cnt_common_groups):
    """

    (int, string, string, int, string, string, string, int, int, int, int, int) -> dict

    Function gets dict user's info by info

    """

    info_user = dict()
    info_user['id'] = user_id
    info_user['first_name'] = first_name
    info_user['last_name'] = last_name
    info_user['age'] = age
    info_user['sex'] = sex
    info_user['interests'] = interests
    info_user['books'] = books
    info_user['music'] = music
    info_user['cnt_common_interests'] = cnt_common_interests
    info_user['cnt_common_books'] = cnt_common_books
    info_user['cnt_common_music'] = cnt_common_music
    info_user['cnt_common_friend'] = cnt_common_friend
    info_user['cnt_common_groups'] = cnt_common_groups

    return info_user


class User:
    """

    Class describe user VK

    """
    # id, first_name, last_name, age, interests, books, music, sex, city
    @property
    def id(self):
        return self.info['id']

    @property
    def first_name(self):
        return self.info['first_name']

    @property
    def last_name(self):
        return self.info['last_name']

    @property
    def age(self):
        return self.info.get('age')

    @property
    def bdate(self):
        return self.info.get('bdate')

    @property
    def interests(self):
        return self.info.get('interests')

    @property
    def books(self):
        return self.info.get('books')

    @property
    def music(self):
        return self.info.get('music')

    def movies(self):
        return self.info.get('movies')

    @property
    def sex(self):
        return self.info.get('sex')

    @property
    def city(self):
        return self.info.get('city')

    @property
    def city_id(self):
        city_dict = self.info.get('city')
        if city_dict is not None:
            return city_dict['id']

    @property
    def link(self):
        user_id = self.id
        if user_id is not None:
            value = f"https://vk.com/id{user_id}"
            return value

    # Initialization class
    def __init__(self):
        """

        (None, string) -> object User or None

        Function of initialization of class User

        """

        self.info = {}
        self.groups = None
        self.friends = None
        self.error = {'error': 0, 'msg': ''}
        self.count_friends = 0
        self.count_groups = 0

        self.cnt_common_friends = 0
        self.cnt_common_groups = 0

        self.cnt_common_interests = ''
        self.cnt_common_books = ''
        self.cnt_common_music = ''

    # Assign class by nickname with check from vk
    def assign_by_nickname(self, nickname):
        # Get user_id as integer value
        try:
            self.info['id'] = int(nickname)
        except ValueError:
            # Convert from nickname to user_id
            error, msg, self.info['id'] = self.get_info(nickname)
            if error != 0:
                self.error = {"error": error, "msg": msg}
                return

        self.error = {"error": 0, "msg": ""}

    # Assign class by user_id which exists in vk
    def assign_by_user_info(self, user_info):
        # id,first_name,last_name,bdate,deactivated,is_closed,interests,books,movies,music,last_seen,personal,relation,sex,city
        for key in vk_common.FIELDS_USER_INFO.split(','):
            value = user_info.get(key)
            if value is not None:
                if key == 'bdate':
                    self.info['age'] = vk_common.get_age(value)
                    self.info[key] = value
                else:
                    self.info[key] = value
            else:
                self.info[key] = None

    # Get user_id by nickname of user VK
    def get_info(self, nickname):
        """

        (None) -> (int, string, int)

        Function gets id of user by nickname

        """

        params_here = vk_common.params.copy()
        params_here["user_ids"] = nickname
        params_here["fields"] = vk_common.FIELDS_USER_INFO
        error, msg, response = vk_common.request_get("https://api.vk.com/method/users.get", params_here,
                                                     vk_common.func_name())
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, info_json_list = vk_common.get_field_of_response(response.json(), "response")
        if error != 0:
            value = (error, msg, None)
            return value

        if len(info_json_list) <= 0:
            value = (-1, "Пустой ответ", None)
            return value

        info_json = info_json_list[0]

        error, msg, deactivated = vk_common.get_field_of_response(info_json, "deactivated")
        if error == 0 and (deactivated == "DELETED" or deactivated == "BANNED"):
            value = (error, msg, None)
            return value

        # Get values of information fields of user
        error, msg, fields = vk_common.get_fields_of_response(info_json, vk_common.FIELDS_USER_INFO)
        if error != 0:
            value = (error, msg, None)
            return value

        # id,first_name,last_name,bdate,deactivated,is_closed,interests,books,music,sex,city
        for key, value in fields.items():
            if value is None:
                self.info[key] = None
                continue
            if key in ('first_name', 'last_name', 'interests', 'books', 'movies', 'music') and len(value) <= 0:
                self.info[key] = None
                continue

            # if key in ('interests', 'books', 'movies', 'music'):
            #     if len(value) <= 0:
            #         self.info[key] = None
            #     else:
            #         self.info[key] = value
            if key == 'bdate':
                self.info['age'] = vk_common.get_age(value)
                self.info[key] = value
            else:
                self.info[key] = value

        value = (0, "", self.info['id'])
        return value

    # Get user_id by nickname of user VK
    def get_top_photos(self, top_count):
        """

        (None) -> (int, string, int)

        Function gets photos of user

        """

        params_here = vk_common.params.copy()
        params_here["owner_id"] = self.id
        params_here["album_id"] = 'profile'
        params_here["rev"] = 1
        params_here["extended"] = 1
        params_here["photo_sizes"] = 1

        error, msg, response = vk_common.request_get("https://api.vk.com/method/photos.get", params_here,
                                                     vk_common.func_name())
        if error != 0:
            if error == 30:
                value = (0, "", (None, None, None))
            else:
                value = (error, msg, None)
            return value

        error, msg, count, items = vk_common.get_count_items_by_response(response)
        if error != 0:
            value = (error, msg, None)
            return value

        if len(items) == 0:
            value = (0, "Нет фотографий в профиле", (None, None, None))
            return value

        url_dict = {}
        for item in items:
            # print(item)
            # Select max size
            sizes = item['sizes']
            max_size_elem = None
            max_size_w = 0
            max_size_h = 0
            for picture in sizes:
                if picture['width'] >= max_size_w and picture['height'] >= max_size_h:
                    max_size_w = picture['width']
                    max_size_h = picture['height']
                    max_size_elem = picture
            item['sizes'] = max_size_elem
            url_dict[max_size_elem['url']] = item['likes']['count']

        # Sort dict by values
        list_d = list(url_dict.items())
        list_d.sort(reverse=True, key=lambda i: i[1])

        top_url = []
        for item in list_d[:top_count:1]:
            top_url.append(item[0])

        value = (0, "", top_url)
        return value

    # Get list of friends of user
    def get_id_friends(self):
        """

        (None) -> tuple(int, string, list or None)

        Function gets list of id friends of user VK: list(int, int, ..., int)

        """

        if self.friends is not None:
            value = (0, "", self.friends)
            return value

        params_here = vk_common.params.copy()
        params_here["user_id"] = self.id

        error, msg, response = vk_common.request_get("https://api.vk.com/method/friends.get", params_here,
                                                     vk_common.func_name())
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, count, items = vk_common.get_count_items_by_response(response)
        if error != 0:
            value = (error, msg, None)
            return value

        # self.count_friends = count_items[0]
        # self.friends = count_items[1]
        self.count_friends = count
        self.friends = items

        value = (0, "", self.friends)
        return value

    # Get list of common friends of user=self and user=other
    def get_common_friends(self, other):
        """

        (object User) -> tuple(int, string, list or None)

        Function gets common friends in list of objects of User

        """

        if not isinstance(other, User):
            print(f"Входные данные типа {type(other)}, а ожидается тип {type(self)}")
            raise ValueError

        # Conversions to sets from lists
        error, msg, id_friends = self.get_id_friends()
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, other_id_friends = other.get_id_friends()
        if error != 0:
            value = (error, msg, None)
            return value

        self_friends = set(id_friends)
        other_friends = set(other_id_friends)

        # Getting common friends equals intersection of sets
        common_friends_list = list(self_friends.intersection(other_friends))

        common_friends = []
        for user_id in common_friends_list:
            user_friend = User()
            user_friend.assign_by_nickname(user_id)
            common_friends.append(user_friend)

        value = (0, "", common_friends)
        return value

    # Override operation "&"
    def __and__(self, other):
        """

        (object User) -> tuple(int, string, list or None)

        Function overrides operation "&" between objects of User and gets common friends in list of objects of User

        """

        return self.get_common_friends(other)

    # Get list of groups of user
    def get_id_groups(self):
        """

        (None) -> list

        Function gets list of id groups of user VK: list(int, int, ..., int)

        """
        if self.groups is not None:
            value = (0, "", self.groups)
            return value

        params_here = vk_common.params.copy()
        params_here["user_id"] = self.id
        params_here["count"] = 1000

        error, msg, response = vk_common.request_get("https://api.vk.com/method/groups.get", params_here,
                                                     vk_common.func_name())
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, count, items = vk_common.get_count_items_by_response(response)
        if error != 0:
            value = (error, msg, None)
            return value

        # self.count_groups = count_items[0]
        # self.groups = count_items[1]
        self.count_groups = count
        self.groups = items

        value = (0, "", self.groups)
        return value

    # Get list of common groups of user=self and user=other
    def get_common_groups(self, other):
        """

        (object User) -> tuple(int, string, list or None)

        Function gets common groups in list of id groups

        """

        if not isinstance(other, User):
            print(f"Входные данные типа {type(other)}, а ожидается тип {type(self)}")
            raise ValueError

        # Conversions to sets from lists
        error, msg, id_groups = self.get_id_groups()
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, other_id_groups = other.get_id_groups()
        if error != 0:
            value = (error, msg, None)
            return value

        self_groups = set(id_groups)
        other_groups = set(other_id_groups)

        # Getting common friends equals intersection of sets
        common_groups_list = list(self_groups.intersection(other_groups))

        value = (0, "", common_groups_list)
        return value

    def print(self):
        print(f"id = {self.id} fio = {self.first_name} {self.last_name}")

    def get_additional_info(self, user):
        # Detect common friends
        error, msg, common_friends = self.get_common_friends(user)
        if error != 0:
            common_friends = []

        if common_friends is None:
            self.cnt_common_friends = 0
        else:
            self.cnt_common_friends = len(common_friends)

        # Detect common groups
        error, msg, common_groups = self.get_common_groups(user)
        if error != 0:
            common_groups = []

        if common_groups is None:
            self.cnt_common_groups = 0
        else:
            self.cnt_common_groups = len(common_groups)

        # Detect common interests
        self.cnt_common_interests = vk_common.is_common_by_text(self.interests, user.interests)
        self.cnt_common_books = vk_common.is_common_by_text(self.books, user.books)
        self.cnt_common_music = vk_common.is_common_by_text(self.music, user.music)
        # TODO написать добавление в базу всех результатов поиска в одну транзакцию
