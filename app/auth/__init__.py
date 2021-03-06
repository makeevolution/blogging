# This main folder contains user authentication routes required by the app instance created by the application factory
# Each type of route is defined in its own .py file

from flask import Blueprint
# The blueprint function below takes in the name of the blueprint, and the module where the blueprint is located (i.e. __name__, which means in this folder)
auth = Blueprint('auth', __name__)
from . import views

