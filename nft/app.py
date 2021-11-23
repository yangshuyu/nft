import ast
import json
import os
import re

from flask import Flask
from flask_cors import CORS

from config import load_config
from nft.ext import db, migrate

from nft import ext


def create_app(app_name="api", blueprints=None):
    from nft import BLUEPRINTS

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
    init_dirs()

    load_project_data()
    load_user_data()
    init_project_config()


# def load_all_users():
#     file_path = load_config().FILE + '/file/users.json'
#     with open(file_path) as f:
#         ext.users = json.loads(f.read())


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
        projects = user.get('projects', []) if user.get('role') == 0 else ext.project_all_data
        for project in projects:
            file_path = '{}/{}/users/{}/{}'.format(
                load_config().PROJECT_FILE, project, user.get('id'), 'json')
            map_file_path = '{}/{}/users/{}/{}'.format(
                load_config().PROJECT_FILE, project, user.get('id'), 'map_json')

            if not os.path.exists(file_path.replace('/json', '')):
                os.mkdir(file_path.replace('/json', ''))
                os.mkdir(file_path)

            if not os.path.exists(file_path.replace('/map_json', '')):
                os.mkdir(file_path.replace('/map_json', ''))
                os.mkdir(map_file_path)

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
    file_path = load_config().PROJECT_FILE
    for _, b, file in os.walk('{}'.format(file_path)):
        ext.projects = b
        break

    if not os.path.exists(load_config().PROJECT_FILE + '/../users.json'):
        map_json = [
            {
                "id": 1,
                "username": "admin",
                "password": "123456",
                "role": 1,
                "projects": [
                ]
            }
        ]
        with open(load_config().PROJECT_FILE + '/../users.json', 'a') as content:
            content.write(json.dumps(map_json))

    file_path = load_config().PROJECT_FILE + '/../users.json'
    with open(file_path) as f:
        ext.users = json.loads(f.read())

    for project in ext.projects:
        file_path = '{}/{}/'.format(
            load_config().PROJECT_FILE, project)
        try:
            if not os.path.exists(file_path + 'images/'):
                os.mkdir(file_path + 'images/')

            if not os.path.exists(file_path + 'mini_images/'):
                os.mkdir(file_path + 'mini_images/')

            if not os.path.exists(file_path + 'json/'):
                os.mkdir(file_path + 'json/')

            if not os.path.exists(file_path + 'map_json/'):
                os.mkdir(file_path + 'map_json/')

            if not os.path.exists(file_path + 'psd/'):
                os.mkdir(file_path + 'psd/')

            if not os.path.exists(file_path + 'psd_images/'):
                os.mkdir(file_path + 'psd_images/')

            if not os.path.exists(file_path + 'layers/'):
                os.mkdir(file_path + 'layers/')

            if not os.path.exists(file_path + 'users/'):
                os.mkdir(file_path + 'users/')

            if not os.path.exists(file_path + 'layers/temp/'):
                os.mkdir(file_path + 'layers/temp/')

        except Exception as e:
            print(e)


def init_project_config():
    if not os.path.exists(load_config().PROJECT_FILE + '/../project_config.json'):
        map_json = {
            "monkey": {"width": 2000, "high": 2000},
        }

        with open(load_config().PROJECT_FILE + '/../project_config.json', 'a') as content:
            content.write(json.dumps(map_json))

    file_path = load_config().PROJECT_FILE + '/../project_config.json'
    with open(file_path) as f:
        ext.project_config = json.loads(f.read())
