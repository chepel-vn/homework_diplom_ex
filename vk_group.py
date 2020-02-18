import vk_common
from decorator_logger import logger_path_decorator, get_name_module


@logger_path_decorator(get_name_module(__file__)+'.log')
def get_groups_with_common_friends(id_groups_user, count_friends_limit):
    # Get groups which have <=N common friends
    params_here = dict()
    params_here["count"] = count_friends_limit
    params_here["filter"] = "friends"

    params_code = vk_common.params.copy()

    start = 0
    groups_common_friends_n = list()
    while True:
        if start > len(id_groups_user):
            break

        script = ""
        for group in id_groups_user[start:start + vk_common.COUNT_REQUESTS_EXECUTE:1]:
            params_here["group_id"] = group
            script += f"API.groups.getMembers({params_here}),"

        params_code["code"] = f"return [{script}];"
        error, msg, response = vk_common.request_get('https://api.vk.com/method/execute', params_code,
                                                     vk_common.func_name())
        if error != 0:
            value = (error, msg, None)
            return value

        response_json = response.json()
        response_json_ = response_json["response"]
        for group_id, response_item in zip(id_groups_user, response_json_):
            # print(group_id, response_item)
            if not response_item:
                continue

            # print(group_id, response_item)
            count = response_item["count"]
            # Accumulate id groups which have <=N=count_friends_limit common friends
            if count in range(1, count_friends_limit+1):
                groups_common_friends_n.append(group_id)

        start = start + vk_common.COUNT_REQUESTS_EXECUTE

    value = (0, "", groups_common_friends_n)
    return value


class Group:
    """

    Class describe group VK

    """

    # Initialization class
    def __init__(self, group_id):
        """

        (None, int) -> object Group or None

        Function of initialization of class Group

        """

        self.group_id = group_id
        self.members_count = 0
        self.group_name = ""

    # Detect a status of user
    def get_name(self):
        """

        (None) -> str

        Function gets name of group VK

        """

        if 'self.group_name' in locals():
            value = (0, "", self.group_name)
            return value

        params_here = vk_common.params.copy()
        params_here["group_ids"] = self.group_id
        params_here["fields"] = "name,members_count"

        error, msg, response = vk_common.request_get('https://api.vk.com/method/groups.getById', params_here,
                                                     vk_common.func_name())
        if error != 0:
            value = (error, msg, None)
            return value

        response_json = response.json()
        error, msg, info_json_list = vk_common.get_field_of_response(response_json, 'response')
        if error != 0:
            value = (error, msg, None)
            return value

        info_json = info_json_list[0]

        error, msg, self.group_name = vk_common.get_field_of_response(info_json, 'name')
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, self.members_count = vk_common.get_field_of_response(info_json, 'members_count')
        if error != 0:
            value = (error, msg, None)
            return value

        value = (0, "", self.group_name)
        return value




