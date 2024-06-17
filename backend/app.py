from flask import Flask, jsonify
from flask_cors import CORS
from get_weather_data import fetch_forecast_weather, fetch_archive_weather
from utils import infer_timezone, is_future_date
from query_db import query_available_years, query_available_races, query_available_sessions, query_session_info, query_location_info
import os

app = Flask(__name__)
CORS(app)

@app.route('/available_years', methods=['GET'])
def get_available_years():
    try:
        years = query_available_years()
        return jsonify({'available_years': years}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@app.route('/available_races/<year>', methods=['GET'])
def get_available_races(year):
    try:
        races= query_available_races(year)
        return jsonify({'year': year, 'available_races': races}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/available_sessions/<year>/<race>', methods=['GET'])
def get_available_sessions(year, race):
    try:
        sessions = query_available_sessions(year, race)

        return jsonify({'year': year, 'race': race, 'available_sessions': sessions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/weather_data/<year>/<race>/<session>', methods=['GET'])
def get_weather_data(year, race, session):

    session_doc = query_session_info(year, race, session)
    latitude, longitude = query_location_info(year, race)

    if not session_doc.exists:
        return jsonify({})

    start_time = session_doc.to_dict().get("start_time")
    end_time = session_doc.to_dict().get("end_time")
    
    if is_future_date(latitude,  longitude, start_time):

        data = fetch_forecast_weather(latitude,  longitude, start_time, end_time) 
        weather_data = {
            "start_time": start_time,
            "end_time": end_time,
            "temperature": {"time": data[0]["time"], "values": data[0]["temperature_2m"]},
            "humidity": {"time": data[0]["time"], "values": data[0]["relative_humidity_2m"]},
            "rain": {"time": data[0]["time"], "values": data[0]["rain"]},
            "windSpeed": {"time": data[0]["time"], "values": data[0]["wind_speed_10m"]},
            "windDirection": {"time": data[0]["time"], "values": data[0]["wind_direction_10m"]},
            "pressure": {"time": data[1]["time"], "values": data[1]["surface_pressure"]}
        }
        
    else: 
        data = fetch_archive_weather(latitude,  longitude, start_time, end_time) 
        weather_data = {
            "start_time": start_time,
            "end_time": end_time,
            "temperature": {"time": data["time"], "values": data["temperature_2m"]},
            "humidity": {"time": data["time"], "values": data["relative_humidity_2m"]},
            "rain": {"time": data["time"], "values": data["rain"]},
            "windSpeed": {"time": data["time"], "values": data["wind_speed_10m"]},
            "windDirection": {"time": data["time"], "values": data["wind_direction_10m"]},
            "pressure": {"time": data["time"], "values": data["surface_pressure"]}
        }

    return jsonify(weather_data)
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))