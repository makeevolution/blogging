# Notes on Alembic

- We have a sqlalchemy model in models.py, how can we create a new sqlite database for this model, given we are using ```flask-sqlalchemy```?
  - First set the new name of the database in customdb configuration in ```config.py```
  -  
- In flasky.py there's a command createdatabase to generate a new sqlite database using alembic.