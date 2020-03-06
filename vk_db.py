import psycopg2
import vk_common
import vk_user

# vk_cities:  "id,name"
# vk_users:   "id,first_name,last_name,age,interests,books,music,sex,city_id,favorite"
# vk_search:  "id,user_id,age_from,age_to,sex"
# vk_results: "id,search_id,user_id,cnt_common_friends,cnt_common_groups,cnt_common_interests,cnt_common_books,
#              cnt_common_music"
# vk_photos:  "id,user_id,top_id,image_file_path, item_id"

CONNECT_STRING = "dbname=test_db user=test password=123 host=127.0.0.1 port=5432"
TABLES_NAMES = ("vk_photos", "vk_cities", "vk_users", "vk_search", "vk_results")


def request_decorator(function_to_decorate):
    """

    (function link) -> function link

    Function decorator for use connection and cursor for access to database

    """

    def wrapper(*args, **kwargs):
        conn = None
        curs = None
        err = (None, -1)
        try:
            conn = psycopg2.connect(CONNECT_STRING)
            conn.autocommit = False
            curs = conn.cursor()

            # Function for select, insert, update request
            function_to_decorate(curs, *args, **kwargs)
            try:
                result_records = curs.fetchall()
                err = (result_records, 0)
            except psycopg2.ProgrammingError:
                err = (None, 0)
        except (Exception, psycopg2.DatabaseError) as error:
            vk_common.dprint(2, error)
            if error.find(" не существует") == -1 and error.find("ОШИБКА:  отношение ") == -1:
                vk_common.dprint(2, "Error in transaction Reverting all other operations of a transaction ", error)
            if conn is not None:
                conn.rollback()
            err = (None, -1)
        finally:
            if conn is not None:
                conn.commit()
                curs.close()
                conn.close()
            return err
    return wrapper


def sql_execute_decorator(function_to_decorate):
    """

    (function link) -> function link

    Function decorator for use connection and cursor for access to database

    """

    def wrapper(*args, **kwargs):
        conn = None
        curs = None
        err = (None, 0)
        try:
            conn = psycopg2.connect(CONNECT_STRING)
            conn.autocommit = False
            curs = conn.cursor()

            # Function for select, insert, update request
            value = function_to_decorate(curs, *args, **kwargs)
            err = (value, 0)
        except (Exception, psycopg2.DatabaseError) as error:
            vk_common.dprint(2, error)
            cnt = vk_common.is_common_by_text('значение ключа нарушает ограничение уникальности', error)
            if cnt == 0:
                vk_common.dprint(2, "Error in transaction Reverting all other operations of a transaction ", error)
                if conn is not None:
                    conn.rollback()
                err = (None, -1)
            else:
                err = (None, -2)
        finally:
            if conn is not None:
                conn.commit()
                curs.close()
                conn.close()
            return err
    return wrapper


@request_decorator
def clear_db(curs):
    """

    (cursor link) -> None

    Function truncates all tables

    """

    for table_idx in (0, 4, 3, 2, 1):
        sql_text = f"""TRUNCATE TABLE {TABLES_NAMES[table_idx]} CASCADE;"""
        curs.execute(sql_text)


@request_decorator
def request_sql(curs, sql_string):
    """

    (cursor link) -> None

    Function execute any sql request from sql_string

    """

    curs.execute(sql_string)


@sql_execute_decorator
def drop_table(curs, table_name):
    """

    (cursor link) -> None

    Function drops table by table name

    """

    sql_text = f"""DROP TABLE if exists {table_name}"""
    vk_common.dprint(2, vk_common.func_name(), f"Текст запроса: {sql_text}")
    curs.execute(sql_text)


def drop_db():
    """

    (cursor link) -> None

    Function drops all tables

    """

    is_drop = 0
    is_exist = 0
    for table_idx in (0, 4, 3, 2, 1):
        result = is_exists_table(TABLES_NAMES[table_idx])
        if result:
            is_exist += 1
        rows, err = drop_table(TABLES_NAMES[table_idx])
        if err == 0:
            is_drop += 1
    vk_common.dprint(2, vk_common.func_name(), f"Существовали {is_exist} таблиц.")
    vk_common.dprint(2, vk_common.func_name(), f"Удалили {is_drop} таблиц.")

    if is_drop != is_exist:
        return -1
    else:
        return is_drop


@request_decorator
def create_db(curs):
    """

    (cursor link) -> None

    Function creates all tables

    """

    # "id,name"
    sql_text = f"""CREATE TABLE if not exists {TABLES_NAMES[1]} (
                    id numeric(4) NOT NULL PRIMARY KEY,
                    name varchar(100));
                    """
    curs.execute(sql_text)
    vk_common.dprint(2, vk_common.func_name(), f"Создали таблицу {TABLES_NAMES[1]}")

    # "id,first_name,last_name,age,interests,books,music,sex,city_id,favorite"
    sql_text = f"""CREATE TABLE if not exists {TABLES_NAMES[2]} (
                id numeric(10) NOT NULL PRIMARY KEY,
                first_name varchar(50),
                last_name varchar(50),              
                age numeric(3),
                interests varchar(3000),
                books varchar(3000),
                music varchar(3000),
                sex numeric(1),
                city_id integer references {TABLES_NAMES[1]}(id),
                favorite numeric(1));
                """
    curs.execute(sql_text)
    vk_common.dprint(2, vk_common.func_name(), f"Создали таблицу {TABLES_NAMES[2]}")

    # "id,user_id,age_from,age_to,sex"
    sql_text = f"""CREATE TABLE if not exists {TABLES_NAMES[3]} (
                id serial PRIMARY KEY,
                user_id integer references {TABLES_NAMES[2]}(id),               
                age_from numeric(3),
                age_to numeric(3),
                sex numeric(1));
                """
    curs.execute(sql_text)
    vk_common.dprint(2, vk_common.func_name(), f"Создали таблицу {TABLES_NAMES[3]}")

    # "id,search_id,user_id,cnt_common_friends,cnt_common_groups,cnt_common_interests,cnt_common_books,cnt_common_music"
    sql_text = f"""CREATE TABLE if not exists {TABLES_NAMES[4]} (
                id serial PRIMARY KEY,
                search_id integer references {TABLES_NAMES[3]}(id),                
                user_id integer references {TABLES_NAMES[2]}(id),
                cnt_common_friends numeric(4),
                cnt_common_groups numeric(4),
                cnt_common_interests numeric(4),
                cnt_common_books numeric(4),
                cnt_common_music numeric(4));
                """
    curs.execute(sql_text)
    vk_common.dprint(2, vk_common.func_name(), f"Создали таблицу {TABLES_NAMES[4]}")

    # "id,user_id,top_id,image_file_path"
    sql_text = f"""CREATE TABLE if not exists {TABLES_NAMES[0]} (
                id serial PRIMARY KEY,
                user_id integer references {TABLES_NAMES[2]}(id),
                top_id numeric(2),
                image_file_path varchar(100),
                item_id integer);
                """
    curs.execute(sql_text)
    vk_common.dprint(2, vk_common.func_name(), f"Создали таблицу {TABLES_NAMES[0]}")


def re_create_db():
    """

    (None) -> None

    Function recreated all tables

    """

    result = drop_db()
    vk_common.dprint(2, vk_common.func_name(), f" Результат работы drop_db равен {result}.")
    if result == -1:
        return "", -1

    msg, err = create_db()
    vk_common.dprint(2, vk_common.func_name(), f"Результат работы create_db равен ({msg} {err})")
    return msg, err


@sql_execute_decorator
def add_city(curs, city):
    """

    (cursor link, dict) -> integer

    Function add city to table of cities

    """

    return add_city_execute(curs, city)


def add_city_execute(curs, city):
    """

    (cursor link, dict) -> int

    Function add city to table of cities

    """

    sql_text = f"insert into {TABLES_NAMES[1]} (id, name) values (%s, %s) returning id"
    curs.execute(sql_text, (city['id'], city['title']))
    rec_id = curs.fetchone()[0]
    return rec_id


@sql_execute_decorator
def add_user_photos(curs, user):
    """

    (cursor link, object User) -> integer

    Function add user's photos to table of photos

    """
    if not hasattr(user, 'photos'):
        vk_common.dprint(2, vk_common.func_name(), "Не определен атрибут photos.")
        return
    vk_common.dprint(2, vk_common.func_name(), "Входные данные user.photos: ", user.photos)

    rec_ids = list()
    for number, photo in enumerate(user.photos, 1):
        item_id = photo[0]
        image_file_path = photo[1]

        sql_text = f"insert into {TABLES_NAMES[0]} (user_id, top_id, image_file_path, item_id) " \
                   f"values (%s, %s, %s, %s) returning id"
        curs.execute(sql_text, (user.uid, number, image_file_path, item_id))
        rec_id = curs.fetchone()[0]
        rec_ids.append(rec_id)
    return rec_ids


def add_user_execute(curs, user):
    """

    (cursor link, object User) -> None

    Function adds user to table of users

    """

    sql_text = f"insert into {TABLES_NAMES[2]} (id, first_name, last_name, age, interests, books, music, sex, " \
               f"city_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning id"
    curs.execute(sql_text, (user.uid, user.first_name, user.last_name, user.age, user.interests, user.books,
                            user.music, user.sex, user.city_id))
    rec_id = curs.fetchone()[0]
    return rec_id


@sql_execute_decorator
def add_user(curs, user):
    """

    (cursor link, object User) -> integer

    Function add one VK user

    """

    rec_id = add_user_execute(curs, user)
    return rec_id


@request_decorator
def get_results_by_search_id_exist_photo(curs, search_id):
    """

    (cursor link, integer, integer) -> None

    Function gets search results by search_id only about users with photos

    """

    sql_text = f"select u.id, u.last_name, u.first_name, f.item_id from {TABLES_NAMES[4]} rs " \
               f"join {TABLES_NAMES[2]} u on u.id = rs.user_id " \
               f"join {TABLES_NAMES[0]} f on f.user_id = rs.user_id " \
               f"where rs.search_id = %s " \
               f"and EXISTS (select 1 from {TABLES_NAMES[0]} where user_id = u.id and item_id IS NOT NULL) "
    curs.execute(sql_text, [search_id])


def print_cursor(curs):
    """

    (cursor link) -> None

    Function helps to print content of cursor

    """

    # rs.search_id, rs.user_id, rs.cnt_common_friends, rs.cnt_common_groups, u.age, u.interests, u.books, u.music,
    # rs.cnt_common_interests, rs.cnt_common_books, rs.cnt_common_music
    for row in curs:
        print(f"search_id: {row[0]}; user_id: {row[1]}; common_friends: {row[2]}; common_groups: {row[3]}; "
              f"age: {row[4]}; interests: {row[5]}; books: {row[6]}; music: {row[7]}; "
              f"cnt_common_interests: {row[8]}; cnt_common_books: {row[9]}; cnt_common_music: {row[10]};")


@request_decorator
def get_data_from_table(curs, table_name):

    """

    (cursor link, string) -> None

    Function prints data of table with name = table_name

    """

    curs.execute(f"""select * from {table_name} """)


def print_table(table_name):
    """

    (cursor link, string) -> None

    Function  prints content of table by table name beautifully

    """

    rows, err = get_data_from_table(table_name)
    if err != 0:
        return 0

    if len(rows) == 0:
        return 0

    print("")
    print(f"Таблица \"{table_name}\":")
    for row in rows:
        if table_name == TABLES_NAMES[2]:
            print(f"user_id: {row[0]}; fio: {row[1]} {row[2]}; age: {row[3]}; interests: {row[4]}; "
                  f"books: {row[5]}; music: {row[6]}; sex: {vk_common.sex_to_char(row[7])}; city_id: {row[8]}; "
                  f"favorite: {row[9]};")
        elif table_name == TABLES_NAMES[3]:
            print(f"search_id: {row[0]}; user_id: {row[1]}; age_from: {row[2]}; age_to: {row[3]}; "
                  f"sex: {vk_common.sex_to_char(row[4])};")
        elif table_name == TABLES_NAMES[4]:
            print(f"search_id: {row[1]}; user_id: {row[2]}; common_friends: {row[3]}; common_groups: {row[4]};"
                  f"cnt_common_interests: {row[5]}; cnt_common_books {row[6]}; cnt_common_music {row[7]};")
        elif table_name == TABLES_NAMES[1]:
            print(f"city_id: {row[0]}; name: {row[1]};")
        else:
            print(row)

    return 1


def is_exists_table(table_name):
    """

    (string) -> bool

    Function detect existing of table of database by table name

    """

    sql_text = f"""select 1 from {table_name}"""
    records, err = request_sql(sql_text)
    if err != 0:
        return False
    else:
        return True


def print_all_tables():
    """

    (None) -> None

    Function prints data of all tables from database

    """

    is_print = 0
    for i in range(0, 5):
        result = print_table(TABLES_NAMES[i])
        is_print += result

    if is_print > 0:
        return True
    else:
        return False


def get_user_by_row(row):
    """

    (list) -> None

    Function gets dict user's info from row of reply from database

    """

    # rs.search_id, rs.user_id, u.age, u.sex, u.interests, u.books, u.music,
    # rs.cnt_common_interests, rs.cnt_common_books, rs.cnt_common_music, rs.cnt_common_friends, rs.cnt_common_groups
    user_info = vk_user.get_info_dict(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10],
                                      row[11], row[12], row[13])
    return user_info


@request_decorator
def get_users_by_old_searches(curs, user_id):
    """

    (cursor link, int) -> None

    Function gets users list which already saved in database by user_id

    """

    sql_text = f"select rs.user_id " \
               f"from {TABLES_NAMES[4]} rs " \
               f"join {TABLES_NAMES[3]} s on s.id = rs.search_id " \
               f"where s.user_id = %s and rs.user_id in (select user_id from {TABLES_NAMES[0]})"
    curs.execute(sql_text, [user_id])


@request_decorator
def get_user(curs, user_id):
    """

    (cursor link, int) -> None

    Function gets data about user by user_id

    """

    sql_text = f"select * from {TABLES_NAMES[2]} where id = %s"
    curs.execute(sql_text, user_id)


@request_decorator
def get_count_rows_of_table(curs, table_name):
    """

    (cursor link, string) -> None

    Function gets count rows of table by table name

    """

    sql_text = f"select count(*) from {table_name}"
    curs.execute(sql_text)


@request_decorator
def get_city_name(curs, city_id):
    """

    (cursor link, int) -> None

    Function gets name of city by city id

    """

    sql_text = f"select name from {TABLES_NAMES[1]} where id = %s"
    curs.execute(sql_text, [city_id])


@sql_execute_decorator
def set_favorite_property_by_user(curs, user_id, value):
    """

    (cursor link, int, int) -> int or None

    Function sets favorite user

    """

    if value not in (1, 2):
        vk_common.dprint(1, "Значение поля favorite может принимать значения 1-избранный 2-черный список")
        return

    sql_text = f"UPDATE {TABLES_NAMES[2]} SET favorite = %s WHERE id = %s returning id"
    curs.execute(sql_text, (value, user_id))
    updated_rows = curs.rowcount
    return updated_rows


@request_decorator
def get_unique_users(curs):
    """

    (cursor link) -> None

    Function gets list of unique user id from table of users

    """

    sql_text = f"select distinct id, last_name, first_name from {TABLES_NAMES[2]}"
    curs.execute(sql_text)


@request_decorator
def get_banned_users(curs):
    """

    (cursor link) -> None

    Function gets list of banned user id from table of users

    """

    sql_text = f"select id from {TABLES_NAMES[2]} where favorite=2"
    curs.execute(sql_text)


@request_decorator
def get_all_users(curs):
    """

    (cursor link) -> None

    Function gets list of all user id from table of users

    """

    sql_text = f"select id from {TABLES_NAMES[2]}"
    curs.execute(sql_text)


@request_decorator
def get_all_cities(curs):
    """

    (cursor link) -> None

    Function gets list of all user id from table of users

    """

    sql_text = f"select id from {TABLES_NAMES[1]}"
    curs.execute(sql_text)


@request_decorator
def get_photo_info_by_user_id(curs, user_id):
    """

    (cursor link, user_id) -> None

    Function gets data about photos of user by user id

    """

    # "id,user_id,top_id,image_file_path"
    sql_text = f"select image_file_path, item_id from {TABLES_NAMES[0]} where user_id = %s"
    curs.execute(sql_text, [user_id])


@request_decorator
def get_all_search(curs):
    """

    (cursor link) -> None

    Function gets list of search id from table of objects of search

    """

    # "id,user_id,age_from,age_to,sex"
    sql_text = f"select id, user_id, age_from, age_to, sex from {TABLES_NAMES[3]}"
    curs.execute(sql_text)


def add_search(search):
    """

    (object Search) -> ((int, list, list) or None, int)

    Function adds object of search to database fully

    """

    # Get list of all users from DB
    rows, err = get_all_cities()
    if err != 0:
        vk_common.dprint(1, "Ошибка при получении списка всех городов.")
        return None, -1

    city_ids = set()
    for row in rows:
        city_ids.add(row[0])
    vk_common.dprint(2, "Список всех городов: ", city_ids)

    # Get list of users which we want to add
    city_add_ids = set()
    for user in search.results:
        city_add_ids.add(user.city_id)
    vk_common.dprint(2, "Список добавляемых городов: ", city_add_ids)

    city_ids_intersect = city_ids.intersection(city_add_ids)
    vk_common.dprint(2, "Список пересечения: (города) ", city_ids_intersect)

    conn = None
    err = (None, -1)
    try:
        conn = psycopg2.connect(CONNECT_STRING)
        conn.autocommit = False
        with conn.cursor() as curs:

            try:
                sql_text = f"insert into {TABLES_NAMES[3]} (user_id, age_from, age_to, sex) values (%s, %s, %s, %s) " \
                           f"returning id"
                curs.execute(sql_text, (search.user_id, search.age_from, search.age_to, search.sex))
                search_id = curs.fetchone()[0]
            except (Exception, psycopg2.DatabaseError) as error:
                vk_common.dprint(1, f"Не могу добавить запись в таблицу {TABLES_NAMES[3]}", error)

            vk_common.dprint(2, "Добавили search_id: ", search_id)

            curs.execute("SAVEPOINT city_successfully")

            city_ids = []
            for user in search.results:

                if user.city_id in city_ids_intersect:
                    continue

                vk_common.dprint(2, f"-------------->> Смотрим на очередной city_id = {user.city_id}")

                try:
                    sql_text = f"insert into {TABLES_NAMES[1]} (id, name) values (%s, %s) returning id"
                    curs.execute(sql_text, (user.city_id, user.city_title))
                    rec_id = curs.fetchone()[0]
                    city_ids.append(rec_id)
                    curs.execute("SAVEPOINT city_successfully")
                    vk_common.dprint(2, f"-------------->> Добавили город корректно city_id = {user.city_id}")

                # except (Exception, psycopg2.DatabaseError, psycopg2.errors.UniqueViolation) as error:
                except (Exception, psycopg2.DatabaseError) as error:
                    vk_common.dprint(2, "error type: ", type(error))
                    vk_common.dprint(2, "error args: ", error.args)
                    str_err = vk_common.is_common_by_text("повторяющееся значение ключа нарушает ограничение "
                                                          "уникальности", error.args[0])
                    vk_common.dprint(2, "str_err = ", str_err)
                    if str_err > 0:
                        vk_common.dprint(1, f"Не могу добавить запись в таблицу {TABLES_NAMES[1]}", error)

                    curs.execute("ROLLBACK TO SAVEPOINT city_successfully")
                    vk_common.dprint(2, f"-------------->> Откат назд после добавления city_id = {user.city_id}")

            curs.execute("SAVEPOINT user_successfully")

            user_ids = []
            for user in search.results:
                # if user.uid in user_ids_intersect:
                #     continue

                vk_common.dprint(2, f"-------------->> Смотрим на очередной user_id = {user.uid}")

                try:
                    sql_text = f"insert into {TABLES_NAMES[2]} (id, first_name, last_name, age, interests, books, " \
                               f"music, sex, city_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning id"
                    curs.execute(sql_text, (user.uid, user.first_name, user.last_name, user.age, user.interests,
                                            user.books, user.music, user.sex, user.city_id))
                    rec_id = curs.fetchone()[0]
                    user_ids.append(rec_id)

                    curs.execute("SAVEPOINT user_successfully")
                    vk_common.dprint(2, f"-------------->> Добавили пользователя корректно user_id = {user.uid}")

                # except (Exception, psycopg2.DatabaseError, psycopg2.errors.UniqueViolation) as error:
                except (Exception, psycopg2.DatabaseError) as error:
                    vk_common.dprint(2, "error type: ", type(error))
                    vk_common.dprint(2, "error args: ", error.args)
                    str_err = vk_common.is_common_by_text("повторяющееся значение ключа нарушает ограничение "
                                                          "уникальности", error.args[0])
                    vk_common.dprint(2, "str_err = ", str_err)
                    if str_err > 0:
                        vk_common.dprint(1, f"Не могу добавить запись в таблицу {TABLES_NAMES[2]}", error)

                    curs.execute("ROLLBACK TO SAVEPOINT user_successfully")
                    vk_common.dprint(2, f"-------------->> Откат назд после добавления user_id = {user.uid}")

            vk_common.dprint(2, "Добавили пользователей: ", user_ids)

            try:
                result_ids = []
                for user in search.results:
                    sql_text = f"insert into {TABLES_NAMES[4]} (search_id, user_id, cnt_common_friends, " \
                               f"cnt_common_groups, cnt_common_interests, cnt_common_books, cnt_common_music) values " \
                               f"(%s, %s, %s, %s, %s, %s, %s) returning id"
                    curs.execute(sql_text, (search_id, user.uid, user.cnt_common_friends, user.cnt_common_groups,
                                            user.cnt_common_interests, user.cnt_common_books, user.cnt_common_music))
                    result_id = curs.fetchone()[0]
                    result_ids.append(result_id)
            except (Exception, psycopg2.DatabaseError) as error:
                vk_common.dprint(1, f"Не могу добавить запись в таблицу {TABLES_NAMES[2]}", error)

            vk_common.dprint(2, "Добавили результаты поиска: ", result_ids)

            err = ((search_id, user_ids, result_ids), 0)
            vk_common.dprint(2, "вернем err = ", err)

    except (Exception, psycopg2.DatabaseError) as error:
        vk_common.dprint(1, "Общая ошибка во всей транзакции: ", error)
        if error.find(" не существует") == -1 and error.find("ОШИБКА:  отношение ") == -1:
            vk_common.dprint(2, "Error in transaction Reverting all other operations of a transaction ", error)
        if conn is not None:
            conn.rollback()
        err = (None, -1)

    finally:
        if conn is not None:
            conn.commit()
            conn.close()

        return err
