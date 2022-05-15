Notes
======
- To run, start virtual env, then ```$env:FLASK_APP = "hello"``` and ```flask run```
- add also ```$env:FLASK_ENV="development"```
- This branch has a web form created using flask-wtf package
- flask-wtf requires the app to have a secret key configured, to prevent against CSRF attacks
- Each web form is a class, inherits from the class ```FlaskForm```
- Each element in the web form is a field of the web form class, where the field
  equals an object inherited from ```wtforms```
- Use ```validators``` to validate the inputs. See hello.py for more examples