import eel
import speech_recognition as sr
import pyttsx3
from algo import FAQBot
import asyncio
import threading

# Initialize Eel with the templates folder
eel.init('templates')

# Initialize FAQBot and TTS engine globally
bot = FAQBot(api_key="AIzaSyBYGcNPmwiakoc03KXGZkTXW-btfGt_itk")
recognizer = sr.Recognizer()
recognizer.energy_threshold = 150
tts_engine = pyttsx3.init()

listening = False
listening_lock = threading.Lock()

@eel.expose
def start_listening():
    global listening
    with listening_lock:
        if listening:
            return  # Already listening
        listening = True

    def listen_loop():
        global listening
        while listening:
            try:
                with sr.Microphone() as source:
                    eel.update_status("Listening... (Speak into mic)")
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=5)
                eel.update_status("Recognizing...")
                try:
                    text = recognizer.recognize_google(audio)
                    eel.update_original(text)
                    eel.update_status("Thinking...")
                    # Get bot response using asyncio event loop
                    response = asyncio.run(bot.generate_response(text))
                    eel.update_processed(response)
                    eel.update_status("Speaking...")
                    tts_engine.say(response)
                    tts_engine.runAndWait()
                    eel.update_status("Ready")
                except sr.UnknownValueError:
                    eel.update_status("Sorry, could not understand audio.")
                except sr.RequestError as e:
                    eel.update_status(f"Could not request results; {e}")
            except sr.WaitTimeoutError:
                eel.update_status("No speech detected, try again.")
            except Exception as e:
                eel.update_status(f"Error: {str(e)}")
            # Wait a bit before next listen to avoid rapid-fire
            import time
            time.sleep(1)
        eel.update_status("Stopped.")

    threading.Thread(target=listen_loop, daemon=True).start()

@eel.expose
def stop_listening():
    global listening
    with listening_lock:
        listening = False

@eel.expose
def speak_text(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

if __name__ == "__main__":
    eel.start('index2_eel.html', size=(800, 900))