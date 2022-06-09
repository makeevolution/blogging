# This is the entry point to starting the whole app

import os
import sys

# Coverage output not possible in debug mode, since COV.start() below starts a different
# thread that actually runs the tests. Check if debug mode is used using sys.gettrace() output.

# When using flask test command (defined below), notice it uses app in its decorator. This
# means that it requires an app instance to be created before the test can be run. In this
# app instance, that's where the login_manager, etc. is initialized i.e. is run. When another
# instance is made (i.e. in setUp of each unit test), this part is not run anymore. The coverage
# engine won't see any decorators using these login_manager etc. (e.g. @login_required) if we
# start the engine after the app.create_app() statemenet below, making the coverage report 
# incorrect.

if (sys.gettrace() is None):
    import coverage
    # Start the coverage engine. the include option is to limit which code to analyse; otherwise it will also analyse
    # the pip packages!
    with open(".coveragerc", "w+") as f:
        coverageString = "[report] \n"
        coverageString = coverageString + "exclude_lines = \n"
        coverageString = coverageString + "\t pragma: no cover \n"
        coverageString = coverageString + "\t import \n"
        coverageString = coverageString + "\t from .* import \n"

        # Regexes for lines to exclude from consideration \n exclude_lines = \n \tpragma: no cover \ \ttest this thing"
        f.write(coverageString)
    COV = coverage.coverage(branch = True, include="app/*")
    COV.start()

# The following import imports from __init__.py of app folder
from app import create_app, db
from app.models import Permission, User, Role, Follow, Post
from flask_migrate import Migrate
from config import config

# Create an instance of an application using a configuration in env var
usedConfiguration = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(usedConfiguration)
# Migrate the existing database, or create a new database if it doesn't exist
migrate = Migrate(app, db, render_as_batch = True)

# Nothing to do with the application, it's here just so that if we run flask shell from cmd, no imports for db, User and Role required
@app.shell_context_processor
def make_shell_context():
    print("Shell started")
    print(f"WARNING: using database " + \
            getattr(config[usedConfiguration], "SQLALCHEMY_DATABASE_URI"))
    return dict(db=db, User=User, Role=Role, Permission = Permission, Follow=Follow, Post=Post)

# Configuration for test coverage report. Need to put it here so that it starts scanning
# before any imports for the app starts.
COV = None

@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__=="__main__":
    app.run(port=5000)