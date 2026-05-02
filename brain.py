from groq import Groq
import requests
import schedule
import time
import threading
import webbrowser
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import tempfile
import os

GROQ_API_KEY = "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"
WEATHER_API_KEY = "76e7779f6efa9ed3a78d13777eb4c319"
NEWS_API_KEY = "b3d3ac45fdee4ed586aa3a72183d5c2a"
CITY = "Kochi"
WORK_TABS = [
    "https://go.business360.app/v2/location/yYN9iZdulvQIskOjHiMY/opportunities",
    "https://docs.google.com/spreadsheets/d/1lNdkYHo0KNjHS_x_OcLWwqcrRtj435EQ35tKcIHF6Xs/edit?gid=423354466#gid=423354466"
]
WO_MIC_DEVICE = 3
WAKE_WORDS = ["zoya", "hey zoya", "oi zoya"]
SILENCE_TIMEOUT = 300  # 5 minutes

client = Groq(api_key=GROQ_API_KEY)
reminders = []

def get_engine():
    engine = __import__('pyttsx3').init()
    engine.setProperty('rate', 175)
    return engine

def speak(text):
    print(f"Zoya: {text}")
    time.sleep(0.5)
    engine = get_engine()
    engine.say(text)
    engine.runAndWait()
    del engine
    time.sleep(0.5)

def record_audio(duration=3):
    sample_rate = 16000
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16',
        device=WO_MIC_DEVICE
    )
    sd.wait()
    return audio, sample_rate

def audio_to_text(audio, sample_rate):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav.write(f.name, sample_rate, audio)
        temp_path = f.name
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_path) as source:
        audio_data = recognizer.record(source)
    os.unlink(temp_path)
    try:
        return recognizer.recognize_google(audio_data).lower()
    except:
        return ""

def listen_for_wake_word():
    print("😴 Sleeping... say 'Hey Zoya' to wake me up")
    while True:
        audio, sample_rate = record_audio(duration=3)
        text = audio_to_text(audio, sample_rate)
        print(f"Heard: {text}")
        if any(word in text for word in WAKE_WORDS):
            return True

def listen_for_command():
    print("🎙️ Listening for command...")
    audio, sample_rate = record_audio(duration=5)
    return audio_to_text(audio, sample_rate)

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
    data = requests.get(url).json()
    if "main" not in data:
        return "Weather data unavailable right now."
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    description = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    return f"Weather in {CITY}: {description}, {temp}C, feels like {feels_like}C, humidity {humidity}%"

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    data = requests.get(url).json()
    articles = data.get("articles", [])
    if not articles:
        return "No news available right now."
    headlines = []
    for i, article in enumerate(articles, 1):
        headlines.append(f"{i}. {article['title']}")
    return "\n".join(headlines)

def open_work_tabs():
    for url in WORK_TABS:
        webbrowser.open(url)
    return "Opening your CRM and Google Sheet now!"

def set_reminder(reminder_time, message):
    def job():
        speak(f"Reminder: {message}")
    schedule.every().day.at(reminder_time).do(job)
    reminders.append({"time": reminder_time, "message": message})

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)

def ask_zoya(command):
    extra_info = ""
    if "weather" in command.lower():
        extra_info = f"Current weather data: {get_weather()}"
    if "news" in command.lower() or "headline" in command.lower():
        extra_info = f"Today's top headlines:\n{get_news()}"
    if "work" in command.lower() or "start" in command.lower():
        return open_work_tabs()
    if "remind" in command.lower():
        extra_info = "The user wants to set a reminder. Extract the time in HH:MM format and the message from their request. Reply in this exact format: REMINDER|HH:MM|message"
    full_command = f"{extra_info}\n\nUser said: {command}" if extra_info else command
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are Zoya, a smart and friendly personal AI assistant. Keep responses short and conversational."},
            {"role": "user", "content": full_command}
        ]
    )
    reply = response.choices[0].message.content
    if reply.startswith("REMINDER|"):
        parts = reply.split("|")
        set_reminder(parts[1].strip(), parts[2].strip())
        return f"Got it! I'll remind you at {parts[1].strip()} to {parts[2].strip()}"
    return reply

# Start scheduler
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

print("✅ Zoya is running in the background!")

# Main loop
while True:
    # Wait for wake word
    listen_for_wake_word()
    speak("Yes?")

    # Conversation loop with timeout
    last_interaction = time.time()
    while True:
        # Check 5 min silence timeout
        if time.time() - last_interaction > SILENCE_TIMEOUT:
            speak("Going to sleep. Call me when you need me!")
            break

        command = listen_for_command()

        if not command:
            continue

        if "bye" in command or "sleep" in command or "stop" in command:
            speak("Going to sleep. Call me when you need me!")
            break

        last_interaction = time.time()
        reply = ask_zoya(command)
        speak(reply)