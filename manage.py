""""""
import sys
from main import app
from models.lessons import db

def create():
    with app.app_context():
        print("ABOUT TO CREATE ALL TABLES...")
        db.create_all()

def drop():
    with app.app_context():
        print("ABOUT TO DROP ALL TABLES...")
        db.drop_all()


def migrate(course_name: str):
    from utils.op2auto import export_projects

    project = export_projects(course_name)

    if project is None:
        print(f"Project not found: {course_name}")
        return



if __name__ == "__main__":
    if sys.argv[1] == "create":
        create()
    elif sys.argv[1] == "drop":
        drop()
    elif sys.argv[1] == "migrate":
        course_identifier = sys.argv[2]
        print(f"Importing course: {course_identifier}")
        migrate(course_identifier)
    else:
        print("Invalid command.")
        quit(1)

