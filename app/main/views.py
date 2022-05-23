from datetime import datetime
from flask import flash, render_template, session, redirect, url_for, abort
from flask_login import current_user, login_required
# the below imports the blueprint called "main" from __init__.py
from . import main
from .forms import EditProfileForm, NameForm
from .. import db
from ..models import Permission, User
from ..decorators import admin_required, permission_required

@main.route('/')
def index():
    return render_template("index.html", current_time = datetime.utcnow())

@main.route('/user/<username>')
def user(username):
    user = db.session.query(User).filter_by(username = username).first()
    if user is None:
        flash(f"User {username} not found")
        abort(404)
    return render_template("user.html", user = user)

@main.route("/edit_profile", methods=["GET","POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
       current_user.username = form.username.data
       current_user.name = form.name.data
       current_user.email = form.email.data
       current_user.location = form.location.data
       current_user.about_me = form.about_me.data
       db.session.add(current_user)
       db.session.commit()
       flash("Your profile has been successfully updated!")
       return redirect(url_for("main.user", username=current_user.username))
    form.username.data = current_user.username
    form.name.data = current_user.name
    form.email.data = current_user.email
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)

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