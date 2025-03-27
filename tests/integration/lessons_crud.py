""""""
import requests

def test_create_lesson():
    data = {
        "title": "Test Lesson",
        "content": "This is a test lesson.",
        "module_id": 1
    }

    response = requests.post('http://localhost:8000/api/lessons', json=data)

    print(response.status_code)
    print(response.json())


def test_get_lessons():
    response = requests.get('http://localhost:8000/api/lessons')

    print(response.status_code)
    print(response.json())


def test_update_lesson():
    data = {
        "title": "Updated Test Lesson",
        "content": "This is an updated test lesson.",
        "module_id": 1
    }

    response = requests.put('http://localhost:8000/api/lessons/1', json=data)

    print(response.status_code)
    print(response.json())


def test_delete_lesson():
    response = requests.delete('http://localhost:8000/api/lessons/1')

    print(response.status_code)
    print(response.json())


if __name__ == '__main__':
    test_create_lesson()
    test_get_lessons()
    test_update_lesson()
    test_delete_lesson()

