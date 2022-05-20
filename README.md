Notes
======
- To run, start virtual env, then ```$env:FLASK_APP = "flasky.py"``` and ```flask run```
- add also ```$env:FLASK_ENV="development"```
- This branch has a web form created using flask-wtf package
- flask-wtf requires the app to have a secret key configured, to prevent against CSRF attacks
- Each web form is a class, inherits from the class ```FlaskForm```
- Each element in the web form is a field of the web form class, where the field
  equals an object inherited from ```wtforms```
- Use ```validators``` to validate the inputs. See hello.py for more examples

- The last request to the index method can be a POST request
- This can be problematic, since if the user refreshes the page after the POST
  request is sent (i.e. pressing submit button), the page will ask for confirmation
  to re-sent the form, which causes duplicate form submission
- Duplicate form submission is not desired
- So it is good practice to do a <b>redirection</b>, by using the redirect function
  to make a get request instead.
- ```name``` is stored in ```session```, because as soon as the redirect is done 
  the form data is destroyed.

- Use flash() function to flash messages to the user on certain
  actions done. For example, if a connected client changes their
  name, we can flash a message telling them they changed their name. This is shown in hello.py.
- The base.html now also includes code to render the flash message.

- In this commit, ```hello.py``` is changed to ```flasky.py```, and the application is refactored and is much neater. Use gitk to see which files changed and comments on it

- In this commit, a database migration framework is applied (Alembic). 
- If we create a change to the models in models.py, using this we can update the database accordingly
- First, add migrate = Migrate(app,db) to flasky.py (shown there). Don't forget to set the ```FLASK_APP``` env variable to ```flasky.py```
- Since ```flasky.py``` uses a default configuration that works with the database ```data-dev.sqlite```, the migration will apply to that database
- To initialize the framework in the project, run ```flask db init``` (before doing any changes to models.py!)
- Then apply changes to the model. For example, in this commit the attribute ```test``` is added to User, which means a new column ```test``` is to be added in the database
- After adding this change, run ```flask db migrate``` to create a migration script
- The migrations folder now has a migration script with upgrade() and downgrade() functions, signifying the changes
- Add the migration script to git, then run ```flask db upgrade``` to upgrade the database