from queue import Empty
from app.models import User
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