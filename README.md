# SARATHI - AI Personal Voice Assistant

SARATHI is a local AI-powered personal voice assistant built with Python.

It combines conversational AI, voice input, text-to-speech, conversation memory, and computer-control commands into a modular desktop assistant.

## Features

- AI conversations using Ollama and Llama 3.2
- Voice input and speech recognition
- Piper TTS voice output
- English and Hindi voice support
- Conversation memory
- Deterministic PC and system commands
- Tkinter desktop interface
- Pygame audio playback
- Local knowledge base
- Local AI processing

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Ollama | Local AI runtime |
| Llama 3.2 | Conversational AI |
| Piper TTS | Text-to-speech |
| Tkinter | Desktop interface |
| Pygame | Audio playback |
| JSON | Knowledge base |
| Git & GitHub | Version control |

## Project Structure

```text
SARATHI/
├── config/
├── core/
│   ├── assistant.py
│   ├── brain.py
│   ├── knowledge_base.json
│   └── system_actions.py
├── notes/
├── ui/
│   └── app.py
├── voice/
│   ├── listener.py
│   ├── speaker.py
│   └── tts_test.py
├── voices/
├── list_voices.py
├── main.py
├── requirements.txt
├── LICENSE
└── README.md

Requirements
Python 3.12+
Ollama
Llama 3.2
Working microphone
Windows PC
Python packages listed in requirements.txt

Installation
Clone the repository
git clone https://github.com/Bhushangcoe/SARATHI.git
cd SARATHI

Create virtual environment
python -m venv .venv

Activate virtual environment
.venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Setup Ollama
Make sure Ollama is installed and running.
ollama pull llama3.2
Check the installed model:
ollama list

Run SARATHI
python main.py
Or:
python -m ui.app

Voice Pipeline
User Voice
    |
    v
Speech Recognition
    |
    v
SARATHI Assistant
    |
    v
Ollama / Llama 3.2
    |
    v
AI Response
    |
    v
Piper TTS
    |
    v
Voice Output

System Commands
SARATHI contains deterministic system-action functionality for predefined computer and system operations.
System actions are handled separately from normal LLM conversations, helping keep predefined operations predictable and controlled.

#Architecture:-
                    +----------------+
                    |      User      |
                    +-------+--------+
                            |
                            v
                    +---------------+
                    | Voice Listener|
                    +-------+-------+
                            |
                            v
                    +---------------+
                    |   Assistant   |
                    +-------+-------+
                            |
                +-----------+-----------+
                |                       |
                v                       v
        +---------------+       +---------------+
        | System Actions|       |    AI Brain   |
        +---------------+       +-------+-------+
                                        |
                                        v
                                +---------------+
                                | Ollama /      |
                                | Llama 3.2     |
                                +-------+-------+
                                        |
                                        v
                                +---------------+
                                | Conversation  |
                                | Memory        |
                                +-------+-------+
                                        |
                                        v
                                +---------------+
                                |   Piper TTS   |
                                +-------+-------+
                                        |
                                        v
                                +---------------+
                                |    Speaker    |
                                +---------------+

Local AI
SARATHI is designed around local AI processing.
Ollama runs the language model locally, while Piper provides local text-to-speech.

Project Goals
The long-term goal of SARATHI is to build a capable personal AI assistant with:
Natural voice interaction
Conversational intelligence
Conversation memory
Local AI models
Voice synthesis
Computer interaction
Modular AI architecture

Author
Bhushan Gangurde
Computer Engineering Graduate
Data Science and AI/ML Enthusiast
GitHub: https://github.com/Bhushangcoe/SARATHI

License
This project is licensed under the terms specified in the LICENSE file.
