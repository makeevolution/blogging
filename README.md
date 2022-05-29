Notes
======
- To run, start virtual env, then ```$env:FLASK_APP = "flasky.py"``` and ```flask run```
- add also ```$env:FLASK_ENV="development"```
- This branch has a web form created using flask-wtf package
- flask-wtf requires the app to have a secret key configured, to prevent against CSRF attacks
- Each web form is a class, inherits from the class ```FlaskForm```
- Each element in the web form is a field of the web form class, where the field
  equals an object inherited from ```wtforms```
- Use ```validators``` to validate the inputs.

- The last request to the index method can be a POST request
- This can be problematic, since if the user refreshes the page after the POST
  request is sent (i.e. pressing submit button), the page will ask for confirmation
  to re-sent the form, which causes duplicate form submission
- Duplicate form submission is not desired
- So it is good practice to do a <b>redirection</b>, by using the redirect function
  to make a get request instead.
- ```name``` is stored in ```session```, because as soon as the redirect is done, the form data is destroyed.

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

- In this commit, user authentication functionality is added
- Uses ```Flask-Login``` (management of user sessions for logged-in users), ```Werkzeug``` (password hashing and verification) and ```itsdangerous``` (token generation and verification).
  
- In this commit, user permission logic is implemented based on the logged in user's role, to limit access to certain routes.

- In this commit, the following/follower feature is implemented through a many to many relationship. See comments on the code for how this works.
- IMPORTANT: When creating this feature, it was found that auto-generated migration scripts fail. This is primarily because the database used (SQLite) has a very limited support for altering existing tables. See https://www.sqlitetutorial.net/sqlite-alter-table/ for more background info.
- To get around this, methods explained in https://stackoverflow.com/questions/62640576/flask-migrate-valueerror-constraint-must-have-a-name were followed.
- In summary, a ```render_as_batch=True``` option is added to the Migrate function in the application factory (```__init.py__```) to get more altering table functionality. In addition, constraints such as foreignkey or primarykey are now given names through ```Config.NAMING_CONVENTION``` option in ```config.py```, because Alembic cannot drop constraints that are not named, which fails upgrades or downgrades that do this. This convention has to be passed in to the migration script, see the migration script ```98a6a60f6c4d.py``` on how this is done, and also the stackoverflow link for more background info. This convention has to also be passed to the db metadata; this is already done in the app factory.

