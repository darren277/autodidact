""""""
from flask import render_template, jsonify

def cornell_notes_route(notes_id):
    from models.lessons import Notes
    notes = Notes.query.get(notes_id)
    if not notes:
        return jsonify({"error": "Notes not found"}), 404

    # Get structured data or fall back to example data
    structured_data = notes.get_structured_data()
    if not structured_data:
        from utils.example_structured_notes import data
        structured_data = data

    return render_template('notes/cornell.html', **structured_data)

def digital_notebook_route(notes_id):
    from models.lessons import Notes
    notes = Notes.query.get(notes_id)
    if not notes:
        return jsonify({"error": "Notes not found"}), 404

    # Get structured data or fall back to example data
    structured_data = notes.get_structured_data()
    if not structured_data:
        from utils.example_structured_notes import data
        structured_data = data

    return render_template('notes/digital-notebook.html', **structured_data)

def mindmap_route(notes_id):
    from models.lessons import Notes
    notes = Notes.query.get(notes_id)
    if not notes:
        return jsonify({"error": "Notes not found"}), 404

    # Get structured data or fall back to example data
    structured_data = notes.get_structured_data()
    if not structured_data:
        from utils.example_structured_notes import data
        structured_data = data

    return render_template('notes/mindmap.html', **structured_data)

def stickynotes_route(notes_id):
    from models.lessons import Notes
    notes = Notes.query.get(notes_id)
    if not notes:
        return jsonify({"error": "Notes not found"}), 404

    # Get structured data or fall back to example data
    structured_data = notes.get_structured_data()
    if not structured_data:
        from utils.example_structured_notes import data
        structured_data = data

    return render_template('notes/stickynotes.html', **structured_data)

def vintage_cards_route(notes_id):
    from models.lessons import Notes
    notes = Notes.query.get(notes_id)
    if not notes:
        return jsonify({"error": "Notes not found"}), 404

    # Get structured data or fall back to example data
    structured_data = notes.get_structured_data()
    if not structured_data:
        from utils.example_structured_notes import data
        structured_data = data

    return render_template('notes/vintage-cards.html', **structured_data)

def augmented_notes_route(notes_id):
    from models.lessons import Notes
    notes = Notes.query.get(notes_id)
    if not notes:
        return jsonify({"error": "Notes not found"}), 404

    # Get structured data or fall back to example data
    structured_data = notes.get_structured_data()
    if not structured_data:
        from utils.example_structured_notes import data
        structured_data = data

    return render_template('notes/augmented.html', **structured_data)
