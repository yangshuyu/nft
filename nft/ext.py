from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy(session_options={"autoflush": False, "autocommit": False})
migrate = Migrate(compare_type=True)
project_all_data = {}
project_config = {}
user_all_data = {}
# required_quantity = -1
# completed_quantity = 0
users = []
projects = []

user_batch_data = {}

# project_all_data
# {'a': [], 'monkey': [{'name': 'name #1', 'attributes': [{'trait_type': 'Background', 'value': 'Aquamarine'},
#                                                         {'trait_type': 'Cloth', 'value': 'White Shirt'},
#                                                         {'trait_type': 'Food', 'value': 'Banana'},
#                                                         {'trait_type': 'Earring', 'value': 'Circle'},
#                                                         {'trait_type': 'Hat', 'value': 'Cowboy'},
#                                                         {'trait_type': 'Mask', 'value': 'Black'},
#                                                         {'trait_type': 'Nacklace', 'value': 'Bitcoin'},
#                                                         {'trait_type': 'Extra', 'value': 'Red Beam'}],
#                       'description': 'this is an awsome project', 'timestamp': 1633935692,
#                       'layer': {'md5': '15b8ea7994b579970de8f5304a97a10a',
#                                 'background1': 'background1/1-Aquamarine:100{<Background>Aquamarine}.png',
#                                 'cloth': 'cloth/3-open_shirt:100{<Cloth>White Shirt}.png',
#                                 'drink': 'drink/4-banana:100{<Food>Banana}.png',
#                                 'earring': 'earring/9-ring:100{<Earring>Circle}.png',
#                                 'hat': 'hat/7-Cowboy:100{<Hat>Cowboy}.png',
#                                 'mouth': 'mouth/8-black:100{<Mask>Black}.png',
#                                 'nacklace': 'nacklace/9-bitcoin:100{<Nacklace>Bitcoin}.png',
#                                 'props': 'props/10-lasereyes_red:9{<Extra>Red Beam}.png'}}]}


# user_all_data
# {1: {'a': [], 'monkey': [{'name': 'name #1', 'attributes': [{'trait_type': 'Background', 'value': 'Purple'},
#                                                             {'trait_type': 'Cloth', 'value': 'White Shirt'},
#                                                             {'trait_type': 'Extra', 'value': 'Microphone'},
#                                                             {'trait_type': 'Earring', 'value': 'Golden Ethereum'},
#                                                             {'trait_type': 'Hat', 'value': 'Bandage'},
#                                                             {'trait_type': 'Nacklace', 'value': 'Golden'},
#                                                             {'trait_type': 'Extra', 'value': 'Red Beam'}],
#                           'description': 'this is an awsome project', 'timestamp': 1636713101,
#                           'layer': {'md5': '1ae67d4077d1a0bb660261e65fef0470',
#                                     'background': 'background/1-Purple:100{<Background>Purple}.png',
#                                     'cloth': 'cloth/3-open_shirt:100{<Cloth>White Shirt}.png',
#                                     'drink': 'drink/4-microphone:100{<Extra>Microphone}.png',
#                                     'earring': 'earring/5-eth_gold:100{<Earring>Golden Ethereum}.png',
#                                     'hat': 'hat/7-bandages:100{<Hat>Bandage}.png',
#                                     'nacklace': 'nacklace/9-gold:100{<Nacklace>Golden}.png',
#                                     'props': 'props/10-lasereyes_red:9{<Extra>Red Beam}.png'}}]}, 2: {}}
