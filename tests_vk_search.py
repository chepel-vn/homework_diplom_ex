import unittest
import vk_db
import vk_common
import vk_user
import vk_search
from unittest.mock import patch

search_param = {
            'age_from': 0,
            'age_to': 0,
            'sex': 0
        }


def set_search_param(age_from, age_to, sex):
    search_param['age_from'] = age_from
    search_param['age_to'] = age_to
    search_param['sex'] = sex


class TestUnitVkDb(unittest.TestCase):

    def setUp(self):
        filename_token = "data\\token.txt"
        vk_common.get_token(filename_token)
        self.user = vk_user.User()
        self.user.assign_by_nickname('chepel_vn')
        vk_db.add_user(self.user)
        self.search = vk_search.Search()
        self.user_id_old = list()
        self.user_id_banned = list()
        set_search_param(20, 40, 0)

    def add_search_classic_ages(self):
        # Classic variant
        set_search_param(23, 35, 0)
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, 0)
        self.assertGreater(len(users_search), 0)

    def add_search_wrong_age(self):
        # variant with zero input data
        set_search_param(0, 0, 0)
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, -1)
        self.assertIsNone(users_search)

        set_search_param(35, 23, 0)
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, -1)
        self.assertIsNone(users_search)

        set_search_param(-1, 23, 0)
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, -1)
        self.assertIsNone(users_search)

        set_search_param(1, -1, 0)
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, -1)
        self.assertIsNone(users_search)

    def add_search_wrong_sex(self):
        set_search_param(20, 40, -1)
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, -1)
        self.assertIsNone(users_search)

        set_search_param(20, 40, 3)
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, -1)
        self.assertIsNone(users_search)

    def add_search_wrong_count(self):
        with patch('vk_search.COUNT_REC_BY_ONE_REQUEST', 0):
            err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                              self.user_id_banned)
            self.assertEqual(err, 0)
            self.assertIsNotNone(users_search)
            self.assertEqual(len(users_search), 0)

        with patch('vk_search.COUNT_REC_BY_ONE_REQUEST', 1000):
            err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                              self.user_id_banned)
            self.assertEqual(err, 0)
            self.assertIsNotNone(users_search)
            self.assertGreater(len(users_search), 0)

        with patch('vk_search.COUNT_REC_BY_ONE_REQUEST', 5000):
            err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                              self.user_id_banned)
            self.assertEqual(err, -1)
            self.assertIsNone(users_search)

    def add_search_wrong_fields(self):
        with patch('vk_common.FIELDS_USER_INFO', ""):
            err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                              self.user_id_banned)
            self.assertEqual(err, 0)
            self.assertEqual(len(users_search), 0)

    def add_search_wrong_city_id(self):
        self.user.city = {'id': -1, 'name': 'xxx'}
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, -1)
        self.assertIsNone(users_search)

    def add_search_wrong_type(self):
        err, msg, users_search = self.search.search_users(4, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, -1)
        self.assertIsNone(users_search)

        err, msg, users_search = self.search.search_users(self.user, search_param, 3, self.user_id_banned)
        self.assertEqual(err, -1)
        self.assertIsNone(users_search)

        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old, "zdfghzdf")
        self.assertEqual(err, -1)
        self.assertIsNone(users_search)

    def add_search_user_id_old(self):
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, 0)
        self.assertIsNotNone(users_search)
        self.assertGreater(len(users_search), 0)
        for user in users_search:
            self.user_id_old.append(user.uid)
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, 0)
        self.assertIsNotNone(users_search)
        self.assertEqual(len(users_search), 0)

        for user in users_search:
            for user_id_del in self.user_id_old:
                self.assertNotEqual(user.uid, user_id_del)

    def add_search_user_id_banned(self):
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, 0)
        self.assertIsNotNone(users_search)
        self.assertGreater(len(users_search), 0)
        for user in users_search:
            self.user_id_banned.append(user.uid)
        err, msg, users_search = self.search.search_users(self.user, search_param, self.user_id_old,
                                                          self.user_id_banned)
        self.assertEqual(err, 0)
        self.assertIsNotNone(users_search)
        self.assertEqual(len(users_search), 0)

        for user in users_search:
            for user_id_del in self.user_id_banned:
                self.assertNotEqual(user.uid, user_id_del)


def create_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestUnitVkDb('add_search_classic_ages'))
    suite.addTest(TestUnitVkDb('add_search_wrong_age'))
    suite.addTest(TestUnitVkDb('add_search_wrong_sex'))
    suite.addTest(TestUnitVkDb('add_search_wrong_count'))
    suite.addTest(TestUnitVkDb('add_search_wrong_fields'))
    suite.addTest(TestUnitVkDb('add_search_wrong_city_id'))
    suite.addTest(TestUnitVkDb('add_search_wrong_type'))
    suite.addTest(TestUnitVkDb('add_search_user_id_old'))
    suite.addTest(TestUnitVkDb('add_search_user_id_banned'))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(create_suite())
