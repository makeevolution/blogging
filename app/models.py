# the import below imports db from __init__.py
from msilib.schema import Font
from flask import current_app
from sqlalchemy import false
from . import db
import os

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16
    # The permissions are in powers of 2 so we can have permissions to be combined by addition, while giving each possible combination of
    # permissions a unique value (the sum is always unique).
    # This is also so that the bitwise comparison in has_permission() in Role functions properly.

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    # db.ForeignKey('roles.id') means the role_id gets its value from
    # id column of roles table

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        # Initialize the role of the user. Remember self.role attribute is defined 
        # in Role class through backref.
        # Interrogate the Base classes first, and if self.role is still
        # not defined, define it here.
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if(self.email == current_app.config["FLASKY_ADMIN"]):
                self.role = Role.query.filter_by(name="Administrator").first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    
    def can(self, permission):
        return self.role is not None and self.role.has_permission(permission)
    def is_administrator(self):
        return self.can(Permission.ADMIN)
    

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy="dynamic")
    
    def __init__(self, **kwargs):
        super(Role,self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
    # Each element in users column is a User object.
    # backref='role' adds a new attribute in the User model
    # so an instance of User can access/set its associated role
    # using this attribute instead of using role_id.
    # e.g. user_role = Role(name="User")
    #      user_susan = User(username="Susan",role=user_role)
    # Page 66 on how to understand this better.

    # lazy is used so that accessing the attribute does not automatically
    # return the attribute, so we can apply filtering to it 
    # e.g. user_role.users.order_by(User.username).all() can also be done
    # like what we usually do for query to an class (e.g. Role.query.filter_by(role=user_role).all())

    def __repr__(self):
        return '<Role %r>' % self.name

    # The following defines methods to edit permission    
    def has_permission(self, perm):
        return self.permissions & perm == perm
        # Bitwise operator & is used here.
        # example: if self.permissions is 5 and perm is 1
        # then, 1 & 5 is 1, and 1 == 1 is True
        # To try out, run flask run and r = Role(name='User), and use r to try the permission functions

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0
    
    # Create roles in the database (i.e. User, Moderator, Administrator) with their respective permissions
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'  
        for r in roles:
            # Try to get the role row in the Role table in the database with name = r
            # If it doesn't exist yet in the database, create the role
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            # If it does exist, update the corresponding permissions for this role with what we have in roles
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (True if role.name == default_role else False)
            db.session.add(role)
            db.session.commit()