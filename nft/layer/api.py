
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
        data, total = Image.get_images_by_query(**args)
        return self.paginate(
            data, total, args.get('page', 1), args.get('per_page', 20))


class ImageResource(BaseResource):
    def delete(self, image_id):
        Image.delete(image_id)
        return {}, 204

    @use_args(CombinationLayerSchema)
    def put(self, args, image_id):
        data = Image.update(image_id, **args)
        return data
