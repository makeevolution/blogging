import unittest, logging,sys

from flask import url_for
from app import create_app, db
from app.main.views import follow
from app.models import User, Role

logging.basicConfig( stream=sys.stdout )
logging.getLogger(__name__).setLevel( logging.DEBUG )

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True) 
    
    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_home_page(self):
        log = logging.getLogger(__name__)
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        #log.debug("testme")
        self.assertTrue("Stranger" in resp.get_data(as_text=True))

    def test_user_registration_and_log_in(self):
        # Use the registration endpoint to register, follow the redirection to main page
        resp = self.client.post('/auth/register', data={
            "username": "testUsername",
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
        
