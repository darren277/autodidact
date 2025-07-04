""""""
import asyncio

from flask import request, render_template, Response, session, jsonify

from lib.tts.main import TTS
from lib.tts.personalities import descriptors
from utils.api_key_manager import get_user_api_key


def tts_route():
    if request.method == 'GET':
        return render_template('tts.html')
    else:
        # Check if user is authenticated
        if 'user' not in session:
            return jsonify({"error": "User not authenticated"}), 401
        
        # Get user's API key from database
        user_sub = session['user']['sub']
        api_key = get_user_api_key(user_sub)
        
        if not api_key:
            return jsonify({"error": "No OpenAI API key configured. Please set your API key in Settings."}), 400
        
        message = request.form.get('message', 'Hello, world!')
        
        try:
            _tts = TTS("gpt-4o-mini-tts", "alloy", descriptors['pirate'], api_key=api_key)
            audio = asyncio.run(_tts.speak(message))
            audio_bytes = audio
            response = Response(audio_bytes, mimetype="audio/wav")
            response.headers["Content-Disposition"] = "attachment; filename=speech.wav"
            return response
        except Exception as e:
            return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500
