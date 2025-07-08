""""""
from flask import request, jsonify, session, redirect, render_template
from settings import MASTER_ENCRYPTION_KEY

def settings_route(db):
    if 'user' not in session:
        return redirect('/')

    # Import User model here to avoid circular imports
    from models.user import User

    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400

            # Google Calendar connect/reset logic
            google_action = data.get('google_action')
            user_sub = session['user']['sub']
            user = User.find_by_sub(user_sub)
            if not user:
                user = User.create_or_update(
                    email=session['user']['email'],
                    name=session['user']['name'],
                    sub=user_sub
                )

            if google_action == 'connect_google_calendar':
                from lib.apis.google_agenda import get_or_create_app_calendar
                try:
                    calendar_id = get_or_create_app_calendar()
                    user.google_calendar_id = calendar_id
                    db.session.commit()
                    return jsonify({"success": True, "message": "Google Calendar connected!", "google_calendar_id": calendar_id})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"success": False, "error": f"Failed to connect Google Calendar: {e}"}), 500
            elif google_action == 'reset_google_calendar':
                user.google_calendar_id = None
                db.session.commit()
                return jsonify({"success": True, "message": "Google Calendar disconnected.", "google_calendar_id": None})

            # OpenAI API key logic (default)
            openai_api_key = data.get('openai_api_key', '').strip()
            if openai_api_key and not openai_api_key.startswith('sk-'):
                return jsonify({"success": False, "error": "Invalid OpenAI API key format"}), 400
            user.set_api_key(openai_api_key, MASTER_ENCRYPTION_KEY)
            db.session.commit()
            session['user']['has_api_key'] = bool(openai_api_key)
            return jsonify({"success": True, "message": "Settings updated successfully"})

        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    # Get user from database for display
    user_sub = session['user']['sub']
    user = User.find_by_sub(user_sub)

    if user:
        session['user']['has_api_key'] = bool(user.encrypted_api_key)
        display_user = {
            'email': user.email,
            'name': user.name,
            'sub': user.sub,
            'has_api_key': bool(user.encrypted_api_key),
            'google_calendar_id': user.google_calendar_id
        }
    else:
        display_user = session['user']
        display_user['has_api_key'] = False
        display_user['google_calendar_id'] = None

    return render_template('settings.html', user=display_user, active_page='settings')
