from random import choice
from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from main import db
from main.models import User, Project, Task
from main.projects.forms import ProjectForm

projects = Blueprint('projects', __name__)


@projects.route("/closedprojects")
@login_required
def closed_projects():
    page = request.args.get('page', default=1, type=int)
    closed_projects = Project.query.filter_by(completion=True)
    projects = closed_projects.paginate(page=page, per_page=5)
    return render_template('closedprojects.html', projects=projects, current_user=current_user)


@projects.route('/project/<string:project_name>')
@login_required
def project(project_name):
    page = request.args.get('page', default=1, type=int)
    open_projects = Project.query.filter_by(completion=False)
    projects = open_projects.paginate(page=page, per_page=5)

    project = Project.query.filter_by(name=project_name).first()
    tasks = Task.query.filter_by(project_id=project.id)
    return render_template('project.html', projects=projects,
                           u_project_name=project.name, users=project.users,
                           manager=project.manager, content=project.content, start_date=project.date_created,
                           end_date=project.date_end, tasks=tasks, complete=project.completion,
                           current_user=current_user)


@projects.route("/project/new", methods=['POST', 'GET'])
@login_required
def new_project():
    form = ProjectForm()
    users = User.query.all()
    if form.validate_on_submit():
        user_list = ', '.join(form.users.data)
        project = Project(name=form.project_name.data, content=form.content.data,
                          manager=current_user, users=user_list, date_end=form.date_due.data)
        db.session.add(project)
        db.session.commit()
        flash('Project has been successfully created!', 'success')
        return redirect(url_for('projects.project', project_name=form.project_name.data))
    return render_template('newproject.html', form=form, current_user=current_user, users=users)


@projects.route("/project/<string:project_name>/completion", methods=['POST', 'GET'])
@login_required
def complete_project(project_name):
    project = Project.query.filter_by(name=project_name).first()
    tasks = Task.query.filter_by(project_id=project.id)
    if not all([task.completion for task in tasks]):
        flash('You cannot complete this project untill you complete all the tasks.', 'danger')
        return redirect(url_for('projects.project', project_name=project_name))
    if current_user != project.manager and not current_user.is_admin:
        flash('You are not eligible to close this project.', 'danger')
        return redirect(url_for('projects.project', project_name=project_name))
    project.completion = True
    db.session.commit()
    flash('The project has been marked as completed', 'success')
    return redirect(url_for('projects.project', project_name=project_name))


@projects.route("/project/<string:project_name>/edit", methods=['POST', 'GET'])
@login_required
def edit_project(project_name):
    project = Project.query.filter_by(name=project_name).first()
    users = User.query.all()
    form = ProjectForm()
    if current_user != project.manager and not current_user.is_admin:
        flash('You are not authorized to edit this project', 'danger')
        return redirect(url_for('projects.project', project_name=project_name))
    if form.validate_on_submit():
        project.name = form.project_name.data
        project.content = form.content.data
        project.users = ', '.join(form.users.data)
        project.date_end = form.date_due.data
        db.session.commit()
        flash('Your project has been edited!', 'success')
        return redirect(url_for('projects.project', project_name=project.name))
    elif request.method == 'GET':
        form.project_name.data = project.name
        form.content.data = project.content
        form.users.data = project.users
        form.date_due.data = project.date_end
    return render_template('editproject.html', project_name=project_name,
                           form=form, current_user=current_user, users=users)


@projects.route("/project/<string:project_name>/delete", methods=['POST', 'GET'])
@login_required
def delete_project(project_name):
    project = Project.query.filter_by(name=project_name).first()
    if current_user != project.manager and not current_user.is_admin:
        flash('You are not authorized to delete this project', 'danger')
        return redirect(url_for('projects.project', project_name=project_name))
    if request.method == 'POST':
        db.session.delete(project)
        db.session.commit()
        flash('Your project has been deleted!', 'success')
        return redirect(url_for('core.index'))
    return render_template('deleteproject.html', project_name=project_name, current_user=current_user)
