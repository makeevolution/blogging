from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

# create_app is an application factory, creating an instance of the app based on an input configuration
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize the app with configurations for each of the libraries
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    # Define the routes for the app using blueprint library of flask
    
    # Importing the blueprint main is put here, so that clients that only import create_app will also create the blueprint.
    # If we put it at the top, the blueprint may never be created since they are not importing this whole module.
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
