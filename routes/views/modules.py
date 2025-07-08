""""""
from flask import render_template, request, redirect, url_for, flash, session, jsonify

def create_module_route(db):
    from models.lessons import Module, Course

    courses = Course.query.all()
    if request.method == 'GET':
        # Create an empty module object for the form
        empty_module = Module()
        return render_template('modules/edit.html', module=empty_module, courses=courses)

    elif request.method == 'POST':
        # Create new module with form data
        module = Module()
        module.title = request.form.get('title', '')
        module.description = request.form.get('description', '')
        module.overview = request.form.get('overview', '')
        module.resources = request.form.get('resources', '')
        module.assessment = request.form.get('assessment', '')
        module.course_id = request.form.get('course_id')
        import json
        learning_outcomes = request.form.getlist('learning_outcomes[]')
        module.learning_outcomes = json.dumps([outcome.strip() for outcome in learning_outcomes if outcome.strip()])
        prerequisites = request.form.getlist('prerequisites[]')
        related_modules = request.form.getlist('related_modules[]')
        module.prerequisites = json.dumps([int(p) for p in prerequisites if p.isdigit()])
        module.related_modules = json.dumps([int(r) for r in related_modules if r.isdigit()])
        try:
            db.session.add(module)
            db.session.commit()
            flash('Module created successfully!', 'success')
            return redirect(url_for('list_modules'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating module: {str(e)}', 'error')
            return render_template('modules/edit.html', module=module, courses=courses)


def edit_module_route(db, module_id):
    from models.lessons import Module, Course

    courses = Course.query.all()
    if request.method == 'GET':
        module = Module.query.get(module_id)
        if not module:
            flash('Module not found', 'error')
            return redirect(url_for('list_modules'))
        return render_template('modules/edit.html', module=module, courses=courses)

    elif request.method == 'POST':
        module = Module.query.get(module_id)
        if not module:
            flash('Module not found', 'error')
            return redirect(url_for('list_modules'))
        module.title = request.form.get('title', '')
        module.description = request.form.get('description', '')
        module.overview = request.form.get('overview', '')
        module.resources = request.form.get('resources', '')
        module.assessment = request.form.get('assessment', '')
        module.course_id = request.form.get('course_id')
        import json
        learning_outcomes = request.form.getlist('learning_outcomes[]')
        module.learning_outcomes = json.dumps([outcome.strip() for outcome in learning_outcomes if outcome.strip()])
        prerequisites = request.form.getlist('prerequisites[]')
        related_modules = request.form.getlist('related_modules[]')
        module.prerequisites = json.dumps([int(p) for p in prerequisites if p.isdigit()])
        module.related_modules = json.dumps([int(r) for r in related_modules if r.isdigit()])
        try:
            db.session.commit()
            flash('Module updated successfully!', 'success')
            return redirect(url_for('list_modules'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating module: {str(e)}', 'error')
            return render_template('modules/edit.html', module=module, courses=courses)

def view_module_route(module_id):
    from models.lessons import Module, Lesson
    module = Module.query.get(module_id)
    if not module:
        return jsonify({"error": "Module not found"}), 404

    # Get lessons for this module
    lessons = Lesson.query.filter_by(module_id=module_id).all()

    # Get user progress if authenticated
    user = None
    if 'user' in session:
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)

    # Build lesson cards with actual progress
    lesson_cards = []
    completed_count = 0
    for i, lesson in enumerate(lessons, 1):
        status = ""
        icon = ""
        action = "Start"

        if user:
            # Get actual progress for this lesson
            progress = user.get_lesson_progress(lesson.id)
            if progress:
                if progress.is_completed:
                    status = "completed"
                    icon = "✓"
                    action = "Review"
                    completed_count += 1
                elif progress.percentage_completed > 0:
                    status = "current"
                    icon = "•"
                    action = "Continue"
                else:
                    status = ""
                    icon = ""
                    action = "Start"
            else:
                # No progress record exists
                status = ""
                icon = ""
                action = "Start"
        else:
            # No user logged in, show default state
            status = ""
            icon = ""
            action = "Start"

        lesson_cards.append({
            "id": lesson.id,
            "status": status,
            "icon": icon,
            "title": f"{i}. {lesson.title}",
            "description": lesson.content[:100] + "..." if len(lesson.content) > 100 else lesson.content,
            "duration": f"{lesson.estimated_time_hours}h {lesson.estimated_time_minutes}m" if lesson.estimated_time_hours > 0 else f"{lesson.estimated_time_minutes}m",
            "action": action,
            "progress_percentage": progress.percentage_completed if user and progress else 0
        })

    # Build module data structure
    module_data = {
        "title": module.title,
        "page_title": module.title,
        "module_progress": {
            "completed": completed_count,
            "total": len(lessons),
            "percentage": int((completed_count / len(lessons)) * 100) if lessons else 0
        },
        "module_download_materials_link": "#",  # TODO: Implement download functionality
        "module_take_quiz_link": "#",  # TODO: Implement quiz functionality
        "module_description": f"<p>This module contains {len(lessons)} lessons covering various topics.</p>",
        "lesson_cards": lesson_cards,
        "resources": []  # TODO: Add resources field to model
    }

    # Fetch prerequisite and related modules
    prereq_modules = {}
    related_modules = {}

    if module.get_prerequisites():
        prereq_ids = module.get_prerequisites()
        prereq_modules_list = Module.query.filter(Module.id.in_(prereq_ids)).all()
        prereq_modules = {m.id: m for m in prereq_modules_list}

    if module.get_related_modules():
        related_ids = module.get_related_modules()
        related_modules_list = Module.query.filter(Module.id.in_(related_ids)).all()
        related_modules = {m.id: m for m in related_modules_list}

    return render_template(
        'modules/view.html',
        active_page=f'module_{module_id}',
        module=module,  # Pass the module object for teacher view
        prereq_modules=prereq_modules,
        related_modules=related_modules,
        **module_data,
        user=session['user']
    )
