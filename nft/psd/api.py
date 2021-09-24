
from flask import request
from webargs.flaskparser import use_args

from libs.base.resource import BaseResource
from nft.psd.model import Psd
from nft.psd.schema import PsdMixtureSchema


class PsdResource(BaseResource):
    def post(self):
        file = request.files.get('file')
        data = Psd.add_psd(file)
        return data


class PsdMixtureResource(BaseResource):
    @use_args(PsdMixtureSchema)
    def post(self, args):
        data = Psd.psd_mixture(**args)
        return data
