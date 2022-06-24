'''
Edit the script and config.py to make sure customdb config option has the correct sqlalchemy uri
Usage: example.py [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  --count                No of users/posts to add
  --help                 Show this message and exit.

Commands:
  fakeposts
  fakeusers
'''
from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
import click, os, sys

parentdir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
currentdir =  os.path.abspath(os.getcwd())
sys.path.append(parentdir)
sys.path.append(currentdir)

from app.models import User, Post
from config import config

from app import create_app, db

app = create_app("customdb")
app_context = app.app_context()
app_context.push()
# To use these fakers, simply call users() or posts() or other fakers

@click.group()
def main():
    pass

@main.command()
@click.option("--count", required = True)
def fakeusers(count=10):
    count = int(count)
    print(f"Creating {str(count)} fake users...")
    fake = Faker()
    i = 0
    while i < count:
        u = User(email = fake.email(),
                 username = fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
        print(f"Users added")
        # IntegrityError occurs if the email or username to be added already
        # exists. If so, it will retry generating another fake email.

@main.command()
@click.option("--count", required = True)
# Create fake post, and assign it to a random user
def fakeposts(count=10):
    count = int(count)
    print(f"Creating {str(count)} fake posts...")
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = db.session.query(User).offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()
    print("Posts added")

if __name__ == '__main__':
    main()