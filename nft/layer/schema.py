import re

from marshmallow import fields, ValidationError

from config import load_config
from libs.base.schema import BaseSchema, Timestamp


class CombinationLayerSchema(BaseSchema):
    data = fields.Dict(missing={})

    class Meta:
        strict = True


class ImageQuerySchema(BaseSchema):
    page = fields.Int(missing=1)
    per_page = fields.Int(missing=20)
    conditions = fields.Dict()

    class Meta:
        strict = True


class ImageSchema(BaseSchema):
    id = fields.Str()
    created_at = Timestamp()
    name = fields.Str()
    attributes = fields.Dict()
    description = fields.Str()
    url = fields.Method(serialize='get_path', dump_only=True)

    def get_path(self, obj):
        return '{}://{}/files/images/{}.png'.format(
            load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, obj.id)

    class Meta:
        strict = True
