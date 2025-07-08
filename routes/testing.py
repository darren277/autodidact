""""""
from flask import render_template

def test_dashboard_route():
    """Simple test route to verify template rendering"""
    test_data = {
        'progress_summary': {
            'completed_lessons': 5,
            'total_lessons': 10,
            'completion_percentage': 50
        },
        'next_session': {
            'lesson_title': 'Test Lesson',
            'module_title': 'Test Module',
            'lesson_id': 1,
            'module_id': 1
        },
        'achievements': {
            'modules_completed': 2,
            'quizzes_passed': 3
        },
        'recent_activity': [
            {
                'type': 'Lesson Completed',
                'lesson_title': 'Test Lesson 1',
                'time_ago': '2 hours ago',
                'percentage': 100,
                'is_completed': True
            }
        ]
    }

    print("=== TEST DASHBOARD DEBUG ===")
    print(f"Test data: {test_data}")
    print("============================")

    return render_template('dashboard.html',
                           active_page='dashboard',
                           user={'name': 'Test User'},
                           **test_data)


def test_dashboard_minimal_route():
    """Test with minimal template"""
    test_data = {
        'progress_summary': {
            'completed_lessons': 5,
            'total_lessons': 10,
            'completion_percentage': 50
        },
        'achievements': {
            'modules_completed': 2,
            'quizzes_passed': 3
        }
    }

    return render_template('dashboard_test.html',
                           user={'name': 'Test User'},
                           **test_data)


def create_test_user_route():
    """Create the test user in the database"""
    try:
        from models.user import User

        # Create the test user that matches the session
        user = User.create_or_update(
            email="devuser@example.com",
            name="Dev User",
            sub="local-dev-user-id"
        )

        return {
            'success': True,
            'user_created': user.id,
            'message': f'User created/updated: {user.name} (ID: {user.id})'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
