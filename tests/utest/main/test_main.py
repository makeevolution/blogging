import ast
from dataclasses import dataclass
from functools import wraps
from multiprocessing.sharedctypes import Value
from string import ascii_letters
import unittest, logging, sys

from flask import url_for
from sqlalchemy import true
from app import create_app, db
from app.main.views import follow
from app.models import *
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
                userInstance = getattr(self,user)
            except AttributeError as e:
                e.args = (f"User {user} is not yet defined!",)
                raise
            self.client.post('/auth/login', data = {
                                "email": userInstance.email,
                                "password": "password"}, follow_redirects = True)
            try:
                f(self)
            finally:
                self.client.get('/auth/logout', follow_redirects = True)
                # Fail-safe to ensure user is actually logged out.
                # Accesssing "/admin" should redirect to login page.
                resp2 = self.client.get('/admin', follow_redirects = True)
                self.assertTrue("/auth/login" in getattr(resp2.request,'full_path'))
        return decorated_function
    return decorator

def post_something(user, post_body = "test"):
    def decorator(f):
        @wraps(f)
        def decorated_function(self, *args, **kwargs):
            try:
                userInstance = getattr(self,user)
            except AttributeError as e:
                e.args = (f"User {user} is not yet defined!",)
                raise
            post = Post(body=post_body, author = userInstance)
            db.session.add(post)
            db.session.commit()
            try:
                f(self)
            finally:
                db.session.delete(post)
                db.session.commit()
        return decorated_function
    return decorator

def comment_something(user, post_id, comment_body):
    def decorator(f):
        @wraps(f)
        def decorated_function(self, *args, **kwargs):
            try:
                userInstance = getattr(self,user)
            except AttributeError as e:
                e.args = (f"User {user} is not yet defined!",)
                raise
            comment = Comment(author = userInstance, body=comment_body, post_id = post_id)
            db.session.add(comment)
            db.session.commit()
            try:
                f(self)
            finally:
                db.session.delete(comment)
                db.session.commit()
        return decorated_function
    return decorator

def unfollow(follower, to_be_unfollowed):
    def decorator(f):
        @wraps(f)
        def decorated_function(self, *args, **kwargs):
            try:
                f(self)
            finally:
                try:
                    userInstanceFollower = getattr(self,follower)
                    userInstanceToBeUnfollowed = getattr(self,to_be_unfollowed)
                except AttributeError as e:
                    e.args = (f"User {follower} or/and {to_be_unfollowed} are not yet defined!",)
                    raise
                userInstanceFollower.unfollow(userInstanceToBeUnfollowed)
        return decorated_function
    return decorator

def follow_with_unfollow_teardown(*followerFollowingPair):
    def decorator(f):
        @wraps(f)
        def decorated_function(self, *args, **kwargs):
            if(len(followerFollowingPair)%2 != 0):
                raise ValueError("Each follower must have a follow target")
            pair = [(followerFollowingPair[i-1],j) for i,j in enumerate(followerFollowingPair) if i%2!=0]  
            for follower, followed in pair:
                try:
                    userInstanceFollower = getattr(self,follower)
                    userInstanceToBeFollowed = getattr(self,followed)
                    userInstanceFollower.follow(userInstanceToBeFollowed)
                except AttributeError as e:
                    e.args = (f"User {follower} or/and {followed} are not yet defined!",)
                    raise
            try:
                f(self)
            finally:
                for follower, followed in pair:
                    userInstanceFollower = getattr(self,follower)
                    userInstanceToBeFollowed = getattr(self,followed)
                    userInstanceFollower.unfollow(userInstanceToBeFollowed)
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
        
    @classmethod
    def tearDownClass(self) -> None:
        self.app_context.pop()

    def setUp(self):
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

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

    def test_index(self):
        #log = logging.getLogger(__name__)
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        #log.debug("testme")
        self.assertTrue("Stranger" in resp.get_data(as_text=True))

    @log_in_and_out("genericUser")
    def test_all(self):
        resp = self.client.get('/all', follow_redirects = True)
        self.assertEqual(resp.status_code, 200)
    
    @log_in_and_out("genericUser")
    def test_following(self):
        resp = self.client.get('/following', follow_redirects = True)
        self.assertEqual(resp.status_code, 200) 
    
    def test_user_page_user_exists(self):
        resp = self.client.get(f'/user/{self.genericUser.username}')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(f"{self.genericUser.username}" in resp.get_data(as_text=True)) 
    
    def test_user_page_user_doesnt_exist(self):
        resp = self.client.get(f'/user/{self.genericUser.username}NotExist', follow_redirects = True)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(f"User {self.genericUser.username}NotExist not found" in resp.get_data(as_text=True))
    
    @log_in_and_out("genericUser")
    def test_editing_profile_for_user(self):
        newName = "aldi"
        newLocation = "jakartas"
        newAboutMe = "smth"
        resp = self.client.post("/edit_profile", data={
            "name": newName, 
            "location": newLocation,
            "about_me": newAboutMe
        }, follow_redirects = True)
        self.assertTrue(resp.status_code, 302)
        self.assertTrue("Your profile has been successfully updated" in resp.get_data(as_text=True))
        self.newMe = db.session.query(User).filter_by(username = self.genericUser.username).first()
        # In SQLAlchemy, the instance is also updated when we update the database!
        # So self.genericUser instance is also updated!
        # But just check all just to make sure
        self.assertEqual(self.newMe, self.genericUser)
        self.assertTrue(newName == self.newMe.name)
        self.assertTrue(newLocation == self.newMe.location)
        self.assertTrue(newAboutMe == self.newMe.about_me)

    def test_editing_profile_not_allowed_for_anon(self):
        newName = "aldi"
        newLocation = "jakartas"
        newAboutMe = "smth"
        resp = self.client.post("/edit_profile", data={
            "name": newName, 
            "location": newLocation,
            "about_me": newAboutMe
        }, follow_redirects = True)
        self.assertTrue(resp.status_code, 302)
        self.assertTrue(resp.request.path == "/auth/login")
        self.assertTrue("Please log in to access this page" in resp.get_data(as_text=True))
    
    @log_in_and_out("administratorUser")
    def test_editing_profile_of_someone_else_by_admin(self):
        # Get ID of the generic user
        genUserId = self.genericUser.id
        # Define new data of the generic user
        newName = "ad"
        newLocation = "test2"
        newAbout_me = "test234" 
        newUsername = "test23423" 
        newEmail = "asdf@test.com"
        newUserConfirmed = False
        newRole = db.session.query(Role).filter_by(name = "Moderator")
        resp = self.client.post(f'/edit_profile/{genUserId}', data = {
            "name": newName,
            "location": newLocation,
            "about_me": newAbout_me,
            "username": newUsername,
            "email": newEmail,
            "confirmed": newUserConfirmed,
            "role": "2"
        })
        self.assertTrue(self.genericUser.role.name == "Moderator")

    # Remember since the decorators are wrappers,
    # the execution order is first post_something up to f(self),
    # then once it reaches there, it executes log_in_and_out,
    # goes up to f(self), then executes f(self).
    # Once f(self) is done, it continues log_in_and_out,
    # then once that's done, it continues post_something.
    # Debug to find out.
    # ARRANGE
    @post_something("genericUser","MyNewPost")
    @log_in_and_out("genericUser")
    def test_post_page(self):
        # ACT (the thing being tested)
        resp = self.client.get("/post/1")
        # ASSERT (that the post by the user is on display)
        self.assertTrue("MyNewPost" in resp.get_data(as_text=True))
        # ASSERT (that the user's username is on display)
        self.assertTrue(f"{self.genericUser.username}" in resp.get_data(as_text = True))

    # ARRANGE
    @post_something("genericUser","MyNewPost")
    @log_in_and_out("moderatorUser")
    def test_commenting_on_a_post_page(self):
        resp = self.client.post("/post/1", data = {
            "text" : "thisIsAComment"
        }, follow_redirects = True)
        self.assertEqual(resp.request.path, "/post/1")
        # ASSERT (that the post by the user is on display)
        self.assertTrue("MyNewPost" in resp.get_data(as_text=True))
        # ASSERT (that the user's username is on display)
        self.assertTrue(f"{self.genericUser.username}" in resp.get_data(as_text = True))
        # ASSERT (that the comment is displayed)
        self.assertTrue(f"thisIsAComment" in resp.get_data(as_text=True))
        # ASSERT (that the commenter's username is displayed)
        self.assertTrue(f"{self.moderatorUser.username}" in resp.get_data(as_text=True))

    @post_something("genericUser","MyNewPost")
    @log_in_and_out("genericUser") 
    def test_editing_post_success(self):
        resp = self.client.post(f"/edit/1", data = {
            "text": "newBody"
        }, follow_redirects = True)
        self.assertTrue("newBody" in resp.get_data(as_text = True))
    
    @post_something("moderatorUser","MyNewPost")
    @log_in_and_out("genericUser")
    def test_editing_post_by_other_valid_user_unauthorized(self):
        resp = self.client.post(f"/edit/1", data = {
            "text": "newBody"
        }, follow_redirects = True)
        self.assertEqual(resp.status_code, 403)

    @post_something("genericUser","MyNewPost")
    def test_editing_post_by_anonymous_user_unauthorized(self):
        resp = self.client.post(f"/edit/1", data = {
            "text": "newBody"
        }, follow_redirects = True)
        self.assertEqual(resp.status_code, 403)

    @log_in_and_out("genericUser")
    @unfollow("genericUser","moderatorUser")
    def test_follow_success(self):
        resp = self.client.get(f"/follow/{self.moderatorUser.username}", follow_redirects = True)
        self.assertTrue(self.genericUser.is_following(self.moderatorUser))
        self.assertTrue("You are now following this user" in resp.get_data(as_text=True))
    
    @log_in_and_out("genericUser")
    @unfollow("genericUser","moderatorUser")
    def test_already_following(self):
        resp = self.client.get(f"/follow/{self.moderatorUser.username}", follow_redirects = True)
        self.assertTrue(self.genericUser.is_following(self.moderatorUser))
        resp2 = self.client.get(f"/follow/{self.moderatorUser.username}", follow_redirects = True)
        self.assertTrue("You are already following this user!" in resp2.get_data(as_text=True))
    
    @log_in_and_out("genericUser")
    def test_following_invalid_user(self):
        resp = self.client.get(f"/follow/someGuyIDontKnow", follow_redirects = True)
        self.assertTrue("Invalid user input!" in resp.get_data(as_text=True))
        self.assertTrue(resp.request.path == "/")

    @log_in_and_out("genericUser")
    @follow_with_unfollow_teardown("genericUser","moderatorUser")
    def test_unfollow_success(self):
        resp = self.client.get(f"/unfollow/{self.moderatorUser.username}", follow_redirects = True)
        self.assertFalse(self.genericUser.is_following(self.moderatorUser))
        self.assertTrue("You have unfollowed this user" in resp.get_data(as_text=True))
    
    @log_in_and_out("genericUser")
    @follow_with_unfollow_teardown("genericUser","moderatorUser")
    def test_already_unfollowing(self):
        resp = self.client.get(f"/unfollow/{self.moderatorUser.username}", follow_redirects = True)
        self.assertFalse(self.genericUser.is_following(self.moderatorUser))
        resp2 = self.client.get(f"/unfollow/{self.moderatorUser.username}", follow_redirects = True)
        self.assertTrue("You are already not following this user!" in resp2.get_data(as_text=True))
    
    @log_in_and_out("genericUser")
    @follow_with_unfollow_teardown("genericUser","moderatorUser")
    def test_unfollowing_invalid_user(self):
        resp = self.client.get(f"/unfollow/someGuyIDontKnow", follow_redirects = True)
        self.assertTrue("Invalid user input!" in resp.get_data(as_text=True))
        self.assertTrue(resp.request.path == "/")

    @follow_with_unfollow_teardown("moderatorUser","genericUser", 
                                    "administratorUser","genericUser")
    def test_followers_success(self):
         resp = self.client.get(f"/followers/{self.genericUser.username}")
         self.assertTrue(f"{self.moderatorUser.username}" in resp.get_data(as_text=True))
         self.assertTrue(f"{self.administratorUser.username}" in resp.get_data(as_text=True))
    
    @follow_with_unfollow_teardown("genericUser","moderatorUser", 
                                    "genericUser","administratorUser")
    def test_followings_success(self):
         resp = self.client.get(f"/followings/{self.genericUser.username}")
         self.assertTrue(f"{self.moderatorUser.username}" in resp.get_data(as_text=True))
         self.assertTrue(f"{self.administratorUser.username}" in resp.get_data(as_text=True))

    @log_in_and_out("moderatorUser")
    def test_moderate_success(self):
        resp = self.client.get(f"/moderate")
        self.assertEqual(resp.status_code, 200)
    
    @log_in_and_out("genericUser")
    def test_moderate_fails(self):
        resp = self.client.get(f"/moderate", follow_redirects = True)
        self.assertEqual(resp.status_code, 403)

    @log_in_and_out("moderatorUser")
    @post_something("genericUser", "testPost")
    @comment_something("genericUser", 1, "testComment")
    def test_moderate_disable_enable_success(self):
        # First test if the comment is enabled
        self.assertEqual(db.session.query(Comment).get(1).disabled, 0)
        resp = self.client.get(f"/moderate/disable/1")
        # Then check if comment is disabled
        self.assertEqual(db.session.query(Comment).get(1).disabled, 1)
        # And also that it is disabled in moderate page 
        resp2 = self.client.get(f"/moderate")
        self.assertTrue("This comment has been disabled" in resp2.get_data(as_text=True))
        # Re-enable and test if it exists again
        resp3 = self.client.get(f"/moderate/enable/1")
        self.assertEqual(db.session.query(Comment).get(1).disabled, 0)
        resp4 = self.client.get(f"/moderate")
        self.assertTrue("testComment" in resp4.get_data(as_text=True))