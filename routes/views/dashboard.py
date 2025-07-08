""""""
from flask import session, redirect, url_for, render_template, request, jsonify

def dashboard_route():
    # Debug: Check session contents
    print("=== SESSION DEBUG ===")
    print(f"Session keys: {list(session.keys())}")
    print(f"Session user: {session.get('user', 'NOT FOUND')}")
    print(f"Session modified flag: {session.modified}")
    print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'No session ID'}")
    print("====================")

    # Check if user is logged in
    if 'user' not in session:
        # Redirect to login if not authenticated
        return redirect(url_for('login'))

    user = session['user']

    # Initialize dashboard data with defaults
    dashboard_data = {
        'progress_summary': {
            'completed_lessons': 0,
            'total_lessons': 0,
            'completion_percentage': 0
        },
        'next_session': None,
        'achievements': {
            'modules_completed': 0,
            'quizzes_passed': 0
        },
        'recent_activity': []
    }

    if user:
        try:
            from models.user import User
            from models.lessons import Lesson, Module, UserProgress
            from datetime import datetime, timedelta

            print(f"Looking for user with sub: {user['sub']}")

            # Get user from database
            user_obj = User.find_by_sub(user['sub'])
            print(f"User object found: {user_obj}")

            if user_obj:
                # Get completion statistics
                stats = user_obj.get_completion_stats()
                dashboard_data['progress_summary'] = {
                    'completed_lessons': stats['completed_lessons'],
                    'total_lessons': stats['total_lessons'],
                    'completion_percentage': stats['completion_percentage']
                }

                # Find next session (recommended lesson)
                next_lesson = user_obj.get_next_recommended_lesson()
                if next_lesson:
                    module = next_lesson.module if next_lesson.module else None

                    # Get progress for this lesson if it exists
                    progress = user_obj.get_lesson_progress(next_lesson.id)

                    dashboard_data['next_session'] = {
                        'lesson_title': next_lesson.title,
                        'module_title': module.title if module else 'Unknown Module',
                        'last_accessed': progress.last_accessed if progress else None,
                        'lesson_id': next_lesson.id,
                        'module_id': module.id if module else None
                    }

                # Count completed modules
                completed_modules = set()
                for progress in user_obj.progress_records:
                    if progress.is_completed and progress.lesson.module:
                        completed_modules.add(progress.lesson.module.id)

                dashboard_data['achievements']['modules_completed'] = len(completed_modules)

                # Get recent activity (last 10 progress updates)
                recent_activity = UserProgress.query.filter_by(
                    user_id=user_obj.id
                ).order_by(UserProgress.updated_at.desc()).limit(10).all()

                for progress in recent_activity:
                    lesson = progress.lesson
                    activity_type = "Lesson Completed" if progress.is_completed else "Progress Updated"
                    activity_time = progress.updated_at

                    # Format time ago
                    time_diff = datetime.utcnow() - activity_time
                    if time_diff.days > 0:
                        time_ago = f"{time_diff.days} day{'s' if time_diff.days != 1 else ''} ago"
                    elif time_diff.seconds > 3600:
                        hours = time_diff.seconds // 3600
                        time_ago = f"{hours} hour{'s' if hours != 1 else ''} ago"
                    else:
                        minutes = time_diff.seconds // 60
                        time_ago = f"{minutes} minute{'s' if minutes != 1 else ''} ago"

                    dashboard_data['recent_activity'].append({
                        'type': activity_type,
                        'lesson_title': lesson.title,
                        'time_ago': time_ago,
                        'percentage': progress.percentage_completed,
                        'is_completed': progress.is_completed
                    })

        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            # Keep default values if there's an error

    # Debug: Print what we're passing to template
    print("=== DASHBOARD DEBUG ===")
    print(f"User: {user}")
    print(f"Progress summary: {dashboard_data['progress_summary']}")
    print(f"Next session: {dashboard_data['next_session']}")
    print(f"Achievements: {dashboard_data['achievements']}")
    print(f"Recent activity: {dashboard_data['recent_activity']}")
    print("=======================")

    # Try passing variables as a single dictionary first
    template_vars = {
        'active_page': 'dashboard',
        'user': user,
        'progress_summary': dashboard_data['progress_summary'],
        'next_session': dashboard_data['next_session'],
        'achievements': dashboard_data['achievements'],
        'recent_activity': dashboard_data['recent_activity']
    }

    print("=== TEMPLATE VARS ===")
    print(f"Template vars: {template_vars}")
    print("====================")

    try:
        return render_template('dashboard.html', **template_vars)
    except Exception as e:
        print(f"Template rendering error: {e}")
        # Fallback to simple template
        return f"Dashboard error: {e}", 500


def toggle_mode_route():
    print(f"DEBUG: toggle_mode called")
    print(f"DEBUG: Session: {session}")
    print(f"DEBUG: Request headers: {dict(request.headers)}")
    print(f"DEBUG: Request data: {request.get_data()}")

    if 'user' not in session:
        print("DEBUG: No user in session")
        return jsonify({"error": "User not authenticated"}), 401

    try:
        data = request.get_json()
        print(f"DEBUG: Parsed JSON data: {data}")

        if data and 'mode' in data:
            new_mode = data['mode']
            print(f"DEBUG: Switching to mode: {new_mode}")
            print(f"DEBUG: Session before change: {session}")
            if new_mode in ['student', 'teacher']:
                session['user']['mode'] = new_mode
                session.modified = True  # Mark session as modified
                print(f"DEBUG: Session after change: {session}")
                print(f"DEBUG: Session modified flag: {session.modified}")
                print(f"DEBUG: Mode updated in session: {session['user']['mode']}")
                return jsonify({"message": "Mode toggled successfully", "mode": new_mode})
            else:
                print(f"DEBUG: Invalid mode: {new_mode}")
                return jsonify({"error": "Invalid mode"}), 400
        else:
            # Fallback to toggle behavior if no mode specified
            current_mode = session['user']['mode']
            print(f"DEBUG: No mode specified, toggling from: {current_mode}")
            if current_mode == 'student':
                session['user']['mode'] = 'teacher'
            else:
                session['user']['mode'] = 'student'
            session.modified = True  # Mark session as modified
            print(f"DEBUG: Mode toggled to: {session['user']['mode']}")
            return jsonify({"message": "Mode toggled successfully", "mode": session['user']['mode']})
    except Exception as e:
        print(f"DEBUG: Exception in toggle_mode: {e}")
        return jsonify({"error": str(e)}), 500
