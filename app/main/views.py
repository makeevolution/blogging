from datetime import datetime
from flask import render_template, session, redirect, url_for
# the below imports the blueprint called "main" from __init__.py
from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/')
def index():
    return render_template("index.html", current_time = datetime.utcnow())

@main.route('/user/<name>')
def user(name):
    return render_template("user.html",name=name)