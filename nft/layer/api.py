
from flask import request
from webargs.flaskparser import use_args

from libs.base.resource import BaseResource
from nft.layer.model import Layer, Image
from nft.layer.schema import CombinationLayerSchema, ImageQuerySchema, ImageSchema


class LayersResource(BaseResource):
    def get(self):
        data = Layer.get_layers_by_query()
        return data


class CombinationImagesResource(BaseResource):
    @use_args(CombinationLayerSchema)
    def post(self, args):
        data = Image.combination_layer(**args)
        return data, 201


class ImagesResource(BaseResource):
    @use_args(ImageQuerySchema)
    def post(self, args):
        data = Image.get_images_by_query(**args)
        return data


class ImageResource(BaseResource):
    def delete(self, image_id):
        Image.delete(image_id)
        return {}, 204

    @use_args(CombinationLayerSchema)
    def update(self, image_id, args):
        data = Image.update(image_id, **args)
        return data
