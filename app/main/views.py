from datetime import datetime
from flask import render_template, session, redirect, url_for
from flask_login import login_required
# the below imports the blueprint called "main" from __init__.py
from . import main
from .forms import NameForm
from .. import db
from ..models import Permission, User
from ..decorators import admin_required, permission_required

@main.route('/')
def index():
    return render_template("index.html", current_time = datetime.utcnow())

@main.route('/user/<name>')
def user(name):
    return render_template("user.html",name=name)

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For Administrators only!"
    
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "For comment Moderators!"