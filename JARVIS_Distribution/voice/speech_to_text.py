import speech_recognition as sr


_recognizer = sr.Recognizer()


def listen():

    microphone = sr.Microphone()

    with microphone as source:

        print("🎤 Listening...")

        _recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )

        try:

            audio = _recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=15
            )

        except sr.WaitTimeoutError:

            print("No speech detected.")

            return ""


    print("🔄 Processing speech...")

    try:

        # Uses the installed/offline recognition
        # backend if available.
        text = _recognizer.recognize_sphinx(
            audio
        )

        return text

    except sr.UnknownValueError:

        print("Could not understand the speech.")

        return ""

    except sr.RequestError as error:

        print(
            "Offline speech recognition is unavailable:"
        )

        print(error)

        return ""