# 🤖 Zoya — AI Voice Assistant

A Jarvis-style personal AI assistant built with Python that responds to voice commands, fetches live weather and news, manages reminders, and automates your work setup.

##  Features

-  **Wake word detection** — Say "Hey Zoya" to activate
-  **Live weather** — Real-time weather for your city
-  **Daily news** — Top headlines fetched live
-  **Smart reminders** — Set reminders by voice
-  **Work automation** — Opens your CRM and work tabs automatically
-  **Voice responses** — Speaks back to you

##  Tech Stack

- **AI Brain** — Groq API (Llama 3.3)
- **Speech Recognition** — Google Speech API
- **Text to Speech** — pyttsx3
- **Weather** — OpenWeatherMap API
- **News** — NewsAPI
- **Audio** — SoundDevice + WO Mic

##  How to Run

1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your API keys
6. Run: `python brain.py`
7. Say **"Hey Zoya"** to wake her up!

## 🔑 Environment Variables

Create a `.env` file with:
