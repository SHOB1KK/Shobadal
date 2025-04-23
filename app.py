import requests
from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv
import tempfile
from playsound import playsound

app = Flask(__name__)

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY") or "your-openai-key"
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY") or "your-elevenlabs-key"
voice_id = "Zlb1dXrM653N07WRdFW3"
weather_api_key = os.getenv("WEATHER_API_KEY")  # API Key for weather service
weather_url = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    params = {
        'q': city,
        'appid': weather_api_key,
        'units': 'metric',  # or 'imperial' for Fahrenheit
        'lang': 'ru'  # to get the weather in Russian
    }
    try:
        response = requests.get(weather_url, params=params)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"Температура в {city}: {temp}°C, {description}."
        else:
            return f"Ошибка при получении данных о погоде: {response.status_code}"
    except Exception as e:
        return f"Ошибка: {e}"

def get_chatgpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are SHOBADALOV, a smart and elegant AI assistant."},
                      {"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"[ERROR] GPT response error: {e}")
        return "Произошла ошибка при получении ответа от ИИ."

def speak_with_elevenlabs(text):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": elevenlabs_api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8
            }
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            playsound(tmp_file_path)
            os.remove(tmp_file_path)
        else:
            print(f"[ERROR] ElevenLabs voice error: {response.text}")
    except Exception as e:
        print(f"[ERROR] Voice generation error: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_input = data.get("prompt", "")
    if not user_input:
        return jsonify({"error": "Нет запроса"}), 400

    # Check if user asks about weather
    if "погода" in user_input:
        city = user_input.split()[-1]  # Assuming last word is the city name
        weather_info = get_weather(city)
        speak_with_elevenlabs(weather_info)
        return jsonify({"response": weather_info})
    
    # Otherwise, handle as normal chat
    response = get_chatgpt_response(user_input)
    speak_with_elevenlabs(response)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
