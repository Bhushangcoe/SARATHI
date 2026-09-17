from core.assistant import get_response
from voice.listener import listen
from voice.speaker import speak


def main():
    welcome_message = "Namaste. Sarathi is ready. Please speak after I finish."

    print(f"SARATHI: {welcome_message}")
    speak(welcome_message)

    while True:
        user_message = listen()

        if not user_message:
            continue

        if user_message.lower() in ["exit", "quit", "bye"]:
            goodbye_message = "Namaste. Sarathi is going offline. See you soon."
            print(f"SARATHI: {goodbye_message}")
            speak(goodbye_message)
            break

        response = get_response(user_message)
        print(f"SARATHI: {response}")
        speak(response)


if __name__ == "__main__":
    main()