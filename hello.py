from wsgiref.validate import validator
from flask import Flask, appcontext_popped, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config["SECRET_KEY"] = "hardtoguesstring"
# validator datarequired() ensures the field is not empty
class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    email = StringField("Add your email: ", validators=[Email()])
    submit = SubmitField('Submit')


@app.route('/', methods=["GET","POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Reminder: you are changing your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template("index.html",
                            form=form,
                            name=session.get('name'), 
                            current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    return render_template("user.html",name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500