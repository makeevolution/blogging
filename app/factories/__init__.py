from ..models import *
from faker import Faker
from .role_factory import role_factory

fake = Faker()

class ModeratorUser(User):
    role = role_factory("Moderator")
    __mapper_args__ = {
        "polymorphic_identity": "ModeratorUser",
    }

class AdminUser(User):
    role = role_factory("Administrator")
    __mapper_args__ = {
        "polymorphic_identity": "AdministratorUser",
    }

class GenericUser(User):
    role = role_factory("User")
    __mapper_args__ = {
        "polymorphic_identity": "GenericUser",
    }
