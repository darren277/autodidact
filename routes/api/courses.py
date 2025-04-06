""""""
from flask import request, jsonify


def courses_route(db):
    from models.lessons import Course
    if request.method == 'GET':
        courses = Course.query.all()
        return jsonify([course.json() for course in courses])
    elif request.method == 'POST':
        data = request.json
        title = data.get('title', None)
        if not title:
            return jsonify({"error": "Missing required fields."}), 400

        course = Course(title=title)
        db.session.add(course)
        db.session.commit()
        return jsonify({"message": "Course added successfully.", "course_id": course.id})
    else:
        return jsonify({"error": "Invalid request method."}), 400


def course_route(db, course_id):
    from models.lessons import Course
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found."}), 404
    if request.method == 'GET':
        return jsonify(course.json())
    elif request.method == 'PUT':
        data = request.json
        title = data.get('title', None)
        if title:
            course.title = title
        db.session.commit()
        return jsonify({"message": "Course updated successfully."})
    elif request.method == 'DELETE':
        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "Course deleted successfully."})
    else:
        return jsonify({"error": "Invalid request method."}), 400
