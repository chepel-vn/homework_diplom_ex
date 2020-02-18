import vk_common
import vk_user
import vk_search
import vk_db


def input_user():
    # Input user id
    user = None
    while True:
        id_string = input("Введите id пользователя ВКонтакте (число=id пользователя или строка=nickname): ").strip()
        # id_string = '171691064'
        # id_string = '5521318'

        try:
            int(id_string)
            id_string = f"id{id_string}"
        except ValueError:
            pass

        if vk_common.test_id(id_string):
            user = vk_user.User()
            user.assign_by_nickname(id_string)
            if user.error["error"] != 0:
                if user.error["error"] == 113:
                    print(f"Аккаунт ВК с id = \"{id_string}\" не определен в системе.")
                    continue
                else:
                    print(f"Возникла ошибка {user.error['error']}: {user.error['msg']}.")
                    return
            else:
                break
        else:
            print("Введенная строка не может быть идентификатором пользователя.")
            continue
    return user


def input_search_parameters(user):
    search_param = dict()

    # If user's age didn't detect then mode "age_method_search=0" we can't use
    if user.age is not None:
        # Input age_from and age_to
        age_method_search = int(input("Поиск ровесников или в диапазоне(0=ровесники, 1=диапазон, q=выход)): ").strip())
    else:
        age_method_search = 1

    if age_method_search == 1:

        # If user's age didn't detect then mode "age_method_search_ex=0" we can't use
        if user.age is not None:
            age_method_search_ex = int(input("Поиск по диапазону(0=относительный 1=абсолютный диапазон, "
                                             "q=выход)): ").strip())
        else:
            age_method_search_ex = 1

        if age_method_search_ex == 0:
            age_div = int(input("Введите +- кол-во лет относительно возраста пользователя(q=выход)): ").strip())
            age_from = user.age - age_div
            age_to = user.age + age_div
            # print(f"age_from = {age_from}; age_to = {age_to}")
        else:
            pass
            age_from = int(input("Введите параметр \"Возраст ОТ\"(q=выход)): ").strip())
            age_to = int(input("Введите параметр \"Возраст ДО\"(q=выход)): ").strip())
            # print(f"age_from = {age_from}; age_to = {age_to}")
    else:
        age_from = user.age
        age_to = user.age
        # print(f"age_from = {age_from}; age_to = {age_to}")

    # Input sex as parameter of search
    sex = int(input("Поиск по полу (0=пол не указан, 1=женский; 2=мужской, q=выход)): ").strip())
    # sex = 1

    search_param['age_from'] = age_from
    search_param['age_to'] = age_to
    # search_param['age_from'] = 25
    # search_param['age_to'] = 30
    search_param['sex'] = sex

    return search_param


def main():
    """

    (None) -> None

    Main function describe main functionality

    """

    # text1 = 'ввелосипед, путешествия, песни под гитару, романтика, люди, поезда, вокзалы, свобода, мечта'
    # text2 = 'Смотреть кино, арт-хаус, компьютерные игры, кошки(коти, мяфсики), Ирландия, манга, косплей, ходить в '
    #         'поход, фэнтази, фантастика, пираты, постмодернизм, живопись, графика, дети ночи, Сальвадор Дали, '
    #         'рисовать, архитектура, гулять по городу, слушать музыку, играть на музыкальных инструментах, валять '
    #         'дурака, ерничать, готика, киберпанк, холодное и огнестрельное оружие, страйкбол, кибер-готика, '
    #         'стимпанк, нуар, пин-ап, ретро стиль, романтика, ролевые игры, цинизм, мрачность, ночной город, '
    #         'вампиры, фолк, эльфы, финансы, фондовый рынок и ценные бумаги, малый бизнес, страйкбол, историческая '
    #         'реконструкция, Вторая мировая война, великие географические открытия'
    # cnt = vk_common.is_common_by_text(text1, text2)
    # print(cnt)
    # return

    # Print data of all VK tables
    # vk_db.print_all_tables()
    # return

    # Made it for getting token
    # vk_common.auth()
    # return

    # Get token from file
    filename_token = "data\\token.txt"
    token = vk_common.get_token(filename_token)
    if len(token) == 0:
        return

    while True:
        mode = int(input("Режим(0=поиск, 1=очистка бд; 2=смотрим бд, 3=ввод кол-ва записей одного запроса, "
                         "4=выход)): ").strip())

        if mode == 1:
            # ReCreate Database
            msg, err = vk_db.re_create_db()
            if err == -1:
                return -1
            continue
        elif mode == 2:
            vk_db.print_all_tables()
            continue
        elif mode == 3:
            while True:
                cnt_users = int(input("Введите кол-во записей получаемых одним запросом(1..1000)): ").strip())
                if cnt_users < 1 or cnt_users > 1000:
                    print("Параметр должен быть в диапазоне от 1 до 1000.")
                    continue
                else:
                    vk_search.COUNT_REC_BY_ONE_REQUEST = cnt_users
                    print(f"Параметр COUNT_REC_BY_ONE_REQUEST изменён и теперь равен "
                          f"{vk_search.COUNT_REC_BY_ONE_REQUEST}.")
                    break
        elif mode == 4:
            break
        else:
            user = input_user()
            search_param = input_search_parameters(user)

            # Write source user to Database
            city_id, err = vk_db.add_city(user.city)
            if err in (0, -2):
                pass
                # print(f"Добавили город с id = {user.city_id} и с именем \"{user.city['title']}\"")
            else:
                print(err)
                return

            user_id, err = vk_db.add_user(user)
            if err == 0:
                pass
                # print(f"Добавили исходного пользователя id = {user_id}")
            else:
                print(err)
                return

            search = vk_search.Search()
            err, msg, users_search = search.search_users(user, search_param)
            if err == 0:
                pass
                # print(f"Произвели поиск по параметрам.")
            else:
                print(err)
                return

            # Detect additional information for searched users
            for item in users_search:
                item.get_additional_info(user)

            # Write results to Database
            # for us in search.results:
            #     print(us.id, us.cnt_common_friends, us.cnt_common_groups, us.cnt_common_interests,
            #           us.cnt_common_books, us.cnt_common_music)

            search_id, err = vk_db.add_search1(search)
            if err == 0:
                print(f"Добавили \"поиск\" номер {search_id}")
            else:
                print(f"Не удалось добавить объект поиска в БД, ошибка {err}.")
                return

            user_ids, err = vk_db.add_users1(search.results)
            if err == 0:
                print(f"Удалось добавить список пользователей в БД, {user_ids}.")
            else:
                print(f"Не удалось добавить список пользователей в БД, ошибка {err}.")
                return

            result_ids, err = vk_db.add_results1(search_id, search.results)
            if err == 0:
                print(f"Добавили результаты поиска в БД, {result_ids}.")
            else:
                print(f"Не удалось добавить результаты поиска в БД, ошибка {err}.")
                return

            # info, err = vk_db.add_search(search)
            # search_id, user_ids, result_ids = info
            # if err != 0:
            #     print(f"Не удалось добавить объект поиска в БД, ошибка {err}.")
            #     # print(f"Добавили \"поиск\" номер {search_id}")
            #     return

            # Select top-10 rows in need order
            rows, err = vk_db.get_top_users_by_search_id(search_id, 10)
            if err == 0:
                if len(rows) == 0:
                    print("Поиск не дал результатов или все результаты получены и записаны в БД.")
                # vk_db.print_cursor(rows)
            else:
                print(f"Не удалось выполнить запрос топ-10 записей, ошибка {err}.")

            top_users = []
            for row in rows:
                user_info_dict = vk_db.get_user_by_row(row)
                print(row)
                top_user = vk_user.User()
                top_user.assign_by_user_info(user_info_dict)

                # Get top-3 url photos from profile of user and save it
                err, msg, photo_urls = top_user.get_top_photos(3)
                if err != 0:
                    continue

                top_user.photos = []
                for number, url in enumerate(photo_urls, 1):
                    # Save to file
                    if url is None:
                        image_file_path = ""
                    else:
                        image_file_path = f"images/{top_user.id}_{number}.jpg"
                        vk_common.download_photo_to_file(url, image_file_path)
                    top_user.photos.append(image_file_path)

                # Add record to database about this user's images
                vk_db.add_user_photos(top_user)
                top_users.append(top_user)

            # Write top-users to json file
            vk_common.write_to_json(f"results/top10_{search_id}.json", top_users)

            # Print data of all VK tables
            # vk_db.print_all_tables()


if __name__ == "__main__":
    main()

    # TODO если задан диапазон возраста то в топ10 попадают сначала кто ближе по возрасту(сначала ровестники итд
    # TODO оптимизация с помощью vk execute
    # TODO написать тесты и отладить функцию, ищущую совпадения с помощью анализа текста
    # TODO отладить неповтор результата поиска
    # TODO определять тех пользователей из результата поиска, и обрабатывать только их, остальных пропускать

