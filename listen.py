import speech_recognition as sr
import pyttsx3
from algo import FAQBot
import asyncio

def main():
    # Initialize FAQBot (replace with your actual API key)
    bot = FAQBot(api_key="AIzaSyBYGcNPmwiakoc03KXGZkTXW-btfGt_itk")
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 150  # Adjust as needed
    tts_engine = pyttsx3.init()
    print("Say something! (Press Ctrl+C to exit)")

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=4, phrase_time_limit=5)
            print("Recognizing...")
            try:
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                # Get bot response using asyncio event loop
                response = asyncio.run(bot.generate_response(text))
                print(f"Bot: {response}")
                tts_engine.say(response)
                tts_engine.runAndWait()
            except sr.UnknownValueError:
                print("Sorry, could not understand audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except sr.WaitTimeoutError:
            print("No speech detected, try again.")

if __name__ == "__main__":
    main()