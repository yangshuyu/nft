import json

from config import load_config
from libs.auth import OAuth
from libs.error import dynamic_error
from nft import ext


class User:
    @classmethod
    def get_users_by_query(cls):
        return ext.users

    @classmethod
    def login(cls, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')

        if not username or not password:
            dynamic_error({}, code=422, message='请舒服正确得账号或密码')

        user = {}
        for u in ext.users:
            if u.get('username') == username and u.get('password') == password:
                user = u
                print(user)
                user['X-Token'] = OAuth.create_token(u)
                return u

        dynamic_error({}, code=422, message='请输入服正确得账号或密码')

    @classmethod
    def update_user(cls, **kwargs):
        user_id = kwargs.get('user_id')
        username = kwargs.get('username')
        password = kwargs.get('password')
        projects = kwargs.get('projects')

        index = -1

        for i, u in enumerate(ext.users):
            if str(u.get('id')) == user_id:
                index = i

        if index != -1:
            if username:
                ext.users[index]['username'] = username
            if password:
                ext.users[index]['password'] = password
            if projects is not None:
                ext.users[index]['projects'] = projects
        else:
            dynamic_error({}, code=422, message='没有查到该用户')

        file_path = load_config().FILE + '/file/users.json'
        with open(file_path, 'w') as content:
            content.write(json.dumps(ext.users))

        return ext.users[index]
