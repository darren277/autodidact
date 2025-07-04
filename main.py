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
from utils.example_lesson import example_lesson
from utils.example_media_annotation import example_media_annotation
from utils.example_module import example_module

from utils.example_structured_notes import data

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
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        data = request.get_json()
        if data and 'mode' in data:
            new_mode = data['mode']
            if new_mode in ['student', 'teacher']:
                session['user']['mode'] = new_mode
                return jsonify({"message": "Mode toggled successfully", "mode": new_mode})
            else:
                return jsonify({"error": "Invalid mode"}), 400
        else:
            # Fallback to toggle behavior if no mode specified
            if session['user']['mode'] == 'student':
                session['user']['mode'] = 'teacher'
            else:
                session['user']['mode'] = 'student'
            return jsonify({"message": "Mode toggled successfully", "mode": session['user']['mode']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/notes/cornell_notes/<notes_id>')
def cornell_notes(notes_id):
    return render_template('notes/cornell.html', **data)

@app.route('/api/notes/cornell_notes/<notes_id>')
def api_cornell_notes(notes_id):
    from utils.example_structured_notes import data
    return render_template('notes/cornell.html', **data)

@app.route('/notes/digital_notebook/<notes_id>')
def digital_notebook(notes_id):
    return render_template('notes/digital-notebook.html', **data)

@app.route('/api/notes/digital_notebook/<notes_id>')
def api_digital_notebook(notes_id):
    from utils.example_structured_notes import data
    return render_template('notes/digital-notebook.html', **data)

@app.route('/notes/mindmap/<notes_id>')
def mindmap(notes_id):
    return render_template('notes/mindmap.html', **data)

@app.route('/api/notes/mindmap/<notes_id>')
def api_mindmap(notes_id):
    from utils.example_structured_notes import data
    return render_template('notes/mindmap.html', **data)

@app.route('/notes/stickynotes/<notes_id>')
def stickynotes(notes_id):
    return render_template('notes/stickynotes.html', **data)

@app.route('/api/notes/stickynotes/<notes_id>')
def api_stickynotes(notes_id):
    from utils.example_structured_notes import data
    return render_template('notes/stickynotes.html', **data)

@app.route('/notes/vintage_cards/<notes_id>')
def vintage_cards(notes_id):
    return render_template('notes/vintage-cards.html', **data)

@app.route('/api/notes/vintage_cards/<notes_id>')
def api_vintage_cards(notes_id):
    from utils.example_structured_notes import data
    return render_template('notes/vintage-cards.html', **data)

@app.route('/notes/augmented/<notes_id>')
def augmented(notes_id):
    return render_template('notes/augmented.html', **data)

@app.route('/api/notes/augmented/<notes_id>')
def api_augmented(notes_id):
    from utils.example_structured_notes import data
    return render_template('notes/augmented.html', **data)

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
    user = session['user'] if session else None
    return render_template('dashboard.html', active_page='dashboard', user=user)

@app.route('/module/<module_id>')
def module(module_id):
    module_data = example_module
    return render_template(
        f'module.html',
        active_page=f'module_{module_id}',
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
        
        if not lesson_id:
            return jsonify({"error": "Lesson ID is required"}), 400
        
        # For now, just return a success response with updated progress
        # TODO: Implement actual progress tracking in database
        return jsonify({
            "success": True, 
            "message": "Lesson marked as complete",
            "new_percentage": 100
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to mark lesson complete: {str(e)}"}), 500

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
        
        # Use the existing assistant system
        return ask_route(r)
        
    except Exception as e:
        return jsonify({"error": f"Failed to submit question: {str(e)}"}), 500

@app.route('/list_lessons')
def list_lessons():
    from models.lessons import Lesson
    #lessons = Lesson.query.all()
    demo_lessons = [{"id": i, "title": f"Lesson {i}", "content": f"This is the content for Lesson {i}."} for i in range(1, 6)]
    lessons = demo_lessons
    return render_template('lessons/list.html', lessons=lessons, total_pages=1)

@app.route('/create_lesson')
def create_lesson():
    raise NotImplementedError
    return render_template('lessons/add.html')

@app.route('/edit_lesson/<lesson_id>')
def edit_lesson(lesson_id):
    from models.lessons import Lesson
    #lesson = Lesson.query.get(lesson_id)
    lesson = example_lesson
    return render_template('lessons/edit.html', lesson=lesson, topic=lesson['topic'])

@app.route('/view_lesson/<lesson_id>')
def view_lesson(lesson_id):
    from models.lessons import Lesson
    #lesson = Lesson.query.get(lesson_id)
    lesson = example_lesson
    other_lessons = []
    notes = convert_to_simple_markdown(data)
    audio_notes = 'presentation'
    
    # Get user's notes for this lesson if authenticated
    user_notes = ""
    if 'user' in session:
        try:
            from models.user import User
            from models.lessons import Notes
            user_sub = session['user']['sub']
            user = User.find_by_sub(user_sub)
            if user:
                notes_obj = Notes.query.filter_by(
                    lesson_id=lesson_id, 
                    user_id=user.id
                ).first()
                if notes_obj:
                    user_notes = notes_obj.content
        except Exception as e:
            print(f"Error loading user notes: {e}")
    
    return render_template(
        'lessons/view.html',
        lesson=lesson,
        user_progress=lesson['user_progress'],
        other_lessons=other_lessons,
        user_notes=user_notes,
        audio_notes=audio_notes
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
    # TODO...
    from models.lessons import Lesson
    #lesson = Lesson.query.get(lesson_id)
    lesson = example_lesson
    return render_template('lessons/preview.html', lesson=lesson)

@app.route('/list_modules')
def list_modules():
    from models.lessons import Module
    #modules = Module.query.all()
    demo_modules = [{"id": 1, "title": f"Module {i}"} for i in range(1, 6)]
    modules = demo_modules
    return render_template('modules/list.html', modules=modules, total_pages=1)

@app.route('/create_module')
def create_module():
    raise NotImplementedError
    return render_template('modules/add.html')

@app.route('/edit_module/<module_id>')
def edit_module(module_id):
    from models.lessons import Module
    module = Module.query.get(module_id)
    return render_template('modules/edit.html', module=module)

@app.route('/view_module/<module_id>')
def view_module(module_id):
    from models.lessons import Module
    #module = Module.query.get(module_id)
    module = {"id": 1, "title": "Module 1"}
    return render_template('modules/view.html', module=module)

@app.route('/module_complete/<module_id>')
def module_complete(module_id):
    from models.lessons import Module
    #module = Module.query.get(module_id)
    module = {"id": 1, "title": "Module 1"}
    return render_template('modules/complete.html', module=module)

@app.route('/lo_chat')
def lo_chat_endpoint():
    return lo_route()

@app.route('/annotated_media/<media_id>')
def annotated_media(media_id):
    return render_template('media/annotated.html', media=example_media_annotation)

@app.route('/')
def index():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return render_template('index.html')

@app.route('/login')
def login():
    print("DEBUG: auth_callback_route called", DEBUG)
    if DEBUG:
        # Simulate a user session in development mode
        session['user'] = {
            "email": "devuser@example.com",
            "name": "Dev User",
            "sub": "local-dev-user-id",
            "mode": "student"
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


@app.route('/hello')
def publish_hello():
    msg = {"message": "Hello!"}
    print("Publishing message...", msg)
    sse.publish(msg, type='greeting')
    return "Message sent!"


@app.errorhandler(400)
def handle_400(e):
    print("400 Error:", e)
    print("Request data:", request.data)
    return jsonify({"error": "Bad request"}), 400
