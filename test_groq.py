import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set.")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are SARATHI, a friendly and intelligent personal AI assistant."
        },
        {
            "role": "user",
            "content": "Hello SARATHI, introduce yourself in two sentences."
        }
    ]
)

print("\nSARATHI:")
print(response.choices[0].message.content)