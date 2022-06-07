from flask import jsonify, render_template, request
from . import api
from app.exceptions import ValidationError
from app.main import main

# View functions in the API can invoke the functions in this file to generate error responses
# The ones decorated with app_errorhandler will be executed when the error in the argument
# is thrown by any code in the corresponding blueprint (e.g. main, api, etc.)

# Since Flask returns a HTML by default for a 404 or 500 errors, we return a JSON instead
# if the client does not support HTML responses

def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        resp = jsonify({'error': 'not found'})
        resp.status_code = 404
        return resp
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        resp = jsonify({'error': 'Internal Server Error'})
        resp.status_code = 500
        return resp
    return render_template('500.html'), 500

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
    
def forbidden(message):
    resp = jsonify({'error': 'forbidden', 'message': message})
    resp.status_code = 403
    return resp

def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response