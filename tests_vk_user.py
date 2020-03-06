import unittest
import vk_user
import vk_common


class TestUnitVkUser(unittest.TestCase):

    def setUp(self):
        filename_token = "data\\token.txt"
        vk_common.get_token(filename_token)
        self.user = vk_user.User()
        self.user.assign_by_nickname('chepel_vn')

    def test_create_new_user(self):
        self.assertIsInstance(self.user, vk_user.User)
        self.assertEqual(self.user.count_friends, 0)

    def test_assign_by_nickname(self):
        self.assertEqual(self.user.error['error'], 0)
        self.assertIsNotNone(self.user.uid)

        # Negative test case
        self.user.assign_by_nickname('*')
        self.assertEqual(self.user.error['error'], 113)

        user = vk_user.User()
        user.assign_by_nickname('')
        self.assertEqual(user.error['error'], -1)

        self.user.assign_by_nickname(214191820)
        self.assertEqual(self.user.error['error'], 0)
        self.assertEqual(self.user.uid, 214191820)

    def test_get_info(self):
        err, msg, user_id = self.user.get_info('chepel_vn')
        self.assertEqual(err, 0)
        self.assertEqual(msg, '')
        self.assertIsNotNone(user_id)

        err, msg, user_id = self.user.get_info('*')
        self.assertEqual(err, 113)
        self.assertIsNone(user_id)

        err, msg, user_id = self.user.get_info('')
        self.assertEqual(err, -1)
        self.assertIsNone(user_id)

        err, msg, user_id = self.user.get_info('654364654564654646')
        self.assertEqual(err, 113)
        self.assertIsNone(user_id)

    def test_get_top_photos(self):
        # Test on request different number of photos
        for i in range(1, 5):
            err, msg, items = self.user.get_top_photos(i)
            self.assertEqual(len(items), i)
            for item in items:
                self.assertIsNotNone(item)

        # If account is blocked
        self.user.assign_by_nickname('helen906')
        err, msg, items = self.user.get_top_photos(2)
        self.assertEqual(err, 15)

    def test_get_id_friends(self):
        self.user.get_id_friends()
        self.assertEqual(self.user.error['error'], 0)

    def test_get_common_friends(self):
        other = vk_user.User()
        other.assign_by_nickname('boytsovph')
        self.assertIsInstance(other, vk_user.User)
        err, msg, common_friends = self.user.get_common_friends(other)
        self.assertEqual(len(common_friends), 1)

        other = vk_user.User()
        other.assign_by_nickname('chepel_vn')
        self.assertIsInstance(other, vk_user.User)
        err, msg, common_friends = self.user.get_common_friends(other)
        self.assertEqual(len(common_friends), 718)

        other = vk_user.User()
        other.assign_by_nickname('*')
        self.assertIsInstance(other, vk_user.User)
        err, msg, common_friends = self.user.get_common_friends(other)
        self.assertEqual(len(common_friends), 0)

    def test_get_additional_info(self):
        other = vk_user.User()
        other.assign_by_nickname('boytsovph')
        self.assertIsInstance(other, vk_user.User)
        self.user.get_additional_info(other)
        self.assertEqual(self.user.cnt_common_friends, 1)
        self.assertEqual(self.user.cnt_common_groups, 2)
        self.assertEqual(self.user.cnt_common_interests, 0)
        self.assertEqual(self.user.cnt_common_books, 0)
        self.assertEqual(self.user.cnt_common_music, 0)


def create_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestUnitVkUser('test_create_new_user'))
    suite.addTest(TestUnitVkUser('test_assign_by_nickname'))
    suite.addTest(TestUnitVkUser('test_get_info'))
    suite.addTest(TestUnitVkUser('test_get_top_photos'))
    suite.addTest(TestUnitVkUser('test_get_id_friends'))
    suite.addTest(TestUnitVkUser('test_get_additional_info'))
    suite.addTest(TestUnitVkUser('test_get_common_friends'))
    suite.addTest(TestUnitVkUser('test_get_additional_info'))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(create_suite())
