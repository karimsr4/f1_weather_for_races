import requests
from datetime import datetime, timedelta

# Global constants.
FORECAST_MINUTELY15_VARIABLES = ["temperature_2m", "relative_humidity_2m", "rain", "wind_speed_10m", "wind_direction_10m"]
FORECAST_HOURLY_VARIABLES = ["surface_pressure"]
ALL_VARIABLES =  ["temperature_2m", "relative_humidity_2m", "rain", "wind_speed_10m", "wind_direction_10m", "surface_pressure"]

FORECAST_API_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_API_URL = "https://archive-api.open-meteo.com/v1/archive"

def fetch_forecast_weather(latitude, longitude, start_time, end_time):

    # Parse the time string to a datetime object
    starttime_datetime_object = datetime.fromisoformat(start_time)
    endtime_datetime_object = datetime.fromisoformat(end_time)

    # Extract the date from the datetime object
    start_date = starttime_datetime_object.date()
    end_date = endtime_datetime_object.date()

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "minutely_15": FORECAST_MINUTELY15_VARIABLES,
        "hourly": FORECAST_HOURLY_VARIABLES,
        "timezone": "auto",
        "start_date": start_date,
        "end_date": end_date
    }

    response = requests.get(FORECAST_API_URL, params=params)

    return filter_weather_data(response.json()["minutely_15"], start_time, end_time), filter_weather_data(response.json()["hourly"], start_time, end_time)


def filter_weather_data(response, start_time_str, end_time_str):
    start_time = datetime.fromisoformat(start_time_str) - timedelta(hours=5)
    end_time = datetime.fromisoformat(end_time_str) + timedelta(hours=2)

    filtered_data = {key: [] for key in response.keys()}

    for i, time_str in enumerate(response['time']):
        time = datetime.fromisoformat(time_str)
        if start_time <= time <= end_time:
            for key in response.keys():
                filtered_data[key].append(response[key][i])

    return filtered_data


def fetch_archive_weather(latitude, longitude, start_time, end_time):

    # Parse the time string to a datetime object
    starttime_datetime_object = datetime.fromisoformat(start_time)
    endtime_datetime_object = datetime.fromisoformat(end_time)

    # Extract the date from the datetime object
    start_date = starttime_datetime_object.date()
    end_date = endtime_datetime_object.date()

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ALL_VARIABLES,
        "timezone": "auto",
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.get(ARCHIVE_API_URL, params=params)

    return filter_weather_data(response.json()["hourly"], start_time, end_time)
