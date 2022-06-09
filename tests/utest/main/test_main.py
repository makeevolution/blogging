from functools import wraps
import unittest, logging, sys

from flask import url_for
from app import create_app, db
from app.main.views import follow
from app.models import User, Role
from app.factories.user_factory import user_factory
from tests.utest.main.conftest import log_in

logging.basicConfig( stream=sys.stdout )
logging.getLogger(__name__).setLevel( logging.DEBUG )

# Helper decorator that logs in a client to an endpoint, returns the client,
# then logs them out once the test is done. 
# Using ‘wraps’ helps to presever info about the function being decorated
# Rmember that when used inside a class, the decorator becomes a "part" of the class, therefore it
# can access the attributes of the class (e.g. self.client) too; just make sure to pass in 
# self.
def log_in_and_out(user):
    def decorator(f):
        @wraps(f)
        def decorated_function(self, *args, **kwargs):
            try:
                userData = getattr(self,user)
            except AttributeError as e:
                e.args = (f"User {user} is not yet defined!",)
                raise
            self.client.post('/auth/login', data = {
                                "email": userData.email,
                                "password": "password"}, follow_redirects = True)
            f(self)
            self.client.get('/auth/logout', follow_redirects = True)
            # Fail-safe to ensure user is actually logged out.
            # Accesssing "/admin" should redirect to login page.
            resp2 = self.client.get('/admin', follow_redirects = True)
            self.assertTrue("/auth/login" in getattr(resp2.request,'full_path'))
        return decorated_function
    return decorator 
    
class MainTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.app = create_app('testing')
        # Get the app context (see page 18 of book for more info)
        self.app_context = self.app.app_context()
        # Make the app accessible by current_app by pushing the app's app_context
        self.app_context.push()
        # Create the tables; the models are ready but the corresponding tables are
        # not created yet!
        db.create_all()
        # Insert the roles
        Role.insert_roles()
        # Create a generic user, moderator and admin, and put them in database 
        # (done by factory)
        self.genericUser = user_factory("User")
        self.moderatorUser = user_factory("Moderator")
        self.administratorUser = user_factory("Administrator")
        # Create a generic test client (i.e. browser)
        self.client = self.app.test_client(use_cookies=True)
    
    @classmethod
    def tearDownClass(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_index(self):
        #log = logging.getLogger(__name__)
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        #log.debug("testme")
        self.assertTrue("Stranger" in resp.get_data(as_text=True))

    @log_in_and_out("genericUser")
    def test_all(self):
        resp = self.client.get('main/all', follow_redirects = True)
        self.assertEqual(resp.status_code, 200)
    
    @log_in_and_out("genericUser")
    def test_following(self):
        resp = self.client.get('main/following', follow_redirects = True)
        self.assertEqual(resp.status_code, 200) 
    
    def test_user_page_user_exists(self):
        resp = self.client.get(f'main/user/{self.genericUser.username}')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(f"{self.genericUser}" in resp.get_data(as_text=True)) 
    
    def test_user_page_user_doesnt_exist(self):
        resp = self.client.get(f'main/user/{self.genericUser.username}NotExist', follow_redirects = True)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(f"User {self.genericUser.username}NotExist not found" in resp.get_data(as_text=True))
    