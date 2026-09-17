import asyncio
import os
import edge_tts

VOICE = "en-IN-NeerjaNeural"

MESSAGE = (
    "Namaste. I am Sarathi, your intelligent and powerful personal assistant. "
    "How may I help you today?"
)

OUTPUT_FILE = "sarathi_voice.mp3"


async def create_voice():
    speaker = edge_tts.Communicate(
        text=MESSAGE,
        voice=VOICE,
        rate="+8%",
        pitch="+3Hz",
        volume="+10%",
    )

    await speaker.save(OUTPUT_FILE)


asyncio.run(create_voice())

print(f"SARATHI voice created: {OUTPUT_FILE}")
os.startfile(OUTPUT_FILE)