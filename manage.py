""""""
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from main import app
from models.lessons import db
from settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASS, POSTGRES_DB

def create():
    with app.app_context():
        print("ABOUT TO CREATE ALL TABLES...")
        db.create_all()

def drop():
    with app.app_context():
        print("ABOUT TO DROP ALL TABLES...")
        db.drop_all()

def create_database():
    """Create the database if it doesn't already exist"""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASS,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (POSTGRES_DB,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{POSTGRES_DB}'...")
            cursor.execute(f'CREATE DATABASE "{POSTGRES_DB}"')
            print(f"Database '{POSTGRES_DB}' created successfully!")
        else:
            print(f"Database '{POSTGRES_DB}' already exists.")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

def migrate(course_name: str):
    from utils.op2auto import export_project

    project = export_project(course_name)

    if project is None:
        print(f"Project not found: {course_name}")
        return

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("Commands: create, drop, migrate <course_name>, create_db")
        sys.exit(1)
        
    if sys.argv[1] == "create":
        create()
    elif sys.argv[1] == "drop":
        drop()
    elif sys.argv[1] == "create_db":
        create_database()
    elif sys.argv[1] == "migrate":
        if len(sys.argv) < 3:
            print("Usage: python manage.py migrate <course_name>")
            sys.exit(1)
        course_identifier = sys.argv[2]
        print(f"Importing course: {course_identifier}")
        migrate(course_identifier)
    else:
        print("Invalid command.")
        print("Available commands: create, drop, migrate <course_name>, create_db")
        sys.exit(1)

