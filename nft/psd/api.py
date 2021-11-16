
from flask import request
from webargs.flaskparser import use_args

from libs.auth import jwt_required
from libs.base.resource import BaseResource
from nft.psd.model import Psd
from nft.psd.schema import PsdMixtureSchema, PsdLayerSaveSchema, PsdFilePostSchema


class PsdResource(BaseResource):
    @jwt_required
    @use_args(PsdFilePostSchema)
    def post(self, args):
        print(request.files)
        data = Psd.add_psd(file=request.files.get('file'), project=args.get('project'))
        return data


class PsdMixtureResource(BaseResource):
    @use_args(PsdMixtureSchema)
    def post(self, args):
        data = Psd.psd_mixture(**args)
        return data


class PsdLayerResource(BaseResource):
    @use_args(PsdLayerSaveSchema)
    def post(self, args):
        data = Psd.add_image_to_layer(**args)
        return data
