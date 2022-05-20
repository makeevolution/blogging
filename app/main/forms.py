from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

# validator datarequired() ensures the field is not empty
class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    email = StringField("Add your email: ", validators=[Email()])
    submit = SubmitField('Submit')
