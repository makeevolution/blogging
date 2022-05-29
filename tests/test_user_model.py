from datetime import datetime
from app.models import AnonymousUser, Permission, User, Role, Follow
import unittest
from app import db, create_app
from faker import Faker

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        # ACT & ASSERT
        u = User(password="cat")
        self.assertTrue(u.password_hash is not None)
    
    def test_no_password_getter(self):
        # ACT & ASSERT
        # assertRaises is used as a context manager
        u = User(password="cat")
        with self.assertRaises(AttributeError) as _:
            u.password
    
    def test_password_verifier(self):
        # ACT & ASSERT
        u = User(password="cat")
        self.assertTrue(u.verify_password("cat"))
    
    def test_user_role(self):
        user = User(role = Role.query.filter_by(name="User").first())
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.WRITE))
        self.assertFalse(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))
    def test_admin_role(self):
        user = User(role = Role.query.filter_by(name="Administrator").first())
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.WRITE))
        self.assertTrue(user.can(Permission.MODERATE))
        self.assertTrue(user.can(Permission.ADMIN))
        self.assertTrue(user.is_administrator())

    def test_moderator_role(self):
        user = User(role = Role.query.filter_by(name="Moderator").first())
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.WRITE))
        self.assertTrue(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))

    def test_anonymous_user(self):
        user = AnonymousUser()
        for permission in filter(lambda x: not x.startswith('--'), dir(Permission)):
            self.assertFalse(user.can(permission))

    def test_follows(self):
        while True:
            email1= Faker().email()
            email2= Faker().email()
            username1= Faker().name()
            username2= Faker().name()
            if(email1!=email2 and username1!=username2):
                break
        # Create two random users
        u1 = User(email=email1, username = username1, password='cat')
        u2 = User(email=email2, username = username2,  password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()
        # Make u1 follow u2
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        # Check their relationships
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        # Check their relationships through attributes
        # u1.following returns a list of users u1 is following
        self.assertTrue(u1.following.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        # Check the relationships through the association table (i.e. follows table)
        # u1.following.all() returns a list of instances of the Follow class, those instances which contain users
        # that u1 is following. [-1] is to get the first entry.
        f = u1.following.all()[-1]
        # The Follow class has an attribute "following" through the backref defined in User class
        self.assertTrue(f.following == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        # Same check as above, this time for u2
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)
        # Now test unfollowing
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.following.count() == 0)
        self.assertTrue(u2.followers.count() == 0)
        # Follow.query.all() returns all instances of following/followed situation (i.e. each row in the table)
        self.assertTrue(Follow.query.count() == 0)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        # Test if the association table removes all relationships for users that are deleted (i.e. the delete-orphan option)
        self.assertTrue(Follow.query.count() == 0)