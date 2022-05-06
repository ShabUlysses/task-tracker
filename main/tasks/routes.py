from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from main import db
from main.models import Project, Task
from main.tasks.forms import TaskForm

tasks = Blueprint('tasks', __name__)


@tasks.route("/project/<string:project_name>/task/<string:task_name>")
@login_required
def task(project_name, task_name):
    projects = Project.query.all()
    task = Task.query.filter_by(name=task_name).first()
    return render_template('task.html', projects=projects, task=task, project_name=project_name,
                           task_name=task.name, task_description=task.content, executor=task.executor,
                           end_date=task.date_end, start_date=task.date_created, complete=task.completion,
                           current_user=current_user)


@tasks.route("/project/<string:project_name>/task/new", methods=['POST', 'GET'])
@login_required
def new_task(project_name):
    project = Project.query.filter_by(name=project_name).first()
    project_users = project.users.split(',')
    form = TaskForm()
    if current_user != project.manager and not current_user.is_admin:
        flash('You cannot add tasks to this project.', 'danger')
        return redirect(url_for('projects.project', project_name=project_name))
    if form.validate_on_submit():
        task = Task(name=form.task_name.data, content=form.task_description.data, project_id=project.id,
                    executor=request.form['executor'], date_end=form.date_due.data)
        db.session.add(task)
        db.session.commit()
        flash('Task has been successfully created!', 'success')
        return redirect(url_for('projects.project', project_name=project.name, task_name=task.name))
    return render_template('newtask.html', form=form, users=project_users,
                           project_name=project.name, current_user=current_user)


@tasks.route("/project/<string:project_name>/task/<string:task_name>/complete", methods=['POST', 'GET'])
@login_required
def complete_task(project_name, task_name):
    project = Project.query.filter_by(name=project_name).first()
    task = Task.query.filter_by(name=task_name).first()
    if current_user != project.manager and current_user.name != task.executor and not current_user.is_admin:
        flash('You are not eligible to close this task.', 'danger')
        return redirect(url_for('tasks.task', project_name=project_name, task_name=task_name))
    task.completion = True
    db.session.commit()
    flash('The task has been marked as completed', 'success')
    return redirect(url_for('projects.project', project_name=project_name))


@tasks.route("/project/<string:project_name>/task/<string:task_name>/edit", methods=['POST', 'GET'])
@login_required
def edit_task(project_name, task_name):
    task = Task.query.filter_by(name=task_name).first()
    project = Project.query.filter_by(name=project_name).first()
    project_users = project.users.split(',')
    form = TaskForm()
    if current_user != project.manager and current_user.name != task.executor and not current_user.is_admin:
        flash('You are not authorized to edit this task', 'danger')
        return redirect(url_for('tasks.task', project_name=project_name, task_name=task.name))
    if form.validate_on_submit():
        task.name = form.task_name.data
        task.content = form.task_description.data
        task.executor = request.form['executor']
        task.date_end = form.date_due.data
        db.session.commit()
        flash('Your task has been edited!', 'success')
        return redirect(url_for('tasks.task', project_name=project_name, task_name=task.name))
    elif request.method == 'GET':
        form.task_name.data = task.name
        form.task_description.data = task.content
        form.date_due.data = task.date_end
    return render_template('edittask.html', project_name=project_name, task_name=task.name,
                           form=form, users=project_users, current_user=current_user)


@tasks.route("/project/<string:project_name>/<string:task_name>/delete", methods=['POST', 'GET'])
@login_required
def delete_task(project_name, task_name):
    task = Task.query.filter_by(name=task_name).first()
    project = Project.query.filter_by(id=task.project_id).first()
    if current_user != project.manager and current_user.name != task.executor and not current_user.is_admin:
        flash('You are not authorized to delete this task', 'danger')
        return redirect(url_for('tasks.task', project_name=project_name, task_name=task_name))
    if request.method == 'POST':
        db.session.delete(task)
        db.session.commit()
        flash('Your task has been deleted!', 'success')
        return redirect(url_for('projects.project', project_name=project_name))
    return render_template('deletetask.html', project_name=project_name, task_name=task_name,
                           current_user=current_user)


@tasks.route("/redirect/<string:task_name>/")
@login_required
def task_redirect(task_name):
    project = Project.query.get(int(Task.query.filter_by(name=task_name).first().project_id))
    return redirect(url_for('tasks.task', project_name=project.name, task_name=task_name))