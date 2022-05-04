from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from main.models import User, Project
from wtforms.fields import DateField

class RegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=250)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data.lower()).first()
        if email:
            raise ValidationError('That email is taken. Please choose different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class ProjectForm(FlaskForm):
    users_list = [user.name for user in User.query.all()]

    project_name = StringField('Project name',
                               validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    users = SelectMultipleField('Choose users that will participate in the project',
                                validators=[DataRequired()], choices=users_list)
    date_due = DateField('When is the end of the project?', format='%Y-%m-%d',
                         validators=[InputRequired(), DataRequired()])
    submit = SubmitField('Create project')


class TaskForm(FlaskForm):
    task_name = StringField('Task name',
                            validators=[DataRequired()])
    task_description = TextAreaField('Description of the task',
                                     validators=[DataRequired()])
    date_due = DateField('What is the deadline on this task?', format='%Y-%m-%d',
                         validators=[InputRequired(), DataRequired()])
    submit = SubmitField('Create task')