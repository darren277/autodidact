#!/usr/bin/env python3
"""
Utility script to create sample lessons in the database.
Run this script to add test lessons if none exist.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from models.lessons import Lesson, Module
import json

def create_sample_lessons():
    """Create sample lessons for testing"""
    with app.app_context():
        # Check if any modules exist
        modules = Module.query.all()
        if not modules:
            print("❌ No modules found. Please create a module first.")
            return
        
        # Check if any lessons exist
        existing_lessons = Lesson.query.all()
        if existing_lessons:
            print(f"Found {len(existing_lessons)} existing lessons:")
            for lesson in existing_lessons:
                print(f"  - {lesson.title} (Module: {lesson.module.title if lesson.module else 'None'})")
            return
        
        # Create sample lessons for the first module
        module = modules[0]
        print(f"Creating sample lessons for module: {module.title}")
        
        sample_lessons = [
            {
                "title": "Introduction to Programming",
                "content": "This lesson introduces the fundamental concepts of programming including variables, data types, and basic syntax.",
                "overview": "Learn the basics of programming and understand how to write your first program.",
                "estimated_time_hours": 1,
                "estimated_time_minutes": 30,
                "difficulty": "beginner",
                "order": 1
            },
            {
                "title": "Variables and Data Types",
                "content": "Explore different types of variables and how to use them effectively in your programs.",
                "overview": "Master the concept of variables and understand different data types.",
                "estimated_time_hours": 1,
                "estimated_time_minutes": 0,
                "difficulty": "beginner",
                "order": 2
            },
            {
                "title": "Control Structures",
                "content": "Learn about if statements, loops, and other control structures that make your programs dynamic.",
                "overview": "Understand how to control the flow of your programs using conditional statements and loops.",
                "estimated_time_hours": 1,
                "estimated_time_minutes": 45,
                "difficulty": "intermediate",
                "order": 3
            }
        ]
        
        created_lessons = []
        for lesson_data in sample_lessons:
            lesson = Lesson(
                title=lesson_data["title"],
                content=lesson_data["content"],
                overview=lesson_data["overview"],
                estimated_time_hours=lesson_data["estimated_time_hours"],
                estimated_time_minutes=lesson_data["estimated_time_minutes"],
                difficulty=lesson_data["difficulty"],
                order=lesson_data["order"],
                module_id=module.id,
                published=True
            )
            
            try:
                db.session.add(lesson)
                created_lessons.append(lesson)
            except Exception as e:
                print(f"❌ Error creating lesson '{lesson_data['title']}': {e}")
        
        try:
            db.session.commit()
            print(f"✅ Successfully created {len(created_lessons)} sample lessons:")
            for lesson in created_lessons:
                print(f"  - {lesson.title} (ID: {lesson.id})")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error saving lessons: {e}")

if __name__ == "__main__":
    create_sample_lessons() 