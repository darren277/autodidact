""""""
import sys
from main import app
from models.lessons import db

def create():
    with app.app_context():
        print("ABOUT TO CREATE ALL TABLES...")
        db.create_all()

def drop():
    raise NotImplementedError


if __name__ == "__main__":
    if sys.argv[1] == "create":
        create()
    elif sys.argv[1] == "drop":
        drop()
    else:
        print("Invalid command.")
        quit(1)

