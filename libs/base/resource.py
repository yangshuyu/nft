import copy

import jwt
from flask import request
from flask_restful import Resource

from nft import ext


class BaseResource(Resource):
    record = None

    @property
    def current_user(self):
        from config import load_config

        config = load_config()
        cookie = request.headers.get("X-Token")

        if not cookie:
            return None
        try:
            data = jwt.decode(
                cookie,
                config.SECRET_KEY,
                audience=config.AUDIENCE,
                algorithms=["HS256"],
            )
            user_id = data.get("user_id")
            for d in ext.users:
                if user_id == d.get('id'):
                    user = copy.deepcopy(d)
                    return user

            return None
        except Exception as e:
            print(e)

    def paginate(self, result, total, page=1, per_page=10):
        has_more = page * per_page < total
        return (
            result,
            200,
            {
                "_extra_data": {"has_more": has_more},
                "X-Total": total,
                "X-Per-Page": per_page,
            },
        )


def generate_response(data, code=0, message='成功'):
    return data, 200, {'message': message, 'response_code': code}
