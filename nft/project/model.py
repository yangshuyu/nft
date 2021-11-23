import copy
import json
import os

from config import load_config
from libs.auth import OAuth
from libs.error import dynamic_error
from nft import ext
from nft.app import load_project_data, load_user_data, init_project_config, init_dirs


class Project:
    @classmethod
    def get_projects_by_query(cls, **kwargs):
        user_id = kwargs.get("user_id")
        file_path = load_config().FILE + '/file/projects'
        for a, b, file in os.walk('{}'.format(file_path)):
            ext.projects = b
            break

        projects, user = [], {}
        for u in ext.users:
            if u.get('id') == user_id:
                user = u
        if user.get('role', 0) == 1:
            projects = ext.projects
        else:
            projects = [p for p in ext.projects if p in user.get('projects', [])]

        return projects

    @classmethod
    def add(cls, **kwargs):
        name = kwargs.get('name')
        width = kwargs.get('width')
        high = kwargs.get('high')

        layer_path = '{}/{}'.format(
            load_config().PROJECT_FILE, name
        )

        if os.path.exists('{}'.format(layer_path)):
            dynamic_error({}, code=422, message='已存在该项目目录')

        else:
            os.mkdir('{}'.format(layer_path))

        ext.project_config[name] = {"width": width, "high": high}

        file_path = load_config().PROJECT_FILE + '/../project_config.json'
        with open(file_path, 'w') as content:
            content.write(json.dumps(ext.project_config))
        init_dirs()
        load_project_data()
        load_user_data()
        init_project_config()

        return ext.project_config

    @classmethod
    def update(cls, **kwargs):
        name = kwargs.get('name')
        width = kwargs.get('width')
        high = kwargs.get('high')

        for key, value in ext.project_config.items():
            if name == key:
                ext.project_config[key] = {'width': width, 'high': high}
        file_path = load_config().PROJECT_FILE + '/../project_config.json'
        with open(file_path, 'w') as content:
            content.write(json.dumps(ext.project_config))

        init_dirs()
        load_project_data()
        load_user_data()
        init_project_config()

        return ext.project_config

    @classmethod
    def get_projects(cls):
        result = []
        for key, value in ext.project_config.items():
            r = copy.deepcopy(value)
            r['name'] = key
            result.append(r)

        return result
