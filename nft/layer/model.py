import copy
import datetime
import hashlib
import json
import os
import random
import uuid

from PIL import Image as pil_image
from sqlalchemy.dialects.postgresql import JSONB

from config import load_config
from libs.base.model import BaseModel
from libs.error import dynamic_error
from nft import ext


class Layer():

    @classmethod
    def decompose_layers(cls, file, path):
        def _get_str(s, left, right):
            return s.split(left)[1].split(right)[0]

        result = {
            'name': _get_str(file, "-", ":"),
            'weight': int(_get_str(file, ":", "{")),
            'fullpath': path + "/" + file}
        traits_str = _get_str(file, "{", "}").split("&")
        result['traits'] = list(map(
            lambda x: (_get_str(x, "<", ">"), x.split(">")[1]), traits_str
        ))
        return result

    @classmethod
    def get_layers_by_query(cls, **kwargs):
        layer_path = load_config().LAYER_FILE
        result = {}
        for path, dir_list, file_list in os.walk(layer_path):
            for dir_name in dir_list:
                result[dir_name] = []
                for _, _, file in os.walk('{}/{}'.format(layer_path, dir_name)):
                    for f in file:
                        result[dir_name].append(cls.decompose_layers(f, dir_name))
        return result


class Image():

    def __init__(self, name, attributes, description, timestamp):
        self.name = name
        self.attributes = attributes
        self.description = description
        self.timestamp = timestamp

    @classmethod
    def combination_layer(cls, **kwargs):
        data = kwargs.get('data', {})
        layer_path = load_config().LAYER_FILE
        layers = ['background', 'body', 'cloth', 'drink', 'earring',
                  'eyewear', 'hat', 'mouth', 'nacklace', 'props']

        layer_images = []
        for layer in layers:
            d = data.get(layer, [])

            ima = ''
            if d:
                ima = random.choice(d)
            else:
                for _, _, file_list in os.walk('{}/{}'.format(layer_path, layer)):
                    ima = random.choice(file_list)
                ima = '{}/{}'.format(layer, ima)
            layer_images.append(ima)

        image = cls.draw_picture(layer_images)
        return image

    @classmethod
    def draw_picture(cls, layer_images):
        layer_path = load_config().LAYER_FILE
        file_path = load_config().FILE
        width = 2000
        height = 2000

        to_image = pil_image.new('RGBA', (width, height), (0, 0, 0, 0))

        timestamp = int(datetime.datetime.now().timestamp())
        image = Image(
            name='Bored Mummy Baby #1',
            attributes=[],
            description='Bored Mummy Baby Waking Up (BMBWU) Collections series under Bored Mummy Waking Up NFT. '
                        'Take good care of your  mummy baby, and great favor will be returned.',
            timestamp=timestamp
        )

        map_json = {}
        # 校验图片是否重复
        m = hashlib.md5(str(sorted(layer_images)).encode('utf-8')).hexdigest()

        for d in ext.all_data:
            if d['layer'].get('md5') == m:
                dynamic_error({}, code=422, message='生成重复图片')
        map_json['md5'] = m

        try:
            for i in range(len(layer_images)):
                from_imge = pil_image.open('{}/{}'.format(layer_path, layer_images[i])).convert('RGBA')
                to_image = pil_image.alpha_composite(to_image, from_imge)

                file = layer_images[i].split('/')[1]
                traits = Layer.decompose_layers(file, layer_path).get('traits')
                image.attributes.append({'trait_type': traits[0][0], 'value': traits[0][1]})
                temp_map = layer_images[i].split('/')
                map_json[temp_map[0]] = layer_images[i]
            # to_image.show()

            to_image.save('{}/../images/{}.png'.format(layer_path, m))
            temp_data = image.__dict__
            with open('{}/file/json/{}.json'.format(file_path, str(m)), 'a') as content:
                content.write(json.dumps(temp_data))

            with open('{}/file/map_json/{}.json'.format(file_path, str(m)), 'a') as content:
                content.write(json.dumps(map_json))
                temp_data['layer'] = map_json

            ext.all_data.append(temp_data)

        except Exception as e:
            print(e)
            dynamic_error({}, code=422, message='图片生成失败' + str(e))
        result = image.__dict__
        result['layer'] = map_json
        return result

    @classmethod
    def get_images_by_query(cls, **kwargs):
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 20)
        conditions = kwargs.get('conditions')
        result = copy.deepcopy(ext.all_data)
        if conditions:
            for data in ext.all_data:
                for key, value in conditions.items():
                    if data['layer'].get(key) not in value:
                        result.remove(data)
                        break
        total = len(result)

        return result[(page-1)*per_page: page * per_page], total

    @classmethod
    def delete(cls, image_id):
        file_path = load_config().FILE
        try:
            if os.path.exists(file_path + '/file/image/{}.png'.format(image_id)):
                os.remove(file_path + '/file/image/{}.png'.format(image_id))
                # os.unlink(file_path)

            if os.path.exists(file_path + '/file/json/{}.json'.format(image_id)):
                os.remove(file_path + '/file/json/{}.json'.format(image_id))
                # os.unlink(file_path)

            if os.path.exists(file_path + '/file/map_json/{}.json'.format(image_id)):
                os.remove(file_path + '/file/map_json/{}.json'.format(image_id))
                # os.unlink(file_path)

            for d in ext.all_data:
                if d['layer'].get('md5') == image_id:
                    ext.all_data.remove(d)
        except Exception as e:
            print(e)

    @classmethod
    def update(cls, image_id, kwargs):
        image = cls.combination_layer(**kwargs)
        cls.delete(image_id)
        return image
