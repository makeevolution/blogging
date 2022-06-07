# This is the entry point to starting the whole app

import os
import sys
import click
# The following import imports from __init__.py of app folder
from app import create_app, db
from app.models import Permission, User, Role, Follow, Post
from flask_migrate import Migrate

# Create an instance of an application using a configuration in env var
usedConfiguration = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(usedConfiguration)
# Migrate the existing database, or create a new database if it doesn't exist
migrate = Migrate(app, db, render_as_batch = True)

COV = None
os.environ['FLASK_COVERAGE'] = '1'
if os.environ.get("FLASK_COVERAGE"):
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

# Nothing to do with the application, it's here just so that if we run flask shell from cmd, no imports for db, User and Role required
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission = Permission, Follow=Follow, Post=Post)

@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    print(tests)
    unittest.TextTestRunner(verbosity=3).run(tests)

@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    print(tests)
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