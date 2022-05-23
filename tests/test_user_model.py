from queue import Empty
from app.models import AnonymousUser, Permission, User, Role 
import unittest

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

