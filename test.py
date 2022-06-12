import sqlalchemy
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey, Boolean, Text
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import event

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    type = Column(String(50), default = "user")
    email = Column(String(64), unique=True, index=True)
    username = Column(String(64), unique=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "user"}
    
class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    default = Column(Boolean, default = False, index = True)
    permissions = Column(Integer)
    users: sqlalchemy.orm.Query = relationship('User', backref='role', lazy="dynamic")

class AdminUser(User):
    role = Role(name="Administrator")
    __mapper_args__ = {
        "polymorphic_identity": "AdministratorUser",
    }

engine = create_engine('sqlite:///')
Base.metadata.create_all(engine)
session = scoped_session(sessionmaker(engine))

session.close()

