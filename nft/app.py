import json
import os
import re

from flask import Flask
from flask_cors import CORS

from nft import BLUEPRINTS
from config import load_config
from nft.ext import db, migrate

from nft import ext


def create_app(app_name="api", blueprints=None):
    app = Flask(app_name)
    config = load_config()
    app.config.from_object(config)

    if blueprints is None:
        blueprints = BLUEPRINTS
    blueprints_resister(app, blueprints)
    extensions_load(app)

    return app


def blueprints_resister(app, blueprints):
    for bp in blueprints:
        app.register_blueprint(bp)
        api_list = ['%s' % rule for rule in app.url_map.iter_rules()]
        api_dict = dict()
        for api in api_list:
            api_re = re.compile(r'\<\w+\>?')
            api_out = re.sub(api_re, '{}', api)
            api_dict[api_out] = api
        app.api_dict = api_dict


def extensions_load(app):
    # db.init_app(app)
    # migrate.init_app(app, db)
    #
    # CORS(app, resources={r"*": {"origins": "*", "expose_headers": "X-Total"}})
    ext.all_data = load_all_data()


def load_all_data():
    file_path = load_config().FILE + '/file/json'
    map_file_path = load_config().FILE + '/file/map_json'
    data = []
    for _, _, file in os.walk('{}'.format(file_path)):
        for f in file:
            try:
                with open('{}/{}'.format(file_path, f)) as content:
                    d = json.load(content)
                    with open('{}/{}'.format(map_file_path, f)) as map_content:
                        d['layer'] = json.load(map_content)
                    data.append(d)
            except Exception as e:
                print(e)

    return data
