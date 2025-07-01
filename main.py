from flask import Flask, request, render_template, jsonify
import os
import speech_recognition as sr
from algo import process_speech
import traceback
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    try:
        app.logger.info("Received audio upload request")
        if 'audio_data' not in request.files:
            app.logger.error('No audio_data in request.files')
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio_data']
        if audio_file.filename == '':
            app.logger.error('Empty filename in audio file')
            return jsonify({'error': 'Empty filename'}), 400

        app.logger.info(f"Received file: {audio_file.filename}, content type: {audio_file.content_type}")

        # Create uploads directory if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            app.logger.info(f"Created uploads directory at {UPLOAD_FOLDER}")

        filepath = os.path.join(UPLOAD_FOLDER, 'user_audio.wav')
        audio_file.save(filepath)
        app.logger.info(f"Saved file to {filepath}, size: {os.path.getsize(filepath)} bytes")

        # Verify file was actually saved
        if not os.path.exists(filepath):
            app.logger.error(f"File was not saved to {filepath}")
            return jsonify({'error': 'Failed to save audio file'}), 500

        # Speech Recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(filepath) as source:
            app.logger.info("Processing audio file with speech recognition")
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio)
                app.logger.info(f"Recognized text: {text}")
                result = process_speech(text)
                return jsonify({'original': text, 'processed': result})
            except sr.UnknownValueError:
                app.logger.error('Speech Recognition could not understand audio')
                return jsonify({'error': 'Could not understand audio'}), 400
            except sr.RequestError as e:
                app.logger.error(f'Speech Recognition service error: {e}')
                return jsonify({'error': f'Service error: {e}'}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/start-listening', methods=['POST'])
def start_listening():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            app.logger.info("Listening from server microphone...")
            audio = recognizer.listen(source, timeout=None)
            app.logger.info("Transcribing audio...")
            try:
                text = recognizer.recognize_google(audio)
                app.logger.info(f"Recognized text: {text}")
                result = process_speech(text)
                return jsonify({'original': text, 'processed': result})
            except sr.UnknownValueError:
                app.logger.error('Speech Recognition could not understand audio')
                return jsonify({'error': 'Could not understand audio'}), 400
            except sr.RequestError as e:
                app.logger.error(f'Speech Recognition service error: {e}')
                return jsonify({'error': f'Service error: {e}'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port="5001")
