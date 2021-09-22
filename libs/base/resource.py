
from flask import request
from flask_restful import Resource


class BaseResource(Resource):
    record = None

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
