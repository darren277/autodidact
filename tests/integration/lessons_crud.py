""""""
import requests
from settings import PORT


def test_create_lesson():
    data = {
        "title": "Test Lesson",
        "content": "This is a test lesson.",
        "module_id": 1
    }

    response = requests.post(f'http://localhost:{PORT}/api/lessons', json=data)

    print(response.status_code)
    print(response.json())


def test_get_lessons():
    response = requests.get(f'http://localhost:{PORT}/api/lessons')

    print(response.status_code)
    print(response.json())


def test_get_specific_lesson():
    response = requests.get(f'http://localhost:{PORT}/api/lessons/1')

    print(response.status_code)
    print(response.json())


def test_update_lesson():
    data = {
        "title": "Updated Test Lesson",
        "content": "This is an updated test lesson.",
        "module_id": 1
    }

    response = requests.put(f'http://localhost:{PORT}/api/lessons/1', json=data)

    print(response.status_code)
    print(response.json())


def test_delete_lesson():
    response = requests.delete(f'http://localhost:{PORT}/api/lessons/1')

    print(response.status_code)
    print(response.json())


if __name__ == '__main__':
    test_create_lesson()
    test_get_lessons()
    test_get_specific_lesson()
    test_update_lesson()
    test_delete_lesson()

