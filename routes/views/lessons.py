""""""
from flask import render_template, session, jsonify

def view_lesson_route(lesson_id):
    from models.lessons import Lesson
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    # Get related lessons from the same module
    other_lessons = Lesson.query.filter_by(module_id=lesson.module_id).filter(Lesson.id != lesson.id).all()

    # Convert lesson content to markdown for display
    from utils.convert_to_markdown import convert_to_simple_markdown
    # TODO: Get structured notes from database for this lesson
    notes = convert_to_simple_markdown({"content": lesson.content})
    audio_notes = 'presentation'

    # Get user's notes and progress for this lesson if authenticated
    user_notes = ""
    user_has_api_key = False
    user_progress = {'completed': False, 'percentage': 0}
    if 'user' in session:
        try:
            from models.user import User
            from models.lessons import Notes
            user_sub = session['user']['sub']
            user = User.find_by_sub(user_sub)
            if user:
                # Check for user notes
                notes_obj = Notes.query.filter_by(
                    lesson_id=lesson_id,
                    user_id=user.id
                ).first()
                if notes_obj:
                    user_notes = notes_obj.content

                # Check for API key status
                user_has_api_key = bool(user.encrypted_api_key)

                # Get user progress for this lesson
                progress = user.get_lesson_progress(lesson_id)
                if progress:
                    user_progress = {
                        'completed': progress.is_completed,
                        'percentage': progress.percentage_completed,
                        'time_spent_minutes': progress.time_spent_minutes,
                        'last_accessed': progress.last_accessed.isoformat() if progress.last_accessed else None
                    }
        except Exception as e:
            print(f"Error loading user data: {e}")

    # Create user object with API key status
    user_data = session.get('user', {})
    if user_data:
        user_data = user_data.copy()
        user_data['has_api_key'] = user_has_api_key

    return render_template(
        'lessons/view.html',
        lesson=lesson,  # Pass the actual lesson object
        user_progress=user_progress,
        other_lessons=other_lessons,
        user_notes=user_notes,
        audio_notes=audio_notes,
        user=user_data  # Add user to template context
    )


def preview_lesson_route(lesson_id):
    # Basically, "view_lesson" but as instructor, not student...
    from models.lessons import Lesson
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    # Check for API key status
    user_has_api_key = False
    if 'user' in session:
        try:
            from models.user import User
            user_sub = session['user']['sub']
            user = User.find_by_sub(user_sub)
            if user:
                user_has_api_key = bool(user.encrypted_api_key)
        except Exception as e:
            print(f"Error loading user data: {e}")

    # Create user object with API key status
    user_data = session.get('user', {})
    if user_data:
        user_data = user_data.copy()
        user_data['has_api_key'] = user_has_api_key

    # Create lesson data structure for template (same as view_lesson)
    lesson_data = {
        'id': lesson.id,
        'title': lesson.title,
        'content': lesson.content,
        'content_html': lesson.content,  # TODO: Convert to HTML if needed
        'examples_html': lesson.examples or '',  # Use examples field from model
        'exercises_html': lesson.exercises or '',  # Use exercises field from model
        'learning_objectives': lesson.get_learning_objectives(),
        'estimated_time': {
            'hours': lesson.estimated_time_hours,
            'minutes': lesson.estimated_time_minutes
        },
        'difficulty': lesson.difficulty,
        'tags': lesson.get_tags(),
        'attachments': lesson.get_attachments(),
        'overview': lesson.overview,
        'module_id': lesson.module_id,
        'module_title': lesson.module.title if lesson.module else 'Unknown Module',
        'user_progress': {'completed': False, 'percentage': 0}  # TODO: Implement progress tracking
    }

    return render_template('lessons/preview.html', lesson=lesson_data, user=user_data)

