import speech_recognition as sr
import pyttsx3


recognizer = sr.Recognizer()

# Give the recognizer more time to understand natural speech.
recognizer.pause_threshold = 1.2
recognizer.phrase_threshold = 0.3
recognizer.non_speaking_duration = 0.8


def listen():

    with sr.Microphone() as source:

        print("Listening...")

        # Calibrate for the room
        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        print("Speak now...")

        try:

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=20
            )

        except sr.WaitTimeoutError:

            return ""

    try:

        print("Processing speech...")

        query = recognizer.recognize_google(
            audio
        )

        print(
            f"You said: {query}"
        )

        return query.strip()

    except sr.UnknownValueError:

        return ""

    except sr.RequestError:

        return ""


def speak(text):

    engine = pyttsx3.init()

    engine.setProperty(
        "rate",
        165
    )

    engine.say(text)

    engine.runAndWait()