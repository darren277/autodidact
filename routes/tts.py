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


def generate_audio_route(lesson_id):
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
