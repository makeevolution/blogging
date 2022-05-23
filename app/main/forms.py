from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
from ..models import Role, User
from .. import db

# validator datarequired() ensures the field is not empty
# Not used anymore from this commit forward
class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    email = StringField("Add your email: ", validators=[Email()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm): 
    name = StringField("Real Name", validators=[Length(0,64)])
    location = StringField("Edit your location", validators=[Length(0,64)])
    about_me = StringField("About me")
    submit = SubmitField('Submit') 

# Admin can edit more stuff, on top of those editable by the user
class EditProfileAdminForm(FlaskForm):
    name = StringField("Real Name", validators=[Length(0,64)])
    location = StringField("Edit your location", validators=[Length(0,64)])
    about_me = StringField("About me")
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(1,64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                   'Usernames must start with a letter, and can only\
                                                    have letters, numbers, dots or underscores.')])
    email = StringField('Email', validators=[DataRequired(),
                                            Length(1,64),
                                            Email()])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Submit') 

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # role.choices here is for the SelectField above
        # SelectField has coerce argument set to int, so that role.id below is interpreted
        # as int (which it is) instead of the default (string)
        self.role.choices = [(role.id, role.name) for role in db.session.query(Role).order_by(Role.name).all()]
        self.user = user

    # Custom validation is done by making a function that starts with validate_
    # and ends with the field name (e.g. email and username here)
    # Use ValidationError to help with redirection to register page and creating
    # the flash message, instead of making our own!
    def validate_email(self, field):
        if self.user.email != field.data and db.session.query(User).filter_by(email= field.data).first() is not None:
            raise ValidationError(f"Email {field.data} is already registered!")
    
    def validate_username(self, field):
        if self.user.username != field.data and db.session.query(User).filter_by(username= field.data).first() is not None:
            raise ValidationError(f"Username {field.data} is already in use!")