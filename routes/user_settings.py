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

            openai_api_key = data.get('openai_api_key', '').strip()

            # Validate API key format (basic validation)
            if openai_api_key and not openai_api_key.startswith('sk-'):
                return jsonify({"success": False, "error": "Invalid OpenAI API key format"}), 400

            # Get or create user in database
            user_sub = session['user']['sub']
            user = User.find_by_sub(user_sub)

            if not user:
                # Create user if not exists
                user = User.create_or_update(
                    email=session['user']['email'],
                    name=session['user']['name'],
                    sub=user_sub
                )

            # Encrypt and store the API key
            user.set_api_key(openai_api_key, MASTER_ENCRYPTION_KEY)
            db.session.commit()

            # Update session with API key status
            session['user']['has_api_key'] = bool(openai_api_key)

            return jsonify({"success": True, "message": "Settings updated successfully"})

        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    # Get user from database for display
    user_sub = session['user']['sub']
    user = User.find_by_sub(user_sub)

    if user:
        # Add API key status to session user data
        session['user']['has_api_key'] = bool(user.encrypted_api_key)
        display_user = {
            'email': user.email,
            'name': user.name,
            'sub': user.sub,
            'has_api_key': bool(user.encrypted_api_key)
        }
    else:
        display_user = session['user']
        display_user['has_api_key'] = False

    return render_template('settings.html', user=display_user, active_page='settings')
