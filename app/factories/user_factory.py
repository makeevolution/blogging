# A factory of different types of users.
# The factory requires the database to already be set up
# and running, since the factory will also push the created
# user to the database. See setUp methods in unit tests.

from . import *
from sqlite3 import IntegrityError

def user_factory(userType):
    userTypes = {
        "User": GenericUser,
        "Administrator": AdminUser,
        "Moderator": ModeratorUser
        }
    createdUser = userTypes[userType](
        email = fake.email(),
        username = fake.user_name(),
        password='password',
        confirmed=True,
        name=fake.name(),
        location=fake.city(),
        about_me=fake.text(),
        member_since=fake.past_date(),
    )
    try:
        db.session.add(createdUser)
        db.session.commit()
    except IntegrityError as e: 
        raise e
    finally:
        return createdUser