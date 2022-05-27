# the import below imports db from __init__.py
from datetime import datetime
import hashlib
import bleach
from flask import current_app
from markdown import markdown
from sqlalchemy import false
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin, UserMixin

# This decorator is used to help the login manager
# to get info about the logged-in user.
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, {"id": int(user_id)})

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16
    # The permissions are in powers of 2 so we can have permissions to be combined by addition, while giving each possible combination of
    # permissions a unique value (the sum is always unique).
    # This is also so that the bitwise comparison in has_permission() in Role functions properly.

# UserMixin is from flask-login, which has properties and methods related to user authentication
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default = datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default = datetime.utcnow)
    avatar_hash = db.Column(db.String(32)) #store avatar hash because computing hash is expensive
    # db.ForeignKey('roles.id') means the role_id gets its value from
    # id column of roles table.
    # More info on what index is: https://dataschool.com/sql-optimization/how-indexing-works/
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    # a db relationship to indicate one to many relationship i.e. one user can have
    # many posts, but one post can only belong to one person.

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        # Initialize the role of the user. Remember self.role attribute is defined 
        # in Role class through backref.
        # Interrogate the Base classes first, and if self.role is still
        # not defined, define it here.
        super(User,self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
        if self.role is None:
            if(self.email == current_app.config["FLASKY_ADMIN"]):
                self.role = Role.query.filter_by(name="Administrator").first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    
    def can(self, permission):
        return self.role is not None and self.role.has_permission(permission)
    def is_administrator(self):
        return self.can(Permission.ADMIN)
    
    @property
    def password(self):
        raise AttributeError("password is not accessible")
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        # Once a password is hashed, it can never be recovered
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=100, default='retro', rating='g'):
        url = "https://www.gravatar.com/avatar"
        hash = self.avatar_hash or self.gravatar_hash()
        return f'{url}/{hash}?s={size}&d={default}&r={rating}'

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

# Flask-login has their own AnonymousUser class, but here we
# override it with our own implementation, to also have can and is_admin methods
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy="dynamic")
    # A db relationship is used to indicate a one to many relationship i.e.
    # one role can have many users, but one user can only have one role

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
    def __init__(self, **kwargs):
        super(Role,self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role %r>' % self.name

    # The following defines methods to edit permission    
    def has_permission(self, perm):
        return self.permissions & perm == perm
        # Bitwise operator & is used here.
        # example: if self.permissions is 5 and perm is 1
        # then, 1 & 5 is 1, and 1 == 1 is True
        # To try out, run flask shell and r = Role(name='User'), and use r to try the permission functions

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

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # The markdown input field can be dangerous, attackers can create markdown that generates
    # html code that can attack the server.
    # To avoid this, the markdown input is filtered by the below staticmethod.
    # The db.event.listen listens to a db.session.add(post) event, that sets/edits the body column.
    # When it happens, the Post.on_changed_body method is run
    # First, the markdown input is turned to html by the markdown() method
    # Second, the bleach.clean() removes any html tags not in allowed_tags
    # Third, the bleach.linkify() is not a security feature; it's there to convert any URL into clickable
    # format (i.e. add <a> tags to them)
    # Finally, the output of this method is put inside body_html.
    # The _posts.html will look if body_html is not empty (should be). If it isn't, then this will be rendered. Otherwise,
    # the raw markdown will be rendered by Jinja to html.
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)
