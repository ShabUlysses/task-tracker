from flask import Flask

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

from main.core.routes import core
from main.users.routes import users
from main.projects.routes import projects
from main.tasks.routes import tasks

app.register_blueprint(core)
app.register_blueprint(users)
app.register_blueprint(projects)
app.register_blueprint(tasks)

