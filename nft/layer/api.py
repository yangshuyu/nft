from flask import request
from webargs.flaskparser import use_args

from libs.auth import jwt_required, requires
from libs.base.resource import BaseResource
from nft import ext
from nft.layer.model import Layer, Image
from nft.layer.schema import CombinationLayerSchema, ImageQuerySchema, ImageSchema, BatchDeleteImage, \
    BatchCombinationLayerSchema, LayerRemoveSchema, LayerMoveSchema, LayerPutSchema, LayerListQuerySchema, \
    LayerQuerySchema, ImageDeleteSchema, ImageUpdateSchema, ImageDashboard, ImageTemporaryToPermanentSchema, \
    TaskDashboardSchema, BatchConditionsDeleteSchema, LayerDirPostSchema, LayerDirImagesPostSchema


class LayersResource(BaseResource):
    @use_args(LayerQuerySchema)
    def get(self, args):
        data = Layer.get_layers_by_query(**args)
        return data


class LayersListResource(BaseResource):
    @use_args(LayerListQuerySchema)
    def get(self, args):
        data, total = Layer.get_layers_list_by_query(**args)
        return self.paginate(
            data, total, args.get('page', 1), args.get('per_page', 20))


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
    def post(self):
        args = request.json
        args['user'] = self.current_user
        data = Image.add_image(**args)
        return data, 201


class ImagesResource(BaseResource):
    @use_args(ImageQuerySchema)
    def post(self, args):
        args['user'] = self.current_user
        data, total = Image.get_images_by_query(**args)
        return self.paginate(
            data, total, args.get('page', 1), args.get('per_page', 20))


class ImageResource(BaseResource):
    @jwt_required
    @use_args(ImageDeleteSchema)
    def delete(self, args, image_id):
        args['image_id'] = image_id
        args['user'] = self.current_user
        Image.delete(**args)
        return {}, 204

    @jwt_required
    @use_args(ImageUpdateSchema)
    def put(self, args, image_id):
        kwargs = request.json
        kwargs['project'] = args.get('project')
        kwargs['type'] = args.get('type')
        kwargs['user'] = self.current_user
        data = Image.update(image_id, **kwargs)
        return data


class BatchDeleteImagesResource(BaseResource):
    @jwt_required
    @use_args(BatchDeleteImage)
    def post(self, args):
        args['user'] = self.current_user
        Image.batch_delete(**args)
        return {}


class BatchCombinationImagesResource(BaseResource):
    @jwt_required
    @use_args(BatchCombinationLayerSchema)
    def post(self, args):
        args['user'] = self.current_user
        Image.batch_add_images(**args)
        return {}, 201


class ImageTaskProgressResource(BaseResource):
    @use_args(TaskDashboardSchema)
    def get(self, args):
        project = args.get('project')
        user = self.current_user
        user_data = ext.user_batch_data.get(user.get('id'))
        if not user_data:
            return {'total': -1, 'completed': 0}

        project_data = ext.user_batch_data[user.get('id')].get(project)
        if not project_data:
            return {'total': -1, 'completed': 0}

        return {'total': ext.user_batch_data[user.get('id')][project].get('required_quantity'),
                'completed': ext.user_batch_data[user.get('id')][project].get('completed_quantity')}


class ImageLayerDashboard(BaseResource):
    @jwt_required
    @use_args(ImageDashboard)
    def get(self, args):
        args['user'] = self.current_user
        data = Image.get_image_layer_dashboard(**args)
        return data


class ImageTemporaryToPermanentResource(BaseResource):
    @jwt_required
    @use_args(ImageTemporaryToPermanentSchema)
    def post(self, args):
        args['user'] = self.current_user
        Image.temporary_to_permanent(**args)
        return {}


class BatchConditionsDeleteImages(BaseResource):
    @use_args(BatchConditionsDeleteSchema)
    def post(self, args):
        args['user'] = self.current_user
        Image.batch_delete_images_by_conditions(**args)
        return {}


class AdminLayerDirResource(BaseResource):
    @requires(1)
    @use_args(LayerDirPostSchema)
    def post(self, args):
        Layer.add_layer_dir(**args)
        return {}


class AdminLayerDirsImagesResource(BaseResource):
    @requires(1)
    @use_args(LayerDirImagesPostSchema)
    def post(self, args):
        Layer.add_layer_dir_images(**args)
        return {}
