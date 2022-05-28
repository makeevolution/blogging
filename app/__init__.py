from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from config import config, Config
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
metadata = MetaData(naming_convention=Config.NAMING_CONVENTION)
db = SQLAlchemy(metadata=metadata)
pagedown = PageDown()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Set path to login page
                                        # Will automatically redirect user to this page
                                        # if user attempts to access protected page

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
    login_manager.init_app(app)
    pagedown.init_app(app)
    # Define the routes for the app using blueprint library of flask
    
    # Importing the blueprint main is put here, so that clients that only import create_app will also create the blueprint.
    # If we put it at the top, the blueprint may never be created since they are not importing this whole module.
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix = '/auth')
    # /auth above is so that the routes inside auth blueprint will
    # start with /auth e.g. localhost:5000/auth/login

    return app
