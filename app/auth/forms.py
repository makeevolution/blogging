from ast import Pass
from flask import redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Regexp, DataRequired, Length, Email, EqualTo
from .. import db
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),
                                            Length(1,64),
                                            Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(1,64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                   'Usernames must start with a letter, and can only\
                                                    have letters, numbers, dots or underscores.')])
    email = StringField('Email', validators=[DataRequired(),
                                            Length(1,64),
                                            Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeatPassword = PasswordField('Repeat Password', validators=[EqualTo('password', "Passwords must match!")
                                                                  , DataRequired()])
    submit = SubmitField('Register')

    # Custom validation is done by making a function that starts with validate_
    # and ends with the field name (e.g. email and username here)
    # Use ValidationError to help with redirection to register page and creating
    # the flash message, instead of making our own!
    def validate_email(self, field):
        if db.session.query(User).filter_by(email= field.data).first() is not None:
            raise ValidationError(f"Email {field.data} is already registered!")
    
    def validate_username(self, field):
        if db.session.query(User).filter_by(username= field.data).first() is not None:
            raise ValidationError(f"Username {field.data} is already in use!")