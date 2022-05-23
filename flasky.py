# This is the entry point to starting the whole app

import os
# The following import imports from __init__.py of app folder
from app import create_app, db
from app.models import Permission, User, Role
from flask_migrate import Migrate

# Create an instance of an application using a configuration in env var
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# Migrate the existing database, or create a new database if it doesn't exist
migrate = Migrate(app, db)

# Nothing to do with the application, it's here just so that if we run flask shell from cmd, no imports for db, User and Role required
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission = Permission)

@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=3).run(tests)

if __name__=="__main__":
    app.run(port=5000)