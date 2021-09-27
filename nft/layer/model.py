import copy
import datetime
import hashlib
import json
import os
import random
import shutil
import uuid

from PIL import Image as pil_image

from config import load_config
from libs.error import dynamic_error
from nft import ext
from concurrent.futures import ThreadPoolExecutor


class Layer():

    @classmethod
    def decompose_layers(cls, file, path):
        def _get_str(s, left, right):
            return s.split(left)[1].split(right)[0]

        result = {
            'name': _get_str(file, "-", ":"),
            'weight': int(_get_str(file, ":", "{")),
            'fullpath': path + "/" + file,
            'file': file
        }
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

    @classmethod
    def remove_layer(cls, **kwargs):
        layer = kwargs.get('layer')
        name = kwargs.get('name')
        layer_path = load_config().LAYER_FILE

        if os.path.exists(layer_path + '/{}/{}'.format(layer, name)):
            os.remove(layer_path + '/{}/{}'.format(layer, name))

    @classmethod
    def move_layer(cls, **kwargs):
        ole_layer = kwargs.get('old_layer')
        old_name = kwargs.get('old_name')
        new_layer = kwargs.get('new_layer')
        new_name = kwargs.get('new_name')

        layer_path = load_config().LAYER_FILE

        old_file_path = layer_path + '/{}/{}'.format(ole_layer, old_name)
        new_file_path = layer_path + '/{}/{}'.format(new_layer, new_name)

        if not os.path.exists(old_file_path):
            dynamic_error({}, code=422, message='不存在该文件')

        if os.path.exists(new_file_path):
            dynamic_error({}, code=422, message='已存在该同名文件')

        try:
            shutil.move(old_file_path, new_file_path)
        except Exception as e:
            print(e)

        return {'url': '{}://{}/files/layers/{}/{}'.format(
            load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, new_layer, new_name)}

    @classmethod
    def update(cls, **kwargs):
        layer = kwargs.get('layer')
        name = kwargs.get('name')
        new_name = kwargs.get('new_name')

        layer_path = load_config().LAYER_FILE

        old_file_path = layer_path + '/{}/{}'.format(layer, name)
        new_file_path = layer_path + '/{}/{}'.format(layer, new_name)

        if not os.path.exists(old_file_path):
            dynamic_error({}, code=422, message='不存在该文件')

        try:
            shutil.move(old_file_path, new_file_path)
        except Exception as e:
            print(e)

        return {'url': '{}://{}/files/layers/{}/{}'.format(
            load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, layer, new_name)}


class Image():

    def __init__(self, name, attributes, description, timestamp):
        self.name = name
        self.attributes = attributes
        self.description = description
        self.timestamp = timestamp

    @classmethod
    def add_image(cls, **kwargs):
        layer_images = cls.combination_layer(**kwargs)
        image_id, err = cls.calibration_md5(layer_images)
        if err:
            dynamic_error({}, code=422, message=err)
        image, map_json, err = cls.create_image(layer_images, image_id)
        if err:
            dynamic_error({}, code=422, message=err)
        result = cls.generate_data(image, map_json, image_id)
        return result

    @classmethod
    def batch_add_images(cls, **kwargs):
        from libs.task.batch_add_images_task import batch_add_images_task
        if ext.required_quantity > 0:
            dynamic_error({}, code=422, message='有任务在执行')

        ThreadPoolExecutor(2).submit(batch_add_images_task, **kwargs)

    @classmethod
    def combination_layer(cls, **kwargs):
        layer_path = load_config().LAYER_FILE
        layers = ['background', 'body', 'cloth', 'drink', 'earring',
                  'eyewear', 'hat', 'mouth', 'nacklace', 'props']

        layer_images = []
        for layer in layers:
            d = kwargs.get(layer)
            percentage = d.get('percentage', 100)
            layer_data = d.get('data', [])

            if layer_data:
                ima = random.choice(layer_data)
            else:
                for _, _, file_list in os.walk('{}/{}'.format(layer_path, layer)):
                    ima = random.choice(file_list)
                ima = '{}/{}'.format(layer, ima)

            per = random.randint(0, 100)
            if per < percentage:
                layer_images.append(ima)
        return layer_images

    @classmethod
    def calibration_md5(cls, layer_images):
        m = hashlib.md5(str(sorted(layer_images)).encode('utf-8')).hexdigest()

        for d in ext.all_data:
            if d['layer'].get('md5') == m:
                return None, '图片重复'

        return m, None

    @classmethod
    def create_image(cls, layer_images, image_id):
        layer_path = load_config().LAYER_FILE
        file_path = load_config().FILE
        width = 2000
        height = 2000

        to_image = pil_image.new('RGBA', (width, height), (0, 0, 0, 0))

        timestamp = int(datetime.datetime.now().timestamp())
        image = Image(
            name='name #1',
            attributes=[],
            description='this is an awsome project',
            timestamp=timestamp
        )

        map_json = {'md5': image_id}
        try:
            for i in range(len(layer_images)):
                from_imge = pil_image.open('{}/{}'.format(layer_path, layer_images[i])).convert('RGBA')
                to_image = pil_image.alpha_composite(to_image, from_imge)

                file = layer_images[i].split('/')[1]
                traits = Layer.decompose_layers(file, layer_path).get('traits')
                image.attributes.append({'trait_type': traits[0][0], 'value': traits[0][1]})
                temp_map = layer_images[i].split('/')
                map_json[temp_map[0]] = layer_images[i]

            to_image.save('{}/../images/{}.png'.format(layer_path, image_id))

            w, h = to_image.size
            to_image.thumbnail((w / 6, h / 6), pil_image.ANTIALIAS)
            to_image.save('{}/../mini_images/{}.png'.format(layer_path, image_id))
            temp_data = image.__dict__

            with open('{}/file/json/{}.json'.format(file_path, str(image_id)), 'a') as content:
                content.write(json.dumps(temp_data))

            with open('{}/file/map_json/{}.json'.format(file_path, str(image_id)), 'a') as content:
                content.write(json.dumps(map_json))
                temp_data['layer'] = map_json
            ext.all_data.append(temp_data)

        except Exception as e:
            return None, None, '图片生成失败' + str(e)

        return image, map_json, None

    @classmethod
    def generate_data(cls, image, map_json, image_id):

        result = image.__dict__
        result['layer'] = map_json
        result['id'] = image_id
        result['url'] = '{}://{}/files/mini_images/{}.png'.format(
            load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, image_id)
        return result

    @classmethod
    def get_images_by_query(cls, **kwargs):
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 20)
        conditions = kwargs.get('conditions')
        result = copy.deepcopy(ext.all_data)
        result = sorted(result, key=lambda item: item.get('timestamp', 0), reverse=True)
        if conditions:
            for data in ext.all_data:
                for key, value in conditions.items():
                    if data['layer'].get(key) not in value:
                        result.remove(data)
                        break
        total = len(result)
        data = result[(page - 1) * per_page: page * per_page]
        for d in data:
            d['id'] = d['layer']['md5']
            d['url'] = '{}://{}/files/mini_images/{}.png'.format(
                load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, d['layer']['md5'])
            d['lossless_url'] = '{}://{}/files/images/{}.png'.format(
                load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, d['layer']['md5'])
        return result[(page - 1) * per_page: page * per_page], total

    @classmethod
    def delete(cls, image_id):
        file_path = load_config().FILE
        try:
            if os.path.exists(file_path + '/file/images/{}.png'.format(image_id)):
                os.remove(file_path + '/file/images/{}.png'.format(image_id))
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
    def update(cls, image_id, **kwargs):
        image = cls.add_image(**kwargs)
        cls.delete(image_id)
        return image

    @classmethod
    def batch_delete(cls, **kwargs):
        image_ids = kwargs.get('image_ids', [])

        for image_id in image_ids:
            cls.delete(image_id)

    @classmethod
    def get_image_layer_dashboard(cls):
        result = {}
        for data in ext.all_data:
            layer = data.get('layer')
            for key, value in layer.items():
                if key == 'md5':
                    continue
                if result.get(key):
                    result[key]['count'] += 1
                    if result[key].get(value):
                        result[key][value] += 1
                    else:
                        result[key][value] = 1
                else:
                    result[key] = {'count': 1, value: 1}

        data = {}
        for layer, layer_data in result.items():
            data[layer] = {}
            user_count = layer_data.get('count')
            for key, value in layer_data.items():
                if key == 'count':
                    continue
                k = key.split('-')[1].split(':')[0]
                data[layer][k] = int(value/user_count*100)

        return data
