""""""
import base64
import requests
from flask import request, session, redirect, url_for, render_template_string
from urllib import parse
from settings import COGNITO_DOMAIN, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, LOGOUT_URI
import logging
logger = logging.getLogger(__name__)

def auth_callback_route():
    # Handle error returned from Cognito
    error = request.args.get('error')
    error_description = request.args.get('error_description')

    if error:
        decoded_description = parse.unquote(error_description or '')
        logger.warning("Cognito auth error: %s - %s", error, decoded_description)
        return render_template_string(
            "<h2>Authentication Error</h2><p>{{ error }}</p><p>{{ description }}</p>",
            error=error,
            description=decoded_description
        ), 400

    code = request.args.get('code')

    token_url = f'https://{COGNITO_DOMAIN}/oauth2/token'

    auth_string = f'{CLIENT_ID}:{CLIENT_SECRET}'
    auth_header = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {auth_header}'
    }

    body = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(token_url, headers=headers, data=body)

    if response.status_code != 200:
        logger.error("Token exchange failed: %s - %s", response.status_code, response.text)
        return render_template_string(
            "<h2>Token Exchange Failed</h2><p>{{ status }}</p><pre>{{ message }}</pre>",
            status=response.status_code,
            message=response.text
        ), 400

    if response.status_code == 200:
        tokens = response.json()

        user_info_url = f'https://{COGNITO_DOMAIN}/oauth2/userInfo'
        headers = {
            'Authorization': f'Bearer {tokens["access_token"]}'
        }

        user_response = requests.get(user_info_url, headers=headers)

        if user_response.status_code != 200:
            logger.error("Failed to fetch user info: %s - %s", user_response.status_code, user_response.text)
            return render_template_string(
                "<h2>Failed to Fetch User Info</h2><p>{{ status }}</p><pre>{{ message }}</pre>",
                status=user_response.status_code,
                message=user_response.text
            ), 400

        if user_response.status_code == 200:
            user_info = user_response.json()
            
            # Create or update user in database
            from models.user import User
            from main import db
            
            try:
                user = User.create_or_update(
                    email=user_info.get('email', ''),
                    name=user_info.get('name', ''),
                    sub=user_info.get('sub', '')
                )

                # Google Calendar sync: create/find dedicated calendar and store ID
                if not user.google_calendar_id:
                    try:
                        from lib.apis.google_agenda import get_or_create_app_calendar
                        calendar_id = get_or_create_app_calendar()
                        user.google_calendar_id = calendar_id
                        db.session.commit()
                    except Exception as cal_err:
                        logger.error(f"Failed to create/find Google Calendar: {cal_err}")
                
                # Preserve existing mode if it exists, otherwise default to student
                existing_mode = session.get('user', {}).get('mode', 'student')
                user_info['mode'] = existing_mode
                user_info['has_api_key'] = bool(user.encrypted_api_key)
                
                session['user'] = user_info
                return redirect(url_for('index'))
                
            except Exception as e:
                logger.error("Failed to create/update user in database: %s", e)
                # Still allow login even if database operation fails
                existing_mode = session.get('user', {}).get('mode', 'student')
                user_info['mode'] = existing_mode
                user_info['has_api_key'] = False
                session['user'] = user_info
                return redirect(url_for('index'))

    return 'Authentication Error', 400


def auth_logout_route():
    session.clear()

    logout_url = (
        f'https://{COGNITO_DOMAIN}/logout?'
        f'client_id={CLIENT_ID}&'
        f'logout_uri={parse.quote(LOGOUT_URI)}'
    )

    return redirect(logout_url)
