import pyttsx3
import threading

def speak_text(text):
    """Speaks the given text using text-to-speech engine in a separate thread."""
    def _speak():
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error in TTS: {e}")

    # Run in a separate thread to avoid blocking the main UI
    thread = threading.Thread(target=_speak)
    thread.start()
