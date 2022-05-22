from flask_login import login_required, login_user, logout_user
from . import auth
from flask import redirect, flash, render_template, url_for, request
from .forms import LoginForm
from .. import db
from ..models import User

@auth.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Get the user object of the user trying to log in 
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None:
            # also create a flash message saying user or password is incorrect!
            flash("Username or password incorrect")
            return redirect(url_for('auth.login'))
        # Check if password input is correct
        if not User.verify_password(user, form.password.data):
            # also flash user or password incorrect
            flash("Username or password incorrect")
            return redirect(url_for('auth.login'))
        # Log in the user using login_user function of flask login package
        # The user's is_authenticated attribute will be set to True
        # The form.remember_me.data, if is True, will set a long-term cookie
        # in the user's browser, so the user don't have to login again
        # when they close the browser and re-open it.
        # Duration of cookie is set in REMEMBER_COOKIE_DURATION configuration option
        login_user(user, form.remember_me.data)

        # If the user got to the log in form because they were accessing a protected route,
        # the protected route is saved by the flask login package in request.args dictionary with
        # key "next". Re-route the user there, or re-route to index page as default. 
        # The next.startswith is there to prevent hackers from rerouting us to another website; it
        # ensures the value is always a relative path to our site. 
        protectedPage = request.args.get('next')
        if protectedPage is None or not next.startswith('/'):
            protectedPage = url_for("main.index")

        return redirect(url_for(protectedPage))

    return render_template('auth/login.html', form = form)

@auth.route('/logout')   
@login_required
def logout():
    # Logout the user using flask login package's logout_user function
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('main.index'))