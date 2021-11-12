from webargs.flaskparser import use_args

from libs.auth import jwt_required
from libs.base.resource import BaseResource
from nft.account.model import User
from nft.account.schema import LoginSchema, UserPutSchema
from nft.project.model import Project


class ProjectsResource(BaseResource):
    @jwt_required
    def get(self):
        user_id = self.current_user.get('id')
        data = Project.get_projects_by_query(user_id=user_id)
        return data
