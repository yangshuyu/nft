import copy
import datetime
import hashlib
import json
import os
import random
import shutil
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
        print(pmd_file_path)
        try:
            print('-----------------')
            psd = PSDImage.open(pmd_file_path)
            print(psd)
            for i in range(len(psd)):
                if i not in save_index:
                    psd[i].visible = False
            file_layer_path = '{}/file/psd_images/{}_{}.png'.format(file_path, layer, name)
            print(file_layer_path)
            psd.compose(True).save(file_layer_path)

        except Exception as e:
            dynamic_error({}, code=422, message='创建图层失败' + str(e))

        new_name = '{}_{}.png'.format(layer, name)
        return {
            'url': '{}://{}/files/psd_images/{}'.format(
                load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, new_name),
            'name': new_name
        }

    @classmethod
    def add_image_to_layer(cls, **kwargs):
        name = kwargs.get('name')
        arry = name.split('_')
        layer, image_name = arry[0], '_'.join(arry[1:])

        layer_path = load_config().LAYER_FILE
        file_path = load_config().FILE

        try:
            old_file_path = '{}/file/psd_images/{}'.format(file_path, name)
            new_file_path = '{}/{}/{}'.format(layer_path, layer, image_name)

            shutil.move(old_file_path, new_file_path)
        except Exception as e:
            print(e)
            dynamic_error({}, code=422, message='移动文件失败' + str(e))

        return {'url': '{}://{}/files/layers/{}/{}'.format(
            load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, layer, image_name)}
