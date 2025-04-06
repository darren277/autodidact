""""""
from flask import request, jsonify


def modules_route(db):
    from models.lessons import Module
    if request.method == 'GET':
        modules = Module.query.all()
        return jsonify([module.json() for module in modules])
    elif request.method == 'POST':
        data = request.json
        title = data.get('title', None)
        course_id = data.get('course_id', None)
        if not title or not course_id:
            return jsonify({"error": "Missing required fields."}), 400

        # Optional fields: start_date, end_date...
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        description = data.get('description', None)

        # check if course exists...
        from models.lessons import Course
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": "Course not found."}), 400

        module = Module(title=title, course_id=course_id)

        if start_date: module.start_date = start_date
        if end_date: module.end_date = end_date
        if description: module.description = description

        db.session.add(module)
        db.session.commit()
        return jsonify({"message": "Module added successfully.", "module_id": module.id})
    else:
        return jsonify({"error": "Invalid request method."}), 400


def module_route(db, module_id):
    from models.lessons import Module
    module = Module.query.get(module_id)
    if not module:
        return jsonify({"error": "Module not found."}), 404
    if request.method == 'GET':
        return jsonify(module.json())
    elif request.method == 'PUT':
        data = request.json
        title = data.get('title', None)
        if title:
            module.title = title
        db.session.commit()
        return jsonify({"message": "Module updated successfully."})
    elif request.method == 'DELETE':
        db.session.delete(module)
        db.session.commit()
        return jsonify({"message": "Module deleted successfully."})
    else:
        return jsonify({"error": "Invalid request method."}), 400
