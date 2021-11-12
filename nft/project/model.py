import json
import os

from config import load_config
from libs.auth import OAuth
from libs.error import dynamic_error
from nft import ext


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



