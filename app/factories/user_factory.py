# A factory of different types of users.
# The factory requires the database to already be set up
# and running, since the factory will also push the created
# user to the database. See setUp methods in unit tests.

from sqlite3 import IntegrityError
from ..models import *
from .role_factory import role_factory
from faker import Faker
fake = Faker()

class ModeratorUser(User):
    email = fake.email()
    username = fake.user_name()
    password='password'
    confirmed=True
    name=fake.name()
    location=fake.city()
    about_me=fake.text()
    member_since=fake.past_date()

    role = role_factory("Moderator")
    __mapper_args__ = {
        "polymorphic_identity": "ModeratorUser",
    }

class AdminUser(User):
    email = fake.email()
    username = fake.user_name()
    password='password'
    confirmed=True
    name=fake.name()
    location=fake.city()
    about_me=fake.text()
    member_since=fake.past_date()


    role = role_factory("Administrator")
    __mapper_args__ = {
        "polymorphic_identity": "AdministratorUser",
    }

class GenericUser(User):
    email = fake.email()
    username = fake.user_name()
    password='password'
    confirmed=True
    name=fake.name()
    location=fake.city()
    about_me=fake.text()
    member_since=fake.past_date()


    role = role_factory("User")
    __mapper_args__ = {
        "polymorphic_identity": "GenericUser",
    }

def user_factory(userType):
    userTypes = {
        "User": GenericUser,
        "Administrator": AdminUser,
        "Moderator": ModeratorUser
        }
    createdUser = userTypes[userType]()

    try:
        db.session.add(createdUser)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise
    finally:        
        return createdUser