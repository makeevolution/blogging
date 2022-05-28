from datetime import datetime
from queue import Empty
from app.models import AnonymousUser, Permission, User, Role, Follow
import unittest
from app import db
from faker import Faker

class UserModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        # ARRANGE
        self.u = User()
        self.u.password = "12345"
        
    def test_password_setter(self):
        # ACT & ASSERT
        self.assertTrue(self.u.password_hash is not None)
    
    def test_no_password_getter(self):
        # ACT & ASSERT
        # assertRaises is used as a context manager
        with self.assertRaises(AttributeError) as _:
            self.u.password
    
    def test_password_verifier(self):
        # ACT & ASSERT
        self.assertTrue(self.u.verify_password("12345"))
    
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
        u1 = User(email=email1, username = username1, password='cat')
        u2 = User(email=email2, username=username2,  password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 0)
        self.assertTrue(u2.followers.count() == 0)
        self.assertTrue(Follow.query.count() == 0)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 0)