from flask import Blueprint, request, current_app
import copy
import json

# 获取logger
from nft.api import CustomApi
from nft.layer.api import LayersResource, ImagesResource, CombinationImagesResource, ImageResource, \
    BatchDeleteImagesResource, BatchCombinationImagesResource, ImageTaskProgressResource, ImageLayerDashboard, \
    LayerRemoveResource, LayerMoveResource, LayerResource
from nft.psd.api import PsdResource, PsdMixtureResource, PsdLayerResource

"""
    api的url统一注册口
"""

api_bp_v1 = Blueprint("api_v1", __name__)
api_v1 = CustomApi(api_bp_v1, prefix="/api/v1")

#
api_v1.add_resource(LayersResource, "/layers")
api_v1.add_resource(LayerResource, '/layer')
api_v1.add_resource(LayerRemoveResource, '/layer/remove')
api_v1.add_resource(LayerMoveResource, '/layer/move')
api_v1.add_resource(CombinationImagesResource, "/combination/images")
api_v1.add_resource(ImagesResource, "/images")
api_v1.add_resource(ImageResource, "/images/<image_id>")

api_v1.add_resource(BatchDeleteImagesResource, '/batch/delete/images')
api_v1.add_resource(BatchCombinationImagesResource, '/batch//combination/images')
api_v1.add_resource(ImageTaskProgressResource, '/image/task/progress')
api_v1.add_resource(ImageLayerDashboard, '/image/layer/dashboard')

api_v1.add_resource(PsdResource, '/psd')
api_v1.add_resource(PsdMixtureResource, '/psd/mixture')
api_v1.add_resource(PsdLayerResource, '/psd/layer')


BLUEPRINTS = [api_bp_v1]

# api_v1.add_resource(AddGitTags, '/gitlab/users')
__all__ = ["BLUEPRINTS"]

# @api_bp_v1.before_request
# def before_request():
#     try:
#         if request.method == "OPTIONS":
#             pass
#         elif request.method == "GET":
#             logger.info("url:{} ,method:{}".format(request.url, request.method))
#         else:
#             logger.info(
#                 "url:{} ,method:{},请求参数:{}".format(
#                     request.url, request.method, request.json
#                 )
#             )
#     # if request.method =='OPTIONS':
#     #     resp = current_app.make_default_options_response()
#     #     if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
#     #         resp.headers['Access-Control-Allow-Headers'] = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']
#     #     resp.headers['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
#     #     resp.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
#     #     return resp
#     except Exception as e:
#         logger.error("Error", exc_info=True)




# @api_bp_v1.after_request
# def after_request(r):
#     result = copy.copy(r.response)
#     if type(result).__name__ == "FileWrapper":
#         return r
#     if result and not isinstance(result[0], bytes):
#         logger.info(
#             "url:{} ,method:{},返回数据:{}".format(
#                 request.url, request.method, json.loads(result[0])
#             )
#         )
#     return r
