<h1> Backend notes </h1>


## Python class definitions, corresponding SQL schema and example data of the project. For more info go to ```models.py``` in ```app``` folder.

--- 

### <h3 align="center"> ```User``` model <=> ```users``` table </h3>

```python
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
    avatar_hash = db.Column(db.String(32)) 

    posts: sqlalchemy.orm.Query = db.relationship('Post', backref = 'author', lazy = 'dynamic')
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
```

```sql
CREATE TABLE "users" (
	"id"	INTEGER NOT NULL,
	"email"	VARCHAR(64),
	"username"	VARCHAR(64),
	"role_id"	INTEGER,
	"password_hash"	VARCHAR(128),
	"confirmed"	BOOLEAN,
	"name"	VARCHAR(64),
	"location"	VARCHAR(64),
	"about_me"	TEXT,
	"member_since"	DATETIME,
	"last_seen"	DATETIME,
	"avatar_hash"	VARCHAR(32),
	PRIMARY KEY("id"),
	FOREIGN KEY("role_id") REFERENCES "roles"("id")
);
```

| id  | email                    | username       | role_id | password_hash | confirmed | name             | location     | about_me  | member_since     | last_seen        | avatar_hash |
| --- | ------------------------ | -------------- | ------- | ------------- | --------- | ---------------- | ------------ | --------- | ---------------- | ---------------- | ----------- |
| 1   | fkrause@example.net      | Dawn Payne     | 1       | pbkdf2        | 0         | joki             | jakarta      | tds       | 2022-05-28 10:16 | 2022-05-28 10:16 | ba          |
| 2   | zsingleton@example.com   | briansmith     | 1       | pbkdf5        | 1         | Nancy            | Lake         | Important | 2022-05-09 00:00 | 2022-05-28 10:20 | bd          |
| 3   | yangrichard@example.com  | gibbsgregory   | 1       | pbkdf2        | 1         | Stacey           | Ortizburgh   | Tv .      | 2022-05-07 00:00 | 2022-05-28 10:20 | 58          |
| 4   | lindaross@example.org    | santosallen    | 1       | pbkdf2        | 1         | Robin Andrews    | Lake7        | Window    | 2022-05-13 00:00 | 2022-05-28 10:20 | 12          |
| 5   | troycummings@example.com | lauraevans     | 1       | pbkdf2        | 1         | Stacey Velazquez | East         | Direction | 2022-05-18 00:00 | 2022-05-28 10:20 | d8          |
| 6   | steven66@example.net     | rosaleskristen | 1       | pbkdf2        | 1         | Margaret Berry   | Manchester   | Agree     | 2022-05-16 00:00 | 2022-05-28 10:20 | 4a          |
| 7   | browntroy@example.org    | patrickevans   | 1       | pbkdf2        | 1         | Tanya Hamilton   | Shawnchester | Fall      | 2022-05-19 00:00 | 2022-05-28 10:20 | e8          |

---
### <h3 align="center"> ```Role``` model <=> ```roles``` table </h3>

```python
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)
    users: sqlalchemy.orm.Query = db.relationship('User', backref='role', lazy="dynamic")
```

```sql
CREATE TABLE "roles" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(64),
	"default"	BOOLEAN,
	"permissions"	INTEGER,
	CONSTRAINT "uq_roles_name" UNIQUE("name"),
	UNIQUE("name"),
	PRIMARY KEY("id")
);
```

| id  | name          | default | permissions |
| --- | ------------- | ------- | ----------- |
| 1   | User          | 1       | 7           |
| 2   | Moderator     | 0       | 15          |
| 3   | Administrator | 0       | 31          |

---
### <h3 align="center"> ```Post``` model <=> ```posts``` table </h3>
```python
class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
```

```sql
CREATE TABLE "posts" (
	"id"	INTEGER NOT NULL,
	"body"	TEXT,
	"body_html"	TEXT,
	"timestamp"	DATETIME,
	"author_id"	INTEGER,
	FOREIGN KEY("author_id") REFERENCES "users"("id"),
	PRIMARY KEY("id")
);
```

| id  | body     | body_html         | timestamp        | author_id |
| --- | -------- | ----------------- | ---------------- | --------- |
| 1   | Note     | <p>Note</p>       | 2022-05-26 00:00 | 44        |
| 2   | Question | <p>Question  </p> | 2022-05-24 00:00 | 42        |
| 3   | Best     | <p>Best</p>       | 2022-05-10 00:00 | 89        |
| 4   | test     | <p>For </p>       | 2022-05-09 00:00 | 61        |
| 5   | American | <p>American.</p>  | 2022-05-07 00:00 | 97        |
| 6   | Reflect  | <p>Reflect </p>   | 2022-05-11 00:00 | 23        |
| 7   | Recent   | <p>Recent </p>    | 2022-05-22 00:00 | 1         |
| 8   | Week     | <p>Week s.</p>    | 2022-04-30 00:00 | 76        |

---

### <h3 align="center"> ```Follow``` model <=> ```follows``` table </h3>

```python
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

```sql
CREATE TABLE "follows" (
	"follower_id"	INTEGER NOT NULL,
	"timestamp"	DATETIME,
	"following_id"	INTEGER NOT NULL,
	"trigger"	TEXT,
	CONSTRAINT "fk_follows_follower_id_users" FOREIGN KEY("follower_id") REFERENCES "users"("id"),
	CONSTRAINT "fk_follows_following_id_users" FOREIGN KEY("following_id") REFERENCES "users"("id"),
	CONSTRAINT "pk_follows" PRIMARY KEY("follower_id","following_id")
);
```
| follower_id | timestamp                  | following_id |
| ----------- | -------------------------- | ------------ |
| 9           | 2022-05-31 17:40:21.156155 | 71           |
| 45          | 2022-05-31 17:26:01.773859 | 9            |
| 46          | 2022-05-31 17:26:01.777593 | 9            |
| 47          | 2022-05-31 17:26:01.778590 | 9            |
| 48          | 2022-05-31 17:26:01.779609 | 9            |
| 49          | 2022-05-31 17:26:22.756153 | 9            |
| 102         | 2022-05-31 09:13:30.798989 | 9            |
| 123         | 2022-05-28 15:14:12.237115 | 124          |
| 9           | 2022-06-01 09:29:27.525373 | 87           |

---

### Naming Convention of Constraints Followed (helpful for for Alembic migration scripts)
```json
    NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
    }
```