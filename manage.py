#!/usr/bin/env python3
"""
Database management script for the autodidact application.
"""
import psycopg2
from flask import Flask
from database import db
from models.lessons import Lesson, Module, Course, Notes, Quiz, Media, Chat, Message
from models.user import User
from settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASS, POSTGRES_DB, MASTER_ENCRYPTION_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_database():
    ISOLATION_LEVEL_AUTOCOMMIT = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
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

#@app.cli.command()
def create_tables():
    """Create all database tables."""
    with app.app_context():
        db.create_all()
    print("All tables created successfully!")

#@app.cli.command()
def create_user_progress_table():
    """Create the UserProgress table specifically."""
    from models.lessons import UserProgress
    with app.app_context():
        UserProgress.__table__.create(db.engine, checkfirst=True)
    print("UserProgress table created successfully!")

def drop_tables():
    """Drop all database tables."""
    with app.app_context():
        try:
            # Drop tables in reverse dependency order to avoid foreign key issues
            # Or use CASCADE to force drop all dependent objects
            
            # Method 1: Drop with CASCADE (PostgreSQL specific)
            db.session.execute(db.text("DROP SCHEMA public CASCADE"))
            db.session.execute(db.text("CREATE SCHEMA public"))
            db.session.execute(db.text(f"GRANT ALL ON SCHEMA public TO {POSTGRES_USER}"))
            db.session.execute(db.text("GRANT ALL ON SCHEMA public TO public"))
            db.session.commit()
            print("All tables dropped successfully using CASCADE!")
            
        except Exception as e:
            print(f"Error dropping tables: {e}")
            # Fallback: Try dropping individual tables in dependency order
            try:
                print("Trying alternative drop method...")
                
                # Drop tables in dependency order (children first, then parents)
                tables_to_drop = [
                    'message',           # Depends on chat
                    'chat',              # Depends on user, lesson
                    'user_progress',     # Depends on user, lesson
                    'notes',             # Depends on user, lesson
                    'quiz',              # Depends on lesson
                    'media',             # Depends on lesson
                    'lesson',            # Depends on module
                    'module',            # Depends on course
                    'course',            # No dependencies
                    'user'               # No dependencies
                ]
                
                for table in tables_to_drop:
                    try:
                        db.session.execute(db.text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                        print(f"Dropped table: {table}")
                    except Exception as table_error:
                        print(f"Warning: Could not drop table {table}: {table_error}")
                
                db.session.commit()
                print("All tables dropped successfully using individual drops!")
                
            except Exception as fallback_error:
                print(f"Fallback drop method also failed: {fallback_error}")
                print("You may need to manually drop tables or use database management tools.")
                raise

def seed_example_data():
    """Seed the database with example data."""
    with app.app_context():
        # Create test user
        test_user = User.create_or_update(
            email="test@example.com",
            name="Test User",
            sub="test-user-123"
        )
        
        # Add a test API key (you should replace this with a real one for testing)
        test_api_key = "sk-test-key-for-development-only"
        test_user.set_api_key(test_api_key, MASTER_ENCRYPTION_KEY)
        
        print(f"Created test user: {test_user.email}")
        print("Note: Test user has a placeholder API key. Replace with a real key for actual testing.")
        
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

def migrate_chat_history():
    """Migrate from old ChatHistory model to new Chat and Message models."""
    with app.app_context():
        try:
            # Check if old chat_history table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'chat_history' in existing_tables:
                print("Found old chat_history table. Starting migration...")
                
                # Get all old chat history records
                old_chat_histories = db.session.execute(
                    db.text("SELECT id, user_id, lesson_id, messages, created_at, updated_at FROM chat_history")
                ).fetchall()
                
                print(f"Found {len(old_chat_histories)} old chat history records to migrate.")
                
                for old_record in old_chat_histories:
                    try:
                        # Parse the old JSON messages
                        import json
                        old_messages = json.loads(old_record.messages) if old_record.messages else []
                        
                        # Create new Chat record
                        new_chat = Chat(
                            user_id=old_record.user_id,
                            lesson_id=old_record.lesson_id,
                            created_at=old_record.created_at,
                            updated_at=old_record.updated_at
                        )
                        db.session.add(new_chat)
                        db.session.flush()  # Get the new chat ID
                        
                        # Create Message records for each message
                        for msg_data in old_messages:
                            if isinstance(msg_data, dict) and 'type' in msg_data and 'content' in msg_data:
                                # Extract timestamp if available, otherwise use chat created_at
                                timestamp = msg_data.get('timestamp')
                                if timestamp:
                                    try:
                                        from datetime import datetime
                                        created_at = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    except:
                                        created_at = old_record.created_at
                                else:
                                    created_at = old_record.created_at
                                
                                new_message = Message(
                                    chat_id=new_chat.id,
                                    message_type=msg_data['type'],
                                    content=msg_data['content'],
                                    created_at=created_at
                                )
                                db.session.add(new_message)
                        
                        print(f"Migrated chat history for user {old_record.user_id}, lesson {old_record.lesson_id}")
                        
                    except Exception as e:
                        print(f"Error migrating chat history record {old_record.id}: {e}")
                        db.session.rollback()
                        continue
                
                # Commit all migrations
                db.session.commit()
                print("Migration completed successfully!")
                
                # Drop the old table
                print("Dropping old chat_history table...")
                db.session.execute(db.text("DROP TABLE chat_history CASCADE"))
                db.session.commit()
                print("Old chat_history table dropped successfully!")
                
            else:
                print("No old chat_history table found. Migration not needed.")
                
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
            raise

def create_chat_tables():
    """Create the Chat and Message tables specifically."""
    with app.app_context():
        Chat.__table__.create(db.engine, checkfirst=True)
        Message.__table__.create(db.engine, checkfirst=True)
    print("Chat and Message tables created successfully!")

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
        
        print("\n=== CHATS ===")
        chats = Chat.query.all()
        for chat in chats:
            print(f"ID: {chat.id}, User ID: {chat.user_id}, Lesson ID: {chat.lesson_id}, Messages: {len(chat.messages)}")
        
        print("\n=== MESSAGES ===")
        messages = Message.query.all()
        for message in messages:
            print(f"ID: {message.id}, Chat ID: {message.chat_id}, Type: {message.message_type}, Content: {message.content[:50]}...")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("Commands:")
        print("  create_tables - Create all database tables")
        print("  create_chat_tables - Create Chat and Message tables specifically")
        print("  drop_tables - Drop all database tables")
        print("  seed_data - Seed database with example data")
        print("  show_tables - Show all tables and their contents")
        print("  migrate_chat_history - Migrate from old ChatHistory to new Chat/Message models")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create_database':
        create_database()
    elif command == 'create_tables':
        create_tables()
        create_user_progress_table()
        create_chat_tables()
    elif command == 'create_chat_tables':
        create_chat_tables()
    elif command == 'drop_tables':
        drop_tables()
    elif command == 'seed_data':
        seed_example_data()
    elif command == 'show_tables':
        show_tables()
    elif command == 'migrate_chat_history':
        migrate_chat_history()
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

