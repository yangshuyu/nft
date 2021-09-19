from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy(session_options={"autoflush": False, "autocommit": False})
migrate = Migrate(compare_type=True)
