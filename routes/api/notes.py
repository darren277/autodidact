""""""
from flask import request, jsonify, session


def save_notes_route(db):
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        lesson_id = data.get('lesson_id')
        content = data.get('content', '').strip()

        if not lesson_id:
            return jsonify({"error": "Lesson ID is required"}), 400

        # Get user from database
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check if notes already exist for this user and lesson
        from models.lessons import Notes
        existing_notes = Notes.query.filter_by(
            lesson_id=lesson_id,
            user_id=user.id
        ).first()

        if existing_notes:
            # Update existing notes
            existing_notes.content = content
        else:
            # Create new notes
            new_notes = Notes(
                content=content,
                lesson_id=lesson_id,
                user_id=user.id
            )
            db.session.add(new_notes)

        db.session.commit()

        return jsonify({"success": True, "message": "Notes saved successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save notes: {str(e)}"}), 500

def get_notes_route(db, lesson_id):
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        # Get user from database
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get notes for this user and lesson
        from models.lessons import Notes
        notes = Notes.query.filter_by(
            lesson_id=lesson_id,
            user_id=user.id
        ).first()

        if notes:
            return jsonify({
                "success": True,
                "content": notes.content
            })
        else:
            return jsonify({
                "success": True,
                "content": ""
            })

    except Exception as e:
        return jsonify({"error": f"Failed to get notes: {str(e)}"}), 500
