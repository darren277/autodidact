""""""
from flask import jsonify, request


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
