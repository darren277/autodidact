""""""
import json
import threading
import asyncio

from flask import Flask, request, Response, render_template, jsonify, render_template_string
from flask_sse import sse

import redis

from lib.assistant.main import AssistantHandler
from lib.completions.main import Completions

from lib.tts.main import TTS
from lib.tts.personalities import descriptors

from tests.example_structured_notes import data

from settings import REDIS_URL, ENABLE_CORS
from settings import PG_USER, PG_PASS, PG_HOST, PG_PORT, PG_DB

from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



if ENABLE_CORS:
    #CORS(app, supports_credentials=True)
    #CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["*"]}})
    CORS(app)



app.config["REDIS_URL"] = REDIS_URL

r = redis.StrictRedis(host='localhost', port=6379, db=0)

#app.register_blueprint(sse, url_prefix='/stream')

@app.route('/stream1')
def stream1():
    def generate():
        for i in range(5):
            yield f"data: Event {i}\n\n"
    return Response(generate(), content_type='text/event-stream')

@app.route('/stream')
def stream():
    def generate():
        pubsub = r.pubsub()
        pubsub.subscribe('channel')
        for message in pubsub.listen():
            yield f"data: {message['data']}\n\n"
    return Response(generate(), content_type='text/event-stream')

#app.run(host='0.0.0.0', port=8000)

#quit(54)


@app.route('/')
def hello_world():
    return render_template('index.html')
    #return open('templates/index.html').read()


@app.route('/ask', methods=['POST'])
def ask():

    question = request.form.get('question')
    if not question:
        question = request.json.get('question', None)
        if not question:
            return Response("Invalid request", status=400)
    assistant_id = request.form.get('assistant_id', None)

    assistant_handler = AssistantHandler(question, assistant_id)
    assistant_handler._r = r
    assistant_handler.initialize_app(app)

    # You can use a unique identifier per user/session
    py_thread_id = request.remote_addr

    threading.Thread(
        target=assistant_handler.run,
        args=(py_thread_id,)
    ).start()

    #return render_template('response.html', question=question, thread_id=py_thread_id)
    return ""


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


@app.route('/cornell_notes')
def cornell_notes():
    return render_template('notes/cornell.html', **data)

@app.route('/digital_notebook')
def digital_notebook():
    return render_template('notes/digital-notebook.html', **data)

@app.route('/mindmap')
def mindmap():
    return render_template('notes/mindmap.html', **data)

@app.route('/stickynotes')
def stickynotes():
    return render_template('notes/stickynotes.html', **data)

@app.route('/vintage_cards')
def vintage_cards():
    return render_template('notes/vintage-cards.html', **data)

@app.route('/augmented')
def augmented():
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
        return render_template_string("""
<html>
<head>
    <title>Convert</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        textarea {
            width: 100%;
            height: 300px;
        }
    </style>
</head>
<body>
    <h1>Convert</h1>
    <form method="POST">
        <label for="direction">Direction:</label>
        <select name="direction">
            <option value="none">Select...</option>
            <option value="json2obsidian">JSON to Obsidian</option>
            <option value="obsidian2json">Obsidian to JSON</option>
        </select>
        <br>
        <label for="content">Content:</label>
        <textarea name="content"></textarea>
        <br>
        <button type="submit">Convert</button>
    </form>
    
    <h2>Output</h2>
    <pre id="output"></pre>
    
    <script>
        const form = document.querySelector('form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const response = await fetch('/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(Object.fromEntries(formData))
            });
            const data = await response.json();
            document.getElementById('output').innerText = JSON.stringify(data, null, 2);
        });
    </script>
    
    <h2>Example JSON</h2>
    <pre>
    {{ example_json }}
    </pre>
    
    <h2>Example Obsidian</h2>
    <pre>
    {{ example_obsidian }}
    </pre>
</body>
</html>
""")


@app.route('/tts', methods=['GET', 'POST'])
def tts():
    if request.method == 'GET':
        return render_template_string("""
<html>
<head>
    <title>TTS</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
    </style>
</head>
<body>
    <h1>TTS</h1>
    <form method="POST">
        <label for="personality">Personality:</label>
        <select name="personality">
            <option value="default">Default</option>
            <option value="pirate">Pirate</option>
        </select>
        <label for="message">Message:</label>
        <textarea name="message"></textarea>
        <br>
        <button type="submit">Speak</button>
    </form>
    
    <h2>Output</h2>
    <audio controls>
        <source src="" type="audio/wav">
        Your browser does not support the audio element.
    </audio>
    
    <script>
        const form = document.querySelector('form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const response = await fetch('/tts', {
                method: 'POST',
                body: formData
            });
            const audio = await response.blob();
            const audioElement = document.querySelector('audio');
            audioElement.src = URL.createObjectURL(audio);
            audioElement.play();
        });
    </script>
</body>
</html>
""")
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
    module_progress = {
        "completed": 2,
        "total": 5,
        "percentage": 40
    }

    module_1_lesson_cards = [
        {
            "status": "completed",
            "icon": "✓",
            "title": "1. Introduction to Lorem Ipsum",
            "description": "Learn the basic principles and history of Lorem Ipsum.",
            "duration": "15 min",
            "action": "Review"
        },
        {
            "status": "completed",
            "icon": "✓",
            "title": "2. Dolor Sit Amet Techniques",
            "description": "Explore various techniques used in Dolor Sit Amet methodology.",
            "duration": "20 min",
            "action": "Review"
        },
        {
            "status": "current",
            "icon": "•",
            "title": "3. Practical Applications",
            "description": "Apply your knowledge to real-world scenarios and case studies.",
            "duration": "25 min",
            "action": "Continue"
        },
        {
            "status": "",
            "icon": "",
            "title": "4. Advanced Concepts",
            "description": "Dive deeper into complex aspects of Lorem Ipsum Dolor.",
            "duration": "30 min",
            "action": "Start"
        },
        {
            "status": "",
            "icon": "",
            "title": "5. Review & Assessment",
            "description": "Consolidate your learning and test your knowledge.",
            "duration": "20 min",
            "action": "Start"
        },
        {
            "status": "completed",
            "icon": "✓",
            "title": "6. Final Exam",
            "description": "Test your knowledge with a comprehensive exam.",
            "duration": "1 hour",
            "action": "Review"
        }
    ]

    module_1_resources = [
        {
            "icon": "📄",
            "title": "Lorem Ipsum: A Comprehensive Guide",
            "description": "A detailed reference document covering all aspects of Lorem Ipsum",
            "link": "#",
            "action": "View"
        },
        {
            "icon": "🎥",
            "title": "Video Tutorial: Dolor Sit Amet in Practice",
            "description": "Watch an expert demonstrate key techniques",
            "link": "#",
            "action": "Watch"
        },
        {
            "icon": "🔗",
            "title": "External Reading: History of Lorem Ipsum",
            "description": "An in-depth article on the origins and evolution of Lorem Ipsum",
            "link": "#",
            "action": "Visit"
        }
    ]

    return render_template(
        f'module.html',
        active_page=f'module_{module_id}',
        title="Module 1: Introduction to Lorem Ipsum",
        page_title="Module 1: Introduction to Lorem Ipsum",
        module_progress=module_progress,
        module_download_materials_link="#",
        module_take_quiz_link="#",
        module_description="""
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam varius massa vitae semper consectetur. Proin lobortis, nunc nec vehicula posuere, turpis velit scelerisque nisi, et convallis lectus massa eget eros.</p>
        <p>This module will cover fundamental concepts of Lorem Ipsum and provide practical exercises to reinforce your understanding.</p>
        """,
        lesson_cards=module_1_lesson_cards,
        resources=module_1_resources
    )

@app.route('/practice')
def practice():
    return render_template('practice.html', active_page='practice')


@app.route('/api/lessons', methods=['GET', 'POST'])
def api_lessons():
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
        db.session.add(lesson)
        db.session.commit()
        return jsonify({"message": "Lesson added successfully."})
    else:
        return jsonify({"error": "Invalid request method."}), 400

@app.route('/api/lessons/<lesson_id>', methods=['GET', 'PUT', 'DELETE'])
def api_lesson(lesson_id):
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
        if title:
            lesson.title = title
        if content:
            lesson.content = content
        if module_id:
            lesson.module_id = module_id
        db.session.commit()
        return jsonify({"message": "Lesson updated successfully."})
    elif request.method == 'DELETE':
        db.session.delete(lesson)
        db.session.commit()
        return jsonify({"message": "Lesson deleted successfully."})
    else:
        return jsonify({"error": "Invalid request method."}), 400



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

