from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, InputRequired

from main.models import User


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