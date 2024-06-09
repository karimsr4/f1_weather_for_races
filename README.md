# Weather For F1 races

In this project, we show weather variables during F1 races (from 2018).

## Web page
The web page can be found on the : [Link](https://f1weather-y66wotluqa-uc.a.run.app). It is deployed on Google Cloud.

### Scraping Race schedules
* The path to script used to scrape race schedules: `./schedules`.
* The race schedules are scraped from [Link](https://www.formula1.com) and stored in a Google Firestore database using `populate_race_info.py`
* Schedules for races in the period 2018-2024 are scraped and stored in the Firestore database.
* To run `populate_race_info.py`, you would need a credentials file (to be stored in `./schedules`) to be able to write data to the Firestore database.
* We deploy `populate_race_info.py` as a job in Google Cloud to be run once a week to scrape not-yet available data (e.g. schedules for 2025 or upcoming events).
* The `Dockerfile` is the dockerfile used to deploy the job.

### Backend: 

* The path to backend scripts: `./backend`
* The backend is deployed to Google Cloud and provides public API endpoints.
* To run the backend, install packages from `requirements.txt`. You would need a credentials file (to be stored in `./schedules`) to be able to fetch data from the Firestore database.
* The Flask app (`app.py`) route methods that provide the data necessary for the frontend.
* `get_weather_data.py` provides methods to fetch weather variables data from Open-Meteo public API 
* `query_db.py` provides code to query the used Firestore database. 
* The `Dockerfile` is the dockerfile used to deploy the backend service.

### Frontend:

* The path to the `React` project: `./frontend`
* The frontend is deployed to Google Cloud in a Docker container and fetch data from backend.
* The `Dockerfile` is the dockerfile used to deploy the frontend service.

