from main.forms import RegistrationForm, LoginForm, ProjectForm, TaskForm
from main.models import User, Project, Task
from flask import render_template, flash, redirect, url_for, request
from main import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
def hello():
    return redirect(url_for('index'))

@app.route('/home')
def home():
    return render_template('publicindex.html')

@app.route('/index')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects = projects)


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
    return render_template('register.html', title='Register', form=form)\


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
    users = project.users.split(',')
    return render_template('project.html', projects=projects,
                           u_project_name=project.name, users=users,
                           manager=project.manager, content=project.content, end_date=project.date_end)


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
    return render_template('newproject.html', form=form)


@app.route("/project/<string:project_name>/edit", methods=['POST', 'GET'])
@login_required
def edit_project(project_name):
    project = Project.query.filter_by(name=project_name).first()
    form = ProjectForm()
    if current_user != project.manager:
        flash('You are not authorized to edit this project', 'danger')
        return redirect(url_for('project', project_name=project_name))
    if form.validate_on_submit():
        project.name = form.project_name.data
        project.content = form.content.data
        project.users = ', '.join(form.users.data)
        project.date_end = form.date_due.data
        db.session.commit()
        flash('Your project has been edited!', 'success')
        return redirect(url_for('project', project_name=project_name))
    elif request.method == 'GET':
        form.project_name.data = project.name
        form.content.data = project.content
        form.users.data = project.users
        form.date_due.data = project.date_end
    return render_template('editproject.html', project_name=project_name, form=form)


@app.route("/project/<string:project_name>/delete", methods=['POST', 'GET'])
@login_required
def delete_project(project_name):
    project = Project.query.filter_by(name=project_name).first()
    if current_user != project.manager:
        flash('You are not authorized to delete this project', 'danger')
        return redirect(url_for('project', project_name=project_name))
    if request.method == 'POST':
        db.session.delete(project)
        db.session.commit()
        flash('Your project has been deleted!', 'success')
        return redirect(url_for('index'))
    return render_template('deleteproject.html', project_name=project_name)


@app.route(("/project/<string:project_name>/task/<string:task_name>"))
@login_required
def task(project_name, task_name):
    projects = Project.query.all()
    task = Task.query.filter_by(name=task_name).first()
    return render_template('task', projects=projects, task=task)


@app.route("/project/<string:project_name>/task/new", methods=['POST', 'GET'])
@login_required
def new_task(project_name):
    project = Project.query.filter_by(name=project_name).first()
    project_users = project.users.split(',')
    print(project_users)
    form = TaskForm()
    if current_user != project.manager:
        flash('You cannot add tasks to this project.')
        return redirect(url_for('project', project_name=project_name))
    if form.validate_on_submit():
        task = Task(name=form.task_name.data, content=form.task_description.data,
                    executor=request.form['executor'], date_end=form.date_due.data)
        db.session.commit()
        return redirect(url_for('task', project_name=project.name, task_name=form.task_name.data))
    return render_template('newtask.html', form=form, users=project_users)


