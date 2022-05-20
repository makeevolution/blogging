from datetime import datetime
from flask import render_template, session, redirect, url_for
# the below imports the blueprint called "main" from __init__.py
from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/', methods=["GET","POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('main.index')) #The path to an endpoint (e.g. index()) now has to be specified with the name of the blueprint (i.e. main)
                                               #The blueprint function makes all route functions fall under a namespace "main" 
    return render_template("index.html",
                            form=form,
                            name=session.get('name'), 
                            current_time=datetime.utcnow(),
                            known=session.get('known', False))

@main.route('/user/<name>')
def user(name):
    return render_template("user.html",name=name)