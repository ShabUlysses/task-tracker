from datetime import datetime
from main import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    projects = db.relationship('Project', backref='manager', lazy=True)
    tasks = db.relationship('Task', backref='executor', lazy=True)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

class Project(db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    users = db.Column(db.String(250), nullable=False)
    task = db.relationship('Task', cascade='all, delete-orphan')
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_end = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Project name:('{self.name}', manager:'{self.manager}')"

    @property
    def serialize(self):
        return {
            'name': self.name
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    content = db.Column(db.String(500))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_due = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Task name:('{self.name}', executor:'{self.manager}')"

    @property
    def serialize(self):
        return {
            'name': self.name,
            'content': self.content
        }


