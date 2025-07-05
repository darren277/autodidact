#!/usr/bin/env python3
"""
Test script for user progress tracking functionality
"""

from main import app
from database import db
from models.user import User
from models.lessons import Lesson, Module, UserProgress

def test_progress_tracking():
    """Test the progress tracking functionality"""
    
    with app.app_context():
        # Create test data
        print("Creating test data...")
        
        # Create a test module
        module = Module(title="Test Module")
        db.session.add(module)
        db.session.commit()
        
        # Create test lessons
        lesson1 = Lesson(title="Lesson 1", content="Content for lesson 1", module_id=module.id)
        lesson2 = Lesson(title="Lesson 2", content="Content for lesson 2", module_id=module.id)
        lesson3 = Lesson(title="Lesson 3", content="Content for lesson 3", module_id=module.id)
        
        db.session.add_all([lesson1, lesson2, lesson3])
        db.session.commit()
        
        # Create a test user
        user = User.create_or_update(
            email="test@example.com",
            name="Test User",
            sub="test-user-sub"
        )
        
        print(f"Created user: {user.name} (ID: {user.id})")
        print(f"Created lessons: {lesson1.title}, {lesson2.title}, {lesson3.title}")
        
        # Test progress tracking
        print("\n--- Testing Progress Tracking ---")
        
        # Test 1: Get or create progress
        progress1 = user.get_or_create_lesson_progress(lesson1.id)
        print(f"Progress for {lesson1.title}: {progress1.percentage_completed}% completed")
        
        # Test 2: Update progress
        user.update_lesson_progress(lesson1.id, 50, time_spent_minutes=15)
        progress1 = user.get_lesson_progress(lesson1.id)
        print(f"Updated progress for {lesson1.title}: {progress1.percentage_completed}% completed, {progress1.time_spent_minutes} minutes spent")
        
        # Test 3: Mark lesson as complete
        user.mark_lesson_complete(lesson2.id)
        progress2 = user.get_lesson_progress(lesson2.id)
        print(f"Completed {lesson2.title}: {progress2.is_completed}, {progress2.percentage_completed}%")
        
        # Test 4: Get completion stats
        stats = user.get_completion_stats()
        print(f"Overall stats: {stats['completed_lessons']}/{stats['total_lessons']} lessons completed ({stats['completion_percentage']}%)")
        
        # Test 5: Get all progress
        all_progress = user.get_all_progress()
        print(f"Total progress records: {len(all_progress)}")
        
        # Test 6: Get completed lessons
        completed = user.get_completed_lessons()
        print(f"Completed lessons: {[p.lesson.title for p in completed]}")
        
        print("\n--- Progress Tracking Test Complete ---")
        
        # Clean up test data
        print("\nCleaning up test data...")
        db.session.delete(user)
        db.session.delete(lesson1)
        db.session.delete(lesson2)
        db.session.delete(lesson3)
        db.session.delete(module)
        db.session.commit()
        print("Test data cleaned up!")

if __name__ == "__main__":
    test_progress_tracking() 