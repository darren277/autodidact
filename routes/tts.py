""""""
import asyncio

from flask import request, render_template, Response

from lib.tts.main import TTS
from lib.tts.personalities import descriptors


def tts_route():
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
