import speech_recognition as sr
import pyttsx3
from algo import FAQBot
import asyncio
import azure.cognitiveservices.speech as speechsdk

def main():
    # Initialize FAQBot (replace with your actual API key)
    bot = FAQBot(api_key="AIzaSyBYGcNPmwiakoc03KXGZkTXW-btfGt_itk")
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 150  # Adjust as needed
    tts_engine = pyttsx3.init()
    print("Say something! (Press Ctrl+C to exit)")

    # Create the event loop once
    loop = asyncio.get_event_loop()

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=4, phrase_time_limit=5)
            print("Recognizing...")
            try:
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                # Use the same event loop for all async calls
                response = loop.run_until_complete(bot.generate_response(text))
                print(f"Bot: {response}")
                # Determine tone based on response or context
                tone = "cheerful"  # Or "sad", "angry", etc.
                speak_with_tone(response, tone)
            except sr.UnknownValueError:
                print("Sorry, could not understand audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except sr.WaitTimeoutError:
            print("No speech detected, try again.")

def speak_with_tone(text, tone="neutral"):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # You can select a different voice if available
    engine.setProperty('voice', voices[0].id)  # Change index for different voices

    # Default values
    rate = 150
    volume = 1.0

    if tone == "cheerful":
        rate = 200
        volume = 1.0
    elif tone == "sad":
        rate = 100
        volume = 0.7
    elif tone == "angry":
        rate = 220
        volume = 1.0
    elif tone == "neutral":
        rate = 150
        volume = 1.0

    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    main()