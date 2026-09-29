import requests 
from flask import Flask, render_template, jsonify
from configure import WEATHER_API_KEY

CITY = "Москва"

app = Flask(__name__)
app.json.ensure_ascii = False


#получаем данные о погоде
def weather():
    params = {"key": WEATHER_API_KEY,
            "q": CITY,
            "lang": "ru"}

    response = requests.get(
        "http://api.weatherapi.com/v1/current.json",
        params=params,
        timeout=10
    )
    data = response.json()

    our_data = {
        "city": data["location"]["name"],
        "timezone": data["location"]["tz_id"],
        "temp": round(data["current"]["temp_c"])
    }
    return our_data

@app.route("/")
def index():
    return render_template("index.html", w=weather)

app.route("/api/weather")
def api ():
    return jsonify(wather())

app.run(debug=True, port=5004)


print ("byebyeworld!")