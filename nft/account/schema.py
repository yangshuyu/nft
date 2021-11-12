import re

from marshmallow import fields, ValidationError

from config import load_config
from libs.base.schema import BaseSchema, Timestamp
from nft import ext


def validate_project(project):
    if project not in ext.projects:
        raise ValidationError("传入得项目不存在", tips="传入得项目不存在")
    return project


class LoginSchema(BaseSchema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

    class Meta:
        strict = True


class UserPutSchema(BaseSchema):
    username = fields.Str()
    password = fields.Str()
    projects = fields.List(fields.Str(validate=validate_project))

    class Meta:
        strict = True
