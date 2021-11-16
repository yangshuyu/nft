import os
import re

from marshmallow import fields, ValidationError

from config import load_config
from libs.base.schema import BaseSchema, Timestamp


def validate_name(name):
    if name.endswith('png'):
        raise ValidationError("文件名称不正确", tips="文件名称不正确，请核实")

    def _get_str(s, left, right):
        return s.split(left)[1].split(right)[0]

    try:
        result = {
            'name': _get_str(name, "-", ":"),
            'weight': int(_get_str(name, ":", "{")),
        }
        traits_str = _get_str(name, "{", "}").split("&")
        result['traits'] = list(map(
            lambda x: (_get_str(x, "<", ">"), x.split(">")[1]), traits_str
        ))
    except Exception as e:
        raise ValidationError("文件名称不正确", tips="文件名称不正确，请核实")
    return name


class PsdFilePostSchema(BaseSchema):
    project = fields.Str(required=True)

    class Meta:
        strict = True


class PsdMixtureSchema(BaseSchema):
    id = fields.Str(required=True)
    save_index = fields.List(fields.Int(), required=True)
    layer = fields.Str(required=True)
    name = fields.Str(required=True, validate=validate_name)
    project = fields.Str(required=True)

    class Meta:
        strict = True


class PsdLayerSaveSchema(BaseSchema):
    name = fields.Str(required=True)
    project = fields.Str(required=True)

    class Meta:
        strict = True
