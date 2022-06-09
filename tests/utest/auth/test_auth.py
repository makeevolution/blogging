from datetime import datetime
import unittest, logging,sys

from flask import url_for
from app import create_app, db
from app.main.views import follow
from app.models import User, Role

logging.basicConfig( stream=sys.stdout )
logging.getLogger(__name__).setLevel( logging.DEBUG )

class AuthTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        # Create a user in the database directly
        self.password = "testPassword"
        self.testUser = User(username="testUsername", password=self.password,
                    email = "test@test.com", location = "jakarta",
                    about_me = "test", member_since = datetime.utcnow(),
                    last_seen = datetime.utcnow())
        db.session.add(self.testUser)
        db.session.commit()
        self.client = self.app.test_client(use_cookies=True)

    @classmethod 
    def tearDownClass(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_registration_then_log_in_finally_log_out(self):
        # Use the registration endpoint to register, follow the redirection to main page
        resp = self.client.post('/auth/register', data={
            "username": "username",
            "password": "1234",
            "repeatPassword": "1234",
            "email": "aldasdf@email.com"
        }, follow_redirects = True)
        # Test if the user is registered in the database
        self.assertTrue(db.session.query(User).filter_by(username = "testUsername").first() is not None)
        # Test if the endpoint redirects to index page after the successful creation of user
        self.assertTrue(resp.request.path == "/")
        self.assertEqual(resp.status_code, 200)

        # Now test logging in
        resp = self.client.post('/auth/login', data = {
            "email": "aldasdf@email.com",
            "password": "1234"
        }, follow_redirects = True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.request.path, "/")
        self.assertTrue("Hello, " in resp.get_data(as_text=True))

        # And test logging out
        resp = self.client.get('/auth/logout', follow_redirects = True)
        self.assertEqual(resp.request.path, "/")
        self.assertTrue("Logged out successfully" in resp.get_data(as_text=True))

    def test_login_incorrect_username_password(self):
        # ACT
        resp = self.client.post('/auth/login', data = {
            "email": self.testUser.email,
            "password": self.password + "incorrect"
        }, follow_redirects = True)
        # ASSERT
        self.assertEqual(resp.request.path, "/auth/login")
        self.assertTrue("Username or password incorrect" in resp.get_data(as_text=True))

        # ACT
        resp = self.client.post('/auth/login', data = {
            "email": self.testUser.email + "wrongemail",
            "password": self.password
        }, follow_redirects = True)
        # ASSERT
        self.assertEqual(resp.request.path, "/auth/login")
        self.assertTrue("Username or password incorrect" in resp.get_data(as_text=True))
    
    def test_user_accessing_forbidden_route_log_in_redirect(self):
        # If an anonymous user accesses a route with a login_required decorator,
        # he should be redirected to log in page.
        # After he logs in, he should be routed back to the page he tried to access.

        # ACT
        resp = self.client.get('/edit_profile/' + str(self.testUser.id), follow_redirects = True)  
        # ASSERT
        self.assertEqual(resp.request.path, "/auth/login")
        self.assertEqual(resp.request.args.get('next'), "/edit_profile/" + str(self.testUser.id))
        # ACT
        # the URL of the redirection to the login page will contain info about the page that
        # was attempted to be accessed (the page with the decorator). Thus, we send login data to
        # that URL instead of a generic /auth/login.
        resp = self.client.post(resp.request.full_path, data = {
            "email": self.testUser.email,
            "password": self.password
        }, follow_redirects = True)
        # ASSERT
        self.assertEqual(resp.request.path, '/edit_profile/'+str(self.testUser.id))

    def test_accessing_registration_page(self):
        # ACT
        resp = self.client.get('/auth/register', follow_redirects = True)  
        # Assert
        self.assertTrue("Register here" in resp.get_data(as_text=True))

