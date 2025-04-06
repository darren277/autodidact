""""""
import base64
import json
import threading
import asyncio
from urllib import parse

import requests
from flask import Flask, request, Response, render_template, jsonify, render_template_string, session, redirect, url_for
from flask_sse import sse

import redis

from lib.assistant.main import AssistantHandler
from lib.completions.main import Completions
from lib.edu.blooms import lo_chat

from lib.tts.main import TTS
from lib.tts.personalities import descriptors
from routes.api.courses import courses_route, course_route
from routes.api.lessons import lessons_route, lesson_route
from routes.api.modules import modules_route, module_route
from routes.assistant import ask_route, stream_route
from routes.auth import auth_callback_route, auth_logout_route
from utils.example_media_annotation import example_media_annotation
from utils.example_module import example_module_progress, example_module_lesson_cards, example_module_resources

from utils.example_structured_notes import data

from settings import REDIS_URL, ENABLE_CORS, APP_SECRET_KEY, LOGOUT_URI, COGNITO_LOGIN_URL
from settings import PG_USER, PG_PASS, PG_HOST, PG_PORT, PG_DB
from settings import COGNITO_DOMAIN, CLIENT_ID, REDIRECT_URI, CLIENT_SECRET

from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy

from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

csrf = CSRFProtect(app)

app.secret_key = APP_SECRET_KEY




if ENABLE_CORS:
    #CORS(app, supports_credentials=True)
    #CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["*"]}})
    CORS(app)



app.config["REDIS_URL"] = REDIS_URL

r = redis.StrictRedis(host='localhost', port=6379, db=0)

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


'''
<article>
    <header>
        <div class="leftheader">Cues</div>
        <div class="rightheader">Date: {{ date }}. Topic: {{ topic }}.</div>
    </header>
    {% for s, section in enumerate(sections) %}
    <section>
        {% for i, part in enumerate(section.parts) %}
        <div class="leftmargin" id="leftmargin{{i}}">{{part.lm}}</div><div class="main" id="main{{i}}">{{part.main}}</div>
        {% endfor %}
        <footer>Summary: {{section.summary}}</footer>
    </section>
    {% endfor %}
</article>
'''


def convert_to_simple_markdown(data):
    markdown = f"# {data['topic']}\n\n"
    for section in data['sections']:
        for part in section['parts']:
            if 'title' in part:
                markdown += f"## {part['title']}\n\n"
            markdown += f"### {part['lm']}\n\n"
            markdown += f"{part['main']}\n\n"
    return markdown


@app.route('/notes/cornell_notes/<notes_id>')
def cornell_notes(notes_id):
    return render_template('notes/cornell.html', **data)

@app.route('/notes/digital_notebook/<notes_id>')
def digital_notebook(notes_id):
    return render_template('notes/digital-notebook.html', **data)

@app.route('/notes/mindmap/<notes_id>')
def mindmap(notes_id):
    return render_template('notes/mindmap.html', **data)

@app.route('/notes/stickynotes/<notes_id>')
def stickynotes(notes_id):
    return render_template('notes/stickynotes.html', **data)

@app.route('/notes/vintage_cards/<notes_id>')
def vintage_cards(notes_id):
    return render_template('notes/vintage-cards.html', **data)

@app.route('/notes/augmented/<notes_id>')
def augmented(notes_id):
    return render_template('notes/augmented.html', **data)


@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json

    system_prompt = data.get('systemPrompt', None)
    if not system_prompt:
        return jsonify({"error": "No system prompt provided."})
    completions = Completions('gpt-4o', system_prompt)

    user_notes = data.get('userNotes', None)
    if not user_notes:
        return jsonify({"error": "No user notes provided."})
    user_notes_string = json.dumps(user_notes)
    result = completions.complete(user_notes_string)

    return jsonify(dict(summary=result))


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    from utils.convert_obsidian import convert_to_obsidian, merge_adjacent_cells, parse_cornell_markdown
    if request.method == 'POST':
        data = request.json
        if data:
            direction = data.get('direction', None)

            if direction != 'json2obsidian' and direction != 'obsidian2json':
                return jsonify({"error": "Invalid conversion direction."})

            content_string = data.get('content', None)

            if direction == 'obsidian2json':
                try:
                    result = merge_adjacent_cells(parse_cornell_markdown(content_string))
                    return jsonify(result)
                except Exception as e:
                    return jsonify({"error": str(e)})
            elif direction == 'json2obsidian':
                try:
                    content = json.loads(content_string)
                except Exception as e:
                    return jsonify({"error": f"Error parsing JSON: {str(e)}"})
                try:
                    result = convert_to_obsidian(content)
                    return jsonify(result)
                except Exception as e:
                    return jsonify({"error": str(e)})
            else:
                return jsonify({"error": "Invalid conversion direction."})
        else:
            return jsonify({"error": "No data provided."})
    else:
        return render_template('convert-notes.html')


@app.route('/tts', methods=['GET', 'POST'])
def tts():
    if request.method == 'GET':
        return render_template('tts.html')
    else:
        message = request.form.get('message', 'Hello, world!')
        _tts = TTS("gpt-4o-mini-tts", "alloy", descriptors['pirate'])
        audio = asyncio.run(_tts.speak(message))
        audio_bytes = audio
        response = Response(audio_bytes, mimetype="audio/wav")
        response.headers["Content-Disposition"] = "attachment; filename=speech.wav"
        return response


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', active_page='dashboard')

@app.route('/module/<module_id>')
def module(module_id):
    return render_template(
        f'module.html',
        active_page=f'module_{module_id}',
        title="Module 1: Introduction to Lorem Ipsum",
        page_title="Module 1: Introduction to Lorem Ipsum",
        module_progress=example_module_progress,
        module_download_materials_link="#",
        module_take_quiz_link="#",
        module_description="""
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam varius massa vitae semper consectetur. Proin lobortis, nunc nec vehicula posuere, turpis velit scelerisque nisi, et convallis lectus massa eget eros.</p>
        <p>This module will cover fundamental concepts of Lorem Ipsum and provide practical exercises to reinforce your understanding.</p>
        """,
        lesson_cards=example_module_lesson_cards,
        resources=example_module_resources
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


@app.route('/list_lessons')
def list_lessons():
    from models.lessons import Lesson
    #lessons = Lesson.query.all()
    demo_lessons = [
        {"id": 1, "title": "Lesson 1", "content": "This is the content for Lesson 1."},
        {"id": 2, "title": "Lesson 2", "content": "This is the content for Lesson 2."},
        {"id": 3, "title": "Lesson 3", "content": "This is the content for Lesson 3."},
        {"id": 4, "title": "Lesson 4", "content": "This is the content for Lesson 4."},
        {"id": 5, "title": "Lesson 5", "content": "This is the content for Lesson 5."}
    ]
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
    lesson = {"id": 1, "title": "Lesson 1", "content": "This is the content for Lesson 1."}
    lesson.update(
        estimated_time=dict(
            hours=1,
            minutes=30
        ),
        difficulty="Intermediate",
        tags=["Python", "Programming", "Web Development"]
    )
    topic = "Python Programming"
    return render_template('lessons/edit.html', lesson=lesson, topic=topic)

@app.route('/view_lesson/<lesson_id>')
def view_lesson(lesson_id):
    from models.lessons import Lesson
    #lesson = Lesson.query.get(lesson_id)
    lesson = {"id": 1, "title": "Lesson 1", "content": "This is the content for Lesson 1."}
    lesson.update(
        estimated_time=dict(
            hours=1,
            minutes=30
        ),
        difficulty="Intermediate",
        tags=["Python", "Programming", "Web Development"]
    )
    user_progress = dict(
        completed=True,
    )
    other_lessons = []
    notes = convert_to_simple_markdown(data)
    audio_notes = 'presentation'
    return render_template(
        'lessons/view.html',
        lesson=lesson,
        user_progress=user_progress,
        other_lessons=other_lessons,
        user_notes=notes,
        audio_notes=audio_notes
    )


@app.route('/audio_notes/<file_name>')
def audio_notes(file_name):
    audio_base_path = 'tests/'
    audio_file = f'{audio_base_path}{file_name}.wav'
    return Response(open(audio_file, 'rb').read(), mimetype="audio/wav")

@app.route('/generate_audio/<lesson_id>')
def generate_audio(lesson_id):
    # TODO: get userId from session and concatenate with lesson_id...
    user_id = 1
    file_name = f'{user_id}_{lesson_id}'
    audio_base_path = 'tests/'
    audio_file = f'{audio_base_path}{file_name}.wav'
    # fetch notes from database...
    # TODO: construct_presentation_from_structured_notes(structured_notes: StructuredNotes or dict)
    return Response(open(audio_file, 'rb').read(), mimetype="audio/wav")


@app.route('/preview_lesson/<lesson_id>')
def preview_lesson(lesson_id):
    # Basically, "view_lesson" but as instructor, not student...
    # TODO...
    from models.lessons import Lesson
    #lesson = Lesson.query.get(lesson_id)
    lesson = {"id": 1, "title": "Lesson 1", "content": "This is the content for Lesson 1."}
    lesson.update(
        estimated_time=dict(
            hours=1,
            minutes=30
        ),
        difficulty="Intermediate",
        tags=["Python", "Programming", "Web Development"]
    )
    return render_template('lessons/preview.html', lesson=lesson)

@app.route('/list_modules')
def list_modules():
    from models.lessons import Module
    #modules = Module.query.all()
    demo_modules = [
        {"id": 1, "title": "Module 1"},
        {"id": 2, "title": "Module 2"},
        {"id": 3, "title": "Module 3"},
        {"id": 4, "title": "Module 4"},
        {"id": 5, "title": "Module 5"}
    ]
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

fmt1 = ['Knowledge', 'Comprehension', 'Application', 'Analysis', 'Synthesis', 'Evaluation']
fmt2 = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']

mapping_fmt2_to_fmt1 = {
    'Remember': 'Knowledge',
    'Understand': 'Comprehension',
    'Apply': 'Application',
    'Analyze': 'Analysis',
    'Evaluate': 'Evaluation',
    'Create': 'Synthesis'
}

@app.route('/lo_chat')
def lo_chat_endpoint():
    stage = request.args.get('stage', None)
    topic = request.args.get('topic', None)

    if not stage or not topic:
        return jsonify({"error": "Invalid request."}), 400

    if stage.lower() not in [stg.lower() for stg in fmt1+fmt2]:
        return jsonify({"error": "Invalid stage."}), 400

    if stage in fmt2:
        stage = mapping_fmt2_to_fmt1[stage]

    response = lo_chat(stage, topic)

    return jsonify(dict(objective=response))




@app.route('/annotated_media/<media_id>')
def annotated_media(media_id):
    return render_template('media/annotated.html', media=example_media_annotation)


@app.route('/')
def index():
    if 'user' in session:
        return render_template('profile.html', user=session['user'])
    return render_template('login.html')


@app.route('/login')
def login():
    return redirect(COGNITO_LOGIN_URL)


@app.route('/callback')
def callback():
    return auth_callback_route()


@app.route('/logout')
def logout():
    return auth_logout_route()



# add enumerate() to Jinja...
app.jinja_env.globals.update(enumerate=enumerate)
# add len() to Jinja...
app.jinja_env.globals.update(len=len)


@app.route('/hello')
def publish_hello():
    msg = {"message": "Hello!"}
    print("Publishing message...", msg)
    sse.publish(msg, type='greeting')
    return "Message sent!"

