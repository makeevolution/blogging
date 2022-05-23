# This main folder contains all the routes required by the app instance created by the application factory
# Each type of route is defined in its own .py file

from flask import Blueprint

from app.models import Permission
# The blueprint function below takes in the name of the blueprint, and the module where the blueprint is located (i.e. __name__, which means in this folder)
main = Blueprint('main', __name__)
from . import views, errors

# The context processor below is added so that every render_template() call will make Permission available for jinja2.
# Thus you don't have to do render_template(yourOtherArguments, Permission=Permission) everytime you want to render a page that
# requires Permission
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)