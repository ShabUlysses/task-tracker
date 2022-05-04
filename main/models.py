from datetime import datetime
from main import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ ='user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(250), nullable=False)
    projects = db.relationship('Project', backref='manager', lazy=True)
    tasks = db.relationship('Task', backref='manager', lazy=True)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"


class Project(db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    content = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    users = db.Column(db.String(250), nullable=False)
    task = db.relationship('Task', cascade='all, delete-orphan')
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_end = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Project name:('{self.name}', manager: '{self.manager.name}', users: '{self.users}', date_end: '{self.date_end}')"

    @property
    def serialize(self):
        return {
            'name': self.name
        }


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    content = db.Column(db.String(500))
    executor = db.Column(db.String(250))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_end = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion = db.Column(db.Boolean, default=False)


    def __repr__(self):
        return f"Task name:('{self.name}', executor:'{self.executor}', project_id: '{self.project_id}')"

    @property
    def serialize(self):
        return {
            'name': self.name,
            'content': self.content
        }

