from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField 
from wtforms.validators import DataRequired, Email, Length

# validator datarequired() ensures the field is not empty
# Not used anymore from this commit forward
class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    email = StringField("Add your email: ", validators=[Email()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    username = StringField("Edit your username")
    email = StringField("Edit your email", validators=[Email()])
    name = StringField("Real Name", validators=[Length(0,64)])
    location = StringField("Edit your location", validators=[Length(0,64)])
    about_me = StringField("About me")
    submit = SubmitField('Submit') 