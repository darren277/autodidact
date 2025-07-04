#!/usr/bin/env python3
"""
Database management script for the autodidact application.
"""

from flask import Flask
from database import db
from models.lessons import Lesson, Module, Course, Notes, Quiz, Media
from models.user import User
from settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASS, POSTGRES_DB

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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

def create_tables():
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def drop_tables():
    """Drop all database tables."""
    with app.app_context():
        db.drop_all()
        print("Database tables dropped successfully!")

def seed_example_data():
    """Seed the database with example data."""
    with app.app_context():
        # Create a sample course
        course = Course(title="Introduction to Programming")
        db.session.add(course)
        db.session.commit()
        
        # Create a sample module
        module = Module(title="Python Basics", course_id=course.id)
        db.session.add(module)
        db.session.commit()
        
        # Create sample lessons
        lessons = [
            Lesson(
                title="Variables and Data Types",
                content="Learn about variables, strings, integers, and other data types in Python. Variables are containers for storing data values. In Python, you don't need to declare the type of a variable - Python automatically determines the type based on the value you assign.",
                module_id=module.id,
                estimated_time_hours=0,
                estimated_time_minutes=30,
                difficulty="beginner",
                tags='["Python", "Variables", "Data Types"]',
                learning_objectives='["Understand what variables are", "Learn about different data types", "Practice creating and using variables"]',
                examples="```python\n# String variable\nname = 'John'\n\n# Integer variable\nage = 25\n\n# Float variable\nheight = 5.9\n\n# Boolean variable\nis_student = True\n```",
                exercises="1. Create a variable called 'city' and assign it the value 'New York'\n2. Create a variable called 'population' and assign it the value 8336817\n3. Print both variables using the print() function",
                overview="This lesson introduces the fundamental concept of variables and the basic data types in Python."
            ),
            Lesson(
                title="Control Flow",
                content="Understand if statements, loops, and control structures. Control flow determines the order in which your program's code executes. Python provides several control flow statements including if/elif/else, for loops, and while loops.",
                module_id=module.id,
                estimated_time_hours=0,
                estimated_time_minutes=45,
                difficulty="beginner",
                tags='["Python", "Control Flow", "Loops", "Conditionals"]',
                learning_objectives='["Understand if/elif/else statements", "Learn about for and while loops", "Practice writing conditional logic"]',
                examples="```python\n# If statement\nif age >= 18:\n    print('Adult')\nelif age >= 13:\n    print('Teenager')\nelse:\n    print('Child')\n\n# For loop\nfor i in range(5):\n    print(i)\n```",
                exercises="1. Write a program that checks if a number is positive, negative, or zero\n2. Create a loop that prints the first 10 even numbers\n3. Write a program that finds the largest number in a list",
                overview="This lesson covers the essential control flow structures that allow you to make decisions and repeat code in Python."
            ),
            Lesson(
                title="Functions",
                content="Learn how to define and use functions in Python. Functions are reusable blocks of code that perform a specific task. They help organize code, make it more readable, and avoid repetition.",
                module_id=module.id,
                estimated_time_hours=1,
                estimated_time_minutes=0,
                difficulty="intermediate",
                tags='["Python", "Functions", "Code Organization"]',
                learning_objectives='["Define and call functions", "Understand parameters and return values", "Learn about scope and local variables"]',
                examples="```python\n# Simple function\ndef greet(name):\n    return f'Hello, {name}!'\n\n# Function with multiple parameters\ndef add_numbers(a, b):\n    return a + b\n\n# Function with default parameters\ndef greet_with_title(name, title='Mr.'):\n    return f'Hello, {title} {name}!'\n```",
                exercises="1. Create a function that calculates the area of a circle\n2. Write a function that checks if a number is prime\n3. Create a function that reverses a string",
                overview="This lesson teaches you how to create and use functions to organize and reuse your code effectively."
            )
        ]
        
        for lesson in lessons:
            db.session.add(lesson)
        
        db.session.commit()
        print("Example data seeded successfully!")

def migrate(course_name: str):
    from utils.op2auto import export_project

    project = export_project(course_name)

    if project is None:
        print(f"Project not found: {course_name}")
        return

def show_tables():
    """Show all tables and their contents."""
    with app.app_context():
        print("\n=== COURSES ===")
        courses = Course.query.all()
        for course in courses:
            print(f"ID: {course.id}, Title: {course.title}")
        
        print("\n=== MODULES ===")
        modules = Module.query.all()
        for module in modules:
            print(f"ID: {module.id}, Title: {module.title}, Course ID: {module.course_id}")
        
        print("\n=== LESSONS ===")
        lessons = Lesson.query.all()
        for lesson in lessons:
            print(f"ID: {lesson.id}, Title: {lesson.title}, Module ID: {lesson.module_id}")
        
        print("\n=== USERS ===")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Name: {user.name}")
        
        print("\n=== NOTES ===")
        notes = Notes.query.all()
        for note in notes:
            print(f"ID: {note.id}, Lesson ID: {note.lesson_id}, User ID: {note.user_id}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("Commands:")
        print("  create_tables - Create all database tables")
        print("  drop_tables - Drop all database tables")
        print("  seed_data - Seed database with example data")
        print("  show_tables - Show all tables and their contents")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create_database':
        create_database()
    elif command == 'create_tables':
        create_tables()
    elif command == 'drop_tables':
        drop_tables()
    elif command == 'seed_data':
        seed_example_data()
    elif command == 'show_tables':
        show_tables()
    elif sys.argv[1] == "migrate":
        if len(sys.argv) < 3:
            print("Usage: python manage.py migrate <course_name>")
            sys.exit(1)
        course_identifier = sys.argv[2]
        print(f"Importing course: {course_identifier}")
        migrate(course_identifier)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

