'''
Script to create a new database given the current model
Usage: python newdb.py --dbname=NewDBName
HOW TO:
1. Set the new db name in config.py under customdb class
2. Run as usage above, run it in the same folder as location of config.py so that the migrations folder are created in the correct location
3. In env.py of created folder, add the following under the from alembic import context line:
from flask import current_app

# Check if current_app has a Flask instance associated with it
try:
    _ = hasattr(current_app,"name")
except RuntimeError:
    # Since the models are defined to inherit from db and not from Base,
    # and the db is a SQLAlchemy() instance of flask-sqlalchemy,
    # we cannot use the models directly without not creating a flask instance.
    # So need to create a Flask app instance to gain access to the models.
    # Push a new app_context so the current_app has an instance.
    from app import create_app
    app = create_app("customdb")
    app_context = app.app_context()
    app_context.push()
4. In env.py too, add target metadata as shown:
target_metadata = current_app.extensions["sqlalchemy"].db.metadata
5. In alembic.ini, check sqlalchemy.url line, point it to your db connection string
6. Run python -m alembic -c migrationsNewDBName/alembic.ini revision --autogenerate to get the migration script
7. Run python -m alembic -c migrationsNewDBName/alembic.ini upgrade head to upgrade db

'''
import click, os, sys
parentdir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
currentdir =  os.path.abspath(os.getcwd())
sys.path.append(parentdir)
sys.path.append(currentdir)

from app import create_app
app = create_app("customdb")
app_context = app.app_context()
app_context.push()

@click.command()
@click.option("--dbname", required = True)
def createdatabase(**kwargs):
    engine = app.extensions["sqlalchemy"].db.engine
    print(engine)

    from alembic.config import Config
    from alembic import command

    app.extensions["sqlalchemy"].db.metadata.create_all(engine)
    folder = f"{os.getcwd()}/migrations{kwargs.get('dbname')}"
    alembic_cfg = Config(f"{folder}/alembic.ini", attributes = {"sqlalchemy.url": str(engine)})
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine))
    command.init(alembic_cfg, directory = folder)

if __name__ == "__main__":
    createdatabase()