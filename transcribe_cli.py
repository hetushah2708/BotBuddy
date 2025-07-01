import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Please speak. Press Ctrl+C to stop recording.")
    try:
        audio = recognizer.listen(source, timeout=None)
        print("Transcribing...")
        text = recognizer.recognize_google(audio)
        print("Transcription:")
        print(text)
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    except Exception as e:
        print(f"Error: {e}")