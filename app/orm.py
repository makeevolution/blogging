from flask import current_app
from sqlalchemy import false
from . import db
from .models import Permission, User, Role

class InvalidAttributeException(Exception):
    def __init__(self, message = "Attribute Invalid!"):
        super(InvalidAttributeException, self).__init__(message)
        print("")

def getAllUsers():
    return db.session.query(User).all()

# Resets all users to User role, except admin
def resetUserRoles():
    for user in getAllUsers():
        if user is None:
            continue
        if user.email ==  current_app.get("FLASKY_ADMIN"):
            user.role = Role.query.filter_by(name="Administrator").first()
        else:
            user.role = Role.query.filter_by(default=True).first()
        db.session.add(user)
        db.session.commit()
    # For each user in the database
    # 
# def addAttributeToUser(attribute: str, val):
#     if not hasattr(User, attribute):
#         raise InvalidAttributeException("Attribute {attribute} invalid!")
#     #get the user first
#     # then add the attr
#     # then commit
#     user = db.session.query.filter_by()