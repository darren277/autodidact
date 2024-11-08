""""""
import threading

from flask import Flask, request, Response, render_template
from flask_sse import sse

from lib.assistant.main import AssistantHandler
from settings import REDIS_URL

app = Flask(__name__)

app.config["REDIS_URL"] = REDIS_URL
app.register_blueprint(sse, url_prefix='/stream')


@app.route('/')
def hello_world():
    return render_template('index.html')
    #return open('templates/index.html').read()


@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    assistant_id = request.form.get('assistant_id', None)

    assistant_handler = AssistantHandler(question, assistant_id)
    assistant_handler.initialize_app(app)

    # You can use a unique identifier per user/session
    py_thread_id = request.remote_addr

    threading.Thread(
        target=assistant_handler.run,
        args=(py_thread_id,)
    ).start()

    return render_template('response.html', question=question, thread_id=py_thread_id)


@app.route('/hello')
def publish_hello():
    sse.publish({"message": "Hello!"}, type='greeting')
    return "Message sent!"

