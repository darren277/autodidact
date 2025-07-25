""""""
import requests
from settings import PORT
from utils.get_headers import headers


def test_create_course():
    data = {
        "title": "Test Course",
    }

    with requests.Session() as s:
        response = s.post(f'http://localhost:{PORT}/api/courses', json=data, headers=headers(s))

        print(response.status_code)
        print(response.json())


def test_get_courses():
    response = requests.get(f'http://localhost:{PORT}/api/courses')

    print(response.status_code)
    print(response.json())


def test_get_specific_course():
    response = requests.get(f'http://localhost:{PORT}/api/courses/1')

    print(response.status_code)
    print(response.json())


def test_update_course():
    data = {
        "title": "Updated Test Course"
    }

    with requests.Session() as s:
        response = s.put(f'http://localhost:{PORT}/api/courses/1', json=data, headers=headers(s))

    print(response.status_code)
    print(response.json())


def test_delete_course():
    with requests.Session() as s:
        response = s.delete(f'http://localhost:{PORT}/api/course/1', headers=headers(s))

    print(response.status_code)
    print(response.json())



def test_create_module():
    data = {
        "title": "Test Module"
    }

    response = requests.post(f'http://localhost:{PORT}/api/modules', json=data)

    print(response.status_code)
    print(response.json())


def test_get_modules():
    response = requests.get(f'http://localhost:{PORT}/api/modules')

    print(response.status_code)
    print(response.json())


def test_get_specific_module():
    response = requests.get(f'http://localhost:{PORT}/api/modules/1')

    print(response.status_code)
    print(response.json())


def test_update_module():
    data = {
        "title": "Updated Test Module"
    }

    response = requests.put(f'http://localhost:{PORT}/api/modules/1', json=data)

    print(response.status_code)
    print(response.json())


def test_delete_module():
    response = requests.delete(f'http://localhost:{PORT}/api/modules/1')

    print(response.status_code)
    print(response.json())



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


def test_save_notes():
    data = {
        "lesson_id": 1,
        "content": "These are my notes for lesson 1. I learned about important concepts."
    }

    with requests.Session() as s:
        response = s.post(f'http://localhost:{PORT}/api/save_notes', json=data, headers=headers(s))

    print("Save Notes Response:")
    print(response.status_code)
    print(response.json())


def test_get_notes():
    with requests.Session() as s:
        response = s.get(f'http://localhost:{PORT}/api/get_notes/1', headers=headers(s))

    print("Get Notes Response:")
    print(response.status_code)
    print(response.json())


def test_mark_lesson_complete():
    data = {
        "lesson_id": 1
    }

    with requests.Session() as s:
        response = s.post(f'http://localhost:{PORT}/api/mark_lesson_complete', json=data, headers=headers(s))

    print("Mark Lesson Complete Response:")
    print(response.status_code)
    print(response.json())


def test_submit_question():
    data = {
        "lesson_id": 1,
        "question": "Can you explain the concept of inheritance in more detail?"
    }

    with requests.Session() as s:
        response = s.post(f'http://localhost:{PORT}/api/submit_question', json=data, headers=headers(s))

    print("Submit Question Response:")
    print(response.status_code)
    print(response.json())


if __name__ == '__main__':
    test_create_course()
    test_get_courses()
    test_get_specific_course()
    test_update_course()
    test_delete_course()

    test_create_module()
    test_get_modules()
    test_get_specific_module()
    test_update_module()
    test_delete_module()

    test_create_lesson()
    test_get_lessons()
    test_get_specific_lesson()
    test_update_lesson()
    test_delete_lesson()

    test_save_notes()
    test_get_notes()
    test_mark_lesson_complete()
    test_submit_question()

