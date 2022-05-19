from pickle import FALSE
from wsgiref.validate import validator
from flask import Flask, appcontext_popped, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config["SECRET_KEY"] = "hardtoguesstring"
app.config["SQLALCHEMY_DATABASE_URI"]=\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)
# the above is so that whenever we do an instance of flask shell,
# the User, Role and db will be imported automatically to the shell

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # db.ForeignKey('roles.id') means the role_id gets its value from
    # id column of roles table

    def __repr__(self):
        return '<User %r>' % self.username

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy="dynamic")
    # Each element in users column is a User object.
    # backref='role' adds a new attribute in the User model
    # so an instance of User can access/set its associated role
    # using this attribute instead of using role_id.
    # e.g. user_role = Role(name="User")
    #      user_susan = User(username="Susan",role=user_role)
    # Page 66 on how to understand this better.

    # lazy is used so that accessing the attribute does not automatically
    # return the attribute, so we can apply filtering to it 
    # e.g. user_role.users.order_by(User.username).all() can also be done
    # like what we usually do for query to an class (e.g. Role.query.filter_by(role=user_role).all())

    def __repr__(self):
        return '<Role %r>' % self.name


# validator datarequired() ensures the field is not empty
class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    email = StringField("Add your email: ", validators=[Email()])
    submit = SubmitField('Submit')


@app.route('/', methods=["GET","POST"])
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
        return redirect(url_for('index'))
    return render_template("index.html",
                            form=form,
                            name=session.get('name'), 
                            current_time=datetime.utcnow(),
                            known=session.get('known', False))

@app.route('/user/<name>')
def user(name):
    return render_template("user.html",name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500