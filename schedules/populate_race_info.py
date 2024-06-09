from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
import re
from datetime import date, timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

AVAILABLE_YEARS = [
    2018,
    2019,
    2020,
    2021,
    2022,
    2023,
    2024
]

MONTH_MAP_START_PAGE = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

MONTH_MAP_SCHEDULE_PAGE = {
    "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3, "APRIL": 4,
    "MAY": 5, "JUNE": 6, "JULY": 7, "AUGUST": 8,
    "SEPTEMBER": 9, "OCTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12
}

CALLED_OFF_RACES = {
    2023 : ["Emilia-Romagna"]
}

# The first year with the current version of the Full Schedule Table.
YEAR_CUTOFF = 2022

PRACTICE = "PRACTICE"
PRESS_CONFERENCE = "PRESS"
QUALIFYING = "QUALIFYING"
ANTHEM = "ANTHEM"
RACE = "GRAND PRIX"
SPRINT = "SPRINT"
CARS_ON_TRACK_EVENTS = [PRACTICE, QUALIFYING, SPRINT, RACE]


TRACK_TO_CITY_MAPPING = {
    "Australia": "Melbourne",
    "Bahrain": "Sakhir",
    "China": "Shanghai",
    "Azerbaijan": "Baku",
    "Spain": "Barcelona",
    "Monaco": "Monte Carlo",
    "Canada": "Montreal",
    "France": "Le Castellet",
    "Austria": "Spielberg",
    "Great Britain": "Silverstone",
    "Germany": "Hockenheim",
    "Hungary": "Mogyoród",
    "Belgium": "Stavelot",
    "Italy": "Monza",
    "Singapore": "Singapore",
    "Russia": "Sochi",
    "Japan": "Suzuka",
    "United States": "Austin",
    "Mexico": "Mexico City",
    "Brazil": "São Paulo",
    "Abu Dhabi": "Yas Island",
    "Styria": "Spielberg",
    "70th Anniversary": "Silverstone",
    "Tuscany": "Mugello",
    "Portugal": "Portimão",
    "Emilia-Romagna": "Imola",
    "Turkey": "Istanbul",
    "Sakhir": "Sakhir",
    "Netherlands": "Zandvoort",
    "Qatar": "Doha",
    "Saudi Arabia": "Jeddah",
    "Miami": "Miami",
    "Las Vegas": "Las Vegas"
}

GEOSPATIAL_API_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Initialize the Firebase Admin SDK
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

def get_races(year : int = 2024) -> dict:
    races = {}
    url = f"https://www.formula1.com/en/racing/{year}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    race_elements = soup.find_all('a', class_='event-item-wrapper event-item-link')
    for race_element in race_elements:
        url = f"https://www.formula1.com/{race_element['href']}"
        race_info = json.loads(race_element["data-tracking"])

        if race_info["eventType"] != "race":
            # Esports, festivals..
            continue
        
        country = race_element['data-racecountryname']

        # skip called off races
        called_off_races = CALLED_OFF_RACES.get(year)
        if called_off_races is not None and country in called_off_races:
            continue

        races[country] = url

    return races

def get_date(date_str : str, year : int) -> datetime.date:
    day_match = re.search(r'\d+', date_str)
    month_match = re.search(r'\b[a-zA-Z]+\b', date_str.split()[-1])
    if day_match and month_match:
        day = int(day_match.group())
        month = MONTH_MAP_SCHEDULE_PAGE[month_match.group().upper()]
        return date(year, month, day)
    else:
        print(f"Could not parse date: {date_str}")

def get_race_timetable(race_url : str, year : int) -> dict:
    timetable = []
    # Navigate to "Full schedule" component
    full_schedule_response = requests.get(race_url)
    soup = BeautifulSoup(full_schedule_response.content, "html.parser")
    full_schedule_link = soup.find("a", class_="d-block link link--btn")["href"]
    if full_schedule_link is None:
        raise ValueError(f"Failed to fetch race Full schedule component for {race_url}")

    timetable_response = requests.get(full_schedule_link)
    soup = BeautifulSoup(timetable_response.content, "html.parser")

    tables = soup.find_all('table')
    for table in tables:
        headers = [th.text.strip() for th in table.find_all('th')]

        # Date for the new version of the website
        if year >= YEAR_CUTOFF:
            date_ = get_date(headers[0], year)
            starting_table_index = 1
        else:
            date_ = None
            starting_table_index = 0
        
        for row in table.find_all('tr')[starting_table_index:]:
            cells = row.find_all('td')
            cell_data = [cell.text.strip() for cell in cells]

            # Old table
            if cell_data[0] == "" and cell_data[1] == "" and cell_data[2] == "":
                continue

            if cell_data[0] != "" and cell_data[1] == "" and cell_data[2] == "":
                print(cell_data[0])
                date_ = get_date(cell_data[0], year)
                continue

            entity = cell_data[0]
            event_name = cell_data[1]

            if "FORMULA 1" not in entity.upper():
                continue

            event_type = None
            for cars_event in CARS_ON_TRACK_EVENTS:
                if cars_event in event_name.upper():
                    event_type = cars_event

            time_str = re.split(' - | -|- |-', cell_data[2])
            start_time_str = time_str[0]

            if ":" in start_time_str:
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
            elif "." in start_time_str:
                start_time = datetime.strptime(start_time_str, '%H.%M').time()
            elif ";" in start_time_str:
                start_time = datetime.strptime(start_time_str, '%H;%M').time()
            else:
                print(f"Uknown start time format {start_time_str}")
                start_time = None

            if len(time_str) == 2:
                end_time_str = time_str[1]
                if ":" in end_time_str:
                    end_time = datetime.strptime(end_time_str, '%H:%M').time()
                elif "." in end_time_str:
                    end_time = datetime.strptime(end_time_str, '%H.%M').time()
                else:
                    print(f"Uknown end time format {end_time_str}")
                    end_time = None  
            else:
                # if there is no end time, set event to last for 2 hours
                end_datetime = datetime.combine(datetime.today(), start_time) + timedelta(hours=2)
                end_time = end_datetime.time()
            
            if event_type is None:
                # print(f"Skipping event {event_name} because it does not involve cars.")
                continue

            event = {
                "event_name" : cell_data[1],
                "start_time" : start_time,
                "end_time" : end_time,
                "date" : date_,
                "event_type": event_type
            }
            timetable.append(event)

    return timetable

def fetch_geospatial_data(city:str):
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    response = requests.get(GEOSPATIAL_API_URL, params=params).json()
    return response["results"][0]["latitude"], response["results"][0]["longitude"]

def populate_race_schedules_data(years):
    for year in years:
        base_path = f"races/all_races"
        db.document(base_path).set({})

        races = get_races(year)
        for race_name, race_url in races.items():
            race_path = f"races/all_races/{year}/{race_name}"
            print(race_name)
            latitude, longitude = fetch_geospatial_data(TRACK_TO_CITY_MAPPING[race_name])
            db.document(race_path).set({"latitude":latitude, "longitude":longitude})

            all_events_race = get_race_timetable(race_url, year)
            for event in all_events_race:
                event_name = event["event_name"]
                start_time_str = datetime.combine(event['date'], event['start_time']).isoformat()
                end_time_str = datetime.combine(event['date'], event['end_time']).isoformat()
                data = {
                    "start_time": start_time_str,  # Example start time in ISO format
                    "end_time": end_time_str,     # Example end time in ISO format
                }
                # # Path to the document where data will be written
                document_path = f"races/all_races/{year}/{race_name}/sessions/{event_name}"

                # Write the data to Firestore
                db.document(document_path).set(data)


current_year = datetime.now().year

# Fetch schedules for current year.
populate_race_schedules_data([current_year])

    
