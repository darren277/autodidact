""""""
from flask import Flask, request, Response, render_template, jsonify, session, redirect, url_for
from flask_sse import sse

import redis

from routes.api.courses import courses_route, course_route
from routes.api.lessons import lessons_route, lesson_route
from routes.api.modules import modules_route, module_route
from routes.assistant import ask_route, stream_route
from routes.auth import auth_callback_route, auth_logout_route
from routes.convert_notes import convert_notes_route
from routes.lo import lo_route
from routes.summarize import summarize_route
from routes.tts import tts_route
from utils.convert_to_markdown import convert_to_simple_markdown

from settings import REDIS_URL, ENABLE_CORS, APP_SECRET_KEY, COGNITO_LOGIN_URL, REDIS_HOST, REDIS_PORT, DEBUG, MASTER_ENCRYPTION_KEY
from settings import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASS, POSTGRES_DB

from flask_cors import CORS

from database import db

from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

csrf = CSRFProtect(app)

app.secret_key = APP_SECRET_KEY

if ENABLE_CORS:
    #CORS(app, supports_credentials=True)
    #CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["*"]}})
    CORS(app)

app.config["REDIS_URL"] = REDIS_URL

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

#app.register_blueprint(sse, url_prefix='/stream')


@app.route('/csrf_token')
def csrf_token():
    '''
    A bit of a hacky way to get the CSRF token for our direct API calls in testing.
    Likely disable for production builds.
    :return:
    '''
    secret_key = app.config['SECRET_KEY']

    request_key = request.args.get('key')

    # app.jinja_env.globals["csrf_token"] = generate_csrf
    if request_key != secret_key:
        return jsonify({"error": "Invalid key"}), 403

    token = app.jinja_env.globals["csrf_token"]()
    return jsonify({"csrf_token": token})

@app.route('/chat')
def chat():
    return render_template('chat-interface.html')

@app.route('/ask', methods=['POST'])
def ask():
    return ask_route(r)

@app.route('/stream')
def stream():
    return stream_route(r)

@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    print(f"DEBUG: toggle_mode called")
    print(f"DEBUG: Session: {session}")
    print(f"DEBUG: Request headers: {dict(request.headers)}")
    print(f"DEBUG: Request data: {request.get_data()}")
    
    if 'user' not in session:
        print("DEBUG: No user in session")
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        data = request.get_json()
        print(f"DEBUG: Parsed JSON data: {data}")
        
        if data and 'mode' in data:
            new_mode = data['mode']
            print(f"DEBUG: Switching to mode: {new_mode}")
            print(f"DEBUG: Session before change: {session}")
            if new_mode in ['student', 'teacher']:
                session['user']['mode'] = new_mode
                session.modified = True  # Mark session as modified
                print(f"DEBUG: Session after change: {session}")
                print(f"DEBUG: Session modified flag: {session.modified}")
                print(f"DEBUG: Mode updated in session: {session['user']['mode']}")
                return jsonify({"message": "Mode toggled successfully", "mode": new_mode})
            else:
                print(f"DEBUG: Invalid mode: {new_mode}")
                return jsonify({"error": "Invalid mode"}), 400
        else:
            # Fallback to toggle behavior if no mode specified
            current_mode = session['user']['mode']
            print(f"DEBUG: No mode specified, toggling from: {current_mode}")
            if current_mode == 'student':
                session['user']['mode'] = 'teacher'
            else:
                session['user']['mode'] = 'student'
            session.modified = True  # Mark session as modified
            print(f"DEBUG: Mode toggled to: {session['user']['mode']}")
            return jsonify({"message": "Mode toggled successfully", "mode": session['user']['mode']})
    except Exception as e:
        print(f"DEBUG: Exception in toggle_mode: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/notes/cornell_notes/<notes_id>')
def cornell_notes(notes_id):
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

@app.route('/api/notes/cornell_notes/<notes_id>')
def api_cornell_notes(notes_id):
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

@app.route('/notes/digital_notebook/<notes_id>')
def digital_notebook(notes_id):
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

@app.route('/api/notes/digital_notebook/<notes_id>')
def api_digital_notebook(notes_id):
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

@app.route('/notes/mindmap/<notes_id>')
def mindmap(notes_id):
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

@app.route('/api/notes/mindmap/<notes_id>')
def api_mindmap(notes_id):
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

@app.route('/notes/stickynotes/<notes_id>')
def stickynotes(notes_id):
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

@app.route('/api/notes/stickynotes/<notes_id>')
def api_stickynotes(notes_id):
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

@app.route('/notes/vintage_cards/<notes_id>')
def vintage_cards(notes_id):
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

@app.route('/api/notes/vintage_cards/<notes_id>')
def api_vintage_cards(notes_id):
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

@app.route('/notes/augmented/<notes_id>')
def augmented(notes_id):
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

@app.route('/api/notes/augmented/<notes_id>')
def api_augmented(notes_id):
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

@app.route('/summarize', methods=['POST'])
def summarize():
    return summarize_route()

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    return convert_notes_route()

@app.route('/tts', methods=['GET', 'POST'])
def tts():
    return tts_route()

@app.route('/dashboard')
def dashboard():
    # Debug: Check session contents
    print("=== SESSION DEBUG ===")
    print(f"Session keys: {list(session.keys())}")
    print(f"Session user: {session.get('user', 'NOT FOUND')}")
    print(f"Session modified flag: {session.modified}")
    print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'No session ID'}")
    print("====================")
    
    # Check if user is logged in
    if 'user' not in session:
        # Redirect to login if not authenticated
        return redirect(url_for('login'))
    
    user = session['user']
    
    # Initialize dashboard data with defaults
    dashboard_data = {
        'progress_summary': {
            'completed_lessons': 0,
            'total_lessons': 0,
            'completion_percentage': 0
        },
        'next_session': None,
        'achievements': {
            'modules_completed': 0,
            'quizzes_passed': 0
        },
        'recent_activity': []
    }
    
    if user:
        try:
            from models.user import User
            from models.lessons import Lesson, Module, UserProgress
            from datetime import datetime, timedelta
            
            print(f"Looking for user with sub: {user['sub']}")
            
            # Get user from database
            user_obj = User.find_by_sub(user['sub'])
            print(f"User object found: {user_obj}")
            
            if user_obj:
                # Get completion statistics
                stats = user_obj.get_completion_stats()
                dashboard_data['progress_summary'] = {
                    'completed_lessons': stats['completed_lessons'],
                    'total_lessons': stats['total_lessons'],
                    'completion_percentage': stats['completion_percentage']
                }
                
                # Find next session (recommended lesson)
                next_lesson = user_obj.get_next_recommended_lesson()
                if next_lesson:
                    module = next_lesson.module if next_lesson.module else None
                    
                    # Get progress for this lesson if it exists
                    progress = user_obj.get_lesson_progress(next_lesson.id)
                    
                    dashboard_data['next_session'] = {
                        'lesson_title': next_lesson.title,
                        'module_title': module.title if module else 'Unknown Module',
                        'last_accessed': progress.last_accessed if progress else None,
                        'lesson_id': next_lesson.id,
                        'module_id': module.id if module else None
                    }
                
                # Count completed modules
                completed_modules = set()
                for progress in user_obj.progress_records:
                    if progress.is_completed and progress.lesson.module:
                        completed_modules.add(progress.lesson.module.id)
                
                dashboard_data['achievements']['modules_completed'] = len(completed_modules)
                
                # Get recent activity (last 10 progress updates)
                recent_activity = UserProgress.query.filter_by(
                    user_id=user_obj.id
                ).order_by(UserProgress.updated_at.desc()).limit(10).all()
                
                for progress in recent_activity:
                    lesson = progress.lesson
                    activity_type = "Lesson Completed" if progress.is_completed else "Progress Updated"
                    activity_time = progress.updated_at
                    
                    # Format time ago
                    time_diff = datetime.utcnow() - activity_time
                    if time_diff.days > 0:
                        time_ago = f"{time_diff.days} day{'s' if time_diff.days != 1 else ''} ago"
                    elif time_diff.seconds > 3600:
                        hours = time_diff.seconds // 3600
                        time_ago = f"{hours} hour{'s' if hours != 1 else ''} ago"
                    else:
                        minutes = time_diff.seconds // 60
                        time_ago = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                    
                    dashboard_data['recent_activity'].append({
                        'type': activity_type,
                        'lesson_title': lesson.title,
                        'time_ago': time_ago,
                        'percentage': progress.percentage_completed,
                        'is_completed': progress.is_completed
                    })
                
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            # Keep default values if there's an error
    
    # Debug: Print what we're passing to template
    print("=== DASHBOARD DEBUG ===")
    print(f"User: {user}")
    print(f"Progress summary: {dashboard_data['progress_summary']}")
    print(f"Next session: {dashboard_data['next_session']}")
    print(f"Achievements: {dashboard_data['achievements']}")
    print(f"Recent activity: {dashboard_data['recent_activity']}")
    print("=======================")
    
    # Try passing variables as a single dictionary first
    template_vars = {
        'active_page': 'dashboard',
        'user': user,
        'progress_summary': dashboard_data['progress_summary'],
        'next_session': dashboard_data['next_session'],
        'achievements': dashboard_data['achievements'],
        'recent_activity': dashboard_data['recent_activity']
    }
    
    print("=== TEMPLATE VARS ===")
    print(f"Template vars: {template_vars}")
    print("====================")
    
    try:
        return render_template('dashboard.html', **template_vars)
    except Exception as e:
        print(f"Template rendering error: {e}")
        # Fallback to simple template
        return f"Dashboard error: {e}", 500

@app.route('/module/<module_id>')
def module(module_id):
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
        'module.html',
        active_page=f'module_{module_id}',
        module=module,  # Pass the module object for teacher view
        prereq_modules=prereq_modules,
        related_modules=related_modules,
        **module_data,
        user=session['user']
    )

@app.route('/practice')
def practice():
    return render_template('practice.html', active_page='practice')

@app.route('/api/lessons', methods=['GET', 'POST'])
def api_lessons():
    return lessons_route(db)

@app.route('/api/lessons/<lesson_id>', methods=['GET', 'PUT', 'DELETE'])
def api_lesson(lesson_id):
    return lesson_route(db, lesson_id)

@app.route('/api/modules', methods=['GET', 'POST'])
def api_modules():
    return modules_route(db)

@app.route('/api/modules/<module_id>', methods=['GET', 'PUT', 'DELETE'])
def api_module(module_id):
    return module_route(db, module_id)

@app.route('/api/courses', methods=['GET', 'POST'])
def api_courses():
    return courses_route(db)

@app.route('/api/courses/<course_id>', methods=['GET', 'PUT', 'DELETE'])
def api_course(course_id):
    return course_route(db, course_id)

@app.route('/api/save_notes', methods=['POST'])
def save_notes():
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        lesson_id = data.get('lesson_id')
        content = data.get('content', '').strip()
        
        if not lesson_id:
            return jsonify({"error": "Lesson ID is required"}), 400
        
        # Get user from database
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if notes already exist for this user and lesson
        from models.lessons import Notes
        existing_notes = Notes.query.filter_by(
            lesson_id=lesson_id, 
            user_id=user.id
        ).first()
        
        if existing_notes:
            # Update existing notes
            existing_notes.content = content
        else:
            # Create new notes
            new_notes = Notes(
                content=content,
                lesson_id=lesson_id,
                user_id=user.id
            )
            db.session.add(new_notes)
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Notes saved successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save notes: {str(e)}"}), 500

@app.route('/api/get_notes/<lesson_id>', methods=['GET'])
def get_notes(lesson_id):
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        # Get user from database
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get notes for this user and lesson
        from models.lessons import Notes
        notes = Notes.query.filter_by(
            lesson_id=lesson_id, 
            user_id=user.id
        ).first()
        
        if notes:
            return jsonify({
                "success": True, 
                "content": notes.content
            })
        else:
            return jsonify({
                "success": True, 
                "content": ""
            })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get notes: {str(e)}"}), 500

@app.route('/api/mark_lesson_complete', methods=['POST'])
def mark_lesson_complete():
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        lesson_id = data.get('lesson_id')
        percentage = data.get('percentage', 100)  # Default to 100% if not specified
        
        if not lesson_id:
            return jsonify({"error": "Lesson ID is required"}), 400
        
        # Get user from database
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Mark lesson as complete
        progress = user.mark_lesson_complete(lesson_id, percentage)
        
        # Get updated completion stats
        stats = user.get_completion_stats()
        
        return jsonify({
            "success": True, 
            "message": "Lesson marked as complete",
            "new_percentage": progress.percentage_completed,
            "is_completed": progress.is_completed,
            "completion_date": progress.completion_date.isoformat() if progress.completion_date else None,
            "overall_stats": stats
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to mark lesson complete: {str(e)}"}), 500

@app.route('/api/update_lesson_progress', methods=['POST'])
def update_lesson_progress():
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        lesson_id = data.get('lesson_id')
        percentage = data.get('percentage', 0)
        time_spent_minutes = data.get('time_spent_minutes')
        
        if not lesson_id:
            return jsonify({"error": "Lesson ID is required"}), 400
        
        if not isinstance(percentage, (int, float)) or percentage < 0 or percentage > 100:
            return jsonify({"error": "Percentage must be a number between 0 and 100"}), 400
        
        # Get user from database
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Update lesson progress
        progress = user.update_lesson_progress(lesson_id, percentage, time_spent_minutes)
        
        return jsonify({
            "success": True, 
            "message": "Progress updated successfully",
            "percentage_completed": progress.percentage_completed,
            "is_completed": progress.is_completed,
            "time_spent_minutes": progress.time_spent_minutes,
            "last_accessed": progress.last_accessed.isoformat() if progress.last_accessed else None
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to update progress: {str(e)}"}), 500

@app.route('/api/get_lesson_progress/<lesson_id>', methods=['GET'])
def get_lesson_progress(lesson_id):
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        # Get user from database
        from models.user import User
        user_sub = session['user']['sub']
        user = User.find_by_sub(user_sub)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get progress for this lesson
        progress = user.get_lesson_progress(lesson_id)
        
        if progress:
            return jsonify({
                "success": True,
                "progress": progress.json()
            })
        else:
            return jsonify({
                "success": True,
                "progress": {
                    "percentage_completed": 0,
                    "is_completed": False,
                    "time_spent_minutes": 0
                }
            })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get progress: {str(e)}"}), 500

@app.route('/api/submit_question', methods=['POST'])
def submit_question():
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        lesson_id = data.get('lesson_id')
        question = data.get('question', '').strip()
        
        if not lesson_id or not question:
            return jsonify({"error": "Lesson ID and question are required"}), 400
        
        # Get lesson context
        from models.lessons import Lesson
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({"error": "Lesson not found"}), 404
        
        # Check if user has API key configured
        from utils.api_key_manager import get_user_api_key
        user_sub = session['user']['sub']
        api_key = get_user_api_key(user_sub)
        
        if not api_key:
            return jsonify({"error": "No OpenAI API key configured. Please set your API key in Settings."}), 400
        
        # Create context-aware question
        lesson_context = f"""
Lesson Context:
Title: {lesson.title}
Content: {lesson.content}
Module: {lesson.module.title if lesson.module else 'Unknown Module'}

User Question: {question}

Please answer the user's question based on the lesson content above. If the question is not related to this lesson, please redirect them to ask about the current lesson material.
"""
        
        # Update the request data with the context-aware question
        data['question'] = lesson_context
        
        # Use the existing assistant system
        return ask_route(r)
        
    except Exception as e:
        return jsonify({"error": f"Failed to submit question: {str(e)}"}), 500

@app.route('/list_lessons')
def list_lessons():
    from models.lessons import Lesson
    lessons = Lesson.query.all()
    return render_template('lessons/list.html', lessons=lessons, total_pages=1)

@app.route('/create_lesson')
def create_lesson():
    raise NotImplementedError
    return render_template('lessons/add.html')

@app.route('/edit_lesson/<lesson_id>')
def edit_lesson(lesson_id):
    from models.lessons import Lesson
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404
    return render_template('lessons/edit.html', lesson=lesson, topic=lesson.title)

@app.route('/view_lesson/<lesson_id>')
def view_lesson(lesson_id):
    from models.lessons import Lesson
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404
    
    # Get related lessons from the same module
    other_lessons = Lesson.query.filter_by(module_id=lesson.module_id).filter(Lesson.id != lesson.id).all()
    
    # Convert lesson content to markdown for display
    from utils.convert_to_markdown import convert_to_simple_markdown
    # TODO: Get structured notes from database for this lesson
    notes = convert_to_simple_markdown({"content": lesson.content})
    audio_notes = 'presentation'
    
    # Get user's notes and progress for this lesson if authenticated
    user_notes = ""
    user_has_api_key = False
    user_progress = {'completed': False, 'percentage': 0}
    if 'user' in session:
        try:
            from models.user import User
            from models.lessons import Notes
            user_sub = session['user']['sub']
            user = User.find_by_sub(user_sub)
            if user:
                # Check for user notes
                notes_obj = Notes.query.filter_by(
                    lesson_id=lesson_id, 
                    user_id=user.id
                ).first()
                if notes_obj:
                    user_notes = notes_obj.content
                
                # Check for API key status
                user_has_api_key = bool(user.encrypted_api_key)
                
                # Get user progress for this lesson
                progress = user.get_lesson_progress(lesson_id)
                if progress:
                    user_progress = {
                        'completed': progress.is_completed,
                        'percentage': progress.percentage_completed,
                        'time_spent_minutes': progress.time_spent_minutes,
                        'last_accessed': progress.last_accessed.isoformat() if progress.last_accessed else None
                    }
        except Exception as e:
            print(f"Error loading user data: {e}")
    
    # Create user object with API key status
    user_data = session.get('user', {})
    if user_data:
        user_data = user_data.copy()
        user_data['has_api_key'] = user_has_api_key
    
    return render_template(
        'lessons/view.html',
        lesson=lesson,  # Pass the actual lesson object
        user_progress=user_progress,
        other_lessons=other_lessons,
        user_notes=user_notes,
        audio_notes=audio_notes,
        user=user_data  # Add user to template context
    )

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user' not in session:
        return redirect('/')
    
    # Import User model here to avoid circular imports
    from models.user import User
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400
            
            openai_api_key = data.get('openai_api_key', '').strip()
            
            # Validate API key format (basic validation)
            if openai_api_key and not openai_api_key.startswith('sk-'):
                return jsonify({"success": False, "error": "Invalid OpenAI API key format"}), 400
            
            # Get or create user in database
            user_sub = session['user']['sub']
            user = User.find_by_sub(user_sub)
            
            if not user:
                # Create user if not exists
                user = User.create_or_update(
                    email=session['user']['email'],
                    name=session['user']['name'],
                    sub=user_sub
                )
            
            # Encrypt and store the API key
            user.set_api_key(openai_api_key, MASTER_ENCRYPTION_KEY)
            db.session.commit()
            
            # Update session with API key status
            session['user']['has_api_key'] = bool(openai_api_key)
            
            return jsonify({"success": True, "message": "Settings updated successfully"})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
    
    # Get user from database for display
    user_sub = session['user']['sub']
    user = User.find_by_sub(user_sub)
    
    if user:
        # Add API key status to session user data
        session['user']['has_api_key'] = bool(user.encrypted_api_key)
        display_user = {
            'email': user.email,
            'name': user.name,
            'sub': user.sub,
            'has_api_key': bool(user.encrypted_api_key)
        }
    else:
        display_user = session['user']
        display_user['has_api_key'] = False
    
    return render_template('settings.html', user=display_user, active_page='settings')

@app.route('/audio_notes/<file_name>')
def audio_notes(file_name):
    audio_base_path = 'tests/'
    audio_file = f'{audio_base_path}{file_name}.wav'
    return Response(open(audio_file, 'rb').read(), mimetype="audio/wav")

@app.route('/generate_audio/<lesson_id>')
def generate_audio(lesson_id):
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401
    
    # Get user's API key from database
    from utils.api_key_manager import get_user_api_key
    user_sub = session['user']['sub']
    api_key = get_user_api_key(user_sub)
    
    if not api_key:
        return jsonify({"error": "No OpenAI API key configured. Please set your API key in Settings."}), 400
    
    try:
        # TODO: fetch structured notes from database for this lesson_id
        # For now, using example data
        from utils.example_structured_notes import data as structured_notes
        
        # Generate audio using TTS
        from lib.tts.main import construct_presentation_from_structured_notes
        construct_presentation_from_structured_notes(structured_notes, api_key=api_key)
        
        # Return the generated audio file
        audio_file = 'presentation.wav'
        return Response(open(audio_file, 'rb').read(), mimetype="audio/wav")
        
    except Exception as e:
        return jsonify({"error": f"Audio generation failed: {str(e)}"}), 500

@app.route('/preview_lesson/<lesson_id>')
def preview_lesson(lesson_id):
    # Basically, "view_lesson" but as instructor, not student...
    from models.lessons import Lesson
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404
    
    # Check for API key status
    user_has_api_key = False
    if 'user' in session:
        try:
            from models.user import User
            user_sub = session['user']['sub']
            user = User.find_by_sub(user_sub)
            if user:
                user_has_api_key = bool(user.encrypted_api_key)
        except Exception as e:
            print(f"Error loading user data: {e}")
    
    # Create user object with API key status
    user_data = session.get('user', {})
    if user_data:
        user_data = user_data.copy()
        user_data['has_api_key'] = user_has_api_key
    
    # Create lesson data structure for template (same as view_lesson)
    lesson_data = {
        'id': lesson.id,
        'title': lesson.title,
        'content': lesson.content,
        'content_html': lesson.content,  # TODO: Convert to HTML if needed
        'examples_html': lesson.examples or '',  # Use examples field from model
        'exercises_html': lesson.exercises or '',  # Use exercises field from model
        'learning_objectives': lesson.get_learning_objectives(),
        'estimated_time': {
            'hours': lesson.estimated_time_hours,
            'minutes': lesson.estimated_time_minutes
        },
        'difficulty': lesson.difficulty,
        'tags': lesson.get_tags(),
        'attachments': lesson.get_attachments(),
        'overview': lesson.overview,
        'module_id': lesson.module_id,
        'module_title': lesson.module.title if lesson.module else 'Unknown Module',
        'user_progress': {'completed': False, 'percentage': 0}  # TODO: Implement progress tracking
    }
    
    return render_template('lessons/preview.html', lesson=lesson_data, user=user_data)

@app.route('/list_modules')
def list_modules():
    from models.lessons import Module
    modules = Module.query.all()
    return render_template('modules/list.html', modules=modules, total_pages=1)

@app.route('/create_module', methods=['GET', 'POST'])
def create_module():
    from models.lessons import Module, Course
    from flask import request, flash, redirect, url_for
    
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

@app.route('/edit_module/<module_id>', methods=['GET', 'POST'])
def edit_module(module_id):
    from models.lessons import Module, Course
    from flask import request, flash, redirect, url_for
    
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

@app.route('/view_module/<module_id>')
def view_module(module_id):
    # Redirect to the unified module route
    return redirect(url_for('module', module_id=module_id))

@app.route('/module_complete/<module_id>')
def module_complete(module_id):
    from models.lessons import Module
    module = Module.query.get(module_id)
    if not module:
        return jsonify({"error": "Module not found"}), 404
    return render_template('modules/complete.html', module=module)

@app.route('/lo_chat')
def lo_chat_endpoint():
    return lo_route()

@app.route('/annotated_media/<media_id>')
def annotated_media(media_id):
    from models.lessons import Media
    media = Media.query.get(media_id)
    if not media:
        return jsonify({"error": "Media not found"}), 404
    
    # Build media data structure for template
    media_data = {
        "title": media.title,
        "description": media.description,
        "media_url": media.media_url,
        "annotations": media.get_annotations(),
        "segments": media.get_segments()
    }
    
    return render_template('media/annotated.html', media=media_data)

@app.route('/')
def index():
    if 'user' in session:
        # Redirect to dashboard instead of rendering dashboard template directly
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
def login():
    print("DEBUG: auth_callback_route called", DEBUG)
    if DEBUG:
        # Simulate a user session in development mode
        # Preserve existing mode if it exists
        current_mode = session.get('user', {}).get('mode', 'student')
        session['user'] = {
            "email": "devuser@example.com",
            "name": "Dev User",
            "sub": "local-dev-user-id",
            "mode": current_mode
        }
        return redirect(url_for('index'))
    return redirect(COGNITO_LOGIN_URL)

@app.route('/callback')
def callback():
    return auth_callback_route()

@app.route('/logout')
def logout():
    return auth_logout_route()

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/')
    user = session['user']
    return render_template('profile.html', user=user)

@app.route('/update_bio', methods=['POST'])
def update_bio():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session['user']
    bio = request.json.get('bio', '')
    # Update the user's bio in the database
    user['bio'] = bio
    session['user'] = user
    return jsonify({"message": "Bio updated successfully"})


app.jinja_env.globals.update(enumerate=enumerate)
app.jinja_env.globals.update(len=len)

@app.context_processor
def inject_modules():
    """Inject modules into all template contexts"""
    from models.lessons import Module
    try:
        # Only fetch modules if we have a database connection
        if db.engine:
            modules = Module.query.all()
        else:
            modules = []
    except Exception as e:
        print(f"Error fetching modules: {e}")
        modules = []
    
    return {'modules': modules}

@app.context_processor
def inject_user():
    """Inject user into all template contexts"""
    return {'user': session.get('user')}


@app.route('/hello')
def publish_hello():
    msg = {"message": "Hello!"}
    print("Publishing message...", msg)
    sse.publish(msg, type='greeting')
    return "Message sent!"

@app.route('/test-dashboard')
def test_dashboard():
    """Simple test route to verify template rendering"""
    test_data = {
        'progress_summary': {
            'completed_lessons': 5,
            'total_lessons': 10,
            'completion_percentage': 50
        },
        'next_session': {
            'lesson_title': 'Test Lesson',
            'module_title': 'Test Module',
            'lesson_id': 1,
            'module_id': 1
        },
        'achievements': {
            'modules_completed': 2,
            'quizzes_passed': 3
        },
        'recent_activity': [
            {
                'type': 'Lesson Completed',
                'lesson_title': 'Test Lesson 1',
                'time_ago': '2 hours ago',
                'percentage': 100,
                'is_completed': True
            }
        ]
    }
    
    print("=== TEST DASHBOARD DEBUG ===")
    print(f"Test data: {test_data}")
    print("============================")
    
    return render_template('dashboard.html', 
                         active_page='dashboard', 
                         user={'name': 'Test User'},
                         **test_data)

@app.route('/test-dashboard-minimal')
def test_dashboard_minimal():
    """Test with minimal template"""
    test_data = {
        'progress_summary': {
            'completed_lessons': 5,
            'total_lessons': 10,
            'completion_percentage': 50
        },
        'achievements': {
            'modules_completed': 2,
            'quizzes_passed': 3
        }
    }
    
    return render_template('dashboard_test.html', 
                         user={'name': 'Test User'},
                         **test_data)

@app.route('/session-status')
def session_status():
    """Check current session status"""
    return {
        'session_keys': list(session.keys()),
        'user_in_session': 'user' in session,
        'user_data': session.get('user', None),
        'debug_mode': DEBUG
    }

@app.route('/create-test-user')
def create_test_user():
    """Create the test user in the database"""
    try:
        from models.user import User
        
        # Create the test user that matches the session
        user = User.create_or_update(
            email="devuser@example.com",
            name="Dev User", 
            sub="local-dev-user-id"
        )
        
        return {
            'success': True,
            'user_created': user.id,
            'message': f'User created/updated: {user.name} (ID: {user.id})'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@app.errorhandler(400)
def handle_400(e):
    print("400 Error:", e)
    print("Request data:", request.data)
    return jsonify({"error": "Bad request"}), 400

@app.route('/list_courses')
def list_courses():
    from models.lessons import Course
    courses = Course.query.all()
    return render_template('courses/list.html', courses=courses, total_pages=1)

@app.route('/create_course', methods=['GET', 'POST'])
def create_course():
    from models.lessons import Course
    from flask import request, flash, redirect, url_for
    
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

@app.route('/edit_course/<course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
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

@app.route('/view_course/<course_id>')
def view_course(course_id):
    from models.lessons import Course
    course = Course.query.get(course_id)
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('list_courses'))
    return render_template('courses/view.html', course=course)

@app.route('/delete_course/<course_id>', methods=['POST'])
def delete_course(course_id):
    from models.lessons import Course
    from flask import request, flash, redirect, url_for
    
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

@app.route('/api/chat_history/<lesson_id>', methods=['GET', 'POST', 'DELETE'])
def chat_history_api(lesson_id):
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401
    from models.user import User
    user_sub = session['user']['sub']
    user = User.find_by_sub(user_sub)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if request.method == 'GET':
        chat = user.get_chat_history(lesson_id)
        if not chat:
            return jsonify({"messages": []})
        # Convert messages to the format expected by frontend
        messages = []
        for message in chat.messages:
            messages.append({
                'type': message.message_type,
                'content': message.content,
                'timestamp': message.created_at.isoformat() if message.created_at else None
            })
        return jsonify({"messages": messages})

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'type' not in data or 'content' not in data:
            return jsonify({"error": "Missing type or content in request body"}), 400
        message_type = data['type']  # 'user' or 'assistant'
        content = data['content']
        chat = user.add_chat_message(lesson_id, message_type, content)
        # Return updated messages in the format expected by frontend
        messages = []
        for message in chat.messages:
            messages.append({
                'type': message.message_type,
                'content': message.content,
                'timestamp': message.created_at.isoformat() if message.created_at else None
            })
        return jsonify({"success": True, "messages": messages})

    elif request.method == 'DELETE':
        chat = user.clear_chat_history(lesson_id)
        return jsonify({"success": True, "messages": []})

    else:
        return jsonify({"error": "Invalid request method."}), 400
