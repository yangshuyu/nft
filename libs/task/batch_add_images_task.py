import time

from config import load_config
from nft import ext
from nft.layer.model import Image


def batch_add_images_task(**kwargs):
    nums = kwargs.get('nums')
    image_data = kwargs.get('data')
    project = kwargs.get('project')
    user = kwargs.get('user')

    image_data['user'] = user
    image_data['project'] = project

    grand_err_total = 0

    user_data = ext.user_batch_data.get(user.get('id'))
    if not user_data:
        ext.user_batch_data[user.get('id')] = {
            project: {'required_quantity': nums, 'completed_quantity': 0}}

    if not ext.user_batch_data[user.get('id')].get('project'):
        ext.user_batch_data[user.get('id')][project] = {'required_quantity': nums, 'completed_quantity': 0}

    while ext.user_batch_data[user.get('id')][project]['completed_quantity'] < nums:

        if grand_err_total > 30:
            # 连续30张生成失败，停止生成
            ext.user_batch_data[user.get('id')].pop(project)
            break
        layer_images = Image.combination_layer(**image_data)
        image_id, err = Image.calibration_md5(layer_images, user, project)
        if err:
            grand_err_total += 1
            continue
        image, map_json, err = Image.create_image(layer_images, image_id, user, project)
        if err:
            grand_err_total += 1
            continue

        ext.user_batch_data[user.get('id')][project]['completed_quantity'] += 1
        grand_err_total = 0
    time.sleep(3)
    ext.user_batch_data[user.get('id')][project] = {'required_quantity': -1, 'completed_quantity': 0}
