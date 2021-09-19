
from flask import request
from webargs.flaskparser import use_args

from libs.base.resource import BaseResource
from nft.layer.model import Layer, Image
from nft.layer.schema import CombinationLayerSchema, ImageQuerySchema, ImageSchema


class LayersResource(BaseResource):
    def get(self):
        data = Layer.get_layers_by_query()
        return data


class ImagesResource(BaseResource):
    @use_args(CombinationLayerSchema)
    def post(self, args):
        image = Image.combination_layer(**args)
        print(image)
        data = ImageSchema(many=False).dump(image).data
        return data

    @use_args(ImageQuerySchema)
    def get(self, args):
        images, total = Image.get_images_by_query(**args)
        data = ImageSchema(many=True).dump(images).data
        return self.paginate(
            data, total, args.get('page', 1), args.get('per_page', 10))

