import copy
import datetime
import hashlib
import json
import os
import random
import uuid

from PIL import Image as pil_image
from psd_tools import PSDImage
from sqlalchemy.dialects.postgresql import JSONB

from config import load_config
from libs.base.model import BaseModel
from libs.error import dynamic_error
from nft import ext


class Psd():

    @classmethod
    def add_psd(cls, file):
        if not file:
            dynamic_error({}, code=422, message='请上传file')
        file_path = load_config().FILE
        psd_m = hashlib.md5(file.read()).hexdigest()
        file.seek(0)
        pmd_file_path = file_path + '/file/psd/{}.psd'.format(psd_m)
        if not os.path.exists(pmd_file_path):
            file.save(pmd_file_path)
        psd = PSDImage.open(pmd_file_path)
        content = []
        for p in psd:
            content.append(p.name)

        return {'id': psd_m, 'content': content}

    @classmethod
    def psd_mixture(cls, **kwargs):
        psd_m = kwargs.get('id')
        save_index = kwargs.get('save_index')
        layer = kwargs.get('layer')
        name = kwargs.get('name')

        layer_path = load_config().LAYER_FILE
        file_path = load_config().FILE

        for _, _, file_list in os.walk('{}/{}'.format(layer_path, layer)):
            for file in file_list:
                if file == name + '.png':

                    dynamic_error({}, code=422, message='已存在该名称图层')

        pmd_file_path = file_path + '/file/psd/{}.psd'.format(psd_m)

        try:
            psd = PSDImage.open(pmd_file_path)
            for i in range(len(psd)):
                if i not in save_index:
                    psd[i].visible = False
                    print(psd[i])
            file_layer_path = '{}/{}/{}.png'.format(layer_path, layer, name)
            print(file_layer_path)
            psd.compose(True).save(file_layer_path)

        except Exception as e:
            dynamic_error({}, code=422, message='创建图层失败' + str(e))

        return {'url': '{}://{}/files/layers/{}/{}.png'.format(
            load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, layer, name)}
