import unittest
import vk_db
import vk_common
import vk_user
from unittest.mock import patch

TABLES_NAMES1 = ("vk_photos1", "vk_cities1", "vk_users1", "vk_search1", "vk_results1")


class TestUnitVkDb(unittest.TestCase):

    def setUp(self):
        with patch('vk_db.TABLES_NAMES', TABLES_NAMES1):
            vk_db.create_db()
            filename_token = "data\\token.txt"
            vk_common.get_token(filename_token)

    def test_drop_table(self):
        with patch('vk_db.TABLES_NAMES', TABLES_NAMES1):
            vk_db.drop_db()
            for table_name in TABLES_NAMES1:
                rep = vk_db.is_exists_table(table_name)
                self.assertFalse(rep)
            vk_db.create_db()
            for table_name in TABLES_NAMES1:
                rep = vk_db.is_exists_table(table_name)
                self.assertTrue(rep)

    def test_drop_db(self):
        with patch('vk_db.TABLES_NAMES', TABLES_NAMES1):
            vk_db.drop_db()
            for table_name in TABLES_NAMES1:
                rep = vk_db.is_exists_table(table_name)
                self.assertFalse(rep)
            vk_db.create_db()
            for table_name in TABLES_NAMES1:
                rep = vk_db.is_exists_table(table_name)
                self.assertTrue(rep)

    def test_create_db(self):
        with patch('vk_db.TABLES_NAMES', TABLES_NAMES1):
            vk_db.create_db()
            for table_name in TABLES_NAMES1:
                rep = vk_db.is_exists_table(table_name)
                self.assertTrue(rep)

    def test_clear_db(self):
        with patch('vk_db.TABLES_NAMES', TABLES_NAMES1):
            vk_db.add_city({'id': 119, 'title': 'dfghzdgh'})
            rows, err = vk_db.get_count_rows_of_table('vk_cities')
            self.assertGreater(rows[0][0], 0)

            user = vk_user.User()
            user.assign_by_nickname('chepel_vn')
            user_id, err = vk_db.add_user(user)
            self.assertEqual(err, 0)
            self.assertIsNotNone(user_id)
            rows, err = vk_db.get_count_rows_of_table('vk_users')
            self.assertGreater(rows[0][0], 0)
            rows, err = vk_db.clear_db()
            self.assertEqual(err, 0)
            self.assertIsNone(rows)

            for table_name in TABLES_NAMES1:
                rows, err = vk_db.get_count_rows_of_table(table_name)
                self.assertEqual(rows[0][0], 0)

    def test_add_city(self):
        with patch('vk_db.TABLES_NAMES', TABLES_NAMES1):
            vk_db.clear_db()
            rows, err = vk_db.get_count_rows_of_table(TABLES_NAMES1[1])
            self.assertEqual(rows[0][0], 0)
            vk_db.add_city({'id': 119, 'title': 'Гуково'})
            rows, err = vk_db.get_count_rows_of_table(TABLES_NAMES1[1])
            self.assertEqual(rows[0][0], 1)
            data, err = vk_db.get_city_name(119)
            self.assertEqual(data[0][0], "Гуково")

            # row_id, err = vk_db.add_city1(119)
            # print(row_id, err)
            # vk_db.print_table('vk_cities1')

            # data, err = vk_db.get_city_name(119)
            # self.assertEqual(data[0][0], "Гуково")

    def test_add_user(self):
        with patch('vk_db.TABLES_NAMES', TABLES_NAMES1):
            vk_db.clear_db()
            vk_db.add_city({'id': 119, 'title': 'Гуково'})
            data, err = vk_db.get_city_name(119)
            self.assertEqual(data[0][0], "Гуково")

            user = vk_user.User()
            user.assign_by_nickname('chepel_vn')
            user_id, err = vk_db.add_user(user)
            self.assertEqual(err, 0)
            self.assertIsNotNone(user_id)

    def test_get_city_name(self):
        with patch('vk_db.TABLES_NAMES', TABLES_NAMES1):
            vk_db.clear_db()
            data, err = vk_db.get_city_name(119)
            self.assertEqual(err, 0)
            self.assertEqual(len(data), 0)
            vk_db.add_city({'id': 119, 'title': 'Гуково'})
            data, err = vk_db.get_city_name(119)
            self.assertEqual(data[0][0], "Гуково")
            vk_db.clear_db()


def create_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestUnitVkDb('test_drop_db'))
    suite.addTest(TestUnitVkDb('test_create_db'))
    suite.addTest(TestUnitVkDb('test_clear_db'))
    suite.addTest(TestUnitVkDb('test_add_city'))
    suite.addTest(TestUnitVkDb('test_get_city_name'))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(create_suite())
