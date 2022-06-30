import unittest
from flask import current_app
from app import create_app, db


class AppInitTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        # Get the app context (see page 18 of book for more info)
        self.app_context = self.app.app_context()
        # Make the app accessible by current_app by pushing the app's app_context
        self.app_context.push()
        # Initialize the database
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
