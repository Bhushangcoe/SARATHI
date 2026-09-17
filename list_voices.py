import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty("voices")

for number, voice in enumerate(voices):
    print(f"{number}: {voice.name}")
    print(f"   ID: {voice.id}")
    print()