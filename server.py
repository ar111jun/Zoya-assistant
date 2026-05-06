from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import requests
import os
import yfinance as yf
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(Path("C:/Users/Adminn/Desktop/zoya/.env"))

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
CITY = "Kollam"

client = Groq(api_key=GROQ_API_KEY)
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
    data = requests.get(url).json()
    if "main" not in data:
        return "Weather unavailable"
    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    return f"{description}, {temp}°C, humidity {humidity}%"

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    data = requests.get(url).json()
    articles = data.get("articles", [])
    if not articles:
        return "No news available"
    headlines = []
    for i, article in enumerate(articles, 1):
        headlines.append(f"{i}. {article['title']}")
    return "\n".join(headlines)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    command = data.get("message", "")
    extra_info = ""

    if "weather" in command.lower():
        extra_info = f"Current weather: {get_weather()}"
    if "news" in command.lower() or "headline" in command.lower():
        extra_info = f"Today's headlines:\n{get_news()}"

    full_command = f"{extra_info}\n\nUser said: {command}" if extra_info else command

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are Zoya, a smart friendly AI assistant. Keep responses short and conversational."},
            {"role": "user", "content": full_command}
        ]
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

@app.route("/briefing", methods=["GET"])
def briefing():
    weather = get_weather()
    news = get_news()
    return jsonify({
        "weather": weather,
        "news": news
    })
@app.route("/stocks", methods=["GET"])
def get_stocks():
    tickers = {
        "NIFTY 50": "^NSEI",
        "Reliance": "RELIANCE.NS",
        "Nippon Gold": "GOLDBEES.NS",
        "Silver ETF": "SILVERBEES.NS",
        "Apple": "AAPL",
        "Tesla": "TSLA",
        "Google": "GOOGL"
    }
    result = []
    for name, symbol in tickers.items():
        try:
            info = yf.Ticker(symbol).info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            change = info.get("regularMarketChangePercent", 0)
            result.append({
                "name": name,
                "price": round(price, 2),
                "change": round(change, 2),
                "bullish": change >= 0
            })
        except:
            pass
    return jsonify(result)
if __name__ == "__main__":
    app.run(port=5000)