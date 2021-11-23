import re

from marshmallow import fields, ValidationError

from config import load_config
from libs.base.schema import BaseSchema, Timestamp


class LayerQuerySchema(BaseSchema):
    project = fields.Str(required=True)

    class Meta:
        strict = True


class LayerListQuerySchema(BaseSchema):
    page = fields.Int(missing=1)
    per_page = fields.Int(missing=20)
    q = fields.Str()
    project = fields.Str(required=True)

    class Meta:
        strict = True


class PostLayerSchema(BaseSchema):
    percentage = fields.Int(missing=100)
    data = fields.List(fields.Str(), missing=[])

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
    data = fields.Dict(required=True)
    nums = fields.Int(validate=lambda val: 10000 > val > 0, required=True)
    project = fields.Str(required=True)

    class Meta:
        strict = True


class TaskDashboardSchema(BaseSchema):
    project = fields.Str(required=True)

    class Meta:
        strict = True


class ImageQuerySchema(BaseSchema):
    page = fields.Int(missing=1)
    per_page = fields.Int(missing=20)
    conditions = fields.Dict()
    type = fields.Int()
    project = fields.Str(required=True)

    class Meta:
        strict = True


class ImageDeleteSchema(BaseSchema):
    type = fields.Int(required=True)
    project = fields.Str(required=True)

    class Meta:
        strict = True


class ImageUpdateSchema(BaseSchema):
    type = fields.Int(required=True)
    project = fields.Str(required=True)

    class Meta:
        strict = True


class BatchDeleteImage(BaseSchema):
    image_ids = fields.List(fields.Str(), missing=[])
    type = fields.Int(required=True)
    project = fields.Str(required=True)

    class Meta:
        strict = True


class ImageDashboard(BaseSchema):
    type = fields.Int(required=True)
    project = fields.Str(required=True)

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


class LayerRemoveSchema(BaseSchema):
    layer = fields.Str(required=True)
    name = fields.Str(required=True)
    project = fields.Str(required=True)

    class Meta:
        strict = True


class LayerMoveSchema(BaseSchema):
    old_layer = fields.Str(required=True)
    old_name = fields.Str(required=True)
    new_layer = fields.Str(required=True)
    new_name = fields.Str(required=True)
    project = fields.Str(required=True)

    class Meta:
        strict = True


class LayerPutSchema(BaseSchema):
    layer = fields.Str(required=True)
    name = fields.Str(required=True)
    new_name = fields.Str(required=True)
    project = fields.Str(required=True)

    class Meta:
        strict = True


class ImageTemporaryToPermanentSchema(BaseSchema):
    project = fields.Str(required=True)
    image_ids = fields.List(fields.Str(), missing=[])

    class Meta:
        strict = True


class BatchConditionsDeleteSchema(BaseSchema):
    conditions = fields.Dict()
    type = fields.Int(missing=0)
    project = fields.Str(required=True)

    class Meta:
        strict = True


class LayerDirImageSchema(BaseSchema):
    thumbUrl = fields.Str()
    name = fields.Str()

    class Meta:
        strict = True


class LayerDirPostSchema(BaseSchema):
    dir = fields.Str(required=True)
    project = fields.Str(required=True)

    class Meta:
        strict = True


class LayerDirImagesPostSchema(BaseSchema):
    dir = fields.Str(required=True)
    project = fields.Str(required=True)
    images = fields.List(fields.Nested(LayerDirImageSchema), required=True)

    class Meta:
        strict = True
