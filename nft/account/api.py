from webargs.flaskparser import use_args

from libs.auth import requires
from libs.base.resource import BaseResource
from nft.account.model import User
from nft.account.schema import LoginSchema, UserPutSchema


class UsersResource(BaseResource):
    @requires(1)
    def get(self):
        data = User.get_users_by_query()
        return data


class LoginResource(BaseResource):
    @use_args(LoginSchema)
    def post(self, args):
        print(args)
        user = User.login(**args)
        return user


class ManageUserResource(BaseResource):
    @requires(1)
    @use_args(UserPutSchema)
    def post(self, args, user_id):
        args['user_id'] = user_id
        user = User.update_user(**args)
        return user

