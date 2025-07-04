#!/usr/bin/env python3
"""
Test script for dashboard functionality
"""

from main import app
from database import db
from models.user import User
from models.lessons import Lesson, Module, Course, UserProgress
from datetime import datetime, timedelta

def test_dashboard():
    """Test the dashboard functionality"""
    
    with app.app_context():
        print("Creating test data for dashboard...")
        
        # Create a test course
        course = Course(title="Test Course")
        db.session.add(course)
        db.session.commit()
        
        # Create test modules
        module1 = Module(title="Module 1: Basics", course_id=course.id)
        module2 = Module(title="Module 2: Advanced", course_id=course.id)
        db.session.add_all([module1, module2])
        db.session.commit()
        
        # Create test lessons
        lessons = [
            Lesson(title="Lesson 1: Introduction", content="Introduction content", module_id=module1.id),
            Lesson(title="Lesson 2: Variables", content="Variables content", module_id=module1.id),
            Lesson(title="Lesson 3: Functions", content="Functions content", module_id=module1.id),
            Lesson(title="Lesson 4: Advanced Topics", content="Advanced content", module_id=module2.id),
            Lesson(title="Lesson 5: Final Project", content="Project content", module_id=module2.id),
        ]
        
        db.session.add_all(lessons)
        db.session.commit()
        
        # Create a test user
        user = User.create_or_update(
            email="dashboard-test@example.com",
            name="Dashboard Test User",
            sub="dashboard-test-sub"
        )
        
        print(f"Created user: {user.name}")
        print(f"Created {len(lessons)} lessons across {len([module1, module2])} modules")
        
        # Simulate user progress
        print("\n--- Simulating User Progress ---")
        
        # Complete first lesson
        user.mark_lesson_complete(lessons[0].id)
        print(f"Completed: {lessons[0].title}")
        
        # Partially complete second lesson
        user.update_lesson_progress(lessons[1].id, 60, time_spent_minutes=20)
        print(f"In progress: {lessons[1].title} (60%)")
        
        # Complete third lesson
        user.mark_lesson_complete(lessons[2].id)
        print(f"Completed: {lessons[2].title}")
        
        # Start fourth lesson
        user.update_lesson_progress(lessons[3].id, 25, time_spent_minutes=10)
        print(f"Started: {lessons[3].title} (25%)")
        
        # Test dashboard data
        print("\n--- Testing Dashboard Data ---")
        
        # Get completion stats
        stats = user.get_completion_stats()
        print(f"Completion stats: {stats['completed_lessons']}/{stats['total_lessons']} lessons ({stats['completion_percentage']}%)")
        
        # Get next recommended lesson
        next_lesson = user.get_next_recommended_lesson()
        print(f"Next recommended lesson: {next_lesson.title if next_lesson else 'None'}")
        
        # Get recent activity
        recent_activity = UserProgress.query.filter_by(user_id=user.id).order_by(UserProgress.updated_at.desc()).limit(5).all()
        print(f"Recent activity: {len(recent_activity)} records")
        
        # Count completed modules
        completed_modules = set()
        for progress in user.progress_records:
            if progress.is_completed and progress.lesson.module:
                completed_modules.add(progress.lesson.module.id)
        print(f"Completed modules: {len(completed_modules)}")
        
        print("\n--- Dashboard Test Complete ---")
        print("You can now visit the dashboard to see the real data!")
        
        # Don't clean up - let the user see the data in the dashboard
        print("Test data preserved for dashboard viewing.")

if __name__ == '__main__':
    test_dashboard() 