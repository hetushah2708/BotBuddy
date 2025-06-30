from flask import Flask, request, render_template, jsonify
import os
import speech_recognition as sr
from algo import process_speech

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio file'}), 400

    audio_file = request.files['audio_data']
    filepath = os.path.join(UPLOAD_FOLDER, 'user_audio.wav')
    audio_file.save(filepath)

    # Speech Recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(filepath) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            result = process_speech(text)
            return jsonify({'original': text, 'processed': result})
        except sr.UnknownValueError:
            return jsonify({'error': 'Could not understand audio'}), 400
        except sr.RequestError as e:
            return jsonify({'error': f'Service error: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)