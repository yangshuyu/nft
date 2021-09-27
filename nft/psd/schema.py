import os
import re

from marshmallow import fields, ValidationError

from config import load_config
from libs.base.schema import BaseSchema, Timestamp


def validate_layer(layer):
    layer_path = load_config().LAYER_FILE
    for dir, _, _ in os.walk('{}'.format(layer_path)):
        if dir == '{}/{}'.format(layer_path, layer):
            return layer
    raise ValidationError("没有正确的图层，去定是否有该图层目录", tips="图层目录不正确，请核实")


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


class PsdMixtureSchema(BaseSchema):
    id = fields.Str(required=True)
    save_index = fields.List(fields.Int(), required=True)
    layer = fields.Str(required=True, validate=validate_layer)
    name = fields.Str(required=True, validate=validate_name)

    class Meta:
        strict = True


class PsdLayerSaveSchema(BaseSchema):
    name = fields.Str(required=True)

    class Meta:
        strict = True
