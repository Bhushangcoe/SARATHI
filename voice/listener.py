import speech_recognition as sr


MICROPHONE_INDEX = 1
LANGUAGE = "en-IN"


def listen():
    recognizer = sr.Recognizer()

    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.7
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 0.4

    try:
        with sr.Microphone(device_index=MICROPHONE_INDEX) as source:

            print("Calibrating microphone...")
            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            print("Listening... Speak in English.")

            audio = recognizer.listen(
                source,
                timeout=6,
                phrase_time_limit=8
            )

        try:
            text = recognizer.recognize_google(
                audio,
                language=LANGUAGE
            )

            print(f"You said: {text}")

            return {
                "text": text,
                "language": "en"
            }

        except sr.UnknownValueError:

            print("I could not understand you.")

            return {
                "text": "",
                "language": "en"
            }

    except sr.WaitTimeoutError:

        print("I did not hear anything.")

        return {
            "text": "",
            "language": "en"
        }

    except sr.RequestError:

        print(
            "Speech recognition is unavailable. "
            "Check your internet connection."
        )

        return {
            "text": "",
            "language": "en"
        }