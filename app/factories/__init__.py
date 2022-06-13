from ..models import *
from faker import Faker
from .role_factory import role_factory

fake = Faker()

class ModeratorUser(User):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.role = db.session.query(Role).filter_by(name = "Moderator").first() 
   
    __mapper_args__ = {
        "polymorphic_identity": "ModeratorUser",
    }

class AdminUser(User):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.role = db.session.query(Role).filter_by(name = "Administrator").first() 

    __mapper_args__ = {
        "polymorphic_identity": "AdministratorUser",
    }

class GenericUser(User):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.role = db.session.query(Role).filter_by(name = "User").first() 

    __mapper_args__ = {
        "polymorphic_identity": "GenericUser",
    }
