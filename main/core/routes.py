from flask import Blueprint, request
from flask import render_template, redirect, url_for
from flask_login import current_user, login_required

from main.models import Project

core = Blueprint('core', __name__)

@core.route("/")
def hello():
    return redirect(url_for('core.index'))


@core.route('/home')
def home():
    return render_template('publicindex.html')


@core.route('/index')
@login_required
def index():
    page = request.args.get('page', default=1, type=int)
    open_projects = Project.query.filter_by(completion=False)
    projects = open_projects.paginate(page=page, per_page=5)
    return render_template('index.html', projects=projects, current_user=current_user)
