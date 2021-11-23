from webargs.flaskparser import use_args

from libs.auth import jwt_required, requires
from libs.base.resource import BaseResource
from nft.account.model import User
from nft.account.schema import LoginSchema, UserPutSchema
from nft.project.model import Project
from nft.project.schema import ProjectPostSchema, ProjectPutSchema


class ProjectsResource(BaseResource):
    @jwt_required
    def get(self):
        user_id = self.current_user.get('id')
        data = Project.get_projects_by_query(user_id=user_id)
        return data

    @requires(1)
    @use_args(ProjectPostSchema)
    def post(self, args):
        project = Project.add(**args)
        return project

    @requires(1)
    @use_args(ProjectPutSchema)
    def put(self, args):
        project = Project.update(**args)
        return project


class AdminProjectsResource(BaseResource):
    @requires(1)
    @jwt_required
    def get(self):
        data = Project.get_projects()
        return data
