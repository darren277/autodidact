""""""
from settings import PORT


def get_csrf_token(s):
    secret_key = 'some super secret key that is changed before deployment'
    from urllib.parse import quote
    response = s.get(f'http://localhost:{PORT}/csrf_token?key={quote(secret_key)}')
    if response.status_code == 200:
        return response.json().get('csrf_token')
    return None


def headers(s):
    csrf_token = get_csrf_token(s)

    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }

    return headers
