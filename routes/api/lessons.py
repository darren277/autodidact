""""""
from flask import jsonify, request, session

from routes.assistant import ask_route


def lesson_route(db, lesson_id):
    from models.lessons import Lesson
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found."}), 404
    if request.method == 'GET':
        return jsonify(lesson.json())
    elif request.method == 'PUT':
        data = request.json
        title = data.get('title', None)
        content = data.get('content', None)
        module_id = data.get('module_id', None)

        missing_fields = []

        if title: lesson.title = title
        else: missing_fields.append("title")

        if content: lesson.content = content
        else: missing_fields.append("content")

        if module_id: lesson.module_id = module_id
        else: missing_fields.append("module_id")

        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        db.session.commit()
        return jsonify({"message": "Lesson updated successfully."})
    elif request.method == 'DELETE':
        db.session.delete(lesson)
        db.session.commit()
        return jsonify({"message": "Lesson deleted successfully."})
    else:
        return jsonify({"error": "Invalid request method."}), 400


def lessons_route(db):
    from models.lessons import Lesson, Module
    if request.method == 'GET':
        lessons = Lesson.query.all()
        print("DEBUG PRINT /api/lessons:", lessons)
        return jsonify([lesson.json() for lesson in lessons])
    elif request.method == 'POST':
        data = request.json
        title = data.get('title', None)
        content = data.get('content', None)
        module_id = data.get('module_id', None)
        if not title or not content or not module_id:
            return jsonify({"error": "Missing required fields."}), 400

        # check if module exists...
        module = Module.query.get(module_id)
        if not module:
            return jsonify({"error": "Module not found."}), 400

        lesson = Lesson(title=title, content=content, module_id=module_id)

        # Optional fields: start_date, end_date...
        if data.get('start_date', None): lesson.start_date = data['start_date']
        if data.get('end_date', None): lesson.end_date = data['end_date']

        db.session.add(lesson)
        db.session.commit()
        return jsonify({"message": "Lesson added successfully."})
    else:
        return jsonify({"error": "Invalid request method."}), 400


def mark_lesson_complete_route():
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        lesson_id = data.get('lesson_id')
        percentage = data.get('percentage', 100)  # Default to 100% if not specified

        if not lesson_id:
            return jsonify({"error": "Lesson ID is required"}), 400

        # Get user from database
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Mark lesson as complete
        progress = user.mark_lesson_complete(lesson_id, percentage)

        # Get updated completion stats
        stats = user.get_completion_stats()

        return jsonify({
            "success": True,
            "message": "Lesson marked as complete",
            "new_percentage": progress.percentage_completed,
            "is_completed": progress.is_completed,
            "completion_date": progress.completion_date.isoformat() if progress.completion_date else None,
            "overall_stats": stats
        })

    except Exception as e:
        return jsonify({"error": f"Failed to mark lesson complete: {str(e)}"}), 500


def update_lesson_progress_route():
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        lesson_id = data.get('lesson_id')
        percentage = data.get('percentage', 0)
        time_spent_minutes = data.get('time_spent_minutes')

        if not lesson_id:
            return jsonify({"error": "Lesson ID is required"}), 400

        if not isinstance(percentage, (int, float)) or percentage < 0 or percentage > 100:
            return jsonify({"error": "Percentage must be a number between 0 and 100"}), 400

        # Get user from database
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update lesson progress
        progress = user.update_lesson_progress(lesson_id, percentage, time_spent_minutes)

        return jsonify({
            "success": True,
            "message": "Progress updated successfully",
            "percentage_completed": progress.percentage_completed,
            "is_completed": progress.is_completed,
            "time_spent_minutes": progress.time_spent_minutes,
            "last_accessed": progress.last_accessed.isoformat() if progress.last_accessed else None
        })

    except Exception as e:
        return jsonify({"error": f"Failed to update progress: {str(e)}"}), 500


def get_lesson_progress_route(lesson_id):
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        # Get user from database
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get progress for this lesson
        progress = user.get_lesson_progress(lesson_id)

        if progress:
            return jsonify({
                "success": True,
                "progress": progress.json()
            })
        else:
            return jsonify({
                "success": True,
                "progress": {
                    "percentage_completed": 0,
                    "is_completed": False,
                    "time_spent_minutes": 0
                }
            })

    except Exception as e:
        return jsonify({"error": f"Failed to get progress: {str(e)}"}), 500

def submit_question_route(r):
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        lesson_id = data.get('lesson_id')
        question = data.get('question', '').strip()

        if not lesson_id or not question:
            return jsonify({"error": "Lesson ID and question are required"}), 400

        # Get lesson context
        from models.lessons import Lesson
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({"error": "Lesson not found"}), 404

        # Check if user has API key configured
        from utils.api_key_manager import get_user_api_key
        user_sub = session['user']['sub']
        api_key = get_user_api_key(user_sub)

        if not api_key:
            return jsonify({"error": "No OpenAI API key configured. Please set your API key in Settings."}), 400

        # Create context-aware question
        lesson_context = f"""
    Lesson Context:
    Title: {lesson.title}
    Content: {lesson.content}
    Module: {lesson.module.title if lesson.module else 'Unknown Module'}

    User Question: {question}

    Please answer the user's question based on the lesson content above. If the question is not related to this lesson, please redirect them to ask about the current lesson material.
    """

        # Update the request data with the context-aware question
        data['question'] = lesson_context

        # Use the existing assistant system
        return ask_route(r)

    except Exception as e:
        return jsonify({"error": f"Failed to submit question: {str(e)}"}), 500

def chat_history_route(lesson_id):
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401
    from models.user import User
    user_sub = session['user']['sub']
    user = User.find_by_sub(user_sub)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if request.method == 'GET':
        chat = user.get_chat_history(lesson_id)
        if not chat:
            return jsonify({"messages": []})
        # Convert messages to the format expected by frontend
        messages = []
        for message in chat.messages:
            messages.append({
                'type': message.message_type,
                'content': message.content,
                'timestamp': message.created_at.isoformat() if message.created_at else None
            })
        return jsonify({"messages": messages})

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'type' not in data or 'content' not in data:
            return jsonify({"error": "Missing type or content in request body"}), 400
        message_type = data['type']  # 'user' or 'assistant'
        content = data['content']
        chat = user.add_chat_message(lesson_id, message_type, content)
        # Return updated messages in the format expected by frontend
        messages = []
        for message in chat.messages:
            messages.append({
                'type': message.message_type,
                'content': message.content,
                'timestamp': message.created_at.isoformat() if message.created_at else None
            })
        return jsonify({"success": True, "messages": messages})

    elif request.method == 'DELETE':
        chat = user.clear_chat_history(lesson_id)
        return jsonify({"success": True, "messages": []})

    else:
        return jsonify({"error": "Invalid request method."}), 400
