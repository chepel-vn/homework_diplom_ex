import psycopg2
import vk_common
import vk_user


CONNECT_STRING = "dbname=test_db user=test password=123 host=127.0.0.1 port=5432"


def request_decorator(function_to_decorate):
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
            function_to_decorate(curs, *args, **kwargs)
            try:
                result_records = curs.fetchall()
                err = (result_records, 0)
            except psycopg2.ProgrammingError:
                err = (None, 0)
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error in transaction Reverting all other operations of a transaction ", error)
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
            if vk_common.is_common_by_text('повторяющееся значение ключа нарушает ограничение '
                                           'уникальности', error) == 0:
                print("Error in transaction Reverting all other operations of a transaction ", error)
                if conn is not None:
                    conn.rollback()
                err = ((None, None, None), -1)
            else:
                err = ((None, None, None), -2)
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

    curs.execute("""TRUNCATE TABLE if exists vk_photos;""")
    curs.execute("""TRUNCATE TABLE if exists vk_results;""")
    curs.execute("""TRUNCATE TABLE if exists vk_search;""")
    curs.execute("""TRUNCATE TABLE if exists vk_users;""")
    curs.execute("""TRUNCATE TABLE if exists vk_cities;""")


@request_decorator
def drop_db(curs):
    """

    (cursor link) -> None

    Function drops all tables

    """

    curs.execute("""DROP TABLE if exists vk_photos;""")
    curs.execute("""DROP TABLE if exists vk_results;""")
    curs.execute("""DROP TABLE if exists vk_search;""")
    curs.execute("""DROP TABLE if exists vk_users;""")
    curs.execute("""DROP TABLE if exists vk_cities;""")


@request_decorator
def create_db(curs):
    """

    (cursor link) -> None

    Function creates all tables

    """

    # "id,name"
    curs.execute("""CREATE TABLE if not exists vk_cities (
                    id numeric(4) NOT NULL PRIMARY KEY,
                    name varchar(100));
                    """)

    # "id,first_name,last_name,age,interests,books,music,sex,city_id"
    curs.execute("""CREATE TABLE if not exists vk_users (
                id numeric(10) NOT NULL PRIMARY KEY,
                first_name varchar(30),
                last_name varchar(30),              
                age numeric(3),
                interests varchar(3000),
                books varchar(3000),
                music varchar(3000),
                sex numeric(1),
                city_id integer references vk_cities(id));
                """)

    # "id,user_id,age_from,age_to,sex"
    curs.execute("""CREATE TABLE if not exists vk_search (
                id serial PRIMARY KEY,
                user_id integer references vk_users(id),               
                age_from numeric(3),
                age_to numeric(3),
                sex numeric(1));
                """)

    # "id,search_id,user_id,cnt_common_friends,cnt_common_groups"
    curs.execute("""CREATE TABLE if not exists vk_results (
                id serial PRIMARY KEY,
                search_id integer references vk_search(id),                
                user_id integer references vk_users(id),
                cnt_common_friends numeric(4),
                cnt_common_groups numeric(4),
                cnt_common_interests numeric(4),
                cnt_common_books numeric(4),
                cnt_common_music numeric(4));
                """)

    # "id,user_id,top_id,image_file_path"
    curs.execute("""CREATE TABLE if not exists vk_photos (
                        id serial PRIMARY KEY,
                        user_id integer references vk_users(id),
                        top_id numeric(2),
                        image_file_path varchar(100));
                        """)


def re_create_db():
    """

    (None) -> None

    Function recreated all tables

    """

    msg, err = drop_db()
    if err == -1:
        value = (msg, err)
        return value
    msg, err = create_db()
    value = (msg, err)
    return value


@sql_execute_decorator
def add_city(curs, city):
    """

    (cursor link, dict) -> integer

    Function add city to table vk_cities

    """

    curs.execute("insert into vk_cities (id, name) "
                 "values (%s, %s) returning id",
                 (city['id'], city['title']))
    rec_id = curs.fetchone()[0]
    return rec_id


@request_decorator
def add_user_photos(curs, user):
    """

    (cursor link, object User) -> integer

    Function add user's photos to table vk_photos

    """

    for number, image_file_path in enumerate(user.photos, 1):
        curs.execute("insert into vk_photos (user_id, top_id, image_file_path) "
                     "values (%s, %s, %s) returning id",
                     (user.id, number, image_file_path))


def add_user_execute(curs, user):
    curs.execute("insert into vk_users (id, first_name, last_name, age, interests, books, music, sex, city_id) "
                 "values (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning id",
                 (user.id, user.first_name, user.last_name, user.age, user.interests, user.books, user.music, user.sex,
                  user.city_id))
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


def add_users(curs, users):
    """

    (cursor link, integer, integer) -> None

    Function adds users to database

    """

    rec_ids = []
    for user in users:
        rec_id = add_user_execute(curs, user)
        rec_ids.append(rec_id)

    return rec_ids


@request_decorator
def get_results_by_search_id(curs, search_id):
    """

    (cursor link, integer, integer) -> None

    Function gets search results by user_id and search_id

    """

    curs.execute("select res.id, s.name, s.gpa, s.birth, c.id, c.name from vk_results res "
                 "join vk_search s on s.id = res.search_id where s.id = %s"
                 "join vk_users u on u.id = res.user_id", search_id)


@sql_execute_decorator
def add_search(curs, search):
    """

    (cursor link, object Search) -> None

    Function adds search to database

    """

    curs.execute("insert into vk_search (user_id, age_from, age_to, sex) values (%s, %s, %s, %s) returning id",
                 (search.user_id, search.age_from, search.age_to, search.sex))
    search_id = curs.fetchone()[0]

    user_ids, result_ids = add_results(curs, search_id, search.results)
    value = (search_id, user_ids, result_ids)
    return value


def add_results(curs, search_id, users):
    """

    (cursor link, integer, list of objects User) -> None

    Function adds results of search with id = search_id to database

    """

    # Add user before adding record to table vk_results
    user_ids = add_users(curs, users)

    result_ids = []
    for user in users:
        curs.execute("insert into vk_results (search_id, user_id, cnt_common_friends, cnt_common_groups, "
                     "cnt_common_interests, cnt_common_books, cnt_common_music) values "
                     "(%s, %s, %s, %s, %s, %s, %s) returning id",
                     (search_id, user.id, user.cnt_common_friends, user.cnt_common_groups,
                      user.cnt_common_interests, user.cnt_common_books, user.cnt_common_music))
        result_id = curs.fetchone()[0]

        result_ids.append(result_id)

    value = (user_ids, result_ids)
    return value


def print_cursor(curs):
    # rs.search_id, rs.user_id, rs.cnt_common_friends, rs.cnt_common_groups, u.age, u.interests, u.books, u.music,
    # rs.cnt_common_interests, rs.cnt_common_books, rs.cnt_common_music
    for row in curs:
        print(f"search_id: {row[0]}; user_id: {row[1]}; common_friends: {row[2]}; common_groups: {row[3]}; "
              f"age: {row[4]}; interests: {row[5]}; books: {row[6]}; music: {row[7]}; "
              f"cnt_common_interests: {row[8]}; cnt_common_books: {row[9]}; cnt_common_music: {row[10]};")


@request_decorator
def print_table(curs, table_name):
    """

    (cursor link, string) -> None

    Function prints data of table with name = table_name

    """
    curs.execute(f"select * from {table_name}")
    print("")
    print(f"Таблица \"{table_name}\":")
    for rows in curs.fetchall():
        if table_name == 'vk_users':
            print(f"user_id: {rows[0]}; fio: {rows[1]} {rows[2]}; age: {rows[3]}; interests: {rows[4]}; "
                  f"books: {rows[5]}; music: {rows[6]}; sex: {vk_common.sex_to_char(rows[7])}; city_id: {rows[8]};")
        elif table_name == 'vk_search':
            print(f"search_id: {rows[0]}; user_id: {rows[1]}; age_from: {rows[2]}; age_to: {rows[3]}; "
                  f"sex: {vk_common.sex_to_char(rows[4])};")
        elif table_name == 'vk_results':
            print(f"search_id: {rows[1]}; user_id: {rows[2]}; common_friends: {rows[3]}; common_groups: {rows[4]};"
                  f"cnt_common_interests: {rows[5]}; cnt_common_books {rows[6]}; cnt_common_music {rows[7]};")
        elif table_name == 'vk_cities':
            print(f"city_id: {rows[0]}; name: {rows[1]};")
        else:
            print(rows)


def print_all_tables():
    """

    (None) -> None

    Function prints data of all VK tables

    """
    print_table('vk_photos')
    print_table('vk_cities')
    print_table('vk_users')
    print_table('vk_search')
    print_table('vk_results')


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
def get_top_users_by_search_id(curs, search_id, count_top):
    """

    (cursor link, integer, integer) -> None

    Function gets top users by search_id (count users = count_top)

    """

    # ПРОРИТЕТЫ ПОИСКА
    # 1) кол-во общих друзей
    # 2) возраст
    # 3) кол-во общих групп
    # 4) интересы
    # 5) музыка
    # 6) книги

    # VK_CITIES  "id,name"
    # VK_USERS   "id,first_name,last_name,age,interests,books,music,sex,city_id"
    # VK_SEARCH  "id,user_id,age_from,age_to,sex"
    # VK_RESULTS "id,search_id,user_id,cnt_common_friends,cnt_common_groups,cnt_common_interests,cnt_common_books,
    #             cnt_common_music"

    curs.execute("select rs.search_id, rs.user_id, u.first_name, u.last_name, u.sex, u.age, u.interests, u.books, "
                 "u.music, rs.cnt_common_interests, rs.cnt_common_books, rs.cnt_common_music, rs.cnt_common_friends, "
                 "rs.cnt_common_groups "
                 "from vk_results rs "
                 "join vk_users u on u.id = rs.user_id "
                 "where rs.search_id = %s and rs.user_id not in (select user_id from vk_photos) "
                 "order by rs.cnt_common_friends desc, u.age desc, rs.cnt_common_groups desc, "
                 "rs.cnt_common_interests desc, rs.cnt_common_music desc, rs.cnt_common_books desc "
                 "limit %s", (search_id, count_top))


@sql_execute_decorator
def add_users1(curs, users):
    """

    (cursor link, integer, integer) -> None

    Function adds users to database

    """

    rec_ids = []
    for user in users:
        rec_id = add_user_execute(curs, user)
        rec_ids.append(rec_id)

    return rec_ids


@request_decorator
def get_user(curs, user_id):
    """

    (cursor link, integer) -> None

    Function gets user

    """

    curs.execute("select * from vk_users where id = %s", user_id)


@sql_execute_decorator
def add_search1(curs, search):
    """

    (cursor link, object Search) -> None

    Function adds search to database

    """

    curs.execute("insert into vk_search (user_id, age_from, age_to, sex) values (%s, %s, %s, %s) returning id",
                 (search.user_id, search.age_from, search.age_to, search.sex))
    rec_id = curs.fetchone()[0]
    return rec_id


@sql_execute_decorator
def add_search2(curs, search, search_id):
    """

    (cursor link, object Search) -> None

    Function adds search to database

    """

    user_ids, result_ids = add_results(curs, search_id, search.results)
    value = (search_id, user_ids, result_ids)
    return value


@sql_execute_decorator
def add_results1(curs, search_id, users):
    """

    (cursor link, integer, list of objects User) -> None

    Function adds results of search with id = search_id to database

    """

    result_ids = []
    for user in users:
        curs.execute("insert into vk_results (search_id, user_id, cnt_common_friends, cnt_common_groups, "
                     "cnt_common_interests, cnt_common_books, cnt_common_music) values "
                     "(%s, %s, %s, %s, %s, %s, %s) returning id",
                     (search_id, user.id, user.cnt_common_friends, user.cnt_common_groups,
                      user.cnt_common_interests, user.cnt_common_books, user.cnt_common_music))
        result_id = curs.fetchone()[0]
        result_ids.append(result_id)

    return result_ids

