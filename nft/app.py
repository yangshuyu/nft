import ast
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
    CORS(app, resources={r"*": {"origins": "*", "expose_headers": "X-Total"}})
    # init_dirs()
    load_all_users()
    load_all_projects()
    load_project_data()
    load_user_data()


def load_all_users():
    file_path = load_config().FILE + '/file/users.json'
    with open(file_path) as f:
        ext.users = json.loads(f.read())


def load_all_projects():
    file_path = load_config().PROJECT_FILE
    for _, b, file in os.walk('{}'.format(file_path)):
        ext.projects = b
        break


def load_project_data():
    for project in ext.projects:
        file_path = '{}/{}/{}'.format(load_config().PROJECT_FILE, project, 'json')
        map_file_path = '{}/{}/{}'.format(load_config().PROJECT_FILE, project, 'map_json')

        data = []
        for _, _, file in os.walk('{}'.format(file_path)):
            for f in file:
                try:
                    with open('{}/{}'.format(file_path, f)) as f_json:

                        d = json.loads(f_json.read())
                        with open('{}/{}'.format(map_file_path, f)) as map_json:
                            # print(map_json.read())
                            map_data = map_json.read()
                            layer = ast.literal_eval(map_data)
                            d['layer'] = layer
                        data.append(d)
                except Exception as e:
                    print(e)
        ext.project_all_data[project] = data


def load_user_data():
    for user in ext.users:
        project_all_data = {}
        for project in user.get('projects', []):
            file_path = '{}/{}/{}/{}'.format(
                load_config().PROJECT_FILE, project, user.get('id'), 'json')
            map_file_path = '{}/{}/{}/{}'.format(
                load_config().PROJECT_FILE, project, user.get('id'),'map_json')

            data = []
            for _, _, file in os.walk('{}'.format(file_path)):
                for f in file:
                    try:
                        with open('{}/{}'.format(file_path, f)) as f_json:

                            d = json.loads(f_json.read())
                            with open('{}/{}'.format(map_file_path, f)) as map_json:
                                # print(map_json.read())
                                map_data = map_json.read()
                                layer = ast.literal_eval(map_data)
                                d['layer'] = layer
                            data.append(d)
                    except Exception as e:
                        print(e)
            project_all_data[project] = data
        ext.user_all_data[user.get('id')] = project_all_data


def init_dirs():
    file_path = load_config().FILE

    try:
        if not os.path.exists(file_path + '/file/images/'):
            os.mkdir(file_path + '/file/images/')

        if not os.path.exists(file_path + '/file/mini_images/'):
            os.mkdir(file_path + '/file/mini_images/')

        if not os.path.exists(file_path + '/file/json/'):
            os.mkdir(file_path + '/file/json/')

        if not os.path.exists(file_path + '/file/map_json/'):
            os.mkdir(file_path + '/file/map_json/')

        if not os.path.exists(file_path + '/file/psd/'):
            os.mkdir(file_path + '/file/psd/')

        if not os.path.exists(file_path + '/file/psd_images/'):
            os.mkdir(file_path + '/file/psd_images/')

        if not os.path.exists(file_path + '/file/layers/'):
            os.mkdir(file_path + '/file/layers/')

        if not os.path.exists(file_path + '/file/layers/temp/'):
            os.mkdir(file_path + '/file/layers/temp/')

    except Exception as e:
        print(e)
