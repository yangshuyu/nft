from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy(session_options={"autoflush": False, "autocommit": False})
migrate = Migrate(compare_type=True)
project_all_data = {}
user_all_data = {}
required_quantity = -1
completed_quantity = 0
users = []
projects = []
