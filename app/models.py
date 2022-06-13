# the import below imports db from __init__.py
from datetime import datetime
import hashlib
import json
from sqlite3 import Timestamp
from xml.dom import ValidationErr
import bleach
from flask import current_app, url_for
from itsdangerous import Serializer
from markdown import markdown
import sqlalchemy
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin, UserMixin
from app.exceptions import ValidationError

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

# The class Follow corresponds to the association table called "follows".
# It has two primary keys. This means no two rows can have the same follower_id and following_id.
# This is to prevent multiple follower/following instances (a user can only follow another user once. That instance has to be deleted (i.e. unfollow) before re-following is possible.
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    trigger = db.Column(db.Text())

# A comment belogns to one user, one user can have multiple comments (one to many)
# A comment belongs to a post, one post can have multiple comments (one to many) 
# Thus, a comment instance has 2 foreign and primary keys, one for the user making it and one for the post its in
# 2 primary keys because it has to be unique to a user and a post
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Integer, default=0)
    
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)

# UserMixin is from flask-login, which has properties and methods related to user authentication
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), default = "user")
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
    # Polymorphic arguments below is for if User is being inherited (like in the factory)
    # Type column is there to register the inheriter in the table.
    # The inheriter needs to set its identity, see user_factory.py on how.
    # More info: https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "user"}
    avatar_hash = db.Column(db.String(32)) #store avatar hash because computing hash is expensive
    # db.ForeignKey('roles.id') means the role_id gets its value from
    # id column of roles table.
    # More info on what index is: https://dataschool.com/sql-optimization/how-indexing-works/
    posts: sqlalchemy.orm.Query = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    # a db relationship to indicate one to many relationship i.e. one user can have
    # many posts, but one post can only belong to one person.
    
    # The two attributes below ("following" and "followers") define the following and follower relationship between users.
    # A User can both be followed by multiple users (followers attribute below) and follow multiple users (following attribute below)
    # So it's a many to many relationship between followers and following.
    # The Follow class (i.e. "follows" table) is the association table between the two.
    
    # The "follows" table has the following structure:
    # | follower_id | following_id | timestamp |

    # "following" attribute below defines one to many relationship definition between this users table and the follows table.
    # The column of "follows" table (i.e. attribute of Follow class) that is assigned by foreign_keys below (i.e. follower_id) will contain a user's primary key.
    # The primary key has to be manually told by the coder to Follow class above (i.e. the db.ForeignKey('users.id') assignment to follower_id in the Follow class above)
    # Thus follower_id column contains all users id that follow someone. The someone is defined in the following_id column.
    
    # Accessing the attribute through an instance of User returns a list of instances of the Follow class, those instances which contain users
    # that the instance is following.

    # The backref "follower" below (and also "following" backref in followers attribute), makes an attribute "follower" (and "following") available to an instance of the Follow class.
    # This "follower" attribute can be accessed (i.e. instance.follower) to get the follower (i.e. instance.follower) and the followed user (i.e. instance.following) in that instance.
    
    # "joined" argument for lazy in backref is explained here https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html#joined-eager-loading
    # Unlike other classes, the backref assignment here has an additional db.backref() so we can apply lazy = "joined" to its query
    # "Cascade" configures how actions performed on a parent object propagates to related objects
    # The "all, delete-orphan" means to use all default settings for cascade, plus a delete-orphan setting
    # The delete orphan setting is there so the association table (i.e. "follows") will delete the foreignkeys of any users that are deleted/user that unfollow another, instead of doing the default behaviour which is to set
    # the key to NULL.

    # The same principles apply to the "follower attribute"
    # Look at unit test test_follows to understand better how the following features are implemented
    following: sqlalchemy.orm.Query = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers: sqlalchemy.orm.Query = db.relationship('Follow',
                                foreign_keys=[Follow.following_id],
                                backref=db.backref('following', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    
    comments: sqlalchemy.orm.Query = db.relationship('Comment',
                                foreign_keys = [Comment.author_id],
                                backref = db.backref('author', lazy = 'joined'),
                                lazy = 'dynamic',
                                cascade = 'all, delete-orphan')

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
    
    def __repr__(self):
        return '<User %r>' % self.username
    def can(self, permission: str) -> bool:
        return self.role is not None and self.role.has_permission(permission)
    def is_administrator(self) -> bool:
        return self.can(Permission.ADMIN)
    
    @property
    def password(self):
        raise AttributeError("password is not accessible")
    @password.setter
    def password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
        # Once a password is hashed, it can never be recovered
    
    def verify_password(self, password: str) -> bool:
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
 
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(following=user)
            self.following.append(f)

    def unfollow(self, user):
        f = self.following.filter_by(following_id=user.id).first()
        if f:
            self.following.remove(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.following.filter_by(
            following_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    # The below property gets the posts of those who follow this user. 
    # We could do [[post for post in follower.posts.all()] for follower in db.session.query(User).filter_by(user = self).followers.all()]
    # but this is expensive; each iteration will interrogate the db once; in total there will be 
    # totalNoOfUsers + firstInitialCallToGetAllFollowersOfSelf calls to the db!
    
    # Better way: We combine posts and follows table, keeping only posts that are authored by users who follow someone (i.e. the argument of .join() below)
    # Then, filter that joined table based on users who follow self (i.e. the argument to .filter() below)
    # Since the query starts with .query(Post), the return value will be of type Post (i.e. only return the columns of the joined table that are in posts table)
    
    # The statement in SQL is:
    # SELECT posts.id AS posts_id, posts.body AS posts_body, posts.body_html AS posts_body_html, posts.timestamp AS posts_timestamp, posts.author_id AS posts_author_id 
    # FROM posts JOIN follows ON follows.following_id = posts.author_id
    # WHERE follows.follower_id = ?
    @property
    def following_posts(self):
        return db.session.query(Post)\
                .join(Follow, Follow.following_id == Post.author_id)\
                .filter(Follow.follower_id == self.id)

    # The token generators below are used by the API to authenticate a user
    # without a password, since sending passwords at every request is dangerous
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])
    
    def to_json(self):
        return { 
            "username": self.username,
            "role": self.role.name,
            "name": self.name,
            "location": self.location,
            "about_me": self.about_me,
            "member_since": self.member_since,
            "last_seen": self.last_seen,
            "posts_url": url_for('api.get_user_posts', id=self.id),
            "post_count": self.posts.count()
        }
    
    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('Post does not have a body')
        return Post(body=body)
    
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
    users: sqlalchemy.orm.Query = db.relationship('User', backref='role', lazy="dynamic")
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

    comments: sqlalchemy.orm.Query = db.relationship('Comment',
                                foreign_keys = [Comment.post_id],
                                backref = db.backref('post', lazy = 'joined'),
                                lazy = 'dynamic',
                                cascade = 'all, delete-orphan')

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

    def create_comment(self, author: User, body: str):
        if body == "":
            return 
        comment = Comment(author = author, post = self, body = body)
        db.session.add(comment)
        db.session.commit()
    
    def to_json(self):
        json_post = {
            "body": self.body,
            "body_html": self.body_html,
            "timestamp": self.timestamp,
            "author_url": url_for("api.get_user", id=self.author_id),
            "comments_url": url_for("api.get_post_comments", id = self.id),
            "comment_count": self.comments.count(),
            "url": url_for('api.get_post', id=self.id)
        }
        return json_post


db.event.listen(Post.body, 'set', Post.on_changed_body)
