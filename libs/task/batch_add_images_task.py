import time

from config import load_config
from nft import ext
from nft.layer.model import Image


def batch_add_images_task(**kwargs):
    nums = kwargs.get('nums')
    image_data = kwargs.get('data')

    grand_err_total = 0
    ext.required_quantity = nums
    ext.completed_quantity = 0
    while ext.completed_quantity < nums:

        if grand_err_total > 30:
            # 连续30张生成失败，停止生成
            ext.required_quantity = -1
            ext.completed_quantity = 0
            break
        layer_images = Image.combination_layer(**image_data)
        image_id, err = Image.calibration_md5(layer_images)
        if err:
            grand_err_total += 1
            continue
        image, map_json, err = Image.create_image(layer_images, image_id)
        if err:
            grand_err_total += 1
            continue

        ext.completed_quantity += 1
        grand_err_total = 0
    time.sleep(3)
    ext.required_quantity = -1
    ext.completed_quantity = 0
