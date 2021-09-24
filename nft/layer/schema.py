import re

from marshmallow import fields, ValidationError

from config import load_config
from libs.base.schema import BaseSchema, Timestamp


class PostLayerSchema(BaseSchema):
    percentage = fields.Int(missing=100)
    layer_data = fields.List(fields.Str(), missing=[])

    class Meta:
        strict = True


class CombinationLayerSchema(BaseSchema):
    background = fields.Nested(PostLayerSchema, required=True)
    body = fields.Nested(PostLayerSchema, required=True)
    cloth = fields.Nested(PostLayerSchema, required=True)
    drink = fields.Nested(PostLayerSchema, required=True)
    earring = fields.Nested(PostLayerSchema, required=True)
    eyewear = fields.Nested(PostLayerSchema, required=True)
    hat = fields.Nested(PostLayerSchema, required=True)
    mouth = fields.Nested(PostLayerSchema, required=True)
    nacklace = fields.Nested(PostLayerSchema, required=True)
    props = fields.Nested(PostLayerSchema, required=True)

    class Meta:
        strict = True


class BatchCombinationLayerSchema(BaseSchema):
    data = fields.Nested(CombinationLayerSchema)
    nums = fields.Int(validate=lambda val: 10000 > val > 0, required=True)

    class Meta:
        strict = True


class ImageQuerySchema(BaseSchema):
    page = fields.Int(missing=1)
    per_page = fields.Int(missing=20)
    conditions = fields.Dict()

    class Meta:
        strict = True


class BatchDeleteImage(BaseSchema):
    image_ids = fields.List(fields.Str(), missing=[])

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
