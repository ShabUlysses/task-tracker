from main.forms import RegistrationForm, LoginForm, ProjectForm, TaskForm
from main.models import User, Project, Task
from flask import render_template, flash, redirect, url_for, request
from main import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
def hello():
    return redirect(url_for('index'))


@app.route('/home')
def home():
    return render_template('publicindex.html')


@app.route('/index')
@login_required
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects, current_user=current_user)


@app.route('/users')
@login_required
def users():
    projects = Project.query.all()
    all_users = User.query.all()
    return render_template('users.html', projects=projects,
                           users=all_users, current_user=current_user)


@app.route('/createusers', methods=['GET', 'POST'])
@login_required
def create_users():
    form = RegistrationForm()
    if not current_user.is_admin:
        flash('You are not allowed to view this page', 'danger')
        return redirect(url_for('index'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data.lower(), password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('User has been successfully created.', 'success')
        return redirect(url_for('create_users'))
    return render_template('createusers.html', form=form)


@app.route("/user/<string:user_name>")
@login_required
def userpage(user_name):
    user = User.query.filter_by(name=user_name).first()
    projects = Project.query.all()
    tasks = Task.query.all()

    return render_template('userpage.html', projects=projects, user=user,
                           username=user_name, tasks=tasks,
                           Project=Project, current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data.lower(), password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html')


@app.route('/project/<string:project_name>')
@login_required
def project(project_name):
    projects = Project.query.all()
    project = Project.query.filter_by(name=project_name).first()
    tasks = Task.query.filter_by(project_id=project.id)
    return render_template('project.html', projects=projects,
                           u_project_name=project.name, users=project.users,
                           manager=project.manager, content=project.content, start_date=project.date_created,
                           end_date=project.date_end, tasks=tasks, complete=project.completion,
                           current_user=current_user)


@app.route("/project/new", methods=['POST', 'GET'])
@login_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        user_list = ', '.join(form.users.data)
        project = Project(name=form.project_name.data, content=form.content.data,
                          manager=current_user, users=user_list, date_end=form.date_due.data)
        db.session.add(project)
        db.session.commit()
        flash('Project has been successfully created!', 'success')
        return redirect(url_for('project', project_name=form.project_name.data))
    return render_template('newproject.html', form=form, current_user=current_user)


@app.route("/project/<string:project_name>/completion", methods=['POST', 'GET'])
@login_required
def complete_project(project_name):
    project = Project.query.filter_by(name=project_name).first()
    tasks = Task.query.filter_by(project_id=project.id)
    if not all([task.completion for task in tasks]):
        flash('You cannot complete this project untill you complete all the tasks.', 'danger')
        return redirect(url_for('project', project_name=project_name))
    if current_user != project.manager and not current_user.is_admin:
        flash('You are not eligible to close this project.', 'danger')
        return redirect(url_for('project', project_name=project_name))
    project.completion = True
    db.session.commit()
    flash('The project has been marked as completed', 'success')
    return redirect(url_for('project', project_name=project_name))


@app.route("/project/<string:project_name>/edit", methods=['POST', 'GET'])
@login_required
def edit_project(project_name):
    project = Project.query.filter_by(name=project_name).first()
    form = ProjectForm()
    if current_user != project.manager and not current_user.is_admin:
        flash('You are not authorized to edit this project', 'danger')
        return redirect(url_for('project', project_name=project_name))
    if form.validate_on_submit():
        project.name = form.project_name.data
        project.content = form.content.data
        project.users = ', '.join(form.users.data)
        project.date_end = form.date_due.data
        db.session.commit()
        flash('Your project has been edited!', 'success')
        return redirect(url_for('project', project_name=project.name))
    elif request.method == 'GET':
        form.project_name.data = project.name
        form.content.data = project.content
        form.users.data = project.users
        form.date_due.data = project.date_end
    return render_template('editproject.html', project_name=project_name,
                           form=form, current_user=current_user)


@app.route("/project/<string:project_name>/delete", methods=['POST', 'GET'])
@login_required
def delete_project(project_name):
    project = Project.query.filter_by(name=project_name).first()
    if current_user != project.manager and not current_user.is_admin:
        flash('You are not authorized to delete this project', 'danger')
        return redirect(url_for('project', project_name=project_name))
    if request.method == 'POST':
        db.session.delete(project)
        db.session.commit()
        flash('Your project has been deleted!', 'success')
        return redirect(url_for('index'))
    return render_template('deleteproject.html', project_name=project_name, current_user=current_user)


@app.route(("/project/<string:project_name>/task/<string:task_name>"))
@login_required
def task(project_name, task_name):
    projects = Project.query.all()
    task = Task.query.filter_by(name=task_name).first()
    return render_template('task.html', projects=projects, task=task, project_name=project_name,
                           task_name=task.name, task_description=task.content, executor=task.executor,
                           end_date=task.date_end, start_date=task.date_created, complete=task.completion,
                           current_user=current_user)


@app.route("/project/<string:project_name>/task/new", methods=['POST', 'GET'])
@login_required
def new_task(project_name):
    project = Project.query.filter_by(name=project_name).first()
    project_users = project.users.split(',')
    form = TaskForm()
    if current_user != project.manager and not current_user.is_admin:
        flash('You cannot add tasks to this project.', 'danger')
        return redirect(url_for('project', project_name=project_name))
    if form.validate_on_submit():
        task = Task(name=form.task_name.data, content=form.task_description.data, project_id=project.id,
                    executor=request.form['executor'], date_end=form.date_due.data)
        db.session.add(task)
        db.session.commit()
        flash('Task has been successfully created!', 'success')
        return redirect(url_for('project', project_name=project.name, task_name=task.name))
    return render_template('newtask.html', form=form, users=project_users,
                           project_name=project.name, current_user=current_user)


@app.route("/project/<string:project_name>/task/<string:task_name>/complete", methods=['POST', 'GET'])
@login_required
def complete_task(project_name, task_name):
    project = Project.query.filter_by(name=project_name).first()
    task = Task.query.filter_by(name=task_name).first()
    if current_user != project.manager and current_user.name != task.executor and not current_user.is_admin:
        flash('You are not eligible to close this task.', 'danger')
        return redirect(url_for('task', project_name=project_name, task_name=task_name))
    task.completion = True
    db.session.commit()
    flash('The task has been marked as completed', 'success')
    return redirect(url_for('project', project_name=project_name))


@app.route("/project/<string:project_name>/task/<string:task_name>/edit", methods=['POST', 'GET'])
@login_required
def edit_task(project_name, task_name):
    task = Task.query.filter_by(name=task_name).first()
    project = Project.query.filter_by(name=project_name).first()
    project_users = project.users.split(',')
    form = TaskForm()
    if current_user != project.manager and current_user.name != task.executor and not current_user.is_admin:
        flash('You are not authorized to edit this task', 'danger')
        return redirect(url_for('task', project_name=project_name, task_name=task.name))
    if form.validate_on_submit():
        task.name = form.task_name.data
        task.content = form.task_description.data
        task.date_end = form.date_due.data
        db.session.commit()
        flash('Your task has been edited!', 'success')
        return redirect(url_for('task', project_name=project_name, task_name=task.name))
    elif request.method == 'GET':
        form.task_name.data = task.name
        form.task_description.data = task.content
        form.date_due.data = task.date_end
    return render_template('edittask.html', project_name=project_name, task_name=task.name,
                           form=form, users=project_users, current_user=current_user)


@app.route("/project/<string:project_name>/<string:task_name>/delete", methods=['POST', 'GET'])
@login_required
def delete_task(project_name, task_name):
    task = Task.query.filter_by(name=task_name).first()
    project = Project.query.filter_by(id=task.project_id).first()
    if current_user != project.manager and current_user.name != task.executor and not current_user.is_admin:
        flash('You are not authorized to delete this task', 'danger')
        return redirect(url_for('task', project_name=project_name, task_name=task_name))
    if request.method == 'POST':
        db.session.delete(task)
        db.session.commit()
        flash('Your task has been deleted!', 'success')
        return redirect(url_for('project', project_name=project_name))
    return render_template('deletetask.html', project_name=project_name, task_name=task_name,
                           current_user=current_user)


@app.route("/redirect/<string:task_name>/")
@login_required
def task_redirect(task_name):
    project = Project.query.get(int(Task.query.filter_by(name=task_name).first().project_id))
    return redirect(url_for('task', project_name=project.name, task_name=task_name))
