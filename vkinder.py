import vk_common
import vk_user
import vk_users
import vk_search
import vk_db
import vk_gdi


def input_user():
    """

    (None) -> object User or None

    Function asks user_id or nickname from standard input and gets object User by this user_id

    """

    # Input user id
    while True:
        id_string = input("Введите id пользователя ВКонтакте (число=id пользователя или строка=nickname): ").strip()
        # id_string = '171691064'
        # id_string = '5521318'

        user, msg, err = get_user_by_id(id_string)
        if err == 0:
            break
        else:
            vk_common.dprint(2, vk_common.func_name(), user, err, msg)
            if err == 5:
                break
            else:
                continue
    return user, err, msg


def get_user_by_id(id_string):
    """

    (string) -> (User or None, string, int)

    Function gets object User by users's id string from VK

    """

    vk_common.dprint(2, vk_common.func_name(), f"Входные данные: id_string = {id_string}")
    try:
        int(id_string)
        id_string = f"id{id_string}"
    except ValueError as error:
        vk_common.dprint(2, vk_common.func_name(), error)

    if vk_common.test_id(id_string):
        user = vk_user.User()
        user.assign_by_nickname(id_string)
        if user.error["error"] != 0:
            if user.error["error"] == 113:
                print(f"Аккаунт ВК с id = \"{id_string}\" не определен в системе.")
            else:
                print(f"Возникла ошибка {user.error['error']}: {user.error['msg']}.")
            return None, user.error['msg'], user.error["error"]
        else:
            return user, "", 0
    else:
        print("Введенная строка не может быть идентификатором пользователя.")
        return None, "", -1


def input_search_parameters(user):
    """

    (object User) -> (dict or None, int)

    Function asks search parameters from standard input and gets dict of these parameters

    """

    search_param = dict()

    # If user's age didn't detect then mode "age_method_search=0" we can't use
    if user.age is not None:
        # Input age_from and age_to
        age_method_search = int(input("Поиск ровесников или в диапазоне(0=ровесники, 1=диапазон, 2=выход)): ").strip())
    else:
        age_method_search = 1

    if age_method_search == 1:

        # If user's age didn't detect then mode "age_method_search_ex=0" we can't use
        if user.age is not None:
            while True:
                age_method_search_ex = int(input("Поиск по диапазону(0=относительный 1=абсолютный диапазон, "
                                                 "2=выход)): ").strip())
                if age_method_search_ex in (0, 1, 2):
                    break
            if age_method_search_ex == 2:
                return None, -1
        else:
            age_method_search_ex = 1

        if age_method_search_ex == 0:
            age_div = int(input("Введите +- кол-во лет относительно возраста пользователя: ").strip())
            age_from = user.age - age_div
            age_to = user.age + age_div
            vk_common.dprint(2, f"age_from = {age_from}; age_to = {age_to}")
        else:
            pass
            age_from = int(input("Введите параметр \"Возраст ОТ\"): ").strip())
            age_to = int(input("Введите параметр \"Возраст ДО\"): ").strip())
            vk_common.dprint(2, f"age_from = {age_from}; age_to = {age_to}")
    else:
        age_from = user.age
        age_to = user.age
        vk_common.dprint(2, f"age_from = {age_from}; age_to = {age_to}")

    # Input sex as parameter of search
    sex = int(input("Поиск по полу (0=пол не указан, 1=женский; 2=мужской, 3=выход)): ").strip())

    search_param['age_from'] = age_from
    search_param['age_to'] = age_to
    search_param['sex'] = sex

    value = (search_param, 0)
    return value


def get_user_id_by_old_searches(user_id):
    """

    (int) -> (list, int)

    Function gets list of user_ids from database are which was written earlier to database

    """

    rows, err = vk_db.get_count_rows_of_table(vk_db.TABLES_NAMES[4])
    if err != 0:
        value = (None, err)
        return value
    else:
        if rows is not None:
            count_rows = rows[0][0]
        else:
            count_rows = 0

    user_id_old = list()
    if count_rows > 0:
        rows, err = vk_db.get_users_by_old_searches(user_id)
        if err != 0:
            vk_common.dprint(2, err)
            value = (None, err)
            return value
        else:
            for row in rows:
                user_id_old.append(row[0])
            return user_id_old, 0
    else:
        return user_id_old, 0


def get_top_users_by_search(search, count_top):
    """

    (object Search, int) -> (list of objects User or None, int)

    Function gets top-list users from results of object search (executes necessary sorting of objects beforehand)

    """

    # user_id_old = vk_db.get_user_id_by_old_searches(user.uid)
    user_list = list()
    for index, u in enumerate(search.results):
        if u is not None:
            # if u.uid not in user_id_old:
            vk_common.dprint(2, f"user_id = {u.uid}, кол-во общ. друзей = {u.cnt_common_friends}, "
                                f"кол-во общ. групп = {u.cnt_common_groups}")
            user_list.append((index, u.age, u.age_difference, u.cnt_common_friends, u.cnt_common_groups,
                              u.cnt_common_interests, u.cnt_common_music, u.cnt_common_books))

    vk_common.dprint(2, f"Получили список пользователей: {user_list}")

    if len(user_list) > 0:
        vk_common.dprint(2, f"Список пользователей до сортировки: {user_list}")
        # u.age_difference asc, u.cnt_common_friends desc, u.cnt_common_groups desc, u.cnt_common_interests desc,
        # u.cnt_common_music desc, u.cnt_common_books desc
        user_list.sort(key=lambda x: (x[2], -x[3], -x[4], -x[5], -x[6], -x[7]))
        vk_common.dprint(2, f"Список пользователей после сортировки: {user_list}")

        top_users = list()
        for number, u in enumerate(user_list, 1):
            if number > count_top:
                break
            top_users.append(search.results[u[0]])

        search.top_results = top_users
        value = (top_users, 0)
    else:
        search.top_results = None
        value = (user_list, 0)

    return value


def write_result_to_db(user, search):
    """

    (object User, object Search) -> (None)

    Function writes results to database

    """

    # Write information to Database
    if user is None or search is None:
        print("Отсутствуют данные для записи")
        return

    if not hasattr(search, 'results'):
        print(f"У объекта поиска нет атрибута \"results\"")
        return

    if len(search.results) < 1:
        print("Список результатов поиска пуст. Нечего записывать в БД.")
        return

    city_id, err = vk_db.add_city(user.city)
    vk_common.dprint(2, city_id, err)
    if err in (0, -2):
        # pass
        if city_id is None:
            vk_common.dprint(2, f"Такой город уже существует.")
        else:
            vk_common.dprint(2, f"Добавили город с id = {user.city_id} и с именем \"{user.city['title']}\"")
    else:
        vk_common.dprint(2, f"Не добавлен город, ошибка {err}")
        return

    user_id, err = vk_db.add_user(user)
    vk_common.dprint(2, user_id, err)
    if err in (0, -2):
        if user_id is None:
            vk_common.dprint(2, f"Такой пользователь уже существует.")
        else:
            vk_common.dprint(2, f"Добавили исходного пользователя id = {user_id}")
    else:
        vk_common.dprint(2, err)
        return

    # Write results to Database
    data, err = vk_db.add_search(search)
    if err == 0:
        if data is not None:
            search_id, user_ids, result_ids = data
            vk_common.dprint(2, f"Записали данные о объекте поиска с номером \"{search_id}\" в БД.")
        else:
            vk_common.dprint(2, "При добавлении объекта поиска процедура вернула пустое значение.")
            return
    elif err == -2:
        print("Список результатов поиска пуст. Нечего записывать в БД.")
        return
    else:
        vk_common.dprint(2, f"Не удалось добавить объект поиска в БД, ошибка {err}.")

    # Add record to database about this user's images
    if not hasattr(search, 'top_results'):
        vk_common.dprint(2, f"У объекта поиска нет атрибута \"top_results\"")
        return

    if search.top_results is None:
        vk_common.dprint(2, "Атрибут top_results не заполнен. Нечего записывать в БД.")
        return

    if len(search.top_results) < 1:
        vk_common.dprint(2, "Атрибут top_results не заполнен. Нечего записывать в БД.")
        return

    for top_user in search.top_results:
        rows, err = vk_db.add_user_photos(top_user)
        if err != 0:
            vk_common.dprint(2, "Ошибка при записи информации о фото в БД.")
            return
        else:
            vk_common.dprint(2, f"Записали информацию о фото в БД.", rows)


def execute_mode_search():
    """

    (None) -> (object User, object Search, int)

    Function creates object User and object Search and execute process of searching

    """

    user, err, msg = input_user()
    if err != 0:
        vk_common.dprint(2, "Ошибка при вводе идентификатора пользователя.", err)
        return None, None, -1
    else:
        vk_common.dprint(2, "Процедура ввода пользователя завершена.")

    search_param, err = input_search_parameters(user)
    if err != 0:
        print("Пользователь выбрал выход из программы.")
        return user, None, -1

    user_id_old, err = get_user_id_by_old_searches(user.uid)
    if err != 0:
        vk_common.dprint(2, "Ошибка при получении кол-ва записей в таблице.")
        return user_id_old, None, -1

    user_id_banned, err = vk_db.get_banned_users()
    if err != 0:
        vk_common.dprint(2, "Ошибка при получении списка пользователей, занесенных в черный список.")
        value = (user_id_banned, None, -1)
        return value

    search = vk_search.Search()
    err, msg, users_search = search.search_users(user, search_param, user_id_old, user_id_banned)
    if err == 0:
        if len(users_search) > 0:
            print(f"Произвели поиск по параметрам. Найдено {len(users_search)} записей.")
        else:
            print(f"По данным критериям больше ничего не найдено.")
            value = (user, search, 0)
            return value
    else:
        vk_common.dprint(2, err)
        value = (user, search, -1)
        return value

    users_obj = vk_users.Users(users_search)

    # Detect additional information for searched users
    users_obj.get_additional_info(user)

    # Detect top-10 users by search
    top_users, err = get_top_users_by_search(search, 10)
    if err != 0:
        vk_common.dprint(2, f"Не определена информация о списке топ-10.")
        value = (None, None, -1)
        return value

    if len(top_users) == 0:
        vk_common.dprint(2, f"Не определена информация о списке топ-10.")
        value = (None, None, -1)
        return value

    # Getting photos
    for top_user in top_users:
        # Get top-3 url photos from profile of user and save it
        err, msg, photo_data = top_user.get_top_photos(3)
        if err != 0:
            continue
        vk_common.dprint(2, "Получили данные о фотографиях: ", photo_data)

        top_user.photos = []
        for number, data in enumerate(photo_data, 1):
            vk_common.dprint(2, "Получили данные об одной фото: ", data)

            # Save to file
            if data is None:
                image_file_path = ""
                item_id = None
            else:
                vk_common.mk_dir(vk_common.DIR_IMAGES)
                image_file_path = f"{vk_common.DIR_IMAGES}{top_user.uid}_{number}.jpg"
                item_id = data[0]
                url = data[1]
                vk_common.download_photo_to_file(url, image_file_path)
            top_user.photos.append((item_id, image_file_path))

    # Write top-users to json file
    vk_common.dprint(2, vk_common.func_name(), f"Проверка перед созданием json: top_users = {top_users}")
    if len(top_users) > 0:
        vk_common.mk_dir(vk_common.DIR_JSON)
        is_ok_write = vk_common.write_to_json(f"{vk_common.DIR_JSON}top10_id{user.uid}_{search.age_from}_"
                                              f"{search.age_to}_{search.sex}_{vk_common.get_current_time_label()}.json",
                                              top_users)
        if is_ok_write:
            print("Записан json файл c топ-10 результата поиска.")
        else:
            print("Произошла ошибка записи json-файла.")

    value = (user, search, 0)
    return value


def input_user_by_unique_list_user_id():
    """

    (None) -> (object User, int)

    Function select user from unique list of all users from database

    """

    unique_users, err = vk_db.get_unique_users()
    if err != 0:
        vk_common.dprint(2, "Ошибка при добавлении избранного пользователя", unique_users, err)
        return None, -1
    else:
        if len(unique_users) > 0:
            print(unique_users)
        else:
            print("Список всех пользователей пуст.")
            return None, 0

    txt = "Список всех пользователей:\n"
    for number, user in enumerate(unique_users, 1):
        txt += f"{number}. Пользователь c id = {user[0]}, {user[1]} {user[2]}\n"

    number = int(input("Введите порядковый номер соответствующий id пользователя из списка:\n" + txt).strip())
    vk_common.dprint(2, f"unique_users = {unique_users}")
    user_id_need = unique_users[number - 1][0]
    vk_common.dprint(2, f"user_id_need = {user_id_need}")
    user_need, msg, err = get_user_by_id(user_id_need)
    if err != 0:
        print(f"Ошибка: В системе ВК не определен пользователь с id = {user_id_need}")
        return None, -1
    else:
        vk_common.dprint(2, f"В системе ВК определен пользователь {user_need.last_name} {user_need.first_name} "
                            f"с id = {user_need.uid}")

    return user_need, 0


def add_favorite_user():
    """

    (None) -> (None)

    Function adds favorite user from unique list of all users

    """

    print("Добавление пользователя в список избранных:")
    favorite_user, err = input_user_by_unique_list_user_id()
    if favorite_user is None:
        return

    print(f"Добавим пользователя с id = {favorite_user.uid} {favorite_user.last_name} "
          f"{favorite_user.first_name} в список избранных.")
    updated_rows, err = vk_db.set_favorite_property_by_user(favorite_user.uid, 1)
    if err == 0:
        print(f"Признак избранности установлен. Было обновлено {updated_rows} записей.")
    else:
        vk_common.dprint(2, "Ошибка установки признака избранности у пользователя.")


def add_banned_user():
    """

    (None) -> (None)

    Function adds banned user from unique list of all users

    """

    print("Добавление пользователя в черный список:")
    banned_user, err = input_user_by_unique_list_user_id()
    if banned_user is None:
        return

    print(f"Добавим пользователя с id = {banned_user.uid} {banned_user.last_name} "
          f"{banned_user.first_name} в черный список.")
    updated_rows, err = vk_db.set_favorite_property_by_user(banned_user.uid, 2)
    if err == 0:
        print(f"Пользователь с id = {banned_user.uid} добавлен в черный список. Было обновлено {updated_rows} записей.")
    else:
        vk_common.dprint(2, f"Ошибка добавления пользователя с id = {banned_user.uid} в черный список.")


def execute_mode_like_images():
    """

    (None) -> (None)

    Function execute mode of liking or disliking top-photos of top-users

    """

    rows, err = vk_db.get_all_search()
    if err != 0:
        vk_common.dprint(2, "Ошибка при запросе списка объектов поиска.")
        return

    if len(rows) <= 0:
        print("Список объектов поиска пуст.")
        return

    # It need to input search id
    print("Список информации обо всех объектах поиска: ")
    list_search_id = list()
    for row in rows:
        # [(1, 5521318, Decimal('23'), Decimal('45'), Decimal('0'))]
        search_id, user_id, age_from, age_to, sex_id = row
        sex = vk_common.sex_to_char(sex_id)
        list_search_id.append(search_id)

        if len(sex.strip()) == 0:
            sex_str = ", пол: любой"
        else:
            sex_str = f", пол: {sex}"

        if age_from == age_to:
            age_str = f", {age_from} лет"
        else:
            age_str = f" от {age_from} до {age_to} лет"

        print(f"{search_id}. Для пользователя с id = {user_id}{age_str}{sex_str}.")

    while True:
        search_id = int(input("Введите идентификатор поиска из списка: ").strip())
        if search_id not in list_search_id:
            print("Введенное информация не соответствует порядковому номеру из списка.")
        else:
            # Get searched users by search id
            rows, err = vk_db.get_results_by_search_id_exist_photo(search_id)
            if err != 0:
                vk_common.dprint("1, Ошибка при получении записей объекта поиска.")
                return
            else:
                vk_common.dprint(2, f"Получили список id пользователей, у которых есть фото: ", rows)

            users_photos = list()
            user_id = None
            user_photos = list()
            for row in rows:
                if row[3] is None:
                    continue
                if user_id != row[0]:
                    if user_id is not None:
                        users_photos.append((user_id, user_photos))
                        user_photos = list()
                        user_id = row[0]
                        user_photos.append(row[3])
                    else:
                        user_id = row[0]
                        user_photos.append(row[3])
                else:
                    user_photos.append(row[3])
            users_photos.append((user_id, user_photos))

            vk_common.dprint(2, "Список после подготовки данных", users_photos)

            if len(users_photos) <= 1 and users_photos[0][0] is None:
                print("Нет фото для загрузки в приложение, выберите другой идентификатор поиска.")
            else:
                break

    # Execute app for liking and disliking photos of these users
    v_images = vk_gdi.LikeImages(users_photos)
    if v_images is not None:
        vk_common.dprint(2, "Объект лайкера создан.")
    v_images.execute_app()


def execute_mode_count_rec_by_one_request():
    """

    (None) -> (None)

    Function execute mode input new value of parameter application COUNT_REC_BY_ONE_REQUEST
    which affects to speed and result

    """

    while True:
        cnt_users = int(input("Введите кол-во записей получаемых одним запросом(1..1000)): ").strip())
        if cnt_users < 1 or cnt_users > 1000:
            print("Параметр должен быть в диапазоне от 1 до 1000.")
            continue
        else:
            vk_search.COUNT_REC_BY_ONE_REQUEST = cnt_users
            vk_common.dprint(2, f"Параметр COUNT_REC_BY_ONE_REQUEST изменён и теперь равен "
                                f"{vk_search.COUNT_REC_BY_ONE_REQUEST}.")
            break


def execute_mode_divide_search_by_month():
    """

        (None) -> (None)

        Function execute mode divide search by month of parameter application MODE_DIVIDE_SEARCH_BY_MONTH
        which affects to amount users which we get from VK

        """

    while True:
        mode = int(input("Включить или выключить режим разделения запроса по 12 месяцам(0=выкл или 1=вкл)): ").strip())
        if mode not in (0, 1):
            print("Параметр может принимать значение 0 или 1.")
            continue
        else:
            vk_search.MODE_DIVIDE_SEARCH_BY_MONTH = mode
            vk_common.dprint(2, f"Параметр MODE_DIVIDE_SEARCH_BY_MONTH изменён и теперь равен "
                                f"{vk_search.MODE_DIVIDE_SEARCH_BY_MONTH}.")
            break


def execute_mode_token_str():
    """

    (None) -> (None)

    Function prints string for getting token through address line of browser

    """

    vk_common.auth()


def main():
    """

    (None) -> None

    Main function describe main functionality

    """

    # Create DB at first
    vk_db.create_db()

    # Get token from file
    filename_token = "data\\token.txt"
    token = vk_common.get_token(filename_token)
    if len(token) == 0:
        return

    while True:
        print("")
        mode = int(input(f"Выберите режим:\n1. Поиск и получение json файла результата;\n2. Очистка БД;\n"
                         f"3. Просмотр БД;\n4. Изменение параметра \"кол-во записей, получаемых одним запросом к ВК\" "
                         f"(текущее значение = {vk_search.COUNT_REC_BY_ONE_REQUEST});\n"
                         f"5. Режим получения большего кол-ва записей за счет деления запроса по месяцам "
                         f"(текущее значение = {vk_search.MODE_DIVIDE_SEARCH_BY_MONTH});\n"
                         f"6. Добавить в избранное;\n"
                         f"7. Добавить в черный список;\n8. Лайкер;\n9. Удалить содержимое каталогов;\n"
                         f"10. Получить строку для получения токена ВК;\n"
                         f"11. Выход;\n>> ").strip())
        if mode == 1:
            user, search, err = execute_mode_search()
            if err != 0:
                print("Возникла ошибка в процедуре поиска.")
                return

            # Write information about search to database fully
            write_result_to_db(user, search)

        # ReCreate Database
        elif mode == 2:
            msg, err = vk_db.re_create_db()
            if err != 0:
                print("Возникала ошибка при пересоздании БД.")
                return -1
            else:
                print("Пересоздали БД.")

        elif mode == 3:
            is_print = vk_db.print_all_tables()
            if not is_print:
                print("Таблицы пусты.")

        elif mode == 4:
            execute_mode_count_rec_by_one_request()

        elif mode == 5:
            execute_mode_divide_search_by_month()

        elif mode == 6:
            add_favorite_user()

        elif mode == 7:
            add_banned_user()

        elif mode == 8:
            execute_mode_like_images()

        elif mode == 9:
            vk_common.recreate_dirs()

        elif mode == 10:
            execute_mode_token_str()

        # Exit from dialog
        elif mode == 11:
            break


if __name__ == "__main__":
    main()
