from flask import request
from webargs.flaskparser import use_args

from libs.base.resource import BaseResource
from nft import ext
from nft.layer.model import Layer, Image
from nft.layer.schema import CombinationLayerSchema, ImageQuerySchema, ImageSchema, BatchDeleteImage, \
    BatchCombinationLayerSchema, LayerRemoveSchema, LayerMoveSchema, LayerPutSchema


class LayersResource(BaseResource):
    def get(self):
        data = Layer.get_layers_by_query()
        return data


class LayerResource(BaseResource):
    @use_args(LayerPutSchema)
    def put(self, args):
        data = Layer.update(**args)
        return data


class LayerRemoveResource(BaseResource):
    @use_args(LayerRemoveSchema)
    def post(self, args):
        Layer.remove_layer(**args)
        return {}


class LayerMoveResource(BaseResource):
    @use_args(LayerMoveSchema)
    def post(self, args):
        data = Layer.move_layer(**args)
        return data


class CombinationImagesResource(BaseResource):
    @use_args(CombinationLayerSchema)
    def post(self, args):
        data = Image.add_image(**args)
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


class BatchDeleteImagesResource(BaseResource):
    @use_args(BatchDeleteImage)
    def post(self, args):
        Image.batch_delete(**args)
        return {}


class BatchCombinationImagesResource(BaseResource):
    @use_args(BatchCombinationLayerSchema)
    def post(self, args):
        Image.batch_add_images(**args)
        return {}, 201


class ImageTaskProgressResource(BaseResource):
    def get(self):
        return {'total': ext.required_quantity, 'completed': ext.completed_quantity}


class ImageLayerDashboard(BaseResource):
    def get(self):
        data = Image.get_image_layer_dashboard()
        return data
