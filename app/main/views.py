from datetime import datetime
from flask import current_app, flash, render_template, request, session, redirect, url_for, abort
from flask_login import current_user, login_required
# the below imports the blueprint called "main" from __init__.py
from . import main
from .forms import EditProfileAdminForm, EditProfileForm, PostForm
from .. import db
from ..models import Permission, Role, User, Post
from ..decorators import admin_required, permission_required

@main.route('/', methods=["GET","POST"])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body = form.text.data, author = current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("main.index"))
    page = request.args.get('page', 1, type=int)
    # type=int is so that if 'page' is not an integer, the default value 1 is returned
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
        error_out = False
    )
    # all() is now replaced with paginate() method.
    # error_out sets what happens if page that is out of range is returned. If True, we go to 404 page,
    # if false, it will return an empty list.
    # desc() orders the column entry in descending order
    posts = pagination.items
    return render_template("index.html",
                            current_time = datetime.utcnow(),
                            form = form,
                            posts = posts,
                            pagination = pagination)

@main.route('/user/<username>')
def user(username):
    user = db.session.query(User).filter_by(username = username).first()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    if user is None:
        flash(f"User {username} not found")
        abort(404)
    return render_template("user.html", user = user, posts = posts)

@main.route("/edit_profile", methods=["GET","POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
       current_user.name = form.name.data
       current_user.location = form.location.data
       current_user.about_me = form.about_me.data
       db.session.add(current_user)
       db.session.commit()
       flash("Your profile has been successfully updated!")
       return redirect(url_for("main.user", username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)

@main.route("/edit_profile/<int:id>", methods=["GET","POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = db.session.query(User).get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
       user.name = form.name.data
       user.location = form.location.data
       user.about_me = form.about_me.data
       user.username = form.username.data
       user.email = form.email.data
       user.confirmed = form.confirmed.data
       user.role = db.session.query(Role).get(form.role.data)
       db.session.add(user)
       db.session.commit()
       flash(f"Profile has been successfully updated!")
       return redirect(url_for("main.user", username=user.username))
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.username.data = user.username
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    # to set the initial value of the role choice, pass in the id of the role in the db,
    # since in the SelectField, the role is identified by its id
    form.role.data = user.role_id
    return render_template("edit_profile.html", form=form, user=user)

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