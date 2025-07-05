#!/usr/bin/env python3
"""
Utility script to create a sample course in the database.
Run this script to add a test course if none exist.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from models.lessons import Course
import json

def create_sample_course():
    """Create a sample course for testing"""
    with app.app_context():
        # Check if any courses exist
        existing_courses = Course.query.all()
        if existing_courses:
            print(f"Found {len(existing_courses)} existing courses:")
            for course in existing_courses:
                print(f"  - {course.title} (ID: {course.id})")
            return
        
        # Create a sample course
        sample_course = Course(
            title="Introduction to Computer Science",
            description="A comprehensive introduction to computer science fundamentals including programming, algorithms, and data structures.",
            overview="This course provides a solid foundation in computer science concepts. Students will learn programming basics, understand algorithms, and explore data structures through hands-on projects.",
            objectives=json.dumps([
                "Understand fundamental programming concepts",
                "Learn basic algorithms and data structures",
                "Develop problem-solving skills",
                "Gain experience with real-world programming projects"
            ]),
            prerequisites=json.dumps([
                "Basic mathematics knowledge",
                "Familiarity with using a computer",
                "No prior programming experience required"
            ]),
            published=True
        )
        
        try:
            db.session.add(sample_course)
            db.session.commit()
            print(f"✅ Successfully created sample course: '{sample_course.title}' (ID: {sample_course.id})")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample course: {e}")

if __name__ == "__main__":
    create_sample_course() 