from . import db
from .models import User

class InvalidAttributeException(Exception):
    def __init__(self, message = "Attribute Invalid!"):
        super(InvalidAttributeException, self).__init__(message)
        print("")
def getAllUsers():
    return db.session.query(User).all()

# def addAttributeToUser(attribute: str, val):
#     if not hasattr(User, attribute):
#         raise InvalidAttributeException("Attribute {attribute} invalid!")
#     #get the user first
#     # then add the attr
#     # then commit
#     user = db.session.query.filter_by()