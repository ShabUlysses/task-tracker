from flask import Flask

from config import SECRET_KEY
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pmapp.db'
db = SQLAlchemy(app)

from main import routes
