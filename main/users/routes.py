import os
from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required

from main import db, bcrypt, app
from main.models import User, Project, Task
from main.users.forms import RegistrationForm, LoginForm, UpdateAccountForm
from main.users.utils import save_picture

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data.lower(), password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('core.index'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.home'))


@users.route("/account", methods=["GET", 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    return render_template('account.html', form=form, image_file=image_file)


@users.route('/accounts')
@login_required
def accounts():
    projects = Project.query.all()
    page = request.args.get('page', default=1, type=int)
    all_users = User.query.paginate(page=page, per_page=5)
    return render_template('accounts.html', projects=projects,
                           users=all_users, current_user=current_user)


@users.route('/createusers', methods=['GET', 'POST'])
@login_required
def create_users():
    form = RegistrationForm()
    if not current_user.is_admin:
        flash('You are not allowed to view this page', 'danger')
        return redirect(url_for('core.index'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data.lower(), password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('User has been successfully created.', 'success')
        return redirect(url_for('users.create_users'))
    return render_template('createusers.html', form=form)


@users.route("/user/<string:user_name>")
@login_required
def userpage(user_name):
    user = User.query.filter_by(name=user_name).first()
    projects = Project.query.all()
    tasks = Task.query.all()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('userpage.html', projects=projects, user=user,
                           username=user_name, tasks=tasks, image_file=image_file,
                           Project=Project, current_user=current_user)
