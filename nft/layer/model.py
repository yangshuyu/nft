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
            'file': file,
            'url': '{}://{}/files/layers/{}/{}'.format(
                load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, path, file)
        }
        traits_str = _get_str(file, "{", "}").split("&")
        result['traits'] = list(map(
            lambda x: (_get_str(x, "<", ">"), x.split(">")[1]), traits_str
        ))
        return result

    @classmethod
    def get_layers_by_query(cls, **kwargs):
        project = kwargs.get('project')
        layer_path = '{}/{}/{}'.format(
            load_config().PROJECT_FILE, project, 'layers'
        )

        result = {}
        for path, dir_list, file_list in os.walk(layer_path):
            for dir_name in dir_list:
                result[dir_name] = []
                for _, _, file in os.walk('{}/{}'.format(layer_path, dir_name)):
                    for f in file:
                        if not f.startswith('.'):
                            result[dir_name].append(cls.decompose_layers(f, dir_name))
        return result

    @classmethod
    def get_layers_list_by_query(cls, **kwargs):
        data = []
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 20)
        q = kwargs.get('q')

        project = kwargs.get('project')
        layer_path = '{}/{}/{}'.format(
            load_config().PROJECT_FILE, project, 'layers'
        )
        for path, dir_list, file_list in os.walk(layer_path):
            for dir_name in dir_list:
                for r, _, file in os.walk('{}/{}'.format(layer_path, dir_name)):
                    for f in file:
                        if not f.startswith('.'):
                            if q:
                                if q not in f and q not in r:
                                    continue
                            d = cls.decompose_layers(f, dir_name)
                            d['layer'] = dir_name
                            data.append(d)

        return data[(page - 1) * per_page: page * per_page], len(data)

    @classmethod
    def remove_layer(cls, **kwargs):
        layer = kwargs.get('layer')
        name = kwargs.get('name')

        project = kwargs.get('project')
        layer_path = '{}/{}/{}'.format(
            load_config().PROJECT_FILE, project, 'layers'
        )

        if os.path.exists(layer_path + '/{}/{}'.format(layer, name)):
            os.remove(layer_path + '/{}/{}'.format(layer, name))

    @classmethod
    def move_layer(cls, **kwargs):
        ole_layer = kwargs.get('old_layer')
        old_name = kwargs.get('old_name')
        new_layer = kwargs.get('new_layer')
        new_name = kwargs.get('new_name')

        project = kwargs.get('project')
        layer_path = '{}/{}/{}'.format(
            load_config().PROJECT_FILE, project, 'layers'
        )

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

        project = kwargs.get('project')
        layer_path = '{}/{}/{}'.format(
            load_config().PROJECT_FILE, project, 'layers'
        )

        old_file_path = layer_path + '/{}/{}'.format(layer, name)
        new_file_path = layer_path + '/{}/{}'.format(layer, new_name)

        if not os.path.exists(old_file_path):
            dynamic_error({}, code=422, message='不存在该文件')

        try:
            shutil.move(old_file_path, new_file_path)
        except Exception as e:
            print(e)

        return {'url': '{}://{}/files/projects/layers/{}/{}'.format(
            load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, layer, new_name)}


class Image():

    def __init__(self, name, attributes, description, timestamp):
        self.name = name
        self.attributes = attributes
        self.description = description
        self.timestamp = timestamp

    @classmethod
    def add_image(cls, **kwargs):
        project = kwargs.get('project')
        user = kwargs.get('user', {})
        if not project:
            dynamic_error({}, code=422, message='请选择项目')

        if user.get('role') != 1 and project not in user.get('projects', []):
            dynamic_error({}, code=422, message='请选择项目')

        layer_images = cls.combination_layer(**kwargs)
        image_id, err = cls.calibration_md5(layer_images, user, project)
        if err:
            dynamic_error({}, code=422, message=err)
        image, map_json, err = cls.create_image(layer_images, image_id, user, project)
        if err:
            dynamic_error({}, code=422, message=err)
        result = cls.generate_data(image, map_json, image_id, user, project)
        return result

    @classmethod
    def batch_add_images(cls, **kwargs):
        from libs.task.batch_add_images_task import batch_add_images_task
        user = kwargs.get('user')
        project = kwargs.get('project')

        user_data = ext.user_batch_data.get(user.get('id'))

        if user_data:
            if user_data.get(project) and user_data.get(project).get('required_quantity') > 0:
                dynamic_error({}, code=422, message='该项目有任务在执行')

        ThreadPoolExecutor(2).submit(batch_add_images_task, **kwargs)

    @classmethod
    def combination_layer(cls, **kwargs):
        project = kwargs.get('project')
        layer_path = '{}/{}/{}'.format(
            load_config().PROJECT_FILE, project, 'layers'
        )
        temp_layers, layers = [], []
        for dir, _, _ in os.walk('{}'.format(layer_path)):
            if layer_path == dir or 'temp' in dir:
                continue
            for _, _, file_list_c in os.walk('{}'.format(dir)):
                if file_list_c:
                    tl = {'k': dir.split('/')[-1], 'v': int(file_list_c[0].split('-')[0])}
                    temp_layers.append(tl)

        temp_layers = sorted(temp_layers, key=lambda t1: t1.get('v'))
        for t in temp_layers:
            layers.append(t['k'])

        layer_images = []
        for layer in layers:
            d = kwargs.get(layer)
            percentage = d.get('percentage', 100)
            layer_data = d.get('data', [])

            if layer_data:
                ima = random.choice(layer_data)
            else:
                for _, _, file_list in os.walk('{}/{}'.format(layer_path, layer)):
                    correct_file_list = []
                    for f in file_list:
                        if not f.startswith('.'):
                            correct_file_list.append(f)
                    ima = random.choice(correct_file_list)
                ima = '{}/{}'.format(layer, ima)

            per = random.randint(0, 100)
            if per < percentage:
                layer_images.append(ima)
        return layer_images

    @classmethod
    def calibration_md5(cls, layer_images, user, project):
        m = hashlib.md5(str(sorted(layer_images)).encode('utf-8')).hexdigest()
        for d in ext.user_all_data.get(user.get('id')).get(project):
            if d['layer'].get('md5') == m:
                return None, '图片重复'
        return m, None

    @classmethod
    def create_image(cls, layer_images, image_id, user, project):
        layer_path = '{}/{}/{}'.format(
            load_config().PROJECT_FILE, project, 'layers'
        )
        save_path = '{}/{}/users/{}'.format(
            load_config().PROJECT_FILE, project, user.get('id')
        )

        width = ext.project_config.get(project, {}).get('width', 2000)
        height = ext.project_config.get(project, {}).get('high', 2000)

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

            if not os.path.exists(save_path + '/images/'):
                os.mkdir(save_path + '/images/')

            if not os.path.exists(save_path + '/mini_images/'):
                os.mkdir(save_path + '/mini_images/')

            to_image.save('{}/images/{}.png'.format(save_path, image_id))

            w, h = to_image.size
            to_image.thumbnail((w / 6, h / 6), pil_image.ANTIALIAS)
            to_image.save('{}/mini_images/{}.png'.format(save_path, image_id))
            temp_data = image.__dict__

            if not os.path.exists(save_path + '/json/'):
                os.mkdir(save_path + '/json/')

            if not os.path.exists(save_path + '/map_json/'):
                os.mkdir(save_path + '/map_json/')

            with open('{}/json/{}.json'.format(save_path, str(image_id)), 'a') as content:
                content.write(json.dumps(temp_data))

            with open('{}/map_json/{}.json'.format(save_path, str(image_id)), 'a') as content:
                content.write(json.dumps(map_json))
                temp_data['layer'] = map_json
            ext.user_all_data[user.get('id')][project].append(temp_data)

        except Exception as e:
            return None, None, '图片生成失败' + str(e)

        return image, map_json, None

    @classmethod
    def generate_data(cls, image, map_json, image_id, user, project):

        result = image.__dict__
        result['layer'] = map_json
        result['id'] = image_id
        result['url'] = '{}://{}/files/projects/{}/users/{}/mini_images/{}.png'.format(
            load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, project, user.get('id'), image_id)
        return result

    @classmethod
    def get_images_by_query(cls, **kwargs):
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 20)
        conditions = kwargs.get('conditions')
        project = kwargs.get('project')
        user = kwargs.get('user')
        t = kwargs.get('type')

        if t == 0:
            result = copy.deepcopy(ext.project_all_data.get(project))
            if conditions:
                for data in ext.project_all_data.get(project):
                    for key, value in conditions.items():
                        if data['layer'].get(key) not in value:
                            result.remove(data)
                            break
        else:
            result = copy.deepcopy(ext.user_all_data.get(user.get('id')).get(project))
            if conditions:
                for data in ext.user_all_data.get(user.get('id')).get(project):
                    for key, value in conditions.items():
                        if data['layer'].get(key) not in value:
                            result.remove(data)
                            break

        result = sorted(result, key=lambda item: item.get('timestamp', 0), reverse=True)

        total = len(result)
        data = result[(page - 1) * per_page: page * per_page]
        for d in data:
            if t == 0:
                d['id'] = d['layer']['md5']
                d['url'] = '{}://{}/files/projects/{}/mini_images/{}.png'.format(
                    load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, project, d['layer']['md5'])
                d['lossless_url'] = '{}://{}/files/projects/{}/images/{}.png'.format(
                    load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN, project, d['layer']['md5'])
            else:
                d['id'] = d['layer']['md5']
                d['url'] = '{}://{}/files/projects/{}/users/{}/mini_images/{}.png'.format(
                    load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN,
                    project, user.get('id'), d['layer']['md5'])
                d['lossless_url'] = '{}://{}/files/projects/{}/users/{}images/{}.png'.format(
                    load_config().SERVER_SCHEME, load_config().SERVER_DOMAIN,
                    project, user.get('id'), d['layer']['md5'])

        return data, total

    @classmethod
    def delete(cls, **kwargs):
        image_id = kwargs.get('image_id')
        project = kwargs.get('project')
        t = kwargs.get('type')
        user = kwargs.get('user')
        file_path = load_config().PROJECT_FILE
        if t == 0:
            try:
                if os.path.exists(file_path + '/{}/images/{}.png'.format(project, image_id)):
                    os.remove(file_path + '/{}/images/{}.png'.format(project, image_id))

                if os.path.exists(file_path + '/{}/mini_image/{}.png'.format(project, image_id)):
                    os.remove(file_path + '/{}/mini_image/{}.png'.format(project, image_id))
                    # os.unlink(file_path)
                print(file_path + '/{}/json/{}.json'.format(project, image_id))
                if os.path.exists(file_path + '/{}/json/{}.json'.format(project, image_id)):
                    os.remove(file_path + '/{}/json/{}.json'.format(project, image_id))
                    # os.unlink(file_path)

                if os.path.exists(file_path + '/{}/map_json/{}.json'.format(project, image_id)):
                    os.remove(file_path + '/{}/map_json/{}.json'.format(project, image_id))
                    # os.unlink(file_path)

                for d in ext.project_all_data.get(project):
                    if d['layer'].get('md5') == image_id:
                        ext.project_all_data.get(project).remove(d)
            except Exception as e:
                print(e)
        elif t == 1:
            try:
                if os.path.exists(file_path + '/{}/users/{}/images/{}.png'.format(
                        project, user.get('id'), image_id)):
                    os.remove(file_path + '/{}/users/{}/images/{}.png'.format(
                        project, user.get('id'), image_id))
                    # os.unlink(file_path)

                if os.path.exists(file_path + '/{}/users/{}/min_image/{}.png'.format(
                        project, user.get('id'), image_id)):
                    os.remove(file_path + '/{}/users/{}/mini_image/{}.png'.format(
                        project, user.get('id'), image_id))

                if os.path.exists(file_path + '/{}/users/{}/json/{}.json'.format(
                        project, user.get('id'), image_id)):
                    os.remove(file_path + '/{}/users/{}/json/{}.json'.format(
                        project, user.get('id'), image_id))
                    # os.unlink(file_path)

                if os.path.exists(file_path + '/{}/users/{}/map_json/{}.json'.format(
                        project, user.get('id'), image_id)):
                    os.remove(file_path + '/{}/users/{}/map_json/{}.json'.format(
                        project, user.get('id'), image_id))
                    # os.unlink(file_path)
                for d in ext.user_all_data.get(user.get('id')).get(project):
                    if d['layer'].get('md5') == image_id:
                        ext.user_all_data.get(user.get('id')).get(project).remove(d)
            except Exception as e:
                print(e)

    @classmethod
    def update(cls, image_id, **kwargs):
        image = cls.add_image(**kwargs)
        kwargs['image_id'] = image_id
        cls.delete(**kwargs)
        return image

    @classmethod
    def batch_delete(cls, **kwargs):
        image_ids = kwargs.get('image_ids', [])

        for image_id in image_ids:
            kwargs['image_id'] = image_id
            cls.delete(**kwargs)

    @classmethod
    def get_image_layer_dashboard(cls, **kwargs):
        result = {}
        t = kwargs.get('type')
        project = kwargs.get('project')
        user = kwargs.get('user')

        if t == 0:
            all_data = ext.project_all_data.get(project)
        else:
            all_data = ext.user_all_data.get(user.get('id')).get(project)

        for data in all_data:
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
                data[layer][k] = int(value / user_count * 100)

        return data

    @classmethod
    def temporary_to_permanent(cls, **kwargs):
        user = kwargs.get('user')
        project = kwargs.get('project')
        image_ids = kwargs.get('image_ids')
        file_path = load_config().PROJECT_FILE

        for image_id in image_ids:

            old_file_path = file_path + \
                            '/{}/users/{}/'.format(project, user.get('id'))
            new_file_path = file_path + '/{}/'.format(project)

            if not os.path.exists(old_file_path + 'json/{}.json'.format(image_id)):
                continue

            if os.path.exists(new_file_path + 'map_json/{}.json'.format(image_id)):
                continue

            try:
                shutil.move(old_file_path + 'images/{}.png'.format(image_id),
                            new_file_path + 'images/{}.png'.format(image_id))
                shutil.move(old_file_path + 'mini_images/{}.png'.format(image_id),
                            new_file_path + 'mini_images/{}.png'.format(image_id))
                shutil.move(old_file_path + 'json/{}.json'.format(image_id),
                            new_file_path + 'json/{}.json'.format(image_id))
                shutil.move(old_file_path + 'map_json/{}.json'.format(image_id),
                            new_file_path + 'map_json/{}.json'.format(image_id))

                data = ext.user_all_data.get(user.get('id')).get(project)

                for index, item in enumerate(data):
                    if item.get('layer', {}).get('md5') == image_id:
                        ext.user_all_data.get(user.get('id')).get(project).remove(item)
                        ext.project_all_data.get(project).append(item)
                        break

            except Exception as e:
                print(e)
