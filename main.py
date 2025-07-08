""""""
from flask import Flask, request, Response, render_template, jsonify, session, redirect, url_for, flash
from flask_sse import sse

import redis

from routes.api.courses import courses_route, course_route
from routes.api.lessons import lessons_route, lesson_route, mark_lesson_complete_route, update_lesson_progress_route, \
    get_lesson_progress_route, submit_question_route, chat_history_route
from routes.api.modules import modules_route, module_route
from routes.api.notes import save_notes_route, get_notes_route
from routes.assistant import ask_route, stream_route
from routes.auth import auth_callback_route, auth_logout_route
from routes.convert_notes import convert_notes_route
from routes.lo import lo_route
from routes.summarize import summarize_route
from routes.testing import test_dashboard_route, test_dashboard_minimal_route, create_test_user_route
from routes.tts import tts_route, generate_audio_route
from routes.user_settings import settings_route
from routes.views.courses import create_course_route, edit_course_route, delete_course_route
from routes.views.dashboard import dashboard_route, toggle_mode_route
from routes.views.lessons import view_lesson_route, preview_lesson_route
from routes.views.modules import create_module_route, edit_module_route, view_module_route
from routes.views.notes import cornell_notes_route, digital_notebook_route, mindmap_route, stickynotes_route, \
    vintage_cards_route, augmented_notes_route
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
    return toggle_mode_route()

@app.route('/notes/cornell_notes/<notes_id>')
def cornell_notes(notes_id):
    return cornell_notes_route(notes_id)

@app.route('/api/notes/cornell_notes/<notes_id>')
def api_cornell_notes(notes_id):
    return cornell_notes_route(notes_id)

@app.route('/notes/digital_notebook/<notes_id>')
def digital_notebook(notes_id):
    return digital_notebook_route(notes_id)

@app.route('/api/notes/digital_notebook/<notes_id>')
def api_digital_notebook(notes_id):
    return digital_notebook_route(notes_id)

@app.route('/notes/mindmap/<notes_id>')
def mindmap(notes_id):
    return mindmap_route(notes_id)

@app.route('/api/notes/mindmap/<notes_id>')
def api_mindmap(notes_id):
    return mindmap_route(notes_id)

@app.route('/notes/stickynotes/<notes_id>')
def stickynotes(notes_id):
    return stickynotes_route(notes_id)

@app.route('/api/notes/stickynotes/<notes_id>')
def api_stickynotes(notes_id):
    return stickynotes_route(notes_id)

@app.route('/notes/vintage_cards/<notes_id>')
def vintage_cards(notes_id):
    return vintage_cards_route(notes_id)

@app.route('/api/notes/vintage_cards/<notes_id>')
def api_vintage_cards(notes_id):
    return vintage_cards_route(notes_id)

@app.route('/notes/augmented/<notes_id>')
def augmented(notes_id):
    return augmented_notes_route(notes_id)

@app.route('/api/notes/augmented/<notes_id>')
def api_augmented(notes_id):
    return augmented_notes_route(notes_id)

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
    return dashboard_route()

@app.route('/module/<module_id>')
def module(module_id):
    return view_module_route(module_id)

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
    return save_notes_route(db)

@app.route('/api/get_notes/<lesson_id>', methods=['GET'])
def get_notes(lesson_id):
    return get_notes_route(db, lesson_id)

@app.route('/api/mark_lesson_complete', methods=['POST'])
def mark_lesson_complete():
    return mark_lesson_complete_route()

@app.route('/api/update_lesson_progress', methods=['POST'])
def update_lesson_progress():
    return update_lesson_progress_route()

@app.route('/api/get_lesson_progress/<lesson_id>', methods=['GET'])
def get_lesson_progress(lesson_id):
    return get_lesson_progress_route(lesson_id)

@app.route('/api/submit_question', methods=['POST'])
def submit_question():
    return submit_question_route(r)

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
    return view_lesson_route(lesson_id)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return settings_route(db)

@app.route('/audio_notes/<file_name>')
def audio_notes(file_name):
    audio_base_path = 'tests/'
    audio_file = f'{audio_base_path}{file_name}.wav'
    return Response(open(audio_file, 'rb').read(), mimetype="audio/wav")

@app.route('/generate_audio/<lesson_id>')
def generate_audio(lesson_id):
    return generate_audio_route(lesson_id)

@app.route('/preview_lesson/<lesson_id>')
def preview_lesson(lesson_id):
    return preview_lesson_route(lesson_id)

@app.route('/list_modules')
def list_modules():
    from models.lessons import Module
    modules = Module.query.all()
    return render_template('modules/list.html', modules=modules, total_pages=1)

@app.route('/create_module', methods=['GET', 'POST'])
def create_module():
    return create_module_route(db)

@app.route('/edit_module/<module_id>', methods=['GET', 'POST'])
def edit_module(module_id):
    return edit_module_route(db, module_id)

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
    return test_dashboard_route()

@app.route('/test-dashboard-minimal')
def test_dashboard_minimal():
    return test_dashboard_minimal_route()

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
    return create_test_user_route()


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
    return create_course_route(db)

@app.route('/edit_course/<course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    return edit_course_route(db, course_id)

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
    return delete_course_route(db, course_id)

@app.route('/api/chat_history/<lesson_id>', methods=['GET', 'POST', 'DELETE'])
def chat_history_api(lesson_id):
    return chat_history_route(lesson_id)

# CALENDAR ROUTES #

# Import calendar functions
from routes.calendar import (
    calendar_view, get_events, create_event, update_event, 
    delete_event, get_event_types
)

@app.route('/calendar')
def calendar():
    return calendar_view()

@app.route('/api/calendar/events', methods=['GET'])
def api_calendar_events():
    return get_events()

@app.route('/api/calendar/events', methods=['POST'])
def api_calendar_create_event():
    return create_event()

@app.route('/api/calendar/events/<int:event_id>', methods=['PUT'])
def api_calendar_update_event(event_id):
    return update_event(event_id)

@app.route('/api/calendar/events/<int:event_id>', methods=['DELETE'])
def api_calendar_delete_event(event_id):
    return delete_event(event_id)

@app.route('/api/calendar/event-types', methods=['GET'])
def api_calendar_event_types():
    return get_event_types()
