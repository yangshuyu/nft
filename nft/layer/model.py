import os
import random
import uuid

from PIL import Image as pil_image
from sqlalchemy.dialects.postgresql import JSONB

from config import load_config
from libs.base.model import BaseModel
from libs.error import dynamic_error
from nft.ext import db


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


class Image(BaseModel):
    __tablename__ = 'images'

    name = db.Column(db.String(512), nullable=False)
    attributes = db.Column(JSONB)
    description = db.Column(db.String(1024))

    @classmethod
    def combination_layer(cls, **kwargs):
        data = kwargs.get('data', {})
        layer_path = load_config().LAYER_FILE
        layers = ['background', 'body', 'cloth', 'drink', 'earring',
                  'eyewear', 'hat', 'mouth', 'nacklace', 'props']

        layer_images = []
        attributes = []
        for layer in layers:
            d = data.get(layer, [])

            ima = ''
            if d:
                ima = random.choice(d)
            else:
                for _, _, file_list in os.walk('{}/{}'.format(layer_path, layer)):
                    ima = random.choice(file_list)
            layer_images.append('{}/{}'.format(layer, ima))
            attribute = {'trait_type': layer.upper(), 'value': ima}
            attributes.append(attribute)

        image = cls.draw_picture(layer_images, attributes)
        return image

    @classmethod
    def draw_picture(cls, layer_images, attributes):
        layer_path = load_config().LAYER_FILE
        width = 2000
        height = 2000

        to_image = pil_image.new('RGBA', (width, height), (0, 0, 0, 0))

        image_id = str(uuid.uuid4())
        image = cls(
            id=image_id,
            name='Bored Mummy Baby #1',
            attributes=attributes,
            description='Bored Mummy Baby Waking Up (BMBWU) Collections series under Bored Mummy Waking Up NFT. '
                        'Take good care of your  mummy baby, and great favor will be returned.'
        )

        try:
            for i in range(len(layer_images)):
                from_imge = pil_image.open('{}/{}'.format(layer_path, layer_images[i])).convert('RGBA')
                to_image = pil_image.alpha_composite(to_image, from_imge)
            # to_image.show()

            to_image.save('{}/../images/{}.png'.format(layer_path, image_id))
            db.session.add(image)
            db.session.commit()
        except Exception as e:
            print(e)
            dynamic_error({}, code=422, message='图片生成失败' + str(e))

        return image

    @classmethod
    def get_images_by_query(cls, **kwargs):
        page = kwargs.get('page')
        per_page = kwargs.get('per_page')
        query = cls.query

        total = query.count()

        if page and per_page:
            query = query.limit(per_page).offset((page - 1) * per_page)

        return query.all(), total

