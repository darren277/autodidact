""""""
import threading

from flask import Flask, request, Response, render_template, jsonify
from flask_sse import sse

import redis

from lib.assistant.main import AssistantHandler
from settings import REDIS_URL, ENABLE_CORS

from flask_cors import CORS

app = Flask(__name__)


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

data = {
    "date": "2025-03-18",
    "topic": "Cornell Notes Example",
    "sections": [
        {
            "parts": [
                {"lm": "Date: 1967", "main": "In 1967, the lorems discovered the ipsum."},
                {"lm": "Idea: Could this have resulted in the great lorem ipsum of 1971?", "main": "The lorems began cultivating ipsum in large quatities."}
            ],
            "summary": "Lorem ipsum blah blah blah."
        }
    ]
}

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


# add enumerate() to Jinja...
app.jinja_env.globals.update(enumerate=enumerate)


@app.route('/hello')
def publish_hello():
    msg = {"message": "Hello!"}
    print("Publishing message...", msg)
    sse.publish(msg, type='greeting')
    return "Message sent!"

app.run(host='0.0.0.0', port=8000)
