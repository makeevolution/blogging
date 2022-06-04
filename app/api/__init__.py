from flask import Blueprint

api = Blueprint('api', __name__)

# Do the imports here because the modules to be imported need the api Blueprint above
from . import authentication, posts, users, comments, errors