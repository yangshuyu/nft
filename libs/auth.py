import datetime

import jwt
import arrow

from functools import wraps
from flask import request
from sqlalchemy import and_

from config import load_config

from libs.error import error, dynamic_error
from nft import ext

config = load_config()


class OAuth(object):

    @classmethod
    def create_token(cls, user):
        payload = {
            "iss": "ec",
            "iat": datetime.datetime.now().timestamp(),
            "exp": (datetime.datetime.now() + datetime.timedelta(days=2)).timestamp(),
            "aud": "nft",
            "sub": "Delivery center management system",
            "username": user.get('username'),
            "user_id": user.get('id'),
        }
        token = jwt.encode(payload, config.SECRET_KEY, algorithm="HS256").decode(
            "utf-8"
        )
        return token


def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cookie = request.headers.get("X-Token")
        if not cookie:
            dynamic_error({}, code=422, message='请传入token')
        try:
            jwt.decode(
                cookie,
                config.SECRET_KEY,
                audience=config.AUDIENCE,
                algorithms=["HS256"],
            )
        except Exception as e:
            print(e)
            dynamic_error({}, code=422, message='错误token' + str(e))
        return func(*args, **kwargs)

    return wrapper


def requires(role):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cookie = request.headers.get("X-Token")
            if not cookie:
                dynamic_error({}, code=422, message='请登录')
            try:
                j = jwt.decode(
                    cookie,
                    config.SECRET_KEY,
                    audience=config.AUDIENCE,
                    algorithms=["HS256"],
                )
            except Exception as e:
                print(e)
                dynamic_error({}, code=422, message='错误token' + str(e))

            for d in ext.users:
                if j.get("user_id") == d.get('id'):
                    if d.get('role') < role:
                        dynamic_error({}, code=422, message='没有该操作权限')
            return func(*args, **kwargs)
        return wrapper

    return decorate

