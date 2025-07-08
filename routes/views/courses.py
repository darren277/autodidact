""""""
from flask import render_template, request, flash, redirect, url_for

def create_course_route(db):
    from models.lessons import Course

    if request.method == 'GET':
        # Create an empty course object for the form
        empty_course = Course()
        return render_template('courses/edit.html', course=empty_course)

    elif request.method == 'POST':
        # Create new course with form data
        course = Course()
        course.title = request.form.get('title', '')
        course.description = request.form.get('description', '')
        course.overview = request.form.get('overview', '')

        # Handle objectives
        import json
        objectives = request.form.getlist('objectives[]')
        course.objectives = json.dumps([obj.strip() for obj in objectives if obj.strip()])

        # Handle prerequisites
        prerequisites = request.form.getlist('prerequisites[]')
        course.prerequisites = json.dumps([prereq.strip() for prereq in prerequisites if prereq.strip()])

        try:
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully!', 'success')
            return redirect(url_for('list_courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating course: {str(e)}', 'error')
            return render_template('courses/edit.html', course=course)


def edit_course_route(db, course_id):
    from models.lessons import Course
    from flask import request, flash, redirect, url_for

    if request.method == 'GET':
        course = Course.query.get(course_id)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('list_courses'))
        return render_template('courses/edit.html', course=course)

    elif request.method == 'POST':
        course = Course.query.get(course_id)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('list_courses'))

        # Update course with form data
        course.title = request.form.get('title', '')
        course.description = request.form.get('description', '')
        course.overview = request.form.get('overview', '')

        # Handle objectives
        import json
        objectives = request.form.getlist('objectives[]')
        course.objectives = json.dumps([obj.strip() for obj in objectives if obj.strip()])

        # Handle prerequisites
        prerequisites = request.form.getlist('prerequisites[]')
        course.prerequisites = json.dumps([prereq.strip() for prereq in prerequisites if prereq.strip()])

        try:
            db.session.commit()
            flash('Course updated successfully!', 'success')
            return redirect(url_for('list_courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating course: {str(e)}', 'error')
            return render_template('courses/edit.html', course=course)


def delete_course_route(db, course_id):
    from models.lessons import Course

    course = Course.query.get(course_id)
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('list_courses'))

    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting course: {str(e)}', 'error')

    return redirect(url_for('list_courses'))
