from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, InputRequired


class TaskForm(FlaskForm):
    task_name = StringField('Task name',
                            validators=[DataRequired()])
    task_description = TextAreaField('Description of the task',
                                     validators=[DataRequired()])
    date_due = DateField('What is the deadline on this task?', format='%Y-%m-%d',
                         validators=[InputRequired(), DataRequired()])
    submit = SubmitField('Create task')